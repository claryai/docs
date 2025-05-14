"""
Tests for the document understanding component.

This module contains tests for the document understanding component.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.ml.llm.document_understanding import DocumentUnderstanding
from app.ml.llm.model_manager import ModelManager
from app.ml.llm.prompt_manager import PromptManager


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
    manager.format_json_for_prompt = MagicMock(return_value='{"key": "value"}')
    manager.parse_json_from_response = MagicMock(return_value={"document_type": "invoice"})
    return manager


@pytest.fixture
def document_understanding(mock_model_manager, mock_prompt_manager):
    """Create a document understanding component."""
    return DocumentUnderstanding(
        model_manager=mock_model_manager,
        prompt_manager=mock_prompt_manager,
        default_model="test-model",
    )


@pytest.mark.asyncio
async def test_understand_document(document_understanding, mock_model_manager, mock_prompt_manager):
    """Test understanding a document."""
    # Set up mock response
    mock_prompt_manager.parse_json_from_response.return_value = {
        "document_type": "invoice",
        "document_purpose": "Billing for products or services",
        "key_entities": {
            "sender": "ABC Company",
            "recipient": "XYZ Corporation",
        },
    }
    
    # Understand document
    result = await document_understanding.understand_document(
        document_text="Test document",
        document_layout={"layout": "test"},
        document_type="invoice",
    )
    
    # Verify prompt was rendered
    mock_prompt_manager.render_template.assert_called_once_with(
        "document_understanding",
        {
            "document_text": "Test document",
            "document_layout": '{"key": "value"}',
            "document_type": "invoice",
        },
    )
    
    # Verify model was called
    mock_model_manager.generate.assert_called_once_with(
        model_name="test-model",
        prompt="Test prompt",
        max_tokens=2048,
        temperature=0.1,
        top_p=0.9,
        stop=["\n\n"],
    )
    
    # Verify response was parsed
    mock_prompt_manager.parse_json_from_response.assert_called_once_with(
        '{"document_type": "invoice"}'
    )
    
    # Verify result
    assert result["document_type"] == "invoice"
    assert result["document_purpose"] == "Billing for products or services"
    assert "key_entities" in result


@pytest.mark.asyncio
async def test_extract_fields(document_understanding, mock_model_manager, mock_prompt_manager):
    """Test extracting fields."""
    # Set up mock response
    mock_prompt_manager.parse_json_from_response.return_value = {
        "invoice_number": {"value": "INV-12345", "confidence": 0.95},
        "date": {"value": "2023-05-10", "confidence": 0.92},
        "total_amount": {"value": "1250.00", "confidence": 0.98},
    }
    
    # Extract fields
    result = await document_understanding.extract_fields(
        document_text="Test document",
        document_layout={"layout": "test"},
        fields_to_extract=[
            {"name": "invoice_number", "type": "string"},
            {"name": "date", "type": "date"},
            {"name": "total_amount", "type": "currency"},
        ],
    )
    
    # Verify prompt was rendered
    mock_prompt_manager.render_template.assert_called_once_with(
        "field_extraction",
        {
            "document_text": "Test document",
            "document_layout": '{"key": "value"}',
            "document_understanding": '{"key": "value"}',
            "fields_to_extract": '{"key": "value"}',
        },
    )
    
    # Verify model was called
    mock_model_manager.generate.assert_called_once_with(
        model_name="test-model",
        prompt="Test prompt",
        max_tokens=2048,
        temperature=0.1,
        top_p=0.9,
        stop=["\n\n"],
    )
    
    # Verify response was parsed
    mock_prompt_manager.parse_json_from_response.assert_called_once_with(
        '{"document_type": "invoice"}'
    )
    
    # Verify result
    assert "invoice_number" in result
    assert "date" in result
    assert "total_amount" in result
    assert result["invoice_number"]["value"] == "INV-12345"
    assert result["date"]["value"] == "2023-05-10"
    assert result["total_amount"]["value"] == "1250.00"


@pytest.mark.asyncio
async def test_extract_tables(document_understanding, mock_model_manager, mock_prompt_manager):
    """Test extracting tables."""
    # Set up mock response
    mock_prompt_manager.parse_json_from_response.return_value = {
        "line_items": {
            "headers": ["Description", "Quantity", "Unit Price", "Total"],
            "rows": [
                ["Product A", "2", "500.00", "1000.00"],
                ["Service B", "1", "250.00", "250.00"],
            ],
            "confidence": 0.9,
        }
    }
    
    # Extract tables
    result = await document_understanding.extract_tables(
        document_text="Test document",
        document_layout={"layout": "test"},
        tables_to_extract=[
            {
                "name": "line_items",
                "columns": ["Description", "Quantity", "Unit Price", "Total"],
            },
        ],
    )
    
    # Verify prompt was rendered
    mock_prompt_manager.render_template.assert_called_once_with(
        "table_extraction",
        {
            "document_text": "Test document",
            "document_layout": '{"key": "value"}',
            "document_understanding": '{"key": "value"}',
            "tables_to_extract": '{"key": "value"}',
        },
    )
    
    # Verify model was called
    mock_model_manager.generate.assert_called_once_with(
        model_name="test-model",
        prompt="Test prompt",
        max_tokens=2048,
        temperature=0.1,
        top_p=0.9,
        stop=["\n\n"],
    )
    
    # Verify response was parsed
    mock_prompt_manager.parse_json_from_response.assert_called_once_with(
        '{"document_type": "invoice"}'
    )
    
    # Verify result
    assert "line_items" in result
    assert "headers" in result["line_items"]
    assert "rows" in result["line_items"]
    assert result["line_items"]["headers"] == ["Description", "Quantity", "Unit Price", "Total"]
    assert len(result["line_items"]["rows"]) == 2


@pytest.mark.asyncio
async def test_validate_extraction(document_understanding, mock_model_manager, mock_prompt_manager):
    """Test validating extraction."""
    # Set up mock response
    mock_prompt_manager.parse_json_from_response.return_value = {
        "valid": True,
        "issues": [],
        "corrections": {},
    }
    
    # Validate extraction
    result = await document_understanding.validate_extraction(
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
    
    # Verify prompt was rendered
    mock_prompt_manager.render_template.assert_called_once_with(
        "validation",
        {
            "document_text": "Test document",
            "document_understanding": '{"key": "value"}',
            "extracted_fields": '{"key": "value"}',
            "extracted_tables": '{"key": "value"}',
        },
    )
    
    # Verify model was called
    mock_model_manager.generate.assert_called_once_with(
        model_name="test-model",
        prompt="Test prompt",
        max_tokens=2048,
        temperature=0.1,
        top_p=0.9,
        stop=["\n\n"],
    )
    
    # Verify response was parsed
    mock_prompt_manager.parse_json_from_response.assert_called_once_with(
        '{"document_type": "invoice"}'
    )
    
    # Verify result
    assert result["valid"] is True
    assert "issues" in result
    assert "corrections" in result


def test_prepare_document_text():
    """Test preparing document text."""
    # Create document understanding
    understanding = DocumentUnderstanding(
        model_manager=MagicMock(),
        prompt_manager=MagicMock(),
        default_model="test-model",
    )
    
    # Prepare short document text
    short_text = "Short document text"
    prepared_short = understanding._prepare_document_text(short_text)
    assert prepared_short == short_text
    
    # Prepare long document text
    long_text = "A" * 5000
    prepared_long = understanding._prepare_document_text(long_text, max_length=4000)
    assert len(prepared_long) <= 4020  # 4000 + length of truncation message
    assert prepared_long.endswith("... [truncated]")


def test_clear_context():
    """Test clearing context."""
    # Create document understanding
    understanding = DocumentUnderstanding(
        model_manager=MagicMock(),
        prompt_manager=MagicMock(),
        default_model="test-model",
    )
    
    # Add items to context
    understanding.context = {
        "document_understanding": {"document_type": "invoice"},
        "extracted_fields": {"invoice_number": {"value": "INV-12345"}},
    }
    
    # Clear context
    understanding.clear_context()
    
    # Verify context was cleared
    assert understanding.context == {}
