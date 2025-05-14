"""
Document understanding for the Clary AI API.

This module provides document understanding capabilities using LLM models.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from app.ml.llm.model_manager import ModelManager
from app.ml.llm.prompt_manager import PromptManager


# Configure logging
logger = logging.getLogger(__name__)


class DocumentUnderstanding:
    """
    Document understanding component.
    
    This class provides methods for understanding documents using LLM models.
    """
    
    def __init__(
        self,
        model_manager: ModelManager,
        prompt_manager: PromptManager,
        default_model: str = "llama-3-8b",
    ):
        """
        Initialize the document understanding component.
        
        Args:
            model_manager: Model manager for loading models.
            prompt_manager: Prompt manager for rendering prompts.
            default_model: Default model to use.
        """
        self.model_manager = model_manager
        self.prompt_manager = prompt_manager
        self.default_model = default_model
        self.context = {}
        
        logger.info(f"Initialized document understanding with default model: {default_model}")
    
    async def understand_document(
        self,
        document_text: str,
        document_layout: Dict[str, Any],
        document_type: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Understand a document.
        
        Args:
            document_text: Text content of the document.
            document_layout: Layout analysis results.
            document_type: Optional document type.
            model_name: Optional model name to use.
            
        Returns:
            Dict[str, Any]: Document understanding results.
        """
        logger.info("Understanding document")
        
        # Use default model if not specified
        model_name = model_name or self.default_model
        
        # Prepare variables for prompt
        variables = {
            "document_text": self._prepare_document_text(document_text),
            "document_layout": self.prompt_manager.format_json_for_prompt(document_layout),
            "document_type": document_type or "unknown",
        }
        
        # Render prompt
        prompt = self.prompt_manager.render_template("document_understanding", variables)
        
        # Generate response
        response = await self.model_manager.generate(
            model_name=model_name,
            prompt=prompt,
            max_tokens=2048,
            temperature=0.1,
            top_p=0.9,
            stop=["\n\n"],
        )
        
        # Parse response
        understanding = self.prompt_manager.parse_json_from_response(response)
        
        # Store understanding in context
        self.context["document_understanding"] = understanding
        
        logger.info("Document understanding completed")
        return understanding
    
    async def extract_fields(
        self,
        document_text: str,
        document_layout: Dict[str, Any],
        fields_to_extract: List[Dict[str, Any]],
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract fields from a document.
        
        Args:
            document_text: Text content of the document.
            document_layout: Layout analysis results.
            fields_to_extract: List of fields to extract.
            model_name: Optional model name to use.
            
        Returns:
            Dict[str, Any]: Extracted fields.
        """
        logger.info("Extracting fields from document")
        
        # Use default model if not specified
        model_name = model_name or self.default_model
        
        # Get document understanding from context
        document_understanding = self.context.get("document_understanding", {})
        
        # Prepare variables for prompt
        variables = {
            "document_text": self._prepare_document_text(document_text),
            "document_layout": self.prompt_manager.format_json_for_prompt(document_layout),
            "document_understanding": self.prompt_manager.format_json_for_prompt(document_understanding),
            "fields_to_extract": self.prompt_manager.format_json_for_prompt(fields_to_extract),
        }
        
        # Render prompt
        prompt = self.prompt_manager.render_template("field_extraction", variables)
        
        # Generate response
        response = await self.model_manager.generate(
            model_name=model_name,
            prompt=prompt,
            max_tokens=2048,
            temperature=0.1,
            top_p=0.9,
            stop=["\n\n"],
        )
        
        # Parse response
        extracted_fields = self.prompt_manager.parse_json_from_response(response)
        
        # Store extracted fields in context
        self.context["extracted_fields"] = extracted_fields
        
        logger.info("Field extraction completed")
        return extracted_fields
    
    async def extract_tables(
        self,
        document_text: str,
        document_layout: Dict[str, Any],
        tables_to_extract: List[Dict[str, Any]],
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract tables from a document.
        
        Args:
            document_text: Text content of the document.
            document_layout: Layout analysis results.
            tables_to_extract: List of tables to extract.
            model_name: Optional model name to use.
            
        Returns:
            Dict[str, Any]: Extracted tables.
        """
        logger.info("Extracting tables from document")
        
        # Use default model if not specified
        model_name = model_name or self.default_model
        
        # Get document understanding from context
        document_understanding = self.context.get("document_understanding", {})
        
        # Prepare variables for prompt
        variables = {
            "document_text": self._prepare_document_text(document_text),
            "document_layout": self.prompt_manager.format_json_for_prompt(document_layout),
            "document_understanding": self.prompt_manager.format_json_for_prompt(document_understanding),
            "tables_to_extract": self.prompt_manager.format_json_for_prompt(tables_to_extract),
        }
        
        # Render prompt
        prompt = self.prompt_manager.render_template("table_extraction", variables)
        
        # Generate response
        response = await self.model_manager.generate(
            model_name=model_name,
            prompt=prompt,
            max_tokens=2048,
            temperature=0.1,
            top_p=0.9,
            stop=["\n\n"],
        )
        
        # Parse response
        extracted_tables = self.prompt_manager.parse_json_from_response(response)
        
        # Store extracted tables in context
        self.context["extracted_tables"] = extracted_tables
        
        logger.info("Table extraction completed")
        return extracted_tables
    
    async def validate_extraction(
        self,
        document_text: str,
        extracted_fields: Dict[str, Any],
        extracted_tables: Dict[str, Any],
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validate extracted information.
        
        Args:
            document_text: Text content of the document.
            extracted_fields: Extracted fields.
            extracted_tables: Extracted tables.
            model_name: Optional model name to use.
            
        Returns:
            Dict[str, Any]: Validation results.
        """
        logger.info("Validating extracted information")
        
        # Use default model if not specified
        model_name = model_name or self.default_model
        
        # Get document understanding from context
        document_understanding = self.context.get("document_understanding", {})
        
        # Prepare variables for prompt
        variables = {
            "document_text": self._prepare_document_text(document_text),
            "document_understanding": self.prompt_manager.format_json_for_prompt(document_understanding),
            "extracted_fields": self.prompt_manager.format_json_for_prompt(extracted_fields),
            "extracted_tables": self.prompt_manager.format_json_for_prompt(extracted_tables),
        }
        
        # Render prompt
        prompt = self.prompt_manager.render_template("validation", variables)
        
        # Generate response
        response = await self.model_manager.generate(
            model_name=model_name,
            prompt=prompt,
            max_tokens=2048,
            temperature=0.1,
            top_p=0.9,
            stop=["\n\n"],
        )
        
        # Parse response
        validation_results = self.prompt_manager.parse_json_from_response(response)
        
        # Store validation results in context
        self.context["validation_results"] = validation_results
        
        logger.info("Validation completed")
        return validation_results
    
    def _prepare_document_text(self, document_text: str, max_length: int = 4000) -> str:
        """
        Prepare document text for inclusion in a prompt.
        
        Args:
            document_text: Text content of the document.
            max_length: Maximum length of the document text.
            
        Returns:
            str: Prepared document text.
        """
        # Truncate document text if it's too long
        if len(document_text) > max_length:
            return document_text[:max_length] + "... [truncated]"
        
        return document_text
    
    def clear_context(self) -> None:
        """Clear the context."""
        logger.info("Clearing context")
        self.context = {}
