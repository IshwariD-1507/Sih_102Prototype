import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# PATH SETUP
# =========================================================

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent

for path in [str(ROOT_DIR), str(APP_DIR)]:
    if path not in sys.path:
        sys.path.insert(0, path)


# =========================================================
# IMPORTS
# =========================================================

from app.components.auth_ui import render_sidebar_auth

from src.mplads.data.loaders import load_unified_data
from src.mplads.auth import filter_by_district


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MPLADS Project Monitoring System",
    page_icon="📊",
    layout="wide",
)


# =========================================================
# AUTHENTICATION
# =========================================================

active_district = render_sidebar_auth()


if not st.session_state.get(
    "authenticated",
    False
):

    st.title(
        "MPLADS Project Monitoring & Audit Portal"
    )

    st.warning(
        "Please log in from the sidebar to access "
        "district project insights."
    )

    st.stop()


# =========================================================
# LOAD DATA
# =========================================================

raw_df = load_unified_data()


if raw_df.empty:

    st.error(
        "No project data is available. "
        "Please generate `project_features.csv` "
        "using the feature-building pipeline."
    )

    st.stop()


# =========================================================
# DISTRICT FILTER
# =========================================================

district_df = filter_by_district(
    raw_df,
    district_col="district"
)


if district_df.empty:

    st.warning(
        "No projects were found for your "
        "current district scope."
    )

    st.stop()


# =========================================================
# TITLE
# =========================================================

st.title(
    "📌 MPLADS Executive Dashboard"
)


if active_district:

    st.subheader(
        f"District Overview: {active_district}"
    )

else:

    st.subheader(
        "National / State Level Overview"
    )


# =========================================================
# SUMMARY METRICS
# =========================================================

total_works = len(district_df)


if "Recommended_Amount" in district_df.columns:

    recommended_amount = (
        pd.to_numeric(
            district_df["Recommended_Amount"],
            errors="coerce"
        )
        .fillna(0)
        .sum()
    )

else:

    recommended_amount = 0


if "Progress_Status" in district_df.columns:

    status = (
        district_df["Progress_Status"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.strip()
    )

    active_projects = (
        status == "in progress"
    ).sum()

    completed_projects = (
        status == "completed"
    ).sum()

else:

    active_projects = 0
    completed_projects = 0


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Total Works Monitored",
    f"{total_works:,}"
)


col2.metric(
    "Total Recommended",
    f"₹{recommended_amount / 1e7:.2f} Cr"
)


col3.metric(
    "Active Projects",
    f"{active_projects:,}"
)


col4.metric(
    "Completed Projects",
    f"{completed_projects:,}"
)


# =========================================================
# STATUS BREAKDOWN
# =========================================================

if "Progress_Status" in district_df.columns:

    st.subheader(
        "📊 Project Status"
    )

    status_counts = (
        district_df["Progress_Status"]
        .fillna("Unknown")
        .astype(str)
        .value_counts()
    )

    st.bar_chart(
        status_counts
    )


# =========================================================
# RISK BREAKDOWN
# =========================================================

if "Risk_Category" in district_df.columns:

    st.subheader(
        "⚠️ Risk Distribution"
    )

    risk_counts = (
        district_df["Risk_Category"]
        .fillna("Unknown")
        .astype(str)
        .value_counts()
    )

    st.bar_chart(
        risk_counts
    )


# =========================================================
# DATA PREVIEW
# =========================================================

st.subheader(
    "📋 Project Data Preview"
)


st.dataframe(
    district_df.head(50),
    width="stretch",
    hide_index=True,
)