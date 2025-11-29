"""CSV document loader."""
from typing import Optional
import pandas as pd
from src.core.logging import logger


class CSVLoader:
    """Loader for CSV documents."""
    
    def __init__(self):
        """Initialize the CSV loader."""
        pass
    
    def load(self, file_path: str, encoding: str = "utf-8", delimiter: Optional[str] = None) -> Optional[str]:
        """
        Load content from CSV file.
        
        Args:
            file_path: Path to the CSV file
            encoding: File encoding (default: utf-8)
            delimiter: CSV delimiter (default: auto-detect)
        
        Returns:
            Extracted content as string, or None if loading fails
        """
        try:
            logger.info(f"Loading CSV file from {file_path}")
            
            # Try to read CSV with different encodings if needed
            encodings = [encoding, "latin-1", "iso-8859-1", "cp1252"]
            df = None
            
            for enc in encodings:
                try:
                    if delimiter:
                        df = pd.read_csv(file_path, encoding=enc, delimiter=delimiter)
                    else:
                        df = pd.read_csv(file_path, encoding=enc)
                    logger.info(f"Successfully read CSV with encoding: {enc}")
                    break
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
            
            if df is None:
                raise ValueError("Failed to read CSV file with any encoding")
            
            # Convert DataFrame to string representation
            content = df.to_string(index=False)
            
            logger.info(f"Successfully loaded CSV file: {file_path}")
            return content
            
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {str(e)}", exc_info=True)
            return None

