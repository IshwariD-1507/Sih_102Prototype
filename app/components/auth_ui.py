import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any

# Mock User Database
USERS_DB: Dict[str, Dict[str, Any]] = {
    "admin": {
        "password": "adminpassword",
        "role": "Central Admin",
        "district": None,  # None means access to ALL districts
        "name": "Central Officer"
    },
    "collector_pune": {
        "password": "punepassword",
        "role": "District Officer",
        "district": "Pune",
        "name": "District Magistrate Pune"
    },
    "collector_mumbai": {
        "password": "mumbaipassword",
        "role": "District Officer",
        "district": "Mumbai City",
        "name": "District Magistrate Mumbai"
    }
}

def login_user(username: str, password: str) -> bool:
    """Validate credentials and initialize the session state."""
    user = USERS_DB.get(username.lower().strip())
    if user and user["password"] == password:
        st.session_state["authenticated"] = True
        st.session_state["user_id"] = username
        st.session_state["user_role"] = user["role"]
        st.session_state["user_district"] = user["district"]
        st.session_state["user_name"] = user["name"]
        return True
    return False

def logout_user() -> None:
    """Clear session data."""
    st.session_state["authenticated"] = False
    st.session_state["user_id"] = None
    st.session_state["user_role"] = None
    st.session_state["user_district"] = None
    st.session_state["user_name"] = None

def filter_by_district(df: pd.DataFrame, district_col: str = "district") -> pd.DataFrame:
    """
    Filters input DataFrame based on logged-in user's assigned district.
    If Central Admin, returns original DataFrame unfiltered.
    """
    if df.empty or district_col not in df.columns:
        return df

    assigned_district: Optional[str] = st.session_state.get("user_district")
    
    # If a specific district is assigned, scope data to that district
    if assigned_district:
        return df[df[district_col].astype(str).str.upper() == assigned_district.upper()].copy()
    
    return df