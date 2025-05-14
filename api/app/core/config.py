"""
Configuration management for the Clary AI API.

This module handles loading and validating configuration from environment variables.
"""

import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Clary AI"
    DEBUG: bool = False

    # Security settings
    SECRET_KEY: str = os.environ.get("SECRET_KEY", secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database settings
    POSTGRES_SERVER: str = os.environ.get("POSTGRES_SERVER", "db")
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "claryai")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", "claryai")
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "claryai")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Construct database URI from components."""
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # Model settings
    MODEL_PATH: str = os.environ.get("MODEL_PATH", "/app/models")
    OCR_MODEL: str = os.environ.get("OCR_MODEL", "tesseract")
    LAYOUT_MODEL: str = os.environ.get("LAYOUT_MODEL", "layoutlm")
    LLM_MODEL: str = os.environ.get("LLM_MODEL", "llama-3-8b")
    LLM_GPU_LAYERS: int = int(os.environ.get("LLM_GPU_LAYERS", "-1"))  # -1 for auto-detect
    LLM_CONTEXT_LENGTH: int = int(os.environ.get("LLM_CONTEXT_LENGTH", "4096"))
    LLM_BATCH_SIZE: int = int(os.environ.get("LLM_BATCH_SIZE", "512"))

    # Storage settings
    UPLOAD_FOLDER: str = os.environ.get("UPLOAD_FOLDER", "/app/data/uploads")
    PROCESSED_FOLDER: str = os.environ.get("PROCESSED_FOLDER", "/app/data/processed")
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16 MB

    # API key settings
    API_KEY_HEADER_NAME: str = "X-API-Key"
    API_KEY_SALT: str = os.environ.get("API_KEY_SALT", "claryai")

    # License validation settings
    LICENSE_VALIDATION_ENABLED: bool = True
    LICENSE_SERVER_URL: str = os.environ.get("LICENSE_SERVER_URL", "https://api.claryai.com/license")
    LICENSE_CHECK_INTERVAL: int = 24  # hours
    CONTAINER_ID: str = os.environ.get("CONTAINER_ID", "")

    # API key tiers and limits
    API_KEY_TIERS: Dict[str, Dict[str, Any]] = {
        "lite": {
            "daily_limit": 50,
            "monthly_limit": 1000,
            "features": ["basic_extraction"],
            "description": "Lightweight version with no pre-integrated LLM",
            "llm_integration": False,
        },
        "standard": {
            "daily_limit": 500,
            "monthly_limit": 10000,
            "features": ["basic_extraction", "advanced_extraction", "table_extraction"],
            "description": "Mid-tier version pre-integrated with Phi-4 Multimodal",
            "llm_integration": True,
            "default_llm": "phi-4-multimodal",
        },
        "professional": {
            "daily_limit": -1,  # unlimited
            "monthly_limit": -1,  # unlimited
            "features": ["basic_extraction", "advanced_extraction", "table_extraction", "custom_templates"],
            "description": "Premium version with cloud LLM connections",
            "llm_integration": True,
            "default_llm": "llama-3-8b",
            "cloud_llm_support": True,
        },
    }

    class Config:
        """Pydantic config."""

        case_sensitive = True
        env_file = ".env"


# Create global settings object
settings = Settings()
