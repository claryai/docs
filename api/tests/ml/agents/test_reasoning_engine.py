"""
Tests for the reasoning engine.

This module contains tests for the reasoning engine.
"""

import asyncio
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.ml.agents.reasoning_engine import ReasoningEngine
from app.ml.llm.model_manager import ModelManager
from app.ml.llm.prompt_manager import PromptManager
from app.ml.llm.document_understanding import DocumentUnderstanding


@pytest.fixture
def mock_model_manager():
    """Create a mock model manager."""
    manager = MagicMock(spec=ModelManager)
    manager.generate = AsyncMock(return_value='{"document_type": "invoice"}')
    return manager


@pytest.fixture
def mock_prompt_manager():
    """Create a mock prompt manager."""
    manager = MagicMock(spec=PromptManager)
    manager.render_template = MagicMock(return_value="Test prompt")
    manager.parse_json_from_response = MagicMock(return_value={"document_type": "invoice"})
    return manager


@pytest.fixture
def mock_document_understanding(mock_model_manager, mock_prompt_manager):
    """Create a mock document understanding."""
    understanding = MagicMock(spec=DocumentUnderstanding)
    understanding.understand_document = AsyncMock(return_value={
        "document_type": "invoice",
        "document_purpose": "Billing for products or services",
        "key_entities": {
            "sender": "ABC Company",
            "recipient": "XYZ Corporation",
        },
    })
    understanding.extract_fields = AsyncMock(return_value={
        "invoice_number": {"value": "INV-12345", "confidence": 0.95},
        "date": {"value": "2023-05-10", "confidence": 0.92},
        "total_amount": {"value": "1250.00", "confidence": 0.98},
    })
    understanding.extract_tables = AsyncMock(return_value={
        "line_items": {
            "headers": ["Description", "Quantity", "Unit Price", "Total"],
            "rows": [
                ["Product A", "2", "500.00", "1000.00"],
                ["Service B", "1", "250.00", "250.00"],
            ],
            "confidence": 0.9,
        }
    })
    understanding.validate_extraction = AsyncMock(return_value={
        "valid": True,
        "issues": [],
        "corrections": {},
    })
    return understanding


@pytest.mark.asyncio
async def test_initialize(mock_model_manager, mock_prompt_manager, mock_document_understanding):
    """Test initializing the reasoning engine."""
    # Create engine
    engine = ReasoningEngine(model_name="test-model")
    
    # Mock dependencies
    with patch("app.ml.agents.reasoning_engine.ModelManager", return_value=mock_model_manager), \
         patch("app.ml.agents.reasoning_engine.PromptManager", return_value=mock_prompt_manager), \
         patch("app.ml.agents.reasoning_engine.DocumentUnderstanding", return_value=mock_document_understanding), \
         patch("app.ml.agents.reasoning_engine.os.makedirs"):
        
        # Initialize engine
        await engine.initialize()
    
    # Verify components were initialized
    assert engine.model_manager == mock_model_manager
    assert engine.prompt_manager == mock_prompt_manager
    assert engine.document_understanding == mock_document_understanding


@pytest.mark.asyncio
async def test_understand_document(mock_model_manager, mock_prompt_manager, mock_document_understanding):
    """Test understanding a document."""
    # Create engine
    engine = ReasoningEngine(model_name="test-model")
    
    # Mock dependencies
    with patch("app.ml.agents.reasoning_engine.ModelManager", return_value=mock_model_manager), \
         patch("app.ml.agents.reasoning_engine.PromptManager", return_value=mock_prompt_manager), \
         patch("app.ml.agents.reasoning_engine.DocumentUnderstanding", return_value=mock_document_understanding), \
         patch("app.ml.agents.reasoning_engine.os.makedirs"):
        
        # Initialize engine
        await engine.initialize()
        
        # Understand document
        result = await engine.understand_document(
            document_text="Test document",
            document_layout={"layout": "test"},
            document_type="invoice",
        )
    
    # Verify document understanding was called
    mock_document_understanding.understand_document.assert_called_once_with(
        document_text="Test document",
        document_layout={"layout": "test"},
        document_type="invoice",
        model_name="test-model",
    )
    
    # Verify result
    assert result["document_type"] == "invoice"
    assert result["document_purpose"] == "Billing for products or services"
    assert "key_entities" in result


