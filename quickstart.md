---
title: 'Quickstart'
description: 'Get started with Clary AI in minutes'
---

# Quickstart Guide

This guide will help you get started with Clary AI quickly. Follow these steps to set up and start using Clary AI for document processing.

## Prerequisites

Before you begin, make sure you have:

- Docker installed on your system
- An API key (for Standard and Professional tiers)
- Basic familiarity with command-line operations

## Step 1: Install Clary AI

Pull the Docker image:

```bash
docker pull claryai/clary-ai:latest
```

## Step 2: Configure Clary AI

Create a configuration file:

```bash
mkdir -p ~/.claryai
touch ~/.claryai/config.yaml
```

Edit the configuration file with your preferred settings:

```yaml
# Basic configuration
api:
  port: 8000
  host: 0.0.0.0

# API key configuration (for Standard and Professional tiers)
auth:
  api_key: your_api_key_here

# Model configuration
models:
  document_processing:
    enabled: true
  reasoning:
    enabled: true
```

## Step 3: Run Clary AI

Start the Clary AI container:

```bash
docker run -d \
  --name claryai \
  -p 8000:8000 \
  -v ~/.claryai:/app/config \
  claryai/clary-ai:latest
```

## Step 4: Verify Installation

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

## Next Steps

Now that you have Clary AI up and running, you can:

- [Learn about the core concepts](/concepts/document-processing/index)
- [Explore the API reference](/api-reference/overview)
- [Compare different tiers](/tiers/overview)

For more detailed setup instructions, check out the [Installation Guide](/installation).
