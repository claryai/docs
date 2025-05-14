"""
Workflow service for the Clary AI API.

This module provides services for managing document processing workflows.
"""

import datetime
import logging
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.document import Document
from app.models.workflow import Workflow, Task, TaskStatus, TaskType
from app.ml.agents.workflow_executor import WorkflowExecutor


# Configure logging
logger = logging.getLogger(__name__)


async def create_workflow(
    document_id: str,
    template_id: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    db: Optional[Session] = None,
) -> str:
    """
    Create a document processing workflow.

    Args:
        document_id: ID of the document to process.
        template_id: Optional ID of extraction template to apply.
        options: Optional processing options.
        db: Optional database session.

    Returns:
        str: ID of the created workflow.
    """
    logger.info(f"Creating workflow for document: {document_id}")

    # Get database session
    if db is None:
        db = next(get_db())

    try:
        # Get document
        document = db.query(Document).filter(Document.document_id == document_id).first()
        if not document:
            raise ValueError(f"Document not found: {document_id}")

        # Create workflow
        workflow_id = f"wf_{uuid.uuid4().hex[:10]}"
        workflow = Workflow(
            id=workflow_id,
            document_id=document_id,
            status=TaskStatus.PENDING,
            template_id=template_id,
            options=options or {},
        )

        # Add workflow to database
        db.add(workflow)
        db.commit()
        db.refresh(workflow)

        # Create tasks
        tasks = _create_tasks(workflow_id, document.file_path, template_id, options)

        # Add tasks to database
        for task in tasks:
            db.add(task)

        # Create task dependencies
        _create_task_dependencies(tasks, db)

        # Commit changes
        db.commit()

        # Update document status
        document.status = "processing"
        document.job_id = workflow_id
        db.commit()

        logger.info(f"Created workflow: {workflow_id}")
        return workflow_id

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating workflow: {e}")
        raise

    finally:
        if db is not None:
            db.close()


def _create_tasks(
    workflow_id: str,
    document_path: str,
    template_id: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
) -> List[Task]:
    """
    Create tasks for a workflow.

    Args:
        workflow_id: ID of the workflow.
        document_path: Path to the document file.
        template_id: Optional ID of extraction template to apply.
        options: Optional processing options.

    Returns:
        List[Task]: List of created tasks.
    """
    tasks = []

    # Preprocess task
    preprocess_task = Task(
        id=f"{workflow_id}_preprocess",
        workflow_id=workflow_id,
        task_type=TaskType.PREPROCESS,
        status=TaskStatus.PENDING,
        params={"document_path": document_path},
        priority=10,
    )
    tasks.append(preprocess_task)

    # Extract text task
    extract_text_task = Task(
        id=f"{workflow_id}_extract_text",
        workflow_id=workflow_id,
        task_type=TaskType.EXTRACT_TEXT,
        status=TaskStatus.PENDING,
        params={"document_path": document_path},
        priority=20,
    )
    tasks.append(extract_text_task)

    # Analyze layout task
    analyze_layout_task = Task(
        id=f"{workflow_id}_analyze_layout",
        workflow_id=workflow_id,
        task_type=TaskType.ANALYZE_LAYOUT,
        status=TaskStatus.PENDING,
        params={"document_path": document_path},
        priority=30,
    )
    tasks.append(analyze_layout_task)

    # Understand document task
    understand_document_task = Task(
        id=f"{workflow_id}_understand_document",
        workflow_id=workflow_id,
        task_type=TaskType.UNDERSTAND_DOCUMENT,
        status=TaskStatus.PENDING,
        params={
            "document_path": document_path,
            "template_id": template_id,
        },
        priority=40,
    )
    tasks.append(understand_document_task)

    # Extract fields task
    extract_fields_task = Task(
        id=f"{workflow_id}_extract_fields",
        workflow_id=workflow_id,
        task_type=TaskType.EXTRACT_FIELDS,
        status=TaskStatus.PENDING,
        params={
            "document_path": document_path,
            "template_id": template_id,
        },
        priority=50,
    )
    tasks.append(extract_fields_task)

    # Extract tables task
    extract_tables_task = Task(
        id=f"{workflow_id}_extract_tables",
        workflow_id=workflow_id,
        task_type=TaskType.EXTRACT_TABLES,
        status=TaskStatus.PENDING,
        params={
            "document_path": document_path,
            "template_id": template_id,
        },
        priority=50,
    )
    tasks.append(extract_tables_task)

    # Validate results task
    validate_results_task = Task(
        id=f"{workflow_id}_validate_results",
        workflow_id=workflow_id,
        task_type=TaskType.VALIDATE_RESULTS,
        status=TaskStatus.PENDING,
        params={},
        priority=60,
    )
    tasks.append(validate_results_task)

    # Postprocess task
    postprocess_task = Task(
        id=f"{workflow_id}_postprocess",
        workflow_id=workflow_id,
        task_type=TaskType.POSTPROCESS,
        status=TaskStatus.PENDING,
        params={},
        priority=70,
    )
    tasks.append(postprocess_task)

    return tasks


