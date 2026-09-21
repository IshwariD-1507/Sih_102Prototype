import sys
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.mplads.auth import filter_by_district
from app.components.auth_ui import render_sidebar_auth

st.set_page_config(page_title="Duplicate Overlap", layout="wide")

render_sidebar_auth()

if not st.session_state.get("authenticated", False):
    st.warning("Please log in from the sidebar to access Duplicate Overlap detection.")
    st.stop()

st.title("👯 Duplicate & Overlap Detection")

INPUT_FILE = ROOT_DIR / "data" / "processed" / "duplicate_candidates.csv"

@st.cache_data
def load_overlap_data():
    if not INPUT_FILE.exists():
        return pd.DataFrame()
    return pd.read_csv(INPUT_FILE)

df = load_overlap_data()

if df.empty:
    st.warning("⚠️ `data/processed/duplicate_candidates.csv` was not found or is empty. Please run your data processing pipeline first.")
else:
    df_filtered = filter_by_district(df, district_col="district")
    st.subheader("Potential Duplicate Project Candidates")
    st.dataframe(df_filtered, use_container_width=True)