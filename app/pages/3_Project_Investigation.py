import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PATH SETUP
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))


# ============================================================
# PROJECT IMPORTS
# ============================================================

from src.mplads.auth import filter_by_district
from app.components.auth_ui import render_sidebar_auth


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Project Investigation",
    layout="wide",
)


# ============================================================
# AUTHENTICATION
# ============================================================

render_sidebar_auth()

if not st.session_state.get("authenticated", False):
    st.warning(
        "Please log in from the sidebar to access Project Investigation."
    )
    st.stop()


# ============================================================
# PAGE TITLE
# ============================================================

st.title("🔍 Project Investigation")


# ============================================================
# DATA PATH
# ============================================================

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "project_features.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_project_data():
    if not INPUT_FILE.exists():
        return pd.DataFrame()

    return pd.read_csv(
        INPUT_FILE,
        low_memory=False,
    )


df = load_project_data()


# ============================================================
# HANDLE EMPTY DATASET
# ============================================================

if df.empty:

    st.warning(
        "⚠️ `data/processed/project_features.csv` "
        "was not found or is empty. "
        "Please run your data processing pipeline first."
    )

    st.stop()


# ============================================================
# DISTRICT FILTERING
# ============================================================

df_filtered = filter_by_district(
    df,
    district_col="district",
)


# ============================================================
# PROJECT SEARCH
# ============================================================

st.subheader("Detailed Project Audit Search")

st.markdown(
    "Search across **all project information** — "
    "Work ID, description, state, MP, constituency, dates, "
    "amounts, status, risk information, and more."
)


search_query = st.text_input(
    "🔎 Search projects",
    placeholder=(
        "Search by Work ID, description, MP, constituency, "
        "state, amount, status, risk, date..."
    ),
    key="project_investigation_search",
)


# ============================================================
# APPLY SEARCH
# ============================================================

if search_query.strip():

    search_text = search_query.strip().lower()

    # Convert every column to string and search across
    # the complete row.
    search_mask = (
        df_filtered
        .astype(str)
        .apply(
            lambda column: column.str.lower().str.contains(
                search_text,
                na=False,
                regex=False,
            )
        )
        .any(axis=1)
    )

    df_display = df_filtered[search_mask].copy()

else:

    df_display = df_filtered.copy()


# ============================================================
# SEARCH RESULTS SUMMARY
# ============================================================

total_projects = len(df_filtered)
matching_projects = len(df_display)

if search_query.strip():

    st.info(
        f"Showing **{matching_projects:,}** matching projects "
        f"out of **{total_projects:,}** projects."
    )

else:

    st.info(
        f"Showing **all {total_projects:,} projects**. "
        "Use the search bar above to find a specific project."
    )


# ============================================================
# NO RESULTS
# ============================================================

if search_query.strip() and df_display.empty:

    st.warning(
        f'No projects found matching **"{search_query}"**.'
    )

    st.stop()


# ============================================================
# PROJECT TABLE
# ============================================================

st.dataframe(
    df_display,
    use_container_width=True,
    height=600,
)