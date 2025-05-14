"""
Document schemas for the DocuAgent API.

This module defines Pydantic schemas for document-related operations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base document schema."""
    
    filename: str


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    
    template_id: Optional[str] = None
    options: Optional[Dict[str, Union[str, int, float, bool, List, Dict]]] = None


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""
    
    status: Optional[str] = None
    extraction_status: Optional[str] = None
    template_id: Optional[str] = None


class DocumentInDBBase(DocumentBase):
    """Base schema for document in database."""
    
    document_id: str
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    extraction_status: Optional[str] = None
    template_id: Optional[int] = None
    
    class Config:
        """Pydantic config."""
        
        orm_mode = True


class Document(DocumentInDBBase):
    """Schema for document response."""
    
    pass


class DocumentInDB(DocumentInDBBase):
    """Schema for document in database."""
    
    id: int
    file_path: str


class BoundingBox(BaseModel):
    """Schema for bounding box."""
    
    left: int
    top: int
    width: int
    height: int
    page: int
    original_page: Optional[int] = None


class ExtractedField(BaseModel):
    """Schema for extracted field."""
    
    value: str
    confidence: float
    bounding_box: Optional[BoundingBox] = None


class LineItem(BaseModel):
    """Schema for line item in an invoice."""
    
    description: str
    quantity: str
    unit_price: str
    total: str


class ExtractionResults(BaseModel):
    """Schema for extraction results."""
    
    document_id: str
    extraction_results: Dict[str, Union[ExtractedField, List[LineItem]]]
    raw_text: Optional[str] = None
    template_id: Optional[str] = None
