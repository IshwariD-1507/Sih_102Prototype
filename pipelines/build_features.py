import sys
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]

SRC_DIR = ROOT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))


# ---------------------------------------------------------
# Import feature functions
# ---------------------------------------------------------
from mplads.models.risk_engine import create_risk_features
from mplads.features.overlap import create_overlap_features
from mplads.features.evidence import create_evidence_features
from mplads.features.financial import create_financial_features
from mplads.features.delay_features import create_delay_features
from mplads.features.progress import create_progress_features
from mplads.features.cost import create_cost_features


# ---------------------------------------------------------
# Input / output
# ---------------------------------------------------------

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "unified_projects.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "project_features.csv"
)
DUPLICATE_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "duplicate_candidates.csv"
)

def main():

    print("\nLoading unified project dataset...\n")

    df = pd.read_csv(INPUT_FILE)
    duplicate_candidates = pd.read_csv(
    DUPLICATE_FILE
)

    print("Input shape:", df.shape)

    # -----------------------------------------------------
    # Financial features
    # -----------------------------------------------------

    print("\nCreating financial features...")

    df = create_financial_features(df)

    # -----------------------------------------------------
    # Lifecycle / duration features
    # -----------------------------------------------------

    print("Creating lifecycle features...")

    df = create_delay_features(df)

    # -----------------------------------------------------
    # Progress / evidence features
    # -----------------------------------------------------

    print("Creating progress features...")

    df = create_progress_features(df)
    print("Creating evidence features...")

    df = create_evidence_features(df)
    print("Creating cost features...")

    df = create_cost_features(df)
    print("Creating overlap features...")

    df = create_overlap_features(
    df,
    duplicate_candidates)
    print("Creating risk features...")

    df = create_risk_features(df)
    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nFeature dataset created!")

    print(f"Saved to: {OUTPUT_FILE}")

    print("\nFinal shape:")
    print(df.shape)

    print("\nNew feature columns:")

    feature_columns = [
        "Recommendation_Sanction_Gap",
        "Recommendation_Sanction_Gap_Percent",
        "Utilisation_Percent",
        "Amount_Remaining",
        "Disbursement_Exceeds_Sanction",
        "Sanction_Exceeds_Recommendation",
        "Days_Recommendation_to_Sanction",
        "Days_Sanction_to_Completion",
        "Days_Recommendation_to_Completion",
        "Is_Completed",
        "Missing_Completion_Data",
        "Progress_Status",
        "Has_Completion_Image",
        "Completion_Evidence_Missing",
        "Evidence_Risk",
    "Completed_Without_Evidence",
        "Cost_Peer_Group",
    "Peer_Median_Sanction_Amount",
    "Cost_Deviation_From_Peer_Median",
    "Cost_Deviation_Percent",
    "High_Cost_Deviation",
    "Potential_Overlap_Count",
"Max_Overlap_Score",
"Has_Potential_Overlap",
"Risk_Score",
"Risk_Category",
"Risk_Reasons",
    ]

    for column in feature_columns:
        if column in df.columns:
            print(" -", column)

    print("\nSample:")

    sample_columns = [
        "Work_ID",
        "Recommended_Amount",
        "Sanction_Amount",
        "Amount_Disbursed",
        "Recommendation_Sanction_Gap_Percent",
        "Utilisation_Percent",
        "Days_Sanction_to_Completion",
        "Progress_Status",
        "Has_Completion_Image",
    ]

    print(
        df[sample_columns]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()