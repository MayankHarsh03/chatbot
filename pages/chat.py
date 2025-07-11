import streamlit as st
from uuid import uuid4
from datetime import datetime
from modules.query_engine import ask_question
from modules.utils import get_today, shorten_title
from modules.structured_compare import compare_documents
from modules.document_loader import load_and_split_documents
import json
import os

# ---- Page Config ----
st.set_page_config(layout="wide", page_title=" AI Assistant")

# ---- Theme Setup ----
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"


def toggle_theme():
    st.session_state.theme_mode = "light" if st.session_state.theme_mode == "dark" else "dark"


theme = st.session_state.theme_mode
dark = theme == "dark"

# ---- CSS Styling ----
st.markdown(f"""
    <style>
    html, body, [class*="st-"] {{
        background-color: {'#1e1e1e' if dark else '#ffffff'};
        color: {'#ffffff' if dark else '#000000'};
    }}
    .chat-bubble {{
        padding: 10px;
        border-radius: 10px;
        margin: 8px 0;
        border: 1px solid #888;
        background-color: {'#2b2b2b' if dark else '#f1f1f1'};
    }}
    .sidebar-title {{
        font-weight: bold;
        font-size: 20px;
        padding-bottom: 10px;
    }}
    .top-right {{
        position: fixed;
        top: 15px;
        right: 25px;
        z-index: 999;
    }}
    </style>
""", unsafe_allow_html=True)

# ---- Logout Function ----


def logout():
    for key in ["user", "chats", "uploaded_files", "current", "renaming_chat_id"]:
        if key in st.session_state:
            del st.session_state[key]
    st.success("✅ Logged out successfully.")
    st.switch_page("pages/login.py")


# ---- Session State Init ----
if "user" not in st.session_state:
    st.warning("Please log in first.")
    st.switch_page("pages/login.py")
    st.stop()

if "chats" not in st.session_state or not isinstance(st.session_state.chats, dict):
    cid = str(uuid4())
    st.session_state.chats = {
        cid: {"title": "New Chat", "messages": [], "vector_db": None}
    }
    st.session_state.current = cid

if "renaming_chat_id" not in st.session_state:
    st.session_state.renaming_chat_id = None

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# ---- Sidebar: Chat History ----
with st.sidebar:
    st.markdown('<div class="sidebar-title">💬 Chats</div>',
                unsafe_allow_html=True)
    st.markdown(f"📅 **{get_today()}**")

    if st.button("➕ New Chat"):
        new_id = str(uuid4())
        st.session_state.chats[new_id] = {
            "title": "New Chat", "messages": [], "vector_db": None
        }
        st.session_state.current = new_id
        st.session_state.renaming_chat_id = None
        st.rerun()

    for chat_id, data in list(st.session_state.chats.items()):
        is_active = (chat_id == st.session_state.current)
        cols = st.columns([5, 1, 1])
        if cols[0].button(data["title"], key=f"select-{chat_id}"):
            st.session_state.current = chat_id
            st.session_state.renaming_chat_id = None
            st.rerun()
        if cols[1].button("✏️", key=f"rename-{chat_id}"):
            st.session_state.renaming_chat_id = chat_id
        if cols[2].button("🗑️", key=f"delete-{chat_id}"):
            st.session_state.chats.pop(chat_id)
            if st.session_state.current == chat_id:
                st.session_state.current = next(
                    iter(st.session_state.chats), None)
            st.session_state.renaming_chat_id = None
            st.rerun()

        if st.session_state.renaming_chat_id == chat_id:
            new_title = st.text_input(
                "Rename:", value=data["title"], key=f"rename-input-{chat_id}")
            if st.button("Save", key=f"save-title-{chat_id}"):
                st.session_state.chats[chat_id]["title"] = new_title
                st.session_state.renaming_chat_id = None
                st.rerun()

# ---- Top Right Controls ----
with st.container():
    col1, col2, col3 = st.columns([0.75, 0.15, 0.10])
    with col2:
        if st.button("🌞" if dark else "🌙", on_click=toggle_theme):
            st.rerun()
    with col3:
        if st.button("🔒 Logout"):
            logout()

# ---- Main Chat Interface ----
st.title("🤖 AI Assistant")

# ---- Welcome Message on First Login ----
if st.session_state.get("show_welcome"):
    st.success(f"👋 Welcome, {st.session_state['user'].capitalize()}!")


chat = st.session_state.chats[st.session_state.current]

for user, bot in chat["messages"]:
    with st.chat_message("user"):
        st.markdown(
            f'<div class="chat-bubble">{user}</div>', unsafe_allow_html=True)
    with st.chat_message("assistant"):
        st.markdown(
            f'<div class="chat-bubble">{bot}</div>', unsafe_allow_html=True)

if st.button("📤 Upload Files"):
    st.switch_page("pages/upload.py")

user_input = st.chat_input("Ask your question...")

if user_input:
    if "show_welcome" in st.session_state:
        del st.session_state["show_welcome"]

    with st.chat_message("user"):
        st.markdown(
            f'<div class="chat-bubble">{user_input}</div>', unsafe_allow_html=True)

    if chat["title"] == "New Chat" and not chat["messages"]:
        chat["title"] = shorten_title(user_input)

    if chat.get("vector_db") is None and st.session_state.uploaded_files:
        with st.spinner("🔍 Reading documents..."):
            chunks = load_and_split_documents(st.session_state.uploaded_files)
            if chunks:
                from modules.vector_store import create_vector_store
                vectordb = create_vector_store(chunks)
                chat["vector_db"] = vectordb
            else:
                chat["vector_db"] = None
                st.error("❌ Failed to process uploaded documents.")

    with st.spinner("🤖 Thinking..."):
        try:
            if "compare" in user_input.lower() and len(st.session_state.uploaded_files) >= 2:
                doc_chunks = load_and_split_documents(
                    st.session_state.uploaded_files)
                if len(doc_chunks) < 2:
                    reply = "❌ Could not load enough content to compare."
                else:
                    half = len(doc_chunks) // 2
                    doc1 = "\n".join(
                        [d.page_content for d in doc_chunks[:half]])
                    doc2 = "\n".join(
                        [d.page_content for d in doc_chunks[half:]])
                    reply = compare_documents(doc1, doc2, prompt=user_input)
            else:
                reply = ask_question(chat.get("vector_db"), user_input)
        except Exception as e:
            reply = f"❌ Error: {str(e)}"

    with st.chat_message("assistant"):
        st.markdown(
            f'<div class="chat-bubble">{reply}</div>', unsafe_allow_html=True)

    chat["messages"].append((user_input, reply))

    # ✅ Save chats after response (excluding vector_db which can't be serialized)
    user = st.session_state.get("user")
    if user:
        with open("users.json", "r") as f:
            data = json.load(f)
        if user not in data:
            data[user] = {}

        # Remove vector_db before saving to JSON
        clean_chats = {}
        for chat_id, chat_data in st.session_state["chats"].items():
            clean_chats[chat_id] = {
                "title": chat_data["title"],
                "messages": chat_data["messages"]
            }

        data[user]["chats"] = clean_chats

        with open("users.json", "w") as f:
            json.dump(data, f, indent=4)
