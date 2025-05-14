"""
Tests for the prompt manager.

This module contains tests for the prompt manager.
"""

import json
import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch

from app.ml.llm.prompt_manager import PromptManager


@pytest.fixture
def temp_templates_dir():
    """Create a temporary directory for templates."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_init_with_built_in_templates():
    """Test initializing with built-in templates."""
    # Create prompt manager
    manager = PromptManager()
    
    # Verify built-in templates were loaded
    assert "document_understanding" in manager.templates
    assert "field_extraction" in manager.templates
    assert "table_extraction" in manager.templates
    assert "validation" in manager.templates


def test_init_with_templates_dir(temp_templates_dir):
    """Test initializing with templates directory."""
    # Create test template file
    template_path = os.path.join(temp_templates_dir, "test_template.txt")
    with open(template_path, "w") as f:
        f.write("Test template content")
    
    # Create prompt manager
    manager = PromptManager(templates_dir=temp_templates_dir)
    
    # Verify template was loaded
    assert "test_template" in manager.templates
    assert manager.templates["test_template"] == "Test template content"


def test_render_template():
    """Test rendering a template."""
    # Create prompt manager
    manager = PromptManager()
    
    # Add test template
    manager.templates["test_template"] = "Hello, {{ name }}!"
    
    # Render template
    rendered = manager.render_template("test_template", {"name": "World"})
    
    # Verify rendered template
    assert rendered == "Hello, World!"


def test_render_template_unknown():
    """Test rendering an unknown template."""
    # Create prompt manager
    manager = PromptManager()
    
    # Render unknown template
    with pytest.raises(ValueError):
        manager.render_template("unknown_template", {})


def test_add_template(temp_templates_dir):
    """Test adding a template."""
    # Create prompt manager
    manager = PromptManager(templates_dir=temp_templates_dir)
    
    # Add template
    manager.add_template("test_template", "Test template content")
    
    # Verify template was added
    assert "test_template" in manager.templates
    assert manager.templates["test_template"] == "Test template content"
    
    # Verify template was saved to file
    template_path = os.path.join(temp_templates_dir, "test_template.txt")
    assert os.path.exists(template_path)
    with open(template_path, "r") as f:
        assert f.read() == "Test template content"


def test_get_template():
    """Test getting a template."""
    # Create prompt manager
    manager = PromptManager()
    
    # Add test template
    manager.templates["test_template"] = "Test template content"
    
    # Get template
    template = manager.get_template("test_template")
    
    # Verify template
    assert template == "Test template content"


def test_get_template_unknown():
    """Test getting an unknown template."""
    # Create prompt manager
    manager = PromptManager()
    
    # Get unknown template
    with pytest.raises(ValueError):
        manager.get_template("unknown_template")


def test_get_available_templates():
    """Test getting available templates."""
    # Create prompt manager
    manager = PromptManager()
    
    # Add test templates
    manager.templates["test_template_1"] = "Test template 1"
    manager.templates["test_template_2"] = "Test template 2"
    
    # Get available templates
    templates = manager.get_available_templates()
    
    # Verify templates
    assert "test_template_1" in templates
    assert "test_template_2" in templates


def test_format_json_for_prompt():
    """Test formatting JSON for prompt."""
    # Create prompt manager
    manager = PromptManager()
    
    # Format JSON
    formatted = manager.format_json_for_prompt({"key": "value"})
    
    # Verify formatted JSON
    assert formatted == json.dumps({"key": "value"}, indent=2)


def test_parse_json_from_response_valid():
    """Test parsing JSON from a valid response."""
    # Create prompt manager
    manager = PromptManager()
    
    # Parse JSON
    parsed = manager.parse_json_from_response('{"key": "value"}')
    
    # Verify parsed JSON
    assert parsed == {"key": "value"}


def test_parse_json_from_response_embedded():
    """Test parsing JSON from a response with embedded JSON."""
    # Create prompt manager
    manager = PromptManager()
    
    # Parse JSON
    parsed = manager.parse_json_from_response('Some text before {"key": "value"} some text after')
    
    # Verify parsed JSON
    assert parsed == {"key": "value"}


def test_parse_json_from_response_array():
    """Test parsing JSON array from a response."""
    # Create prompt manager
    manager = PromptManager()
    
    # Parse JSON
    parsed = manager.parse_json_from_response('Some text before ["item1", "item2"] some text after')
    
    # Verify parsed JSON
    assert parsed == ["item1", "item2"]


def test_parse_json_from_response_invalid():
    """Test parsing JSON from an invalid response."""
    # Create prompt manager
    manager = PromptManager()
    
    # Parse JSON
    parsed = manager.parse_json_from_response('Not a valid JSON')
    
    # Verify parsed JSON
    assert "error" in parsed
    assert parsed["raw_response"] == 'Not a valid JSON'
