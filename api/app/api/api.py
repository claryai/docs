"""
API router for the Clary AI API.

This module provides the main API router for the application.
"""

from fastapi import APIRouter

from app.api.endpoints import documents, models


api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
