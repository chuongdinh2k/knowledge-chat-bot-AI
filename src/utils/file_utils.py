"""File utility functions."""
import os
from typing import Optional
from src.core.logging import logger


def get_file_extension(file_path: str) -> str:
    """Get file extension from file path."""
    return os.path.splitext(file_path)[1].lower()


def validate_file_path(file_path: str) -> bool:
    """Validate if file path exists."""
    return os.path.exists(file_path)


def get_file_size(file_path: str) -> Optional[int]:
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        logger.error(f"Could not get file size for {file_path}")
        return None

