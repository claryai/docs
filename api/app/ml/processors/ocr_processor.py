"""
OCR processor for the DocuAgent API.

This module provides OCR processing capabilities.
"""

import logging
import os
from typing import Any, Dict, List, Optional

import pytesseract
from PIL import Image
from pdf2image import convert_from_path


# Configure logging
logger = logging.getLogger(__name__)


class OCRProcessor:
    """
    OCR processor for extracting text from documents.
    
    This class provides methods for extracting text from images and PDFs.
    """
    
    def __init__(self, model_name: str = "tesseract"):
        """
        Initialize the OCR processor.
        
        Args:
            model_name: Name of the OCR model to use.
        """
        self.model_name = model_name
        logger.info(f"Initialized OCR processor with model: {model_name}")
    
    async def process(self, document_path: str) -> Dict[str, Any]:
        """
        Process a document and extract text.
        
        Args:
            document_path: Path to the document file.
            
        Returns:
            Dict[str, Any]: The OCR results.
        """
        logger.info(f"Processing document with OCR: {document_path}")
        
        # Check file extension
        _, ext = os.path.splitext(document_path)
        ext = ext.lower()
        
        if ext == ".pdf":
            return await self._process_pdf(document_path)
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"]:
            return await self._process_image(document_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    async def _process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a PDF document.
        
        Args:
            pdf_path: Path to the PDF file.
            
        Returns:
            Dict[str, Any]: The OCR results.
        """
        logger.info(f"Processing PDF: {pdf_path}")
        
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        
        # Process each page
        pages = []
        for i, image in enumerate(images):
            page_result = await self._process_pil_image(image, page_num=i+1)
            pages.append(page_result)
        
        return {
            "text": "\n\n".join(page["text"] for page in pages),
            "pages": pages,
        }
    
    async def _process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process an image document.
        
        Args:
            image_path: Path to the image file.
            
        Returns:
            Dict[str, Any]: The OCR results.
        """
        logger.info(f"Processing image: {image_path}")
        
        # Open image
        image = Image.open(image_path)
        
        # Process image
        return await self._process_pil_image(image)
    
    async def _process_pil_image(
        self, 
        image: Image.Image, 
        page_num: int = 1
    ) -> Dict[str, Any]:
        """
        Process a PIL Image.
        
        Args:
            image: PIL Image to process.
            page_num: Page number.
            
        Returns:
            Dict[str, Any]: The OCR results.
        """
        if self.model_name == "tesseract":
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image)
            
            # Extract word and line bounding boxes
            word_data = pytesseract.image_to_data(
                image, 
                output_type=pytesseract.Output.DICT
            )
            
            # Construct words with bounding boxes
            words = []
            for i in range(len(word_data["text"])):
                if word_data["text"][i].strip():
                    words.append({
                        "text": word_data["text"][i],
                        "bbox": {
                            "left": word_data["left"][i],
                            "top": word_data["top"][i],
                            "width": word_data["width"][i],
                            "height": word_data["height"][i],
                            "page": page_num,
                        },
                        "conf": word_data["conf"][i],
                    })
            
            return {
                "text": text,
                "words": words,
                "page": page_num,
            }
        
        elif self.model_name == "paddleocr":
            # In a real implementation, use PaddleOCR here
            # For now, fall back to Tesseract
            return await self._process_pil_image(image, page_num)
        
        else:
            raise ValueError(f"Unsupported OCR model: {self.model_name}")
