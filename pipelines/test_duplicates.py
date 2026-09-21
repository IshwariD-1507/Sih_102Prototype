import sys
from pathlib import Path

import pandas as pd


# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from mplads.models.duplicates import DuplicateDetector


# =========================================================
# FILES
# =========================================================

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
    / "duplicate_candidates.csv"
)


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "\n=============================================="
    )

    print(
        "MPLADS DUPLICATE / OVERLAP DETECTION"
    )

    print(
        "==============================================\n"
    )

    # -----------------------------------------------------
    # Check input
    # -----------------------------------------------------

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "Unified project dataset not found.\n\n"
            "Run:\n"
            "    python pipelines/build_dataset.py\n\n"
            f"Expected:\n{INPUT_FILE}"
        )

    # -----------------------------------------------------
    # Load unified dataset
    # -----------------------------------------------------

    print(
        "Loading unified project dataset..."
    )

    df = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"Loaded {len(df):,} projects."
    )

    # -----------------------------------------------------
    # Detector
    # -----------------------------------------------------

    print(
        "\nLoading semantic similarity model..."
    )

    detector = DuplicateDetector()

    # -----------------------------------------------------
    # Detect candidates
    # -----------------------------------------------------

    print(
        "\nSearching for potential overlaps..."
    )

    results = detector.find_similar_projects(
        df,
        threshold=0.80,
    )

    # -----------------------------------------------------
    # Calculate overlap score
    # -----------------------------------------------------

    if not results.empty:

        results = (
            detector
            .calculate_overlap_score(
                results
            )
        )

    else:

        # Preserve a useful empty schema
        results = pd.DataFrame(
            columns=[
                "Work_ID_A",
                "Work_ID_B",
                "State",
                "Work_Category",
                "district",
                "Description_A",
                "Description_B",
                "Semantic_Similarity",
                "Sanction_Amount_A",
                "Sanction_Amount_B",
                "Sanction_Date_A",
                "Sanction_Date_B",
                "Cost_Similarity",
                "Date_Similarity",
                "Overlap_Score",
                "Review_Category",
            ]
        )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    results.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print(
        "\n=============================================="
    )

    print(
        "RESULT"
    )

    print(
        "=============================================="
    )

    print(
        f"Potential candidate pairs: "
        f"{len(results):,}"
    )

    print(
        f"Saved to:\n{OUTPUT_FILE}"
    )

    if not results.empty:

        print(
            "\nReview category distribution:"
        )

        print(
            results[
                "Review_Category"
            ]
            .value_counts()
            .to_string()
        )

        print(
            "\nTop candidates:"
        )

        print(
            results
            .sort_values(
                "Overlap_Score",
                ascending=False,
            )
            .head(10)
            .to_string(
                index=False
            )
        )

    else:

        print(
            "\nNo potential overlap candidates "
            "were found at the current threshold."
        )


if __name__ == "__main__":
    main()