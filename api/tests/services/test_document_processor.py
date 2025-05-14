"""
Tests for the document processor service.

This module contains tests for the document processor service.
"""

import asyncio
import datetime
import json
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.document_processor import (
    process_document,
    process_document_async,
    get_processing_status,
    _execute_workflow_background,
)


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def mock_document():
    """Create a mock document."""
    document = MagicMock(spec=Document)
    document.document_id = "test_document"
    document.file_path = "test_document.pdf"
    document.status = "pending"
    document.job_id = None
    return document


@pytest.mark.asyncio
async def test_process_document():
    """Test processing a document."""
    # Mock processors
    with patch("app.services.document_processor.DocumentPreprocessor") as mock_preprocessor_class, \
         patch("app.services.document_processor.PDFExtractor") as mock_pdf_extractor_class, \
         patch("app.services.document_processor.LayoutProcessor") as mock_layout_processor_class, \
         patch("app.services.document_processor.ExtractionAgent") as mock_extraction_agent_class:
        
        # Set up mock returns
        mock_preprocessor = mock_preprocessor_class.return_value
        mock_preprocessor.process = AsyncMock(return_value={
            "text": "Test document text",
            "document_type": "invoice",
            "structure": {"pages": 1},
            "elements": [{"type": "text", "text": "Test document text"}],
        })
        
        mock_pdf_extractor = mock_pdf_extractor_class.return_value
        mock_pdf_extractor.process = AsyncMock(return_value={
            "text": "Test document text",
            "pages": [{"text": "Test document text", "page": 1}],
        })
        
        mock_layout_processor = mock_layout_processor_class.return_value
        mock_layout_processor.process = AsyncMock(return_value={
            "layout": [{"type": "text", "text": "Test document text"}],
        })
        
        mock_extraction_agent = mock_extraction_agent_class.return_value
        mock_extraction_agent.extract = AsyncMock(return_value={
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
        
        # Process document
        result = await process_document(
            document_path="test_document.pdf",
            template_id="test_template",
            options={"option1": "value1"},
        )
    
    # Verify processors were called
    mock_preprocessor.process.assert_called_once_with("test_document.pdf")
    mock_pdf_extractor.process.assert_called_once_with("test_document.pdf")
    mock_layout_processor.process.assert_called_once()
    mock_extraction_agent.extract.assert_called_once()
    
    # Verify result
    assert result["document_type"] == "invoice"
    assert "fields" in result
    assert "tables" in result
    assert "confidence" in result


@pytest.mark.asyncio
async def test_process_document_async(mock_db_session, mock_document):
    """Test processing a document asynchronously."""
    # Set up mocks
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_document
    
    # Mock create_workflow
    with patch("app.services.document_processor.create_workflow") as mock_create_workflow, \
         patch("app.services.document_processor.asyncio.create_task") as mock_create_task, \
         patch("app.services.document_processor.get_db", return_value=iter([mock_db_session])):
        
        mock_create_workflow.return_value = "test_workflow"
        
        # Process document asynchronously
        workflow_id = await process_document_async(
            document_path="test_document.pdf",
            template_id="test_template",
            options={"option1": "value1"},
            callback_url="http://example.com/callback",
        )
    
    # Verify create_workflow was called
    mock_create_workflow.assert_called_once_with(
        document_id="test_document",
        template_id="test_template",
        options={"option1": "value1"},
        db=mock_db_session,
    )
    
    # Verify create_task was called
    mock_create_task.assert_called_once()
    
    # Verify result
    assert workflow_id == "test_workflow"


@pytest.mark.asyncio
async def test_execute_workflow_background():
    """Test executing a workflow in the background."""
    # Mock execute_workflow
    with patch("app.services.document_processor.execute_workflow") as mock_execute_workflow:
        mock_execute_workflow.return_value = {"status": "completed"}
        
        # Execute workflow in background
        await _execute_workflow_background(
            workflow_id="test_workflow",
            callback_url="http://example.com/callback",
        )
    
    # Verify execute_workflow was called
    mock_execute_workflow.assert_called_once_with("test_workflow")


@pytest.mark.asyncio
async def test_get_processing_status_workflow():
    """Test getting processing status for a workflow."""
    # Mock get_workflow_status
    with patch("app.services.document_processor.get_workflow_status") as mock_get_workflow_status:
        mock_get_workflow_status.return_value = {
            "workflow_id": "test_workflow",
            "document_id": "test_document",
            "status": "running",
            "task_counts": {"total": 8, "completed": 4},
            "progress": 50.0,
        }
        
        # Get processing status
        status = await get_processing_status("test_workflow")
    
    # Verify get_workflow_status was called
    mock_get_workflow_status.assert_called_once_with("test_workflow")
    
    # Verify result
    assert status["workflow_id"] == "test_workflow"
    assert status["document_id"] == "test_document"
    assert status["status"] == "running"
    assert status["progress"] == 50.0


@pytest.mark.asyncio
async def test_get_processing_status_document(mock_db_session, mock_document):
    """Test getting processing status for a document."""
    # Set up mocks
    mock_document.job_id = "test_job"
    mock_document.status = "completed"
    mock_document.extraction_status = "success"
    mock_document.created_at = datetime.datetime.now(datetime.timezone.utc)
    mock_document.completed_at = datetime.datetime.now(datetime.timezone.utc)
    
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_document
    
    # Mock get_workflow_status
    with patch("app.services.document_processor.get_workflow_status") as mock_get_workflow_status, \
         patch("app.services.document_processor.get_db", return_value=iter([mock_db_session])):
        
        mock_get_workflow_status.return_value = {"status": "not_found"}
        
        # Get processing status
        status = await get_processing_status("test_job")
    
    # Verify get_workflow_status was called
    mock_get_workflow_status.assert_called_once_with("test_job")
    
    # Verify result
    assert status["job_id"] == "test_job"
    assert status["document_id"] == "test_document"
    assert status["status"] == "completed"
    assert status["extraction_status"] == "success"
