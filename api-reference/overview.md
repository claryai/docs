---
title: 'API Overview'
description: 'Overview of the Clary AI API'
---

# API Overview

The Clary AI API provides programmatic access to all Clary AI features, allowing you to integrate document processing capabilities into your applications.

## API Basics

- **Base URL**: `https://api.claryai.com/v1` or `http://localhost:8000/v1` for self-hosted deployments
- **Authentication**: API key authentication (Bearer token)
- **Response Format**: JSON
- **Rate Limiting**: Varies by tier

## API Endpoints

The API is organized into several endpoint groups:

### Documents

The Documents endpoints allow you to upload, retrieve, and manage documents:

- [Upload Document](/api-reference/endpoints/documents#upload-document)
- [Get Document](/api-reference/endpoints/documents#get-document)
- [List Documents](/api-reference/endpoints/documents#list-documents)
- [Delete Document](/api-reference/endpoints/documents#delete-document)

### Workflows

The Workflows endpoints allow you to create, manage, and execute document processing workflows:

- [Create Workflow](/api-reference/endpoints/workflows#create-workflow)
- [Get Workflow](/api-reference/endpoints/workflows#get-workflow)
- [List Workflows](/api-reference/endpoints/workflows#list-workflows)
- [Execute Workflow](/api-reference/endpoints/workflows#execute-workflow)
- [Get Workflow Execution](/api-reference/endpoints/workflows#get-workflow-execution)

### Analysis

The Analysis endpoints provide direct access to document analysis capabilities:

- [Extract Text](/api-reference/endpoints/analysis#extract-text)
- [Extract Entities](/api-reference/endpoints/analysis#extract-entities)
- [Classify Document](/api-reference/endpoints/analysis#classify-document)
- [Summarize Document](/api-reference/endpoints/analysis#summarize-document)

## Authentication

All API requests require authentication using an API key. Include your API key in the `Authorization` header of your requests:

```bash
curl -X GET https://api.claryai.com/v1/documents \
  -H "Authorization: Bearer your_api_key_here"
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests. In case of an error, the response body will contain additional information about the error:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "The request was invalid",
    "details": [
      {
        "field": "document_id",
        "message": "Document ID is required"
      }
    ]
  }
}
```

## Pagination

List endpoints support pagination using the `limit` and `offset` query parameters:

```bash
curl -X GET https://api.claryai.com/v1/documents?limit=10&offset=20 \
  -H "Authorization: Bearer your_api_key_here"
```

The response will include pagination metadata:

```json
{
  "data": [...],
  "pagination": {
    "total": 100,
    "limit": 10,
    "offset": 20,
    "next_offset": 30,
    "prev_offset": 10
  }
}
```

## Next Steps

- [Learn about API Authentication](/api-reference/authentication)
- [Explore Document Endpoints](/api-reference/endpoints/documents)
- [Explore Workflow Endpoints](/api-reference/endpoints/workflows)
- [Explore Analysis Endpoints](/api-reference/endpoints/analysis)
