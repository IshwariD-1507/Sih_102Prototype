from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw")


files = list(RAW_DIR.glob("*.csv"))

print(f"\nFound {len(files)} CSV files.\n")


for file in files:

    print("=" * 80)
    print(f"FILE: {file.name}")
    print("=" * 80)

    df = pd.read_csv(file)

    print(f"Shape: {df.shape}")

    print("\nCOLUMNS:")
    for column in df.columns:
        print(f"  - {column}")

    print("\nMISSING VALUES:")
    print(df.isna().sum().to_string())

    print("\nFIRST 3 ROWS:")
    print(df.head(3).to_string(index=False))

    print("\n")