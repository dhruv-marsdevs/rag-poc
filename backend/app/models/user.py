from sqlalchemy import Boolean, Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from app.db.base_class import Base


class User(Base):
    """
    User model for SQLAlchemy
    """

    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="user")
