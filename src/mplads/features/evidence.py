import pandas as pd


def create_evidence_features(df):
    """
    Create evidence and data-quality features using
    information currently available in the MPLADS dataset.

    Missing evidence is treated as a data-quality signal,
    not as proof of irregularity.
    """

    df = df.copy()

    # ---------------------------------------------------------
    # Completion evidence signal
    # ---------------------------------------------------------

    df["Evidence_Risk"] = 0

    df.loc[
        df["Completion_Evidence_Missing"],
        "Evidence_Risk"
    ] = 1

    # ---------------------------------------------------------
    # Completed project without completion evidence
    # ---------------------------------------------------------

    df["Completed_Without_Evidence"] = (
        (df["Progress_Status"] == "Completed")
        & (df["Completion_Evidence_Missing"])
    )

    return df