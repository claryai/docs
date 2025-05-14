---
title: 'Document Endpoints'
description: 'API endpoints for managing documents'
---

# Document Endpoints

The Document endpoints allow you to upload, retrieve, and manage documents in Clary AI.

## Upload Document

```
POST /v1/documents
```

Upload a new document to Clary AI.

### Request

**Content-Type**: `multipart/form-data`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | The document file to upload |
| `name` | String | No | Custom name for the document |
| `metadata` | JSON | No | Additional metadata for the document |

### Response

```json
{
  "document_id": "doc_123456789",
  "name": "Invoice-2023-01-01.pdf",
  "content_type": "application/pdf",
  "size": 1024,
  "created_at": "2023-01-01T12:00:00Z",
  "status": "processing",
  "metadata": {
    "custom_field": "custom_value"
  }
}
```

### Example

```bash
curl -X POST https://api.claryai.com/v1/documents \
  -H "Authorization: Bearer your_api_key_here" \
  -F "file=@invoice.pdf" \
  -F "name=Invoice-2023-01-01" \
  -F "metadata={\"category\":\"invoice\"}"
```

## Get Document

```
GET /v1/documents/{document_id}
```

Retrieve information about a specific document.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_id` | String | Yes | The ID of the document to retrieve |

### Response

```json
{
  "document_id": "doc_123456789",
  "name": "Invoice-2023-01-01.pdf",
  "content_type": "application/pdf",
  "size": 1024,
  "created_at": "2023-01-01T12:00:00Z",
  "status": "processed",
  "metadata": {
    "custom_field": "custom_value"
  },
  "processing_results": {
    "page_count": 2,
    "text_content": "...",
    "entities": [...]
  }
}
```

### Example

```bash
curl -X GET https://api.claryai.com/v1/documents/doc_123456789 \
  -H "Authorization: Bearer your_api_key_here"
```

## List Documents

```
GET /v1/documents
```

List all documents.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | Integer | No | Maximum number of documents to return (default: 10, max: 100) |
| `offset` | Integer | No | Offset for pagination (default: 0) |
| `status` | String | No | Filter by document status (e.g., "processing", "processed", "failed") |
| `content_type` | String | No | Filter by document content type |

### Response

```json
{
  "data": [
    {
      "document_id": "doc_123456789",
      "name": "Invoice-2023-01-01.pdf",
      "content_type": "application/pdf",
      "size": 1024,
      "created_at": "2023-01-01T12:00:00Z",
      "status": "processed"
    },
    {
      "document_id": "doc_987654321",
      "name": "Contract-2023-02-01.docx",
      "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "size": 2048,
      "created_at": "2023-02-01T12:00:00Z",
      "status": "processed"
    }
  ],
  "pagination": {
    "total": 100,
    "limit": 10,
    "offset": 0,
    "next_offset": 10
  }
}
```

### Example

```bash
curl -X GET https://api.claryai.com/v1/documents?limit=10&offset=0&status=processed \
  -H "Authorization: Bearer your_api_key_here"
```

## Delete Document

```
DELETE /v1/documents/{document_id}
```

Delete a specific document.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_id` | String | Yes | The ID of the document to delete |

### Response

```json
{
  "success": true,
  "message": "Document deleted successfully"
}
```

### Example

```bash
curl -X DELETE https://api.claryai.com/v1/documents/doc_123456789 \
  -H "Authorization: Bearer your_api_key_here"
```

## Download Document

```
GET /v1/documents/{document_id}/content
```

Download the original document content.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_id` | String | Yes | The ID of the document to download |

### Response

The original document file with appropriate Content-Type header.

### Example

```bash
curl -X GET https://api.claryai.com/v1/documents/doc_123456789/content \
  -H "Authorization: Bearer your_api_key_here" \
  --output document.pdf
```

## Next Steps

- [Learn about Workflow Endpoints](/api-reference/endpoints/workflows)
- [Learn about Analysis Endpoints](/api-reference/endpoints/analysis)
