"""
PDF text extractor for the Clary AI API.

This module provides PDF text extraction capabilities using Marker.
"""

import logging
import os
from typing import Any, Dict, List, Optional

import marker
from marker.convert import convert_pdf_to_text
from marker.models import load_model

# Configure logging
logger = logging.getLogger(__name__)


class PDFExtractor:
    """
    PDF extractor for extracting text from PDF documents.
    
    This class provides methods for extracting text from PDFs using Marker.
    """
    
    def __init__(self, model_name: str = "marker-base"):
        """
        Initialize the PDF extractor.
        
        Args:
            model_name: Name of the Marker model to use.
        """
        self.model_name = model_name
        self.model = None
        logger.info(f"Initialized PDF extractor with model: {model_name}")
    
    async def process(self, document_path: str) -> Dict[str, Any]:
        """
        Process a PDF document and extract text.
        
        Args:
            document_path: Path to the PDF file.
            
        Returns:
            Dict[str, Any]: The extraction results.
        """
        logger.info(f"Extracting text from PDF: {document_path}")
        
        # Check file extension
        _, ext = os.path.splitext(document_path)
        ext = ext.lower()
        
        if ext != ".pdf":
            raise ValueError(f"Expected PDF file, got: {ext}")
        
        try:
            # Load model if not already loaded
            if self.model is None:
                self.model = load_model(self.model_name)
            
            # Extract text using Marker
            text_by_page = convert_pdf_to_text(
                document_path,
                model=self.model,
                return_pages=True
            )
            
            # Process the extracted text
            return self._process_extracted_text(text_by_page, document_path)
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def _process_extracted_text(
        self, 
        text_by_page: List[str], 
        document_path: str
    ) -> Dict[str, Any]:
        """
        Process the text extracted by Marker.
        
        Args:
            text_by_page: List of text extracted from each page.
            document_path: Path to the PDF file.
            
        Returns:
            Dict[str, Any]: The extraction results.
        """
        # Combine all text
        full_text = "\n\n".join(text_by_page)
        
        # Create pages structure
        pages = []
        for i, page_text in enumerate(text_by_page):
            # Simple line-based structure
            lines = page_text.split("\n")
            words = []
            
            # Create a simple word-level representation
            for line in lines:
                line_words = line.split()
                for word in line_words:
                    words.append({
                        "text": word,
                        # Note: Marker doesn't provide bounding boxes,
                        # so we're not including them here
                    })
            
            pages.append({
                "text": page_text,
                "page": i + 1,
                "lines": lines,
                "words": words
            })
        
        # Create result dictionary
        result = {
            "text": full_text,
            "pages": pages,
            "num_pages": len(pages),
            "extraction_method": f"marker-{self.model_name}"
        }
        
        return result
