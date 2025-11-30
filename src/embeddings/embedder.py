"""Text embedding service."""
from typing import List, Optional
from src.core.logging import logger
from src.core.config import settings

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. Install with: pip install openai")


class Embedder:
    """Service for generating text embeddings."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the embedder."""
        self.api_key = api_key or settings.openai_api_key
        self.client = None
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        self.model = "text-embedding-3-small"  # or text-embedding-ada-002
        self.dimension = 1536
    
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for text (synchronous).
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        logger.info("Generating embedding")
        try:
            if not OPENAI_AVAILABLE or not self.client:
                logger.warning("OpenAI not available or API key not set, returning zero vector")
                return [0.0] * self.dimension
            
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}", exc_info=True)
            # Return zero vector on error
            return [0.0] * self.dimension
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (synchronous).
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        logger.info(f"Generating embeddings for {len(texts)} texts")
        try:
            if not OPENAI_AVAILABLE or not self.client:
                logger.warning("OpenAI not available or API key not set, returning zero vectors")
                return [[0.0] * self.dimension for _ in texts]
            
            # OpenAI API supports batch requests
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}", exc_info=True)
            # Return zero vectors on error
            return [[0.0] * self.dimension for _ in texts]
    
    async def embed_async(self, text: str) -> List[float]:
        """Generate embedding for text (async version)."""
        return self.embed(text)
    
    async def embed_batch_async(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (async version)."""
        return self.embed_batch(texts)

