import os
import logging
from typing import List, Dict, Any
import pypdf
import docx
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.utils.vector_store import get_vector_store, add_documents_to_vectorstore

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_document(file_path: str, document_id: str, filename: str):
    """
    Process a document, extract text, split into chunks, and add to vector store

    Args:
        file_path: Path to the document file
        document_id: Unique ID of the document
        filename: Original filename of the document
    """
    logger.info(f"Processing document: {filename} (ID: {document_id})")

    # Extract text based on file type
    if file_path.endswith(".pdf"):
        text_chunks = process_pdf(file_path, document_id, filename)
    elif file_path.endswith(".docx"):
        text_chunks = process_docx(file_path, document_id, filename)
    else:
        logger.error(f"Unsupported file type: {file_path}")
        return

    # Add the chunks to the vector store
    logger.info(
        f"Adding {len(text_chunks)} chunks to vector store for document {document_id}"
    )
    add_documents_to_vectorstore(text_chunks)
    logger.info(f"Document {document_id} processed successfully")


def process_pdf(
    file_path: str, document_id: str, filename: str
) -> List[Dict[str, Any]]:
    """
    Process a PDF file, extract text, and create chunks with metadata

    Args:
        file_path: Path to the PDF file
        document_id: Unique ID of the document
        filename: Original filename of the document

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
        return create_chunks_with_metadata(text_by_page, document_id, filename)

    except Exception as e:
        logger.error(f"Error processing PDF {file_path}: {e}")
        return []


def process_docx(
    file_path: str, document_id: str, filename: str
) -> List[Dict[str, Any]]:
    """
    Process a DOCX file, extract text, and create chunks with metadata

    Args:
        file_path: Path to the DOCX file
        document_id: Unique ID of the document
        filename: Original filename of the document

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
            [(None, combined_text)], document_id, filename
        )

    except Exception as e:
        logger.error(f"Error processing DOCX {file_path}: {e}")
        return []


def create_chunks_with_metadata(
    text_by_page: List[tuple], document_id: str, filename: str
) -> List[Dict[str, Any]]:
    """
    Split text into chunks and add metadata

    Args:
        text_by_page: List of tuples (page_number, text)
        document_id: Unique ID of the document
        filename: Original filename of the document

    Returns:
        List of dictionaries with text chunks and metadata
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    chunks_with_metadata = []

    for page_num, text in text_by_page:
        chunks = text_splitter.split_text(text)

        for chunk in chunks:
            metadata = {
                "document_id": document_id,
                "document": filename,
                "page": page_num,
                "text": chunk,
                "source": f"{filename} {'(page ' + str(page_num) + ')' if page_num else ''}",
            }

            chunks_with_metadata.append({"text": chunk, "metadata": metadata})

    return chunks_with_metadata
