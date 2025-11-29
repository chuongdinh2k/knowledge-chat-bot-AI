"""Excel document loader."""
from typing import Optional
import pandas as pd
from src.core.logging import logger


class ExcelLoader:
    """Loader for Excel documents (.xlsx, .xls)."""
    
    def __init__(self):
        """Initialize the Excel loader."""
        pass
    
    def load(self, file_path: str) -> Optional[str]:
        """
        Load content from Excel file.
        
        Args:
            file_path: Path to the Excel file
        
        Returns:
            Extracted content as string, or None if loading fails
        """
        try:
            logger.info(f"Loading Excel file from {file_path}")
            
            # Read all sheets from the Excel file
            excel_file = pd.ExcelFile(file_path)
            all_sheets_content = []
            
            for sheet_name in excel_file.sheet_names:
                logger.info(f"Processing sheet: {sheet_name}")
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Convert DataFrame to string representation
                sheet_content = f"\n--- Sheet: {sheet_name} ---\n"
                sheet_content += df.to_string(index=False)
                all_sheets_content.append(sheet_content)
            
            # Combine all sheets
            content = "\n".join(all_sheets_content)
            
            logger.info(f"Successfully loaded Excel file: {file_path}")
            return content
            
        except Exception as e:
            logger.error(f"Error loading Excel file {file_path}: {str(e)}", exc_info=True)
            return None

