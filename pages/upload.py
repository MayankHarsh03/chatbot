# upload.py
import streamlit as st
from modules.document_loader import load_and_split_documents
import os
import json
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="📤 Upload Documents", layout="wide")
st.title("📤 Upload Documents")

# ---- Theme Setup ----
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"


def toggle_theme():
    st.session_state.theme_mode = "light" if st.session_state.theme_mode == "dark" else "dark"


theme = st.session_state.theme_mode
dark = theme == "dark"

# ---- Logout Function ----


def logout():
    for key in ["user", "chats", "uploaded_files", "current", "renaming_chat_id"]:
        if key in st.session_state:
            del st.session_state[key]
    st.success("✅ Logged out successfully.")
    st.switch_page("pages/login.py")


# ---- Check login ----
if "user" not in st.session_state:
    st.warning("Please login first.")
    st.switch_page("pages/login.py")
    st.stop()

username = st.session_state.user
user_upload_dir = f"uploads/{username}"
os.makedirs(user_upload_dir, exist_ok=True)

# ---- Top Right Buttons ----
col1, col2, col3 = st.columns([0.7, 0.2, 0.1])
with col2:
    if st.button("🌞" if dark else "🌙", on_click=toggle_theme):
        st.rerun()
with col3:
    if st.button("🔒 Logout"):
        logout()

# ---- Initialize file list ----
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# ---- File uploader ----
uploaded = st.file_uploader("Upload PDF/DOCX/TXT/Image files", accept_multiple_files=True,
                            type=["pdf", "PDF", "docx", "DOCX", "txt", "TXT", "jpg", "JPG", "jpeg", "JPEG", "png", "PNG"])

if uploaded:
    new_files = []
    existing_names = [f.name for f in st.session_state.uploaded_files]

    for file in uploaded:
        if file.name not in existing_names:
            # Save to user folder
            file_path = os.path.join(user_upload_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            # Reload the file after saving so that each file is independently processed
            with open(file_path, "rb") as f:
                file_bytes = BytesIO(f.read())
                file_bytes.name = file.name
                new_files.append(file_bytes)

    if new_files:
        st.session_state.uploaded_files.extend(new_files)
        st.success(f"✅ Added {len(new_files)} new file(s).")

# ---- File preview ----
if st.session_state.uploaded_files:
    st.subheader("📄 Uploaded File Preview")
    for i, file in enumerate(st.session_state.uploaded_files, start=1):
        file.seek(0)
        file_size = len(file.read())
        st.markdown(f"**File {i}:** `{file.name}` — {file_size} bytes")
        file.seek(0)

        if file.name.lower().endswith((".png", ".jpg", ".jpeg")):
            image = Image.open(file)
            st.image(image, width=150)
        elif file.name.lower().endswith((".txt", ".docx")):
            try:
                text = file.read(2000).decode(errors='ignore')
                st.code(text[:500])
            except:
                st.write("⚠️ Preview not available.")
        file.seek(0)

    if st.button("🗑️ Clear Uploaded Files"):
        st.session_state.uploaded_files = []
        st.rerun()

# ---- Navigation ----
if st.button("💬 Go to Chat"):
    st.switch_page("pages/chat.py")
