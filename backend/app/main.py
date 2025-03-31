import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import SessionLocal
from app.db.init_db import init_db

# Get settings
settings = get_settings()

# Setup logging
logger = setup_logging()

# Create the FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for uploading documents and querying them with RAG",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Request timer middleware
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """
    Root endpoint - redirects to API documentation
    """
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api": settings.API_V1_STR,
    }


# Create necessary directories
@app.on_event("startup")
async def startup_event():
    """
    Application startup: create necessary directories and initialize services
    """
    try:
        # Ensure data directories exist
        os.makedirs(settings.DOCUMENTS_DIRECTORY, exist_ok=True)

        # Initialize database
        logger.info("Initializing database")
        db = SessionLocal()
        init_db(db)
        db.close()

        logger.info(f"Application started: {settings.PROJECT_NAME} v{settings.VERSION}")
        logger.info(f"API prefix: {settings.API_V1_STR}")
        logger.info(f"Database: {settings.SQLITE_DATABASE_URL}")
        logger.info(f"Documents directory: {settings.DOCUMENTS_DIRECTORY}")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown: cleanup
    """
    logger.info("Application shutting down")
