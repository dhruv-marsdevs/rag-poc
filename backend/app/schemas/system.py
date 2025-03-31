from pydantic import BaseModel
from typing import Dict, Any, Optional, List


class VectorStoreStatus(BaseModel):
    """Vector store status schema."""
    
    status: str
    document_count: int
    embedding_model: str
    collection_name: Optional[str] = None


class SystemStatus(BaseModel):
    """System status schema."""
    
    status: str
    vector_store: VectorStoreStatus
    message: Optional[str] = None


class SystemStats(BaseModel):
    """System statistics schema."""
    
    total_documents: int
    queries_today: int
    active_users: int
    avg_response_time: float
    document_types: Dict[str, int]
    
    class Config:
        from_attributes = True 