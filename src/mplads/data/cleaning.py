import pandas as pd


def clean_column_names(df):
    """
    Remove unnecessary spaces/tabs from column names.
    """
    df = df.copy()

    df.columns = (
        df.columns
        .str.replace("\t", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    return df


def clean_text_columns(df):
    """
    Clean whitespace and tabs inside text columns.
    """
    df = df.copy()

    for column in df.select_dtypes(include="object").columns:
        df[column] = (
            df[column]
            .astype(str)
            .str.replace("\t", " ", regex=False)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

        # Convert the string "nan" back to actual missing values
        df[column] = df[column].replace("nan", pd.NA)

    return df


def clean_dates(df, date_columns):
    """
    Convert specified columns into datetime.
    """
    df = df.copy()

    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce",
                dayfirst=True
            )

    return df


def clean_amount_columns(df, amount_columns):
    """
    Convert monetary columns to numeric values.
    """
    df = df.copy()

    for column in amount_columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("₹", "", regex=False)
                .str.strip()
            )

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df
def normalize_work_id(df):
    """
    Standardize Work IDs so the same work can be matched
    across Recommended, Sanctioned and Completed datasets.
    """

    df = df.copy()

    if "Work_ID" in df.columns:
        df["Work_ID"] = (
            df["Work_ID"]
            .astype("string")
            .str.replace(r"\s+", "", regex=True)
            .str.strip()
        )

    return df
