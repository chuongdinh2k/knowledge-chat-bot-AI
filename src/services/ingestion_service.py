"""Document ingestion service."""
import os
from typing import Optional, Dict, Any
from fastapi import UploadFile
from src.api.models.ingest_request import IngestRequest, IngestResponse
from src.tasks.document_tasks import process_document
from src.utils.id_gen import generate_id
from src.core.logging import logger


class IngestionService:
    """Service for ingesting documents."""
    
    def __init__(self):
        """Initialize the ingestion service."""
        self.upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def ingest_file(
        self,
        file: UploadFile,
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IngestResponse:
        """
        Ingest a file by uploading it and processing with Celery.
        
        Args:
            file: Uploaded file
            document_id: Optional document ID
            metadata: Optional metadata
        
        Returns:
            IngestResponse with task information
        """
        document_id = document_id or generate_id()
        logger.info(f"Ingesting file: {file.filename} for document {document_id}")
        
        # Determine file type from extension
        file_extension = os.path.splitext(file.filename)[1].lower().lstrip('.')
        supported_types = ["xlsx", "xls", "csv"]
        
        if file_extension not in supported_types:
            raise ValueError(f"Unsupported file type: {file_extension}. Supported types: {supported_types}")
        
        # Save uploaded file
        file_path = os.path.join(self.upload_dir, f"{document_id}_{file.filename}")
        try:
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            logger.info(f"File saved to {file_path}")
            
            # Submit task to Celery
            task = process_document.delay(
                file_path=file_path,
                document_id=document_id,
                file_type=file_extension,
                metadata=metadata
            )
            
            logger.info(f"Task {task.id} submitted for document {document_id}")
            
            return IngestResponse(
                document_id=document_id,
                status="processing",
                message=f"File uploaded and processing started. Task ID: {task.id}",
                task_id=task.id
            )
            
        except Exception as e:
            logger.error(f"Error ingesting file: {str(e)}", exc_info=True)
            # Clean up file if it was created
            if os.path.exists(file_path):
                os.remove(file_path)
            raise
    
    async def ingest(self, request: IngestRequest) -> IngestResponse:
        """
        Ingest a document from content string.
        
        Args:
            request: IngestRequest with content
        
        Returns:
            IngestResponse
        """
        logger.info(f"Ingesting document: {request.document_id or 'new'}")
        
        # Placeholder implementation for text content
        document_id = request.document_id or generate_id()
        
        return IngestResponse(
            document_id=document_id,
            status="success",
            message="Document ingested successfully"
        )

