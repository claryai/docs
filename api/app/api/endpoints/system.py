"""
System endpoints for the Clary AI API.

This module provides API endpoints for system operations.
"""

import os
import platform
import time
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_api_key
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.services.license_validator import license_validator


router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Check the health of the system.
    
    Returns:
        Dict[str, Any]: Health status information.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": "development" if settings.DEBUG else "production",
        "system": {
            "platform": platform.system(),
            "python_version": platform.python_version(),
        }
    }


@router.get("/license")
async def license_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Get the license status.
    
    Args:
        db: Database session.
        current_user: Current authenticated user.
        
    Returns:
        Dict[str, Any]: License status information.
    """
    # Get the API key from the request
    api_key = db.query("ApiKey").filter(
        "ApiKey.user_id" == current_user.id,
        "ApiKey.is_active" == True,
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active API key found",
        )
    
    # Get license information
    license_info = license_validator.get_license_info(api_key.key)
    
    # Get cache information
    cache_file = os.path.join(settings.MODEL_PATH, ".license_cache")
    cache_info = {}
    if os.path.exists(cache_file):
        try:
            import json
            with open(cache_file, "r") as f:
                cache_info = json.load(f)
        except Exception:
            pass
    
    return {
        "status": "active" if license_info.get("valid", False) else "inactive",
        "api_key": {
            "id": api_key.id,
            "name": api_key.name,
            "tier": api_key.tier,
            "is_active": api_key.is_active,
            "created_at": api_key.created_at.isoformat() if api_key.created_at else None,
            "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None,
            "last_used_at": api_key.last_used_at.isoformat() if api_key.last_used_at else None,
            "usage_count": api_key.usage_count,
        },
        "license": license_info,
        "cache": {
            "valid_until": datetime.fromtimestamp(cache_info.get("valid_until", 0)).isoformat() if cache_info.get("valid_until", 0) > 0 else None,
            "container_id": cache_info.get("container_id", ""),
            "tier": cache_info.get("tier", ""),
        },
        "container_id": settings.CONTAINER_ID,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/usage")
async def usage_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Get usage statistics.
    
    Args:
        db: Database session.
        current_user: Current authenticated user.
        
    Returns:
        Dict[str, Any]: Usage statistics.
    """
    # Get the API key from the request
    api_key = db.query("ApiKey").filter(
        "ApiKey.user_id" == current_user.id,
        "ApiKey.is_active" == True,
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active API key found",
        )
    
    # Get usage statistics
    today = datetime.utcnow().date()
    first_day = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    daily_usage = db.query("Document").filter(
        "Document.user_id" == current_user.id,
        "Document.created_at" >= today,
    ).count()
    
    monthly_usage = db.query("Document").filter(
        "Document.user_id" == current_user.id,
        "Document.created_at" >= first_day,
    ).count()
    
    total_usage = db.query("Document").filter(
        "Document.user_id" == current_user.id,
    ).count()
    
    # Get tier limits
    tier = api_key.tier
    daily_limit = settings.API_KEY_TIERS.get(tier, {}).get("daily_limit", 0)
    monthly_limit = settings.API_KEY_TIERS.get(tier, {}).get("monthly_limit", 0)
    
    return {
        "api_key": {
            "id": api_key.id,
            "name": api_key.name,
            "tier": tier,
        },
        "usage": {
            "daily": {
                "used": daily_usage,
                "limit": daily_limit,
                "remaining": max(0, daily_limit - daily_usage) if daily_limit > 0 else -1,
            },
            "monthly": {
                "used": monthly_usage,
                "limit": monthly_limit,
                "remaining": max(0, monthly_limit - monthly_usage) if monthly_limit > 0 else -1,
            },
            "total": total_usage,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
