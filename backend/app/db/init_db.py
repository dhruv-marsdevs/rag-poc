import logging
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import engine
from app.models.user import User

# Import all SQLAlchemy models here to ensure they are registered with the Base metadata
# This is necessary for creating tables

logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """
    Initialize the database by creating all tables and optionally adding seed data.

    Args:
        db: SQLAlchemy Session
    """
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Add a superuser if none exists
    user = db.query(User).filter(User.email == "admin@example.com").first()
    if not user:
        user = User(
            email="admin@example.com",
            full_name="Administrator",
            hashed_password=get_password_hash("admin"),  # Change in production!
            is_superuser=True,
        )
        db.add(user)
        db.commit()
        logger.info("Created initial superuser: admin@example.com")
