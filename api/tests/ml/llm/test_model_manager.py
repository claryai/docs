"""
Tests for the model manager.

This module contains tests for the model manager.
"""

import asyncio
import os
import tempfile
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.ml.llm.model_manager import ModelManager


@pytest.fixture
def temp_model_dir():
    """Create a temporary directory for models."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_llama():
    """Create a mock Llama model."""
    llama = MagicMock()
    llama.return_value = {"choices": [{"text": "Test response"}]}
    return llama


@pytest.mark.asyncio
async def test_load_model(temp_model_dir, mock_llama):
    """Test loading a model."""
    # Create model manager
    manager = ModelManager(model_dir=temp_model_dir)
    
    # Add test model config
    manager.model_configs["test-model"] = {
        "repo_id": "test/model",
        "filename": "test-model.gguf",
        "type": "llama",
        "context_length": 4096,
        "batch_size": 512,
    }
    
    # Mock dependencies
    with patch("app.ml.llm.model_manager.Llama", return_value=mock_llama), \
         patch("app.ml.llm.model_manager.huggingface_hub.hf_hub_download"), \
         patch("app.ml.llm.model_manager.shutil.move"), \
         patch("app.ml.llm.model_manager.os.path.exists", return_value=True):
        
        # Load model
        model = await manager.load_model("test-model")
    
    # Verify model was loaded
    assert model == mock_llama
    assert "test-model" in manager.models


@pytest.mark.asyncio
async def test_download_model(temp_model_dir):
    """Test downloading a model."""
    # Create model manager
    manager = ModelManager(model_dir=temp_model_dir)
    
    # Add test model config
    manager.model_configs["test-model"] = {
        "repo_id": "test/model",
        "filename": "test-model.gguf",
        "type": "llama",
        "context_length": 4096,
        "batch_size": 512,
    }
    
    # Mock dependencies
    with patch("app.ml.llm.model_manager.huggingface_hub.hf_hub_download") as mock_download, \
         patch("app.ml.llm.model_manager.shutil.move") as mock_move, \
         patch("app.ml.llm.model_manager.os.path.exists", return_value=False):
        
        # Download model
        await manager._download_model("test-model")
    
    # Verify download was called
    mock_download.assert_called_once()
    mock_move.assert_called_once()


@pytest.mark.asyncio
async def test_generate(temp_model_dir, mock_llama):
    """Test generating text."""
    # Create model manager
    manager = ModelManager(model_dir=temp_model_dir)
    
    # Add test model config
    manager.model_configs["test-model"] = {
        "repo_id": "test/model",
        "filename": "test-model.gguf",
        "type": "llama",
        "context_length": 4096,
        "batch_size": 512,
    }
    
    # Mock dependencies
    with patch("app.ml.llm.model_manager.Llama", return_value=mock_llama), \
         patch("app.ml.llm.model_manager.huggingface_hub.hf_hub_download"), \
         patch("app.ml.llm.model_manager.shutil.move"), \
         patch("app.ml.llm.model_manager.os.path.exists", return_value=True):
        
        # Load model
        await manager.load_model("test-model")
        
        # Generate text
        response = await manager.generate(
            model_name="test-model",
            prompt="Test prompt",
            max_tokens=100,
            temperature=0.5,
            top_p=0.9,
            stop=["END"],
        )
    
    # Verify generate was called
    mock_llama.assert_called_with(
        prompt="Test prompt",
        max_tokens=100,
        temperature=0.5,
        top_p=0.9,
        stop=["END"],
        echo=False,
    )
    
    # Verify response
    assert response == "Test response"


@pytest.mark.asyncio
async def test_generate_stream(temp_model_dir, mock_llama):
    """Test generating text stream."""
    # Create model manager
    manager = ModelManager(model_dir=temp_model_dir)
    
    # Add test model config
    manager.model_configs["test-model"] = {
        "repo_id": "test/model",
        "filename": "test-model.gguf",
        "type": "llama",
        "context_length": 4096,
        "batch_size": 512,
    }
    
    # Mock stream response
    mock_llama.return_value = [
        {"choices": [{"text": "Test"}]},
        {"choices": [{"text": " response"}]},
    ]
    
    # Mock dependencies
    with patch("app.ml.llm.model_manager.Llama", return_value=mock_llama), \
         patch("app.ml.llm.model_manager.huggingface_hub.hf_hub_download"), \
         patch("app.ml.llm.model_manager.shutil.move"), \
         patch("app.ml.llm.model_manager.os.path.exists", return_value=True):
        
        # Load model
        await manager.load_model("test-model")
        
        # Generate text stream
        chunks = []
        async for chunk in manager.generate_stream(
            model_name="test-model",
            prompt="Test prompt",
            max_tokens=100,
            temperature=0.5,
            top_p=0.9,
            stop=["END"],
        ):
            chunks.append(chunk)
    
    # Verify generate was called
    mock_llama.assert_called_with(
        prompt="Test prompt",
        max_tokens=100,
        temperature=0.5,
        top_p=0.9,
        stop=["END"],
        echo=False,
        stream=True,
    )
    
    # Verify response
    assert chunks == ["Test", " response"]


def test_unload_model(temp_model_dir):
    """Test unloading a model."""
    # Create model manager
    manager = ModelManager(model_dir=temp_model_dir)
    
    # Add mock model
    mock_model = MagicMock()
    manager.models["test-model"] = mock_model
    
    # Unload model
    with patch("app.ml.llm.model_manager.gc.collect") as mock_gc:
        manager.unload_model("test-model")
    
    # Verify model was unloaded
    assert "test-model" not in manager.models
    mock_gc.assert_called_once()


def test_unload_all_models(temp_model_dir):
    """Test unloading all models."""
    # Create model manager
    manager = ModelManager(model_dir=temp_model_dir)
    
    # Add mock models
    mock_model1 = MagicMock()
    mock_model2 = MagicMock()
    manager.models["test-model-1"] = mock_model1
    manager.models["test-model-2"] = mock_model2
    
    # Unload all models
    with patch("app.ml.llm.model_manager.gc.collect") as mock_gc:
        manager.unload_all_models()
    
    # Verify models were unloaded
    assert len(manager.models) == 0
    assert mock_gc.call_count == 2


def test_get_available_models(temp_model_dir):
    """Test getting available models."""
    # Create model manager
    manager = ModelManager(model_dir=temp_model_dir)
    
    # Add test model configs
    manager.model_configs = {
        "test-model-1": {},
        "test-model-2": {},
    }
    
    # Get available models
    models = manager.get_available_models()
    
    # Verify models
    assert "test-model-1" in models
    assert "test-model-2" in models
    assert len(models) == 2


def test_get_loaded_models(temp_model_dir):
    """Test getting loaded models."""
    # Create model manager
    manager = ModelManager(model_dir=temp_model_dir)
    
    # Add mock models
    mock_model1 = MagicMock()
    mock_model2 = MagicMock()
    manager.models["test-model-1"] = mock_model1
    manager.models["test-model-2"] = mock_model2
    
    # Get loaded models
    models = manager.get_loaded_models()
    
    # Verify models
    assert "test-model-1" in models
    assert "test-model-2" in models
    assert len(models) == 2
