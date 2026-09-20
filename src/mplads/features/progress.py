import pandas as pd


def create_progress_features(df):
    """
    Create progress-related features using the information
    currently available in the MPLADS datasets.

    The current five datasets do not contain numerical
    physical-progress percentages, so this module does not
    invent them.
    """

    df = df.copy()

    # ---------------------------------------------------------
    # Completion-based progress indicator
    # ---------------------------------------------------------

    df["Progress_Status"] = "In Progress"

    df.loc[
        df["Completion_Date"].notna(),
        "Progress_Status"
    ] = "Completed"

    # ---------------------------------------------------------
    # Completion evidence
    # ---------------------------------------------------------

    if "Image" in df.columns:

        df["Has_Completion_Image"] = (
            df["Image"].notna()
            & (df["Image"].astype(str).str.strip() != "")
        )

    else:

        df["Has_Completion_Image"] = False

    # ---------------------------------------------------------
    # Basic evidence-quality indicator
    # ---------------------------------------------------------

    df["Completion_Evidence_Missing"] = (
        ~df["Has_Completion_Image"]
    )

    return df