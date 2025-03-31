from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.user import User
from app.schemas.system import SystemStatus, SystemStats
from app.services.vector_store_service import get_vector_store_status
from app.services.document_service import get_document_stats
from app.services.rag_service import get_query_stats
from typing import Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/status", response_model=SystemStatus)
async def get_system_status(
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Get system status information.

    Only available to superusers.
    """
    # Get vector store status
    vector_store_status = get_vector_store_status()

    # Return system status info
    return {
        "status": "operational",
        "vector_store": vector_store_status,
        "message": "If vector_store shows zero documents, you need to upload documents first.",
    }


@router.get("/stats", response_model=SystemStats)
async def get_system_statistics(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> SystemStats:
    """
    Get system statistics for the dashboard.
    
    Returns metrics like document count, query count, response times, etc.
    Available to all authenticated users.
    """
    try:
        # Get document statistics
        document_stats = get_document_stats(db)
        
        # Get query statistics
        query_stats = get_query_stats()
        
        return {
            "total_documents": document_stats["total_count"],
            "queries_today": query_stats["today_count"],
            "active_users": query_stats["active_users"],
            "avg_response_time": query_stats["avg_response_time"],
            "document_types": document_stats["file_types"]
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}", exc_info=True)
        # Return sensible defaults if there's an error
        return {
            "total_documents": 0,
            "queries_today": 0,
            "active_users": 1,
            "avg_response_time": 0.0,
            "document_types": {}
        }
