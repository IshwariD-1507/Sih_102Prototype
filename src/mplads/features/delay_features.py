import pandas as pd


def create_delay_features(df):
    """
    Create project lifecycle and duration features.

    These features describe how long a project has taken.
    They do NOT claim that an incomplete project is officially delayed,
    because an official expected completion deadline is not available
    in the current dataset.
    """

    df = df.copy()

    # Make sure dates are datetime
    date_columns = [
        "Recommended_Date",
        "Sanction_Date",
        "Completion_Date",
    ]

    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    # ---------------------------------------------------------
    # 1. Recommendation → Sanction duration
    # ---------------------------------------------------------

    df["Days_Recommendation_to_Sanction"] = (
        df["Sanction_Date"]
        - df["Recommended_Date"]
    ).dt.days

    # ---------------------------------------------------------
    # 2. Sanction → Completion duration
    # ---------------------------------------------------------

    df["Days_Sanction_to_Completion"] = (
        df["Completion_Date"]
        - df["Sanction_Date"]
    ).dt.days

    # ---------------------------------------------------------
    # 3. Total lifecycle duration
    # ---------------------------------------------------------

    df["Days_Recommendation_to_Completion"] = (
        df["Completion_Date"]
        - df["Recommended_Date"]
    ).dt.days

    # ---------------------------------------------------------
    # 4. Completion status
    # ---------------------------------------------------------

    df["Is_Completed"] = (
        df["Completion_Date"].notna()
    )

    # ---------------------------------------------------------
    # 5. Missing completion information
    # ---------------------------------------------------------

    df["Missing_Completion_Data"] = (
        df["Completion_Date"].isna()
    )

    return df
