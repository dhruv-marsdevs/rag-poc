import os
import logging
from typing import List, Dict, Any, Optional
from functools import lru_cache
from langchain_chroma import Chroma
from chromadb.config import Settings
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain_core.documents import Document
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Chroma configuration
CHROMA_PERSIST_DIRECTORY = os.path.join(settings.DATA_DIR, "chroma")
CHROMA_SETTINGS = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=CHROMA_PERSIST_DIRECTORY,
    anonymized_telemetry=False,
)

# Global to hold the vector store instance
_vector_store = None


@lru_cache
def get_embeddings():
    """
    Get the embeddings model based on environment configuration.
    Caches the result for better performance.
    """
    try:
        if settings.OPENAI_API_KEY:
            # Use OpenAI embeddings if API key is provided
            return OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        else:
            # Fall back to HuggingFace embeddings model
            logger.info(
                f"Using HuggingFace embeddings model: {settings.EMBEDDING_MODEL}"
            )
            return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    except Exception as e:
        logger.error(f"Error creating embeddings model: {str(e)}", exc_info=True)
        raise


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
def get_vector_store():
    global _vector_store
    if _vector_store is None:
        try:
            embeddings = get_embeddings()
            # Updated Chroma initialization for new client architecture
            _vector_store = Chroma(
                persist_directory=CHROMA_PERSIST_DIRECTORY,
                embedding_function=embeddings,
                # Removed client_settings parameter
            )
            logger.info("Chroma vector store initialized")
        except Exception as e:
            logger.error(f"Vector store init failed: {str(e)}")
            raise
    return _vector_store


def get_vector_store_status():
    try:
        vector_store = get_vector_store()
        count = vector_store._collection.count()
        return {
            "status": "ok",
            "document_count": count,
            "persist_directory": CHROMA_PERSIST_DIRECTORY,
            "embedding_model": settings.EMBEDDING_MODEL,
        }
    except Exception as e:
        logger.error(f"Error getting vector store status: {str(e)}")
        return {"status": "error", "error": str(e)}


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
def add_documents_to_vectorstore(chunks: List[Dict[str, Any]]):
    """
    Add document chunks to the vector store.
    Uses retry logic for better resilience.

    Args:
        chunks: List of dictionaries with text and metadata
    """
    if not chunks or len(chunks) == 0:
        logger.warning("No chunks provided to add to vector store")
        return

    try:
        vector_store = get_vector_store()
        if not vector_store:
            raise ValueError("Vector store not available")

        # Convert chunks to LangChain Documents
        documents = []
        for chunk in chunks:
            doc = Document(page_content=chunk["text"], metadata=chunk["metadata"])
            documents.append(doc)

        # Add to the vector store
        vector_store.add_documents(documents)
        logger.info(f"Added {len(documents)} chunks to vector store")

        # Verify addition
        try:
            if hasattr(vector_store, "_collection") and hasattr(
                vector_store._collection, "count"
            ):
                collection_size = vector_store._collection.count()
                logger.info(f"Vector store now contains {collection_size} documents")
        except Exception as e:
            logger.warning(f"Could not verify document count after adding: {str(e)}")

    except Exception as e:
        logger.error(f"Error adding documents to vector store: {str(e)}", exc_info=True)
        raise


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
def query_vectorstore(
    query: str, top_k: int = 3, user_id: Optional[str] = None
) -> List[Document]:
    """
    Query the vector store for relevant document chunks.
    Uses retry logic for better resilience.

    Args:
        query: The query string
        top_k: Number of results to return
        user_id: Optional user ID to filter results

    Returns:
        List of relevant document chunks with metadata
    """
    if not query or not query.strip():
        logger.warning("Empty query provided to vector store")
        return []

    try:
        vector_store = get_vector_store()
        if not vector_store:
            logger.error("Failed to initialize vector store for query")
            return []

        try:
            logger.info(f"Using Chroma vector store for query: {query}")
            # Handle filtering if needed
            if user_id:
                # Chroma uses different filtering syntax
                filter_dict = {"user_id": {"$eq": user_id}}
                results = vector_store.similarity_search(
                    query, k=top_k, filter=filter_dict
                )
            else:
                results = vector_store.similarity_search(query, k=top_k)
            logger.info(f"Chroma query returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error querying Chroma vector store: {str(e)}", exc_info=True)
            return []

    except Exception as e:
        logger.error(f"Error querying vector store: {str(e)}", exc_info=True)
        # Return empty results instead of raising to avoid breaking the app
        return []


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
def delete_document_from_vectorstore(document_id: str):
    """
    Delete all chunks related to a specific document from the vector store.
    Uses retry logic for better resilience.

    Args:
        document_id: ID of the document to delete
    """
    if not document_id:
        logger.warning("No document_id provided for deletion")
        return

    try:
        vector_store = get_vector_store()
        if not vector_store:
            raise ValueError("Vector store not available")

        try:
            # In Chroma we need to get the IDs first and then delete by ID
            # The where filter needs to use the $eq operator syntax
            where_filter = {"document_id": {"$eq": document_id}}
            
            # Get IDs of matching documents
            matching_docs = vector_store._collection.get(where=where_filter)
            
            if matching_docs and "ids" in matching_docs and len(matching_docs["ids"]) > 0:
                # Delete documents by ID
                vector_store._collection.delete(ids=matching_docs["ids"])
                logger.info(
                    f"Deleted {len(matching_docs['ids'])} chunks for document {document_id}"
                )
            else:
                logger.warning(f"No chunks found for document {document_id}")
        except Exception as e:
            logger.error(f"Error deleting from Chroma: {str(e)}", exc_info=True)
            raise

    except Exception as e:
        logger.error(
            f"Error deleting document from vector store: {str(e)}", exc_info=True
        )
        raise
