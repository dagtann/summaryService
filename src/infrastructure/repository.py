import logging
from typing import Dict, Optional

from src.domain import SummaryProgress, SummaryResult, SummaryRepository


logger = logging.getLogger(__name__)


class InMemorySummaryRepository(SummaryRepository):
    """In-memory implementation of SummaryRepository for development/testing"""
    
    def __init__(self):
        self._progress: Dict[str, SummaryProgress] = {}
        self._results: Dict[str, SummaryResult] = {}
        logger.info("Initialized in-memory summary repository")
    
    async def save_progress(self, progress: SummaryProgress) -> None:
        logger.debug(f"Saving progress for request {progress.request_id}")
        self._progress[progress.request_id] = progress
    
    async def get_progress(self, request_id: str) -> Optional[SummaryProgress]:
        logger.debug(f"Getting progress for request {request_id}")
        return self._progress.get(request_id)
    
    async def save_result(self, result: SummaryResult) -> None:
        logger.debug(f"Saving result for request {result.request_id}")
        self._results[result.request_id] = result
    
    async def get_result(self, request_id: str) -> Optional[SummaryResult]:
        logger.debug(f"Getting result for request {request_id}")
        return self._results.get(request_id)