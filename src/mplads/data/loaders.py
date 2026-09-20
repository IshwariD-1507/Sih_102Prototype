from pathlib import Path
import pandas as pd


def load_csv(path):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return pd.read_csv(path)


def load_all_raw_data(raw_dir):
    raw_dir = Path(raw_dir)

    files = list(raw_dir.glob("*.csv"))

    if not files:
        raise FileNotFoundError(
            f"No CSV files found in {raw_dir}"
        )

    datasets = {}

    for file in files:
        datasets[file.stem.lower()] = load_csv(file)

    return datasets
