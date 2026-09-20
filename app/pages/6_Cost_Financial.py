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
    page_title="Cost & Financial",
    page_icon="💰",
    layout="wide"
)


@st.cache_data
def load_project_data():

    return pd.read_csv(INPUT_FILE)


df = load_project_data()


st.title("Cost & Financial Analysis")

st.markdown(
    """
    This page analyses recommendation, sanction and
    disbursement amounts together with peer-project cost
    comparisons. Financial differences are screening signals
    for human review and do not by themselves establish
    financial irregularity.
    """
)


# ---------------------------------------------------------
# Prepare financial fields
# ---------------------------------------------------------

numeric_columns = [
    "Recommended_Amount",
    "Sanction_Amount",
    "Amount_Disbursed",
    "Recommendation_Sanction_Gap",
    "Recommendation_Sanction_Gap_Percent",
    "Utilisation_Percent",
    "Amount_Remaining",
    "Peer_Median_Sanction_Amount",
    "Cost_Deviation_From_Peer_Median",
    "Cost_Deviation_Percent",
]


for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)


with col1:

    total_sanction = (
        df["Sanction_Amount"]
        .sum()
    )

    st.metric(
        "Total Sanction Amount",
        f"₹{total_sanction:,.0f}"
    )


with col2:

    total_disbursed = (
        df["Amount_Disbursed"]
        .sum()
    )

    st.metric(
        "Total Disbursed",
        f"₹{total_disbursed:,.0f}"
    )


with col3:

    average_utilisation = (
        df["Utilisation_Percent"]
        .dropna()
        .mean()
    )

    st.metric(
        "Average Utilisation",
        f"{average_utilisation:.1f}%"
    )


with col4:

    high_cost_count = (
        df["High_Cost_Deviation"]
        .fillna(False)
        .sum()
    )

    st.metric(
        "High Cost Deviation",
        f"{high_cost_count:,}"
    )


st.divider()


# ---------------------------------------------------------
# Financial signals
# ---------------------------------------------------------

st.subheader("Financial Screening Signals")


col1, col2, col3, col4 = st.columns(4)


with col1:

    disbursement_exceeds = (
        df["Disbursement_Exceeds_Sanction"]
        .fillna(False)
        .sum()
    )

    st.metric(
        "Disbursement > Sanction",
        f"{disbursement_exceeds:,}"
    )


with col2:

    sanction_exceeds = (
        df["Sanction_Exceeds_Recommendation"]
        .fillna(False)
        .sum()
    )

    st.metric(
        "Sanction > Recommendation",
        f"{sanction_exceeds:,}"
    )


with col3:

    high_deviation = (
        df["High_Cost_Deviation"]
        .fillna(False)
        .sum()
    )

    st.metric(
        "High Cost Deviation",
        f"{high_deviation:,}"
    )


with col4:

    remaining_amount = (
        df["Amount_Remaining"]
        .dropna()
        .sum()
    )

    st.metric(
        "Amount Remaining",
        f"₹{remaining_amount:,.0f}"
    )


st.divider()


# ---------------------------------------------------------
# Filters
# ---------------------------------------------------------

st.subheader("Filters")


col1, col2, col3 = st.columns(3)


with col1:

    categories = st.multiselect(
        "Risk Category",
        options=[
            "Low",
            "Medium",
            "High",
            "Critical",
        ],
        default=[
            "Medium",
            "High",
            "Critical",
        ]
    )


with col2:

    financial_signal = st.selectbox(
        "Financial Signal",
        options=[
            "All Projects",
            "Disbursement Exceeds Sanction",
            "Sanction Exceeds Recommendation",
            "High Cost Deviation",
        ]
    )


with col3:

    utilisation_filter = st.selectbox(
        "Utilisation",
        options=[
            "All",
            "Completed / Utilised",
            "Low / Missing Utilisation",
        ]
    )


filtered_df = df[
    df["Risk_Category"].isin(categories)
].copy()


if financial_signal == "Disbursement Exceeds Sanction":

    filtered_df = filtered_df[
        filtered_df["Disbursement_Exceeds_Sanction"]
        .fillna(False)
    ]


elif financial_signal == "Sanction Exceeds Recommendation":

    filtered_df = filtered_df[
        filtered_df["Sanction_Exceeds_Recommendation"]
        .fillna(False)
    ]


elif financial_signal == "High Cost Deviation":

    filtered_df = filtered_df[
        filtered_df["High_Cost_Deviation"]
        .fillna(False)
    ]


if utilisation_filter == "Completed / Utilised":

    filtered_df = filtered_df[
        filtered_df["Utilisation_Percent"]
        .notna()
    ]


elif utilisation_filter == "Low / Missing Utilisation":

    filtered_df = filtered_df[
        filtered_df["Utilisation_Percent"]
        .isna()
        |
        (filtered_df["Utilisation_Percent"] < 50)
    ]


