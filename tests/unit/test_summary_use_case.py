import pytest
from unittest.mock import AsyncMock, Mock
from src.domain import (
    Document, 
    SummaryRequest, 
    SummaryProgress, 
    SummaryStatus,
    LLMService,
    SummaryRepository
)
from src.use_cases import SummaryUseCase


@pytest.fixture
def mock_llm_service():
    service = Mock(spec=LLMService)
    service.generate_initial_summary = AsyncMock(return_value="Initial summary")
    service.refine_summary = AsyncMock(return_value="Refined summary")
    return service


@pytest.fixture
def mock_repository():
    repo = Mock(spec=SummaryRepository)
    repo.save_progress = AsyncMock()
    repo.get_progress = AsyncMock()
    repo.save_result = AsyncMock()
    repo.get_result = AsyncMock()
    return repo


@pytest.fixture
def summary_use_case(mock_llm_service, mock_repository):
    return SummaryUseCase(mock_llm_service, mock_repository)


class TestSummaryUseCase:
    @pytest.mark.asyncio
    async def test_create_summary_single_document(self, summary_use_case, mock_llm_service, mock_repository):
        # Arrange
        documents = [Document(content="Test content")]
        request = SummaryRequest(documents=documents, request_id="test-123")
        
        # Act
        result = await summary_use_case.create_summary(request)
        
        # Assert
        assert result.request_id == "test-123"
        assert result.summary == "Initial summary"
        assert result.status == SummaryStatus.COMPLETED
        assert result.error_message is None
        
        # Verify LLM service was called correctly
        mock_llm_service.generate_initial_summary.assert_called_once_with("Test content")
        mock_llm_service.refine_summary.assert_not_called()
        
        # Verify repository interactions
        assert mock_repository.save_progress.call_count == 3  # Initial, after first doc, final
        mock_repository.save_result.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_summary_multiple_documents(self, summary_use_case, mock_llm_service, mock_repository):
        # Arrange
        documents = [
            Document(content="Content 1"),
            Document(content="Content 2"),
            Document(content="Content 3")
        ]
        request = SummaryRequest(documents=documents, request_id="test-123")
        
        # Act
        result = await summary_use_case.create_summary(request)
        
        # Assert
        assert result.request_id == "test-123"
        assert result.summary == "Refined summary"
        assert result.status == SummaryStatus.COMPLETED
        
        # Verify LLM service was called correctly
        mock_llm_service.generate_initial_summary.assert_called_once_with("Content 1")
        assert mock_llm_service.refine_summary.call_count == 2
        mock_llm_service.refine_summary.assert_any_call("Initial summary", "Content 2")
        mock_llm_service.refine_summary.assert_any_call("Refined summary", "Content 3")
    
    @pytest.mark.asyncio
    async def test_create_summary_no_documents(self, summary_use_case, mock_llm_service, mock_repository):
        # Arrange
        request = SummaryRequest(documents=[], request_id="test-123")
        
        # Act
        result = await summary_use_case.create_summary(request)
        
        # Assert
        assert result.request_id == "test-123"
        assert result.summary == ""
        assert result.status == SummaryStatus.FAILED
        assert result.error_message == "No documents provided"
        
        # Verify LLM service was not called
        mock_llm_service.generate_initial_summary.assert_not_called()
        mock_llm_service.refine_summary.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_summary_llm_error(self, summary_use_case, mock_llm_service, mock_repository):
        # Arrange
        documents = [Document(content="Test content")]
        request = SummaryRequest(documents=documents, request_id="test-123")
        mock_llm_service.generate_initial_summary.side_effect = Exception("LLM Error")
        
        # Act
        result = await summary_use_case.create_summary(request)
        
        # Assert
        assert result.request_id == "test-123"
        assert result.summary == ""
        assert result.status == SummaryStatus.FAILED
        assert "LLM Error" in result.error_message
    
    @pytest.mark.asyncio
    async def test_get_summary_status(self, summary_use_case, mock_repository):
        # Arrange
        expected_progress = SummaryProgress(
            request_id="test-123",
            current_document_index=1,
            total_documents=2,
            current_summary="Partial summary",
            status=SummaryStatus.IN_PROGRESS
        )
        mock_repository.get_progress.return_value = expected_progress
        
        # Act
        result = await summary_use_case.get_summary_status("test-123")
        
        # Assert
        assert result == expected_progress
        mock_repository.get_progress.assert_called_once_with("test-123")
    
    @pytest.mark.asyncio
    async def test_get_summary_status_not_found(self, summary_use_case, mock_repository):
        # Arrange
        mock_repository.get_progress.return_value = None
        
        # Act
        result = await summary_use_case.get_summary_status("test-123")
        
        # Assert
        assert result is None
        mock_repository.get_progress.assert_called_once_with("test-123")