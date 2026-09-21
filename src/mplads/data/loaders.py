from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# PROJECT PATHS
# =========================================================

# loaders.py
#   ↓
# data/
#   ↓
# mplads/
#   ↓
# src/
#   ↓
# Sih_102Prototype/   ← project root
#
# parents[3] therefore points to Sih_102Prototype.

ROOT_DIR = Path(__file__).resolve().parents[3]

PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"


# =========================================================
# HELPER
# =========================================================

def _load_csv(filename: str) -> pd.DataFrame:
    """
    Load a CSV from data/processed.

    Returns an empty DataFrame if the file does not exist
    or cannot be read.
    """

    file_path = PROCESSED_DATA_DIR / filename

    if not file_path.exists():
        st.warning(
            f"Data file not found:\n\n"
            f"`{file_path}`"
        )
        return pd.DataFrame()

    try:
        return pd.read_csv(file_path)

    except Exception as exc:
        st.error(
            f"Could not load `{filename}`.\n\n"
            f"Error: {exc}"
        )
        return pd.DataFrame()


# =========================================================
# UNIFIED PROJECT DATA
# =========================================================

@st.cache_data
def load_unified_data() -> pd.DataFrame:
    """
    Load the main project feature dataset.

    Expected file:
        data/processed/project_features.csv
    """

    return _load_csv(
        "project_features.csv"
    )


# =========================================================
# REVIEW QUEUE
# =========================================================

@st.cache_data
def load_review_queue_data() -> pd.DataFrame:
    """
    Load the project review queue.

    Expected file:
        data/processed/review_queue.csv
    """

    return _load_csv(
        "review_queue.csv"
    )


# =========================================================
# DUPLICATE / OVERLAP DATA
# =========================================================

@st.cache_data
def load_duplicate_data() -> pd.DataFrame:
    """
    Load duplicate / overlap candidate records.

    Expected file:
        data/processed/duplicate_candidates.csv
    """

    return _load_csv(
        "duplicate_candidates.csv"
    )