def _create_task_dependencies(tasks: List[Task], db: Session):
    """
    Create dependencies between tasks.

    Args:
        tasks: List of tasks.
        db: Database session.
    """
    from app.models.workflow import TaskDependency

    # Create a dictionary of tasks by ID
    tasks_by_id = {task.id: task for task in tasks}

    # Define dependencies
    dependencies = [
        # Extract text depends on preprocess
        (f"{tasks[0].workflow_id}_extract_text", f"{tasks[0].workflow_id}_preprocess"),

        # Analyze layout depends on extract text
        (f"{tasks[0].workflow_id}_analyze_layout", f"{tasks[0].workflow_id}_extract_text"),

        # Understand document depends on analyze layout
        (f"{tasks[0].workflow_id}_understand_document", f"{tasks[0].workflow_id}_analyze_layout"),

        # Extract fields depends on understand document
        (f"{tasks[0].workflow_id}_extract_fields", f"{tasks[0].workflow_id}_understand_document"),

        # Extract tables depends on understand document
        (f"{tasks[0].workflow_id}_extract_tables", f"{tasks[0].workflow_id}_understand_document"),

        # Validate results depends on extract fields and extract tables
        (f"{tasks[0].workflow_id}_validate_results", f"{tasks[0].workflow_id}_extract_fields"),
        (f"{tasks[0].workflow_id}_validate_results", f"{tasks[0].workflow_id}_extract_tables"),

        # Postprocess depends on validate results
        (f"{tasks[0].workflow_id}_postprocess", f"{tasks[0].workflow_id}_validate_results"),
    ]

    # Create dependencies
    for dependent_id, dependency_id in dependencies:
        dependency = TaskDependency(
            dependent_task_id=dependent_id,
            dependency_task_id=dependency_id,
        )
        db.add(dependency)


async def execute_workflow(
    workflow_id: str,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Execute a document processing workflow.

    Args:
        workflow_id: ID of the workflow to execute.
        db: Optional database session.

    Returns:
        Dict[str, Any]: Workflow execution results.
    """
    logger.info(f"Executing workflow: {workflow_id}")

    # Get database session
    if db is None:
        db = next(get_db())

    # Create workflow executor
    executor = WorkflowExecutor(db_session=db)

    try:
        # Get workflow
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")

        # Execute workflow
        result = await executor.execute_workflow(workflow_id)

        logger.info(f"Workflow executed: {workflow_id}")
        return result

    except Exception as e:
        logger.error(f"Error executing workflow: {e}")

        # Update workflow status
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if workflow:
            workflow.status = TaskStatus.FAILED
            workflow.error = str(e)
            workflow.updated_at = datetime.datetime.now(datetime.timezone.utc)
            db.commit()

        raise

    finally:
        # Shutdown executor
        await executor.shutdown()

        # Close database session
        if db is not None:
            db.close()


async def get_workflow_status(
    workflow_id: str,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Get the status of a workflow.

    Args:
        workflow_id: ID of the workflow.
        db: Optional database session.

    Returns:
        Dict[str, Any]: Workflow status.
    """
    logger.info(f"Getting status for workflow: {workflow_id}")

    # Get database session
    if db is None:
        db = next(get_db())

    try:
        # Get workflow
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            return {
                "workflow_id": workflow_id,
                "status": "not_found",
            }

        # Get task counts
        task_counts = {
            "total": len(workflow.tasks),
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
        }

        for task in workflow.tasks:
            if task.status == TaskStatus.PENDING:
                task_counts["pending"] += 1
            elif task.status == TaskStatus.RUNNING:
                task_counts["running"] += 1
            elif task.status == TaskStatus.COMPLETED:
                task_counts["completed"] += 1
            elif task.status == TaskStatus.FAILED:
                task_counts["failed"] += 1

        # Calculate progress
        progress = 0
        if task_counts["total"] > 0:
            progress = (task_counts["completed"] / task_counts["total"]) * 100

        return {
            "workflow_id": workflow_id,
            "document_id": workflow.document_id,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
            "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "error": workflow.error,
            "task_counts": task_counts,
            "progress": progress,
        }

    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        return {
            "workflow_id": workflow_id,
            "status": "error",
            "error": str(e),
        }

    finally:
        if db is not None:
            db.close()
