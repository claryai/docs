# Deployment Guide

This guide provides instructions for deploying Clary AI in various environments, from local development to production.

## Prerequisites

Before deploying Clary AI, ensure you have the following:

- Docker and Docker Compose installed
- At least 8GB of RAM for running the models
- 10GB of free disk space
- Internet connection for initial model downloads and API key validation
- Valid API key for container activation
- (Optional) GPU for improved performance

## Local Development Deployment

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/claryai.git
cd claryai
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```
# API Configuration
API_PORT=8000
API_HOST=0.0.0.0
DEBUG=true
PROJECT_NAME=Clary AI

# Database Configuration
DB_USER=claryai
DB_PASSWORD=your_secure_password
DB_NAME=claryai
DB_HOST=db

# Model Configuration
MODEL_PATH=/app/models
OCR_MODEL=tesseract
LAYOUT_MODEL=layoutlm
LLM_MODEL=llama-3-8b

# Security
API_KEY_SALT=your_random_salt_string
JWT_SECRET=your_jwt_secret

# License Configuration
LICENSE_VALIDATION_ENABLED=true
LICENSE_SERVER_URL=https://api.claryai.com/license
LICENSE_CHECK_INTERVAL=24
CONTAINER_ID=your_container_id_here

# Web UI
WEB_PORT=3000
```

### 3. Start the Services

```bash
docker-compose up -d
```

This will start all the required services:
- Web UI on port 3000
- API on port 8000
- PostgreSQL database
- Model server

### 4. Initialize the Database

```bash
docker-compose exec api python scripts/init_db.py
```

### 5. Download Models

```bash
docker-compose exec api python scripts/download_models.py
```

### 6. Activate the Container

When you first access the application, you'll be prompted to enter an API key. You can obtain an API key from the Clary AI website or from your account manager.

```bash
docker-compose exec api python scripts/activate_container.py --api-key YOUR_API_KEY
```

### 7. Access the Application

Open your browser and navigate to:

```
http://localhost:3000
```

## Production Deployment

For production environments, additional security and performance considerations are necessary.

### 1. Configure Production Environment Variables

Create a `.env.production` file:

```
# API Configuration
API_PORT=8000
API_HOST=0.0.0.0
DEBUG=false

# Database Configuration
DB_USER=docuagent
DB_PASSWORD=your_very_secure_password
DB_NAME=docuagent
DB_HOST=db

# Model Configuration
MODEL_PATH=/app/models
OCR_MODEL=paddleocr
LAYOUT_MODEL=layoutlmv3
LLM_MODEL=llama-3-8b

# Security
API_KEY_SALT=your_random_salt_string
JWT_SECRET=your_jwt_secret
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=100

# Web UI
WEB_PORT=3000

# TLS/SSL
ENABLE_TLS=true
TLS_CERT_PATH=/path/to/cert.pem
TLS_KEY_PATH=/path/to/key.pem
```

### 2. Use Production Docker Compose File

Create a `docker-compose.prod.yml` file:

