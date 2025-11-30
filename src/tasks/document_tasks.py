"""Celery tasks for document processing."""
import os
from typing import Dict, Any, Optional
from celery import Task
from src.celery_app import celery_app
from src.loaders.excel_loader import ExcelLoader
from src.loaders.csv_loader import CSVLoader
from src.embeddings.chunker import Chunker  # You'll need to implement this
from src.embeddings.embedder import Embedder
from src.vectorstore.pgvector_client import PgVectorClient
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
def process_document(
    self,
    file_path: str,
    document_id: str,
    file_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a document based on file type and store in database.
    
    Args:
        file_path: Path to the document file
        document_id: Unique identifier for the document
        file_type: Type of file (excel, csv, etc.)
        metadata: Optional metadata dictionary
    
    Returns:
        Dictionary with processing results
    """
    try:
        logger.info(f"Processing document: {file_path} for document {document_id}")
        
        # Step 1: Load and extract content
        file_type_lower = file_type.lower()
        loader = None
        
        if file_type_lower in ["xlsx", "xls", "excel"]:
            loader = ExcelLoader()
        elif file_type_lower == "csv":
            loader = CSVLoader()
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Detect if Excel file contains Q&A format
        is_qa_format = False
        qa_pairs = None
        
        if file_type_lower in ["xlsx", "xls", "excel"] and isinstance(loader, ExcelLoader):
            detected_format = loader.detect_format(file_path)
            if detected_format == 'qa':
                is_qa_format = True
                qa_pairs = loader.load_qa_pairs(file_path)
                if qa_pairs is None or len(qa_pairs) == 0:
                    logger.warning("Q&A format detected but no Q&A pairs extracted. Falling back to content mode.")
                    is_qa_format = False
        
        vectors = []
        
        if is_qa_format and qa_pairs:
            # Process Q&A pairs
            logger.info(f"Processing {len(qa_pairs)} Q&A pairs from {file_path}")
            
            # Step 2: Generate embeddings for Q&A pairs
            embedder = Embedder()
            
            # Create text for embedding (combine question and answer)
            qa_texts = []
            for qa_pair in qa_pairs:
                # Format: "Question: {question}\nAnswer: {answer}"
                qa_text = f"Question: {qa_pair['question']}\nAnswer: {qa_pair['answer']}"
                qa_texts.append(qa_text)
            
            embeddings = embedder.embed_batch(qa_texts)
            logger.info(f"Generated {len(embeddings)} embeddings for Q&A pairs")
            
            if len(embeddings) != len(qa_pairs):
                raise ValueError(f"Mismatch between Q&A pairs ({len(qa_pairs)}) and embeddings ({len(embeddings)})")
            
            # Step 3: Prepare vectors for database with Q&A structure
            for i, (qa_pair, embedding) in enumerate(zip(qa_pairs, embeddings)):
                qa_metadata = {
                    **(metadata or {}),
                    "qa_index": i,
                    "file_type": file_type,
                    "file_path": file_path,
                    "total_qa_pairs": len(qa_pairs),
                    "document_id": document_id,
                    "format": "qa",
                    "question": qa_pair["question"],
                    "answer": qa_pair["answer"],
                    "sheet": qa_pair.get("sheet"),
                    "row_index": qa_pair.get("row_index")
                }
                
                # Include additional metadata if present
                if "metadata" in qa_pair:
                    qa_metadata.update(qa_pair["metadata"])
                
                # Store combined Q&A text as content
                content = f"Question: {qa_pair['question']}\nAnswer: {qa_pair['answer']}"
                
                vectors.append({
                    "document_id": document_id,
                    "content": content,
                    "embedding": embedding,
                    "metadata": qa_metadata
                })
            
            logger.info(f"Prepared {len(vectors)} Q&A vectors for database storage")
            
        else:
            # Process regular content (original flow)
            content = loader.load(file_path)
            if content is None:
                raise ValueError(f"Failed to extract content from {file_path}")
            
            logger.info(f"Extracted content from {file_path} ({len(content)} characters)")
            
            # Step 2: Chunk the content
            chunker = Chunker()
            chunks = chunker.chunk(content)
            logger.info(f"Created {len(chunks)} chunks from document")
            
            if not chunks:
                raise ValueError(f"No chunks created from content in {file_path}")
            
            # Step 3: Generate embeddings (using sync method for Celery)
            embedder = Embedder()
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = embedder.embed_batch(chunk_texts)
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            if len(embeddings) != len(chunks):
                raise ValueError(f"Mismatch between chunks ({len(chunks)}) and embeddings ({len(embeddings)})")
            
            # Step 4: Prepare vectors for database
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_metadata = {
                    **(metadata or {}),
                    "chunk_index": i,
                    "file_type": file_type,
                    "file_path": file_path,
                    "total_chunks": len(chunks),
                    "document_id": document_id,
                    "format": "content"
                }
                
                vectors.append({
                    "document_id": document_id,
                    "content": chunk["text"],
                    "embedding": embedding,
                    "metadata": chunk_metadata
                })
        
        # Step 5: Store in vector database (using sync method)
        if not settings.database_url:
            raise ValueError("Database URL not configured. Set DATABASE_URL environment variable.")
        
        logger.info(f"Preparing to store {len(vectors)} vectors in database for document {document_id}")
        logger.debug(f"First vector sample - content length: {len(vectors[0]['content']) if vectors else 0}, embedding length: {len(vectors[0]['embedding']) if vectors and vectors[0].get('embedding') else 0}")
        
        # Create client with connection pooling for better performance
        vector_client = PgVectorClient(settings.database_url, min_connections=1, max_connections=3)
        try:
            vector_client.insert_vectors(vectors)
            logger.info(f"Successfully stored {len(vectors)} vectors in database for document {document_id}")
            
            # Verify insertion immediately after
            try:
                import psycopg2
                conn = psycopg2.connect(settings.database_url)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM documents WHERE metadata->>'document_id' = %s",
                    (document_id,)
                )
                count = cursor.fetchone()[0]
                logger.info(f"Verification: Found {count} documents in database for document_id: {document_id}")
                cursor.close()
                conn.close()
                
                if count == 0:
                    logger.error(f"WARNING: No documents found in database after insertion for document_id: {document_id}")
                    raise RuntimeError(f"Data insertion verification failed: expected documents but found 0")
            except Exception as verify_error:
                logger.error(f"Error during verification: {str(verify_error)}", exc_info=True)
                # Don't fail the task if verification fails, but log it
        except Exception as insert_error:
            logger.error(f"Failed to insert vectors: {str(insert_error)}", exc_info=True)
            raise
        finally:
            # Close pool when done
            vector_client.close()
        
        # Prepare result based on format
        if is_qa_format and qa_pairs:
            result = {
                "document_id": document_id,
                "status": "success",
                "file_type": file_type,
                "format": "qa",
                "qa_pairs_processed": len(qa_pairs),
                "vectors_stored": len(vectors),
                "metadata": metadata or {}
            }
        else:
            # For content format, we need to count chunks
            # This is done in the content processing section above
            chunks_count = len(vectors)  # In content mode, vectors = chunks
            result = {
                "document_id": document_id,
                "status": "success",
                "file_type": file_type,
                "format": "content",
                "chunks_created": chunks_count,
                "vectors_stored": len(vectors),
                "metadata": metadata or {}
            }
        
        logger.info(f"Successfully processed and stored document {document_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing document {file_path}: {str(e)}", exc_info=True)
        raise