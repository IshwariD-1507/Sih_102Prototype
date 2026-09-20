import sys
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]

SRC_DIR = ROOT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))


from mplads.features.overlap import create_overlap_features


PROJECT_FILE = (
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

    print("\nLoading project data...")

    df = pd.read_csv(PROJECT_FILE)

    print(
        f"Projects loaded: {len(df)}"
    )

    print("\nLoading duplicate candidates...")

    duplicate_candidates = pd.read_csv(
        DUPLICATE_FILE
    )

    print(
        f"Potential overlap pairs: "
        f"{len(duplicate_candidates)}"
    )

    # ---------------------------------------------------------
    # Create overlap features
    # ---------------------------------------------------------

    result = create_overlap_features(
        df,
        duplicate_candidates
    )

    # ---------------------------------------------------------
    # Output checks
    # ---------------------------------------------------------

    print("\nPotential Overlap:")

    print(
        result["Has_Potential_Overlap"]
        .value_counts(dropna=False)
    )

    print("\nOverlap Count:")

    print(
        result["Potential_Overlap_Count"]
        .describe()
    )

    print("\nMaximum Overlap Score:")

    print(
        result["Max_Overlap_Score"]
        .describe()
    )

    # ---------------------------------------------------------
    # Top projects
    # ---------------------------------------------------------

    print("\nTop projects by overlap score:")

    print(
        result[
            [
                "Work_ID",
                "Potential_Overlap_Count",
                "Max_Overlap_Score",
                "Has_Potential_Overlap",
            ]
        ]
        .sort_values(
            "Max_Overlap_Score",
            ascending=False
        )
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()