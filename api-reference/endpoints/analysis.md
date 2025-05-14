---
title: 'Analysis Endpoints'
description: 'API endpoints for document analysis'
---

# Analysis Endpoints

The Analysis endpoints provide direct access to document analysis capabilities in Clary AI.

## Extract Text

```
POST /v1/analysis/extract-text
```

Extract text from a document.

### Request

**Content-Type**: `application/json`

```json
{
  "document_id": "doc_123456789",
  "options": {
    "include_layout": true,
    "include_tables": true,
    "include_images": false
  }
}
```

### Response

```json
{
  "document_id": "doc_123456789",
  "text": "This is the extracted text from the document...",
  "pages": [
    {
      "page_number": 1,
      "text": "Page 1 text...",
      "layout": {
        "width": 612,
        "height": 792,
        "elements": [...]
      },
      "tables": [...]
    },
    {
      "page_number": 2,
      "text": "Page 2 text...",
      "layout": {
        "width": 612,
        "height": 792,
        "elements": [...]
      },
      "tables": [...]
    }
  ]
}
```

### Example

```bash
curl -X POST https://api.claryai.com/v1/analysis/extract-text \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "doc_123456789",
    "options": {
      "include_layout": true,
      "include_tables": true,
      "include_images": false
    }
  }'
```

## Extract Entities

```
POST /v1/analysis/extract-entities
```

Extract entities from a document.

### Request

**Content-Type**: `application/json`

```json
{
  "document_id": "doc_123456789",
  "entities": [
    "person",
    "organization",
    "date",
    "amount",
    "custom_entity"
  ],
  "custom_entities": [
    {
      "name": "custom_entity",
      "pattern": "\\b[A-Z]{3}\\d{3}\\b"
    }
  ]
}
```

### Response

```json
{
  "document_id": "doc_123456789",
  "entities": [
    {
      "type": "person",
      "value": "John Doe",
      "confidence": 0.95,
      "page": 1,
      "position": {
        "x": 100,
        "y": 200,
        "width": 80,
        "height": 20
      }
    },
    {
      "type": "organization",
      "value": "Acme Inc.",
      "confidence": 0.92,
      "page": 1,
      "position": {
        "x": 100,
        "y": 250,
        "width": 100,
        "height": 20
      }
    },
    {
      "type": "date",
      "value": "2023-01-01",
      "confidence": 0.98,
      "page": 1,
      "position": {
        "x": 400,
        "y": 200,
        "width": 80,
        "height": 20
      }
    },
    {
      "type": "amount",
      "value": "1000.00",
      "confidence": 0.97,
      "page": 1,
      "position": {
        "x": 400,
        "y": 400,
        "width": 80,
        "height": 20
      }
    },
    {
      "type": "custom_entity",
      "value": "ABC123",
      "confidence": 0.90,
      "page": 1,
      "position": {
        "x": 200,
        "y": 300,
        "width": 60,
        "height": 20
      }
    }
  ]
}
```

### Example

```bash
curl -X POST https://api.claryai.com/v1/analysis/extract-entities \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "doc_123456789",
    "entities": [
      "person",
      "organization",
      "date",
      "amount",
      "custom_entity"
    ],
    "custom_entities": [
      {
        "name": "custom_entity",
        "pattern": "\\b[A-Z]{3}\\d{3}\\b"
      }
    ]
  }'
```

## Classify Document

```
POST /v1/analysis/classify
```

Classify a document into one or more categories.

### Request

**Content-Type**: `application/json`

```json
{
  "document_id": "doc_123456789",
  "categories": [
    "invoice",
    "contract",
    "receipt",
    "resume"
  ],
  "options": {
    "multi_label": false,
    "confidence_threshold": 0.7
  }
}
```

### Response

```json
{
  "document_id": "doc_123456789",
  "classifications": [
    {
      "category": "invoice",
      "confidence": 0.95
    }
  ]
}
```

### Example

```bash
curl -X POST https://api.claryai.com/v1/analysis/classify \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "doc_123456789",
    "categories": [
      "invoice",
      "contract",
      "receipt",
      "resume"
    ],
    "options": {
      "multi_label": false,
      "confidence_threshold": 0.7
    }
  }'
```

## Summarize Document

```
POST /v1/analysis/summarize
```

Generate a summary of a document.

### Request

**Content-Type**: `application/json`

```json
{
  "document_id": "doc_123456789",
  "options": {
    "max_length": 500,
    "format": "paragraph",
    "focus": [
      "key_points",
      "conclusions"
    ]
  }
}
```

### Response

```json
{
  "document_id": "doc_123456789",
  "summary": "This is a summary of the document...",
  "key_points": [
    "Key point 1",
    "Key point 2",
    "Key point 3"
  ]
}
```

### Example

```bash
curl -X POST https://api.claryai.com/v1/analysis/summarize \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "doc_123456789",
    "options": {
      "max_length": 500,
      "format": "paragraph",
      "focus": [
        "key_points",
        "conclusions"
      ]
    }
  }'
```

## Next Steps

- [Learn about Document Endpoints](/api-reference/endpoints/documents)
- [Learn about Workflow Endpoints](/api-reference/endpoints/workflows)
