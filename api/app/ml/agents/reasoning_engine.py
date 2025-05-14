"""
Reasoning engine for the Clary AI API.

This module provides LLM-based reasoning capabilities for document processing.
"""

import logging
import os
import json
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.ml.llm.model_manager import ModelManager
from app.ml.llm.prompt_manager import PromptManager
from app.ml.llm.document_understanding import DocumentUnderstanding


# Configure logging
logger = logging.getLogger(__name__)


class ReasoningEngine:
    """
    Reasoning engine for document understanding and extraction.

    This class provides LLM-based reasoning capabilities for document processing.
    """

    def __init__(self, model_name: str = None):
        """
        Initialize the reasoning engine.

        Args:
            model_name: Name of the LLM model to use.
        """
        self.model_name = model_name or settings.LLM_MODEL
        self.model_path = os.path.join(settings.MODEL_PATH, "llm")
        self.model_manager = None
        self.prompt_manager = None
        self.document_understanding = None
        self.context = {}

        logger.info(f"Initialized reasoning engine with model: {self.model_name}")

    async def initialize(self):
        """Initialize the LLM components."""
        if self.model_manager is not None:
            return

        logger.info("Initializing reasoning engine components")

        # Create model directory if it doesn't exist
        os.makedirs(self.model_path, exist_ok=True)

        # Initialize model manager
        self.model_manager = ModelManager(model_dir=self.model_path)

        # Initialize prompt manager
        templates_dir = os.path.join(settings.MODEL_PATH, "templates")
        os.makedirs(templates_dir, exist_ok=True)
        self.prompt_manager = PromptManager(templates_dir=templates_dir)

        # Initialize document understanding
        self.document_understanding = DocumentUnderstanding(
            model_manager=self.model_manager,
            prompt_manager=self.prompt_manager,
            default_model=self.model_name,
        )

        # Preload model
        try:
            await self.model_manager.load_model(self.model_name)
            logger.info(f"Model {self.model_name} loaded successfully")
        except Exception as e:
            logger.warning(f"Error preloading model {self.model_name}: {e}")
            logger.warning("Reasoning engine will attempt to load the model when needed")

        logger.info("Reasoning engine components initialized successfully")

    async def understand_document(
        self,
        document_text: str,
        document_layout: Dict[str, Any],
        document_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Understand a document using LLM-based reasoning.

        Args:
            document_text: Text content of the document.
            document_layout: Layout analysis results.
            document_type: Optional document type.

        Returns:
            Dict[str, Any]: Document understanding results.
        """
        logger.info("Understanding document with LLM")

        # Initialize components if needed
        await self.initialize()

        # Understand document
        understanding = await self.document_understanding.understand_document(
            document_text=document_text,
            document_layout=document_layout,
            document_type=document_type,
            model_name=self.model_name,
        )

        # Update context
        self.context["document_understanding"] = understanding

        return understanding

    def _create_document_understanding_prompt(
        self,
        document_text: str,
        document_layout: Dict[str, Any],
        document_type: Optional[str] = None,
    ) -> PromptTemplate:
        """
        Create a prompt for document understanding.

        Args:
            document_text: Text content of the document.
            document_layout: Layout analysis results.
            document_type: Optional document type.

        Returns:
            PromptTemplate: Prompt template for document understanding.
        """
        template = """
        You are an AI assistant that understands documents. You will be given the text and layout information of a document, and your task is to understand its structure, purpose, and key components.

        Document Text:
        {document_text}

        Document Layout Information:
        {document_layout}

        Document Type (if known): {document_type}

        Please analyze this document and provide the following information:
        1. Document Type: What type of document is this? (e.g., invoice, receipt, contract, letter, etc.)
        2. Document Purpose: What is the main purpose of this document?
        3. Key Entities: Who are the main entities mentioned in the document? (e.g., sender, recipient, company names)
        4. Key Sections: What are the main sections or components of the document?
        5. Important Fields: What are the important fields or data points in this document?
        6. Tables: Are there any tables in the document? If so, what information do they contain?
        7. Next Steps: What processing steps would be most appropriate for this document?

        Provide your analysis in a structured JSON format with the following keys:
        - document_type
        - document_purpose
        - key_entities
        - key_sections
        - important_fields
        - tables
        - next_steps

        JSON Response:
        """

        return PromptTemplate(
            template=template,
            input_variables=["document_text", "document_layout", "document_type"],
        )

    def _parse_document_understanding_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the response from the document understanding prompt.

        Args:
            response: LLM response.

        Returns:
            Dict[str, Any]: Parsed document understanding.
        """
        # In a real implementation, parse the JSON response
        # For now, return a mock result
        return {
            "document_type": "invoice",
            "document_purpose": "Billing for products or services",
            "key_entities": {
                "sender": "ABC Company",
                "recipient": "XYZ Corporation",
            },
            "key_sections": [
                "header",
                "billing_info",
                "line_items",
                "totals",
                "footer",
            ],
            "important_fields": [
                "invoice_number",
                "date",
                "due_date",
                "total_amount",
                "tax_amount",
            ],
            "tables": [
                {
                    "name": "line_items",
                    "columns": ["description", "quantity", "unit_price", "total"],
                }
            ],
            "next_steps": [
                "extract_fields",
                "extract_tables",
                "validate_results",
            ],
        }

    async def extract_fields(
        self,
        document_text: str,
        document_layout: Dict[str, Any],
        fields_to_extract: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Extract fields from a document using LLM-based reasoning.

        Args:
            document_text: Text content of the document.
            document_layout: Layout analysis results.
            fields_to_extract: List of fields to extract.

        Returns:
            Dict[str, Any]: Extracted fields.
        """
        logger.info("Extracting fields with LLM")

        # Initialize components if needed
        await self.initialize()

        # Extract fields
        extracted_fields = await self.document_understanding.extract_fields(
            document_text=document_text,
            document_layout=document_layout,
            fields_to_extract=fields_to_extract,
            model_name=self.model_name,
        )

        # Update context
        self.context["extracted_fields"] = extracted_fields

        return extracted_fields

    def _create_field_extraction_prompt(
        self,
        document_text: str,
        document_layout: Dict[str, Any],
        fields_to_extract: List[Dict[str, Any]],
    ) -> PromptTemplate:
        """
        Create a prompt for field extraction.

        Args:
            document_text: Text content of the document.
            document_layout: Layout analysis results.
            fields_to_extract: List of fields to extract.

        Returns:
            PromptTemplate: Prompt template for field extraction.
        """
        template = """
        You are an AI assistant that extracts information from documents. You will be given the text and layout information of a document, along with a list of fields to extract.

        Document Text:
        {document_text}

        Document Layout Information:
        {document_layout}

        Document Understanding:
        {document_understanding}

        Fields to Extract:
        {fields_to_extract}

        Please extract the requested fields from the document. For each field, provide:
        1. The extracted value
        2. A confidence score (0.0 to 1.0)
        3. The location in the document where the field was found (if available)

        Provide your extraction in a structured JSON format with field names as keys, and values containing the extracted information.

        JSON Response:
        """

        return PromptTemplate(
            template=template,
            input_variables=[
                "document_text",
                "document_layout",
                "fields_to_extract",
                "document_understanding",
            ],
        )

    def _parse_field_extraction_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the response from the field extraction prompt.

        Args:
            response: LLM response.

        Returns:
            Dict[str, Any]: Parsed extracted fields.
        """
        # In a real implementation, parse the JSON response
        # For now, return a mock result
        return {
            "invoice_number": {
                "value": "INV-12345",
                "confidence": 0.95,
                "location": "top-right",
            },
            "date": {
                "value": "2023-05-10",
                "confidence": 0.92,
                "location": "top-right",
            },
            "total_amount": {
                "value": "1250.00",
                "confidence": 0.98,
                "location": "bottom-right",
            },
        }

    async def extract_tables(
        self,
        document_text: str,
        document_layout: Dict[str, Any],
        tables_to_extract: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Extract tables from a document using LLM-based reasoning.

        Args:
            document_text: Text content of the document.
            document_layout: Layout analysis results.
            tables_to_extract: List of tables to extract.

        Returns:
            Dict[str, Any]: Extracted tables.
        """
        logger.info("Extracting tables with LLM")

        # Initialize components if needed
        await self.initialize()

        # Extract tables
        extracted_tables = await self.document_understanding.extract_tables(
            document_text=document_text,
            document_layout=document_layout,
            tables_to_extract=tables_to_extract,
            model_name=self.model_name,
        )

        # Update context
        self.context["extracted_tables"] = extracted_tables

        return extracted_tables

    def _create_table_extraction_prompt(
        self,
        document_text: str,
        document_layout: Dict[str, Any],
        tables_to_extract: List[Dict[str, Any]],
    ) -> PromptTemplate:
        """
        Create a prompt for table extraction.

        Args:
            document_text: Text content of the document.
            document_layout: Layout analysis results.
            tables_to_extract: List of tables to extract.

        Returns:
            PromptTemplate: Prompt template for table extraction.
        """
        template = """
        You are an AI assistant that extracts tables from documents. You will be given the text and layout information of a document, along with a list of tables to extract.

        Document Text:
        {document_text}

        Document Layout Information:
        {document_layout}

        Document Understanding:
        {document_understanding}

        Tables to Extract:
        {tables_to_extract}

        Please extract the requested tables from the document. For each table, provide:
        1. The table name
        2. The column headers
        3. The rows of data
        4. A confidence score (0.0 to 1.0)

        Provide your extraction in a structured JSON format with table names as keys, and values containing the extracted information.

        JSON Response:
        """

        return PromptTemplate(
            template=template,
            input_variables=[
                "document_text",
                "document_layout",
                "tables_to_extract",
                "document_understanding",
            ],
        )

    def _parse_table_extraction_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the response from the table extraction prompt.

        Args:
            response: LLM response.

        Returns:
            Dict[str, Any]: Parsed extracted tables.
        """
        # In a real implementation, parse the JSON response
        # For now, return a mock result
        return {
            "line_items": {
                "headers": ["Description", "Quantity", "Unit Price", "Total"],
                "rows": [
                    ["Product A", "2", "500.00", "1000.00"],
                    ["Service B", "1", "250.00", "250.00"],
                ],
                "confidence": 0.9,
            }
        }

    async def validate_extraction(
        self,
        document_text: str,
        extracted_fields: Dict[str, Any],
        extracted_tables: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate extracted information using LLM-based reasoning.

        Args:
            document_text: Text content of the document.
            extracted_fields: Extracted fields.
            extracted_tables: Extracted tables.

        Returns:
            Dict[str, Any]: Validation results.
        """
        logger.info("Validating extraction with LLM")

        # Initialize components if needed
        await self.initialize()

        # Validate extraction
        validation_results = await self.document_understanding.validate_extraction(
            document_text=document_text,
            extracted_fields=extracted_fields,
            extracted_tables=extracted_tables,
            model_name=self.model_name,
        )

        # Update context
        self.context["validation_results"] = validation_results

        return validation_results

    def clear_context(self) -> None:
        """Clear the context."""
        logger.info("Clearing context")
        self.context = {}

        # Clear document understanding context if initialized
        if self.document_understanding:
            self.document_understanding.clear_context()

    async def shutdown(self) -> None:
        """Shutdown the reasoning engine."""
        logger.info("Shutting down reasoning engine")

        # Unload models
        if self.model_manager:
            self.model_manager.unload_all_models()

        # Clear context
        self.clear_context()

        logger.info("Reasoning engine shut down successfully")
