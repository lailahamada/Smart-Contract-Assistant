from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import CHROMA_PATH
from app.core.config import GOOGLE_API_KEY


def create_vectorstore(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY,
        task_type="RETRIEVAL_QUERY"
    )

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    return db


def load_vectorstore():
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001"
    )

    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
