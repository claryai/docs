"""
API key schemas for the Clary AI API.

This module defines the API key schemas for the API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ApiKeyBase(BaseModel):
    """Base API key schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tier: str = Field("lite", regex="^(lite|standard|professional)$")


class ApiKeyCreate(ApiKeyBase):
    """API key creation schema."""

    valid_days: Optional[int] = Field(None, ge=1, le=365)


class ApiKeyUpdate(BaseModel):
    """API key update schema."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    tier: Optional[str] = Field(None, regex="^(lite|standard|professional)$")
    valid_days: Optional[int] = Field(None, ge=1, le=365)


class ApiKeyResponse(ApiKeyBase):
    """API key response schema."""

    id: int
    key: str
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    usage_count: int

    class Config:
        """Pydantic config."""

        orm_mode = True
