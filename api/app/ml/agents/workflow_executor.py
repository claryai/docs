"""
Workflow executor for the Clary AI API.

This module provides workflow execution capabilities for document processing.
"""

import asyncio
import datetime
import json
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.workflow import Workflow, Task, TaskStatus, TaskType
from app.models.template import Template
from app.ml.processors.document_preprocessor import DocumentPreprocessor
from app.ml.processors.pdf_extractor import PDFExtractor
from app.ml.processors.ocr_processor import OCRProcessor
from app.ml.processors.layout_processor import LayoutProcessor
from app.ml.agents.reasoning_engine import ReasoningEngine


# Configure logging
logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """
    Workflow executor for document processing.

    This class executes document processing workflows.
    """

    def __init__(self, db_session: Session, max_concurrency: int = 4):
        """
        Initialize the workflow executor.

        Args:
            db_session: Database session.
            max_concurrency: Maximum number of concurrent tasks.
        """
        self.db_session = db_session
        self.max_concurrency = max_concurrency

        # Initialize reasoning engine
        from app.core.config import settings
        self.reasoning_engine = ReasoningEngine(model_name=settings.LLM_MODEL)

        # Initialize task executors
        self.task_executors = {
            TaskType.PREPROCESS: self._execute_preprocess_task,
            TaskType.EXTRACT_TEXT: self._execute_extract_text_task,
            TaskType.ANALYZE_LAYOUT: self._execute_analyze_layout_task,
            TaskType.UNDERSTAND_DOCUMENT: self._execute_understand_document_task,
            TaskType.EXTRACT_FIELDS: self._execute_extract_fields_task,
            TaskType.EXTRACT_TABLES: self._execute_extract_tables_task,
            TaskType.VALIDATE_RESULTS: self._execute_validate_results_task,
            TaskType.POSTPROCESS: self._execute_postprocess_task,
        }

        logger.info(f"Initialized workflow executor with max concurrency: {max_concurrency}")

    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a document processing workflow.

        Args:
            workflow_id: ID of the workflow to execute.

        Returns:
            Dict[str, Any]: Workflow execution results.
        """
        logger.info(f"Executing workflow: {workflow_id}")

        # Get workflow from database
        workflow = self.db_session.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")

        # Update workflow status
        workflow.status = TaskStatus.RUNNING
        workflow.updated_at = datetime.datetime.now(datetime.timezone.utc)
        self.db_session.commit()

        try:
            # Get tasks in execution order
            tasks = self._get_execution_order(workflow)

            # Execute tasks with proper concurrency control
            semaphore = asyncio.Semaphore(self.max_concurrency)
            execution_tasks = []

            for task in tasks:
                execution_tasks.append(
                    self._execute_task_with_semaphore(semaphore, task)
                )

            # Wait for all tasks to complete
            await asyncio.gather(*execution_tasks)

            # Update workflow status
            workflow.status = TaskStatus.COMPLETED
            workflow.completed_at = datetime.datetime.now(datetime.timezone.utc)
            self.db_session.commit()

            # Return workflow results
            return self._get_workflow_results(workflow)

        except Exception as e:
            # Update workflow status
            workflow.status = TaskStatus.FAILED
            workflow.error = str(e)
            workflow.updated_at = datetime.datetime.now(datetime.timezone.utc)
            self.db_session.commit()

            logger.error(f"Error executing workflow: {e}")
            raise

    def _get_execution_order(self, workflow: Workflow) -> List[Task]:
        """
        Get tasks in execution order using topological sort.

        Args:
            workflow: Workflow containing tasks.

        Returns:
            List[Task]: Tasks in execution order.
        """
        # Build dependency graph
        tasks_by_id = {task.id: task for task in workflow.tasks}
        dependencies = {task.id: set() for task in workflow.tasks}

        for task in workflow.tasks:
            for dependency in task.dependencies:
                dependencies[task.id].add(dependency.dependency_task_id)

        # Topological sort
        visited = set()
        temp_visited = set()
        order = []

        def visit(task_id: str):
            if task_id in temp_visited:
                raise ValueError("Circular dependency detected in workflow tasks")
            if task_id in visited:
                return

            temp_visited.add(task_id)

            for dep_id in dependencies[task_id]:
                visit(dep_id)

            temp_visited.remove(task_id)
            visited.add(task_id)
            order.append(tasks_by_id[task_id])

        for task_id in tasks_by_id:
            if task_id not in visited:
                visit(task_id)

        # Reverse to get correct execution order
        return list(reversed(order))

    async def _execute_task_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        task: Task
    ) -> None:
        """
        Execute a task with semaphore for concurrency control.

        Args:
            semaphore: Semaphore for concurrency control.
            task: Task to execute.
        """
        async with semaphore:
            await self._execute_task(task)

    async def _execute_task(self, task: Task) -> None:
        """
        Execute a task.

        Args:
            task: Task to execute.
        """
        logger.info(f"Executing task: {task.id} ({task.task_type})")

        # Check if task can be executed
        if not task.can_execute():
            logger.warning(f"Task cannot be executed: {task.id}")
            return

        # Update task status
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.datetime.now(datetime.timezone.utc)
        self.db_session.commit()

        try:
            # Execute task based on type
            executor = self.task_executors.get(task.task_type)
            if not executor:
                raise ValueError(f"No executor found for task type: {task.task_type}")

            result = await executor(task)

            # Update task with result
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.datetime.now(datetime.timezone.utc)
            self.db_session.commit()

            logger.info(f"Task completed: {task.id}")

        except Exception as e:
            # Update task status
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.updated_at = datetime.datetime.now(datetime.timezone.utc)
            self.db_session.commit()

            logger.error(f"Error executing task: {task.id} - {e}")
            raise

    async def _execute_preprocess_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a document preprocessing task.

        Args:
            task: Task to execute.

        Returns:
            Dict[str, Any]: Task execution results.
        """
        # Get document path from task parameters
        document_path = task.params.get("document_path")
        if not document_path:
            raise ValueError("Document path not specified in task parameters")

        # Initialize document preprocessor
        document_preprocessor = DocumentPreprocessor()

        # Process document
        preprocess_result = await document_preprocessor.process(document_path)

        # Validate result
        if not preprocess_result or "text" not in preprocess_result:
            raise ValueError("Invalid preprocessing result: missing text")

        return preprocess_result

    async def _execute_extract_text_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a text extraction task.

        Args:
            task: Task to execute.

        Returns:
            Dict[str, Any]: Task execution results.
        """
        # Get document path from task parameters
        document_path = task.params.get("document_path")
        if not document_path:
            raise ValueError("Document path not specified in task parameters")

        # Get preprocess result from dependency
        preprocess_task = self._get_dependency_task(task, TaskType.PREPROCESS)
        if not preprocess_task or not preprocess_task.result:
            raise ValueError("Preprocess task result not found")

        preprocess_result = preprocess_task.result

        # Determine document type
        import os
        _, ext = os.path.splitext(document_path)
        ext = ext.lower()

        if ext == ".pdf":
            # Use Marker for PDF text extraction
            pdf_extractor = PDFExtractor()
            text_result = await pdf_extractor.process(document_path)
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"]:
            # Use OCR for image text extraction
            ocr_processor = OCRProcessor()
            text_result = await ocr_processor.process(document_path)
        else:
            # For other document types, use the preprocessor result
            text_result = {
                "text": preprocess_result["text"],
                "pages": [{"text": preprocess_result["text"], "page": 1}]
            }

        # Validate result
        if not text_result or "text" not in text_result:
            raise ValueError("Invalid text extraction result: missing text")

        return text_result

    async def _execute_analyze_layout_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a layout analysis task.

        Args:
            task: Task to execute.

        Returns:
            Dict[str, Any]: Task execution results.
        """
        # Get document path from task parameters
        document_path = task.params.get("document_path")
        if not document_path:
            raise ValueError("Document path not specified in task parameters")

        # Get text extraction result from dependency
        text_task = self._get_dependency_task(task, TaskType.EXTRACT_TEXT)
        if not text_task or not text_task.result:
            raise ValueError("Text extraction task result not found")

        text_result = text_task.result

        # Initialize layout processor
        layout_processor = LayoutProcessor()

        # Process document
        layout_result = await layout_processor.process(document_path, text_result)

        # Validate result
        if not layout_result:
            raise ValueError("Invalid layout analysis result")

        # Get preprocess result from dependency
        preprocess_task = self._get_dependency_task(task, TaskType.PREPROCESS)
        if not preprocess_task or not preprocess_task.result:
            raise ValueError("Preprocess task result not found")

        preprocess_result = preprocess_task.result

        # Enhance layout result with preprocessor information
        enhanced_layout = {
            **layout_result,
            "document_type": preprocess_result.get("document_type", "unknown"),
            "structure": preprocess_result.get("structure", {}),
            "elements": preprocess_result.get("elements", [])
        }

        return enhanced_layout

    async def _execute_understand_document_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a document understanding task.

        Args:
            task: Task to execute.

        Returns:
            Dict[str, Any]: Task execution results.
        """
        # Get document path and template ID from task parameters
        document_path = task.params.get("document_path")
        template_id = task.params.get("template_id")

        if not document_path:
            raise ValueError("Document path not specified in task parameters")

        # Get layout analysis result from dependency
        layout_task = self._get_dependency_task(task, TaskType.ANALYZE_LAYOUT)
        if not layout_task or not layout_task.result:
            raise ValueError("Layout analysis task result not found")

        layout_result = layout_task.result

        # Get text extraction result from dependency
        text_task = self._get_dependency_task(task, TaskType.EXTRACT_TEXT)
        if not text_task or not text_task.result:
            raise ValueError("Text extraction task result not found")

        text_result = text_task.result

        try:
            # Initialize reasoning engine
            await self.reasoning_engine.initialize()

            # Understand document
            understanding_result = await self.reasoning_engine.understand_document(
                document_text=text_result.get("text", ""),
                document_layout=layout_result,
                document_type=layout_result.get("document_type"),
            )

            # Validate result
            if not understanding_result:
                raise ValueError("Invalid document understanding result")

            # Add template information if available
            if template_id:
                understanding_result["template_id"] = template_id

            return understanding_result
        except Exception as e:
            logger.error(f"Error in document understanding: {e}")
            raise

    async def _execute_extract_fields_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a field extraction task.

        Args:
            task: Task to execute.

        Returns:
            Dict[str, Any]: Task execution results.
        """
        # Get document path and template ID from task parameters
        document_path = task.params.get("document_path")
        template_id = task.params.get("template_id")

        if not document_path:
            raise ValueError("Document path not specified in task parameters")

        # Get document understanding result from dependency
        understanding_task = self._get_dependency_task(task, TaskType.UNDERSTAND_DOCUMENT)
        if not understanding_task or not understanding_task.result:
            raise ValueError("Document understanding task result not found")

        understanding_result = understanding_task.result

        # Get layout analysis result from dependency
        layout_task = self._get_dependency_task(task, TaskType.ANALYZE_LAYOUT)
        if not layout_task or not layout_task.result:
            raise ValueError("Layout analysis task result not found")

        layout_result = layout_task.result

        # Get text extraction result from dependency
        text_task = self._get_dependency_task(task, TaskType.EXTRACT_TEXT)
        if not text_task or not text_task.result:
            raise ValueError("Text extraction task result not found")

        text_result = text_task.result

        # Determine fields to extract based on document type and template
        fields_to_extract = await self._get_fields_to_extract(
            understanding_result, template_id
        )

        try:
            # Initialize reasoning engine
            await self.reasoning_engine.initialize()

            # Extract fields
            extraction_result = await self.reasoning_engine.extract_fields(
                document_text=text_result.get("text", ""),
                document_layout=layout_result,
                fields_to_extract=fields_to_extract,
            )

            # Validate result
            if not extraction_result:
                raise ValueError("Invalid field extraction result")

            return extraction_result
        except Exception as e:
            logger.error(f"Error in field extraction: {e}")
            raise

    async def _execute_extract_tables_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a table extraction task.

        Args:
            task: Task to execute.

        Returns:
            Dict[str, Any]: Task execution results.
        """
        # Get document path and template ID from task parameters
        document_path = task.params.get("document_path")
        template_id = task.params.get("template_id")

        if not document_path:
            raise ValueError("Document path not specified in task parameters")

        # Get document understanding result from dependency
        understanding_task = self._get_dependency_task(task, TaskType.UNDERSTAND_DOCUMENT)
        if not understanding_task or not understanding_task.result:
            raise ValueError("Document understanding task result not found")

        understanding_result = understanding_task.result

        # Get layout analysis result from dependency
        layout_task = self._get_dependency_task(task, TaskType.ANALYZE_LAYOUT)
        if not layout_task or not layout_task.result:
            raise ValueError("Layout analysis task result not found")

        layout_result = layout_task.result

        # Get text extraction result from dependency
        text_task = self._get_dependency_task(task, TaskType.EXTRACT_TEXT)
        if not text_task or not text_task.result:
            raise ValueError("Text extraction task result not found")

        text_result = text_task.result

        # Determine tables to extract based on document type and template
        tables_to_extract = await self._get_tables_to_extract(
            understanding_result, template_id
        )

        # If no tables to extract, return empty result
        if not tables_to_extract:
            return {}

        try:
            # Initialize reasoning engine
            await self.reasoning_engine.initialize()

            # Extract tables
            extraction_result = await self.reasoning_engine.extract_tables(
                document_text=text_result.get("text", ""),
                document_layout=layout_result,
                tables_to_extract=tables_to_extract,
            )

            # Validate result
            if extraction_result is None:
                raise ValueError("Invalid table extraction result")

            return extraction_result
        except Exception as e:
            logger.error(f"Error in table extraction: {e}")
            raise

    async def _execute_validate_results_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a result validation task.

        Args:
            task: Task to execute.

        Returns:
            Dict[str, Any]: Task execution results.
        """
        # Get field extraction result from dependency
        fields_task = self._get_dependency_task(task, TaskType.EXTRACT_FIELDS)
        if not fields_task or not fields_task.result:
            raise ValueError("Field extraction task result not found")

        fields_result = fields_task.result

        # Get table extraction result from dependency
        tables_task = self._get_dependency_task(task, TaskType.EXTRACT_TABLES)
        if not tables_task or not tables_task.result:
            raise ValueError("Table extraction task result not found")

        tables_result = tables_task.result

        # Get document understanding result from dependency
        understanding_task = self._get_dependency_task(task, TaskType.UNDERSTAND_DOCUMENT)
        if not understanding_task or not understanding_task.result:
            raise ValueError("Document understanding task result not found")

        understanding_result = understanding_task.result

        # Get text extraction result from dependency
        text_task = self._get_dependency_task(task, TaskType.EXTRACT_TEXT)
        if not text_task or not text_task.result:
            raise ValueError("Text extraction task result not found")

        text_result = text_task.result

        try:
            # Initialize reasoning engine
            await self.reasoning_engine.initialize()

            # Validate extraction results using reasoning engine
            validation_result = await self.reasoning_engine.validate_extraction(
                document_text=text_result.get("text", ""),
                extracted_fields=fields_result,
                extracted_tables=tables_result,
            )

            # If validation fails, fall back to basic validation
            if not validation_result:
                validation_result = await self._validate_extraction_results(
                    fields_result, tables_result, understanding_result
                )

            # Combine results
            combined_result = {
                "document_type": understanding_result.get("document_type", "unknown"),
                "fields": fields_result,
                "tables": tables_result,
                "validation": validation_result,
                "confidence": self._calculate_confidence(fields_result, tables_result),
            }

            return combined_result
        except Exception as e:
            logger.error(f"Error in validation: {e}")

            # Fall back to basic validation
            validation_result = await self._validate_extraction_results(
                fields_result, tables_result, understanding_result
            )

            # Combine results
            combined_result = {
                "document_type": understanding_result.get("document_type", "unknown"),
                "fields": fields_result,
                "tables": tables_result,
                "validation": validation_result,
                "confidence": self._calculate_confidence(fields_result, tables_result),
            }

            return combined_result

    async def _execute_postprocess_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a postprocessing task.

        Args:
            task: Task to execute.

        Returns:
            Dict[str, Any]: Task execution results.
        """
        # Get validation result from dependency
        validation_task = self._get_dependency_task(task, TaskType.VALIDATE_RESULTS)
        if not validation_task or not validation_task.result:
            raise ValueError("Validation task result not found")

        validation_result = validation_task.result

        # Format results for output
        formatted_result = self._format_extraction_results(validation_result)

        # Get workflow
        workflow = task.workflow

        # Update document with extraction results
        if workflow.document:
            workflow.document.extraction_results_json = json.dumps(formatted_result)
            workflow.document.extraction_status = "success"
            workflow.document.status = "completed"
            workflow.document.completed_at = datetime.datetime.now(datetime.timezone.utc)
            self.db_session.commit()

        return formatted_result

    def _get_dependency_task(self, task: Task, task_type: TaskType) -> Optional[Task]:
        """
        Get a dependency task of a specific type.

        Args:
            task: Task to get dependency for.
            task_type: Type of dependency task to get.

        Returns:
            Optional[Task]: Dependency task of the specified type, or None if not found.
        """
        for dependency in task.dependencies:
            if dependency.dependency_task.task_type == task_type:
                return dependency.dependency_task

        return None

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
        # If template ID is provided, get fields from template
        if template_id:
            template = self.db_session.query(Template).filter(Template.id == template_id).first()
            if template and template.fields:
                try:
                    return json.loads(template.fields)
                except json.JSONDecodeError:
                    pass

        # Otherwise, determine fields based on document type
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
        elif document_type == "receipt":
            return [
                {"name": "receipt_number", "type": "string", "required": False},
                {"name": "date", "type": "date", "required": True},
                {"name": "total_amount", "type": "currency", "required": True},
                {"name": "tax_amount", "type": "currency", "required": False},
                {"name": "merchant_name", "type": "string", "required": True},
                {"name": "merchant_address", "type": "string", "required": False},
                {"name": "payment_method", "type": "string", "required": False},
            ]
        elif document_type == "contract":
            return [
                {"name": "contract_number", "type": "string", "required": False},
                {"name": "date", "type": "date", "required": True},
                {"name": "effective_date", "type": "date", "required": False},
                {"name": "expiration_date", "type": "date", "required": False},
                {"name": "party_1", "type": "string", "required": True},
                {"name": "party_2", "type": "string", "required": True},
                {"name": "contract_type", "type": "string", "required": False},
                {"name": "contract_value", "type": "currency", "required": False},
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
        # If template ID is provided, get tables from template
        if template_id:
            template = self.db_session.query(Template).filter(Template.id == template_id).first()
            if template and template.tables:
                try:
                    return json.loads(template.tables)
                except json.JSONDecodeError:
                    pass

        # Otherwise, determine tables based on document type
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
        elif document_type == "receipt":
            return [
                {
                    "name": "items",
                    "required": True,
                    "columns": [
                        {"name": "description", "type": "string"},
                        {"name": "quantity", "type": "number"},
                        {"name": "price", "type": "currency"},
                    ],
                }
            ]
        else:
            # Check if document understanding identified any tables
            tables = document_understanding.get("tables", [])
            if tables:
                return [
                    {
                        "name": table.get("name", f"table_{i}"),
                        "required": False,
                        "columns": [
                            {"name": col, "type": "string"}
                            for col in table.get("columns", [])
                        ],
                    }
                    for i, table in enumerate(tables)
                ]

            # No tables for generic documents
            return []

    async def _validate_extraction_results(
        self,
        fields_result: Dict[str, Any],
        tables_result: Dict[str, Any],
        understanding_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate extraction results.

        Args:
            fields_result: Field extraction results.
            tables_result: Table extraction results.
            understanding_result: Document understanding results.

        Returns:
            Dict[str, Any]: Validation results.
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        # Validate required fields
        document_type = understanding_result.get("document_type", "unknown")
        fields_to_extract = await self._get_fields_to_extract(understanding_result)

        for field_def in fields_to_extract:
            field_name = field_def.get("name")
            required = field_def.get("required", False)

            if required and (field_name not in fields_result or not fields_result[field_name].get("value")):
                validation_result["valid"] = False
                validation_result["errors"].append(
                    f"Required field '{field_name}' is missing or empty"
                )

        # Validate required tables
        tables_to_extract = await self._get_tables_to_extract(understanding_result)

        for table_def in tables_to_extract:
            table_name = table_def.get("name")
            required = table_def.get("required", False)

            if required and (table_name not in tables_result or not tables_result[table_name].get("rows")):
                validation_result["valid"] = False
                validation_result["errors"].append(
                    f"Required table '{table_name}' is missing or empty"
                )

        # Validate field types
        for field_def in fields_to_extract:
            field_name = field_def.get("name")
            field_type = field_def.get("type", "string")

            if field_name in fields_result and fields_result[field_name].get("value"):
                value = fields_result[field_name].get("value")

                if field_type == "date" and not self._is_valid_date(value):
                    validation_result["warnings"].append(
                        f"Field '{field_name}' has invalid date format: {value}"
                    )

                elif field_type == "currency" and not self._is_valid_currency(value):
                    validation_result["warnings"].append(
                        f"Field '{field_name}' has invalid currency format: {value}"
                    )

                elif field_type == "number" and not self._is_valid_number(value):
                    validation_result["warnings"].append(
                        f"Field '{field_name}' has invalid number format: {value}"
                    )

        return validation_result

    def _is_valid_date(self, value: str) -> bool:
        """
        Check if a value is a valid date.

        Args:
            value: Value to check.

        Returns:
            bool: True if the value is a valid date, False otherwise.
        """
        import re

        # Check common date formats
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
            r"\d{2}-\d{2}-\d{4}",  # MM-DD-YYYY
            r"\d{2}\.\d{2}\.\d{4}",  # MM.DD.YYYY
        ]

        for pattern in date_patterns:
            if re.fullmatch(pattern, value):
                return True

        return False

    def _is_valid_currency(self, value: str) -> bool:
        """
        Check if a value is a valid currency.

        Args:
            value: Value to check.

        Returns:
            bool: True if the value is a valid currency, False otherwise.
        """
        import re

        # Check common currency formats
        currency_patterns = [
            r"\$\d+(\.\d{2})?",  # $123.45
            r"\d+(\.\d{2})?\s*USD",  # 123.45 USD
            r"€\d+(\.\d{2})?",  # €123.45
            r"\d+(\.\d{2})?\s*EUR",  # 123.45 EUR
            r"£\d+(\.\d{2})?",  # £123.45
            r"\d+(\.\d{2})?\s*GBP",  # 123.45 GBP
            r"\d+(\.\d{2})?",  # 123.45
        ]

        for pattern in currency_patterns:
            if re.fullmatch(pattern, value):
                return True

        return False

    def _is_valid_number(self, value: str) -> bool:
        """
        Check if a value is a valid number.

        Args:
            value: Value to check.

        Returns:
            bool: True if the value is a valid number, False otherwise.
        """
        try:
            float(value.replace(",", ""))
            return True
        except (ValueError, TypeError):
            return False

    def _calculate_confidence(
        self,
        fields_result: Dict[str, Any],
        tables_result: Dict[str, Any],
    ) -> float:
        """
        Calculate overall confidence score.

        Args:
            fields_result: Field extraction results.
            tables_result: Table extraction results.

        Returns:
            float: Overall confidence score.
        """
        # Calculate average confidence of fields
        field_confidences = [
            field.get("confidence", 0.0) for field in fields_result.values()
        ]

        # Calculate average confidence of tables
        table_confidences = [
            table.get("confidence", 0.0) for table in tables_result.values()
        ]

        # Combine confidences
        all_confidences = field_confidences + table_confidences

        if not all_confidences:
            return 0.0

        return sum(all_confidences) / len(all_confidences)

    def _format_extraction_results(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format extraction results for output.

        Args:
            validation_result: Validation results.

        Returns:
            Dict[str, Any]: Formatted extraction results.
        """
        # Get components from validation result
        document_type = validation_result.get("document_type", "unknown")
        fields = validation_result.get("fields", {})
        tables = validation_result.get("tables", {})
        validation = validation_result.get("validation", {})
        confidence = validation_result.get("confidence", 0.0)

        # Format fields
        formatted_fields = {}
        for field_name, field_data in fields.items():
            formatted_fields[field_name] = {
                "value": field_data.get("value"),
                "confidence": field_data.get("confidence", 0.0),
            }

            # Add bounding box if available
            if "bounding_box" in field_data:
                formatted_fields[field_name]["bounding_box"] = field_data["bounding_box"]

        # Format tables
        formatted_tables = {}
        for table_name, table_data in tables.items():
            formatted_tables[table_name] = {
                "headers": table_data.get("headers", []),
                "rows": table_data.get("rows", []),
                "confidence": table_data.get("confidence", 0.0),
            }

        # Create formatted result
        formatted_result = {
            "document_type": document_type,
            "fields": formatted_fields,
            "tables": formatted_tables,
            "validation": {
                "valid": validation.get("valid", True),
                "errors": validation.get("errors", []),
                "warnings": validation.get("warnings", []),
            },
            "confidence": confidence,
        }

        return formatted_result

    def _get_workflow_results(self, workflow: Workflow) -> Dict[str, Any]:
        """
        Get workflow results.

        Args:
            workflow: Workflow to get results for.

        Returns:
            Dict[str, Any]: Workflow results.
        """
        # Get postprocess task
        postprocess_task = None
        for task in workflow.tasks:
            if task.task_type == TaskType.POSTPROCESS and task.status == TaskStatus.COMPLETED:
                postprocess_task = task
                break

        if postprocess_task and postprocess_task.result:
            return postprocess_task.result

        # If postprocess task is not completed, return workflow status
        return {
            "status": workflow.status.value,
            "error": workflow.error,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
        }

    async def shutdown(self):
        """Shutdown the workflow executor and release resources."""
        logger.info("Shutting down workflow executor")

        # Shutdown reasoning engine
        if self.reasoning_engine:
            await self.reasoning_engine.shutdown()

        logger.info("Workflow executor shut down successfully")
