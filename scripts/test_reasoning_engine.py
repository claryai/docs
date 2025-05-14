#!/usr/bin/env python3
"""
Script to test the Reasoning Engine with local models for Clary AI.

This script runs a simple test workflow to validate that the Reasoning Engine
is working correctly with local models.
"""

import os
import sys
import asyncio
import logging
import json
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
    from api.app.ml.agents.reasoning_engine import ReasoningEngine
except ImportError as e:
    logger.error(f"Error importing Clary AI modules: {e}")
    logger.error("Make sure you're running this script from the project root directory.")
    sys.exit(1)


async def test_reasoning_engine():
    """Test the Reasoning Engine with a simple document understanding task."""
    logger.info("Testing Reasoning Engine with local models...")
    
    # Create a sample document
    document_text = """
    INVOICE
    
    Invoice Number: INV-12345
    Date: 2023-05-10
    Due Date: 2023-06-10
    
    From:
    ABC Company
    123 Business St
    Business City, BC 12345
    
    To:
    XYZ Corporation
    456 Corporate Ave
    Corporate City, CC 67890
    
    Item Description | Quantity | Unit Price | Total
    ----------------|----------|------------|------
    Product A       | 2        | $500.00    | $1,000.00
    Service B       | 1        | $250.00    | $250.00
    
    Subtotal: $1,250.00
    Tax (0%): $0.00
    Total: $1,250.00
    
    Payment Terms: Net 30
    """
    
    document_layout = {
        "pages": [
            {
                "page_num": 1,
                "width": 612,
                "height": 792,
                "blocks": [
                    {"type": "text", "text": "INVOICE", "bbox": [256, 50, 356, 70]},
                    {"type": "text", "text": "Invoice Number: INV-12345", "bbox": [50, 100, 300, 120]},
                    {"type": "text", "text": "Date: 2023-05-10", "bbox": [50, 120, 300, 140]},
                    {"type": "text", "text": "Due Date: 2023-06-10", "bbox": [50, 140, 300, 160]},
                    {"type": "text", "text": "From:", "bbox": [50, 180, 100, 200]},
                    {"type": "text", "text": "ABC Company", "bbox": [50, 200, 300, 220]},
                    {"type": "text", "text": "To:", "bbox": [50, 280, 100, 300]},
                    {"type": "text", "text": "XYZ Corporation", "bbox": [50, 300, 300, 320]},
                    {"type": "table", "bbox": [50, 380, 562, 480]},
                    {"type": "text", "text": "Subtotal: $1,250.00", "bbox": [400, 500, 562, 520]},
                    {"type": "text", "text": "Total: $1,250.00", "bbox": [400, 540, 562, 560]},
                ]
            }
        ]
    }
    
    # Initialize the Reasoning Engine
    model_name = settings.LLM_MODEL
    logger.info(f"Using model: {model_name}")
    
    reasoning_engine = ReasoningEngine(model_name=model_name)
    
    try:
        # Initialize the engine
        await reasoning_engine.initialize()
        logger.info("Reasoning Engine initialized successfully")
        
        # Test document understanding
        logger.info("Testing document understanding...")
        understanding = await reasoning_engine.understand_document(
            document_text=document_text,
            document_layout=document_layout,
            document_type="invoice",
        )
        
        logger.info("Document understanding results:")
        logger.info(json.dumps(understanding, indent=2))
        
        # Test field extraction
        logger.info("Testing field extraction...")
        fields_to_extract = [
            {"name": "invoice_number", "type": "string"},
            {"name": "date", "type": "date"},
            {"name": "total_amount", "type": "currency"},
        ]
        
        extracted_fields = await reasoning_engine.extract_fields(
            document_text=document_text,
            document_layout=document_layout,
            fields_to_extract=fields_to_extract,
        )
        
        logger.info("Field extraction results:")
        logger.info(json.dumps(extracted_fields, indent=2))
        
        # Shutdown the engine
        await reasoning_engine.shutdown()
        logger.info("Reasoning Engine shut down successfully")
        
    except Exception as e:
        logger.error(f"Error testing Reasoning Engine: {e}")
        logger.error("Please check your model configuration and files.")
    
    logger.info("Reasoning Engine test complete.")


if __name__ == "__main__":
    asyncio.run(test_reasoning_engine())
