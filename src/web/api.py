import logging
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware

from src.domain import Document, SummaryRequest, SummaryService
from src.use_cases import SummaryUseCase
from src.infrastructure import LangChainLLMService, InMemorySummaryRepository
from .models import (
    SummaryCreateRequest,
    SummaryCreateResponse,
    SummaryProgressResponse,
    SummaryResponse,
    SummaryStatusResponse,
    HealthResponse
)


logger = logging.getLogger(__name__)

# Global dependency instances
llm_service: Optional[LangChainLLMService] = None
repository: Optional[InMemorySummaryRepository] = None
summary_service: Optional[SummaryUseCase] = None


def get_summary_service() -> SummaryService:
    global summary_service
    if summary_service is None:
        raise HTTPException(status_code=500, detail="Summary service not initialized")
    return summary_service


def create_app(anthropic_api_key: Optional[str] = None) -> FastAPI:
    global llm_service, repository, summary_service
    
    app = FastAPI(
        title="Document Summary Service",
        description="A microservice for creating iterative document summaries using LangChain",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize services
    llm_service = LangChainLLMService(api_key=anthropic_api_key)
    repository = InMemorySummaryRepository()
    summary_service = SummaryUseCase(llm_service, repository)
    
    logger.info("FastAPI application initialized with all services")
    
    return app


app = create_app()


async def process_summary_async(request: SummaryRequest, service: SummaryService):
    """Background task to process summary asynchronously"""
    logger.info(f"Starting background processing for request {request.request_id}")
    try:
        await service.create_summary(request)
        logger.info(f"Completed background processing for request {request.request_id}")
    except Exception as e:
        logger.error(f"Error in background processing for request {request.request_id}: {str(e)}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", message="Service is running")


@app.post("/summaries", response_model=SummaryCreateResponse)
async def create_summary(
    request: SummaryCreateRequest,
    background_tasks: BackgroundTasks,
    service: SummaryService = Depends(get_summary_service)
):
    """Create a new summary request"""
    logger.info(f"Received summary creation request with {len(request.documents)} documents")
    
    try:
        request_id = str(uuid.uuid4())
        
        # Convert web models to domain models
        documents = [
            Document(
                content=doc.content,
                title=doc.title,
                metadata=doc.metadata
            )
            for doc in request.documents
        ]
        
        summary_request = SummaryRequest(
            request_id=request_id,
            documents=documents
        )
        
        # Start background processing
        background_tasks.add_task(process_summary_async, summary_request, service)
        
        logger.info(f"Started background processing for request {request_id}")
        
        return SummaryCreateResponse(
            request_id=request_id,
            status=SummaryStatusResponse.PENDING,
            message="Summary request created and processing started"
        )
        
    except Exception as e:
        logger.error(f"Error creating summary request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create summary request: {str(e)}")


@app.get("/summaries/{request_id}/status", response_model=SummaryProgressResponse)
async def get_summary_status(
    request_id: str,
    service: SummaryService = Depends(get_summary_service)
):
    """Get the current status of a summary request"""
    logger.debug(f"Getting status for request {request_id}")
    
    try:
        progress = await service.get_summary_status(request_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail="Summary request not found")
        
        return SummaryProgressResponse(
            request_id=progress.request_id,
            status=SummaryStatusResponse(progress.status.value),
            current_document_index=progress.current_document_index,
            total_documents=progress.total_documents,
            current_summary=progress.current_summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summary status for request {request_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary status: {str(e)}")


@app.get("/summaries/{request_id}", response_model=SummaryResponse)
async def get_summary(
    request_id: str,
    service: SummaryService = Depends(get_summary_service)
):
    """Get the final summary result"""
    logger.debug(f"Getting summary result for request {request_id}")
    
    try:
        # First check if we have a completed result
        global repository
        if repository:
            result = await repository.get_result(request_id)
            if result:
                return SummaryResponse(
                    request_id=result.request_id,
                    summary=result.summary,
                    status=SummaryStatusResponse(result.status.value),
                    error_message=result.error_message
                )
        
        # If no result, check progress
        progress = await service.get_summary_status(request_id)
        if not progress:
            raise HTTPException(status_code=404, detail="Summary request not found")
        
        # Return current state based on progress
        return SummaryResponse(
            request_id=progress.request_id,
            summary=progress.current_summary,
            status=SummaryStatusResponse(progress.status.value),
            error_message=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summary for request {request_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")