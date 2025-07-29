import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.infrastructure import LangChainLLMService, InMemorySummaryRepository
from src.domain import SummaryProgress, SummaryResult, SummaryStatus


class TestLangChainLLMService:
    @pytest.fixture
    def mock_llm(self):
        with patch('src.infrastructure.llm_service.init_chat_model') as mock_init:
            mock_model = Mock()
            mock_init.return_value = mock_model
            service = LangChainLLMService(api_key="test-key")
            return service, mock_model
    
    @pytest.mark.asyncio
    async def test_generate_initial_summary(self, mock_llm):
        # Arrange
        service, mock_model = mock_llm
        service.initial_summary_chain = AsyncMock(return_value="Generated summary")
        
        # Act
        result = await service.generate_initial_summary("Test content")
        
        # Assert
        assert result == "Generated summary"
        service.initial_summary_chain.ainvoke.assert_called_once_with({"context": "Test content"})
    
    @pytest.mark.asyncio
    async def test_refine_summary(self, mock_llm):
        # Arrange
        service, mock_model = mock_llm
        service.refine_summary_chain = AsyncMock(return_value="Refined summary")
        
        # Act
        result = await service.refine_summary("Existing summary", "New content")
        
        # Assert
        assert result == "Refined summary"
        service.refine_summary_chain.ainvoke.assert_called_once_with({
            "existing_answer": "Existing summary",
            "context": "New content"
        })
    
    @pytest.mark.asyncio
    async def test_generate_initial_summary_error(self, mock_llm):
        # Arrange
        service, mock_model = mock_llm
        service.initial_summary_chain = AsyncMock(side_effect=Exception("LLM Error"))
        
        # Act & Assert
        with pytest.raises(Exception, match="LLM Error"):
            await service.generate_initial_summary("Test content")
    
    @pytest.mark.asyncio
    async def test_refine_summary_error(self, mock_llm):
        # Arrange
        service, mock_model = mock_llm
        service.refine_summary_chain = AsyncMock(side_effect=Exception("LLM Error"))
        
        # Act & Assert
        with pytest.raises(Exception, match="LLM Error"):
            await service.refine_summary("Existing", "New")


class TestInMemorySummaryRepository:
    @pytest.fixture
    def repository(self):
        return InMemorySummaryRepository()
    
    @pytest.mark.asyncio
    async def test_save_and_get_progress(self, repository):
        # Arrange
        progress = SummaryProgress(
            request_id="test-123",
            current_document_index=1,
            total_documents=2,
            current_summary="Test summary",
            status=SummaryStatus.IN_PROGRESS
        )
        
        # Act
        await repository.save_progress(progress)
        result = await repository.get_progress("test-123")
        
        # Assert
        assert result == progress
        assert result.request_id == "test-123"
        assert result.current_document_index == 1
    
    @pytest.mark.asyncio
    async def test_get_progress_not_found(self, repository):
        # Act
        result = await repository.get_progress("nonexistent")
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_save_and_get_result(self, repository):
        # Arrange
        result_obj = SummaryResult(
            request_id="test-123",
            summary="Final summary",
            status=SummaryStatus.COMPLETED
        )
        
        # Act
        await repository.save_result(result_obj)
        result = await repository.get_result("test-123")
        
        # Assert
        assert result == result_obj
        assert result.request_id == "test-123"
        assert result.summary == "Final summary"
    
    @pytest.mark.asyncio
    async def test_get_result_not_found(self, repository):
        # Act
        result = await repository.get_result("nonexistent")
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_progress(self, repository):
        # Arrange
        initial_progress = SummaryProgress(
            request_id="test-123",
            current_document_index=1,
            total_documents=3,
            current_summary="Initial",
            status=SummaryStatus.IN_PROGRESS
        )
        
        updated_progress = SummaryProgress(
            request_id="test-123",
            current_document_index=2,
            total_documents=3,
            current_summary="Updated",
            status=SummaryStatus.IN_PROGRESS
        )
        
        # Act
        await repository.save_progress(initial_progress)
        await repository.save_progress(updated_progress)
        result = await repository.get_progress("test-123")
        
        # Assert
        assert result == updated_progress
        assert result.current_document_index == 2
        assert result.current_summary == "Updated"