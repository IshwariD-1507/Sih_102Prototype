import pandas as pd


def create_cost_features(df):
    """
    Create cost-anomaly features by comparing a project
    with other projects in the same state and work category.

    This is a statistical screening signal, not a finding
    of financial misconduct.
    """

    df = df.copy()

    # ---------------------------------------------------------
    # 1. Create peer-group identifier
    # ---------------------------------------------------------
    #
    # Projects are compared primarily with projects having
    # the same State + Work Category.
    #

    df["Cost_Peer_Group"] = (
        df["State"].astype("string").fillna("UNKNOWN")
        + " | "
        + df["Work_Category"].astype("string").fillna("UNKNOWN")
    )

    # ---------------------------------------------------------
    # 2. Median sanctioned amount of peer group
    # ---------------------------------------------------------

    peer_median = (
        df.groupby("Cost_Peer_Group")["Sanction_Amount"]
        .transform("median")
    )

    df["Peer_Median_Sanction_Amount"] = peer_median

    # ---------------------------------------------------------
    # 3. Difference from peer median
    # ---------------------------------------------------------

    df["Cost_Deviation_From_Peer_Median"] = (
        df["Sanction_Amount"]
        - df["Peer_Median_Sanction_Amount"]
    )

    # ---------------------------------------------------------
    # 4. Percentage deviation
    # ---------------------------------------------------------

    df["Cost_Deviation_Percent"] = (
        df["Cost_Deviation_From_Peer_Median"]
        / df["Peer_Median_Sanction_Amount"]
    ) * 100

    df["Cost_Deviation_Percent"] = (
        df["Cost_Deviation_Percent"]
        .replace(
            [float("inf"), -float("inf")],
            pd.NA
        )
    )

    # ---------------------------------------------------------
    # 5. Flag unusually high cost
    # ---------------------------------------------------------
    #
    # Prototype threshold:
    # 50% above peer median.
    #
    # This is a screening threshold chosen for the prototype,
    # NOT an official MPLADS threshold.
    #

    df["High_Cost_Deviation"] = (
        df["Cost_Deviation_Percent"] > 50
    )

    return df
