"""
Tests for the workflow service.

This module contains tests for the workflow service.
"""

import asyncio
import datetime
import json
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.workflow import Workflow, Task, TaskStatus, TaskType, TaskDependency
from app.services.workflow_service import (
    create_workflow,
    execute_workflow,
    get_workflow_status,
    _create_tasks,
    _create_task_dependencies,
)


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def mock_document():
    """Create a mock document."""
    document = MagicMock(spec=Document)
    document.document_id = "test_document"
    document.file_path = "test_document.pdf"
    document.status = "pending"
    document.job_id = None
    return document


@pytest.fixture
def mock_workflow():
    """Create a mock workflow."""
    workflow = MagicMock(spec=Workflow)
    workflow.id = "test_workflow"
    workflow.document_id = "test_document"
    workflow.status = TaskStatus.PENDING
    workflow.created_at = datetime.datetime.now(datetime.timezone.utc)
    workflow.updated_at = datetime.datetime.now(datetime.timezone.utc)
    workflow.completed_at = None
    workflow.error = None
    return workflow


@pytest.mark.asyncio
async def test_create_workflow(mock_db_session, mock_document):
    """Test creating a workflow."""
    # Set up mocks
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_document
    
    # Mock UUID generation
    with patch("uuid.uuid4", return_value=MagicMock(hex="1234567890")):
        # Create workflow
        workflow_id = await create_workflow(
            document_id="test_document",
            template_id="test_template",
            options={"option1": "value1"},
            db=mock_db_session,
        )
    
    # Verify workflow was created
    assert workflow_id == "wf_1234567890"
    
    # Verify workflow was added to database
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called()
    
    # Verify document status was updated
    assert mock_document.status == "processing"
    assert mock_document.job_id == workflow_id


@pytest.mark.asyncio
async def test_execute_workflow(mock_db_session, mock_workflow):
    """Test executing a workflow."""
    # Set up mocks
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_workflow
    
    # Mock workflow executor
    with patch("app.services.workflow_service.WorkflowExecutor") as mock_executor_class:
        mock_executor = mock_executor_class.return_value
        mock_executor.execute_workflow = AsyncMock(return_value={"status": "completed"})
        
        # Execute workflow
        result = await execute_workflow(
            workflow_id="test_workflow",
            db=mock_db_session,
        )
    
    # Verify workflow executor was created
    mock_executor_class.assert_called_once_with(db_session=mock_db_session)
    
    # Verify workflow was executed
    mock_executor.execute_workflow.assert_called_once_with("test_workflow")
    
    # Verify result
    assert result == {"status": "completed"}


@pytest.mark.asyncio
async def test_get_workflow_status(mock_db_session, mock_workflow):
    """Test getting workflow status."""
    # Set up mocks
    mock_workflow.tasks = [
        MagicMock(status=TaskStatus.PENDING),
        MagicMock(status=TaskStatus.RUNNING),
        MagicMock(status=TaskStatus.COMPLETED),
        MagicMock(status=TaskStatus.FAILED),
    ]
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_workflow
    
    # Get workflow status
    status = await get_workflow_status(
        workflow_id="test_workflow",
        db=mock_db_session,
    )
    
    # Verify status
    assert status["workflow_id"] == "test_workflow"
    assert status["document_id"] == "test_document"
    assert status["status"] == mock_workflow.status.value
    assert status["task_counts"]["total"] == 4
    assert status["task_counts"]["pending"] == 1
    assert status["task_counts"]["running"] == 1
    assert status["task_counts"]["completed"] == 1
    assert status["task_counts"]["failed"] == 1
    assert status["progress"] == 25.0


def test_create_tasks():
    """Test creating tasks for a workflow."""
    # Create tasks
    tasks = _create_tasks(
        workflow_id="test_workflow",
        document_path="test_document.pdf",
        template_id="test_template",
        options={"option1": "value1"},
    )
    
    # Verify tasks
    assert len(tasks) == 8
    
    # Verify task types
    task_types = [task.task_type for task in tasks]
    assert TaskType.PREPROCESS in task_types
    assert TaskType.EXTRACT_TEXT in task_types
    assert TaskType.ANALYZE_LAYOUT in task_types
    assert TaskType.UNDERSTAND_DOCUMENT in task_types
    assert TaskType.EXTRACT_FIELDS in task_types
    assert TaskType.EXTRACT_TABLES in task_types
    assert TaskType.VALIDATE_RESULTS in task_types
    assert TaskType.POSTPROCESS in task_types
    
    # Verify task parameters
    for task in tasks:
        assert task.workflow_id == "test_workflow"
        assert task.status == TaskStatus.PENDING
        
        if task.task_type in [
            TaskType.PREPROCESS,
            TaskType.EXTRACT_TEXT,
            TaskType.ANALYZE_LAYOUT,
        ]:
            assert task.params["document_path"] == "test_document.pdf"
        
        if task.task_type in [
            TaskType.UNDERSTAND_DOCUMENT,
            TaskType.EXTRACT_FIELDS,
            TaskType.EXTRACT_TABLES,
        ]:
            assert task.params["document_path"] == "test_document.pdf"
            assert task.params["template_id"] == "test_template"


def test_create_task_dependencies(mock_db_session):
    """Test creating task dependencies."""
    # Create tasks
    tasks = _create_tasks(
        workflow_id="test_workflow",
        document_path="test_document.pdf",
    )
    
    # Create dependencies
    _create_task_dependencies(tasks, mock_db_session)
    
    # Verify dependencies were added to database
    assert mock_db_session.add.call_count >= 8  # At least 8 dependencies
