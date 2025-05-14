---
title: 'AI Models'
description: 'Understanding the AI models used in Clary AI'
---

# AI Models

Clary AI leverages a variety of open-source AI models to provide powerful document processing and analysis capabilities.

## Model Types

### Document Processing Models

These models are responsible for parsing documents, extracting text, and understanding document structure:

- **OCR Models**: For extracting text from images and scanned documents
- **Layout Analysis Models**: For understanding document structure and layout
- **Table Extraction Models**: For identifying and extracting tables from documents

### Natural Language Processing Models

These models process and analyze the text extracted from documents:

- **Entity Recognition Models**: For identifying entities such as names, dates, and amounts
- **Classification Models**: For categorizing documents or parts of documents
- **Summarization Models**: For generating concise summaries of document content

### Reasoning Models

These models provide agentic capabilities, allowing Clary AI to reason about document content and perform complex tasks:

- **Phi-4 Multimodal**: A powerful multimodal model that can understand both text and images (Standard tier)
- **Llama 4**: A state-of-the-art language model for advanced reasoning tasks (Professional tier)

## Model Tiers

Clary AI offers different tiers with varying model capabilities:

### Lite Tier

- Basic document processing models
- Limited NLP capabilities
- No pre-integrated LLM

### Standard Tier

- Advanced document processing models
- Comprehensive NLP capabilities
- Phi-4 Multimodal pre-integrated

### Professional Tier

- Enterprise-grade document processing models
- Advanced NLP capabilities
- Cloud LLM connections (including Llama 4)
- Custom model fine-tuning

## Model Deployment

Clary AI models are deployed within Docker containers, making them easy to set up and use. The models run locally on your infrastructure, ensuring data privacy and security.

### Hardware Requirements

Different models have different hardware requirements:

- **Basic models**: Can run on standard CPU hardware
- **Advanced models**: Benefit from GPU acceleration
- **Large models**: May require dedicated GPU hardware

## Model Updates

Clary AI regularly updates its models to incorporate the latest advancements in AI research. Updates are delivered through Docker image updates, making it easy to stay current.

## Integration with Workflow Engine

The AI models are tightly integrated with Clary AI's [Workflow Engine](/concepts/workflow-engine/index), allowing you to leverage their capabilities in your document processing workflows.

## Next Steps

- [Learn about Document Processing](/concepts/document-processing/index)
- [Explore the Workflow Engine](/concepts/workflow-engine/index)
- [Check out the API Reference](/api-reference/overview)
