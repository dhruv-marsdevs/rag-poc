import os
import uuid
import shutil
from typing import List
import logging
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    File,
    UploadFile,
    BackgroundTasks,
    status,
)
from app.api import deps
from app.core.config import get_settings
from app.schemas.user import User
from app.schemas.document import DocumentResponse, WebScrapeRequest, WebScrapeResponse
from app.services.document_service import (
    process_document,
    list_documents,
    delete_document as service_delete_document,
)
from app.services.scraping_service import scrape_website
from datetime import datetime

settings = get_settings()
router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED
)
async def upload_document(
    *,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user_from_token_or_key),
):
    """
    Upload a PDF or Word document for indexing.

    The document will be processed in the background and added to the vector store.
    """
    try:
        # Validate file type
        content_type = file.content_type
        if content_type not in [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF and Word documents are supported",
            )

        # Generate unique ID 
        document_id = str(uuid.uuid4())
        
        # Get file extension from the original filename or content type
        original_filename = file.filename
        file_ext = os.path.splitext(original_filename)[1].lower()
        if not file_ext:
            # Fallback to content type if extension not in filename
            file_ext = ".pdf" if content_type == "application/pdf" else ".docx"
        
        # Create a filename using the original name but ensure uniqueness
        # by adding the UUID as a prefix
        safe_filename = f"{document_id}_{original_filename}"
        file_path = os.path.join(settings.DOCUMENTS_DIRECTORY, safe_filename)

        # Ensure directory exists
        os.makedirs(settings.DOCUMENTS_DIRECTORY, exist_ok=True)

        # Save the file
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Process the document in the background
        background_tasks.add_task(
            process_document,
            file_path=file_path,
            document_id=document_id,
            filename=original_filename,
            user_id=current_user.id,
        )

        # Return document info
        return DocumentResponse(
            id=document_id,
            filename=original_filename,
            content_type=content_type,
            size=os.path.getsize(file_path),
            created_at=None,  # Would be set if we had a database
        )
    except Exception as e:
        # Log the error
        logger.error(f"Error uploading document: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}",
        )


@router.post(
    "/scrape-website", 
    response_model=WebScrapeResponse, 
    status_code=status.HTTP_201_CREATED
)
async def scrape_website_endpoint(
    *,
    scrape_request: WebScrapeRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(deps.get_current_user_from_token_or_key),
):
    """
    Scrape a website and index its content.
    
    The website will be crawled, and its content will be processed and added to the vector store.
    """
    try:
        logger.info(f"Received request to scrape website: {scrape_request.url}")
        
        # Start scraping in the background
        background_tasks.add_task(
            _process_website_scraping,
            url=str(scrape_request.url),
            max_pages=scrape_request.max_pages,
            max_depth=scrape_request.max_depth,
            user_id=current_user.id
        )
        
        # Return immediate response while processing continues in background
        domain = str(scrape_request.url).split("//")[1].split("/")[0]
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        temporary_id = str(uuid.uuid4())
        
        return WebScrapeResponse(
            id=temporary_id,
            filename=f"web_{domain}_{timestamp}.txt",
            pages_scraped=0,  # Will be updated during processing
            time_taken=0,     # Will be updated during processing
            base_url=str(scrape_request.url),
            content_type="text/plain",
            size=0            # Will be updated during processing
        )
        
    except Exception as e:
        logger.error(f"Error initiating website scraping: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scraping website: {str(e)}",
        )


async def _process_website_scraping(
    url: str, max_pages: int, max_depth: int, user_id: str
):
    """
    Process website scraping in the background.
    
    Args:
        url: Website URL to scrape
        max_pages: Maximum number of pages to scrape
        max_depth: Maximum depth of links to follow
        user_id: ID of the user requesting the scrape
    """
    try:
        # Perform the actual scraping
        result = scrape_website(
            url=url,
            user_id=user_id,
            max_pages=max_pages,
            max_depth=max_depth
        )
        
        logger.info(f"Website scraping completed: {result}")
        
        # The document is now automatically processed and indexed in the vector store
        # This allows the content to be searched and retrieved in queries
        
    except Exception as e:
        logger.error(f"Error in background scraping task: {str(e)}", exc_info=True)


@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    current_user: User = Depends(deps.get_current_user_from_token_or_key),
):
    """
    Retrieve all documents for the current user.
    """
    documents = list_documents(user_id=current_user.id)
    return documents


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: User = Depends(deps.get_current_user_from_token_or_key),
):
    """
    Delete a document and its vectors from the system.
    """
    success = service_delete_document(document_id=document_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return None
