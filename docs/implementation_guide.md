# Implementation Guide for Clary AI Tiered Approach

This guide provides detailed instructions for implementing the Clary AI tiered approach using separate repositories for each tier (Lite, Standard, Professional) while maintaining a private core repository.

## Prerequisites

Before implementing the tiered approach, ensure you have:

- Git installed and configured
- Access to GitHub or another Git hosting service
- Docker and Docker Compose installed
- Understanding of CI/CD pipelines (GitHub Actions, GitLab CI, etc.)

## Step 1: Set Up the Core Repository

### 1.1 Create the Core Repository

```bash
# Create a new directory for the core repository
mkdir claryai-core
cd claryai-core

# Initialize Git repository
git init

# Create a .gitignore file
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
htmlcov/

# Node.js
node_modules/
npm-debug.log
yarn-debug.log
yarn-error.log
.pnp/
.pnp.js
coverage/
.next/
out/
build/
*.pem

# Docker
.dockerignore

# Environment variables
.env
.env.*
!.env.example

# Models
models/
*.gguf
*.bin
*.pt
*.onnx

# Data
data/
uploads/
processed/

# IDE
.idea/
.vscode/
*.swp
*.swo
.project
.classpath
.c9/
*.launch
.settings/
*.sublime-workspace
EOF

# Create a README.md file
cat > README.md << EOF
# Clary AI Core

This is the core repository for Clary AI, a document processing platform with agentic capabilities.

## Overview

This repository contains the core components of Clary AI:

- Core Processing Engine
- Agentic Orchestration Layer
- Extraction Service
- API Gateway
- Web Interface
- License Validator

## Development

See the [Development Guide](docs/development.md) for instructions on setting up a development environment.

## License

This repository is private and proprietary. All rights reserved.
EOF

# Add existing code (assuming you're in the root of the existing project)
# Copy all files except those that will be tier-specific
cp -r api .
cp -r web .
cp -r license-server .
cp -r docs .
mkdir -p scripts

# Create a base Dockerfile that will be extended by tier-specific Dockerfiles
cat > Dockerfile.base << EOF
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    libpq-dev \\
    tesseract-ocr \\
    libtesseract-dev \\
    poppler-utils \\
    ghostscript \\
    libmagic1 \\
    pandoc \\
    libgl1-mesa-glx \\
    libglib2.0-0 \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for models and data
RUN mkdir -p /app/models /app/data

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Commit the changes
git add .
git commit -m "Initial commit of core repository"

# Create a GitHub repository and push
# Replace 'your-org' with your GitHub organization or username
git remote add origin git@github.com:your-org/claryai-core.git
git push -u origin main
```

### 1.2 Set Up Feature Flags

Modify the configuration to support feature flags for different tiers:

```python
# api/app/core/config.py

# API key tiers and limits
API_KEY_TIERS: Dict[str, Dict[str, Any]] = {
    "lite": {
        "daily_limit": 50,
        "monthly_limit": 1000,
        "features": ["basic_extraction"],
        "description": "Lightweight version with no pre-integrated LLM",
        "llm_integration": False,
    },
    "standard": {
        "daily_limit": 500,
        "monthly_limit": 10000,
        "features": ["basic_extraction", "advanced_extraction", "table_extraction"],
        "description": "Mid-tier version pre-integrated with Phi-4 Multimodal",
        "llm_integration": True,
        "default_llm": "phi-4-multimodal",
    },
    "professional": {
        "daily_limit": -1,  # unlimited
        "monthly_limit": -1,  # unlimited
        "features": ["basic_extraction", "advanced_extraction", "table_extraction", "custom_templates"],
        "description": "Premium version with cloud LLM connections",
        "llm_integration": True,
        "default_llm": "llama-3-8b",
        "cloud_llm_support": True,
    },
}
```

## Step 2: Set Up Tier-Specific Repositories

### 2.1 Create the Lite Repository

