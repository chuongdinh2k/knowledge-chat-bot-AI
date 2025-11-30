"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.config import settings
from src.core.logging import setup_logging, logger
from src.api.routers import health
from src.api.routers.v1 import ingest, query
from src.vectorstore.db_init import init_database, check_database_connection

# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting application...")
    
    # Initialize database on startup
    if settings.database_url:
        logger.info("Checking database connection...")
        if check_database_connection():
            logger.info("Database connection successful")
            if init_database():
                logger.info("Database initialized successfully")
            else:
                logger.warning("Database initialization failed, but continuing...")
        else:
            logger.error("Cannot connect to database. Please check DATABASE_URL.")
    else:
        logger.warning("DATABASE_URL not set. Database features will not work.")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.debug,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(ingest.router)  # Router already has prefix /api/v1/ingest
app.include_router(query.router)  # Router already has prefix /api/v1/query


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Knowledge Chat Bot API", "version": settings.api_version}