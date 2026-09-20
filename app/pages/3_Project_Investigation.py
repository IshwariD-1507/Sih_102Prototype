from pathlib import Path

import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "project_features.csv"
)


st.set_page_config(
    page_title="Project Investigation",
    page_icon="🔎",
    layout="wide"
)


@st.cache_data
def load_project_data():

    return pd.read_csv(INPUT_FILE)


df = load_project_data()


st.title("Project Investigation")

st.markdown(
    """
    Select an individual project to examine its financial,
    lifecycle, evidence, cost, overlap, and risk signals.
    """
)


# ---------------------------------------------------------
# Project selection
# ---------------------------------------------------------

project_ids = (
    df["Work_ID"]
    .dropna()
    .astype(str)
    .tolist()
)


selected_project = st.selectbox(
    "Select Project",
    options=project_ids
)


project = df[
    df["Work_ID"].astype(str) == selected_project
].iloc[0]


# ---------------------------------------------------------
# Project overview
# ---------------------------------------------------------

st.divider()

st.subheader("Project Overview")

st.write(
    project.get(
        "Work_Description",
        "Description unavailable"
    )
)


col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "Risk Score",
        f"{project['Risk_Score']:.0f}"
    )


with col2:
    st.metric(
        "Risk Category",
        project["Risk_Category"]
    )


with col3:
    st.metric(
        "Progress",
        project["Progress_Status"]
    )


with col4:
    st.metric(
        "Potential Overlaps",
        int(project["Potential_Overlap_Count"])
    )


# ---------------------------------------------------------
# Risk reasons
# ---------------------------------------------------------

st.subheader("Risk Reasons")

if (
    pd.notna(project["Risk_Reasons"])
    and str(project["Risk_Reasons"]).strip()
):

    reasons = str(
        project["Risk_Reasons"]
    ).split("; ")

    for reason in reasons:
        st.warning(reason)

else:

    st.success(
        "No current risk reasons were generated."
    )


# ---------------------------------------------------------
# Financial signals
# ---------------------------------------------------------

st.subheader("Financial Information")

col1, col2, col3 = st.columns(3)


with col1:
    st.metric(
        "Recommended Amount",
        f"₹{project['Recommended_Amount']:,.0f}"
        if pd.notna(project["Recommended_Amount"])
        else "N/A"
    )


with col2:
    st.metric(
        "Sanction Amount",
        f"₹{project['Sanction_Amount']:,.0f}"
        if pd.notna(project["Sanction_Amount"])
        else "N/A"
    )


with col3:
    st.metric(
        "Amount Disbursed",
        f"₹{project['Amount_Disbursed']:,.0f}"
        if pd.notna(project["Amount_Disbursed"])
        else "N/A"
    )


# ---------------------------------------------------------
# Timeline
# ---------------------------------------------------------

st.subheader("Lifecycle")

timeline_data = {
    "Recommendation → Sanction": project[
        "Days_Recommendation_to_Sanction"
    ],
    "Sanction → Completion": project[
        "Days_Sanction_to_Completion"
    ],
    "Recommendation → Completion": project[
        "Days_Recommendation_to_Completion"
    ],
}


timeline_df = pd.DataFrame(
    timeline_data.items(),
    columns=["Metric", "Days"]
)


st.dataframe(
    timeline_df,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# Evidence
# ---------------------------------------------------------

st.subheader("Evidence")

evidence_col1, evidence_col2 = st.columns(2)


with evidence_col1:

    st.metric(
        "Completion Image",
        "Available"
        if project["Has_Completion_Image"]
        else "Missing"
    )


with evidence_col2:

    st.metric(
        "Completed Without Evidence",
        "Yes"
        if project["Completed_Without_Evidence"]
        else "No"
    )


# ---------------------------------------------------------
# Cost analysis
# ---------------------------------------------------------

st.subheader("Cost Analysis")

cost_col1, cost_col2, cost_col3 = st.columns(3)


with cost_col1:
    st.metric(
        "Peer Group",
        str(project["Cost_Peer_Group"])
    )


with cost_col2:
    st.metric(
        "Cost Deviation",
        f"{project['Cost_Deviation_Percent']:.1f}%"
        if pd.notna(project["Cost_Deviation_Percent"])
        else "N/A"
    )


with cost_col3:
    st.metric(
        "High Cost Deviation",
        "Yes"
        if project["High_Cost_Deviation"]
        else "No"
    )


# ---------------------------------------------------------
# Overlap
# ---------------------------------------------------------

st.subheader("Potential Overlap")

overlap_col1, overlap_col2 = st.columns(2)


with overlap_col1:

    st.metric(
        "Potential Overlap Count",
        int(project["Potential_Overlap_Count"])
    )


with overlap_col2:

    st.metric(
        "Maximum Overlap Score",
        f"{project['Max_Overlap_Score']:.2f}"
    )


st.caption(
    "Potential overlap is a screening signal and does not "
    "confirm that projects are duplicates."
)
