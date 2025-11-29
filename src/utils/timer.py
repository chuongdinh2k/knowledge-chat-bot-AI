"""Timer utility for performance measurement."""
import time
from contextlib import contextmanager
from typing import Generator
from src.core.logging import logger


@contextmanager
def timer(operation_name: str) -> Generator[None, None, None]:
    """Context manager for timing operations."""
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        logger.info(f"{operation_name} took {elapsed_time:.2f} seconds")

