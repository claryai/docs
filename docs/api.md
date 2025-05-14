# API Documentation

This document describes the REST API endpoints provided by Clary AI for document processing and data extraction.

## Base URL

All API endpoints are relative to the base URL:

```
http://localhost:8000/api/v1
```

For production deployments, replace with your domain.

## Authentication

All API requests require authentication using an API key. Include the API key in the request header:

```
X-API-Key: your_api_key_here
```

API keys are tied to specific tiers (free, professional, enterprise) which determine usage limits and available features. See the [API Key Management](api_keys.md) documentation for more information.

## Endpoints

### System

#### Health Check

```
GET /api/v1/system/health
```

Returns the health status of the system.

#### License Status

```
GET /api/v1/system/license
```

Returns information about the current license status.

### API Key Management

#### List API Keys

```
GET /api/v1/api-keys
```

Returns a list of all API keys for the authenticated user.

#### Create API Key

```
POST /api/v1/api-keys
```

Creates a new API key.

Request body:
```json
{
  "name": "My API Key",
  "description": "For testing purposes",
  "tier": "professional",
  "valid_days": 30
}
```

#### Get API Key

```
GET /api/v1/api-keys/{api_key_id}
```

Returns details about a specific API key.

#### Update API Key

```
PUT /api/v1/api-keys/{api_key_id}
```

Updates an existing API key.

#### Delete API Key

```
DELETE /api/v1/api-keys/{api_key_id}
```

Deletes an API key.

#### Revoke API Key

```
POST /api/v1/api-keys/{api_key_id}/revoke
```

Revokes an API key (sets is_active to false).

#### Regenerate API Key

```
POST /api/v1/api-keys/{api_key_id}/regenerate
```

Regenerates the API key value while keeping the same settings.

### Document Processing

#### Upload Document

```
POST /documents/upload
```

Upload a document for processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: The document file (PDF, image, etc.)
  - `template_id` (optional): ID of extraction template to apply
  - `options` (optional): JSON string with processing options

**Response:**
```json
{
  "document_id": "doc_123456",
  "filename": "invoice.pdf",
  "status": "processing",
  "created_at": "2023-05-13T10:30:00Z"
}
```

#### Get Document Status

```
GET /documents/{document_id}
```

Check the status of a document processing job.

**Response:**
```json
{
  "document_id": "doc_123456",
  "filename": "invoice.pdf",
  "status": "completed",
  "created_at": "2023-05-13T10:30:00Z",
  "completed_at": "2023-05-13T10:31:05Z",
  "extraction_status": "success"
}
```

#### Get Document Results

```
GET /documents/{document_id}/results
```

Retrieve the extraction results for a processed document.

**Response:**
```json
{
  "document_id": "doc_123456",
  "extraction_results": {
    "invoice_number": {
      "value": "INV-12345",
      "confidence": 0.95,
      "bounding_box": [100, 200, 200, 230]
    },
    "date": {
      "value": "2023-05-10",
      "confidence": 0.92,
      "bounding_box": [300, 200, 400, 230]
    },
    "total_amount": {
      "value": "1250.00",
      "confidence": 0.98,
      "bounding_box": [500, 600, 600, 630]
    },
    "line_items": [
      {
        "description": "Product A",
        "quantity": "2",
        "unit_price": "500.00",
        "total": "1000.00"
      },
      {
        "description": "Service B",
        "quantity": "1",
        "unit_price": "250.00",
        "total": "250.00"
      }
    ]
  },
  "raw_text": "...",
  "template_id": "template_invoice_standard"
}
```

#### Delete Document

```
DELETE /documents/{document_id}
```

Delete a document and its extraction results.

**Response:**
```json
{
  "success": true,
  "message": "Document deleted successfully"
}
```

### Template Management

#### List Templates

```
GET /templates
```

List all available extraction templates.

**Response:**
```json
{
  "templates": [
    {
      "template_id": "template_invoice_standard",
      "name": "Standard Invoice",
      "description": "Template for standard invoices",
      "created_at": "2023-04-01T09:00:00Z",
      "document_type": "invoice"
    },
    {
      "template_id": "template_receipt",
      "name": "Receipt",
      "description": "Template for receipts",
      "created_at": "2023-04-02T10:00:00Z",
      "document_type": "receipt"
    }
  ]
}
```

#### Get Template

```
GET /templates/{template_id}
```

Get details of a specific template.

