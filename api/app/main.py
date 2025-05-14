"""
Main application module for the DocuAgent API.

This module initializes the FastAPI application.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.api import api_router
from app.core.config import settings
from app.db.session import engine
from app.models import Base


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("app")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: The configured FastAPI application.
    """
    # Create FastAPI app
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="API for document processing with agentic capabilities",
        version="0.1.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    # Add CORS middleware
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        # For development
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Check system health."""
        return {"status": "healthy"}

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": f"Welcome to {settings.PROJECT_NAME} API",
            "version": "0.1.0",
            "docs_url": f"{settings.API_V1_STR}/docs",
        }

    # Exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return app


# Create tables
Base.metadata.create_all(bind=engine)

# Create application
app = create_app()
