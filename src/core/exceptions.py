"""Custom exceptions for the application."""


class KnowledgeBotException(Exception):
    """Base exception for the application."""
    pass


class IngestionError(KnowledgeBotException):
    """Error during document ingestion."""
    pass


class RetrievalError(KnowledgeBotException):
    """Error during document retrieval."""
    pass


class LLMError(KnowledgeBotException):
    """Error during LLM operations."""
    pass