```bash
# Create a new directory for the Lite repository
mkdir claryai-lite
cd claryai-lite

# Initialize Git repository
git init

# Create a .gitmodules file to reference the core repository
cat > .gitmodules << EOF
[submodule "core"]
    path = core
    url = git@github.com:your-org/claryai-core.git
EOF

# Add the core repository as a submodule
git submodule add git@github.com:your-org/claryai-core.git core

# Create a Dockerfile that extends the base Dockerfile
cat > Dockerfile << EOF
FROM claryai-core:latest

# Set environment variables for Lite tier
ENV TIER=lite
ENV LLM_INTEGRATION=false

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Create a docker-compose.yml file
cat > docker-compose.yml << EOF
version: '3'
services:
  web:
    build: ./core/web
    ports:
      - "3000:3000"
    depends_on:
      - api
    volumes:
      - ./data:/app/data
    environment:
      - API_URL=http://api:8000
      - NODE_ENV=development
      - PROJECT_NAME=Clary AI Lite
    restart: unless-stopped

  api:
    build:
      context: ./core
      dockerfile: ../Dockerfile
    ports:
      - "8000:8000"
    depends_on:
      - db
    volumes:
      - ./models:/app/models
      - ./data:/app/data
    environment:
      - MODEL_PATH=/app/models
      - DATABASE_URL=postgresql://claryai:claryai@db:5432/claryai
      - DEBUG=true
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - PROJECT_NAME=Clary AI Lite
      - API_KEY_SALT=claryai
      - LICENSE_VALIDATION_ENABLED=true
      - LICENSE_SERVER_URL=https://api.claryai.com/license
      - CONTAINER_ID=\${CONTAINER_ID:-lite_container}
      - TIER=lite
    restart: unless-stopped

  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=claryai
      - POSTGRES_PASSWORD=claryai
      - POSTGRES_DB=claryai
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
EOF

# Create a README.md file
cat > README.md << EOF
# Clary AI Lite

Clary AI Lite is a lightweight document processing platform with agentic capabilities.

## Features

- Basic document extraction
- API access
- Self-hosted deployment
- Bring your own LLM integration

## Hardware Requirements

- CPU: 2+ cores
- RAM: 4GB minimum, 8GB recommended
- Storage: 5GB for installation, plus storage for documents
- GPU: Not required

## Getting Started

See the [Deployment Guide](docs/deployment.md) for instructions on deploying Clary AI Lite.

## License

This project is licensed under the [MIT License](LICENSE).
EOF

# Create a deployment guide
mkdir -p docs
cat > docs/deployment.md << EOF
# Deployment Guide for Clary AI Lite

This guide provides instructions for deploying Clary AI Lite using Docker.

## Prerequisites

- Docker and Docker Compose installed
- 4GB+ RAM
- 5GB+ free disk space

## Deployment Steps

1. Clone the repository:
   \`\`\`bash
   git clone https://github.com/your-org/claryai-lite.git
   cd claryai-lite
   \`\`\`

2. Initialize and update the submodule:
   \`\`\`bash
   git submodule init
   git submodule update
   \`\`\`

3. Create a \`.env\` file:
   \`\`\`bash
   cp core/.env.example .env
   \`\`\`

4. Start the services:
   \`\`\`bash
   docker-compose up -d
   \`\`\`

5. Access the application:
   - Web UI: http://localhost:3000
   - API: http://localhost:8000
EOF

# Commit the changes
git add .
git commit -m "Initial commit of Lite repository"

# Create a GitHub repository and push
# Replace 'your-org' with your GitHub organization or username
git remote add origin git@github.com:your-org/claryai-lite.git
git push -u origin main
```

### 2.2 Create the Standard Repository

Follow similar steps as for the Lite repository, but with Standard-specific configurations.

### 2.3 Create the Professional Repository

Follow similar steps as for the Lite repository, but with Professional-specific configurations.

## Step 3: Set Up CI/CD Pipelines

### 3.1 Core Repository CI/CD

Create a GitHub Actions workflow for the core repository:

```yaml
# .github/workflows/build.yml
name: Build Core

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v1
    
    - name: Login to GitHub Container Registry
      uses: docker/login-action@v1
      with:
        registry: ghcr.io
        username: ${{ github.repository_owner }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push base image
      uses: docker/build-push-action@v2
      with:
        context: .
        file: ./Dockerfile.base
        push: true
        tags: ghcr.io/${{ github.repository_owner }}/claryai-core:latest
```

### 3.2 Tier Repository CI/CD

Create GitHub Actions workflows for each tier repository.

## Step 4: Testing and Validation

Implement comprehensive testing for each tier to ensure functionality and feature availability.

## Step 5: Documentation

Create detailed documentation for each tier, including setup guides, feature lists, and upgrade paths.
