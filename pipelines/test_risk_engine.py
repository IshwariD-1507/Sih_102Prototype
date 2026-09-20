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
# Import risk engine
# ---------------------------------------------------------

from mplads.models.risk_engine import create_risk_features


# ---------------------------------------------------------
# Input
# ---------------------------------------------------------

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "project_features.csv"
)


def main():

    print("\nLoading project feature data...")

    df = pd.read_csv(INPUT_FILE)

    print(
        f"Projects loaded: {len(df)}"
    )

    # -----------------------------------------------------
    # Create risk features
    # -----------------------------------------------------

    print("\nCreating risk features...")

    result = create_risk_features(df)

    # -----------------------------------------------------
    # Risk category distribution
    # -----------------------------------------------------

    print("\nRisk Category:")

    print(
        result["Risk_Category"]
        .value_counts(dropna=False)
    )

    # -----------------------------------------------------
    # Risk score statistics
    # -----------------------------------------------------

    print("\nRisk Score:")

    print(
        result["Risk_Score"]
        .describe()
    )

    # -----------------------------------------------------
    # Top projects
    # -----------------------------------------------------

    print("\nTop projects by risk score:")

    print(
        result[
            [
                "Work_ID",
                "Risk_Score",
                "Risk_Category",
                "Risk_Reasons",
            ]
        ]
        .sort_values(
            "Risk_Score",
            ascending=False
        )
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()