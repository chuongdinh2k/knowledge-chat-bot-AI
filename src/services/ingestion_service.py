"""Document ingestion service."""
from src.api.models.ingest_request import IngestRequest, IngestResponse
from src.utils.id_gen import generate_id
from src.core.logging import logger


class IngestionService:
    """Service for ingesting documents."""
    
    def __init__(self):
        """Initialize the ingestion service."""
        pass
    
    async def ingest(self, request: IngestRequest) -> IngestResponse:
        """Ingest a document."""
        logger.info(f"Ingesting document: {request.document_id or 'new'}")
        
        # Placeholder implementation
        document_id = request.document_id or generate_id()
        
        return IngestResponse(
            document_id=document_id,
            status="success",
            message="Document ingested successfully"
        )

