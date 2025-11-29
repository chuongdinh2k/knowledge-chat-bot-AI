"""Retrieval service tests."""
import pytest
from src.services.retrieval_service import RetrievalService


@pytest.mark.asyncio
async def test_retrieve_documents():
    """Test document retrieval."""
    service = RetrievalService()
    results = await service.retrieve("test query", top_k=5)
    assert isinstance(results, list)

