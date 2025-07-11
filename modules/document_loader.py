import os
import tempfile
from io import BytesIO
from langchain.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
from langchain.schema import Document
import streamlit as st

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


def extract_text_from_image(img):
    return pytesseract.image_to_string(img).strip()


def process_uploaded_file(file):
    filename = file.name
    ext = filename.split(".")[-1].lower()
    file_bytes = file.read()
    file.seek(0)  # reset pointer for reuse

    file_path = os.path.join(tempfile.gettempdir(), filename)
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    try:
        if ext == "pdf":
            try:
                loader = PyPDFLoader(file_path)
                docs = loader.load()
            except Exception:
                # Fallback: OCR for scanned PDF
                images = convert_from_bytes(file_bytes)
                text = "\n".join([extract_text_from_image(img)
                                 for img in images])
                docs = [Document(page_content=text)]
        elif ext == "docx":
            loader = Docx2txtLoader(file_path)
            docs = loader.load()
        elif ext == "txt":
            loader = TextLoader(file_path)
            docs = loader.load()
        elif ext in ["png", "jpg", "jpeg"]:
            image = Image.open(file_path)
            text = extract_text_from_image(image)
            docs = [Document(page_content=text)]
        else:
            st.warning(f"⚠️ Unsupported file type: {filename}")
            return []
        chunks = splitter.split_documents(docs)
        return chunks
    except Exception as e:
        st.error(f"❌ Failed to process {filename}: {e}")
        return []


def load_and_split_documents(files):
    all_chunks = []
    for file in files:
        chunks = process_uploaded_file(file)
        all_chunks.extend(chunks)
    return all_chunks


def load_and_split_files_from_paths(paths):
    all_chunks = []
    for path in paths:
        try:
            filename = os.path.basename(path)
            with open(path, "rb") as f:
                file_like = BytesIO(f.read())
                file_like.name = filename  # ❗ This line mimics an uploaded file
                chunks = process_uploaded_file(file_like)
                all_chunks.extend(chunks)
        except Exception as e:
            st.error(f"❌ Failed to read file: {path}: {e}")
    return all_chunks
