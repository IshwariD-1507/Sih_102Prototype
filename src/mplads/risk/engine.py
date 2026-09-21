from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd


# =========================================================
# RISK WEIGHTS
# =========================================================

WEIGHTS = {
    "financial_anomaly": 20,
    "progress_mismatch": 25,
    "delay_risk": 20,
    "cost_anomaly": 15,
    "duplicate_overlap": 10,
    "data_quality": 10,
}


# =========================================================
# HELPERS
# =========================================================

def _num(series: pd.Series) -> pd.Series:
    """Safely convert a Series to numeric."""
    return pd.to_numeric(
        series,
        errors="coerce",
    )


def _get_column(
    df: pd.DataFrame,
    column: str,
    default,
) -> pd.Series:
    """Return a column or a correctly indexed default Series."""

    if column in df.columns:
        return df[column]

    return pd.Series(
        default,
        index=df.index,
    )


# =========================================================
# MAIN RISK ENGINE
# =========================================================

def create_risk_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create an explainable project-level screening risk score.

    This is a screening mechanism for identifying projects
    that may deserve human review.

    It does NOT establish fraud, corruption,
    misuse, or misconduct.
    """

    df = df.copy()

    # =====================================================
    # ENSURE REQUIRED / OPTIONAL COLUMNS
    # =====================================================

    optional_numeric = [
        "Recommendation_Sanction_Gap_Percent",
        "Utilisation_Percent",
        "Cost_Deviation_Percent",
        "Max_Overlap_Score",
        "Potential_Overlap_Count",
        "Days_Sanction_to_Completion",
    ]

    for column in optional_numeric:
        if column not in df.columns:
            df[column] = np.nan

    # -----------------------------------------------------
    # Progress status
    #
    # The actual project dataset uses Progress_Status.
    # -----------------------------------------------------

    if "Progress_Status" not in df.columns:

        if "Work_Status" in df.columns:
            df["Progress_Status"] = (
                df["Work_Status"]
                .fillna("")
                .astype(str)
            )

        else:
            df["Progress_Status"] = ""

    # -----------------------------------------------------
    # Completion date
    # -----------------------------------------------------

    if "Completion_Date" not in df.columns:
        df["Completion_Date"] = pd.NaT

    # -----------------------------------------------------
    # Evidence fields
    # -----------------------------------------------------

    if "Has_Completion_Image" not in df.columns:
        df["Has_Completion_Image"] = False

    if "Completion_Evidence_Missing" not in df.columns:

        # Only explicitly missing evidence should create
        # an evidence signal.
        df["Completion_Evidence_Missing"] = (
            ~df["Has_Completion_Image"]
            .fillna(False)
            .astype(bool)
        )

    # =====================================================
    # BASE SIGNALS
    # =====================================================

    financial_gap = _num(
        df["Recommendation_Sanction_Gap_Percent"]
    )

    cost_deviation = _num(
        df["Cost_Deviation_Percent"]
    )

    overlap_score = _num(
        df["Max_Overlap_Score"]
    ).fillna(0)

    overlap_count = _num(
        df["Potential_Overlap_Count"]
    ).fillna(0)

    duration = _num(
        df["Days_Sanction_to_Completion"]
    )

    # =====================================================
    # 1. FINANCIAL ANOMALY
    # =====================================================

    disbursement_exceeds = (
        _get_column(
            df,
            "Disbursement_Exceeds_Sanction",
            False,
        )
        .fillna(False)
        .astype(bool)
    )

    financial_flag = (
        financial_gap.abs().gt(20)
        | disbursement_exceeds
    )

    # =====================================================
    # 2. PROGRESS MISMATCH
    # =====================================================

    status = (
        df["Progress_Status"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    status_completed = (
        status.isin(
            [
                "completed",
                "work completed",
                "complete",
            ]
        )
        | status.str.contains(
            "work completed",
            na=False,
        )
    )

    completion_date = pd.to_datetime(
        df["Completion_Date"],
        errors="coerce",
    )

    completion_missing = (
        completion_date.isna()
    )

    # A project marked completed without a completion
    # date is treated as a progress/data consistency signal.
    progress_mismatch = (
        status_completed
        & completion_missing
    )

    # =====================================================
    # 3. DELAY RISK
    # =====================================================

    if duration.notna().any():

        duration_threshold = duration.quantile(
            0.90
        )

        delay_flag = (
            duration.notna()
            & (
                duration
                > duration_threshold
            )
        )

    else:

        delay_flag = pd.Series(
            False,
            index=df.index,
        )

    # =====================================================
    # 4. COST ANOMALY
    # =====================================================

    cost_flag = (
        cost_deviation
        .fillna(0)
        .gt(50)
    )

    # =====================================================
    # 5. DUPLICATE / OVERLAP
    # =====================================================

    overlap_flag = (
        (overlap_score >= 75)
        | (overlap_count >= 2)
    )

    # =====================================================
    # 6. DATA QUALITY
    # =====================================================

    recommended_amount = _num(
        _get_column(
            df,
            "Recommended_Amount",
            np.nan,
        )
    )

    sanction_amount = _num(
        _get_column(
            df,
            "Sanction_Amount",
            np.nan,
        )
    )

    sanction_date = pd.to_datetime(
        _get_column(
            df,
            "Sanction_Date",
            pd.NaT,
        ),
        errors="coerce",
    )

    core_missing = (
        recommended_amount.isna()
        | sanction_amount.isna()
        | sanction_date.isna()
    )

    evidence_missing = (
        df["Completion_Evidence_Missing"]
        .fillna(False)
        .astype(bool)
    )

    data_quality_flag = (
        core_missing
        | (
            status_completed
            & evidence_missing
        )
    )

    # =====================================================
    # STORE FLAGS
    # =====================================================

    df["Financial_Anomaly_Flag"] = (
        financial_flag.astype(bool)
    )

    df["Progress_Mismatch_Flag"] = (
        progress_mismatch.astype(bool)
    )

    df["Delay_Risk_Flag"] = (
        delay_flag.astype(bool)
    )

    df["Cost_Anomaly_Flag"] = (
        cost_flag.astype(bool)
    )

    df["Duplicate_Overlap_Flag"] = (
        overlap_flag.astype(bool)
    )

    df["Data_Quality_Flag"] = (
        data_quality_flag.astype(bool)
    )

    # =====================================================
    # RISK POINTS — SEVERITY BASED
    # =====================================================

    # -----------------------------------------------------
    # 1. FINANCIAL ANOMALY
    # -----------------------------------------------------

    financial_gap_abs = (
        financial_gap
        .abs()
        .fillna(0)
    )

    df["Financial_Risk_Points"] = 0

    df.loc[
        financial_gap_abs > 20,
        "Financial_Risk_Points",
    ] = 10

    df.loc[
        financial_gap_abs > 50,
        "Financial_Risk_Points",
    ] = 15

    df.loc[
        financial_gap_abs > 100,
        "Financial_Risk_Points",
    ] = 20

    # -----------------------------------------------------
    # 2. PROGRESS MISMATCH
    # -----------------------------------------------------

    df["Progress_Risk_Points"] = (
        progress_mismatch.astype(int) * 20
    )

    # -----------------------------------------------------
    # 3. DELAY RISK
    # -----------------------------------------------------

    df["Delay_Risk_Points"] = (
        delay_flag.astype(int) * 20
    )

    # -----------------------------------------------------
    # 4. COST ANOMALY — SEVERITY BASED
    # -----------------------------------------------------

    cost_deviation_abs = (
        cost_deviation
        .abs()
        .fillna(0)
    )

    df["Cost_Risk_Points"] = 0

    df.loc[
        cost_deviation_abs > 50,
        "Cost_Risk_Points",
    ] = 10

    df.loc[
        cost_deviation_abs > 100,
        "Cost_Risk_Points",
    ] = 15

    df.loc[
        cost_deviation_abs > 200,
        "Cost_Risk_Points",
    ] = 20

    df.loc[
        cost_deviation_abs > 300,
        "Cost_Risk_Points",
    ] = 25

    # -----------------------------------------------------
    # 5. DUPLICATE / OVERLAP — SEVERITY BASED
    # -----------------------------------------------------

    df["Overlap_Risk_Points"] = 0

    # Similarity 75–84.99
    df.loc[
        overlap_score >= 75,
        "Overlap_Risk_Points",
    ] = 10

    # Similarity 85–89.99
    df.loc[
        overlap_score >= 85,
        "Overlap_Risk_Points",
    ] = 15

    # Similarity 90–94.99
    df.loc[
        overlap_score >= 90,
        "Overlap_Risk_Points",
    ] = 20

    # Similarity >=95
    df.loc[
        overlap_score >= 95,
        "Overlap_Risk_Points",
    ] = 25

    # -----------------------------------------------------
    # Additional overlap count
    # -----------------------------------------------------

    # Multiple related projects increase review priority.
    #
    # 2–4 overlaps    → +2
    # 5–9 overlaps    → +4
    # 10–19 overlaps  → +6
    # 20–49 overlaps  → +8
    # 50+ overlaps    → +10
    #
    # Maximum additional points = 10.

    additional_overlap_points = pd.Series(
        0,
        index=df.index,
        dtype=int,
    )

    additional_overlap_points.loc[
        overlap_count >= 2
    ] = 2

    additional_overlap_points.loc[
        overlap_count >= 5
    ] = 4

    additional_overlap_points.loc[
        overlap_count >= 10
    ] = 6

    additional_overlap_points.loc[
        overlap_count >= 20
    ] = 8

    additional_overlap_points.loc[
        overlap_count >= 50
    ] = 10

    df["Overlap_Risk_Points"] = (
        df["Overlap_Risk_Points"]
        + additional_overlap_points
    ).clip(
        upper=35
    )

    # -----------------------------------------------------
    # 6. DATA QUALITY
    # -----------------------------------------------------

    df["Data_Quality_Risk_Points"] = (
        data_quality_flag.astype(int) * 10
    )

    # =====================================================
    # FINAL SCORE
    # =====================================================

    df["Risk_Score"] = (
        df["Financial_Risk_Points"]
        + df["Progress_Risk_Points"]
        + df["Delay_Risk_Points"]
        + df["Cost_Risk_Points"]
        + df["Overlap_Risk_Points"]
        + df["Data_Quality_Risk_Points"]
    )

    df["Risk_Score"] = (
        df["Risk_Score"]
        .clip(
            lower=0,
            upper=100,
        )
        .astype(int)
    )

    # =====================================================
    # RISK CATEGORY
    # =====================================================

    # 0–30   = Low
    # 31–60  = Medium
    # 61–80  = High
    # 81–100 = Critical

    df["Risk_Category"] = "Low"

    df.loc[
        df["Risk_Score"].between(
            31,
            60,
        ),
        "Risk_Category",
    ] = "Medium"

    df.loc[
        df["Risk_Score"].between(
            61,
            80,
        ),
        "Risk_Category",
    ] = "High"

    df.loc[
        df["Risk_Score"] >= 81,
        "Risk_Category",
    ] = "Critical"

    # =====================================================
    # EXPLAINABLE REASONS
    # =====================================================

    def build_reasons(
        row: pd.Series,
    ) -> str:

        reasons: List[str] = []

        # -------------------------------------------------
        # Financial
        # -------------------------------------------------

        if row["Financial_Anomaly_Flag"]:

            gap = row[
                "Recommendation_Sanction_Gap_Percent"
            ]

            if pd.notna(gap):

                reasons.append(
                    "Recommendation/sanction amount "
                    f"deviation is "
                    f"{abs(float(gap)):.1f}%"
                )

            else:

                reasons.append(
                    "Financial amount inconsistency detected"
                )

        # -------------------------------------------------
        # Progress
        # -------------------------------------------------

        if row["Progress_Mismatch_Flag"]:

            reasons.append(
                "Project is marked completed but "
                "completion information is incomplete"
            )

        # -------------------------------------------------
        # Delay
        # -------------------------------------------------

        if row["Delay_Risk_Flag"]:

            reasons.append(
                "Project completion duration is unusually "
                "high compared with the dataset"
            )

        # -------------------------------------------------
        # Cost
        # -------------------------------------------------

        if row["Cost_Anomaly_Flag"]:

            deviation = row[
                "Cost_Deviation_Percent"
            ]

            if pd.notna(deviation):

                reasons.append(
                    "Sanction amount is "
                    f"{float(deviation):.1f}% above "
                    "the peer-group benchmark"
                )

        # -------------------------------------------------
        # Overlap
        # -------------------------------------------------

        if row["Duplicate_Overlap_Flag"]:

            overlap_count_value = row[
                "Potential_Overlap_Count"
            ]

            if pd.notna(
                overlap_count_value
            ):

                reasons.append(
                    "Potential overlap with "
                    f"{int(overlap_count_value)} "
                    "related project(s)"
                )

            else:

                reasons.append(
                    "Potential project overlap detected"
                )

        # -------------------------------------------------
        # Data quality
        # -------------------------------------------------

        if row["Data_Quality_Flag"]:

            reasons.append(
                "Important project or monitoring "
                "information is missing"
            )

        # -------------------------------------------------
        # No signals
        # -------------------------------------------------

        if not reasons:

            return (
                "No major screening signals detected"
            )

        return "; ".join(
            reasons
        )

    df["Risk_Reasons"] = df.apply(
        build_reasons,
        axis=1,
    )

    return df