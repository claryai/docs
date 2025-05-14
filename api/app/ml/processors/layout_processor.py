"""
Layout processor for the DocuAgent API.

This module provides layout analysis capabilities.
"""

import logging
import os
from typing import Any, Dict, List, Optional

import numpy as np
from PIL import Image


# Configure logging
logger = logging.getLogger(__name__)


class LayoutProcessor:
    """
    Layout processor for analyzing document structure.
    
    This class provides methods for analyzing document layout.
    """
    
    def __init__(self, model_name: str = "layoutlm"):
        """
        Initialize the layout processor.
        
        Args:
            model_name: Name of the layout model to use.
        """
        self.model_name = model_name
        logger.info(f"Initialized layout processor with model: {model_name}")
    
    async def process(
        self, 
        document_path: str, 
        ocr_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a document and analyze layout.
        
        Args:
            document_path: Path to the document file.
            ocr_result: OCR results from OCRProcessor.
            
        Returns:
            Dict[str, Any]: The layout analysis results.
        """
        logger.info(f"Analyzing layout of document: {document_path}")
        
        # In a real implementation, use LayoutLM or similar model
        # For now, implement a simple layout analysis based on OCR results
        
        # Check if document has pages
        if "pages" in ocr_result:
            # Process each page
            pages = []
            for page in ocr_result["pages"]:
                page_result = await self._analyze_page(page)
                pages.append(page_result)
            
            return {
                "blocks": [block for page in pages for block in page["blocks"]],
                "pages": pages,
            }
        else:
            # Process single page
            return await self._analyze_page(ocr_result)
    
    async def _analyze_page(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the layout of a page.
        
        Args:
            page: OCR results for a page.
            
        Returns:
            Dict[str, Any]: The layout analysis results.
        """
        # Extract words from OCR result
        words = page.get("words", [])
        
        # Group words into lines based on vertical position
        lines = self._group_words_into_lines(words)
        
        # Group lines into blocks based on spacing
        blocks = self._group_lines_into_blocks(lines)
        
        # Classify blocks (header, paragraph, list, table, etc.)
        blocks = self._classify_blocks(blocks)
        
        return {
            "blocks": blocks,
            "page": page.get("page", 1),
        }
    
    def _group_words_into_lines(self, words: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group words into lines based on vertical position.
        
        Args:
            words: List of words with bounding boxes.
            
        Returns:
            List[Dict[str, Any]]: List of lines.
        """
        if not words:
            return []
        
        # Sort words by top position and then by left position
        sorted_words = sorted(words, key=lambda w: (w["bbox"]["top"], w["bbox"]["left"]))
        
        lines = []
        current_line = [sorted_words[0]]
        current_top = sorted_words[0]["bbox"]["top"]
        
        for word in sorted_words[1:]:
            # If word is on the same line (within threshold)
            if abs(word["bbox"]["top"] - current_top) < 10:
                current_line.append(word)
            else:
                # Start a new line
                lines.append({
                    "words": current_line,
                    "text": " ".join(w["text"] for w in current_line),
                    "bbox": self._merge_bboxes([w["bbox"] for w in current_line]),
                })
                current_line = [word]
                current_top = word["bbox"]["top"]
        
        # Add the last line
        if current_line:
            lines.append({
                "words": current_line,
                "text": " ".join(w["text"] for w in current_line),
                "bbox": self._merge_bboxes([w["bbox"] for w in current_line]),
            })
        
        return lines
    
    def _group_lines_into_blocks(self, lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group lines into blocks based on spacing.
        
        Args:
            lines: List of lines.
            
        Returns:
            List[Dict[str, Any]]: List of blocks.
        """
        if not lines:
            return []
        
        blocks = []
        current_block = [lines[0]]
        current_bottom = lines[0]["bbox"]["top"] + lines[0]["bbox"]["height"]
        
        for line in lines[1:]:
            # If line is close to the previous line
            if line["bbox"]["top"] - current_bottom < 20:
                current_block.append(line)
            else:
                # Start a new block
                blocks.append({
                    "lines": current_block,
                    "text": "\n".join(l["text"] for l in current_block),
                    "bbox": self._merge_bboxes([l["bbox"] for l in current_block]),
                })
                current_block = [line]
            
            current_bottom = line["bbox"]["top"] + line["bbox"]["height"]
        
        # Add the last block
        if current_block:
            blocks.append({
                "lines": current_block,
                "text": "\n".join(l["text"] for l in current_block),
                "bbox": self._merge_bboxes([l["bbox"] for l in current_block]),
            })
        
        return blocks
    
    def _classify_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Classify blocks (header, paragraph, list, table, etc.).
        
        Args:
            blocks: List of blocks.
            
        Returns:
            List[Dict[str, Any]]: List of classified blocks.
        """
        classified_blocks = []
        
        for block in blocks:
            # Simple classification based on heuristics
            # In a real implementation, use a more sophisticated approach
            
            text = block["text"]
            lines = block["lines"]
            
            # Check if it's a header
            if len(lines) == 1 and len(text) < 100:
                block_type = "Header"
            # Check if it's a table (contains multiple tabs or spaces)
            elif any("\t" in line["text"] or "    " in line["text"] for line in lines):
                block_type = "Table"
            # Check if it's a list
            elif any(line["text"].strip().startswith(("•", "-", "*", "1.", "2.")) for line in lines):
                block_type = "List"
            # Default to paragraph
            else:
                block_type = "Paragraph"
            
            classified_blocks.append({
                **block,
                "type": block_type,
            })
        
        return classified_blocks
    
    def _merge_bboxes(self, bboxes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple bounding boxes into one.
        
        Args:
            bboxes: List of bounding boxes.
            
        Returns:
            Dict[str, Any]: Merged bounding box.
        """
        if not bboxes:
            return {"left": 0, "top": 0, "width": 0, "height": 0, "page": 1}
        
        left = min(bbox["left"] for bbox in bboxes)
        top = min(bbox["top"] for bbox in bboxes)
        right = max(bbox["left"] + bbox["width"] for bbox in bboxes)
        bottom = max(bbox["top"] + bbox["height"] for bbox in bboxes)
        page = bboxes[0]["page"]
        
        return {
            "left": left,
            "top": top,
            "width": right - left,
            "height": bottom - top,
            "page": page,
        }
