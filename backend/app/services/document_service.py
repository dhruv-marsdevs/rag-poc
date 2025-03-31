import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import pypdf
import docx
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict

from app.core.config import get_settings
from app.schemas.document import DocumentResponse
from app.services.vector_store_service import (
    add_documents_to_vectorstore,
    delete_document_from_vectorstore,
)
from app.models.document import Document

settings = get_settings()
logger = logging.getLogger(__name__)


def process_document(
    file_path: str, document_id: str, filename: str, user_id: str
) -> None:
    """
    Process a document, extract text, split into chunks, and add to vector store.

    Args:
        file_path: Path to the document file
        document_id: Unique ID of the document
        filename: Original filename of the document
        user_id: ID of the user who uploaded the document
    """
    logger.info(
        f"Processing document: {filename} (ID: {document_id}) for user: {user_id}"
    )

    try:
        # Extract text based on file type
        if file_path.endswith(".pdf"):
            text_chunks = process_pdf(file_path, document_id, filename, user_id)
        elif file_path.endswith(".docx"):
            text_chunks = process_docx(file_path, document_id, filename, user_id)
        elif file_path.endswith(".txt"):
            text_chunks = process_txt(file_path, document_id, filename, user_id)
        else:
            logger.error(f"Unsupported file type: {file_path}")
            return

        # Add the chunks to the vector store
        if text_chunks and len(text_chunks) > 0:
            logger.info(
                f"Adding {len(text_chunks)} chunks to vector store for document {document_id}"
            )
            try:
                add_documents_to_vectorstore(text_chunks)
                logger.info(f"Document {document_id} processed successfully")
            except Exception as e:
                logger.error(
                    f"Error adding document to vector store: {str(e)}", exc_info=True
                )
                # Continue execution - file is saved even if vector store fails
        else:
            logger.warning(f"No text chunks extracted from document {document_id}")

    except Exception as e:
        logger.error(
            f"Error processing document {document_id}: {str(e)}", exc_info=True
        )


def process_pdf(
    file_path: str, document_id: str, filename: str, user_id: str
) -> List[Dict[str, Any]]:
    """
    Process a PDF file, extract text, and create chunks with metadata.

    Args:
        file_path: Path to the PDF file
        document_id: Unique ID of the document
        filename: Original filename of the document
        user_id: ID of the user who uploaded the document

    Returns:
        List of dictionaries with text chunks and metadata
    """
    try:
        # Extract text from PDF
        pdf_reader = pypdf.PdfReader(file_path)
        text_by_page = []

        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text.strip():  # Skip empty pages
                text_by_page.append((i + 1, page_text))

        # Split the text into chunks
        return create_chunks_with_metadata(text_by_page, document_id, filename, user_id)

    except Exception as e:
        logger.error(f"Error processing PDF {file_path}: {str(e)}", exc_info=True)
        return []


def process_docx(
    file_path: str, document_id: str, filename: str, user_id: str
) -> List[Dict[str, Any]]:
    """
    Process a DOCX file, extract text, and create chunks with metadata.

    Args:
        file_path: Path to the DOCX file
        document_id: Unique ID of the document
        filename: Original filename of the document
        user_id: ID of the user who uploaded the document

    Returns:
        List of dictionaries with text chunks and metadata
    """
    try:
        # Extract text from DOCX
        doc = docx.Document(file_path)
        full_text = []

        for paragraph in doc.paragraphs:
            if paragraph.text.strip():  # Skip empty paragraphs
                full_text.append(paragraph.text)

        # DOCX doesn't have page numbers, so we'll use a tuple with None for page
        combined_text = "\n".join(full_text)
        return create_chunks_with_metadata(
            [(None, combined_text)], document_id, filename, user_id
        )

    except Exception as e:
        logger.error(f"Error processing DOCX {file_path}: {str(e)}", exc_info=True)
        return []


def process_txt(
    file_path: str, document_id: str, filename: str, user_id: str
) -> List[Dict[str, Any]]:
    """
    Process a TXT file, extract text, and create chunks with metadata.

    Args:
        file_path: Path to the TXT file
        document_id: Unique ID of the document
        filename: Original filename of the document
        user_id: ID of the user who uploaded the document

    Returns:
        List of dictionaries with text chunks and metadata
    """
    try:
        # Read the text file with error handling for different encodings
        text = ""
        try:
            # Try UTF-8 first (most common)
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            # Fall back to Latin-1 (should handle most text files)
            with open(file_path, 'r', encoding='latin-1') as f:
                text = f.read()
            logger.warning(f"Used Latin-1 encoding for {filename} as UTF-8 failed")
        
        # Skip if empty
        if not text.strip():
            logger.warning(f"No content found in text file: {filename}")
            return []
        
        # Text files don't have page numbers, so we'll use a tuple with None for page
        return create_chunks_with_metadata(
            [(None, text)], document_id, filename, user_id
        )

    except Exception as e:
        logger.error(f"Error processing TXT {file_path}: {str(e)}", exc_info=True)
        return []


