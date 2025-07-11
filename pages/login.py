import streamlit as st
import json
import os
from uuid import uuid4


USER_DB = "users.json"

# Initialize user database if not exists
if not os.path.exists(USER_DB):
    with open(USER_DB, "w") as f:
        json.dump({}, f)

with open(USER_DB, "r") as f:
    users = json.load(f)


def save_users():
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)


def load_user_data(username):
    """Load user's chat history and uploaded files into session state."""
    user_data = users.get(username, {})
    st.session_state["chat_history"] = user_data.get("chats", [])
    st.session_state["uploaded_files"] = user_data.get("files", [])


def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state["user"] = username
            load_user_data(username)
            st.success(f"✅ Logged in as {username}")
            st.switch_page("pages/chat.py")  # Redirect to chat page
        else:
            st.error("❌ Invalid username or password")
    if username in users and users[username]["password"] == password:
        st.session_state["user"] = username
        st.session_state["show_welcome"] = True  # 👈 Show welcome on login
        st.success(f"✅ Logged in as {username}")
        # Restore chat history and files
        st.session_state["chats"] = users[username].get("chats", {})
        st.session_state["uploaded_files"] = []
        st.session_state["current"] = next(
            iter(st.session_state["chats"]), str(uuid4()))
        st.success(f"✅ Logged in as {username}")
        st.switch_page("pages/chat.py")

    st.markdown("---")

    st.subheader("New user? Create an account:")
    new_user = st.text_input("New username")
    new_pass = st.text_input("New password", type="password")

    if st.button("Register"):
        if new_user in users:
            st.warning("⚠️ Username already exists")
        else:
            users[new_user] = {
                "password": new_pass,
                "chats": [],
                "files": []
            }
            save_users()
            st.success("✅ Registered! Please login now.")


# Run login interface
login()
