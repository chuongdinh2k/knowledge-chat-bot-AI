"""Ingestion router for API v1."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from src.api.models.ingest_request import IngestRequest, IngestResponse
from src.services.ingestion_service import IngestionService
from src.core.config import settings
from src.celery_app import celery_app
from celery.result import AsyncResult

router = APIRouter(
    prefix="/api/v1/ingest",
    tags=["ingestion", "v1"]
)

# API Version constant
API_VERSION = "v1"


def get_ingestion_service() -> IngestionService:
    """Dependency for ingestion service."""
    return IngestionService()


@router.post("/", response_model=IngestResponse)
async def ingest_document(
    request: IngestRequest,
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    """
    Ingest a document from content string.
    
    **API Version:** v1
    """
    try:
        result = await ingestion_service.ingest(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    document_id: Optional[str] = Form(None),
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    """
    Ingest a file (Excel or CSV) for processing.
    
    The file will be processed asynchronously using Celery.
    
    **API Version:** v1
    
    **Supported file types:**
    - Excel: `.xlsx`, `.xls`
    - CSV: `.csv`
    """
    try:
        result = await ingestion_service.ingest_file(
            file=file,
            document_id=document_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/version")
async def get_version():
    """
    Get the API version information for ingestion endpoints.
    
    **API Version:** v1
    """
    return {
        "api_version": settings.api_version,
        "endpoint_version": API_VERSION,
        "endpoints": {
            "ingest_document": "/api/v1/ingest/",
            "ingest_file": "/api/v1/ingest/file",
            "version": "/api/v1/ingest/version"
        }
    }

@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status of a processing task.
    
    **API Version:** v1
    
    **Task Status Values:**
    - `PENDING`: Task is waiting to be processed
    - `STARTED`: Task has been started by a worker
    - `SUCCESS`: Task completed successfully
    - `FAILURE`: Task failed with an error
    - `RETRY`: Task is being retried
    - `REVOKED`: Task was cancelled
    
    **Response includes:**
    - `status`: Current task status
    - `result`: Task result (if completed)
    - `error`: Error message (if failed)
    - `progress`: Progress information (if available)
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        response = {
            "task_id": task_id,
            "status": task_result.status,
        }
        
        if task_result.status == "SUCCESS":
            response["result"] = task_result.result
            response["message"] = "Task completed successfully"
        elif task_result.status == "FAILURE":
            response["error"] = str(task_result.info)
            response["message"] = "Task failed"
        elif task_result.status == "PENDING":
            response["message"] = "Task is waiting to be processed"
        elif task_result.status == "STARTED":
            response["message"] = "Task is currently being processed"
        else:
            response["message"] = f"Task status: {task_result.status}"
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking task status: {str(e)}")

