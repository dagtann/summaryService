from abc import ABC, abstractmethod
from typing import Optional

from .models import SummaryRequest, SummaryResult, SummaryProgress


class SummaryRepository(ABC):
    @abstractmethod
    async def save_progress(self, progress: SummaryProgress) -> None:
        pass
    
    @abstractmethod
    async def get_progress(self, request_id: str) -> Optional[SummaryProgress]:
        pass
    
    @abstractmethod
    async def save_result(self, result: SummaryResult) -> None:
        pass
    
    @abstractmethod
    async def get_result(self, request_id: str) -> Optional[SummaryResult]:
        pass


class LLMService(ABC):
    @abstractmethod
    async def generate_initial_summary(self, content: str) -> str:
        pass
    
    @abstractmethod
    async def refine_summary(self, existing_summary: str, new_content: str) -> str:
        pass


class SummaryService(ABC):
    @abstractmethod
    async def create_summary(self, request: SummaryRequest) -> SummaryResult:
        pass
    
    @abstractmethod
    async def get_summary_status(self, request_id: str) -> Optional[SummaryProgress]:
        pass