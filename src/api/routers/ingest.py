"""Ingestion router."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from src.api.models.ingest_request import IngestRequest, IngestResponse
from src.services.ingestion_service import IngestionService

router = APIRouter()


def get_ingestion_service() -> IngestionService:
    """Dependency for ingestion service."""
    return IngestionService()


@router.post("/", response_model=IngestResponse)
async def ingest_document(
    request: IngestRequest,
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    """Ingest a document from content string."""
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

