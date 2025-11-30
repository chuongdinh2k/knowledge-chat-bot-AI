"""Excel document loader."""
from typing import Optional, List, Dict, Any
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
    
    def load_qa_pairs(self, file_path: str) -> Optional[List[Dict[str, Any]]]:
        """
        Load Q&A pairs from Excel file with 'question' and 'answer' columns.
        
        Expected Excel format:
        - Columns: 'question' (or 'Question', 'Q', etc.) and 'answer' (or 'Answer', 'A', etc.)
        - Each row represents a Q&A pair
        
        Args:
            file_path: Path to the Excel file
        
        Returns:
            List of dictionaries with 'question' and 'answer' keys, or None if loading fails
        """
        try:
            logger.info(f"Loading Q&A pairs from Excel file: {file_path}")
            
            # Read all sheets from the Excel file
            excel_file = pd.ExcelFile(file_path)
            all_qa_pairs = []
            
            for sheet_name in excel_file.sheet_names:
                logger.info(f"Processing sheet: {sheet_name} for Q&A pairs")
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Normalize column names (case-insensitive, handle variations)
                df.columns = df.columns.str.strip().str.lower()
                
                # Find question and answer columns (flexible matching)
                question_col = None
                answer_col = None
                
                # Try to find question column
                for col in df.columns:
                    if col in ['question', 'q', 'questions', 'query', 'queries']:
                        question_col = col
                        break
                
                # Try to find answer column
                for col in df.columns:
                    if col in ['answer', 'a', 'answers', 'response', 'responses', 'reply', 'replies']:
                        answer_col = col
                        break
                
                if question_col is None or answer_col is None:
                    logger.warning(f"Sheet '{sheet_name}' does not have required Q&A columns. "
                               f"Found columns: {list(df.columns)}. "
                               f"Looking for 'question' and 'answer' columns.")
                    continue
                
                # Extract Q&A pairs
                for idx, row in df.iterrows():
                    question = str(row[question_col]).strip() if pd.notna(row[question_col]) else ""
                    answer = str(row[answer_col]).strip() if pd.notna(row[answer_col]) else ""
                    
                    # Skip empty rows
                    if not question and not answer:
                        continue
                    
                    # Create Q&A pair
                    qa_pair = {
                        "question": question,
                        "answer": answer,
                        "sheet": sheet_name,
                        "row_index": int(idx)
                    }
                    
                    # Add any additional columns as metadata
                    additional_metadata = {}
                    for col in df.columns:
                        if col not in [question_col, answer_col] and pd.notna(row[col]):
                            additional_metadata[col] = str(row[col]).strip()
                    
                    if additional_metadata:
                        qa_pair["metadata"] = additional_metadata
                    
                    all_qa_pairs.append(qa_pair)
                
                logger.info(f"Extracted {len([p for p in all_qa_pairs if p['sheet'] == sheet_name])} Q&A pairs from sheet '{sheet_name}'")
            
            logger.info(f"Successfully loaded {len(all_qa_pairs)} Q&A pairs from Excel file: {file_path}")
            return all_qa_pairs if all_qa_pairs else None
            
        except Exception as e:
            logger.error(f"Error loading Q&A pairs from Excel file {file_path}: {str(e)}", exc_info=True)
            return None
    
    def detect_format(self, file_path: str) -> str:
        """
        Detect if Excel file contains Q&A format or regular content.
        
        Args:
            file_path: Path to the Excel file
        
        Returns:
            'qa' if Q&A format detected, 'content' otherwise
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=5)  # Read first 5 rows
                df.columns = df.columns.str.strip().str.lower()
                
                # Check for Q&A columns
                has_question = any(col in ['question', 'q', 'questions', 'query', 'queries'] for col in df.columns)
                has_answer = any(col in ['answer', 'a', 'answers', 'response', 'responses', 'reply', 'replies'] for col in df.columns)
                
                if has_question and has_answer:
                    logger.info(f"Detected Q&A format in sheet '{sheet_name}'")
                    return 'qa'
            
            return 'content'
            
        except Exception as e:
            logger.warning(f"Error detecting format: {str(e)}. Defaulting to 'content'")
            return 'content'

