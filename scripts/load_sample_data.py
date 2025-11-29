"""Script to load sample data."""
import asyncio
from src.services.ingestion_service import IngestionService
from src.api.models.ingest_request import IngestRequest


async def main():
    """Load sample data."""
    service = IngestionService()
    
    sample_data = [
        {"content": "This is a sample document about AI.", "document_id": "doc1"},
        {"content": "Machine learning is a subset of AI.", "document_id": "doc2"},
    ]
    
    for data in sample_data:
        request = IngestRequest(**data)
        result = await service.ingest(request)
        print(f"Ingested: {result.document_id}")


if __name__ == "__main__":
    asyncio.run(main())