# ---------------------------------------------------------
# Cost overview
# ---------------------------------------------------------

st.subheader("Cost Analysis")


col1, col2, col3 = st.columns(3)


with col1:

    average_sanction = (
        filtered_df["Sanction_Amount"]
        .dropna()
        .mean()
    )

    if pd.notna(average_sanction):

        st.metric(
            "Average Sanction Amount",
            f"₹{average_sanction:,.0f}"
        )

    else:

        st.metric(
            "Average Sanction Amount",
            "N/A"
        )


with col2:

    average_deviation = (
        filtered_df["Cost_Deviation_Percent"]
        .dropna()
        .mean()
    )

    if pd.notna(average_deviation):

        st.metric(
            "Average Cost Deviation",
            f"{average_deviation:.1f}%"
        )

    else:

        st.metric(
            "Average Cost Deviation",
            "N/A"
        )


with col3:

    average_remaining = (
        filtered_df["Amount_Remaining"]
        .dropna()
        .mean()
    )

    if pd.notna(average_remaining):

        st.metric(
            "Average Amount Remaining",
            f"₹{average_remaining:,.0f}"
        )

    else:

        st.metric(
            "Average Amount Remaining",
            "N/A"
        )


st.divider()


# ---------------------------------------------------------
# Financial project table
# ---------------------------------------------------------

st.subheader("Financial Projects Requiring Review")


display_columns = [
    "Work_ID",
    "Recommended_Amount",
    "Sanction_Amount",
    "Amount_Disbursed",
    "Recommendation_Sanction_Gap_Percent",
    "Utilisation_Percent",
    "Amount_Remaining",
    "Cost_Deviation_Percent",
    "High_Cost_Deviation",
    "Risk_Score",
    "Risk_Category",
]


available_columns = [
    column
    for column in display_columns
    if column in filtered_df.columns
]


display_df = filtered_df[
    available_columns
].sort_values(
    "Risk_Score",
    ascending=False
)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# Project financial investigation
# ---------------------------------------------------------

st.divider()

st.subheader("Project Financial Details")


if len(filtered_df) > 0:

    project_options = (
        filtered_df["Work_ID"]
        .astype(str)
        .tolist()
    )


    selected_project = st.selectbox(
        "Select a project",
        options=project_options
    )


    project = filtered_df[
        filtered_df["Work_ID"].astype(str)
        == selected_project
    ].iloc[0]


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Recommended Amount",
            f"₹{project['Recommended_Amount']:,.0f}"
        )


    with col2:

        st.metric(
            "Sanction Amount",
            f"₹{project['Sanction_Amount']:,.0f}"
        )


    with col3:

        if pd.notna(project["Amount_Disbursed"]):

            st.metric(
                "Amount Disbursed",
                f"₹{project['Amount_Disbursed']:,.0f}"
            )

        else:

            st.metric(
                "Amount Disbursed",
                "Not available"
            )


    with col4:

        st.metric(
            "Amount Remaining",
            (
                f"₹{project['Amount_Remaining']:,.0f}"
                if pd.notna(project["Amount_Remaining"])
                else "N/A"
            )
        )


    st.markdown("### Financial Breakdown")


    financial_columns = [
        "Recommended_Amount",
        "Sanction_Amount",
        "Amount_Disbursed",
        "Recommendation_Sanction_Gap",
        "Recommendation_Sanction_Gap_Percent",
        "Utilisation_Percent",
        "Amount_Remaining",
        "Peer_Median_Sanction_Amount",
        "Cost_Deviation_From_Peer_Median",
        "Cost_Deviation_Percent",
    ]


    available_financial_columns = [
        column
        for column in financial_columns
        if column in project.index
    ]


    financial_data = pd.DataFrame(
        {
            "Field": available_financial_columns,
            "Value": [
                project[column]
                for column in available_financial_columns
            ],
        }
    )


    st.dataframe(
        financial_data,
        use_container_width=True,
        hide_index=True
    )


    # -----------------------------------------------------
    # Financial screening signals
    # -----------------------------------------------------

    st.markdown("### Financial Screening Signals")


    signals = []


    if project["Disbursement_Exceeds_Sanction"]:

        signals.append(
            "Disbursement exceeds the sanctioned amount."
        )


    if project["Sanction_Exceeds_Recommendation"]:

        signals.append(
            "Sanction amount exceeds the recommended amount."
        )


    if project["High_Cost_Deviation"]:

        signals.append(
            "Sanction amount shows a high deviation "
            "from comparable peer projects."
        )


    if len(signals) == 0:

        st.success(
            "No financial screening signals were generated "
            "for this project."
        )

    else:

        for signal in signals:

            st.warning(signal)


st.caption(
    "Financial differences and peer-project deviations are "
    "screening signals for human review. They do not by "
    "themselves establish financial irregularity."
)
