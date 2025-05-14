---
title: 'API Authentication'
description: 'Authentication methods for the Clary AI API'
---

# API Authentication

All requests to the Clary AI API must be authenticated. This page describes the authentication methods supported by the API.

## API Key Authentication

The primary authentication method is API key authentication. Each API key is associated with a specific tier (Lite, Standard, or Professional) and has specific permissions.

### Obtaining an API Key

API keys can be obtained through the following methods:

- **Self-hosted deployments**: Generate API keys through the admin interface or configuration file
- **Cloud service**: Obtain API keys from the Clary AI dashboard

### Using API Keys

To authenticate using an API key, include it in the `Authorization` header of your requests using the Bearer token format:

```bash
curl -X GET https://api.claryai.com/v1/documents \
  -H "Authorization: Bearer your_api_key_here"
```

### API Key Security

API keys should be kept secure and not exposed in client-side code. Best practices include:

- Store API keys in environment variables or secure key management systems
- Rotate API keys regularly
- Use different API keys for different environments (development, staging, production)
- Set appropriate permissions for each API key

## JWT Authentication

For more advanced use cases, Clary AI also supports JWT (JSON Web Token) authentication. This is particularly useful for integrating with existing authentication systems.

### Generating JWTs

To generate a JWT, you'll need to:

1. Create a JWT with the appropriate claims
2. Sign the JWT with your API key
3. Include the JWT in the `Authorization` header of your requests

Example JWT payload:

```json
{
  "sub": "user_id",
  "iat": 1516239022,
  "exp": 1516242622,
  "tier": "standard"
}
```

### Using JWTs

To authenticate using a JWT, include it in the `Authorization` header of your requests:

```bash
curl -X GET https://api.claryai.com/v1/documents \
  -H "Authorization: Bearer your_jwt_here"
```

## Error Responses

If authentication fails, the API will return a `401 Unauthorized` status code with an error message:

```json
{
  "error": {
    "code": "unauthorized",
    "message": "Invalid API key"
  }
}
```

If the authenticated user doesn't have permission to access a resource, the API will return a `403 Forbidden` status code:

```json
{
  "error": {
    "code": "forbidden",
    "message": "Insufficient permissions"
  }
}
```

## Next Steps

- [Explore the API Overview](/api-reference/overview)
- [Learn about Document Endpoints](/api-reference/endpoints/documents)
- [Learn about Workflow Endpoints](/api-reference/endpoints/workflows)
