from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime


class DocumentBase(BaseModel):
    """Base document schema."""

    filename: str
    content_type: str


class DocumentCreate(DocumentBase):
    """Document creation schema."""

    pass


class DocumentResponse(DocumentBase):
    """Document response schema."""

    id: str
    size: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SourceDocument(BaseModel):
    """Source document schema for query responses."""

    page: Optional[int] = None
    document: str
    text: str


class QueryRequest(BaseModel):
    """Query request schema."""

    query: str
    top_k: int = Field(default=3, ge=1, le=10)


class QueryResponse(BaseModel):
    """Query response schema."""

    answer: str
    sources: List[SourceDocument]


class TokenPayload(BaseModel):
    """Token payload schema."""

    sub: Optional[str] = None
    exp: Optional[int] = None


class Token(BaseModel):
    """Token schema."""

    access_token: str
    token_type: str


class WebScrapeRequest(BaseModel):
    """Website scraping request schema."""
    
    url: HttpUrl = Field(..., description="The URL to scrape")
    max_pages: int = Field(50, ge=1, le=100, description="Maximum number of pages to scrape")
    max_depth: int = Field(3, ge=1, le=5, description="Maximum depth of links to follow")


class WebScrapeResponse(BaseModel):
    """Website scraping response schema."""
    
    id: str
    filename: str
    pages_scraped: int
    time_taken: Optional[float] = None
    base_url: str
    content_type: str
    size: int
