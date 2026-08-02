import streamlit as st
from services.persistance.exercise_repository import get_or_create_user

def render_login_wall():

    if st.session_state.get("user_id") is not None: # if user is already login
        return True

    st.title("AI Real-time GYM Trainer")
    st.markdown("### Welcome! Please enter a username to start.")

    with st.form("login_form",clear_on_submit=False):
        username = st.text_input("Name (Unique)",placeholder="unique name e.q. Bob")
        submit_button = st.form_submit_button("Start session,",width="stretch")

    if submit_button:
        if not username:
            st.error("Name cannot be empty")
            return False

        user = get_or_create_user(username)

        st.session_state["username"] = user["username"]
        st.session_state["user_id"] = user["id"]

        st.rerun()

    return False
