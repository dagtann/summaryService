from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class SummaryStatusResponse(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentRequest(BaseModel):
    content: str = Field(..., description="Markdown content of the document")
    title: Optional[str] = Field(None, description="Optional title for the document")
    metadata: Optional[dict] = Field(None, description="Optional metadata for the document")


class SummaryCreateRequest(BaseModel):
    documents: List[DocumentRequest] = Field(..., description="List of documents to summarize", min_items=1)


class SummaryCreateResponse(BaseModel):
    request_id: str = Field(..., description="Unique identifier for the summary request")
    status: SummaryStatusResponse = Field(..., description="Current status of the summary")
    message: str = Field(..., description="Human-readable message about the request")


class SummaryStatusRequest(BaseModel):
    request_id: str = Field(..., description="Unique identifier for the summary request")


class SummaryProgressResponse(BaseModel):
    request_id: str = Field(..., description="Unique identifier for the summary request")
    status: SummaryStatusResponse = Field(..., description="Current status of the summary")
    current_document_index: int = Field(..., description="Index of currently processed document")
    total_documents: int = Field(..., description="Total number of documents to process")
    current_summary: str = Field(..., description="Current summary (markdown formatted)")


class SummaryResponse(BaseModel):
    request_id: str = Field(..., description="Unique identifier for the summary request")
    summary: str = Field(..., description="Final summary in markdown format")
    status: SummaryStatusResponse = Field(..., description="Status of the summary")
    error_message: Optional[str] = Field(None, description="Error message if status is failed")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status of the service")
    message: str = Field(..., description="Health status message")