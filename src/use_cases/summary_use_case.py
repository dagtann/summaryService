import logging
import uuid
from typing import Optional

from src.domain import (
    SummaryRequest, 
    SummaryResult, 
    SummaryProgress, 
    SummaryStatus,
    SummaryRepository,
    LLMService,
    SummaryService
)


logger = logging.getLogger(__name__)


class SummaryUseCase(SummaryService):
    def __init__(self, llm_service: LLMService, repository: SummaryRepository):
        self.llm_service = llm_service
        self.repository = repository
    
    async def create_summary(self, request: SummaryRequest) -> SummaryResult:
        logger.info(f"Starting summary creation for request {request.request_id}")
        
        try:
            if not request.documents:
                logger.warning(f"No documents provided for request {request.request_id}")
                result = SummaryResult(
                    request_id=request.request_id,
                    summary="",
                    status=SummaryStatus.FAILED,
                    error_message="No documents provided"
                )
                await self.repository.save_result(result)
                return result
            
            # Initialize progress
            progress = SummaryProgress(
                request_id=request.request_id,
                current_document_index=0,
                total_documents=len(request.documents),
                current_summary="",
                status=SummaryStatus.IN_PROGRESS
            )
            await self.repository.save_progress(progress)
            
            # Generate initial summary from first document
            logger.info(f"Generating initial summary from first document for request {request.request_id}")
            first_doc = request.documents[0]
            initial_summary = await self.llm_service.generate_initial_summary(first_doc.content)
            
            progress.current_summary = initial_summary
            progress.current_document_index = 1
            await self.repository.save_progress(progress)
            
            # Refine summary with remaining documents
            current_summary = initial_summary
            for i, doc in enumerate(request.documents[1:], start=1):
                logger.info(f"Refining summary with document {i + 1}/{len(request.documents)} for request {request.request_id}")
                
                current_summary = await self.llm_service.refine_summary(
                    current_summary, 
                    doc.content
                )
                
                progress.current_summary = current_summary
                progress.current_document_index = i + 1
                await self.repository.save_progress(progress)
            
            # Mark as completed
            progress.status = SummaryStatus.COMPLETED
            await self.repository.save_progress(progress)
            
            result = SummaryResult(
                request_id=request.request_id,
                summary=current_summary,
                status=SummaryStatus.COMPLETED
            )
            await self.repository.save_result(result)
            
            logger.info(f"Successfully completed summary for request {request.request_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating summary for request {request.request_id}: {str(e)}")
            
            # Update progress to failed
            failed_progress = SummaryProgress(
                request_id=request.request_id,
                current_document_index=0,
                total_documents=len(request.documents) if request.documents else 0,
                current_summary="",
                status=SummaryStatus.FAILED
            )
            await self.repository.save_progress(failed_progress)
            
            result = SummaryResult(
                request_id=request.request_id,
                summary="",
                status=SummaryStatus.FAILED,
                error_message=str(e)
            )
            await self.repository.save_result(result)
            return result
    
    async def get_summary_status(self, request_id: str) -> Optional[SummaryProgress]:
        logger.debug(f"Getting summary status for request {request_id}")
        return await self.repository.get_progress(request_id)