@pytest.mark.asyncio
async def test_extract_fields(mock_model_manager, mock_prompt_manager, mock_document_understanding):
    """Test extracting fields."""
    # Create engine
    engine = ReasoningEngine(model_name="test-model")
    
    # Mock dependencies
    with patch("app.ml.agents.reasoning_engine.ModelManager", return_value=mock_model_manager), \
         patch("app.ml.agents.reasoning_engine.PromptManager", return_value=mock_prompt_manager), \
         patch("app.ml.agents.reasoning_engine.DocumentUnderstanding", return_value=mock_document_understanding), \
         patch("app.ml.agents.reasoning_engine.os.makedirs"):
        
        # Initialize engine
        await engine.initialize()
        
        # Extract fields
        result = await engine.extract_fields(
            document_text="Test document",
            document_layout={"layout": "test"},
            fields_to_extract=[
                {"name": "invoice_number", "type": "string"},
                {"name": "date", "type": "date"},
                {"name": "total_amount", "type": "currency"},
            ],
        )
    
    # Verify field extraction was called
    mock_document_understanding.extract_fields.assert_called_once_with(
        document_text="Test document",
        document_layout={"layout": "test"},
        fields_to_extract=[
            {"name": "invoice_number", "type": "string"},
            {"name": "date", "type": "date"},
            {"name": "total_amount", "type": "currency"},
        ],
        model_name="test-model",
    )
    
    # Verify result
    assert "invoice_number" in result
    assert "date" in result
    assert "total_amount" in result
    assert result["invoice_number"]["value"] == "INV-12345"
    assert result["date"]["value"] == "2023-05-10"
    assert result["total_amount"]["value"] == "1250.00"


@pytest.mark.asyncio
async def test_extract_tables(mock_model_manager, mock_prompt_manager, mock_document_understanding):
    """Test extracting tables."""
    # Create engine
    engine = ReasoningEngine(model_name="test-model")
    
    # Mock dependencies
    with patch("app.ml.agents.reasoning_engine.ModelManager", return_value=mock_model_manager), \
         patch("app.ml.agents.reasoning_engine.PromptManager", return_value=mock_prompt_manager), \
         patch("app.ml.agents.reasoning_engine.DocumentUnderstanding", return_value=mock_document_understanding), \
         patch("app.ml.agents.reasoning_engine.os.makedirs"):
        
        # Initialize engine
        await engine.initialize()
        
        # Extract tables
        result = await engine.extract_tables(
            document_text="Test document",
            document_layout={"layout": "test"},
            tables_to_extract=[
                {
                    "name": "line_items",
                    "columns": ["Description", "Quantity", "Unit Price", "Total"],
                },
            ],
        )
    
    # Verify table extraction was called
    mock_document_understanding.extract_tables.assert_called_once_with(
        document_text="Test document",
        document_layout={"layout": "test"},
        tables_to_extract=[
            {
                "name": "line_items",
                "columns": ["Description", "Quantity", "Unit Price", "Total"],
            },
        ],
        model_name="test-model",
    )
    
    # Verify result
    assert "line_items" in result
    assert "headers" in result["line_items"]
    assert "rows" in result["line_items"]
    assert result["line_items"]["headers"] == ["Description", "Quantity", "Unit Price", "Total"]
    assert len(result["line_items"]["rows"]) == 2


@pytest.mark.asyncio
async def test_validate_extraction(mock_model_manager, mock_prompt_manager, mock_document_understanding):
    """Test validating extraction."""
    # Create engine
    engine = ReasoningEngine(model_name="test-model")
    
    # Mock dependencies
    with patch("app.ml.agents.reasoning_engine.ModelManager", return_value=mock_model_manager), \
         patch("app.ml.agents.reasoning_engine.PromptManager", return_value=mock_prompt_manager), \
         patch("app.ml.agents.reasoning_engine.DocumentUnderstanding", return_value=mock_document_understanding), \
         patch("app.ml.agents.reasoning_engine.os.makedirs"):
        
        # Initialize engine
        await engine.initialize()
        
        # Validate extraction
        result = await engine.validate_extraction(
            document_text="Test document",
            extracted_fields={
                "invoice_number": {"value": "INV-12345", "confidence": 0.95},
                "date": {"value": "2023-05-10", "confidence": 0.92},
                "total_amount": {"value": "1250.00", "confidence": 0.98},
            },
            extracted_tables={
                "line_items": {
                    "headers": ["Description", "Quantity", "Unit Price", "Total"],
                    "rows": [
                        ["Product A", "2", "500.00", "1000.00"],
                        ["Service B", "1", "250.00", "250.00"],
                    ],
                    "confidence": 0.9,
                }
            },
        )
    
    # Verify validation was called
    mock_document_understanding.validate_extraction.assert_called_once_with(
        document_text="Test document",
        extracted_fields={
            "invoice_number": {"value": "INV-12345", "confidence": 0.95},
            "date": {"value": "2023-05-10", "confidence": 0.92},
            "total_amount": {"value": "1250.00", "confidence": 0.98},
        },
        extracted_tables={
            "line_items": {
                "headers": ["Description", "Quantity", "Unit Price", "Total"],
                "rows": [
                    ["Product A", "2", "500.00", "1000.00"],
                    ["Service B", "1", "250.00", "250.00"],
                ],
                "confidence": 0.9,
            }
        },
        model_name="test-model",
    )
    
    # Verify result
    assert result["valid"] is True
    assert "issues" in result
    assert "corrections" in result
