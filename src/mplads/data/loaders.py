import sys
from pathlib import Path
import pandas as pd
import streamlit as st

# Path Setup
ROOT_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"

@st.cache_data
def load_unified_data() -> pd.DataFrame:
    """
    Loads the primary processed dataset (project_features.csv).
    If the file is missing, returns an empty DataFrame to prevent crashes.
    """
    file_path = PROCESSED_DATA_DIR / "project_features.csv"
    if not file_path.exists():
        st.warning(f"Data file not found at: {file_path}. Returning empty dataset.")
        return pd.DataFrame()
    return pd.read_csv(file_path)

@st.cache_data
def load_review_queue_data() -> pd.DataFrame:
    """Loads review queue dataset."""
    file_path = PROCESSED_DATA_DIR / "review_queue.csv"
    if not file_path.exists():
        return pd.DataFrame()
    return pd.read_csv(file_path)

@st.cache_data
def load_duplicate_data() -> pd.DataFrame:
    """Loads duplicate candidates dataset."""
    file_path = PROCESSED_DATA_DIR / "duplicate_candidates.csv"
    if not file_path.exists():
        return pd.DataFrame()
    return pd.read_csv(file_path)