"""
Extraction agent for the Clary AI API.

This module provides agentic extraction capabilities.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.ml.agents.workflow_engine import WorkflowEngine
from app.ml.agents.reasoning_engine import ReasoningEngine


# Configure logging
logger = logging.getLogger(__name__)


class ExtractionAgent:
    """
    Extraction agent for extracting structured information from documents.

    This class provides methods for extracting information using LLMs.
    """

    def __init__(self, model_name: str = "llama-3-8b"):
        """
        Initialize the extraction agent.

        Args:
            model_name: Name of the LLM model to use.
        """
        self.model_name = model_name
        self.workflow_engine = WorkflowEngine()
        self.reasoning_engine = ReasoningEngine(model_name=model_name)
        logger.info(f"Initialized extraction agent with model: {model_name}")

    async def extract(
        self,
        document_path: str,
        ocr_result: Dict[str, Any],
        layout_result: Dict[str, Any],
        template_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Extract structured information from a document.

        Args:
            document_path: Path to the document file.
            ocr_result: OCR results from OCRProcessor.
            layout_result: Layout analysis results from LayoutProcessor.
            template_id: Optional ID of extraction template to apply.
            options: Optional extraction options.

        Returns:
            Dict[str, Any]: The extraction results.
        """
        logger.info(f"Extracting information from document: {document_path}")

        try:
            # Create and execute workflow
            workflow_id = await self.workflow_engine.create_workflow(
                document_path=document_path,
                template_id=template_id,
                options=options,
            )

            # Store OCR and layout results in context
            self.reasoning_engine.context["ocr_result"] = ocr_result
            self.reasoning_engine.context["layout_result"] = layout_result

            # Understand document
            document_understanding = await self.reasoning_engine.understand_document(
                document_text=ocr_result.get("text", ""),
                document_layout=layout_result,
                document_type=layout_result.get("document_type"),
            )

            # Determine fields to extract based on document type and template
            fields_to_extract = await self._get_fields_to_extract(
                document_understanding, template_id
            )

            # Extract fields
            extracted_fields = await self.reasoning_engine.extract_fields(
                document_text=ocr_result.get("text", ""),
                document_layout=layout_result,
                fields_to_extract=fields_to_extract,
            )

            # Determine tables to extract based on document type and template
            tables_to_extract = await self._get_tables_to_extract(
                document_understanding, template_id
            )

            # Extract tables
            extracted_tables = await self.reasoning_engine.extract_tables(
                document_text=ocr_result.get("text", ""),
                document_layout=layout_result,
                tables_to_extract=tables_to_extract,
            )

            # Combine results
            extraction_results = {
                "document_type": document_understanding.get("document_type", "unknown"),
                "fields": extracted_fields,
                "tables": extracted_tables,
                "confidence": self._calculate_confidence(extracted_fields, extracted_tables),
            }

            logger.info(f"Extraction completed for document: {document_path}")
            return extraction_results

        except Exception as e:
            logger.error(f"Error extracting information from document: {e}")
            # Fallback to simpler extraction if workflow fails
            if template_id == "template_invoice_standard" or (
                document_understanding and document_understanding.get("document_type") == "invoice"
            ):
                return await self._extract_invoice(ocr_result, layout_result)
            else:
                return await self._extract_generic(ocr_result, layout_result)

    async def _get_fields_to_extract(
        self,
        document_understanding: Dict[str, Any],
        template_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get fields to extract based on document type and template.

        Args:
            document_understanding: Document understanding results.
            template_id: Optional ID of extraction template to apply.

        Returns:
            List[Dict[str, Any]]: List of fields to extract.
        """
        # In a real implementation, get fields from template or document understanding
        # For now, return a mock list

        document_type = document_understanding.get("document_type", "unknown")

        if document_type == "invoice":
            return [
                {"name": "invoice_number", "type": "string", "required": True},
                {"name": "date", "type": "date", "required": True},
                {"name": "due_date", "type": "date", "required": False},
                {"name": "total_amount", "type": "currency", "required": True},
                {"name": "tax_amount", "type": "currency", "required": False},
                {"name": "vendor_name", "type": "string", "required": True},
                {"name": "vendor_address", "type": "string", "required": False},
                {"name": "customer_name", "type": "string", "required": True},
                {"name": "customer_address", "type": "string", "required": False},
            ]
        else:
            # Generic fields
            return [
                {"name": "title", "type": "string", "required": False},
                {"name": "date", "type": "date", "required": False},
                {"name": "author", "type": "string", "required": False},
            ]

    async def _get_tables_to_extract(
        self,
        document_understanding: Dict[str, Any],
        template_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get tables to extract based on document type and template.

        Args:
            document_understanding: Document understanding results.
            template_id: Optional ID of extraction template to apply.

        Returns:
            List[Dict[str, Any]]: List of tables to extract.
        """
        # In a real implementation, get tables from template or document understanding
        # For now, return a mock list

        document_type = document_understanding.get("document_type", "unknown")

        if document_type == "invoice":
            return [
                {
                    "name": "line_items",
                    "required": True,
                    "columns": [
                        {"name": "description", "type": "string"},
                        {"name": "quantity", "type": "number"},
                        {"name": "unit_price", "type": "currency"},
                        {"name": "total", "type": "currency"},
                    ],
                }
            ]
        else:
            # No tables for generic documents
            return []

    def _calculate_confidence(
        self,
        extracted_fields: Dict[str, Any],
        extracted_tables: Dict[str, Any],
    ) -> float:
        """
        Calculate overall confidence score.

        Args:
            extracted_fields: Extracted fields.
            extracted_tables: Extracted tables.

        Returns:
            float: Overall confidence score.
        """
        # Calculate average confidence of fields
        field_confidences = [
            field.get("confidence", 0.0) for field in extracted_fields.values()
        ]

        # Calculate average confidence of tables
        table_confidences = [
            table.get("confidence", 0.0) for table in extracted_tables.values()
        ]

        # Combine confidences
        all_confidences = field_confidences + table_confidences

        if not all_confidences:
            return 0.0

        return sum(all_confidences) / len(all_confidences)

    async def _extract_invoice(
        self,
        ocr_result: Dict[str, Any],
        layout_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract information from an invoice.

        Args:
            ocr_result: OCR results from OCRProcessor.
            layout_result: Layout analysis results from LayoutProcessor.

        Returns:
            Dict[str, Any]: The extraction results.
        """
        # In a real implementation, use the LLM to extract information
        # For now, return mock results

        return {
            "document_type": "invoice",
            "fields": {
                "invoice_number": {
                    "value": "INV-12345",
                    "confidence": 0.95,
                    "bounding_box": {
                        "left": 100,
                        "top": 200,
                        "width": 100,
                        "height": 30,
                        "page": 1,
                    }
                },
                "date": {
                    "value": "2023-05-10",
                    "confidence": 0.92,
                    "bounding_box": {
                        "left": 300,
                        "top": 200,
                        "width": 100,
                        "height": 30,
                        "page": 1,
                    }
                },
                "total_amount": {
                    "value": "1250.00",
                    "confidence": 0.98,
                    "bounding_box": {
                        "left": 500,
                        "top": 600,
                        "width": 100,
                        "height": 30,
                        "page": 1,
                    }
                },
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
        }

    async def _extract_generic(
        self,
        ocr_result: Dict[str, Any],
        layout_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract information from a generic document.

        Args:
            ocr_result: OCR results from OCRProcessor.
            layout_result: Layout analysis results from LayoutProcessor.

        Returns:
            Dict[str, Any]: The extraction results.
        """
        # In a real implementation, use the LLM to extract information
        # For now, return mock results

        return {
            "document_type": "generic",
            "fields": {
                "title": {
                    "value": "Sample Document",
                    "confidence": 0.9,
                },
                "content": {
                    "value": ocr_result.get("text", ""),
                    "confidence": 0.8,
                }
            },
            "tables": {},
            "confidence": 0.85,
        }
