"""Database initialization utilities."""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from src.core.logging import logger
from src.core.config import settings
import os


def init_database(connection_string: str = None) -> bool:
    """
    Initialize the database by creating tables and extensions.
    
    Args:
        connection_string: Database connection string. If None, uses settings.database_url
        
    Returns:
        True if successful, False otherwise
    """
    if connection_string is None:
        connection_string = settings.database_url
    
    if not connection_string:
        logger.error("Database URL not configured. Cannot initialize database.")
        return False
    
    conn = None
    try:
        logger.info("Initializing database...")
        conn = psycopg2.connect(connection_string)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Enable pgvector extension
        logger.info("Enabling pgvector extension...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Create documents table
        logger.info("Creating documents table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                content TEXT NOT NULL,
                metadata JSONB,
                embedding vector(1536),
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # Create index if it doesn't exist
        logger.info("Creating embedding index...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS documents_embedding_idx 
            ON documents 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """)
        
        # Verify table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'documents'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            logger.info("Database initialized successfully")
            cursor.close()
            return True
        else:
            logger.error("Failed to create documents table")
            cursor.close()
            return False
            
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection error: {str(e)}")
        logger.error("Please check your DATABASE_URL and ensure PostgreSQL is running")
        return False
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        return False
    finally:
        if conn and not conn.closed:
            conn.close()


def check_database_connection(connection_string: str = None) -> bool:
    """
    Check if database connection is available.
    
    Args:
        connection_string: Database connection string. If None, uses settings.database_url
        
    Returns:
        True if connection is available, False otherwise
    """
    if connection_string is None:
        connection_string = settings.database_url
    
    if not connection_string:
        return False
    
    try:
        conn = psycopg2.connect(connection_string)
        conn.close()
        return True
    except Exception:
        return False

