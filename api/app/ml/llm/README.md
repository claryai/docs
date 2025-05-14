# LLM Integration for Clary AI

This directory contains the LLM integration components for the Clary AI document processing platform.

## Overview

The LLM integration provides local LLM-based reasoning capabilities through the following modules:

1. **Model Manager**: Manages LLM models, including loading, downloading, and inference.
2. **Prompt Manager**: Manages prompt templates for document understanding and extraction.
3. **Document Understanding**: Provides document understanding and extraction capabilities.

## Model Manager

The Model Manager handles LLM model management, including:

- Model downloading from Hugging Face
- Model loading and initialization
- Inference with proper resource management
- Streaming responses
- Model unloading and cleanup

### Usage

```python
from app.ml.llm.model_manager import ModelManager

# Create model manager
manager = ModelManager(model_dir="/path/to/models")

# Load model
model = await manager.load_model("llama-3-8b")

# Generate text
response = await manager.generate(
    model_name="llama-3-8b",
    prompt="Hello, world!",
    max_tokens=100,
    temperature=0.1,
)

# Generate text stream
async for chunk in manager.generate_stream(
    model_name="llama-3-8b",
    prompt="Hello, world!",
    max_tokens=100,
    temperature=0.1,
):
    print(chunk, end="", flush=True)

# Unload model
manager.unload_model("llama-3-8b")
```

## Prompt Manager

The Prompt Manager handles prompt templates for document understanding and extraction, including:

- Built-in prompt templates
- Custom prompt templates
- Template rendering with variables
- JSON formatting and parsing

### Usage

```python
from app.ml.llm.prompt_manager import PromptManager

# Create prompt manager
manager = PromptManager(templates_dir="/path/to/templates")

# Render template
prompt = manager.render_template(
    "document_understanding",
    {
        "document_text": "Document text...",
        "document_layout": {"layout": "information"},
        "document_type": "invoice",
    },
)

# Parse JSON from response
result = manager.parse_json_from_response('{"document_type": "invoice"}')
```

## Document Understanding

The Document Understanding component provides document understanding and extraction capabilities, including:

- Document type classification
- Field extraction
- Table extraction
- Validation and correction

### Usage

```python
from app.ml.llm.document_understanding import DocumentUnderstanding
from app.ml.llm.model_manager import ModelManager
from app.ml.llm.prompt_manager import PromptManager

# Create components
model_manager = ModelManager(model_dir="/path/to/models")
prompt_manager = PromptManager(templates_dir="/path/to/templates")
understanding = DocumentUnderstanding(
    model_manager=model_manager,
    prompt_manager=prompt_manager,
    default_model="llama-3-8b",
)

# Understand document
result = await understanding.understand_document(
    document_text="Document text...",
    document_layout={"layout": "information"},
    document_type="invoice",
)

# Extract fields
fields = await understanding.extract_fields(
    document_text="Document text...",
    document_layout={"layout": "information"},
    fields_to_extract=[
        {"name": "invoice_number", "type": "string", "required": True},
        {"name": "date", "type": "date", "required": True},
    ],
)

# Extract tables
tables = await understanding.extract_tables(
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

# Validate extraction
validation = await understanding.validate_extraction(
    document_text="Document text...",
    extracted_fields=fields,
    extracted_tables=tables,
)
```

## Supported Models

The following models are supported:

- **Llama 3 8B**: A powerful open-source LLM from Meta AI
- **Mistral 7B**: A high-performance open-source LLM from Mistral AI

## Implementation Details

The LLM integration is implemented in Python using the following technologies:

- **llama-cpp-python**: For local LLM inference
- **Hugging Face Hub**: For model downloading
- **Jinja2**: For prompt template rendering
- **Asyncio**: For asynchronous processing

## Testing

The LLM integration is tested using pytest. To run the tests:

```bash
cd api
pytest tests/ml/llm/
```

## Future Enhancements

The LLM integration will be enhanced with the following features in future releases:

1. **Model Quantization**: Support for different quantization levels
2. **GPU Acceleration**: Improved GPU support for faster inference
3. **Model Caching**: Intelligent model caching for better performance
4. **Prompt Optimization**: Optimized prompts for better extraction accuracy
5. **Multi-Model Inference**: Support for using multiple models for different tasks
