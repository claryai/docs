---
title: 'Upgrade Guide'
description: 'Guide for upgrading between Clary AI tiers'
---

# Upgrade Guide

This guide provides instructions for upgrading between Clary AI tiers.

## Upgrading from Lite to Standard

### Prerequisites

- Clary AI Lite installed and running
- Docker environment with sufficient resources for Standard tier
- API key for Standard tier (contact sales to obtain one)

### Upgrade Steps

1. **Backup your data**:
   ```bash
   docker exec -it claryai backup
   ```

2. **Stop the current container**:
   ```bash
   docker stop claryai
   docker rm claryai
   ```

3. **Update your configuration file**:
   ```yaml
   # ~/.claryai/config.yaml
   # Add Standard tier configuration
   auth:
     enabled: true
     api_key: your_standard_tier_api_key_here

   # Update model configuration
   models:
     document_processing:
       enabled: true
     reasoning:
       enabled: true
       model: phi-4-multimodal
   ```

4. **Pull the Standard tier image**:
   ```bash
   docker pull claryai/clary-ai:standard
   ```

5. **Start the new container**:
   ```bash
   docker run -d \
     --name claryai \
     -p 8000:8000 \
     -v ~/.claryai:/app/config \
     claryai/clary-ai:standard
   ```

6. **Verify the upgrade**:
   ```bash
   curl http://localhost:8000/health
   ```

   You should see a response indicating the Standard tier:
   ```json
   {
     "status": "healthy",
     "version": "1.0.0",
     "tier": "standard"
   }
   ```

### Post-Upgrade Steps

1. **Update API clients** to use the new API key
2. **Explore new features** available in the Standard tier
3. **Update workflows** to leverage the Phi-4 Multimodal model

## Upgrading from Standard to Professional

### Prerequisites

- Clary AI Standard installed and running
- Docker environment with sufficient resources for Professional tier
- API key for Professional tier (contact sales to obtain one)
- Consultation with Clary AI support team

### Upgrade Steps

1. **Backup your data**:
   ```bash
   docker exec -it claryai backup
   ```

2. **Stop the current container**:
   ```bash
   docker stop claryai
   docker rm claryai
   ```

3. **Update your configuration file**:
   ```yaml
   # ~/.claryai/config.yaml
   # Add Professional tier configuration
   auth:
     enabled: true
     api_key: your_professional_tier_api_key_here

   # Update model configuration
   models:
     document_processing:
       enabled: true
       advanced_features: true
     reasoning:
       enabled: true
       model: llama-4
       cloud_connection:
         enabled: true
         api_key: your_cloud_api_key_here
   ```

4. **Pull the Professional tier image**:
   ```bash
   docker pull claryai/clary-ai:professional
   ```

5. **Start the new container**:
   ```bash
   docker run -d \
     --name claryai \
     -p 8000:8000 \
     -v ~/.claryai:/app/config \
     claryai/clary-ai:professional
   ```

6. **Verify the upgrade**:
   ```bash
   curl http://localhost:8000/health
   ```

   You should see a response indicating the Professional tier:
   ```json
   {
     "status": "healthy",
     "version": "1.0.0",
     "tier": "professional"
   }
   ```

### Post-Upgrade Steps

1. **Update API clients** to use the new API key
2. **Configure cloud LLM connections** if needed
3. **Set up advanced security features**
4. **Update workflows** to leverage the new capabilities
5. **Schedule a consultation** with the support team for optimization

## Downgrading

If you need to downgrade to a lower tier, the process is similar to upgrading, but you should be aware of the following:

- Some features will no longer be available
- Workflows using tier-specific features will need to be modified
- Data created with higher-tier features may not be fully accessible

Contact the support team for assistance with downgrading.

## Troubleshooting

### Common Issues

1. **Container fails to start after upgrade**:
   - Check Docker logs: `docker logs claryai`
   - Verify that your configuration file is properly formatted
   - Ensure you have sufficient resources for the new tier

2. **API returns authentication errors**:
   - Verify that your API key is correctly set in the configuration
   - Ensure you're using the correct API key for your tier

3. **Features not available after upgrade**:
   - Verify that you're using the correct Docker image for your tier
   - Check your configuration file for any missing settings
   - Restart the container to apply all changes

### Getting Help

If you encounter issues during the upgrade process, contact our support team:

- Email: support@claryai.com
- Support portal: https://support.claryai.com
- Documentation: https://docs.claryai.com

## Next Steps

- [Compare all tiers](/tiers/overview)
- [Learn about the Lite tier](/tiers/lite)
- [Learn about the Standard tier](/tiers/standard)
- [Learn about the Professional tier](/tiers/professional)
