"""Text chunking service."""
from typing import List, Dict, Any
from src.core.logging import logger


class Chunker:
    """Service for chunking text into smaller pieces."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize the chunker."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunk text into smaller pieces.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of dictionaries with 'text' key and optional metadata
        """
        logger.info(f"Chunking text of length {len(text)}")
        
        if not text or len(text.strip()) == 0:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # Extract chunk
            chunk_text = text[start:end]
            
            # If not the last chunk, try to break at a sentence or word boundary
            if end < len(text) and self.chunk_overlap > 0:
                # Look for sentence endings
                for i in range(len(chunk_text) - 1, max(0, len(chunk_text) - 200), -1):
                    if chunk_text[i] in '.!?\n':
                        chunk_text = chunk_text[:i+1]
                        end = start + i + 1
                        break
                # If no sentence boundary, look for word boundary
                if end == start + self.chunk_size:
                    for i in range(len(chunk_text) - 1, max(0, len(chunk_text) - 100), -1):
                        if chunk_text[i] in ' \t':
                            chunk_text = chunk_text[:i+1]
                            end = start + i + 1
                            break
            
            chunks.append({
                "text": chunk_text.strip(),
                "start": start,
                "end": min(end, len(text))
            })
            
            # Move start position with overlap
            start = end - self.chunk_overlap if self.chunk_overlap > 0 else end
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks

