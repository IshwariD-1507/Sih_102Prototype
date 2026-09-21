import sys
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from mplads.features.cost import create_cost_features
from mplads.features.delay_features import create_delay_features
from mplads.features.evidence import create_evidence_features
from mplads.features.financial import create_financial_features
from mplads.features.overlap import create_overlap_features
from mplads.features.progress import create_progress_features
from mplads.risk.engine import create_risk_features


PROCESSED_DIR = ROOT_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "unified_projects.csv"
OUTPUT_FILE = PROCESSED_DIR / "project_features.csv"
DUPLICATE_FILE = PROCESSED_DIR / "duplicate_candidates.csv"


def load_duplicate_candidates() -> pd.DataFrame:
    """
    Load duplicate candidates if they already exist.

    Duplicate detection is optional at this stage, so the feature
    pipeline can still run before duplicate_candidates.csv exists.
    """

    if not DUPLICATE_FILE.exists():

        print(
            "\nNo duplicate_candidates.csv found."
        )

        print(
            "Overlap features will initially be zero."
        )

        print(
            "Run duplicate detection later and rerun "
            "build_features.py to populate overlap signals."
        )

        return pd.DataFrame()

    try:

        return pd.read_csv(DUPLICATE_FILE)

    except Exception as exc:

        print(
            f"\nWarning: could not read duplicate candidates: {exc}"
        )

        return pd.DataFrame()


def main():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "Unified dataset not found.\n\n"
            "Run:\n"
            "    python pipelines/build_dataset.py\n\n"
            f"Expected file:\n{INPUT_FILE}"
        )

    print("\nLoading unified project dataset...\n")

    df = pd.read_csv(INPUT_FILE)

    duplicate_candidates = load_duplicate_candidates()

    print("Input shape:", df.shape)

    print(
        "Duplicate candidates:",
        len(duplicate_candidates)
    )

    print("\nCreating financial features...")

    df = create_financial_features(df)

    print("Creating lifecycle features...")

    df = create_delay_features(df)

    print("Creating progress features...")

    df = create_progress_features(df)

    print("Creating evidence features...")

    df = create_evidence_features(df)

    print("Creating cost features...")

    df = create_cost_features(df)

    print("Creating overlap features...")

    df = create_overlap_features(
        df,
        duplicate_candidates
    )

    print("Creating risk features...")

    df = create_risk_features(df)

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nFeature dataset created!")

    print(
        f"Saved to: {OUTPUT_FILE}"
    )

    print(
        "Final shape:",
        df.shape
    )

    print("\nRisk category distribution:")

    print(
        df["Risk_Category"]
        .value_counts(dropna=False)
        .to_string()
    )

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
        "Risk_Score",
        "Risk_Category",
    ]

    available_columns = [
        column
        for column in sample_columns
        if column in df.columns
    ]

    print(
        df[available_columns]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()