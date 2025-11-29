"""API endpoint tests."""
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


def test_root(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "version" in response.json()


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

