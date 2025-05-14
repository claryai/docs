# Dockerfile for Clary AI Professional
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    CLARY_TIER=professional \
    LLM_INTEGRATION=true \
    LLM_MODEL=cloud

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt .
COPY core/requirements.txt core-requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r core-requirements.txt

# Copy the core code
COPY core /app/core

# Copy the professional-specific code
COPY . /app

# Set up feature flags for professional tier
ENV FEATURE_FLAG_ADVANCED_EXTRACTION=true \
    FEATURE_FLAG_TABLE_EXTRACTION=true \
    FEATURE_FLAG_CUSTOM_TEMPLATES=true \
    FEATURE_FLAG_CLOUD_LLM=true \
    FEATURE_FLAG_ADVANCED_ANALYTICS=true

# Expose port
EXPOSE 8000

# Set up entrypoint
CMD ["uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
