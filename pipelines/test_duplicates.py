import sys
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]

SRC_DIR = ROOT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))


from mplads.models.duplicates import DuplicateDetector


INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "project_features.csv"
)


def main():

    print("\nLoading project data...")

    df = pd.read_csv(INPUT_FILE)

    # -----------------------------------------------------
    # Use a small sample for the first test
    # -----------------------------------------------------

    sample = df.head(500).copy()

    print(
        f"Testing duplicate detection on "
        f"{len(sample)} projects..."
    )

    # -----------------------------------------------------
    # Detector
    # -----------------------------------------------------

    detector = DuplicateDetector()

    results = detector.find_similar_projects(
        sample,
        threshold=0.80
    )
    results = detector.calculate_overlap_score(results)
    # -----------------------------------------------------
    # Output
    # -----------------------------------------------------

    output_file = (
        ROOT_DIR
        / "data"
        / "processed"
        / "duplicate_candidates.csv"
    )

    results.to_csv(
        output_file,
        index=False
    )

    print("\nPotential overlaps found:")

    print(len(results))

    print(
        f"\nSaved to: {output_file}"
    )

    if len(results) > 0:

        print("\nTop candidates:")

        print(
            results
            .sort_values(
                "Semantic_Similarity",
                ascending=False
            )
            .head(10)
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()