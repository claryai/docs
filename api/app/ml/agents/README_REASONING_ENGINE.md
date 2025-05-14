# Reasoning Engine for Clary AI

## Overview

The Reasoning Engine is a core component of the Clary AI document processing platform that provides LLM-based reasoning capabilities for document understanding and extraction. It uses local LLMs (Llama 3 or Mistral) to analyze documents, extract information, and validate results.

## Architecture

The Reasoning Engine consists of the following components:

1. **Model Manager**: Manages LLM models, including loading, downloading, and inference.
2. **Prompt Manager**: Manages prompt templates for document understanding and extraction.
3. **Document Understanding**: Provides document understanding and extraction capabilities.
4. **Reasoning Engine**: Integrates all components and provides a unified interface.

## Implementation Details

### Model Manager

The Model Manager handles LLM model management, including:

- Model downloading from Hugging Face
- Model loading and initialization
- Inference with proper resource management
- Streaming responses
- Model unloading and cleanup

The Model Manager supports the following models:

- **Llama 3 8B**: A powerful open-source LLM from Meta AI
- **Mistral 7B**: A high-performance open-source LLM from Mistral AI

### Prompt Manager

The Prompt Manager handles prompt templates for document understanding and extraction, including:

- Built-in prompt templates
- Custom prompt templates
- Template rendering with variables
- JSON formatting and parsing

The Prompt Manager includes the following built-in templates:

- **Document Understanding**: For understanding document type, structure, and purpose
- **Field Extraction**: For extracting fields from documents
- **Table Extraction**: For extracting tables from documents
- **Validation**: For validating extracted information

### Document Understanding

The Document Understanding component provides document understanding and extraction capabilities, including:

- Document type classification
- Field extraction
- Table extraction
- Validation and correction

### Reasoning Engine

The Reasoning Engine integrates all components and provides a unified interface for:

- Document understanding
- Field extraction
- Table extraction
- Validation and correction

## Integration with Workflow Engine

The Reasoning Engine is integrated with the Workflow Engine to provide a complete document processing solution. The Workflow Engine uses the Reasoning Engine for the following tasks:

- **Document Understanding**: Understanding document type, structure, and purpose
- **Field Extraction**: Extracting fields from documents
- **Table Extraction**: Extracting tables from documents
- **Validation**: Validating extracted information

## Configuration

The Reasoning Engine can be configured using the following environment variables:

- `LLM_MODEL`: The LLM model to use (default: `llama-3-8b`)
- `LLM_GPU_LAYERS`: Number of layers to offload to GPU (default: `-1` for auto-detect)
- `LLM_CONTEXT_LENGTH`: Context length for the LLM (default: `4096`)
- `LLM_BATCH_SIZE`: Batch size for the LLM (default: `512`)
- `MODEL_PATH`: Path to the model directory (default: `/app/models`)

## Usage

### Document Understanding

```python
from app.ml.agents.reasoning_engine import ReasoningEngine

# Create reasoning engine
engine = ReasoningEngine()

# Initialize engine
await engine.initialize()

# Understand document
understanding = await engine.understand_document(
    document_text="Document text...",
    document_layout={"layout": "information"},
    document_type="invoice",
)
```

### Field Extraction

```python
# Extract fields
fields = await engine.extract_fields(
    document_text="Document text...",
    document_layout={"layout": "information"},
    fields_to_extract=[
        {"name": "invoice_number", "type": "string", "required": True},
        {"name": "date", "type": "date", "required": True},
    ],
)
```

### Table Extraction

```python
# Extract tables
tables = await engine.extract_tables(
    document_text="Document text...",
    document_layout={"layout": "information"},
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

### Validation

```python
# Validate extraction
validation = await engine.validate_extraction(
    document_text="Document text...",
    extracted_fields=fields,
    extracted_tables=tables,
)
```

## Performance Considerations

The Reasoning Engine is designed to be efficient and performant, with the following considerations:

- **Model Loading**: Models are loaded on demand and cached for reuse
- **GPU Acceleration**: GPU acceleration is used when available
- **Context Management**: Context is managed to minimize memory usage
- **Resource Cleanup**: Resources are properly cleaned up when no longer needed

## Future Enhancements

The Reasoning Engine will be enhanced with the following features in future releases:

1. **Model Quantization**: Support for different quantization levels
2. **GPU Acceleration**: Improved GPU support for faster inference
3. **Model Caching**: Intelligent model caching for better performance
4. **Prompt Optimization**: Optimized prompts for better extraction accuracy
5. **Multi-Model Inference**: Support for using multiple models for different tasks
