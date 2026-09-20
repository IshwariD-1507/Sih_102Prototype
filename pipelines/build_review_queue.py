import sys
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]

SRC_DIR = ROOT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))


INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "project_features.csv"
)


OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "review_queue.csv"
)


def main():

    print("\nLoading project feature data...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Projects loaded: {len(df)}")

    print("\nBuilding review queue...")

    review_queue = df[
        df["Risk_Category"].isin(
            ["Medium", "High", "Critical"]
        )
    ].copy()

    review_queue = review_queue.sort_values(
        ["Risk_Score", "Max_Overlap_Score"],
        ascending=False
    )

    review_queue.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nReview queue created!")

    print(
        f"Projects requiring review: "
        f"{len(review_queue)}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )

    print("\nReview queue categories:")

    print(
        review_queue["Risk_Category"]
        .value_counts()
    )

    print("\nTop review candidates:")

    print(
        review_queue[
            [
                "Work_ID",
                "Risk_Score",
                "Risk_Category",
                "Risk_Reasons",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()