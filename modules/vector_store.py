from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS


def create_vector_store(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="/Users/mayankharsh/Documents/models/all-MiniLM-L6-v2")
    vectordb = FAISS.from_documents(chunks, embeddings)
    return vectordb
