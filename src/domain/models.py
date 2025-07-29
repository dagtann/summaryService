from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class SummaryStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Document:
    content: str
    title: Optional[str] = None
    metadata: Optional[dict] = None


@dataclass
class SummaryRequest:
    documents: List[Document]
    request_id: str


@dataclass
class SummaryResult:
    request_id: str
    summary: str
    status: SummaryStatus
    error_message: Optional[str] = None


@dataclass
class SummaryProgress:
    request_id: str
    current_document_index: int
    total_documents: int
    current_summary: str
    status: SummaryStatus