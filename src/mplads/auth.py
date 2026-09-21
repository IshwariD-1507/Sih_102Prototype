import re
from typing import Optional, Dict, Any

import pandas as pd
import streamlit as st


# =========================================================
# MOCK USER DATABASE
# =========================================================

USERS_DB: Dict[str, Dict[str, Any]] = {

    "admin": {
        "password": "adminpassword",
        "role": "Central Admin",
        "district": None,
        "name": "Central Officer",
    },

    "collector_pune": {
        "password": "punepassword",
        "role": "District Officer",
        "district": "Pune",
        "name": "District Magistrate Pune",
    },

    "collector_mumbai": {
        "password": "mumbaipassword",
        "role": "District Officer",
        "district": "Mumbai City",
        "name": "District Magistrate Mumbai",
    },
}


# =========================================================
# AUTHENTICATION
# =========================================================

def login_user(
    username: str,
    password: str
) -> bool:

    """
    Validate credentials and initialize session state.
    """

    username = (
        username
        .strip()
        .lower()
    )

    user = USERS_DB.get(username)

    if user is None:
        return False

    if user["password"] != password:
        return False

    st.session_state["authenticated"] = True
    st.session_state["user_id"] = username
    st.session_state["user_role"] = user["role"]
    st.session_state["user_district"] = user["district"]
    st.session_state["user_name"] = user["name"]

    return True


def logout_user() -> None:

    """
    Clear authentication-related session state.
    """

    st.session_state["authenticated"] = False
    st.session_state["user_id"] = None
    st.session_state["user_role"] = None
    st.session_state["user_district"] = None
    st.session_state["user_name"] = None


# =========================================================
# DISTRICT NORMALIZATION
# =========================================================

def _normalize_district_name(
    district: Optional[str]
) -> str:

    """
    Normalize district names so that variations such as:

        Pune
        PUNE
        Pune District

    can be compared consistently.
    """

    if district is None:
        return ""

    value = str(district).strip().upper()

    value = re.sub(
        r"\s+DISTRICT$",
        "",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# =========================================================
# EXTRACT DISTRICT FROM IDA
# =========================================================

def _extract_district_from_ida(
    ida_series: pd.Series
) -> pd.Series:

    """
    Extract the district name from the MPLADS IDA field.

    Examples:

        PUNE(DISTRICT COLLECTOR PUNE_IDA)
        -> Pune

        MUMBAI(DISTRICT COLLECTOR MUMBAI CITY_IDA)
        -> Mumbai City

        DHARWAD(DEPUTY COMMISSIONER DHARWAR_IDA)
        -> Dharwad
    """

    values = (
        ida_series
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # Everything before the first "(" is the district label
    extracted = (
        values
        .str.split(
            "(",
            n=1
        )
        .str[0]
        .str.strip()
    )

    # Special handling for the Mumbai City IDA.
    #
    # The official IDA can appear as:
    #
    # MUMBAI(DISTRICT COLLECTOR MUMBAI CITY_IDA)
    #
    # while our user database calls this:
    #
    # Mumbai City
    #

    extracted = extracted.where(
        ~values.str.contains(
            "MUMBAI CITY_IDA",
            case=False,
            na=False
        ),
        "Mumbai City"
    )

    return extracted


# =========================================================
# ENSURE DISTRICT COLUMN EXISTS
# =========================================================

def ensure_district_column(
    df: pd.DataFrame
) -> pd.DataFrame:

    """
    Return a copy of the dataframe with a standardized
    'district' column.

    Priority:

    1. Existing 'district' column
    2. IDA-derived district
    """

    df = df.copy()

    # -----------------------------------------------------
    # Existing district column
    # -----------------------------------------------------

    if "district" in df.columns:

        df["district"] = (
            df["district"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        return df

    # -----------------------------------------------------
    # Derive from IDA
    # -----------------------------------------------------

    if "IDA" in df.columns:

        df["district"] = (
            _extract_district_from_ida(
                df["IDA"]
            )
        )

        return df

    # -----------------------------------------------------
    # No district information available
    # -----------------------------------------------------

    df["district"] = ""

    return df


# =========================================================
# DISTRICT FILTER
# =========================================================

def filter_by_district(
    df: pd.DataFrame,
    district_col: str = "district"
) -> pd.DataFrame:

    """
    Apply role-based district filtering.

    Central Admin:
        Returns all records.

    District Officer:
        Returns ONLY records belonging to the assigned district.

    IMPORTANT:
        If a district-specific user is logged in and the dataset
        does not contain usable district information, this function
        returns an empty dataframe rather than accidentally exposing
        the entire dataset.
    """

    if df is None or df.empty:

        return df.copy()

    df = df.copy()

    assigned_district = st.session_state.get(
        "user_district"
    )

    # -----------------------------------------------------
    # Central Admin
    # -----------------------------------------------------

    if not assigned_district:

        return df

    # -----------------------------------------------------
    # Ensure district information exists
    # -----------------------------------------------------

    if district_col not in df.columns:

        df = ensure_district_column(df)

    # -----------------------------------------------------
    # If we STILL cannot determine district,
    # fail closed for district users.
    # -----------------------------------------------------

    if district_col not in df.columns:

        return df.iloc[0:0].copy()

    district_values = (
        df[district_col]
        .fillna("")
        .astype(str)
        .map(_normalize_district_name)
    )

    target_district = _normalize_district_name(
        assigned_district
    )

    filtered = df[
        district_values == target_district
    ].copy()

    return filtered


# =========================================================
# AUTHORIZATION HELPERS
# =========================================================

def is_authenticated() -> bool:

    return bool(
        st.session_state.get(
            "authenticated",
            False
        )
    )


def is_central_admin() -> bool:

    return (
        st.session_state.get(
            "user_role"
        )
        == "Central Admin"
    )


def get_current_district() -> Optional[str]:

    return st.session_state.get(
        "user_district"
    )


__all__ = [
    "USERS_DB",
    "login_user",
    "logout_user",
    "filter_by_district",
    "ensure_district_column",
    "is_authenticated",
    "is_central_admin",
    "get_current_district",
]