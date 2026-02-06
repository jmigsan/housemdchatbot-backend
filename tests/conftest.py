import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import create_app


@pytest.fixture(scope="session")
def mock_dependencies():
    """Mock all external dependencies to avoid actual API calls during tests."""
    with patch("app.dependencies.get_gemini_client") as mock_gemini, \
         patch("app.dependencies.get_housemd_client") as mock_housemd, \
         patch("app.dependencies.get_deepinfra_client") as mock_deepinfra, \
         patch("app.dependencies.get_pinecone_index") as mock_pinecone:
        
        mock_gemini.return_value = MagicMock()
        mock_housemd.return_value = MagicMock()
        mock_deepinfra.return_value = MagicMock()
        mock_pinecone.return_value = MagicMock()
        
        yield {
            "gemini": mock_gemini,
            "housemd": mock_housemd,
            "deepinfra": mock_deepinfra,
            "pinecone": mock_pinecone,
        }


@pytest.fixture
def app(mock_dependencies):
    """Create a fresh FastAPI app instance for each test."""
    return create_app()


@pytest.fixture
def client(app):
    """Create a TestClient for making requests to the app."""
    with TestClient(app) as test_client:
        yield test_client