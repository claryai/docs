#!/usr/bin/env python3
"""
Script to download models for DocuAgent.

This script downloads the required AI models for the application.
"""

import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("download_models")


# Define model paths
MODEL_DIR = Path(settings.MODEL_PATH)


# Define models to download
MODELS = {
    "llm": {
        "llama-3-8b": {
            "url": "https://huggingface.co/TheBloke/Llama-3-8B-GGUF/resolve/main/llama-3-8b.Q4_K_M.gguf",
            "path": MODEL_DIR / "llm" / "llama-3-8b.Q4_K_M.gguf",
            "tier": "professional",
        },
        "mistral-7b": {
            "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
            "path": MODEL_DIR / "llm" / "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
            "tier": "professional",
        },
        "phi-4-multimodal": {
            "url": "https://huggingface.co/microsoft/Phi-4-Multimodal-GGUF/resolve/main/phi-4-multimodal.Q4_K_M.gguf",
            "path": MODEL_DIR / "llm" / "phi-4-multimodal.Q4_K_M.gguf",
            "tier": "standard",
        },
    },
    "layout": {
        "layoutlmv3": {
            "url": "https://huggingface.co/microsoft/layoutlmv3-base",
            "path": MODEL_DIR / "layout" / "layoutlmv3-base",
            "use_transformers": True,
        },
    },
}


def download_model(model_type: str, model_name: str) -> bool:
    """
    Download a specific model.

    Args:
        model_type: Type of model (llm, layout, etc.).
        model_name: Name of the model.

    Returns:
        bool: True if successful, False otherwise.
    """
    if model_type not in MODELS or model_name not in MODELS[model_type]:
        logger.error(f"Unknown model: {model_type}/{model_name}")
        return False

    model_info = MODELS[model_type][model_name]
    model_path = model_info["path"]

    # Create directory if it doesn't exist
    os.makedirs(model_path.parent, exist_ok=True)

    # Check if model already exists
    if model_path.exists() and not model_info.get("use_transformers", False):
        logger.info(f"Model {model_type}/{model_name} already exists at {model_path}")
        return True

    # Download model
    logger.info(f"Downloading {model_type}/{model_name} to {model_path}")

    if model_info.get("use_transformers", False):
        # Use transformers to download the model
        try:
            from transformers import AutoModel
            AutoModel.from_pretrained(model_info["url"], cache_dir=str(model_path))
            logger.info(f"Successfully downloaded {model_type}/{model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to download {model_type}/{model_name}: {e}")
            return False
    else:
        # Use wget to download the model
        try:
            subprocess.run(
                ["wget", "-O", str(model_path), model_info["url"]],
                check=True,
            )
            logger.info(f"Successfully downloaded {model_type}/{model_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download {model_type}/{model_name}: {e}")
            return False


def download_all_models() -> bool:
    """
    Download all models.

    Returns:
        bool: True if all downloads were successful, False otherwise.
    """
    success = True
    for model_type, models in MODELS.items():
        for model_name in models:
            if not download_model(model_type, model_name):
                success = False
    return success


def main() -> int:
    """
    Main function.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(description="Download models for DocuAgent")
    parser.add_argument(
        "--model-type",
        choices=list(MODELS.keys()),
        help="Type of model to download",
    )
    parser.add_argument(
        "--model-name",
        help="Name of model to download",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all models",
    )

    args = parser.parse_args()

    if args.all:
        success = download_all_models()
    elif args.model_type and args.model_name:
        success = download_model(args.model_type, args.model_name)
    else:
        parser.print_help()
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
