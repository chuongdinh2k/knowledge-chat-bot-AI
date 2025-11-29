"""Ingestion service tests."""
import pytest
from src.services.ingestion_service import IngestionService
from src.api.models.ingest_request import IngestRequest


@pytest.mark.asyncio
async def test_ingest_document():
    """Test document ingestion."""
    service = IngestionService()
    request = IngestRequest(content="Test content")
    result = await service.ingest(request)
    assert result.status == "success"
    assert result.document_id is not None

