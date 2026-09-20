import pandas as pd


def create_overlap_features(df, duplicate_candidates):
    """
    Create project-level potential-overlap features.

    The duplicate detector produces pair-level candidates.
    This function converts those candidates into project-level
    screening signals.

    A potential overlap is a screening signal and does not
    confirm that two projects are duplicates.
    """

    df = df.copy()
    duplicate_candidates = duplicate_candidates.copy()

    # ---------------------------------------------------------
    # Initialize overlap features
    # ---------------------------------------------------------

    df["Potential_Overlap_Count"] = 0

    df["Max_Overlap_Score"] = 0.0

    df["Has_Potential_Overlap"] = False

    # ---------------------------------------------------------
    # Handle empty candidate dataset
    # ---------------------------------------------------------

    if duplicate_candidates.empty:
        return df

    # ---------------------------------------------------------
    # Count potential overlaps for each project
    # ---------------------------------------------------------

    overlap_a = (
        duplicate_candidates[
            [
                "Work_ID_A",
                "Overlap_Score"
            ]
        ]
        .rename(
            columns={
                "Work_ID_A": "Work_ID"
            }
        )
    )

    overlap_b = (
        duplicate_candidates[
            [
                "Work_ID_B",
                "Overlap_Score"
            ]
        ]
        .rename(
            columns={
                "Work_ID_B": "Work_ID"
            }
        )
    )

    all_overlaps = pd.concat(
        [
            overlap_a,
            overlap_b
        ],
        ignore_index=True
    )

    # ---------------------------------------------------------
    # Aggregate project-level signals
    # ---------------------------------------------------------

    overlap_summary = (
        all_overlaps
        .groupby("Work_ID")
        .agg(
            Potential_Overlap_Count=(
                "Work_ID",
                "count"
            ),
            Max_Overlap_Score=(
                "Overlap_Score",
                "max"
            )
        )
        .reset_index()
    )

    # ---------------------------------------------------------
    # Merge back into project dataset
    # ---------------------------------------------------------

    df = df.drop(
        columns=[
            "Potential_Overlap_Count",
            "Max_Overlap_Score"
        ],
        errors="ignore"
    )

    df = df.merge(
        overlap_summary,
        on="Work_ID",
        how="left"
    )

    # ---------------------------------------------------------
    # Fill projects with no potential overlaps
    # ---------------------------------------------------------

    df["Potential_Overlap_Count"] = (
        df["Potential_Overlap_Count"]
        .fillna(0)
        .astype(int)
    )

    df["Max_Overlap_Score"] = (
        df["Max_Overlap_Score"]
        .fillna(0)
        .round(2)
    )

    df["Has_Potential_Overlap"] = (
        df["Potential_Overlap_Count"] > 0
    )

    return df