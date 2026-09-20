from pathlib import Path

import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "review_queue.csv"
)


st.set_page_config(
    page_title="Risk Alerts",
    page_icon="⚠️",
    layout="wide"
)


@st.cache_data
def load_review_queue():

    return pd.read_csv(INPUT_FILE)


df = load_review_queue()


st.title("Risk Alerts")

st.markdown(
    """
    Projects shown here have generated one or more
    screening signals and are prioritised for human review.
    """
)


# ---------------------------------------------------------
# Filters
# ---------------------------------------------------------

st.subheader("Filters")

available_categories = [
    "Medium",
    "High",
    "Critical",
]

selected_categories = st.multiselect(
    "Risk Category",
    options=available_categories,
    default=available_categories
)


filtered_df = df[
    df["Risk_Category"].isin(selected_categories)
].copy()


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

col1, col2, col3 = st.columns(3)


with col1:
    st.metric(
        "Projects Shown",
        f"{len(filtered_df):,}"
    )


with col2:
    high_count = filtered_df[
        filtered_df["Risk_Category"].isin(
            ["High", "Critical"]
        )
    ].shape[0]

    st.metric(
        "High / Critical",
        f"{high_count:,}"
    )


with col3:
    overlap_count = filtered_df[
        filtered_df["Has_Potential_Overlap"]
        .fillna(False)
    ].shape[0]

    st.metric(
        "With Potential Overlap",
        f"{overlap_count:,}"
    )


st.divider()


# ---------------------------------------------------------
# Alerts table
# ---------------------------------------------------------

st.subheader("Projects Requiring Review")


display_columns = [
    "Work_ID",
    "Risk_Score",
    "Risk_Category",
    "Risk_Reasons",
]


display_df = (
    filtered_df[display_columns]
    .sort_values(
        "Risk_Score",
        ascending=False
    )
)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


st.caption(
    "These alerts are screening signals for human review. "
    "They do not confirm fraud, duplication, or irregularity."
)
