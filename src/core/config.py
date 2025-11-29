"""Configuration management for the application."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    api_title: str = "Knowledge Chat Bot API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # Database Settings
    database_url: Optional[str] = None
    
    # LLM Settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    
    # Vector Store Settings
    vector_dimension: int = 1536
    
    # Redis Settings
    redis_url: str = "redis://localhost:6379/0"
    
    # Celery Settings
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()

