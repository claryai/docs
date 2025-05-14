"""
Template schemas for the DocuAgent API.

This module defines Pydantic schemas for template-related operations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class TemplateFieldColumn(BaseModel):
    """Schema for template field column."""
    
    name: str
    type: str


class TemplateField(BaseModel):
    """Schema for template field."""
    
    type: str
    required: bool
    extraction_hints: List[str]
    columns: Optional[List[TemplateFieldColumn]] = None


class TemplateBase(BaseModel):
    """Base template schema."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    document_type: str = Field(..., min_length=1, max_length=50)
    fields: Dict[str, TemplateField]


class TemplateCreate(TemplateBase):
    """Schema for creating a template."""
    
    pass


class TemplateUpdate(BaseModel):
    """Schema for updating a template."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    document_type: Optional[str] = Field(None, min_length=1, max_length=50)
    fields: Optional[Dict[str, TemplateField]] = None


class TemplateInDBBase(TemplateBase):
    """Base schema for template in database."""
    
    template_id: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic config."""
        
        orm_mode = True


class Template(TemplateInDBBase):
    """Schema for template response."""
    
    pass


class TemplateInDB(TemplateInDBBase):
    """Schema for template in database."""
    
    id: int
