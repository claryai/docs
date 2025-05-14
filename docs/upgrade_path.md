# Upgrade Path for Clary AI Tiers

This document outlines the upgrade paths between different tiers of Clary AI (Lite, Standard, Professional), including the technical implementation, data migration process, and user experience.

## Overview

Clary AI is designed to allow seamless upgrades between tiers, ensuring that users can start with a lower tier and upgrade as their needs grow without losing data or disrupting their workflows.

## Upgrade Scenarios

### Lite to Standard Upgrade

#### Technical Implementation

1. **License Key Update**:
   - User obtains a new Standard tier license key
   - The license key is validated with the license server
   - The container is restarted with the new tier configuration

2. **Container Reconfiguration**:
   ```bash
   # Stop the current container
   docker-compose down
   
   # Update the .env file with the new tier
   sed -i 's/TIER=lite/TIER=standard/g' .env
   sed -i 's/LLM_INTEGRATION=false/LLM_INTEGRATION=true/g' .env
   echo "LLM_MODEL=phi-4-multimodal" >> .env
   
   # Pull the Standard tier image
   docker-compose pull
   
   # Start the new container
   docker-compose up -d
   ```

3. **Model Download**:
   - The Standard tier container automatically downloads the Phi-4 Multimodal model
   - Progress is displayed to the user during the download
   - The system is ready to use once the model is downloaded

#### Data Migration

1. **Database Migration**:
   - The database schema is compatible across tiers
   - No schema migration is required
   - All existing data is preserved

2. **Document Storage**:
   - All processed documents are preserved
   - Document metadata is updated to reflect new capabilities
   - Previously processed documents can be reprocessed with new features

3. **User Settings**:
   - User settings and preferences are preserved
   - New settings specific to the Standard tier are initialized with defaults

#### User Experience

1. **Upgrade Process**:
   - User initiates upgrade from the web interface
   - User enters the new license key
   - System validates the key and initiates the upgrade
   - Progress is displayed during the upgrade
   - User is notified when the upgrade is complete

2. **New Features Introduction**:
   - User is presented with a guided tour of new features
   - Documentation for new features is made available
   - Sample workflows demonstrate new capabilities

3. **Reprocessing Option**:
   - User is given the option to reprocess existing documents with new capabilities
   - Batch reprocessing is available for multiple documents
   - Original results are preserved until reprocessing is complete

### Standard to Professional Upgrade

#### Technical Implementation

1. **License Key Update**:
   - User obtains a new Professional tier license key
   - The license key is validated with the license server
   - The container is restarted with the new tier configuration

2. **Container Reconfiguration**:
   ```bash
   # Stop the current container
   docker-compose down
   
   # Update the .env file with the new tier
   sed -i 's/TIER=standard/TIER=professional/g' .env
   sed -i 's/LLM_MODEL=phi-4-multimodal/LLM_MODEL=llama-3-8b/g' .env
   echo "CLOUD_LLM_SUPPORT=true" >> .env
   
   # Pull the Professional tier image
   docker-compose pull
   
   # Start the new container
   docker-compose up -d
   ```

3. **Model Download**:
   - The Professional tier container automatically downloads the Llama 3 8B model
   - Progress is displayed to the user during the download
   - The system is ready to use once the model is downloaded

4. **Cloud LLM Configuration**:
   - User is prompted to configure cloud LLM connections
   - API keys and endpoints can be configured
   - Connection is tested and validated

#### Data Migration

1. **Database Migration**:
   - The database schema is compatible across tiers
   - No schema migration is required
   - All existing data is preserved

2. **Document Storage**:
   - All processed documents are preserved
   - Document metadata is updated to reflect new capabilities
   - Previously processed documents can be reprocessed with new features

3. **Template Migration**:
   - Standard templates are preserved
   - New template capabilities are enabled
   - Custom template creation is enabled

#### User Experience

1. **Upgrade Process**:
   - User initiates upgrade from the web interface
   - User enters the new license key
   - System validates the key and initiates the upgrade
   - Progress is displayed during the upgrade
   - User is notified when the upgrade is complete

2. **New Features Introduction**:
   - User is presented with a guided tour of new features
   - Documentation for new features is made available
   - Sample workflows demonstrate new capabilities

3. **Cloud LLM Setup**:
   - User is guided through cloud LLM setup
   - Connection options are explained
   - Best practices for cloud LLM usage are provided

## Implementation Details

### License Validation

The license validation system checks the tier associated with the license key:

```python
def validate_license(api_key: str, container_id: str) -> Tuple[bool, str, str]:
    """
    Validate the license with the license server.
    
    Args:
        api_key: The API key to validate.
        container_id: The unique ID of this container.
        
    Returns:
        Tuple[bool, str, str]: A tuple containing:
            - A boolean indicating if the license is valid
            - The tier associated with the license
            - An error message if the license is not valid
    """
    # Hash the API key for secure transmission
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    try:
        # Send validation request to license server
        response = requests.post(
            settings.LICENSE_SERVER_URL,
            json={
                "key_hash": key_hash,
                "container_id": container_id,
                "timestamp": int(time.time())
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("valid", False), data.get("tier", "lite"), data.get("message", "")
        else:
            return False, "lite", f"License server error: {response.status_code}"
                
    except Exception as e:
        return False, "lite", f"License validation error: {str(e)}"
```

