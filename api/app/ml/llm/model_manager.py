"""
Model manager for the Clary AI API.

This module provides model management for LLM models.
"""

import asyncio
import logging
import os
import shutil
import tempfile
from typing import Any, Dict, List, Optional, Union

import aiohttp
import huggingface_hub
from llama_cpp import Llama


# Configure logging
logger = logging.getLogger(__name__)


class ModelManager:
    """
    Model manager for loading and managing LLM models.

    This class provides methods for loading, downloading, and managing LLM models.
    """

    def __init__(self, model_dir: str):
        """
        Initialize the model manager.

        Args:
            model_dir: Directory where models are stored.
        """
        self.model_dir = model_dir
        self.models = {}
        self.model_configs = {
            "llama-3-8b": {
                "repo_id": "TheBloke/Llama-3-8B-GGUF",
                "filename": "llama-3-8b.Q4_K_M.gguf",
                "type": "llama",
                "context_length": 4096,
                "batch_size": 512,
                "tier": "professional",
                "description": "Llama 3 8B model for professional tier",
            },
            "mistral-7b": {
                "repo_id": "TheBloke/Mistral-7B-v0.1-GGUF",
                "filename": "mistral-7b-v0.1.Q4_K_M.gguf",
                "type": "llama",  # Uses llama.cpp compatible format
                "context_length": 4096,
                "batch_size": 512,
                "tier": "professional",
                "description": "Mistral 7B model for professional tier",
            },
            "phi-4-multimodal": {
                "repo_id": "microsoft/Phi-4-Multimodal-GGUF",
                "filename": "phi-4-multimodal.Q4_K_M.gguf",
                "type": "llama",  # Uses llama.cpp compatible format
                "context_length": 4096,
                "batch_size": 512,
                "tier": "standard",
                "description": "Phi-4 Multimodal model for standard tier",
            },
        }

        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)

        logger.info(f"Initialized model manager with model directory: {model_dir}")

    def get_models_for_tier(self, tier: str) -> List[str]:
        """
        Get a list of models available for a given tier.

        Args:
            tier: The tier to check.

        Returns:
            List[str]: List of model names available for the tier.
        """
        models = []

        # For lite tier, no models are available
        if tier == "lite":
            return []

        # For standard tier, only standard models are available
        if tier == "standard":
            for model_name, config in self.model_configs.items():
                if config.get("tier") == "standard":
                    models.append(model_name)
            return models

        # For professional tier, all models are available
        if tier == "professional":
            return list(self.model_configs.keys())

        return models

    def is_model_available_for_tier(self, model_name: str, tier: str) -> bool:
        """
        Check if a model is available for a given tier.

        Args:
            model_name: The model to check.
            tier: The tier to check.

        Returns:
            bool: True if the model is available for the tier, False otherwise.
        """
        # For lite tier, no models are available
        if tier == "lite":
            return False

        # For standard tier, only standard models are available
        if tier == "standard":
            model_config = self.model_configs.get(model_name, {})
            return model_config.get("tier") == "standard"

        # For professional tier, all models are available
        if tier == "professional":
            return model_name in self.model_configs

        return False

    async def load_model(
        self,
        model_name: str,
        force_download: bool = False,
        gpu_layers: int = -1,
    ) -> Any:
        """
        Load a model.

        Args:
            model_name: Name of the model to load.
            force_download: Whether to force download the model even if it exists.
            gpu_layers: Number of layers to offload to GPU (-1 for auto-detect).

        Returns:
            Any: The loaded model.
        """
        logger.info(f"Loading model: {model_name}")

        # Check if model is already loaded
        if model_name in self.models and not force_download:
            logger.info(f"Model already loaded: {model_name}")
            return self.models[model_name]

        # Get model config
        if model_name not in self.model_configs:
            raise ValueError(f"Unknown model: {model_name}")

        config = self.model_configs[model_name]
        model_path = os.path.join(self.model_dir, config["filename"])

        # Download model if it doesn't exist or force_download is True
        if not os.path.exists(model_path) or force_download:
            await self._download_model(model_name)

        # Load model based on type
        if config["type"] == "llama":
            logger.info(f"Loading Llama model: {model_name}")
            model = Llama(
                model_path=model_path,
                n_ctx=config["context_length"],
                n_batch=config["batch_size"],
                n_gpu_layers=gpu_layers,
                verbose=False,
            )
        else:
            raise ValueError(f"Unsupported model type: {config['type']}")

        # Store model
        self.models[model_name] = model

        logger.info(f"Model loaded successfully: {model_name}")
        return model

    async def _download_model(self, model_name: str) -> None:
        """
        Download a model.

        Args:
            model_name: Name of the model to download.
        """
        logger.info(f"Downloading model: {model_name}")

        # Get model config
        config = self.model_configs[model_name]
        model_path = os.path.join(self.model_dir, config["filename"])

        try:
            # Create a temporary directory for downloading
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download model from Hugging Face
                logger.info(f"Downloading from Hugging Face: {config['repo_id']}/{config['filename']}")
                huggingface_hub.hf_hub_download(
                    repo_id=config["repo_id"],
                    filename=config["filename"],
                    local_dir=temp_dir,
                    local_dir_use_symlinks=False,
                )

                # Move model to model directory
                temp_model_path = os.path.join(temp_dir, config["filename"])
                shutil.move(temp_model_path, model_path)

            logger.info(f"Model downloaded successfully: {model_name}")

        except Exception as e:
            logger.error(f"Error downloading model {model_name}: {e}")
            raise

    async def generate(
        self,
        model_name: str,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.1,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None,
    ) -> str:
        """
        Generate text using a model.

        Args:
            model_name: Name of the model to use.
            prompt: Prompt to generate from.
            max_tokens: Maximum number of tokens to generate.
            temperature: Temperature for sampling.
            top_p: Top-p for nucleus sampling.
            stop: List of strings to stop generation at.

        Returns:
            str: Generated text.
        """
        logger.info(f"Generating text with model: {model_name}")

        # Load model if not already loaded
        model = await self.load_model(model_name)

        # Generate text
        try:
            response = model(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop or [],
                echo=False,
            )

            # Extract generated text
            if isinstance(response, dict) and "choices" in response:
                generated_text = response["choices"][0]["text"]
            else:
                generated_text = response

            logger.info(f"Text generated successfully with model: {model_name}")
            return generated_text

        except Exception as e:
            logger.error(f"Error generating text with model {model_name}: {e}")
            raise

    async def generate_stream(
        self,
        model_name: str,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.1,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None,
    ) -> Any:
        """
        Generate text using a model with streaming.

        Args:
            model_name: Name of the model to use.
            prompt: Prompt to generate from.
            max_tokens: Maximum number of tokens to generate.
            temperature: Temperature for sampling.
            top_p: Top-p for nucleus sampling.
            stop: List of strings to stop generation at.

        Returns:
            Any: Generator yielding generated text chunks.
        """
        logger.info(f"Generating text stream with model: {model_name}")

        # Load model if not already loaded
        model = await self.load_model(model_name)

        # Generate text stream
        try:
            response_iter = model(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop or [],
                echo=False,
                stream=True,
            )

            # Yield generated text chunks
            for response in response_iter:
                if isinstance(response, dict) and "choices" in response:
                    chunk = response["choices"][0]["text"]
                    yield chunk
                else:
                    yield response

            logger.info(f"Text stream generated successfully with model: {model_name}")

        except Exception as e:
            logger.error(f"Error generating text stream with model {model_name}: {e}")
            raise

    def unload_model(self, model_name: str) -> None:
        """
        Unload a model.

        Args:
            model_name: Name of the model to unload.
        """
        logger.info(f"Unloading model: {model_name}")

        if model_name in self.models:
            # Get model
            model = self.models[model_name]

            # Unload model
            del self.models[model_name]

            # Force garbage collection
            import gc
            gc.collect()

            logger.info(f"Model unloaded successfully: {model_name}")
        else:
            logger.warning(f"Model not loaded: {model_name}")

    def unload_all_models(self) -> None:
        """Unload all models."""
        logger.info("Unloading all models")

        # Get list of loaded models
        model_names = list(self.models.keys())

        # Unload each model
        for model_name in model_names:
            self.unload_model(model_name)

        logger.info("All models unloaded successfully")

    def get_available_models(self) -> List[str]:
        """
        Get list of available models.

        Returns:
            List[str]: List of available model names.
        """
        return list(self.model_configs.keys())

    def get_loaded_models(self) -> List[str]:
        """
        Get list of loaded models.

        Returns:
            List[str]: List of loaded model names.
        """
        return list(self.models.keys())
