"""Ingestion router."""
from fastapi import APIRouter, Depends, HTTPException
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
    """Ingest a document."""
    try:
        result = await ingestion_service.ingest(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