```yaml
version: '3'
services:
  web:
    build:
      context: ./web
      dockerfile: Dockerfile.prod
    ports:
      - "443:3000"
    depends_on:
      - api
    volumes:
      - ./data:/app/data
      - ./certs:/app/certs
    env_file:
      - .env.production
    restart: always

  api:
    build:
      context: ./api
      dockerfile: Dockerfile.prod
    ports:
      - "8443:8000"
    volumes:
      - ./models:/app/models
      - ./data:/app/data
      - ./certs:/app/certs
    env_file:
      - .env.production
    restart: always

  db:
    image: postgres:14
    env_file:
      - .env.production
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}

  redis:
    image: redis:7
    restart: always
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 3. Start the Production Services

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Set Up Reverse Proxy (Optional)

For production deployments, it's recommended to use a reverse proxy like Nginx:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Cloud Deployment Options

### Railway Deployment

[Railway](https://railway.app/) provides a simple way to deploy DocuAgent:

1. Create a new project in Railway
2. Connect your GitHub repository
3. Add PostgreSQL and Redis services
4. Configure environment variables
5. Deploy the application

### Digital Ocean Deployment

1. Create a Droplet with Docker pre-installed
2. SSH into your Droplet
3. Clone your repository
4. Configure environment variables
5. Start the services with Docker Compose

## API Service Hosting

For hosting the commercial API service:

1. Set up a separate deployment for the API service
2. Configure API key authentication
3. Implement usage tracking and billing
4. Set up monitoring and alerting
5. Configure auto-scaling for handling load

## Self-Hosted Docker Configuration

For clients who want to self-host Clary AI:

1. Download the Docker Compose file from your Clary AI account
2. Configure environment variables including your API key
3. Start the container with Docker Compose
4. Validate the API key activation
5. Begin processing documents

Example `docker-compose.client.yml`:

```yaml
version: '3'
services:
  claryai:
    image: claryai/processor:latest
    ports:
      - "3000:3000"
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./config:/app/config
    environment:
      - API_KEY=your_api_key
      - CONTAINER_ID=${CONTAINER_ID:-your_container_id}
      - LICENSE_SERVER_URL=https://api.claryai.com/license
      - LICENSE_CHECK_INTERVAL=24
    restart: always
```

### API Key Activation

The container requires a valid API key to function. When you first start the container, it will attempt to validate the API key with the Clary AI license server. If the validation is successful, the container will be activated and will function normally.

The container will periodically validate the API key with the license server to ensure it remains valid. If the container cannot reach the license server, it will continue to function using the cached validation for the period specified by `LICENSE_CHECK_INTERVAL` (in hours).

## Monitoring and Maintenance

### Health Checks

Implement health checks for all services:

```bash
curl http://localhost:8000/api/v1/system/health
```

You can also check the license status:

```bash
curl -H "X-API-Key: your_api_key" http://localhost:8000/api/v1/system/license
```

### Backup Strategy

1. Set up regular database backups:

```bash
docker-compose exec db pg_dump -U claryai claryai > backup_$(date +%Y%m%d).sql
```

2. Back up extracted data and templates:

```bash
tar -czf data_backup_$(date +%Y%m%d).tar.gz ./data
```

### Updating the Application

1. Pull the latest changes:

```bash
git pull origin main
```

2. Rebuild and restart the services:

```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## Troubleshooting

### API Key and License Issues

#### Invalid API Key
- Verify the API key is entered correctly
- Check if the API key has been revoked or expired
- Ensure the API key is for the correct environment (development/production)

#### License Validation Failed
- Check your internet connection
- Verify the container can reach the license server
- Ensure your subscription is active
- Contact support if the issue persists

#### Usage Limits Exceeded
- Check your current usage in the API key portal
- Wait for the limit to reset (daily/monthly)
- Consider upgrading to a higher tier
- Contact sales for temporary limit increases

### Common Issues

1. **Models not loading**:
   - Check if models were downloaded correctly
   - Verify MODEL_PATH environment variable
   - Ensure sufficient disk space

2. **Database connection issues**:
   - Verify database credentials
   - Check if database service is running
   - Ensure database initialization was completed

3. **Performance problems**:
   - Check system resources (CPU, RAM, disk)
   - Consider using GPU for model inference
   - Optimize model selection for your hardware

### Logs

Access logs for troubleshooting:

```bash
# API logs
docker-compose logs api

# Web UI logs
docker-compose logs web

# Database logs
docker-compose logs db
```

## Security Considerations

1. **API Key Management**:
   - Rotate API keys regularly
   - Use strong, unique keys
   - Implement key revocation

2. **Data Protection**:
   - Enable TLS/SSL for all connections
   - Implement data encryption at rest
   - Configure proper access controls

3. **Model Security**:
   - Validate model sources
   - Scan models for vulnerabilities
   - Keep models updated
