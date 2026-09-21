from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd


WEIGHTS = {
    "financial_anomaly": 20,
    "progress_mismatch": 25,
    "delay_risk": 20,
    "cost_anomaly": 15,
    "duplicate_overlap": 10,
    "data_quality": 10,
}


def _num(series: pd.Series) -> pd.Series:

    return pd.to_numeric(
        series,
        errors="coerce"
    )


def create_risk_features(
    df: pd.DataFrame
) -> pd.DataFrame:

    """
    Create an explainable project-level screening risk score.

    This score identifies projects that may deserve review.
    It does NOT establish fraud, corruption, misuse, or misconduct.
    """

    df = df.copy()

    # ---------------------------------------------------------
    # Ensure optional columns exist
    # ---------------------------------------------------------

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

    if "Work_Status" not in df.columns:

        df["Work_Status"] = ""

    if "Completion_Date" not in df.columns:

        df["Completion_Date"] = pd.NaT

    if "Has_Completion_Image" not in df.columns:

        df["Has_Completion_Image"] = False

    if "Completion_Evidence_Missing" not in df.columns:

        df["Completion_Evidence_Missing"] = True

    # ---------------------------------------------------------
    # Base signals
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # 1. Financial anomaly
    # ---------------------------------------------------------

    disbursement_exceeds = (
        df.get(
            "Disbursement_Exceeds_Sanction",
            pd.Series(
                False,
                index=df.index
            )
        )
        .fillna(False)
        .astype(bool)
    )

    financial_flag = (
        financial_gap.abs().gt(20)
        | disbursement_exceeds
    )

    # ---------------------------------------------------------
    # 2. Progress mismatch
    # ---------------------------------------------------------

    status = (
        df["Work_Status"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    status_completed = status.str.contains(
        "work completed",
        na=False
    )

    completion_missing = (
        df["Completion_Date"].isna()
    )

    progress_mismatch = (
        status_completed
        & completion_missing
    ) | (
        status.str.contains(
            "sanction|vendor|inspection|time estimation",
            regex=True,
            na=False
        )
        & df["Completion_Date"].notna()
    )

    # ---------------------------------------------------------
    # 3. Delay signal
    # ---------------------------------------------------------

    if duration.notna().any():

        duration_threshold = duration.quantile(0.90)

        delay_flag = (
            duration.notna()
            & (duration > duration_threshold)
        )

    else:

        delay_flag = pd.Series(
            False,
            index=df.index
        )

    # ---------------------------------------------------------
    # 4. Cost anomaly
    # ---------------------------------------------------------

    cost_flag = (
        cost_deviation > 50
    )

    # ---------------------------------------------------------
    # 5. Duplicate / overlap
    # ---------------------------------------------------------

    overlap_flag = (
        (overlap_score >= 75)
        | (overlap_count >= 2)
    )

    # ---------------------------------------------------------
    # 6. Data quality
    # ---------------------------------------------------------

    recommended_amount = pd.to_numeric(
        df.get(
            "Recommended_Amount",
            pd.Series(np.nan, index=df.index)
        ),
        errors="coerce"
    )

    sanction_amount = pd.to_numeric(
        df.get(
            "Sanction_Amount",
            pd.Series(np.nan, index=df.index)
        ),
        errors="coerce"
    )

    sanction_date = pd.to_datetime(
        df.get(
            "Sanction_Date",
            pd.Series(pd.NaT, index=df.index)
        ),
        errors="coerce"
    )

    core_missing = (
        recommended_amount.isna()
        | sanction_amount.isna()
        | sanction_date.isna()
    )

    evidence_missing = (
        df["Completion_Evidence_Missing"]
        .fillna(True)
    )

    data_quality_flag = (
        core_missing
        | (
            status_completed
            & evidence_missing
        )
    )

    # ---------------------------------------------------------
    # Store flags
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Risk points
    # ---------------------------------------------------------

    df["Financial_Risk_Points"] = (
        financial_flag.astype(int)
        * WEIGHTS["financial_anomaly"]
    )

    df["Progress_Risk_Points"] = (
        progress_mismatch.astype(int)
        * WEIGHTS["progress_mismatch"]
    )

    df["Delay_Risk_Points"] = (
        delay_flag.astype(int)
        * WEIGHTS["delay_risk"]
    )

    df["Cost_Risk_Points"] = (
        cost_flag.astype(int)
        * WEIGHTS["cost_anomaly"]
    )

    df["Overlap_Risk_Points"] = (
        overlap_flag.astype(int)
        * WEIGHTS["duplicate_overlap"]
    )

    df["Data_Quality_Risk_Points"] = (
        data_quality_flag.astype(int)
        * WEIGHTS["data_quality"]
    )

    # ---------------------------------------------------------
    # Final score
    # ---------------------------------------------------------

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
        .clip(0, 100)
        .astype(int)
    )

    # ---------------------------------------------------------
    # Risk category
    # ---------------------------------------------------------

    df["Risk_Category"] = "Low"

    df.loc[
        df["Risk_Score"].between(31, 60),
        "Risk_Category"
    ] = "Elevated"

    df.loc[
        df["Risk_Score"].between(61, 80),
        "Risk_Category"
    ] = "High"

    df.loc[
        df["Risk_Score"] >= 81,
        "Risk_Category"
    ] = "Critical"

    # ---------------------------------------------------------
    # Explainable reasons
    # ---------------------------------------------------------

    def build_reasons(
        row: pd.Series
    ) -> str:

        reasons: List[str] = []

        if row["Financial_Anomaly_Flag"]:

            gap = row[
                "Recommendation_Sanction_Gap_Percent"
            ]

            if pd.notna(gap):

                reasons.append(
                    "Recommendation/sanction amount "
                    f"deviation is {abs(float(gap)):.1f}%"
                )

            else:

                reasons.append(
                    "Financial amount inconsistency detected"
                )

        if row["Progress_Mismatch_Flag"]:

            reasons.append(
                "Project status and completion "
                "information are inconsistent"
            )

        if row["Delay_Risk_Flag"]:

            reasons.append(
                "Completed project duration is unusually "
                "high compared with the dataset"
            )

        if row["Cost_Anomaly_Flag"]:

            deviation = row[
                "Cost_Deviation_Percent"
            ]

            reasons.append(
                f"Sanction amount is {float(deviation):.1f}% "
                "above the peer-group median"
            )

        if row["Duplicate_Overlap_Flag"]:

            reasons.append(
                "Potential overlap with "
                f"{int(row['Potential_Overlap_Count'])} "
                "related project(s)"
            )

        if row["Data_Quality_Flag"]:

            reasons.append(
                "Important monitoring or evidence "
                "data is missing or inconsistent"
            )

        if not reasons:

            return (
                "No major screening signals detected"
            )

        return "; ".join(reasons)

    df["Risk_Reasons"] = df.apply(
        build_reasons,
        axis=1
    )

    return df