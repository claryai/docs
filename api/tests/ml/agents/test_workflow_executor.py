"""
Tests for the workflow executor.

This module contains tests for the workflow executor.
"""

import asyncio
import datetime
import json
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.orm import Session

from app.models.workflow import Workflow, Task, TaskStatus, TaskType, TaskDependency
from app.ml.agents.workflow_executor import WorkflowExecutor


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock(spec=Session)
    return session


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


@pytest.fixture
def mock_tasks():
    """Create mock tasks for the workflow."""
    tasks = []
    
    # Preprocess task
    preprocess_task = MagicMock(spec=Task)
    preprocess_task.id = "test_workflow_preprocess"
    preprocess_task.workflow_id = "test_workflow"
    preprocess_task.task_type = TaskType.PREPROCESS
    preprocess_task.status = TaskStatus.PENDING
    preprocess_task.params = {"document_path": "test_document.pdf"}
    preprocess_task.result = None
    preprocess_task.error = None
    preprocess_task.dependencies = []
    preprocess_task.can_execute.return_value = True
    tasks.append(preprocess_task)
    
    # Extract text task
    extract_text_task = MagicMock(spec=Task)
    extract_text_task.id = "test_workflow_extract_text"
    extract_text_task.workflow_id = "test_workflow"
    extract_text_task.task_type = TaskType.EXTRACT_TEXT
    extract_text_task.status = TaskStatus.PENDING
    extract_text_task.params = {"document_path": "test_document.pdf"}
    extract_text_task.result = None
    extract_text_task.error = None
    extract_text_task.dependencies = [MagicMock(spec=TaskDependency)]
    extract_text_task.dependencies[0].dependency_task = preprocess_task
    extract_text_task.can_execute.return_value = False
    tasks.append(extract_text_task)
    
    return tasks


@pytest.mark.asyncio
async def test_execute_workflow(mock_db_session, mock_workflow, mock_tasks):
    """Test executing a workflow."""
    # Set up mocks
    mock_workflow.tasks = mock_tasks
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_workflow
    
    # Create executor
    executor = WorkflowExecutor(db_session=mock_db_session)
    
    # Mock task execution methods
    executor._execute_task = AsyncMock()
    executor._get_execution_order = MagicMock(return_value=mock_tasks)
    executor._get_workflow_results = MagicMock(return_value={"status": "completed"})
    
    # Execute workflow
    result = await executor.execute_workflow("test_workflow")
    
    # Verify workflow status was updated
    assert mock_workflow.status == TaskStatus.COMPLETED
    assert mock_workflow.completed_at is not None
    
    # Verify task execution was called
    executor._execute_task.assert_called_once_with(mock_tasks[0])
    
    # Verify result
    assert result == {"status": "completed"}


@pytest.mark.asyncio
async def test_execute_task(mock_db_session, mock_workflow, mock_tasks):
    """Test executing a task."""
    # Set up mocks
    mock_workflow.tasks = mock_tasks
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_workflow
    
    # Create executor
    executor = WorkflowExecutor(db_session=mock_db_session)
    
    # Mock task execution methods
    executor._execute_preprocess_task = AsyncMock(return_value={"status": "preprocessed"})
    
    # Execute task
    await executor._execute_task(mock_tasks[0])
    
    # Verify task status was updated
    assert mock_tasks[0].status == TaskStatus.COMPLETED
    assert mock_tasks[0].result == {"status": "preprocessed"}
    assert mock_tasks[0].completed_at is not None
    
    # Verify task execution method was called
    executor._execute_preprocess_task.assert_called_once_with(mock_tasks[0])


@pytest.mark.asyncio
async def test_execute_task_error(mock_db_session, mock_workflow, mock_tasks):
    """Test executing a task with an error."""
    # Set up mocks
    mock_workflow.tasks = mock_tasks
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_workflow
    
    # Create executor
    executor = WorkflowExecutor(db_session=mock_db_session)
    
    # Mock task execution methods
    executor._execute_preprocess_task = AsyncMock(side_effect=ValueError("Test error"))
    
    # Execute task
    with pytest.raises(ValueError):
        await executor._execute_task(mock_tasks[0])
    
    # Verify task status was updated
    assert mock_tasks[0].status == TaskStatus.FAILED
    assert mock_tasks[0].error == "Test error"
    assert mock_tasks[0].updated_at is not None


@pytest.mark.asyncio
async def test_get_execution_order(mock_db_session, mock_workflow, mock_tasks):
    """Test getting task execution order."""
    # Set up mocks
    mock_workflow.tasks = mock_tasks
    
    # Create executor
    executor = WorkflowExecutor(db_session=mock_db_session)
    
    # Get execution order
    order = executor._get_execution_order(mock_workflow)
    
    # Verify order
    assert len(order) == 2
    assert order[0] == mock_tasks[0]  # Preprocess task first
    assert order[1] == mock_tasks[1]  # Extract text task second
