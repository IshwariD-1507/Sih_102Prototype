import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# PATH SETUP
# =========================================================

APP_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = APP_DIR.parent

for path in [str(ROOT_DIR), str(APP_DIR)]:
    if path not in sys.path:
        sys.path.insert(0, path)


# =========================================================
# IMPORTS
# =========================================================

from app.components.auth_ui import render_sidebar_auth

from src.mplads.auth import filter_by_district
from src.mplads.data.loaders import load_unified_data


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="District Project Overview",
    page_icon="📈",
    layout="wide",
)


# =========================================================
# AUTHENTICATION
# =========================================================

render_sidebar_auth()

if not st.session_state.get(
    "authenticated",
    False
):

    st.warning(
        "Please log in from the sidebar to access "
        "district project insights."
    )

    st.stop()


# =========================================================
# PAGE TITLE
# =========================================================

st.title("📈 District Project Overview")


# =========================================================
# LOAD DATA
# =========================================================

df = load_unified_data()


if df.empty:

    st.warning(
        "No project records are available. "
        "Please make sure `project_features.csv` "
        "has been generated."
    )

    st.stop()


# =========================================================
# DISTRICT FILTER
# =========================================================

df_filtered = filter_by_district(
    df,
    district_col="district"
)


# =========================================================
# CURRENT SCOPE
# =========================================================

user_district = st.session_state.get(
    "user_district"
)

if user_district:

    st.info(
        f"Displaying filtered metrics for "
        f"**{user_district} District**"
    )

else:

    st.info(
        "Displaying aggregated metrics for "
        "**All Districts (Central Admin)**"
    )


# =========================================================
# NO DATA AFTER FILTER
# =========================================================

if df_filtered.empty:

    st.warning(
        "No records found for the selected district."
    )

    st.stop()


# =========================================================
# SUMMARY METRICS
# =========================================================

total_works = len(df_filtered)


# Recommended amount
if "Recommended_Amount" in df_filtered.columns:

    total_recommended = (
        pd.to_numeric(
            df_filtered["Recommended_Amount"],
            errors="coerce"
        )
        .fillna(0)
        .sum()
    )

else:

    total_recommended = 0


# Completed works
if "Progress_Status" in df_filtered.columns:

    progress_status = (
        df_filtered["Progress_Status"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    completed_works = (
        progress_status
        .str.lower()
        .eq("completed")
        .sum()
    )

    active_works = (
        progress_status
        .str.lower()
        .eq("in progress")
        .sum()
    )

else:

    completed_works = 0
    active_works = 0


# =========================================================
# METRIC CARDS
# =========================================================

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Total Works",
    f"{total_works:,}"
)


col2.metric(
    "Total Recommended",
    f"₹{total_recommended / 1e7:.2f} Cr"
)


col3.metric(
    "Completed Works",
    f"{completed_works:,}"
)


col4.metric(
    "Active Works",
    f"{active_works:,}"
)


# =========================================================
# PROJECT STATUS
# =========================================================

if "Progress_Status" in df_filtered.columns:

    st.subheader(
        "📊 Project Status Breakdown"
    )

    status_counts = (
        df_filtered["Progress_Status"]
        .fillna("Unknown")
        .astype(str)
        .value_counts()
    )

    st.bar_chart(
        status_counts
    )


# =========================================================
# RISK SUMMARY
# =========================================================

if "Risk_Category" in df_filtered.columns:

    st.subheader(
        "⚠️ Risk Distribution"
    )

    risk_counts = (
        df_filtered["Risk_Category"]
        .fillna("Unknown")
        .astype(str)
        .value_counts()
    )

    st.bar_chart(
        risk_counts
    )


# =========================================================
# PROJECT DETAILS
# =========================================================

st.subheader(
    "📋 Project Details"
)


# Prefer important columns first
preferred_columns = [
    "Work_ID",
    "Work_Category",
    "State",
    "district",
    "Constituency",
    "Work_Description",
    "Recommended_Amount",
    "Sanction_Amount",
    "Amount_Disbursed",
    "Recommended_Date",
    "Sanction_Date",
    "Completion_Date",
    "Progress_Status",
    "Risk_Score",
    "Risk_Category",
]


available_columns = [
    column
    for column in preferred_columns
    if column in df_filtered.columns
]


# Show important columns first, then the rest
remaining_columns = [
    column
    for column in df_filtered.columns
    if column not in available_columns
]


display_columns = (
    available_columns
    + remaining_columns
)


st.dataframe(
    df_filtered[display_columns],
    width="stretch",
    hide_index=True,
)