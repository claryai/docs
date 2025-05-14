---
title: 'Installation'
description: 'Detailed installation instructions for Clary AI'
---

# Installation Guide

This guide provides detailed instructions for installing and configuring Clary AI on your system.

## System Requirements

- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB+ recommended
- **Storage**: 20GB+ free space
- **Operating System**: Linux, macOS, or Windows with Docker support
- **Docker**: Version 20.10.0 or higher
- **Internet Connection**: Required for pulling Docker images and model downloads

## Installation Methods

### Method 1: Docker (Recommended)

1. **Pull the Docker image**:

   ```bash
   docker pull claryai/clary-ai:latest
   ```

2. **Create a configuration directory**:

   ```bash
   mkdir -p ~/.claryai
   ```

3. **Create a configuration file**:

   Create a file named `config.yaml` in the `~/.claryai` directory with the following content:

   ```yaml
   # Server configuration
   server:
     port: 8000
     host: 0.0.0.0
     workers: 4

   # Authentication configuration
   auth:
     enabled: true
     api_key: your_api_key_here  # Only for Standard and Professional tiers

   # Document processing configuration
   document_processing:
     max_file_size_mb: 50
     supported_formats:
       - pdf
       - docx
       - txt
       - jpg
       - png

   # Model configuration
   models:
     document_processing:
       enabled: true
     reasoning:
       enabled: true
       model: phi-4-multimodal  # Only for Standard tier
   ```

4. **Run the Docker container**:

   ```bash
   docker run -d \
     --name claryai \
     -p 8000:8000 \
     -v ~/.claryai:/app/config \
     claryai/clary-ai:latest
   ```

### Method 2: Docker Compose

1. **Create a Docker Compose file**:

   Create a file named `docker-compose.yml` with the following content:

   ```yaml
   version: '3'
   services:
     claryai:
       image: claryai/clary-ai:latest
       ports:
         - "8000:8000"
       volumes:
         - ~/.claryai:/app/config
       restart: unless-stopped
   ```

2. **Start the services**:

   ```bash
   docker-compose up -d
   ```

## Post-Installation Steps

### Verify Installation

Check if Clary AI is running:

```bash
curl http://localhost:8000/health
```

You should see a response like:

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Configure API Access

To use the API, you'll need to include your API key in the request headers:

```bash
curl -X GET http://localhost:8000/api/v1/status \
  -H "Authorization: Bearer your_api_key_here"
```

## Troubleshooting

### Common Issues

1. **Docker container fails to start**:
   - Check Docker logs: `docker logs claryai`
   - Ensure the configuration file is properly formatted
   - Verify that the ports are not already in use

2. **API returns authentication errors**:
   - Verify that your API key is correctly set in the configuration
   - Ensure you're including the API key in the request headers

3. **Document processing fails**:
   - Check if the document format is supported
   - Verify that the document size is within the configured limits

## Next Steps

Now that you have Clary AI installed, you can:

- [Learn about the core concepts](/concepts/document-processing/index)
- [Explore the API reference](/api-reference/overview)
- [Compare different tiers](/tiers/overview)
