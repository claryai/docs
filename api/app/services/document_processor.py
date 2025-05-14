"""
Document processor service for the Clary AI API.

This module provides services for processing documents.
"""

import logging
import os
import asyncio
import datetime
from typing import Any, Dict, Optional

from app.core.config import settings
from app.ml.processors.document_preprocessor import DocumentPreprocessor
from app.ml.processors.pdf_extractor import PDFExtractor
from app.ml.processors.ocr_processor import OCRProcessor
from app.ml.processors.layout_processor import LayoutProcessor
from app.ml.agents.extraction_agent import ExtractionAgent


# Configure logging
logger = logging.getLogger(__name__)


async def process_document(
    document_path: str,
    template_id: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Process a document and extract information.

    Args:
        document_path: Path to the document file.
        template_id: Optional ID of extraction template to apply.
        options: Optional processing options.

    Returns:
        Dict[str, Any]: The extraction results.
    """
    logger.info(f"Processing document: {document_path}")

    # Initialize processors
    document_preprocessor = DocumentPreprocessor()
    pdf_extractor = PDFExtractor()
    ocr_processor = OCRProcessor(model_name=settings.OCR_MODEL)
    layout_processor = LayoutProcessor(model_name=settings.LAYOUT_MODEL)
    extraction_agent = ExtractionAgent(model_name=settings.LLM_MODEL)

    try:
        # Preprocess document using Unstructured.io
        logger.info("Preprocessing document with Unstructured.io")
        preprocess_result = await document_preprocessor.process(document_path)

        # Extract text based on document type
        _, ext = os.path.splitext(document_path)
        ext = ext.lower()

        if ext == ".pdf":
            # Use Marker for PDF text extraction
            logger.info("Extracting text from PDF with Marker")
            text_result = await pdf_extractor.process(document_path)
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"]:
            # Use OCR for image text extraction
            logger.info("Extracting text with OCR")
            text_result = await ocr_processor.process(document_path)
        else:
            # For other document types, use the preprocessor result
            logger.info("Using preprocessor result for text extraction")
            text_result = {
                "text": preprocess_result["text"],
                "pages": [{"text": preprocess_result["text"], "page": 1}]
            }

        # Analyze layout
        logger.info("Analyzing document layout")
        layout_result = await layout_processor.process(document_path, text_result)

        # Enhance layout result with preprocessor information
        enhanced_layout = {
            **layout_result,
            "document_type": preprocess_result.get("document_type", "unknown"),
            "structure": preprocess_result.get("structure", {}),
            "elements": preprocess_result.get("elements", [])
        }

        # Extract information using agent
        logger.info("Extracting information with agent")
        extraction_result = await extraction_agent.extract(
            document_path,
            text_result,
            enhanced_layout,
            template_id=template_id,
            options=options,
        )

        logger.info("Document processing completed successfully")
        return extraction_result

    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise


async def process_document_async(
    document_path: str,
    template_id: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    callback_url: Optional[str] = None,
) -> str:
    """
    Process a document asynchronously and return a job ID.

    Args:
        document_path: Path to the document file.
        template_id: Optional ID of extraction template to apply.
        options: Optional processing options.
        callback_url: Optional URL to call when processing is complete.

    Returns:
        str: Job ID for tracking the processing job.
    """
    from app.db.session import get_db
    from app.models.document import Document
    from app.services.workflow_service import create_workflow, execute_workflow

    # Create a database session
    db = next(get_db())

    try:
        # Get document from database
        document = db.query(Document).filter(Document.file_path == document_path).first()
        if not document:
            raise ValueError(f"Document not found: {document_path}")

        # Create workflow
        workflow_id = await create_workflow(
            document_id=document.document_id,
            template_id=template_id,
            options=options,
            db=db,
        )

        # Start workflow execution in background
        asyncio.create_task(
            _execute_workflow_background(
                workflow_id=workflow_id,
                callback_url=callback_url,
            )
        )

        return workflow_id

    except Exception as e:
        logger.error(f"Error starting document processing: {e}")
        raise

    finally:
        db.close()


async def _execute_workflow_background(
    workflow_id: str,
    callback_url: Optional[str] = None,
) -> None:
    """
    Execute a workflow in the background.

    Args:
        workflow_id: ID of the workflow to execute.
        callback_url: Optional URL to call when processing is complete.
    """
    from app.services.workflow_service import execute_workflow, get_workflow_status

    try:
        # Execute the workflow
        result = await execute_workflow(workflow_id)

        # Call callback URL if provided
        if callback_url:
            logger.info(f"Would call callback URL: {callback_url} with status: completed")
            # In a real implementation, use httpx or aiohttp to call the callback URL
            # For now, just log the callback

    except Exception as e:
        logger.error(f"Error executing workflow in background: {e}")

        # Call callback URL if provided
        if callback_url:
            logger.info(f"Would call callback URL: {callback_url} with status: failed, error: {str(e)}")
            # In a real implementation, use httpx or aiohttp to call the callback URL
            # For now, just log the callback


async def get_processing_status(job_id: str) -> Dict[str, Any]:
    """
    Get the status of a document processing job.

    Args:
        job_id: Job ID for tracking the processing job.

    Returns:
        Dict[str, Any]: Job status information.
    """
    from app.services.workflow_service import get_workflow_status

    try:
        # First try to get status as a workflow
        workflow_status = await get_workflow_status(job_id)

        if workflow_status.get("status") != "not_found":
            return workflow_status

        # If not found as a workflow, try to get status from document
        from app.db.session import get_db
        from app.models.document import Document

        # Create a database session
        db = next(get_db())

        try:
            # Get document from database
            document = db.query(Document).filter(Document.job_id == job_id).first()

            if not document:
                return {
                    "job_id": job_id,
                    "status": "not_found",
                }

            return {
                "job_id": job_id,
                "document_id": document.document_id,
                "status": document.status,
                "extraction_status": document.extraction_status,
                "created_at": document.created_at.isoformat() if document.created_at else None,
                "completed_at": document.completed_at.isoformat() if document.completed_at else None,
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        return {
            "job_id": job_id,
            "status": "error",
            "error": str(e),
        }
