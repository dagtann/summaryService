import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from src.web import create_app
from src.domain import SummaryStatus


@pytest.fixture
def mock_llm_service():
    with patch('src.web.api.LangChainLLMService') as mock:
        service = Mock()
        service.generate_initial_summary = AsyncMock(return_value="Test summary")
        service.refine_summary = AsyncMock(return_value="Refined summary")
        mock.return_value = service
        return service


@pytest.fixture
def mock_repository():
    with patch('src.web.api.InMemorySummaryRepository') as mock:
        repo = Mock()
        repo.save_progress = AsyncMock()
        repo.get_progress = AsyncMock()
        repo.save_result = AsyncMock()
        repo.get_result = AsyncMock()
        mock.return_value = repo
        return repo


@pytest.fixture
def client(mock_llm_service, mock_repository):
    app = create_app(anthropic_api_key="test-key")
    return TestClient(app)


class TestAPI:
    def test_health_check(self, client):
        # Act
        response = client.get("/health")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data
    
    def test_create_summary(self, client):
        # Arrange
        request_data = {
            "documents": [
                {
                    "content": "# Test Document\n\nThis is a test document.",
                    "title": "Test"
                }
            ]
        }
        
        # Act
        response = client.post("/summaries", json=request_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert data["status"] == "pending"
        assert "message" in data
    
    def test_create_summary_empty_documents(self, client):
        # Arrange
        request_data = {"documents": []}
        
        # Act
        response = client.post("/summaries", json=request_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_get_summary_status_not_found(self, client, mock_repository):
        # Arrange
        mock_repository.get_progress = AsyncMock(return_value=None)
        
        # Act
        response = client.get("/summaries/nonexistent/status")
        
        # Assert
        assert response.status_code == 404
    
    def test_get_summary_not_found(self, client, mock_repository):
        # Arrange
        mock_repository.get_result = AsyncMock(return_value=None)
        mock_repository.get_progress = AsyncMock(return_value=None)
        
        # Act
        response = client.get("/summaries/nonexistent")
        
        # Assert
        assert response.status_code == 404
    
    def test_create_summary_invalid_json(self, client):
        # Act
        response = client.post(
            "/summaries",
            json={"invalid": "data"}
        )
        
        # Assert
        assert response.status_code == 422
    
    def test_cors_headers(self, client):
        # Act
        response = client.options("/summaries")
        
        # Assert
        assert "access-control-allow-origin" in response.headers