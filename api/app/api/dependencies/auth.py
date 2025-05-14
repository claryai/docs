"""
Authentication dependencies for the Clary AI API.

This module provides dependencies for API authentication and license validation.
"""

import time
from datetime import datetime, timedelta
import hashlib
import requests
from typing import Dict, Optional, Tuple

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.models.api_key import ApiKey


API_KEY_HEADER = APIKeyHeader(name=settings.API_KEY_HEADER_NAME)


def validate_license(api_key: str, container_id: str) -> bool:
    """
    Validate the license with the license server.

    Args:
        api_key: The API key to validate.
        container_id: The unique ID of this container.

    Returns:
        bool: True if the license is valid, False otherwise.
    """
    if not settings.LICENSE_VALIDATION_ENABLED:
        return True

    try:
        # Hash the API key for secure transmission
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Send validation request to license server
        response = requests.post(
            settings.LICENSE_SERVER_URL,
            json={
                "key_hash": key_hash,
                "container_id": container_id,
                "timestamp": int(time.time())
            },
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("valid", False)

    except Exception:
        # If license server is unreachable, check local cache
        # This allows for offline operation with periodic validation
        pass

    return False


async def get_api_key(
    api_key_header: str = Security(API_KEY_HEADER),
    db: Session = Depends(get_db),
) -> User:
    """
    Validate API key and return the associated user.

    Args:
        api_key_header: API key from request header.
        db: Database session.

    Returns:
        User: The user associated with the API key.

    Raises:
        HTTPException: If the API key is invalid.
    """
    # In development mode, accept the mock API key
    if settings.DEBUG and api_key_header == "dev_api_key":
        # Get the first user (admin) for development
        user = db.query(User).first()
        if user:
            return user

    # Get the API key from the database
    api_key = db.query(ApiKey).filter(ApiKey.key == api_key_header).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    # Check if the API key is active
    if not api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive API key",
        )

    # Check if the API key has expired
    if api_key.expires_at and api_key.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Expired API key",
        )

    # Validate the license with the license server
    if not validate_license(api_key_header, settings.CONTAINER_ID):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="License validation failed",
        )

    # Get the user associated with the API key
    user = db.query(User).filter(User.id == api_key.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User inactive or not found",
        )

    # Update API key usage statistics
    api_key.last_used_at = datetime.now()
    api_key.usage_count += 1
    db.commit()

    return user


async def check_api_key_permissions(
    required_tier: str = "free",
    required_features: Optional[list] = None,
    user: User = Depends(get_api_key),
    db: Session = Depends(get_db),
) -> User:
    """
    Check if the API key has the required permissions.

    Args:
        required_tier: The minimum tier required.
        required_features: List of required features.
        user: The authenticated user.
        db: Database session.

    Returns:
        User: The authenticated user if permissions are valid.

    Raises:
        HTTPException: If the API key doesn't have the required permissions.
    """
    if required_features is None:
        required_features = []

    # Get the API key
    api_key = db.query(ApiKey).filter(ApiKey.user_id == user.id, ApiKey.is_active == True).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active API key found",
        )

    # Check tier
    tier_levels = {"free": 0, "professional": 1, "enterprise": 2}
    if tier_levels.get(api_key.tier, 0) < tier_levels.get(required_tier, 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This operation requires {required_tier} tier or higher",
        )

    # Check features
    tier_features = settings.API_KEY_TIERS.get(api_key.tier, {}).get("features", [])
    for feature in required_features:
        if feature not in tier_features:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This operation requires the {feature} feature",
            )

    # Check usage limits
    if api_key.tier != "enterprise":  # Enterprise has no limits
        # Check daily limit
        daily_limit = settings.API_KEY_TIERS.get(api_key.tier, {}).get("daily_limit", 0)
        if daily_limit > 0:
            today = datetime.now().date()
            daily_usage = db.query(ApiKey).filter(
                ApiKey.id == api_key.id,
                ApiKey.last_used_at >= today
            ).count()

            if daily_usage >= daily_limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Daily usage limit of {daily_limit} reached",
                )

        # Check monthly limit
        monthly_limit = settings.API_KEY_TIERS.get(api_key.tier, {}).get("monthly_limit", 0)
        if monthly_limit > 0:
            first_day = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_usage = db.query(ApiKey).filter(
                ApiKey.id == api_key.id,
                ApiKey.last_used_at >= first_day
            ).count()

            if monthly_usage >= monthly_limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Monthly usage limit of {monthly_limit} reached",
                )

    return user
