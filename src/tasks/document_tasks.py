"""Celery tasks for document processing."""
import os
from typing import Dict, Any, Optional
from celery import Task
from src.celery_app import celery_app
from src.loaders.excel_loader import ExcelLoader
from src.loaders.csv_loader import CSVLoader
from src.core.logging import logger
from src.core.config import settings


class DocumentProcessingTask(Task):
    """Base task class for document processing."""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        logger.error(f"Task {task_id} failed: {exc}", exc_info=einfo)
        super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success."""
        logger.info(f"Task {task_id} completed successfully")


@celery_app.task(bind=True, base=DocumentProcessingTask)
def process_excel_file(
    self,
    file_path: str,
    document_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process an Excel file and extract content.
    
    Args:
        file_path: Path to the Excel file
        document_id: Unique identifier for the document
        metadata: Optional metadata dictionary
    
    Returns:
        Dictionary with processing results
    """
    try:
        logger.info(f"Processing Excel file: {file_path} for document {document_id}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        loader = ExcelLoader()
        content = loader.load(file_path)
        
        if content is None:
            raise ValueError(f"Failed to extract content from {file_path}")
        
        result = {
            "document_id": document_id,
            "status": "success",
            "content": content,
            "metadata": metadata or {},
            "file_type": "excel"
        }
        
        logger.info(f"Successfully processed Excel file: {file_path}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing Excel file {file_path}: {str(e)}", exc_info=True)
        raise


@celery_app.task(bind=True, base=DocumentProcessingTask)
def process_csv_file(
    self,
    file_path: str,
    document_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a CSV file and extract content.
    
    Args:
        file_path: Path to the CSV file
        document_id: Unique identifier for the document
        metadata: Optional metadata dictionary
    
    Returns:
        Dictionary with processing results
    """
    try:
        logger.info(f"Processing CSV file: {file_path} for document {document_id}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        loader = CSVLoader()
        content = loader.load(file_path)
        
        if content is None:
            raise ValueError(f"Failed to extract content from {file_path}")
        
        result = {
            "document_id": document_id,
            "status": "success",
            "content": content,
            "metadata": metadata or {},
            "file_type": "csv"
        }
        
        logger.info(f"Successfully processed CSV file: {file_path}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing CSV file {file_path}: {str(e)}", exc_info=True)
        raise


@celery_app.task(bind=True, base=DocumentProcessingTask)
def process_document(
    self,
    file_path: str,
    document_id: str,
    file_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a document based on file type.
    
    Args:
        file_path: Path to the document file
        document_id: Unique identifier for the document
        file_type: Type of file (excel, csv, etc.)
        metadata: Optional metadata dictionary
    
    Returns:
        Dictionary with processing results
    """
    file_type_lower = file_type.lower()
    
    if file_type_lower in ["xlsx", "xls", "excel"]:
        return process_excel_file(file_path, document_id, metadata)
    elif file_type_lower == "csv":
        return process_csv_file(file_path, document_id, metadata)
    else:
        raise ValueError(f"Unsupported file type: {file_type}. Supported types: xlsx, xls, csv")

