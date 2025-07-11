import streamlit as st

st.set_page_config(page_title="AI Assistant", layout="wide")

# Redirect to login if not logged in
if "username" not in st.session_state:
    st.switch_page("pages/login.py")  # Ensure it redirects to login

# Optional: If logged in, auto-redirect to chat
else:
    st.switch_page("pages/chat.py")