def create_chunks_with_metadata(
    text_by_page: List[tuple], document_id: str, filename: str, user_id: str
) -> List[Dict[str, Any]]:
    """
    Split text into chunks and add metadata.

    Args:
        text_by_page: List of tuples (page_number, text)
        document_id: Unique ID of the document
        filename: Original filename of the document
        user_id: ID of the user who uploaded the document

    Returns:
        List of dictionaries with text chunks and metadata
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
    )

    chunks_with_metadata = []

    for page_num, text in text_by_page:
        chunks = text_splitter.split_text(text)

        for chunk in chunks:
            # Ensure no None values in metadata - convert to strings or appropriate defaults
            source = filename
            if page_num is not None:
                source = f"{filename} (page {page_num})"
                
            # Convert None to empty string or appropriate defaults for vector store compatibility
            metadata = {
                "document_id": document_id,
                "document": filename,
                "page": str(page_num) if page_num is not None else "0",  # Use "0" instead of None
                "text": chunk,
                "user_id": user_id,
                "source": source,
                "created_at": datetime.utcnow().isoformat(),
            }

            chunks_with_metadata.append({"text": chunk, "metadata": metadata})

    return chunks_with_metadata


def list_documents(user_id: str) -> List[DocumentResponse]:
    """
    List all documents for a user.

    Args:
        user_id: ID of the user

    Returns:
        List of document response objects
    """
    documents = []

    # Get list of physical files
    for filename in os.listdir(settings.DOCUMENTS_DIRECTORY):
        if filename.endswith((".pdf", ".docx", ".txt")):
            file_path = os.path.join(settings.DOCUMENTS_DIRECTORY, filename)
            
            # Parse document ID from filename
            # New format: {document_id}_{original_filename}
            try:
                parts = filename.split("_", 1)
                if len(parts) < 2:
                    # Skip files not matching our format
                    logger.warning(f"Skipping file with invalid format: {filename}")
                    continue
                    
                document_id = parts[0]
                original_filename = parts[1]

                # Determine content type
                content_type = (
                    "application/pdf"
                    if original_filename.endswith(".pdf")
                    else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    if original_filename.endswith(".docx")
                    else "text/plain"
                )

                # In a production system, we would check if the document belongs to the user
                # Here we're just returning all documents since we don't have a database

                try:
                    # Get file modification time for created_at
                    created_at = datetime.fromtimestamp(os.path.getmtime(file_path))

                    documents.append(
                        DocumentResponse(
                            id=document_id,
                            filename=original_filename,
                            content_type=content_type,
                            size=os.path.getsize(file_path),
                            created_at=created_at,
                        )
                    )
                except Exception as e:
                    logger.error(f"Error getting document info: {str(e)}")
            except Exception as e:
                logger.error(f"Error parsing filename {filename}: {str(e)}")

    return documents


def delete_document(document_id: str, user_id: str) -> bool:
    """
    Delete a document and its vectors from the system.

    Args:
        document_id: ID of the document to delete
        user_id: ID of the user requesting deletion

    Returns:
        True if deletion was successful, False otherwise
    """
    # Check if document exists and belongs to user
    # In a production system, we would validate this against a database

    # Find and delete the document file with the pattern document_id_*
    found = False
    document_dir = settings.DOCUMENTS_DIRECTORY
    
    try:
        for filename in os.listdir(document_dir):
            # Check if file starts with document_id_
            if filename.startswith(f"{document_id}_"):
                file_path = os.path.join(document_dir, filename)
                try:
                    os.remove(file_path)
                    found = True
                    logger.info(f"Deleted document file: {file_path}")
                    break
                except Exception as e:
                    logger.error(f"Error deleting document file: {str(e)}")
                    return False
    except Exception as e:
        logger.error(f"Error listing documents directory: {str(e)}")
        return False

    if not found:
        logger.warning(f"Document not found: {document_id}")
        return False

    # Remove from vector store
    try:
        delete_document_from_vectorstore(document_id)
    except Exception as e:
        logger.error(f"Error removing document from vector store: {str(e)}")
        # We still return True since the file was deleted successfully

    return True


def get_document_stats(db: Session) -> Dict[str, Any]:
    """
    Get document statistics for the dashboard.
    
    Returns:
        Dict with stats like total count and breakdown by file type
    """
    # Get total document count
    total_count = db.query(func.count(Document.id)).scalar() or 0
    
    # Get breakdown by file type
    file_type_counts = db.query(
        Document.file_type, 
        func.count(Document.id)
    ).group_by(Document.file_type).all()
    
    # Convert to dictionary
    file_types = {file_type: count for file_type, count in file_type_counts}
    
    return {
        "total_count": total_count,
        "file_types": file_types
    }
