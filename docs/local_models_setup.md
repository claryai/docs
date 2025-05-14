# Using Local LLM Models with Clary AI

This guide provides instructions on how to configure Clary AI to use locally downloaded LLM models for testing and development purposes.

## 1. Model File Placement

Clary AI is configured to look for model files in a specific directory structure. Follow these steps to set up your local models:

1. Create a `models/llm` directory in your project root:

```bash
mkdir -p models/llm
```

2. Place your model files in this directory with the correct filenames:

For Llama 3:
- Filename: `llama-3-8b.Q4_K_M.gguf`
- Path: `models/llm/llama-3-8b.Q4_K_M.gguf`

For Mistral:
- Filename: `mistral-7b-v0.1.Q4_K_M.gguf`
- Path: `models/llm/mistral-7b-v0.1.Q4_K_M.gguf`

> **Note**: The model files must have exactly these filenames to match the configuration in `model_manager.py`. If your files have different names, you can either rename them or update the configuration in the code.

## 2. Configuration Settings

Create a `.env.local` file in your project root with the following settings:

```
# Local development environment configuration for Clary AI

# Model settings
MODEL_PATH=./models
LLM_MODEL=llama-3-8b  # Options: llama-3-8b, mistral-7b
LLM_GPU_LAYERS=0      # Set to number of layers to offload to GPU, 0 for CPU only, -1 for auto-detect

# Storage settings
UPLOAD_FOLDER=./data/uploads
PROCESSED_FOLDER=./data/processed

# Debug mode
DEBUG=true
```

You can adjust these settings based on your preferences:

- `LLM_MODEL`: Set to either `llama-3-8b` or `mistral-7b` depending on which model you want to use
- `LLM_GPU_LAYERS`: Set to `0` for CPU-only inference, `-1` for auto-detection, or a specific number of layers to offload to GPU

## 3. Verifying Local Model Setup

Run the verification script to check if your local models are properly configured:

```bash
python scripts/verify_local_models.py
```

This script will:
1. Check if the model directory exists
2. Verify if the model files are present
3. Attempt to load the default model
4. Run a simple test generation to confirm the model is working

If everything is set up correctly, you should see output indicating that the model was loaded successfully and a response from the model.

## 4. Testing the Reasoning Engine

To test that the Reasoning Engine is working correctly with your local models, run:

```bash
python scripts/test_reasoning_engine.py
```

This script will:
1. Initialize the Reasoning Engine with your local model
2. Run a document understanding task on a sample invoice
3. Extract fields from the document
4. Display the results

## 5. Troubleshooting

If you encounter issues with loading local models:

1. **Model file not found**: Ensure the model files are in the correct location with the exact filenames specified in the configuration.

2. **Import errors**: Make sure you're running the scripts from the project root directory.

3. **Memory issues**: If you're getting out of memory errors, try:
   - Using a quantized model (e.g., Q4_K_M)
   - Reducing the context length in the configuration
   - Setting `LLM_GPU_LAYERS=0` to use CPU only

4. **Slow inference**: If inference is too slow:
   - Try setting `LLM_GPU_LAYERS=-1` to use GPU acceleration if available
   - Consider using a smaller model or more aggressive quantization

## 6. Advanced Configuration

For advanced users, you can modify the model configurations in `api/app/ml/llm/model_manager.py` to:

1. Add support for additional models
2. Change the quantization level
3. Adjust context length and batch size
4. Configure other model-specific parameters

Example of adding a new model configuration:

```python
self.model_configs = {
    # Existing configurations...
    "your-custom-model": {
        "repo_id": "HuggingFace/Repo",
        "filename": "your-model-file.gguf",
        "type": "llama",
        "context_length": 4096,
        "batch_size": 512,
    },
}
```

Then update your `.env.local` file to use the new model:

```
LLM_MODEL=your-custom-model
```

## 7. Performance Optimization

To optimize performance with local models:

1. **GPU Acceleration**: Set `LLM_GPU_LAYERS` to `-1` for auto-detection or a specific number based on your GPU memory.

2. **Quantization**: Use appropriately quantized models (Q4_K_M is a good balance of quality and performance).

3. **Batch Processing**: Adjust the `LLM_BATCH_SIZE` setting for your specific hardware.

4. **Context Length**: Reduce `LLM_CONTEXT_LENGTH` if you're experiencing memory issues.

## 8. Next Steps

After successfully configuring local models, consider exploring:

1. Creating custom prompt templates in the `models/templates` directory
2. Implementing the remaining workflow engine tasks
3. Optimizing model performance for your specific use cases
4. Developing a web interface for monitoring extraction progress
