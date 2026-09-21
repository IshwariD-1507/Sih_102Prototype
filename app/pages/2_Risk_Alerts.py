import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.mplads.auth import filter_by_district
from app.components.auth_ui import render_sidebar_auth


st.set_page_config(
    page_title="Risk Alerts",
    layout="wide"
)

render_sidebar_auth()


# ---------------------------------------------------------
# Authentication
# ---------------------------------------------------------

if not st.session_state.get("authenticated", False):
    st.warning("Please log in from the sidebar to access Risk Alerts.")
    st.stop()


# ---------------------------------------------------------
# Page title
# ---------------------------------------------------------

st.title("🚨 Risk Alerts & Review Queue")


# ---------------------------------------------------------
# Load review queue
# ---------------------------------------------------------

INPUT_FILE = ROOT_DIR / "data" / "processed" / "review_queue.csv"


@st.cache_data
def load_review_queue():
    if not INPUT_FILE.exists():
        return pd.DataFrame()

    return pd.read_csv(INPUT_FILE, low_memory=False)


df = load_review_queue()


# ---------------------------------------------------------
# Handle missing dataset
# ---------------------------------------------------------

if df.empty:

    st.warning(
        "⚠️ `data/processed/review_queue.csv` was not found or is empty. "
        "Please run your data processing pipeline first."
    )

    st.stop()


# ---------------------------------------------------------
# Apply district filtering
# ---------------------------------------------------------

df_filtered = filter_by_district(
    df,
    district_col="district"
)


# ---------------------------------------------------------
# Prepare Risk Alerts table
# ---------------------------------------------------------

st.subheader("Projects Flagged for Review")


# Make a copy so we do not modify the original dataframe
display_df = df_filtered.copy()


# ---------------------------------------------------------
# Sort by risk score
# ---------------------------------------------------------

if "Risk_Score" in display_df.columns:

    display_df["Risk_Score"] = pd.to_numeric(
        display_df["Risk_Score"],
        errors="coerce"
    ).fillna(0)

    display_df = display_df.sort_values(
        by="Risk_Score",
        ascending=False,
        kind="stable"
    ).reset_index(drop=True)


# ---------------------------------------------------------
# Create rank column
# ---------------------------------------------------------

display_df.insert(
    0,
    "#",
    range(1, len(display_df) + 1)
)


# ---------------------------------------------------------
# Reorder columns
#
# Desired order:
#
# # 
# Risk_Score
# Risk_Category
# Risk_Reasons
# Work_ID
# remaining columns...
# ---------------------------------------------------------

priority_columns = [
    "#",
    "Risk_Score",
    "Risk_Category",
    "Risk_Reasons",
    "Work_ID",
]


existing_priority_columns = [
    column
    for column in priority_columns
    if column in display_df.columns
]


remaining_columns = [
    column
    for column in display_df.columns
    if column not in existing_priority_columns
]


display_df = display_df[
    existing_priority_columns + remaining_columns
]


# ---------------------------------------------------------
# Show table
# ---------------------------------------------------------

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)