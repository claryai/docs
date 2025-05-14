# API Key Management

This document describes the API key management system for Clary AI, including how to create, manage, and use API keys for container activation.

## Overview

Clary AI uses an API key activation model for its Docker containers. Each container requires a valid API key to function, which provides several benefits:

1. **Monetization**: API keys are tied to subscription plans with different tiers and usage limits
2. **Security**: Prevents unauthorized use of the software
3. **Usage Tracking**: Allows monitoring of document processing volume
4. **Feature Control**: Different API key tiers provide access to different features

## API Key Tiers

Clary AI offers three tiers of API keys:

### Free Tier
- **Daily Limit**: 50 documents
- **Monthly Limit**: 1,000 documents
- **Features**: Basic document extraction
- **Validity**: 30 days

### Professional Tier
- **Daily Limit**: 500 documents
- **Monthly Limit**: 10,000 documents
- **Features**: Basic extraction, advanced extraction, table extraction
- **Validity**: Based on subscription

### Enterprise Tier
- **Daily Limit**: Unlimited
- **Monthly Limit**: Unlimited
- **Features**: All features including custom templates
- **Validity**: Based on subscription

## Container Activation

When a Clary AI Docker container starts, it requires a valid API key to function:

1. **Initial Setup**: When first deploying the container, you'll be prompted to enter an API key
2. **Validation**: The container validates the API key with the Clary AI license server
3. **Offline Operation**: Once validated, the container can operate offline for a period (typically 24 hours)
4. **Periodic Validation**: The container periodically validates the API key when internet connectivity is available

## API Key Management Portal

Clary AI provides a web portal for managing API keys:

### Creating API Keys

1. Log in to the Clary AI web portal
2. Navigate to "API Keys" section
3. Click "Create New API Key"
4. Enter a name and description for the key
5. Select the tier (based on your subscription)
6. Set an expiration date (optional)
7. Click "Create"

### Managing API Keys

From the API Keys dashboard, you can:

- **View**: See all your active and inactive API keys
- **Edit**: Change the name, description, or expiration date
- **Revoke**: Immediately invalidate an API key
- **Regenerate**: Create a new key value while keeping the same settings
- **Monitor**: Track usage statistics for each key

### API Key Security

To keep your API keys secure:

1. **Never share** your API keys publicly
2. Use **environment variables** to store API keys in your deployment
3. **Rotate keys** periodically for sensitive deployments
4. Set **expiration dates** for temporary access
5. **Revoke keys** immediately if compromised

## Using API Keys in the API

When making API requests to Clary AI, include the API key in the request header:

```
X-API-Key: your_api_key_here
```

Example using curl:

```bash
curl -X POST \
  https://your-claryai-instance.com/api/v1/documents/upload \
  -H 'X-API-Key: your_api_key_here' \
  -F 'file=@document.pdf'
```

## API Key Endpoints

The following API endpoints are available for managing API keys:

### List API Keys

```
GET /api/v1/api-keys
```

Returns a list of all API keys for the authenticated user.

### Create API Key

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

### Get API Key

```
GET /api/v1/api-keys/{api_key_id}
```

Returns details about a specific API key.

### Update API Key

```
PUT /api/v1/api-keys/{api_key_id}
```

Updates an existing API key.

Request body:
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "is_active": true,
  "tier": "enterprise",
  "valid_days": 90
}
```

### Delete API Key

```
DELETE /api/v1/api-keys/{api_key_id}
```

Deletes an API key.

### Revoke API Key

```
POST /api/v1/api-keys/{api_key_id}/revoke
```

Revokes an API key (sets is_active to false).

### Regenerate API Key

```
POST /api/v1/api-keys/{api_key_id}/regenerate
```

Regenerates the API key value while keeping the same settings.

## Troubleshooting

### Invalid API Key

If you receive an "Invalid API key" error:

1. Verify the API key is entered correctly
2. Check if the API key has been revoked or expired
3. Ensure the API key is for the correct environment (development/production)

### License Validation Failed

If you receive a "License validation failed" error:

1. Check your internet connection
2. Verify the container can reach the license server
3. Ensure your subscription is active
4. Contact support if the issue persists

### Usage Limits Exceeded

If you receive a "Usage limit exceeded" error:

1. Check your current usage in the API key portal
2. Wait for the limit to reset (daily/monthly)
3. Consider upgrading to a higher tier
4. Contact sales for temporary limit increases
