import pytest
from src.domain.models import Document, SummaryRequest, SummaryResult, SummaryProgress, SummaryStatus


class TestDocument:
    def test_document_creation(self):
        doc = Document(content="Test content")
        assert doc.content == "Test content"
        assert doc.title is None
        assert doc.metadata is None
    
    def test_document_with_optional_fields(self):
        metadata = {"author": "test"}
        doc = Document(
            content="Test content",
            title="Test Title",
            metadata=metadata
        )
        assert doc.content == "Test content"
        assert doc.title == "Test Title"
        assert doc.metadata == metadata


class TestSummaryRequest:
    def test_summary_request_creation(self):
        docs = [Document(content="Doc 1"), Document(content="Doc 2")]
        request = SummaryRequest(documents=docs, request_id="test-123")
        
        assert request.request_id == "test-123"
        assert len(request.documents) == 2
        assert request.documents[0].content == "Doc 1"


class TestSummaryResult:
    def test_summary_result_success(self):
        result = SummaryResult(
            request_id="test-123",
            summary="Test summary",
            status=SummaryStatus.COMPLETED
        )
        
        assert result.request_id == "test-123"
        assert result.summary == "Test summary"
        assert result.status == SummaryStatus.COMPLETED
        assert result.error_message is None
    
    def test_summary_result_failure(self):
        result = SummaryResult(
            request_id="test-123",
            summary="",
            status=SummaryStatus.FAILED,
            error_message="Test error"
        )
        
        assert result.request_id == "test-123"
        assert result.summary == ""
        assert result.status == SummaryStatus.FAILED
        assert result.error_message == "Test error"


class TestSummaryProgress:
    def test_summary_progress_creation(self):
        progress = SummaryProgress(
            request_id="test-123",
            current_document_index=1,
            total_documents=3,
            current_summary="Partial summary",
            status=SummaryStatus.IN_PROGRESS
        )
        
        assert progress.request_id == "test-123"
        assert progress.current_document_index == 1
        assert progress.total_documents == 3
        assert progress.current_summary == "Partial summary"
        assert progress.status == SummaryStatus.IN_PROGRESS


class TestSummaryStatus:
    def test_summary_status_values(self):
        assert SummaryStatus.PENDING.value == "pending"
        assert SummaryStatus.IN_PROGRESS.value == "in_progress"
        assert SummaryStatus.COMPLETED.value == "completed"
        assert SummaryStatus.FAILED.value == "failed"