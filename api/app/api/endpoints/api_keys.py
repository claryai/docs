"""
API key endpoints for the Clary AI API.

This module provides API endpoints for API key management.
"""

from datetime import datetime, timedelta
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_api_key
from app.core.config import settings
from app.db.session import get_db
from app.models.api_key import ApiKey
from app.models.user import User
from app.schemas.api_key import ApiKeyCreate, ApiKeyResponse, ApiKeyUpdate


router = APIRouter()


@router.get("/", response_model=List[ApiKeyResponse])
async def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_api_key),
) -> Any:
    """
    List all API keys for the current user.
    
    Args:
        db: Database session.
        current_user: Current authenticated user.
        
    Returns:
        List[ApiKeyResponse]: List of API keys.
    """
    api_keys = db.query(ApiKey).filter(ApiKey.user_id == current_user.id).all()
    return api_keys


@router.post("/", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_in: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_api_key),
) -> Any:
    """
    Create a new API key.
    
    Args:
        api_key_in: API key data.
        db: Database session.
        current_user: Current authenticated user.
        
    Returns:
        ApiKeyResponse: The created API key.
    """
    # Check if user has reached the maximum number of API keys
    api_key_count = db.query(ApiKey).filter(ApiKey.user_id == current_user.id).count()
    if api_key_count >= 5:  # Limit to 5 API keys per user
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum number of API keys reached",
        )
    
    # Create expiry date if specified
    expires_at = None
    if api_key_in.valid_days:
        expires_at = datetime.utcnow() + timedelta(days=api_key_in.valid_days)
    
    # Create API key
    api_key = ApiKey(
        key=ApiKey.generate_key(),
        name=api_key_in.name,
        description=api_key_in.description,
        user_id=current_user.id,
        tier=api_key_in.tier,
        expires_at=expires_at,
    )
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    return api_key


@router.get("/{api_key_id}", response_model=ApiKeyResponse)
async def get_api_key_by_id(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_api_key),
) -> Any:
    """
    Get an API key by ID.
    
    Args:
        api_key_id: API key ID.
        db: Database session.
        current_user: Current authenticated user.
        
    Returns:
        ApiKeyResponse: The API key.
    """
    api_key = db.query(ApiKey).filter(
        ApiKey.id == api_key_id,
        ApiKey.user_id == current_user.id,
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    return api_key


@router.put("/{api_key_id}", response_model=ApiKeyResponse)
async def update_api_key(
    api_key_id: int,
    api_key_in: ApiKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_api_key),
) -> Any:
    """
    Update an API key.
    
    Args:
        api_key_id: API key ID.
        api_key_in: API key data.
        db: Database session.
        current_user: Current authenticated user.
        
    Returns:
        ApiKeyResponse: The updated API key.
    """
    api_key = db.query(ApiKey).filter(
        ApiKey.id == api_key_id,
        ApiKey.user_id == current_user.id,
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    # Update fields
    if api_key_in.name is not None:
        api_key.name = api_key_in.name
    if api_key_in.description is not None:
        api_key.description = api_key_in.description
    if api_key_in.is_active is not None:
        api_key.is_active = api_key_in.is_active
    if api_key_in.tier is not None:
        api_key.tier = api_key_in.tier
    
    # Update expiry date if specified
    if api_key_in.valid_days is not None:
        api_key.expires_at = datetime.utcnow() + timedelta(days=api_key_in.valid_days)
    
    db.commit()
    db.refresh(api_key)
    
    return api_key


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_api_key),
) -> Any:
    """
    Delete an API key.
    
    Args:
        api_key_id: API key ID.
        db: Database session.
        current_user: Current authenticated user.
    """
    api_key = db.query(ApiKey).filter(
        ApiKey.id == api_key_id,
        ApiKey.user_id == current_user.id,
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    db.delete(api_key)
    db.commit()
    
    return None


@router.post("/{api_key_id}/revoke", response_model=ApiKeyResponse)
async def revoke_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_api_key),
) -> Any:
    """
    Revoke an API key.
    
    Args:
        api_key_id: API key ID.
        db: Database session.
        current_user: Current authenticated user.
        
    Returns:
        ApiKeyResponse: The revoked API key.
    """
    api_key = db.query(ApiKey).filter(
        ApiKey.id == api_key_id,
        ApiKey.user_id == current_user.id,
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    api_key.is_active = False
    db.commit()
    db.refresh(api_key)
    
    return api_key


@router.post("/{api_key_id}/regenerate", response_model=ApiKeyResponse)
async def regenerate_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_api_key),
) -> Any:
    """
    Regenerate an API key.
    
    Args:
        api_key_id: API key ID.
        db: Database session.
        current_user: Current authenticated user.
        
    Returns:
        ApiKeyResponse: The regenerated API key.
    """
    api_key = db.query(ApiKey).filter(
        ApiKey.id == api_key_id,
        ApiKey.user_id == current_user.id,
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    api_key.key = ApiKey.generate_key()
    api_key.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(api_key)
    
    return api_key
