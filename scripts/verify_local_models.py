#!/usr/bin/env python3
"""
Script to verify local model configuration for Clary AI.

This script checks if local models are properly configured and can be loaded.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import Clary AI modules
try:
    from api.app.core.config import settings
    from api.app.ml.llm.model_manager import ModelManager
except ImportError as e:
    logger.error(f"Error importing Clary AI modules: {e}")
    logger.error("Make sure you're running this script from the project root directory.")
    sys.exit(1)


async def verify_models():
    """Verify that local models are properly configured and can be loaded."""
    logger.info("Verifying local model configuration...")
    
    # Check model directory
    model_dir = os.path.join(settings.MODEL_PATH, "llm")
    logger.info(f"Model directory: {model_dir}")
    
    if not os.path.exists(model_dir):
        logger.warning(f"Model directory does not exist: {model_dir}")
        os.makedirs(model_dir, exist_ok=True)
        logger.info(f"Created model directory: {model_dir}")
    
    # Initialize model manager
    model_manager = ModelManager(model_dir=model_dir)
    
    # Get available models
    available_models = model_manager.get_available_models()
    logger.info(f"Available models: {available_models}")
    
    # Check if model files exist
    for model_name in available_models:
        config = model_manager.model_configs[model_name]
        model_path = os.path.join(model_dir, config["filename"])
        
        if os.path.exists(model_path):
            logger.info(f"Model file found: {model_path}")
            logger.info(f"Model file size: {os.path.getsize(model_path) / (1024 * 1024):.2f} MB")
        else:
            logger.warning(f"Model file not found: {model_path}")
            logger.info(f"Expected model file: {config['filename']}")
            logger.info(f"From Hugging Face repo: {config['repo_id']}")
    
    # Try to load the default model
    default_model = settings.LLM_MODEL
    logger.info(f"Default model: {default_model}")
    
    try:
        logger.info(f"Attempting to load model: {default_model}")
        model = await model_manager.load_model(default_model)
        logger.info(f"Model loaded successfully: {default_model}")
        
        # Test generation
        logger.info("Testing model generation...")
        prompt = "Hello, I am testing if you are working correctly. Please respond with a short greeting."
        response = await model_manager.generate(
            model_name=default_model,
            prompt=prompt,
            max_tokens=50,
            temperature=0.7,
        )
        logger.info(f"Model response: {response}")
        
        # Unload model
        model_manager.unload_model(default_model)
        logger.info(f"Model unloaded: {default_model}")
        
    except Exception as e:
        logger.error(f"Error loading model {default_model}: {e}")
        logger.error("Please check your model configuration and files.")
    
    logger.info("Model verification complete.")


if __name__ == "__main__":
    asyncio.run(verify_models())