**Response:**
```json
{
  "template_id": "template_invoice_standard",
  "name": "Standard Invoice",
  "description": "Template for standard invoices",
  "created_at": "2023-04-01T09:00:00Z",
  "document_type": "invoice",
  "fields": [
    {
      "name": "invoice_number",
      "type": "string",
      "required": true,
      "extraction_hints": ["Invoice Number", "Invoice #", "Invoice No"]
    },
    {
      "name": "date",
      "type": "date",
      "required": true,
      "extraction_hints": ["Date", "Invoice Date"]
    },
    {
      "name": "total_amount",
      "type": "currency",
      "required": true,
      "extraction_hints": ["Total", "Amount Due", "Total Due"]
    },
    {
      "name": "line_items",
      "type": "table",
      "required": false,
      "columns": [
        {"name": "description", "type": "string"},
        {"name": "quantity", "type": "number"},
        {"name": "unit_price", "type": "currency"},
        {"name": "total", "type": "currency"}
      ]
    }
  ]
}
```

#### Create Template

```
POST /templates
```

Create a new extraction template.

**Request:**
```json
{
  "name": "Purchase Order",
  "description": "Template for purchase orders",
  "document_type": "purchase_order",
  "fields": [
    {
      "name": "po_number",
      "type": "string",
      "required": true,
      "extraction_hints": ["PO Number", "Purchase Order #", "PO #"]
    },
    {
      "name": "date",
      "type": "date",
      "required": true,
      "extraction_hints": ["Date", "PO Date"]
    },
    {
      "name": "vendor",
      "type": "string",
      "required": true,
      "extraction_hints": ["Vendor", "Supplier"]
    },
    {
      "name": "total_amount",
      "type": "currency",
      "required": true,
      "extraction_hints": ["Total", "Amount"]
    }
  ]
}
```

**Response:**
```json
{
  "template_id": "template_purchase_order",
  "name": "Purchase Order",
  "description": "Template for purchase orders",
  "created_at": "2023-05-13T11:00:00Z",
  "document_type": "purchase_order"
}
```

#### Update Template

```
PUT /templates/{template_id}
```

Update an existing extraction template.

**Request:**
Same format as Create Template.

**Response:**
```json
{
  "template_id": "template_purchase_order",
  "name": "Purchase Order",
  "description": "Updated template for purchase orders",
  "created_at": "2023-05-13T11:00:00Z",
  "updated_at": "2023-05-13T12:00:00Z",
  "document_type": "purchase_order"
}
```

#### Delete Template

```
DELETE /templates/{template_id}
```

Delete an extraction template.

**Response:**
```json
{
  "success": true,
  "message": "Template deleted successfully"
}
```

### System Management

#### Get System Status

```
GET /system/status
```

Get the status of the DocuAgent system.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "database": "connected",
    "document_processor": "running",
    "extraction_service": "running",
    "cloud_connector": "disconnected"
  },
  "models": {
    "ocr": "tesseract-4.1.1",
    "layout": "layoutlm-v3",
    "llm": "llama-3-8b"
  },
  "usage": {
    "documents_processed_today": 15,
    "documents_processed_total": 1250,
    "storage_used": "1.2GB"
  }
}
```

#### Get Usage Statistics

```
GET /system/usage
```

Get usage statistics for the system.

**Response:**
```json
{
  "period": "2023-05",
  "documents_processed": 150,
  "pages_processed": 450,
  "successful_extractions": 145,
  "failed_extractions": 5,
  "average_processing_time": 3.2,
  "document_types": {
    "invoice": 80,
    "receipt": 45,
    "purchase_order": 25
  }
}
```

## Error Responses

All API endpoints return standard HTTP status codes:

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

Error responses include a JSON body with details:

```json
{
  "error": true,
  "code": "invalid_template",
  "message": "The specified template does not exist",
  "details": {
    "template_id": "non_existent_template"
  }
}
```

## Rate Limiting

API requests are subject to rate limiting:

- 100 requests per minute per API key
- 1000 requests per hour per API key

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1589547834
```

## Webhooks

DocuAgent can send webhook notifications when document processing is complete:

### Configure Webhook

```
POST /webhooks
```

**Request:**
```json
{
  "url": "https://your-server.com/webhook",
  "events": ["document.processed", "document.failed"],
  "secret": "your_webhook_secret"
}
```

**Response:**
```json
{
  "webhook_id": "webhook_123456",
  "url": "https://your-server.com/webhook",
  "events": ["document.processed", "document.failed"],
  "created_at": "2023-05-13T14:00:00Z"
}
```

### Webhook Payload

When a document is processed, DocuAgent sends a POST request to your webhook URL:

```json
{
  "event": "document.processed",
  "document_id": "doc_123456",
  "timestamp": "2023-05-13T14:05:00Z",
  "status": "completed",
  "extraction_status": "success"
}
```

The request includes a signature header for verification:

```
X-ClaryAI-Signature: sha256=...
```
