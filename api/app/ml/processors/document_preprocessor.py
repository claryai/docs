"""
Document preprocessor for the Clary AI API.

This module provides document preprocessing capabilities using Unstructured.io.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from unstructured.partition.auto import partition
from unstructured.documents.elements import (
    Element, Text, Title, NarrativeText, ListItem, Table
)

# Configure logging
logger = logging.getLogger(__name__)


class DocumentPreprocessor:
    """
    Document preprocessor for normalizing and preprocessing documents.
    
    This class provides methods for preprocessing documents using Unstructured.io.
    """
    
    def __init__(self):
        """Initialize the document preprocessor."""
        logger.info("Initialized document preprocessor with Unstructured.io")
    
    async def process(self, document_path: str) -> Dict[str, Any]:
        """
        Preprocess a document using Unstructured.io.
        
        Args:
            document_path: Path to the document file.
            
        Returns:
            Dict[str, Any]: The preprocessing results.
        """
        logger.info(f"Preprocessing document: {document_path}")
        
        # Check file extension
        _, ext = os.path.splitext(document_path)
        ext = ext.lower()
        
        try:
            # Use Unstructured.io to partition the document
            elements = partition(document_path)
            
            # Process the elements
            return self._process_elements(elements, document_path)
            
        except Exception as e:
            logger.error(f"Error preprocessing document: {e}")
            raise
    
    def _process_elements(
        self, 
        elements: List[Element], 
        document_path: str
    ) -> Dict[str, Any]:
        """
        Process the elements extracted by Unstructured.io.
        
        Args:
            elements: List of elements extracted by Unstructured.io.
            document_path: Path to the document file.
            
        Returns:
            Dict[str, Any]: The preprocessing results.
        """
        # Extract text from elements
        text = "\n\n".join(str(element) for element in elements)
        
        # Categorize elements
        titles = [e for e in elements if isinstance(e, Title)]
        paragraphs = [e for e in elements if isinstance(e, NarrativeText)]
        list_items = [e for e in elements if isinstance(e, ListItem)]
        tables = [e for e in elements if isinstance(e, Table)]
        
        # Create structured representation
        structured_elements = []
        for element in elements:
            element_type = type(element).__name__
            element_dict = {
                "type": element_type,
                "text": str(element),
            }
            
            # Add metadata if available
            if hasattr(element, "metadata"):
                element_dict["metadata"] = element.metadata
                
            # Add coordinates if available
            if hasattr(element, "coordinates"):
                element_dict["coordinates"] = element.coordinates
                
            structured_elements.append(element_dict)
        
        # Create result dictionary
        result = {
            "text": text,
            "elements": structured_elements,
            "document_type": self._detect_document_type(elements, document_path),
            "structure": {
                "titles": len(titles),
                "paragraphs": len(paragraphs),
                "list_items": len(list_items),
                "tables": len(tables),
            }
        }
        
        return result
    
    def _detect_document_type(
        self, 
        elements: List[Element], 
        document_path: str
    ) -> str:
        """
        Detect the document type based on content and structure.
        
        Args:
            elements: List of elements extracted by Unstructured.io.
            document_path: Path to the document file.
            
        Returns:
            str: The detected document type.
        """
        # Extract text for analysis
        text = " ".join(str(element) for element in elements).lower()
        
        # Simple heuristic-based detection
        if "invoice" in text or "bill" in text:
            return "invoice"
        elif "receipt" in text:
            return "receipt"
        elif "contract" in text or "agreement" in text:
            return "contract"
        elif "resume" in text or "cv" in text:
            return "resume"
        elif "tax" in text and ("form" in text or "return" in text):
            return "tax_form"
        else:
            return "general"