### Feature Activation

Features are activated based on the tier:

```python
def activate_features_for_tier(tier: str) -> None:
    """
    Activate features for the specified tier.
    
    Args:
        tier: The tier to activate features for.
    """
    # Get tier configuration
    tier_config = settings.API_KEY_TIERS.get(tier, {})
    
    # Set environment variables
    os.environ["TIER"] = tier
    os.environ["LLM_INTEGRATION"] = str(tier_config.get("llm_integration", False)).lower()
    
    if tier_config.get("llm_integration", False):
        os.environ["LLM_MODEL"] = tier_config.get("default_llm", "")
    
    if tier == "professional":
        os.environ["CLOUD_LLM_SUPPORT"] = "true"
    else:
        os.environ["CLOUD_LLM_SUPPORT"] = "false"
    
    # Reload settings
    settings.reload()
    
    # Log activation
    logger.info(f"Activated features for tier: {tier}")
    logger.info(f"LLM integration: {os.environ.get('LLM_INTEGRATION')}")
    logger.info(f"LLM model: {os.environ.get('LLM_MODEL', 'None')}")
    logger.info(f"Cloud LLM support: {os.environ.get('CLOUD_LLM_SUPPORT')}")
```

### Model Management

Models are managed based on the tier:

```python
def download_models_for_tier(tier: str) -> None:
    """
    Download models for the specified tier.
    
    Args:
        tier: The tier to download models for.
    """
    if tier == "lite":
        # No models to download for Lite tier
        logger.info("No models to download for Lite tier")
        return
    
    if tier == "standard":
        # Download Phi-4 Multimodal model for Standard tier
        logger.info("Downloading Phi-4 Multimodal model for Standard tier")
        download_model("llm", "phi-4-multimodal")
    
    if tier == "professional":
        # Download Llama 3 8B model for Professional tier
        logger.info("Downloading Llama 3 8B model for Professional tier")
        download_model("llm", "llama-3-8b")
```

## Upgrade Scripts

### Lite to Standard Upgrade Script

```bash
#!/bin/bash
# upgrade_to_standard.sh

# Check if a license key was provided
if [ -z "$1" ]; then
    echo "Usage: $0 <license_key>"
    exit 1
fi

LICENSE_KEY=$1

# Validate the license key
echo "Validating license key..."
RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"key\": \"$LICENSE_KEY\", \"container_id\": \"$(hostname)\"}" \
    https://api.claryai.com/license/validate)

VALID=$(echo $RESPONSE | jq -r '.valid')
TIER=$(echo $RESPONSE | jq -r '.tier')

if [ "$VALID" != "true" ]; then
    echo "Invalid license key"
    exit 1
fi

if [ "$TIER" != "standard" ]; then
    echo "This license key is for tier: $TIER, not standard"
    exit 1
fi

# Stop the current container
echo "Stopping current container..."
docker-compose down

# Update the .env file
echo "Updating configuration..."
sed -i 's/TIER=lite/TIER=standard/g' .env
sed -i 's/LLM_INTEGRATION=false/LLM_INTEGRATION=true/g' .env
echo "LLM_MODEL=phi-4-multimodal" >> .env

# Update the license key
sed -i "s/API_KEY=.*/API_KEY=$LICENSE_KEY/g" .env

# Pull the Standard tier image
echo "Pulling Standard tier image..."
docker-compose pull

# Start the new container
echo "Starting new container..."
docker-compose up -d

echo "Upgrade to Standard tier complete!"
echo "The system is now downloading the Phi-4 Multimodal model. This may take some time."
echo "You can check the progress with: docker-compose logs -f api"
```

### Standard to Professional Upgrade Script

```bash
#!/bin/bash
# upgrade_to_professional.sh

# Check if a license key was provided
if [ -z "$1" ]; then
    echo "Usage: $0 <license_key>"
    exit 1
fi

LICENSE_KEY=$1

# Validate the license key
echo "Validating license key..."
RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"key\": \"$LICENSE_KEY\", \"container_id\": \"$(hostname)\"}" \
    https://api.claryai.com/license/validate)

VALID=$(echo $RESPONSE | jq -r '.valid')
TIER=$(echo $RESPONSE | jq -r '.tier')

if [ "$VALID" != "true" ]; then
    echo "Invalid license key"
    exit 1
fi

if [ "$TIER" != "professional" ]; then
    echo "This license key is for tier: $TIER, not professional"
    exit 1
fi

# Stop the current container
echo "Stopping current container..."
docker-compose down

# Update the .env file
echo "Updating configuration..."
sed -i 's/TIER=standard/TIER=professional/g' .env
sed -i 's/LLM_MODEL=phi-4-multimodal/LLM_MODEL=llama-3-8b/g' .env
echo "CLOUD_LLM_SUPPORT=true" >> .env

# Update the license key
sed -i "s/API_KEY=.*/API_KEY=$LICENSE_KEY/g" .env

# Pull the Professional tier image
echo "Pulling Professional tier image..."
docker-compose pull

# Start the new container
echo "Starting new container..."
docker-compose up -d

echo "Upgrade to Professional tier complete!"
echo "The system is now downloading the Llama 3 8B model. This may take some time."
echo "You can check the progress with: docker-compose logs -f api"
```
