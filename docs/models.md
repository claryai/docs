# Open Source Models

This document outlines the open source AI models used in DocuAgent for document processing, text extraction, and agentic capabilities.

## Document Layout Analysis Models

### LayoutLM / LayoutLMv3

**Description**: Microsoft's pre-trained model for document image understanding and information extraction.

**Features**:
- Joint modeling of text and layout information
- Pre-trained on large-scale document corpus
- Supports document classification, form understanding, and information extraction

**Implementation**:
```python
from transformers import LayoutLMv3Processor, LayoutLMv3ForSequenceClassification
import torch
from PIL import Image

processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base")
model = LayoutLMv3ForSequenceClassification.from_pretrained("microsoft/layoutlmv3-base")

image = Image.open("document.png").convert("RGB")
encoding = processor(image, return_tensors="pt")
outputs = model(**encoding)
```

**Resource Requirements**:
- Memory: 2-4GB RAM
- Disk: ~500MB for model
- GPU: Optional but recommended for faster processing

**References**:
- [LayoutLMv3 GitHub](https://github.com/microsoft/unilm/tree/master/layoutlmv3)
- [Hugging Face Model](https://huggingface.co/microsoft/layoutlmv3-base)

### Donut (Document Understanding Transformer)

**Description**: End-to-end document understanding transformer that directly generates structured outputs from document images.

**Features**:
- Visual encoder + text decoder architecture
- No need for OCR preprocessing
- Supports various document understanding tasks

**Implementation**:
```python
from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image

processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base")
model = VisionEncoderDecoderModel.from_pretrained("naver-clova-ix/donut-base")

image = Image.open("document.png").convert("RGB")
pixel_values = processor(image, return_tensors="pt").pixel_values
outputs = model.generate(pixel_values)
```

**Resource Requirements**:
- Memory: 4GB RAM
- Disk: ~1GB for model
- GPU: Recommended for reasonable performance

**References**:
- [Donut GitHub](https://github.com/clovaai/donut)
- [Hugging Face Model](https://huggingface.co/naver-clova-ix/donut-base)

## OCR and Text Extraction Models

### Tesseract OCR

**Description**: Open source OCR engine maintained by Google.

**Features**:
- Supports over 100 languages
- Layout analysis capabilities
- Character and word recognition

**Implementation**:
```python
import pytesseract
from PIL import Image

image = Image.open("document.png")
text = pytesseract.image_to_string(image)
```

**Resource Requirements**:
- Memory: 1GB RAM
- Disk: ~30MB for model
- CPU: Works well on CPU

**References**:
- [Tesseract GitHub](https://github.com/tesseract-ocr/tesseract)
- [PyTesseract](https://github.com/madmaze/pytesseract)

### PaddleOCR

**Description**: Practical OCR tool developed by Baidu.

**Features**:
- High accuracy text detection and recognition
- Support for multiple languages
- Layout analysis and table structure recognition

**Implementation**:
```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='en')
result = ocr.ocr('document.png', cls=True)
```

**Resource Requirements**:
- Memory: 2GB RAM
- Disk: ~300MB for models
- GPU: Optional but recommended for faster processing

**References**:
- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)

## Table Extraction Models

### TableTransformer

**Description**: Model for detecting tables in documents and extracting their structure.

**Features**:
- Table detection in document images
- Table structure recognition
- Cell content extraction

**Implementation**:
```python
from transformers import AutoModelForObjectDetection, AutoImageProcessor
import torch
from PIL import Image

processor = AutoImageProcessor.from_pretrained("microsoft/table-transformer-detection")
model = AutoModelForObjectDetection.from_pretrained("microsoft/table-transformer-detection")

image = Image.open("document.png").convert("RGB")
inputs = processor(images=image, return_tensors="pt")
outputs = model(**inputs)
```

**Resource Requirements**:
- Memory: 2GB RAM
- Disk: ~300MB for model
- GPU: Recommended for reasonable performance

**References**:
- [Table Transformer GitHub](https://github.com/microsoft/table-transformer)
- [Hugging Face Model](https://huggingface.co/microsoft/table-transformer-detection)

### Camelot/Tabula

**Description**: Python libraries for extracting tables from PDF files.

**Features**:
- PDF table extraction
- Support for complex table structures
- Export to various formats (CSV, Excel, JSON)

**Implementation**:
```python
import camelot

tables = camelot.read_pdf('document.pdf')
tables[0].df  # pandas DataFrame
```

**Resource Requirements**:
- Memory: 512MB RAM
- Disk: Minimal
- CPU: Works well on CPU

**References**:
- [Camelot GitHub](https://github.com/camelot-dev/camelot)
- [Tabula-py GitHub](https://github.com/chezou/tabula-py)

## LLM for Agentic Capabilities

### Llama 3 (8B or 70B)

**Description**: Open source large language model from Meta.

**Features**:
- Strong reasoning capabilities
- Context understanding
- Instruction following

**Implementation**:
```python
from llama_cpp import Llama

llm = Llama(model_path="./models/llama-3-8b.gguf", n_ctx=4096)
output = llm.create_completion(
    "Extract the invoice number and total amount from this document: ...",
    max_tokens=100,
    temperature=0.1
)
```

**Resource Requirements**:
- Memory: 8GB RAM for 8B model, 32GB+ for 70B model
- Disk: 4GB for 8B model, 40GB for 70B model
- GPU: Optional for 8B model, required for 70B model

**References**:
- [Llama 3 GitHub](https://github.com/meta-llama/llama)
- [llama.cpp GitHub](https://github.com/ggerganov/llama.cpp)

### Mistral 7B

**Description**: Efficient open source language model with strong reasoning capabilities.

**Features**:
- Efficient architecture
- Strong reasoning and instruction following
- Good performance on smaller hardware

**Implementation**:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")

inputs = tokenizer("Extract the following fields from this invoice: ", return_tensors="pt")
outputs = model.generate(**inputs, max_length=200)
```

**Resource Requirements**:
- Memory: 6GB RAM
- Disk: 4GB for model
- GPU: Optional but recommended

**References**:
- [Mistral AI GitHub](https://github.com/mistralai/mistral-src)
- [Hugging Face Model](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)

## Model Selection Strategy

The choice of models depends on the specific requirements and hardware constraints:

1. **For minimal hardware requirements**:
   - Tesseract OCR for text extraction
   - Camelot for table extraction
   - Phi-3-mini for basic reasoning

2. **For balanced performance**:
   - PaddleOCR for text extraction
   - TableTransformer for table detection
   - Mistral 7B for reasoning

3. **For optimal performance**:
   - LayoutLMv3 for document understanding
   - PaddleOCR for text extraction
   - TableTransformer for table extraction
   - Llama 3 (8B or 70B) for reasoning

## Model Integration Architecture

DocuAgent uses a modular approach to model integration, allowing different models to be swapped based on requirements:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Document Input │────▶│  Layout Model   │────▶│    OCR Model    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Extracted Data │◀────│   Table Model   │◀────│ Processed Text  │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │
        ▼
┌─────────────────┐
│                 │
│    LLM Agent    │
│                 │
└─────────────────┘
```

This architecture allows for:
- Independent model updates
- Hardware-specific optimizations
- Progressive enhancement based on available resources
