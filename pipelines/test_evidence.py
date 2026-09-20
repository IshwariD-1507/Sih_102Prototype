import sys
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]

SRC_DIR = ROOT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))


from mplads.features.evidence import create_evidence_features


INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "project_features.csv"
)


def main():

    print("\nLoading project data...")

    df = pd.read_csv(INPUT_FILE)

    print(
        f"Testing evidence features on "
        f"{len(df)} projects..."
    )

    # ---------------------------------------------------------
    # Create evidence features
    # ---------------------------------------------------------

    result = create_evidence_features(df)

    # ---------------------------------------------------------
    # Output
    # ---------------------------------------------------------

    print("\nEvidence Risk:")

    print(
        result["Evidence_Risk"]
        .value_counts(dropna=False)
    )

    print("\nCompleted Without Evidence:")

    print(
        result["Completed_Without_Evidence"]
        .value_counts(dropna=False)
    )

    print("\nSample results:")

    print(
        result[
            [
                "Work_ID",
                "Progress_Status",
                "Has_Completion_Image",
                "Completion_Evidence_Missing",
                "Evidence_Risk",
                "Completed_Without_Evidence",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()