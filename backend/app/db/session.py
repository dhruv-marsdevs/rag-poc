from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.core.config import get_settings

settings = get_settings()

# Create SQLite database directory if it doesn't exist
os.makedirs(os.path.dirname(settings.SQLITE_DATABASE_URL), exist_ok=True)

# Create SQLAlchemy engine
engine = create_engine(
    settings.SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency function that yields db sessions
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
