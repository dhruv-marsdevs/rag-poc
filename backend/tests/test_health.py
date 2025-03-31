import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import get_settings

settings = get_settings()
client = TestClient(app)


def test_health_endpoint():
    """Test the health endpoint returns 200 and correct data structure."""
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "api_version" in data
    assert "vector_store" in data


def test_root_endpoint():
    """Test the root endpoint returns 200 and basic app info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert data["app"] == settings.PROJECT_NAME
    assert "version" in data
    assert data["version"] == settings.VERSION
