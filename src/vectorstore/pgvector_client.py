"""PostgreSQL pgvector client."""
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2 import pool as psycopg2_pool
from psycopg2.extras import execute_values
from psycopg2.extras import Json
import json
from contextlib import contextmanager
import time
from src.core.logging import logger

try:
    from pgvector.psycopg2 import register_vector
    from pgvector import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    Vector = None
    logger.warning("pgvector library not available. Install with: pip install pgvector")


class PgVectorClient:
    """Client for PostgreSQL with pgvector extension."""
    
    def __init__(self, connection_string: str, min_connections: int = 1, max_connections: int = 5):
        """
        Initialize the pgvector client with connection pooling.
        
        Args:
            connection_string: Database connection string
            min_connections: Minimum number of connections in pool
            max_connections: Maximum number of connections in pool
        """
        self.connection_string = connection_string
        self._connection_pool = None
        self._initialize_pool(min_connections, max_connections)
    
    def _initialize_pool(self, min_conn: int, max_conn: int):
        """Initialize connection pool with retry logic."""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                self._connection_pool = psycopg2_pool.ThreadedConnectionPool(
                    min_conn,
                    max_conn,
                    self.connection_string
                )
                # Test connection and register pgvector
                test_conn = self._connection_pool.getconn()
                if test_conn is None:
                    raise RuntimeError("Failed to get test connection from pool")
                if PGVECTOR_AVAILABLE:
                    register_vector(test_conn)
                self._connection_pool.putconn(test_conn)
                logger.info(f"Initialized pgvector client with connection pool ({min_conn}-{max_conn} connections)")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to initialize connection pool (attempt {attempt + 1}/{max_retries}): {str(e)}. Retrying...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"Failed to initialize connection pool after {max_retries} attempts: {str(e)}", exc_info=True)
                    self._connection_pool = None
                    raise
    
    @contextmanager
    def _get_connection(self, max_retries: int = 3):
        """Get database connection from pool (context manager) with retry logic."""
        if self._connection_pool is None:
            raise RuntimeError("Connection pool not initialized")
        
        conn = None
        last_error = None
        
        for attempt in range(max_retries):
            try:
                conn = self._connection_pool.getconn()
                if conn is None:
                    if attempt < max_retries - 1:
                        time.sleep(0.1 * (attempt + 1))
                        continue
                    raise RuntimeError("Failed to get connection from pool after retries")
                
                # Check if connection is still valid
                if conn.closed:
                    if attempt < max_retries - 1:
                        conn = None
                        time.sleep(0.1 * (attempt + 1))
                        continue
                    raise RuntimeError("Connection is closed")
                
                yield conn
                return
                
            except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
                last_error = e
                if conn:
                    try:
                        self._connection_pool.putconn(conn, close=True)
                    except:
                        pass
                    conn = None
                
                if attempt < max_retries - 1:
                    logger.warning(f"Connection error (attempt {attempt + 1}/{max_retries}): {str(e)}. Retrying...")
                    time.sleep(0.2 * (attempt + 1))
                else:
                    break
                    
            except Exception as e:
                last_error = e
                if conn:
                    try:
                        conn.rollback()
                    except:
                        pass
                raise
            finally:
                if conn:
                    try:
                        self._connection_pool.putconn(conn)
                    except Exception as e:
                        logger.warning(f"Error returning connection to pool: {str(e)}")
        
        # If we get here, all retries failed
        if last_error:
            raise last_error
        raise RuntimeError("Failed to get connection from pool after retries")
    
    def insert_vectors(self, vectors: List[Dict[str, Any]]) -> None:
        """
        Insert vectors into the database (synchronous).
        
        Args:
            vectors: List of dictionaries with 'content', 'embedding', 'metadata', and optionally 'document_id'
        """
        if not vectors:
            logger.warning("No vectors to insert")
            return
        
        logger.info(f"Inserting {len(vectors)} vectors")
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                try:
                    # Ensure pgvector is registered for this connection
                    if PGVECTOR_AVAILABLE:
                        register_vector(conn)
                    
                    # Get document_id from first vector for verification
                    first_document_id = vectors[0].get("document_id") if vectors else None
                    
                    # Prepare data for insertion
                    insert_data = []
                    original_embeddings = []  # Store original embeddings for fallback
                    for i, vector in enumerate(vectors):
                        content = vector.get("content", "")
                        embedding = vector.get("embedding", [])
                        metadata = vector.get("metadata", {})
                        document_id = vector.get("document_id")
                        
                        # Validate content
                        if not content or not content.strip():
                            logger.warning(f"Skipping vector {i} with empty content")
                            continue
                        
                        # Validate embedding
                        if not embedding or len(embedding) == 0:
                            logger.warning(f"Skipping vector {i} with empty embedding")
                            continue
                        
                        if len(embedding) != 1536:
                            logger.warning(f"Vector {i} has embedding dimension {len(embedding)}, expected 1536")
                        
                        # Prepare metadata JSON
                        if document_id and "document_id" not in metadata:
                            metadata = {**metadata, "document_id": document_id}
                        metadata_json = Json(metadata) if metadata else Json({})
                        
                        # Store original embedding for potential fallback
                        original_embeddings.append(embedding)
                        
                        # Convert embedding to proper format
                        # If pgvector is available, use Vector type
                        # Otherwise, convert to string format
                        try:
                            if PGVECTOR_AVAILABLE and Vector:
                                embedding_value = Vector(embedding)
                            else:
                                # Fallback: use string format
                                embedding_value = "[" + ",".join(map(str, embedding)) + "]"
                        except Exception as e:
                            logger.error(f"Error converting embedding for vector {i}: {str(e)}")
                            raise
                        
                        insert_data.append((
                            content,
                            embedding_value,
                            metadata_json
                        ))
                    
                    if not insert_data:
                        logger.error("No valid data to insert after validation")
                        raise ValueError("No valid vectors to insert")
                    
                    logger.info(f"Prepared {len(insert_data)} vectors for insertion (from {len(vectors)} total)")
                    
                    # Insert vectors one by one to ensure Vector type is properly handled
                    # execute_values doesn't always work correctly with custom types like Vector
                    insert_query = """
                        INSERT INTO documents (content, embedding, metadata)
                        VALUES (%s, %s, %s)
                    """
                    
                    rows_inserted = 0
                    first_error = None
                    for i, (content, embedding_value, metadata_json) in enumerate(insert_data):
                        try:
                            cursor.execute(insert_query, (content, embedding_value, metadata_json))
                            rows_inserted += 1
                        except Exception as e:
                            if first_error is None:
                                first_error = e
                            logger.error(f"Error inserting vector {i}: {str(e)}", exc_info=True)
                            
                            # If Vector type fails, try with string format as fallback
                            if PGVECTOR_AVAILABLE and Vector and isinstance(embedding_value, Vector) and i < len(original_embeddings):
                                try:
                                    # Get original embedding list
                                    original_embedding = original_embeddings[i]
                                    if isinstance(original_embedding, list):
                                        # Convert to string format
                                        embedding_str = "[" + ",".join(map(str, original_embedding)) + "]"
                                        logger.info(f"Retrying vector {i} with string format embedding")
                                        cursor.execute(insert_query, (content, embedding_str, metadata_json))
                                        rows_inserted += 1
                                        continue
                                except Exception as fallback_error:
                                    logger.error(f"Fallback insertion also failed for vector {i}: {str(fallback_error)}")
                            
                            # Continue with next vector instead of failing completely
                            continue
                    
                    if first_error and rows_inserted == 0:
                        # If all inserts failed, raise the first error
                        raise RuntimeError(f"All vector insertions failed. First error: {str(first_error)}") from first_error
                    
                    logger.info(f"Inserted {rows_inserted} out of {len(insert_data)} vectors")
                    
                    if rows_inserted == 0:
                        raise RuntimeError("Failed to insert any vectors into database")
                    
                    # Commit the transaction
                    conn.commit()
                    logger.info(f"Successfully committed {rows_inserted} vectors to database")
                    
                    # Verify insertion by counting rows (if document_id available)
                    if first_document_id:
                        cursor.execute("SELECT COUNT(*) FROM documents WHERE metadata->>'document_id' = %s", (first_document_id,))
                        count = cursor.fetchone()[0]
                        logger.info(f"Verified: {count} documents found in database for document_id: {first_document_id}")
                    else:
                        # Count all documents if no document_id
                        cursor.execute("SELECT COUNT(*) FROM documents")
                        total_count = cursor.fetchone()[0]
                        logger.info(f"Total documents in database: {total_count}")
                    
                except Exception as e:
                    logger.error(f"Error during database insertion: {str(e)}", exc_info=True)
                    try:
                        conn.rollback()
                        logger.info("Transaction rolled back")
                    except Exception as rollback_error:
                        logger.error(f"Error during rollback: {str(rollback_error)}")
                    raise
                finally:
                    cursor.close()
                    
        except Exception as e:
            logger.error(f"Error inserting vectors: {str(e)}", exc_info=True)
            raise
    
    async def insert_vectors_async(self, vectors: List[Dict[str, Any]]) -> None:
        """Insert vectors into the database (async wrapper)."""
        return self.insert_vectors(vectors)
    
    def search_vectors(self, query_vector: List[float], top_k: int = 5, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors (synchronous).
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            document_id: Optional document ID to filter by
            
        Returns:
            List of similar documents
        """
        logger.info(f"Searching for {top_k} similar vectors")
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                try:
                    # Convert query vector to proper format
                    if PGVECTOR_AVAILABLE and Vector:
                        query_vector_value = Vector(query_vector)
                    else:
                        query_vector_value = "[" + ",".join(map(str, query_vector)) + "]"
                    
                    # Build query
                    if document_id:
                        search_query = """
                            SELECT id, content, metadata, embedding <-> %s::vector AS distance
                            FROM documents
                            WHERE metadata->>'document_id' = %s
                            ORDER BY embedding <-> %s::vector
                            LIMIT %s
                        """
                        cursor.execute(search_query, (query_vector_value, document_id, query_vector_value, top_k))
                    else:
                        search_query = """
                            SELECT id, content, metadata, embedding <-> %s::vector AS distance
                            FROM documents
                            ORDER BY embedding <-> %s::vector
                            LIMIT %s
                        """
                        cursor.execute(search_query, (query_vector_value, query_vector_value, top_k))
                    
                    results = []
                    for row in cursor.fetchall():
                        results.append({
                            "id": str(row[0]),
                            "content": row[1],
                            "metadata": row[2] if isinstance(row[2], dict) else json.loads(row[2]) if row[2] else {},
                            "distance": float(row[3])
                        })
                    
                    logger.info(f"Found {len(results)} similar vectors")
                    return results
                    
                finally:
                    cursor.close()
                    
        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}", exc_info=True)
            return []
    
    async def search_vectors_async(self, query_vector: List[float], top_k: int = 5, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors (async wrapper)."""
        return self.search_vectors(query_vector, top_k, document_id)
    
    def close(self):
        """Close connection pool."""
        if self._connection_pool:
            self._connection_pool.closeall()
            logger.info("Database connection pool closed")

