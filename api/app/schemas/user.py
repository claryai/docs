"""
User schemas for the DocuAgent API.

This module defines Pydantic schemas for user-related operations.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""
    
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a user."""
    
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserInDBBase(UserBase):
    """Base schema for user in database."""
    
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic config."""
        
        orm_mode = True


class User(UserInDBBase):
    """Schema for user response."""
    
    pass


class UserInDB(UserInDBBase):
    """Schema for user in database with password hash."""
    
    password_hash: str
    api_key: str
