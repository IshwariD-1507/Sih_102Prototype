import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from mplads.features.location_extraction import (
    create_location_features
)


INPUT_FILE = "data/processed/project_features.csv"


def main():
    print("Loading project features...")

    df = pd.read_csv(
        INPUT_FILE,
        low_memory=False
    )

    print(f"Projects loaded: {len(df):,}")

    print("\nCreating location features...")

    df = create_location_features(df)

    print("\nLocation extraction summary:")
    print(
        df["Location_Confidence"]
        .value_counts(dropna=False)
    )

    print("\nLocation source summary:")
    print(
        df["Location_Source"]
        .value_counts(dropna=False)
    )

    print("\nProjects with extracted district:")
    print(
        df["Extracted_District"]
        .astype(str)
        .str.strip()
        .ne("")
        .sum()
    )

    print("\nProjects with extracted place:")
    print(
        df["Extracted_Place"]
        .astype(str)
        .str.strip()
        .ne("")
        .sum()
    )

    print("\nSample extracted locations:")

    sample = df[
        df["Extracted_District"].astype(str).str.strip().ne("")
        | df["Extracted_Place"].astype(str).str.strip().ne("")
    ][
        [
            "Work_ID",
            "State",
            "IDA",
            "Constituency",
            "Work_Description",
            "Extracted_District",
            "Extracted_Place",
            "Location_Confidence",
            "Location_Source",
        ]
    ].head(20)

    print(sample.to_string(index=False))


if __name__ == "__main__":
    main()