import pandas as pd

from mplads.data.cleaning import (
    clean_column_names,
    clean_text_columns,
    clean_dates,
    clean_amount_columns,
    normalize_work_id,
)


def prepare_recommended(df):
    df = clean_column_names(df)
    df = clean_text_columns(df)
    

    df = clean_dates(
        df,
        ["Recommended date", "Sanction Date"]
    )

    df = clean_amount_columns(
        df,
        ["RECOMMENDED AMOUNT ( ₹ )"]
    )

    df = df.rename(
        columns={
            "WORK": "Work_ID",
            "Work category": "Work_Category",
            "Work description": "Work_Description",
            "Hon'ble Members of Parliament": "MP",
            "RECOMMENDED AMOUNT ( ₹ )": "Recommended_Amount",
            "Recommended date": "Recommended_Date",
            "Sanction Date": "Sanction_Date",
        }
    )
    df = normalize_work_id(df)
    return df


def prepare_sanctioned(df):
    df = clean_column_names(df)
    df = clean_text_columns(df)
    

    df = clean_dates(
        df,
        ["Recommended date", "Sanction Date"]
    )

    df = clean_amount_columns(
        df,
        ["Sanction Amount ( ₹ )"]
    )

    df = df.rename(
        columns={
            "Work": "Work_ID",
            "Work category": "Work_Category",
            "Work description": "Work_Description",
            "Hon'ble Members of Parliament": "MP",
            "Recommended date": "Recommended_Date",
            "Sanction Date": "Sanction_Date",
            "Sanction Amount ( ₹ )": "Sanction_Amount",
            "Work Status": "Work_Status",
        }
    )
    df = normalize_work_id(df)
    return df


def prepare_completed(df):
    df = clean_column_names(df)
    df = clean_text_columns(df)
    

    df = clean_dates(
        df,
        ["Completion Date"]
    )

    df = clean_amount_columns(
        df,
        ["Amount Disbursed ( ₹ )"]
    )

    df = df.rename(
        columns={
            "Work": "Work_ID",
            "Work Category": "Work_Category",
            "Work Description": "Work_Description",
            "Hon'ble Members of Parliament": "MP",
            "Completion Date": "Completion_Date",
            "Amount Disbursed ( ₹ )": "Amount_Disbursed",
        }
    )
    df = normalize_work_id(df)
    return df


def build_unified_projects(
    recommended,
    sanctioned,
    completed
):

    recommended = prepare_recommended(recommended)
    sanctioned = prepare_sanctioned(sanctioned)
    completed = prepare_completed(completed)

    # Keep only the useful columns from each dataset
    recommended = recommended[
        [
            "Work_ID",
            "Work_Category",
            "State",
            "IDA",
            "MP",
            "Constituency",
            "Work_Description",
            "Recommended_Date",
            "Recommended_Amount",
            "Sanction_Date",
        ]
    ]

    sanctioned = sanctioned[
        [
            "Work_ID",
            "Sanction_Date",
            "Sanction_Amount",
            "Work_Status",
        ]
    ]

    completed = completed[
        [
            "Work_ID",
            "Completion_Date",
            "Amount_Disbursed",
            "Image",
        ]
    ]

    # Remove accidental duplicate Work IDs before merging
    recommended = recommended.drop_duplicates(
        subset="Work_ID",
        keep="first"
    )

    sanctioned = sanctioned.drop_duplicates(
        subset="Work_ID",
        keep="first"
    )

    completed = completed.drop_duplicates(
        subset="Work_ID",
        keep="first"
    )

    # Start with recommended works
        # Start with ALL sanctioned works.
    # This ensures sanctioned projects are not lost.
    unified = sanctioned.merge(
        recommended,
        on="Work_ID",
        how="left",
        suffixes=("_sanctioned", "")
    )

    unified = unified.merge(
        completed,
        on="Work_ID",
        how="left"
    )

    # Prefer the sanctioned dataset's core project information
    # because it is our master project table.

    for column in [
        "Work_Category",
        "State",
        "IDA",
        "MP",
        "Constituency",
        "Work_Description"
    ]:

        sanctioned_column = f"{column}_sanctioned"

        if sanctioned_column in unified.columns:
            if column in unified.columns:
                unified[column] = (
                    unified[column]
                    .combine_first(unified[sanctioned_column])
                )

                unified = unified.drop(
                    columns=[sanctioned_column]
                )
            else:
                unified = unified.rename(
                    columns={
                        sanctioned_column: column
                    }
                )

    # Prefer the sanctioned date from the sanctioned dataset.
    if "Sanction_Date_sanctioned" in unified.columns:

        if "Sanction_Date" in unified.columns:
            unified["Sanction_Date"] = (
                unified["Sanction_Date_sanctioned"]
                .combine_first(unified["Sanction_Date"])
            )

            unified = unified.drop(
                columns=["Sanction_Date_sanctioned"]
            )

        else:
            unified = unified.rename(
                columns={
                    "Sanction_Date_sanctioned":
                    "Sanction_Date"
                }
            )

    return unified
