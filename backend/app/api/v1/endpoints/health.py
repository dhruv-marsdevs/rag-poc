from fastapi import APIRouter, Depends
from app.services.vector_store_service import get_vector_store_status
from app.core.config import get_settings
import os

settings = get_settings()
router = APIRouter()


@router.get("/")
async def health_check():
    """
    Health check endpoint to verify the application is running properly.
    """
    vector_store_status = get_vector_store_status()

    # Check if documents directory exists
    documents_dir_exists = os.path.isdir(settings.DOCUMENTS_DIRECTORY)

    return {
        "status": "ok",
        "api_version": settings.VERSION,
        "vector_store": vector_store_status,
        "documents_directory": {
            "path": settings.DOCUMENTS_DIRECTORY,
            "exists": documents_dir_exists,
        },
    }
