# Agentic Components for Clary AI

This directory contains the agentic components for the Clary AI document processing platform.

## Overview

The agentic components provide intelligent document processing capabilities through the following modules:

1. **Workflow Engine**: Manages the document processing workflow, including task scheduling, state management, and error handling.
2. **Reasoning Engine**: Provides LLM-based reasoning capabilities for document understanding and extraction.
3. **Extraction Agent**: Coordinates the document processing workflow and extraction process.

## Workflow Engine

The Workflow Engine manages the document processing workflow. It creates and executes tasks in a dependency-based order, ensuring that each task has the necessary inputs from previous tasks.

### Key Features

- Task creation and scheduling
- Dependency management
- State tracking
- Error handling and recovery
- Concurrency control

### Usage

```python
from app.ml.agents.workflow_executor import WorkflowExecutor
from app.db.session import get_db

# Get database session
db = next(get_db())

# Create workflow executor
executor = WorkflowExecutor(db_session=db)

# Execute workflow
result = await executor.execute_workflow("workflow_id")
```

## Reasoning Engine

The Reasoning Engine provides LLM-based reasoning capabilities for document understanding and extraction. It uses a local LLM (Llama 3 or Mistral) to analyze documents, extract information, and validate results.

### Key Features

- Document understanding
- Field extraction
- Table extraction
- Validation and correction

### Usage

```python
from app.ml.agents.reasoning_engine import ReasoningEngine

# Create reasoning engine
engine = ReasoningEngine()

# Initialize engine
await engine.initialize()

# Understand document
understanding = await engine.understand_document(
    document_text="Document text...",
    document_layout=layout_result,
    document_type="invoice",
)

# Extract fields
fields = await engine.extract_fields(
    document_text="Document text...",
    document_layout=layout_result,
    fields_to_extract=[
        {"name": "invoice_number", "type": "string", "required": True},
        {"name": "date", "type": "date", "required": True},
    ],
)

# Extract tables
tables = await engine.extract_tables(
    document_text="Document text...",
    document_layout=layout_result,
    tables_to_extract=[
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
    ],
)
```

## Extraction Agent

The Extraction Agent coordinates the document processing workflow and extraction process. It integrates with the Workflow Engine and Reasoning Engine to provide a complete document processing solution.

### Key Features

- Workflow creation and execution
- Template-based extraction
- Confidence scoring
- Result formatting

### Usage

```python
from app.ml.agents.extraction_agent import ExtractionAgent

# Create extraction agent
agent = ExtractionAgent()

# Extract information from document
result = await agent.extract(
    document_path="path/to/document.pdf",
    ocr_result=ocr_result,
    layout_result=layout_result,
    template_id="template_invoice_standard",
)
```

## Workflow

The document processing workflow consists of the following steps:

1. **Preprocessing**: Normalize and preprocess the document using Unstructured.io.
2. **Text Extraction**: Extract text from the document using Marker (for PDFs) or OCR (for images).
3. **Layout Analysis**: Analyze the document layout to identify structure, tables, and forms.
4. **Document Understanding**: Use the Reasoning Engine to understand the document type, purpose, and structure.
5. **Field Extraction**: Extract fields from the document based on templates or document understanding.
6. **Table Extraction**: Extract tables from the document based on templates or document understanding.
7. **Validation**: Validate the extraction results and correct errors.
8. **Postprocessing**: Format and finalize the extraction results.

## Implementation Details

The agentic components are implemented in Python using the following technologies:

- **LangChain**: For LLM integration and prompt management
- **Llama 3 / Mistral**: For local LLM-based reasoning
- **FastAPI**: For API integration
- **Asyncio**: For asynchronous processing
- **SQLAlchemy**: For database integration

## Testing

The agentic components are tested using pytest. To run the tests:

```bash
cd api
pytest tests/ml/agents/
```

## Future Enhancements

The agentic components will be enhanced with the following features in future releases:

1. **Multi-Agent Collaboration**: Multiple agents working together to process complex documents
2. **Learning from Feedback**: Improving extraction accuracy based on user feedback
3. **Domain-Specific Reasoning**: Specialized reasoning for specific document types and domains
4. **Advanced Validation**: More sophisticated validation and correction mechanisms
5. **Performance Optimization**: Improved processing speed and resource usage
