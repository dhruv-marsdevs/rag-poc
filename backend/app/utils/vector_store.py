import os
import logging
from typing import List, Dict, Any
from langchain_chroma import Chroma
from chromadb.config import Settings
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


def get_embeddings():
    """
    Get the embeddings model based on environment configuration
    """
    if OPENAI_API_KEY:
        # Use OpenAI embeddings if API key is provided
        return OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    else:
        # Fall back to HuggingFace embeddings model
        return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


# Chroma configuration
CHROMA_PERSIST_DIRECTORY = os.path.join(os.getcwd(), "data", "chroma")
CHROMA_SETTINGS = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=CHROMA_PERSIST_DIRECTORY,
    anonymized_telemetry=False,
)

# Initialize Chroma client
_vector_store = None


def get_vector_store():
    """Get Chroma vector store instance"""
    global _vector_store
    if _vector_store is None:
        embeddings = get_embeddings()
        _vector_store = Chroma(
            persist_directory=CHROMA_PERSIST_DIRECTORY,
            embedding_function=embeddings,
            client_settings=CHROMA_SETTINGS,
        )
        logger.info("Initialized Chroma vector store")
    return _vector_store


def add_documents_to_vectorstore(chunks: List[Dict[str, Any]]):
    """Add document chunks to Chroma"""
    vector_store = get_vector_store()
    documents = [
        Document(page_content=chunk["text"], metadata=chunk["metadata"])
        for chunk in chunks
    ]
    vector_store.add_documents(documents)
    logger.info(f"Added {len(documents)} documents to Chroma")


def query_vectorstore(query: str, top_k: int = 3) -> List[Document]:
    """Query Chroma vector store"""
    vector_store = get_vector_store()
    return vector_store.similarity_search(query, k=top_k)
