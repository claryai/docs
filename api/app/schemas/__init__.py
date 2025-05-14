"""
Schemas package for the DocuAgent API.

This package contains Pydantic schemas for API validation.
"""

from app.schemas.user import User, UserCreate, UserInDB, UserUpdate
from app.schemas.document import (
    Document, DocumentCreate, DocumentInDB, DocumentUpdate,
    ExtractionResults, BoundingBox, ExtractedField, LineItem
)
from app.schemas.template import (
    Template, TemplateCreate, TemplateInDB, TemplateUpdate,
    TemplateField, TemplateFieldColumn
)

__all__ = [
    "User", "UserCreate", "UserInDB", "UserUpdate",
    "Document", "DocumentCreate", "DocumentInDB", "DocumentUpdate",
    "ExtractionResults", "BoundingBox", "ExtractedField", "LineItem",
    "Template", "TemplateCreate", "TemplateInDB", "TemplateUpdate",
    "TemplateField", "TemplateFieldColumn"
]
