import sys
from pathlib import Path
import pandas as pd
import streamlit as st

# Setup Root Directory & Path Resolution BEFORE imports
APP_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = APP_DIR.parent

for path in [str(ROOT_DIR), str(APP_DIR)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Safe package imports
from app.components.auth_ui import render_sidebar_auth

from src.mplads.auth import filter_by_district

# Streamlit Page Config
st.set_page_config(page_title="Overview", layout="wide")

# Render Sidebar Login & Authentication Info
render_sidebar_auth()

# Block Access if Not Authenticated
if not st.session_state.get("authenticated", False):
    st.warning("Please log in from the sidebar to access the Overview page.")
    st.stop()

st.title("📈 District Project Overview")

# Define Data Path
PROJECT_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "project_features.csv"
)

# Load Dataset Safely
@st.cache_data
def load_data(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        st.warning(f"Data file not found at: {file_path}")
        return pd.DataFrame()
    return pd.read_csv(file_path)

raw_df = load_data(PROJECT_FILE)

# Apply District-Level Role-Based Access Filter
df_filtered = filter_by_district(raw_df, district_col="district")

# Display Current District Scope Status
user_district = st.session_state.get("user_district")
if user_district:
    st.info(f"Displaying filtered metrics for **{user_district} District**")
else:
    st.info("Displaying aggregated metrics for **All Districts** (Central Admin)")

# Summary Metrics & Visualizations
if df_filtered.empty:
    st.warning("No records found for the selected scope or missing dataset.")
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Works", len(df_filtered))
    
    if "recommended_amount" in df_filtered.columns:
        col2.metric("Total Recommended (Cr)", f"₹{df_filtered['recommended_amount'].sum() / 1e7:.2f}")
    
    if "status" in df_filtered.columns:
        col3.metric("Completed Works", len(df_filtered[df_filtered["status"].astype(str).str.lower() == "completed"]))
        
        st.subheader("Project Status Breakdown")
        status_counts = df_filtered["status"].value_counts()
        st.bar_chart(status_counts)

    st.subheader("Project Details")
    st.dataframe(df_filtered, use_container_width=True)