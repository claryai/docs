---
title: 'Workflow Endpoints'
description: 'API endpoints for managing workflows'
---

# Workflow Endpoints

The Workflow endpoints allow you to create, manage, and execute document processing workflows in Clary AI.

## Create Workflow

```
POST /v1/workflows
```

Create a new workflow.

### Request

**Content-Type**: `application/json`

```json
{
  "name": "Invoice Processing",
  "description": "Extract information from invoices",
  "definition": {
    "triggers": [
      {
        "type": "document_upload",
        "filter": {
          "mime_types": ["application/pdf"]
        }
      }
    ],
    "tasks": [
      {
        "id": "parse_document",
        "type": "document_parser",
        "config": {
          "output_format": "json"
        }
      },
      {
        "id": "extract_invoice_data",
        "type": "entity_extraction",
        "depends_on": ["parse_document"],
        "config": {
          "entities": [
            "invoice_number",
            "date",
            "total_amount",
            "vendor_name",
            "line_items"
          ]
        }
      },
      {
        "id": "store_results",
        "type": "database_connector",
        "depends_on": ["extract_invoice_data"],
        "config": {
          "connection": "default_database",
          "table": "invoices"
        }
      }
    ],
    "error_handling": {
      "retry": {
        "max_attempts": 3,
        "backoff": "exponential"
      }
    }
  }
}
```

### Response

```json
{
  "workflow_id": "wf_123456789",
  "name": "Invoice Processing",
  "description": "Extract information from invoices",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z",
  "status": "active",
  "definition": {...}
}
```

### Example

```bash
curl -X POST https://api.claryai.com/v1/workflows \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Invoice Processing",
    "description": "Extract information from invoices",
    "definition": {...}
  }'
```

## Get Workflow

```
GET /v1/workflows/{workflow_id}
```

Retrieve information about a specific workflow.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | String | Yes | The ID of the workflow to retrieve |

### Response

```json
{
  "workflow_id": "wf_123456789",
  "name": "Invoice Processing",
  "description": "Extract information from invoices",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z",
  "status": "active",
  "definition": {...},
  "stats": {
    "executions_total": 100,
    "executions_successful": 95,
    "executions_failed": 5,
    "average_duration_ms": 1500
  }
}
```

### Example

```bash
curl -X GET https://api.claryai.com/v1/workflows/wf_123456789 \
  -H "Authorization: Bearer your_api_key_here"
```

## List Workflows

```
GET /v1/workflows
```

List all workflows.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | Integer | No | Maximum number of workflows to return (default: 10, max: 100) |
| `offset` | Integer | No | Offset for pagination (default: 0) |
| `status` | String | No | Filter by workflow status (e.g., "active", "inactive") |

### Response

```json
{
  "data": [
    {
      "workflow_id": "wf_123456789",
      "name": "Invoice Processing",
      "description": "Extract information from invoices",
      "created_at": "2023-01-01T12:00:00Z",
      "updated_at": "2023-01-01T12:00:00Z",
      "status": "active"
    },
    {
      "workflow_id": "wf_987654321",
      "name": "Contract Analysis",
      "description": "Analyze contract documents",
      "created_at": "2023-02-01T12:00:00Z",
      "updated_at": "2023-02-01T12:00:00Z",
      "status": "active"
    }
  ],
  "pagination": {
    "total": 50,
    "limit": 10,
    "offset": 0,
    "next_offset": 10
  }
}
```

### Example

```bash
curl -X GET https://api.claryai.com/v1/workflows?limit=10&offset=0&status=active \
  -H "Authorization: Bearer your_api_key_here"
```

## Execute Workflow

```
POST /v1/workflows/{workflow_id}/executions
```

Execute a workflow on a specific document.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | String | Yes | The ID of the workflow to execute |

### Request

**Content-Type**: `application/json`

```json
{
  "document_id": "doc_123456789",
  "parameters": {
    "custom_parameter": "custom_value"
  }
}
```

### Response

```json
{
  "execution_id": "exec_123456789",
  "workflow_id": "wf_123456789",
  "document_id": "doc_123456789",
  "status": "running",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### Example

```bash
curl -X POST https://api.claryai.com/v1/workflows/wf_123456789/executions \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "doc_123456789",
    "parameters": {
      "custom_parameter": "custom_value"
    }
  }'
```

## Get Workflow Execution

```
GET /v1/workflows/{workflow_id}/executions/{execution_id}
```

Retrieve information about a specific workflow execution.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | String | Yes | The ID of the workflow |
| `execution_id` | String | Yes | The ID of the execution to retrieve |

### Response

```json
{
  "execution_id": "exec_123456789",
  "workflow_id": "wf_123456789",
  "document_id": "doc_123456789",
  "status": "completed",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:01:30Z",
  "duration_ms": 90000,
  "tasks": [
    {
      "id": "parse_document",
      "status": "completed",
      "started_at": "2023-01-01T12:00:00Z",
      "completed_at": "2023-01-01T12:00:30Z",
      "duration_ms": 30000,
      "output": {...}
    },
    {
      "id": "extract_invoice_data",
      "status": "completed",
      "started_at": "2023-01-01T12:00:30Z",
      "completed_at": "2023-01-01T12:01:00Z",
      "duration_ms": 30000,
      "output": {...}
    },
    {
      "id": "store_results",
      "status": "completed",
      "started_at": "2023-01-01T12:01:00Z",
      "completed_at": "2023-01-01T12:01:30Z",
      "duration_ms": 30000,
      "output": {...}
    }
  ],
  "result": {...}
}
```

### Example

```bash
curl -X GET https://api.claryai.com/v1/workflows/wf_123456789/executions/exec_123456789 \
  -H "Authorization: Bearer your_api_key_here"
```

## Next Steps

- [Learn about Document Endpoints](/api-reference/endpoints/documents)
- [Learn about Analysis Endpoints](/api-reference/endpoints/analysis)
