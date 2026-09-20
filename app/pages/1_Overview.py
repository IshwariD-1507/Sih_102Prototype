import sys
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]

PROJECT_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "project_features.csv"
)


st.set_page_config(
    page_title="MPLADS Risk Screening",
    page_icon="📊",
    layout="wide"
)


@st.cache_data
def load_project_data():

    return pd.read_csv(PROJECT_FILE)


df = load_project_data()


st.title("MPLADS Project Risk Screening")

st.markdown(
    """
    **Explainable screening dashboard for MPLADS projects**

    The system combines financial, lifecycle, evidence,
    cost, and potential-overlap signals to identify projects
    that may require closer human review.
    """
)


# ---------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------

total_projects = len(df)

review_projects = (
    df["Risk_Category"]
    .isin(["Medium", "High", "Critical"])
    .sum()
)

high_projects = (
    df["Risk_Category"]
    .isin(["High", "Critical"])
    .sum()
)

potential_overlap = (
    df["Has_Potential_Overlap"]
    .fillna(False)
    .sum()
)


col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "Total Projects",
        f"{total_projects:,}"
    )


with col2:
    st.metric(
        "Projects for Review",
        f"{review_projects:,}"
    )


with col3:
    st.metric(
        "High / Critical",
        f"{high_projects:,}"
    )


with col4:
    st.metric(
        "Potential Overlap",
        f"{potential_overlap:,}"
    )


st.divider()


# ---------------------------------------------------------
# Risk distribution
# ---------------------------------------------------------

st.subheader("Risk Distribution")


risk_distribution = (
    df["Risk_Category"]
    .value_counts()
    .reindex(
        ["Low", "Medium", "High", "Critical"],
        fill_value=0
    )
)


st.bar_chart(risk_distribution)


# ---------------------------------------------------------
# Top review candidates
# ---------------------------------------------------------

st.subheader("Top Projects for Review")


top_projects = (
    df[
        [
            "Work_ID",
            "Risk_Score",
            "Risk_Category",
            "Risk_Reasons",
        ]
    ]
    .sort_values(
        "Risk_Score",
        ascending=False
    )
    .head(10)
)


st.dataframe(
    top_projects,
    use_container_width=True,
    hide_index=True
)


st.caption(
    "Risk scores are screening signals intended to "
    "prioritise human review. They do not confirm fraud, "
    "duplication, or irregularity."
)
