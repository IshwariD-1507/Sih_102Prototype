from pathlib import Path
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 50)
pd.set_option("display.max_colwidth", 40)

for f in sorted(Path("data/raw").iterdir()):
    if f.suffix.lower() not in (".csv", ".xlsx"):
        continue
    print("\n" + "=" * 80, f.name)
    try:
        if f.suffix.lower() == ".csv":
            for enc in ("utf-8", "utf-8-sig", "latin-1"):
                try:
                    df = pd.read_csv(f, encoding=enc, low_memory=False); break
                except UnicodeDecodeError:
                    continue
        else:
            df = pd.read_excel(f, nrows=200000)
        print("rows:", len(df), "| columns:", len(df.columns))
        print(df.dtypes.to_string())
        print(df.head(3).to_string())
        print("missing values per column:\n", df.isna().sum()[df.isna().sum() > 0].to_string())
    except Exception as e:
        print("could not read:", e)