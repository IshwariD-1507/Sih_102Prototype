import pandas as pd


def create_financial_features(df):
    """
    Create financial monitoring features for each MPLADS work.
    """

    df = df.copy()

    # ---------------------------------------------------------
    # 1. Recommendation → Sanction amount difference
    # ---------------------------------------------------------

    df["Recommendation_Sanction_Gap"] = (
        df["Sanction_Amount"]
        - df["Recommended_Amount"]
    )

    # Percentage difference relative to recommended amount
    df["Recommendation_Sanction_Gap_Percent"] = (
        df["Recommendation_Sanction_Gap"]
        / df["Recommended_Amount"]
    ) * 100

    # Avoid infinite values
    df["Recommendation_Sanction_Gap_Percent"] = (
        df["Recommendation_Sanction_Gap_Percent"]
        .replace([float("inf"), -float("inf")], pd.NA)
    )

    # ---------------------------------------------------------
    # 2. Disbursement / sanctioned amount
    # ---------------------------------------------------------

    df["Utilisation_Percent"] = (
        df["Amount_Disbursed"]
        / df["Sanction_Amount"]
    ) * 100

    df["Utilisation_Percent"] = (
        df["Utilisation_Percent"]
        .replace([float("inf"), -float("inf")], pd.NA)
    )

    # ---------------------------------------------------------
    # 3. Amount remaining
    # ---------------------------------------------------------

    df["Amount_Remaining"] = (
        df["Sanction_Amount"]
        - df["Amount_Disbursed"]
    )

    # ---------------------------------------------------------
    # 4. Basic financial flags
    # ---------------------------------------------------------

    df["Disbursement_Exceeds_Sanction"] = (
        df["Amount_Disbursed"]
        > df["Sanction_Amount"]
    )

    df["Sanction_Exceeds_Recommendation"] = (
        df["Sanction_Amount"]
        > df["Recommended_Amount"]
    )

    # ---------------------------------------------------------
    # 5. Missing financial information
    # ---------------------------------------------------------

    df["Missing_Disbursement_Data"] = (
        df["Amount_Disbursed"].isna()
    )

    df["Missing_Recommendation_Data"] = (
        df["Recommended_Amount"].isna()
    )

    return df
