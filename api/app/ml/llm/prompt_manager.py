"""
Prompt manager for the Clary AI API.

This module provides prompt management for LLM models.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

from jinja2 import Template


# Configure logging
logger = logging.getLogger(__name__)


class PromptManager:
    """
    Prompt manager for managing prompt templates.
    
    This class provides methods for loading, rendering, and managing prompt templates.
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the prompt manager.
        
        Args:
            templates_dir: Directory where prompt templates are stored.
        """
        self.templates_dir = templates_dir
        self.templates = {}
        
        # Load built-in templates
        self._load_built_in_templates()
        
        # Load templates from directory if provided
        if templates_dir:
            self._load_templates_from_directory(templates_dir)
        
        logger.info(f"Initialized prompt manager with {len(self.templates)} templates")
    
    def _load_built_in_templates(self) -> None:
        """Load built-in prompt templates."""
        logger.info("Loading built-in prompt templates")
        
        # Document understanding template
        self.templates["document_understanding"] = """
You are an AI assistant that understands documents. You will be given the text and layout information of a document, and your task is to understand its structure, purpose, and key components.

Document Text:
{{ document_text }}

Document Layout Information:
{{ document_layout }}

Document Type (if known): {{ document_type }}

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
        
        # Field extraction template
        self.templates["field_extraction"] = """
You are an AI assistant that extracts information from documents. You will be given the text and layout information of a document, along with a list of fields to extract.

Document Text:
{{ document_text }}

Document Layout Information:
{{ document_layout }}

Document Understanding:
{{ document_understanding }}

Fields to Extract:
{{ fields_to_extract }}

Please extract the requested fields from the document. For each field, provide:
1. The extracted value
2. A confidence score (0.0 to 1.0)
3. The location in the document where the field was found (if available)

Provide your extraction in a structured JSON format with field names as keys, and values containing the extracted information.

JSON Response:
"""
        
        # Table extraction template
        self.templates["table_extraction"] = """
You are an AI assistant that extracts tables from documents. You will be given the text and layout information of a document, along with a list of tables to extract.

Document Text:
{{ document_text }}

Document Layout Information:
{{ document_layout }}

Document Understanding:
{{ document_understanding }}

Tables to Extract:
{{ tables_to_extract }}

Please extract the requested tables from the document. For each table, provide:
1. The table name
2. The column headers
3. The rows of data
4. A confidence score (0.0 to 1.0)

Provide your extraction in a structured JSON format with table names as keys, and values containing the extracted information.

JSON Response:
"""
        
        # Validation template
        self.templates["validation"] = """
You are an AI assistant that validates extracted information from documents. You will be given the extracted fields and tables, along with the original document text and understanding.

Document Text:
{{ document_text }}

Document Understanding:
{{ document_understanding }}

Extracted Fields:
{{ extracted_fields }}

Extracted Tables:
{{ extracted_tables }}

Please validate the extracted information and identify any issues or inconsistencies. For each issue, provide:
1. The field or table name
2. The issue description
3. A suggested correction (if possible)

Provide your validation in a structured JSON format with the following keys:
- valid (boolean)
- issues (list of issues)
- corrections (suggested corrections)

JSON Response:
"""
        
        logger.info(f"Loaded {len(self.templates)} built-in prompt templates")
    
    def _load_templates_from_directory(self, directory: str) -> None:
        """
        Load prompt templates from a directory.
        
        Args:
            directory: Directory containing prompt templates.
        """
        logger.info(f"Loading prompt templates from directory: {directory}")
        
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Load templates from directory
        for filename in os.listdir(directory):
            if filename.endswith(".txt") or filename.endswith(".j2"):
                template_name = os.path.splitext(filename)[0]
                template_path = os.path.join(directory, filename)
                
                try:
                    with open(template_path, "r") as f:
                        template_content = f.read()
                    
                    self.templates[template_name] = template_content
                    logger.info(f"Loaded template: {template_name}")
                    
                except Exception as e:
                    logger.error(f"Error loading template {template_name}: {e}")
        
        logger.info(f"Loaded {len(self.templates)} prompt templates from directory")
    
    def render_template(
        self,
        template_name: str,
        variables: Dict[str, Any],
    ) -> str:
        """
        Render a prompt template.
        
        Args:
            template_name: Name of the template to render.
            variables: Variables to use in the template.
            
        Returns:
            str: Rendered prompt.
        """
        logger.info(f"Rendering template: {template_name}")
        
        # Get template
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template_content = self.templates[template_name]
        
        # Render template
        try:
            template = Template(template_content)
            rendered = template.render(**variables)
            
            logger.info(f"Template rendered successfully: {template_name}")
            return rendered
            
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            raise
    
    def add_template(self, template_name: str, template_content: str) -> None:
        """
        Add a new prompt template.
        
        Args:
            template_name: Name of the template.
            template_content: Content of the template.
        """
        logger.info(f"Adding template: {template_name}")
        
        # Add template
        self.templates[template_name] = template_content
        
        # Save template to directory if provided
        if self.templates_dir:
            template_path = os.path.join(self.templates_dir, f"{template_name}.txt")
            
            try:
                with open(template_path, "w") as f:
                    f.write(template_content)
                
                logger.info(f"Template saved to file: {template_path}")
                
            except Exception as e:
                logger.error(f"Error saving template {template_name} to file: {e}")
        
        logger.info(f"Template added successfully: {template_name}")
    
    def get_template(self, template_name: str) -> str:
        """
        Get a prompt template.
        
        Args:
            template_name: Name of the template.
            
        Returns:
            str: Template content.
        """
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        return self.templates[template_name]
    
    def get_available_templates(self) -> List[str]:
        """
        Get list of available templates.
        
        Returns:
            List[str]: List of available template names.
        """
        return list(self.templates.keys())
    
    def format_json_for_prompt(self, data: Any) -> str:
        """
        Format data as JSON for inclusion in a prompt.
        
        Args:
            data: Data to format as JSON.
            
        Returns:
            str: Formatted JSON string.
        """
        return json.dumps(data, indent=2)
    
    def parse_json_from_response(self, response: str) -> Any:
        """
        Parse JSON from a model response.
        
        Args:
            response: Model response containing JSON.
            
        Returns:
            Any: Parsed JSON data.
        """
        # Find JSON in response
        try:
            # Try to parse the entire response as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from the response
            import re
            
            # Look for JSON objects
            json_match = re.search(r'({.*})', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # Look for JSON arrays
            json_match = re.search(r'(\[.*\])', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # If all else fails, return the raw response
            logger.warning("Could not parse JSON from response")
            return {"error": "Could not parse JSON from response", "raw_response": response}
