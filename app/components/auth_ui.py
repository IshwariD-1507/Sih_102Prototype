import streamlit as st
from typing import Optional

from src.mplads.auth import filter_by_district, login_user, logout_user


def render_sidebar_auth() -> Optional[str]:
    """
    Render the authentication UI in the sidebar.

    Returns:
        The logged-in user's district, or None if the user is not logged in.
    """

    # ---------------------------------------------------------
    # Initialize session state
    # ---------------------------------------------------------

    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("user_id", None)
    st.session_state.setdefault("user_role", None)
    st.session_state.setdefault("user_district", None)
    st.session_state.setdefault("user_name", None)

    # ---------------------------------------------------------
    # Sidebar heading
    # ---------------------------------------------------------

    st.sidebar.title("🔐 Authentication")

    # ---------------------------------------------------------
    # Logged-in state
    # ---------------------------------------------------------

    if st.session_state["authenticated"]:

        st.sidebar.success("Authenticated")

        st.sidebar.write(
            f"**User:** {st.session_state.get('user_name', 'User')}"
        )

        st.sidebar.write(
            f"**Role:** {st.session_state.get('user_role', 'Unknown')}"
        )

        district = st.session_state.get("user_district")

        if district:
            st.sidebar.write(
                f"**Scope:** {district} District"
            )
        else:
            st.sidebar.write(
                "**Scope:** All Districts"
            )

        # -----------------------------------------------------
        # Logout
        # -----------------------------------------------------

        if st.sidebar.button(
            "Logout",
            use_container_width=True
        ):
            logout_user()
            st.rerun()

        return district

    # ---------------------------------------------------------
    # Login form
    # ---------------------------------------------------------

    with st.sidebar.form("mplads_login_form"):

        st.subheader("Sign in")

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True
        )

    # ---------------------------------------------------------
    # Process login
    # ---------------------------------------------------------

    if submitted:

        if login_user(
            username,
            password
        ):
            st.rerun()

        else:
            st.sidebar.error(
                "Invalid username or password."
            )

    return None


# Keep this available for any older code that imported it from here.
__all__ = [
    "render_sidebar_auth",
    "filter_by_district",
]