import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from pathlib import Path


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="GIS Risk Map",
    page_icon="🗺️",
    layout="wide"
)


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[2]

FEATURE_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "project_features.csv"
)


# ---------------------------------------------------------
# Load project data
# ---------------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv(
        FEATURE_FILE,
        low_memory=False
    )

    return df


df = load_data()


# ---------------------------------------------------------
# Title
# ---------------------------------------------------------

st.title("🗺️ GIS Risk Map")

st.markdown(
    """
    Geographic view of MPLADS projects and their
    risk-screening signals.
    """
)


# ---------------------------------------------------------
# Check geographic data
# ---------------------------------------------------------

possible_latitude_columns = [
    "Latitude",
    "latitude",
    "Lat",
    "lat"
]

possible_longitude_columns = [
    "Longitude",
    "longitude",
    "Lon",
    "lon"
]


latitude_column = next(
    (
        column
        for column in possible_latitude_columns
        if column in df.columns
    ),
    None
)

longitude_column = next(
    (
        column
        for column in possible_longitude_columns
        if column in df.columns
    ),
    None
)


# ---------------------------------------------------------
# Filters
# ---------------------------------------------------------

st.sidebar.header("Map Filters")


if "State" in df.columns:

    states = sorted(
        df["State"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_state = st.sidebar.selectbox(
        "State",
        ["All"] + states
    )

else:

    selected_state = "All"


if "Risk_Category" in df.columns:

    risk_categories = [
        "All",
        "Low",
        "Medium",
        "High",
        "Critical"
    ]

    selected_risk = st.sidebar.selectbox(
        "Risk Category",
        risk_categories
    )

else:

    selected_risk = "All"


if "Work_Category" in df.columns:

    categories = sorted(
        df["Work_Category"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_category = st.sidebar.selectbox(
        "Work Category",
        ["All"] + categories
    )

else:

    selected_category = "All"


# ---------------------------------------------------------
# Apply filters
# ---------------------------------------------------------

filtered_df = df.copy()


if selected_state != "All":

    filtered_df = filtered_df[
        filtered_df["State"].astype(str)
        == selected_state
    ]


if selected_risk != "All":

    filtered_df = filtered_df[
        filtered_df["Risk_Category"].astype(str)
        == selected_risk
    ]


if selected_category != "All":

    filtered_df = filtered_df[
        filtered_df["Work_Category"].astype(str)
        == selected_category
    ]


# ---------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Projects",
        len(filtered_df)
    )


with col2:

    if "Risk_Score" in filtered_df.columns:

        st.metric(
            "Average Risk Score",
            round(
                filtered_df["Risk_Score"]
                .mean(),
                2
            )
        )


with col3:

    if "Has_Potential_Overlap" in filtered_df.columns:

        overlap_count = int(
            filtered_df["Has_Potential_Overlap"]
            .fillna(False)
            .sum()
        )

        st.metric(
            "Potential Overlap",
            overlap_count
        )


with col4:

    if "Evidence_Risk" in filtered_df.columns:

        evidence_count = int(
            filtered_df["Evidence_Risk"]
            .fillna(0)
            .sum()
        )

        st.metric(
            "Evidence Signals",
            evidence_count
        )


# ---------------------------------------------------------
# Geographic availability
# ---------------------------------------------------------

if latitude_column is None or longitude_column is None:

    st.warning(
        "Reliable project-level latitude and longitude "
        "data are not currently available in the dataset."
    )

    st.info(
        """
        The risk-analysis pipeline is working normally, but
        project markers cannot be placed on a geographic map
        without reliable coordinates.

        No coordinates are being fabricated.
        """
    )

    st.subheader("Projects matching the selected filters")

    display_columns = [
        column
        for column in [
            "Work_ID",
            "State",
            "District",
            "Work_Category",
            "Risk_Score",
            "Risk_Category",
            "Potential_Overlap_Count",
            "Max_Overlap_Score"
        ]
        if column in filtered_df.columns
    ]

    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        hide_index=True
    )

    st.stop()


# ---------------------------------------------------------
# Prepare geographic data
# ---------------------------------------------------------

map_df = filtered_df.copy()


map_df[latitude_column] = pd.to_numeric(
    map_df[latitude_column],
    errors="coerce"
)

map_df[longitude_column] = pd.to_numeric(
    map_df[longitude_column],
    errors="coerce"
)


map_df = map_df.dropna(
    subset=[
        latitude_column,
        longitude_column
    ]
)


# ---------------------------------------------------------
# Map
# ---------------------------------------------------------

if len(map_df) == 0:

    st.warning(
        "No projects with valid geographic coordinates "
        "match the selected filters."
    )

else:

    center_lat = map_df[latitude_column].mean()
    center_lon = map_df[longitude_column].mean()

    project_map = folium.Map(
        location=[
            center_lat,
            center_lon
        ],
        zoom_start=7
    )


    # -----------------------------------------------------
    # Project markers
    # -----------------------------------------------------

    for _, row in map_df.iterrows():

        risk_category = str(
            row.get(
                "Risk_Category",
                "Unknown"
            )
        )

        marker_color = {
            "Low": "green",
            "Medium": "orange",
            "High": "red",
            "Critical": "darkred"
        }.get(
            risk_category,
            "blue"
        )


        popup_html = f"""
        <b>Project:</b>
        {row.get("Work_ID", "N/A")}
        <br><br>

        <b>Work:</b>
        {row.get("Work_Description", "N/A")}
        <br><br>

        <b>Risk Score:</b>
        {row.get("Risk_Score", "N/A")}
        <br>

        <b>Risk Category:</b>
        {risk_category}
        <br>

        <b>State:</b>
        {row.get("State", "N/A")}
        <br>

        <b>District:</b>
        {row.get("District", "N/A")}
        """


        folium.Marker(
            location=[
                row[latitude_column],
                row[longitude_column]
            ],
            popup=folium.Popup(
                popup_html,
                max_width=400
            ),
            tooltip=(
                f"{risk_category} | "
                f"Risk Score: "
                f"{row.get('Risk_Score', 'N/A')}"
            ),
            icon=folium.Icon(
                color=marker_color
            )
        ).add_to(project_map)


    # -----------------------------------------------------
    # Display map
    # -----------------------------------------------------

    st_folium(
        project_map,
        width=None,
        height=650
    )


# ---------------------------------------------------------
# Project table
# ---------------------------------------------------------

st.subheader("Projects in Current Map View")

display_columns = [
    column
    for column in [
        "Work_ID",
        "State",
        "District",
        "Work_Category",
        "Risk_Score",
        "Risk_Category",
        "Potential_Overlap_Count",
        "Max_Overlap_Score"
    ]
    if column in filtered_df.columns
]


st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    hide_index=True
)
