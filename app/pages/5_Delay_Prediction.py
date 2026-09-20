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
    page_title="Delay Prediction",
    page_icon="⏱️",
    layout="wide"
)


@st.cache_data
def load_project_data():

    return pd.read_csv(INPUT_FILE)


df = load_project_data()


st.title("Delay & Lifecycle Analysis")

st.markdown(
    """
    Projects shown here are analysed using available lifecycle
    information such as sanction dates, completion dates and
    completion duration. These signals help identify projects
    that may require closer review.
    """
)


# ---------------------------------------------------------
# Prepare delay indicators
# ---------------------------------------------------------

df["Days_Sanction_to_Completion"] = pd.to_numeric(
    df["Days_Sanction_to_Completion"],
    errors="coerce"
)


df["Long_Duration"] = (
    df["Days_Sanction_to_Completion"] > 365
)


df["Incomplete_Lifecycle"] = (
    df["Progress_Status"] == "In Progress"
)


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Projects",
        f"{len(df):,}"
    )


with col2:

    completed_projects = (
        df["Progress_Status"] == "Completed"
    ).sum()

    st.metric(
        "Completed",
        f"{completed_projects:,}"
    )


with col3:

    long_duration = (
        df["Long_Duration"]
    ).sum()

    st.metric(
        "Long Duration > 365 Days",
        f"{long_duration:,}"
    )


with col4:

    in_progress = (
        df["Incomplete_Lifecycle"]
    ).sum()

    st.metric(
        "In Progress",
        f"{in_progress:,}"
    )


st.divider()


# ---------------------------------------------------------
# Filters
# ---------------------------------------------------------

st.subheader("Filters")


col1, col2 = st.columns(2)


with col1:

    progress_filter = st.multiselect(
        "Progress Status",
        options=[
            "Completed",
            "In Progress",
        ],
        default=[
            "Completed",
            "In Progress",
        ]
    )


with col2:

    duration_filter = st.selectbox(
        "Duration Filter",
        options=[
            "All Projects",
            "Long Duration (>365 days)",
            "Normal Duration (<=365 days)",
            "Missing Completion Duration",
        ]
    )


filtered_df = df[
    df["Progress_Status"].isin(progress_filter)
].copy()


if duration_filter == "Long Duration (>365 days)":

    filtered_df = filtered_df[
        filtered_df["Long_Duration"]
    ]


elif duration_filter == "Normal Duration (<=365 days)":

    filtered_df = filtered_df[
        (
            filtered_df["Days_Sanction_to_Completion"]
            .notna()
        )
        & (~filtered_df["Long_Duration"])
    ]


elif duration_filter == "Missing Completion Duration":

    filtered_df = filtered_df[
        filtered_df["Days_Sanction_to_Completion"]
        .isna()
    ]


# ---------------------------------------------------------
# Delay overview
# ---------------------------------------------------------

st.subheader("Lifecycle Overview")


col1, col2, col3 = st.columns(3)


with col1:

    avg_duration = (
        filtered_df[
            "Days_Sanction_to_Completion"
        ]
        .dropna()
        .mean()
    )

    if pd.notna(avg_duration):

        st.metric(
            "Average Completion Duration",
            f"{avg_duration:.0f} days"
        )

    else:

        st.metric(
            "Average Completion Duration",
            "N/A"
        )


with col2:

    long_duration_count = (
        filtered_df["Long_Duration"]
        .sum()
    )

    st.metric(
        "Long Duration Projects",
        f"{long_duration_count:,}"
    )


with col3:

    missing_duration = (
        filtered_df[
            "Days_Sanction_to_Completion"
        ]
        .isna()
        .sum()
    )

    st.metric(
        "Missing Completion Duration",
        f"{missing_duration:,}"
    )


st.divider()


# ---------------------------------------------------------
# Projects requiring lifecycle review
# ---------------------------------------------------------

st.subheader("Projects Requiring Lifecycle Review")


review_df = filtered_df[
    (
        filtered_df["Long_Duration"]
    )
    |
    (
        filtered_df["Progress_Status"] == "In Progress"
    )
].copy()


display_columns = [
    "Work_ID",
    "Progress_Status",
    "Days_Recommendation_to_Sanction",
    "Days_Sanction_to_Completion",
    "Days_Recommendation_to_Completion",
    "Risk_Score",
    "Risk_Category",
]


available_columns = [
    column
    for column in display_columns
    if column in review_df.columns
]


display_df = (
    review_df[available_columns]
    .sort_values(
        "Days_Sanction_to_Completion",
        ascending=False,
        na_position="last"
    )
)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# Project investigation
# ---------------------------------------------------------

st.divider()

st.subheader("Project Lifecycle Details")


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
            "Progress Status",
            str(project["Progress_Status"])
        )


    with col2:

        duration = project[
            "Days_Sanction_to_Completion"
        ]

        if pd.notna(duration):

            st.metric(
                "Completion Duration",
                f"{duration:.0f} days"
            )

        else:

            st.metric(
                "Completion Duration",
                "Not available"
            )


    with col3:

        recommendation_to_completion = project[
            "Days_Recommendation_to_Completion"
        ]

        if pd.notna(recommendation_to_completion):

            st.metric(
                "Recommendation → Completion",
                f"{recommendation_to_completion:.0f} days"
            )

        else:

            st.metric(
                "Recommendation → Completion",
                "Not available"
            )


    with col4:

        st.metric(
            "Risk Category",
            str(project["Risk_Category"])
        )


    st.markdown("### Lifecycle Information")


    lifecycle_columns = [
        "Recommended_Date",
        "Sanction_Date",
        "Completion_Date",
        "Days_Recommendation_to_Sanction",
        "Days_Sanction_to_Completion",
        "Days_Recommendation_to_Completion",
        "Progress_Status",
        "Missing_Completion_Data",
    ]


    available_lifecycle_columns = [
        column
        for column in lifecycle_columns
        if column in project.index
    ]


    lifecycle_data = pd.DataFrame(
        {
            "Field": available_lifecycle_columns,
            "Value": [
                project[column]
                for column in available_lifecycle_columns
            ],
        }
    )


    st.dataframe(
        lifecycle_data,
        use_container_width=True,
        hide_index=True
    )


    # -----------------------------------------------------
    # Interpretation
    # -----------------------------------------------------

    st.markdown("### Screening Signals")


    signals = []


    if project["Long_Duration"]:

        signals.append(
            "Completion duration exceeds 365 days."
        )


    if project["Progress_Status"] == "In Progress":

        signals.append(
            "Project is currently marked as In Progress."
        )


    if (
        "Missing_Completion_Data" in project.index
        and project["Missing_Completion_Data"]
    ):

        signals.append(
            "Completion information is not available."
        )


    if len(signals) == 0:

        st.success(
            "No lifecycle screening signals were generated "
            "for this project."
        )

    else:

        for signal in signals:

            st.warning(signal)


st.caption(
    "Lifecycle duration is calculated from available project "
    "dates. A long duration or missing completion information "
    "is a screening signal and does not by itself establish "
    "that a project is delayed improperly."
)
