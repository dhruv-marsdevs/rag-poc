import pytest
import os
import shutil
from fastapi.testclient import TestClient
from typing import Dict, Generator

from app.main import app
from app.core.config import get_settings

settings = get_settings()


@pytest.fixture
def client() -> Generator:
    """Create a test client for FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_document_path() -> str:
    """Return path to a test document."""
    # This is just a placeholder - in a real test you would create a test PDF
    return os.path.join(os.path.dirname(__file__), "data", "test_document.pdf")


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """Return authentication headers for test user."""
    # In a real test, you would get an actual token
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
def api_key_headers() -> Dict[str, str]:
    """Return API key headers for test user."""
    # In a real test, you would use a real API key
    return {"X-API-Key": "test_api_key"}


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up any test files after each test."""
    yield
    # Clean up test files here
    test_dir = os.path.join(settings.DOCUMENTS_DIRECTORY, "test")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
