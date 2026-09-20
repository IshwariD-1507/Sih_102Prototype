import sys
from pathlib import Path

import pandas as pd

# Add src to Python path
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))

from mplads.data.unify import build_unified_projects


RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"


def main():

    print("\nLoading raw datasets...\n")

    recommended = pd.read_csv(
        RAW_DIR / "Works Recommended.csv"
    )

    sanctioned = pd.read_csv(
        RAW_DIR / "Works Sanctioned.csv"
    )

    completed = pd.read_csv(
        RAW_DIR / "Works Completed.csv"
    )

    print("Recommended:", recommended.shape)
    print("Sanctioned:", sanctioned.shape)
    print("Completed:", completed.shape)

    print("\nBuilding unified project dataset...\n")

    unified = build_unified_projects(
        recommended,
        sanctioned,
        completed
    )

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        PROCESSED_DIR /
        "unified_projects.csv"
    )

    unified.to_csv(
        output_path,
        index=False
    )

    print("Unified dataset created!")
    print(f"Saved to: {output_path}")

    print("\nFinal shape:")
    print(unified.shape)

    print("\nColumns:")
    for column in unified.columns:
        print(" -", column)

    print("\nMissing values:")
    print(unified.isna().sum())

    print("\nFirst 5 rows:")
    print(unified.head().to_string(index=False))


if __name__ == "__main__":
    main()
