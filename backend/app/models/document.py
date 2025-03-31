from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from app.db.base_class import Base


class Document(Base):
    """
    Document model for SQLAlchemy
    """

    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    filename = Column(String, index=True, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    status = Column(String, default="completed")  # processing, completed, error
    user_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="documents") 