# Architecture Overview

This document describes the architecture of DocuAgent, including its components, data flow, and integration points.

## System Architecture

DocuAgent follows a modular architecture with several key components that can run locally via Docker:

```
┌─────────────────────────────────────────────────────────────────┐
│                        DocuAgent System                         │
│                                                                 │
│  ┌─────────┐     ┌─────────────┐      ┌────────────────────┐   │
│  │         │     │             │      │                    │   │
│  │  Web UI │────▶│ API Gateway │─────▶│ Document Processor │   │
│  │         │     │             │      │                    │   │
│  └─────────┘     └─────────────┘      └────────────────────┘   │
│                         │                       │               │
│                         │                       │               │
│                         ▼                       ▼               │
│                  ┌─────────────┐      ┌────────────────────┐   │
│                  │             │      │                    │   │
│                  │  Database   │◀────▶│ Extraction Service │   │
│                  │             │      │                    │   │
│                  └─────────────┘      └────────────────────┘   │
│                                                │               │
│                                                │               │
│                                                ▼               │
│                                       ┌────────────────────┐   │
│                                       │                    │   │
│                                       │ Agentic Orchestrator│  │
│                                       │                    │   │
│                                       └────────────────────┘   │
│                                                │               │
│                                                │               │
│                  ┌─────────────┐               │               │
│                  │             │               │               │
│                  │Cloud Service│◀──────────────┘               │
│                  │ Connector   │ (Optional)                    │
│                  │             │                               │
│                  └─────────────┘                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Core Processing Engine

The Core Processing Engine handles document intake, preprocessing, and analysis:

- **Document Intake**: Accepts PDF, image, and office document uploads
- **Preprocessing**: Normalizes documents for consistent processing using Unstructured.io
- **Text Extraction**: Extracts high-quality text from PDFs using Marker
- **OCR Processing**: Extracts text from images and scanned documents
- **Layout Analysis**: Identifies document structure, tables, and forms

**Technologies**:
- Python
- FastAPI
- Unstructured.io - For document preprocessing and parsing
- Marker - For high-accuracy PDF text extraction
- Tesseract OCR
- PaddleOCR
- PDFPlumber/PyPDF

### 2. Agentic Orchestration Layer

The Agentic Orchestration Layer manages the document processing workflow:

- **Workflow Management**: Coordinates processing steps
- **Reasoning Logic**: Applies LLM-based reasoning to understand documents
- **Self-Correction**: Validates and corrects extraction results
- **Context Management**: Maintains context across document sections

**Technologies**:
- LangChain
- Llama 3 / Mistral (local LLM)
- Python
- State management system

### 3. Extraction Service

The Extraction Service handles structured data extraction:

- **Template Management**: Stores and applies extraction templates
- **Schema-Based Extraction**: Extracts data according to defined schemas
- **Field Validation**: Validates extracted data against rules
- **Confidence Scoring**: Assigns confidence scores to extracted fields

**Technologies**:
- Python
- JSON Schema
- Regular expressions
- Rule-based validation

### 4. API Gateway

The API Gateway provides access to the system:

- **REST API**: Endpoints for document processing
- **Authentication**: API key validation
- **Rate Limiting**: Controls usage
- **Usage Tracking**: Monitors system usage

**Technologies**:
- FastAPI
- JWT authentication
- Redis (for rate limiting)
- Logging system

### 5. Web Interface

The Web Interface provides a user-friendly front end:

- **Document Upload**: Interface for uploading documents
- **Template Management**: UI for creating and editing templates
- **Results Visualization**: Display of extraction results
- **Export Options**: Export to various formats

**Technologies**:
- React or Vue.js
- Tailwind CSS
- Axios for API communication
- File upload components

### 6. Optional Cloud Connector

The Cloud Connector provides enhanced capabilities:

- **API Integration**: Connects to cloud services
- **Enhanced Models**: Access to more powerful models
- **Feedback Collection**: Gathers anonymized feedback
- **Subscription Management**: Handles service subscriptions

**Technologies**:
- Python
- REST API client
- JWT authentication
- Encryption for secure communication

## Data Flow

1. User uploads document through Web Interface
2. API Gateway authenticates and routes request
3. Core Processing Engine preprocesses document using Unstructured.io
4. If PDF, Marker extracts high-quality text; if image/scan, OCR extracts text
5. Layout analysis identifies document structure and components
6. Agentic Orchestrator analyzes document and determines processing steps
7. Extraction Service applies templates and extracts structured data
8. Results are stored in Database
9. User views and can export results through Web Interface
10. (Optional) Cloud Connector enhances processing with additional capabilities

## Docker Deployment

The system is designed to be deployed using Docker Compose:

```yaml
# docker-compose.yml
version: '3'
services:
  web:
    build: ./web
    ports:
      - "3000:3000"
    depends_on:
      - api
    volumes:
      - ./data:/app/data

  api:
    build: ./api
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./data:/app/data
    environment:
      - MODEL_PATH=/app/models
      - DATABASE_URL=postgresql://user:password@db:5432/docuagent

  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=docuagent
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Security Considerations

- All communication secured with TLS
- API key authentication for all requests
- Data encryption at rest
- Secure model storage
- Configurable data retention policies
- Audit logging for all operations
