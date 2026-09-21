import sys
from pathlib import Path
import streamlit as st

# Ensure project root (Sih_102Prototype) and app folder are in sys.path
APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent

for path in [str(ROOT_DIR), str(APP_DIR)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Safe package imports
from app.components.auth_ui import render_sidebar_auth

from src.mplads.data.loaders import load_unified_data
from src.mplads.auth import filter_by_district

st.set_page_config(
    page_title="MPLADS Project Monitoring System",
    page_icon="📊",
    layout="wide"
)

# Initialize Session Auth State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Render Login UI & Get Active District
active_district = render_sidebar_auth()

if not st.session_state["authenticated"]:
    st.title("MPLADS Project Monitoring & Audit Portal")
    st.warning("Please log in from the sidebar to access district project insights.")
    st.stop()

# Load and Filter Data
raw_df = load_unified_data()

if raw_df.empty:
    st.error("No data loaded. Please check that processed files exist in `data/processed/`.")
    st.stop()

district_df = filter_by_district(raw_df, district_col="district")

st.title("📌 MPLADS Executive Dashboard")

if active_district:
    st.subheader(f"District Overview: {active_district}")
else:
    st.subheader("National / State Level Overview")

col1, col2, col3 = st.columns(3)
col1.metric("Total Works Monitored", len(district_df))

if "recommended_amount" in district_df.columns:
    col2.metric("Total Recommended (Cr)", f"₹{district_df['recommended_amount'].sum() / 1e7:.2f}")

if "status" in district_df.columns:
    col3.metric("Active Projects", len(district_df[district_df["status"] == "In Progress"]))

st.dataframe(district_df.head(50), use_container_width=True)