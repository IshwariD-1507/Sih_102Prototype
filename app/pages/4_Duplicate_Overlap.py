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

        sys.path.insert(
            0,
            path
        )


# =========================================================
# IMPORTS
# =========================================================

from app.components.auth_ui import (
    render_sidebar_auth
)

from src.mplads.auth import (
    filter_by_district
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Duplicate & Overlap",
    page_icon="👯",
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
        "Duplicate & Overlap detection."
    )

    st.stop()


# =========================================================
# TITLE
# =========================================================

st.title(
    "👯 Duplicate & Overlap Detection"
)

st.caption(
    "Potential overlaps are screening signals for "
    "human review. They do not establish that projects "
    "are duplicates or indicate wrongdoing."
)


# =========================================================
# LOAD DATA
# =========================================================

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "duplicate_candidates.csv"
)


@st.cache_data
def load_overlap_data():

    if not INPUT_FILE.exists():

        return pd.DataFrame()

    try:

        return pd.read_csv(
            INPUT_FILE
        )

    except Exception as exc:

        st.error(
            f"Could not load overlap data: {exc}"
        )

        return pd.DataFrame()


df = load_overlap_data()


# =========================================================
# EMPTY STATE
# =========================================================

if df.empty:

    st.warning(
        "No duplicate candidates are available yet."
    )

    st.info(
        "Run:\n\n"
        "`python pipelines/test_duplicates.py`"
    )

    st.stop()


# =========================================================
# DISTRICT FILTER
# =========================================================

df_filtered = filter_by_district(
    df,
    district_col="district"
)


if df_filtered.empty:

    st.warning(
        "No potential overlap candidates were found "
        "within your current district scope."
    )

    st.stop()


# =========================================================
# SUMMARY
# =========================================================

total_candidates = len(
    df_filtered
)


high_candidates = 0

if "Review_Category" in df_filtered.columns:

    high_candidates = (
        df_filtered[
            "Review_Category"
        ]
        .isin(
            [
                "High",
                "Critical",
            ]
        )
        .sum()
    )


avg_score = 0

if "Overlap_Score" in df_filtered.columns:

    avg_score = (
        pd.to_numeric(
            df_filtered[
                "Overlap_Score"
            ],
            errors="coerce",
        )
        .mean()
    )


col1, col2, col3 = st.columns(3)


col1.metric(
    "Potential Candidate Pairs",
    f"{total_candidates:,}"
)


col2.metric(
    "High / Critical",
    f"{high_candidates:,}"
)


col3.metric(
    "Average Overlap Score",
    (
        f"{avg_score:.1f}"
        if pd.notna(avg_score)
        else "—"
    )
)


# =========================================================
# REVIEW CATEGORY
# =========================================================

if "Review_Category" in df_filtered.columns:

    st.subheader(
        "Review Priority"
    )

    category_counts = (
        df_filtered[
            "Review_Category"
        ]
        .fillna("Unknown")
        .value_counts()
    )

    st.bar_chart(
        category_counts
    )


# =========================================================
# SORT
# =========================================================

display_df = df_filtered.copy()


if "Overlap_Score" in display_df.columns:

    display_df = display_df.sort_values(
        "Overlap_Score",
        ascending=False,
    )


# =========================================================
# DISPLAY CANDIDATES
# =========================================================

st.subheader(
    "Potential Overlap Candidates"
)


preferred_columns = [
    "Work_ID_A",
    "Work_ID_B",
    "district",
    "State",
    "Work_Category",
    "Semantic_Similarity",
    "Cost_Similarity",
    "Date_Similarity",
    "Overlap_Score",
    "Review_Category",
    "Description_A",
    "Description_B",
]


available_columns = [
    column
    for column in preferred_columns
    if column in display_df.columns
]


st.dataframe(
    display_df[
        available_columns
    ],
    width="stretch",
    hide_index=True,
)