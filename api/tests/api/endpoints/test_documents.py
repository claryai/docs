"""
Tests for the documents API endpoints.

This module contains tests for the documents API endpoints.
"""

import asyncio
import datetime
import json
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.endpoints.documents import router
from app.models.document import Document
from app.models.user import User


@pytest.fixture
def app():
    """Create a FastAPI app for testing."""
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/documents")
    return app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def mock_user():
    """Create a mock user."""
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    return user


@pytest.fixture
def mock_document():
    """Create a mock document."""
    document = MagicMock(spec=Document)
    document.id = 1
    document.document_id = "test_document"
    document.user_id = 1
    document.filename = "test_document.pdf"
    document.file_path = "/tmp/test_document.pdf"
    document.status = "pending"
    document.extraction_status = None
    document.created_at = datetime.datetime.now(datetime.timezone.utc)
    document.updated_at = datetime.datetime.now(datetime.timezone.utc)
    document.completed_at = None
    document.template_id = None
    document.job_id = None
    return document


def test_get_documents(client, mock_db_session, mock_user, mock_document):
    """Test getting documents."""
    # Set up mocks
    mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_document]
    
    # Mock dependencies
    with patch("app.api.endpoints.documents.get_db", return_value=iter([mock_db_session])), \
         patch("app.api.endpoints.documents.get_api_key", return_value=mock_user):
        
        # Get documents
        response = client.get("/api/v1/documents/")
    
    # Verify response
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["document_id"] == "test_document"


def test_get_document(client, mock_db_session, mock_user, mock_document):
    """Test getting a document."""
    # Set up mocks
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_document
    
    # Mock dependencies
    with patch("app.api.endpoints.documents.get_db", return_value=iter([mock_db_session])), \
         patch("app.api.endpoints.documents.get_api_key", return_value=mock_user):
        
        # Get document
        response = client.get("/api/v1/documents/test_document")
    
    # Verify response
    assert response.status_code == 200
    assert response.json()["document_id"] == "test_document"


def test_upload_document(client, mock_db_session, mock_user, mock_document):
    """Test uploading a document."""
    # Set up mocks
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None
    
    # Mock document creation
    with patch("app.api.endpoints.documents.Document", return_value=mock_document), \
         patch("app.api.endpoints.documents.get_db", return_value=iter([mock_db_session])), \
         patch("app.api.endpoints.documents.get_api_key", return_value=mock_user), \
         patch("app.api.endpoints.documents.process_document_async", return_value="test_workflow"), \
         patch("app.api.endpoints.documents.uuid.uuid4", return_value=MagicMock(hex="1234567890")), \
         patch("app.api.endpoints.documents.os.path.join", return_value="/tmp/test_document.pdf"), \
         patch("app.api.endpoints.documents.shutil.copyfileobj"):
        
        # Upload document
        with open("api/tests/api/endpoints/test_documents.py", "rb") as f:
            response = client.post(
                "/api/v1/documents/upload",
                files={"file": ("test_document.pdf", f, "application/pdf")},
                data={"template_id": "test_template", "options": '{"option1": "value1"}'},
            )
    
    # Verify response
    assert response.status_code == 200
    assert response.json()["document_id"] == "test_document"
    assert response.json()["status"] == "pending"
    assert response.json()["job_id"] == "test_workflow"


def test_get_job_status(client, mock_db_session, mock_user, mock_document):
    """Test getting job status."""
    # Set up mocks
    mock_document.job_id = "test_workflow"
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_document
    
    # Mock dependencies
    with patch("app.api.endpoints.documents.get_db", return_value=iter([mock_db_session])), \
         patch("app.api.endpoints.documents.get_api_key", return_value=mock_user), \
         patch("app.api.endpoints.documents.get_processing_status", return_value={
             "workflow_id": "test_workflow",
             "document_id": "test_document",
             "status": "running",
             "progress": 50.0,
         }):
        
        # Get job status
        response = client.get("/api/v1/documents/jobs/test_workflow")
    
    # Verify response
    assert response.status_code == 200
    assert response.json()["workflow_id"] == "test_workflow"
    assert response.json()["document_id"] == "test_document"
    assert response.json()["status"] == "running"
    assert response.json()["progress"] == 50.0


def test_get_document_results(client, mock_db_session, mock_user, mock_document):
    """Test getting document results."""
    # Set up mocks
    mock_document.status = "completed"
    mock_document.extraction_results_json = json.dumps({
        "document_type": "invoice",
        "fields": {
            "invoice_number": {"value": "INV-12345", "confidence": 0.95},
            "date": {"value": "2023-05-10", "confidence": 0.92},
            "total_amount": {"value": "1250.00", "confidence": 0.98},
        },
        "tables": {
            "line_items": {
                "headers": ["Description", "Quantity", "Unit Price", "Total"],
                "rows": [
                    ["Product A", "2", "500.00", "1000.00"],
                    ["Service B", "1", "250.00", "250.00"],
                ],
                "confidence": 0.9,
            }
        },
        "confidence": 0.95,
    })
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_document
    
    # Mock dependencies
    with patch("app.api.endpoints.documents.get_db", return_value=iter([mock_db_session])), \
         patch("app.api.endpoints.documents.get_api_key", return_value=mock_user):
        
        # Get document results
        response = client.get("/api/v1/documents/test_document/results")
    
    # Verify response
    assert response.status_code == 200
    assert response.json()["document_id"] == "test_document"
    assert "extraction_results" in response.json()
    assert response.json()["extraction_results"]["document_type"] == "invoice"
    assert "fields" in response.json()["extraction_results"]
    assert "tables" in response.json()["extraction_results"]
