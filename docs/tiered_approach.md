# Clary AI Tiered Approach

This document provides a comprehensive overview of the Clary AI tiered approach, including repository strategy, implementation details, and documentation.

## Overview

Clary AI is a document processing platform with agentic capabilities, built on open source AI models. It is designed to be self-hosted via Docker containers and offers a commercial API service that clients can connect to.

The platform is offered in three tiers:

1. **Clary AI Lite**: A lightweight version with no pre-integrated LLM, where users would need to configure their own model connections
2. **Clary AI Standard**: Mid-tier version pre-integrated with Phi-4 Multimodal for local document processing
3. **Clary AI Professional**: Premium version that connects to hosted/cloud LLM models for enhanced performance

## Repository Strategy

To implement the tiered approach, Clary AI uses a repository strategy that separates the core codebase from tier-specific configurations:

### Private Core Repository

- **Repository Name**: `claryai-core`
- **Visibility**: Private
- **Content**: Core processing engine, agentic orchestration layer, extraction service, API gateway, web interface, license validator, shared utilities and libraries

### Public Tier-Specific Repositories

#### Clary AI Lite Repository

- **Repository Name**: `claryai-lite`
- **Visibility**: Public
- **Content**: `Dockerfile.lite`, tier-specific documentation, setup guides, example configurations

#### Clary AI Standard Repository

- **Repository Name**: `claryai-standard`
- **Visibility**: Public
- **Content**: `Dockerfile.standard`, tier-specific documentation, setup guides, example configurations

#### Clary AI Professional Repository

- **Repository Name**: `claryai-professional`
- **Visibility**: Public
- **Content**: `Dockerfile.professional`, tier-specific documentation, setup guides, example configurations

## Implementation Strategy

The implementation of the tiered approach involves several key components:

### Git Submodules

Each tier-specific repository includes the core repository as a Git submodule:

```bash
# Initialize tier repository
git init claryai-lite
cd claryai-lite
# Add core repository as submodule
git submodule add git@github.com:your-org/claryai-core.git core
```

### Feature Flags

Feature flags are used to control which features are available in each tier:

```python
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

### Docker Configuration

Each tier has its own Dockerfile that extends the base Dockerfile:

```dockerfile
# Lite tier
FROM claryai-core:latest
ENV TIER=lite
ENV LLM_INTEGRATION=false

# Standard tier
FROM claryai-core:latest
ENV TIER=standard
ENV LLM_INTEGRATION=true
ENV LLM_MODEL=phi-4-multimodal

# Professional tier
FROM claryai-core:latest
ENV TIER=professional
ENV LLM_INTEGRATION=true
ENV LLM_MODEL=llama-3-8b
ENV CLOUD_LLM_SUPPORT=true
```

### Model Registry

The model registry manages AI models across different tiers:

```python
def get_models_for_tier(self, tier: str) -> List[str]:
    """
    Get a list of models available for a given tier.

    Args:
        tier: The tier to check.

    Returns:
        List[str]: List of model names available for the tier.
    """
    models = []

    # For lite tier, no models are available
    if tier == "lite":
        return []

    # For standard tier, only standard models are available
    if tier == "standard":
        for model_name, config in self.model_configs.items():
            if config.get("tier") == "standard":
                models.append(model_name)
        return models

    # For professional tier, all models are available
    if tier == "professional":
        return list(self.model_configs.keys())

    return models
```

## Documentation

Comprehensive documentation is provided for the tiered approach:

1. **Repository Strategy**: [Repository Strategy](repository_strategy.md)
2. **Tier Comparison**: [Tier Comparison](tier_comparison.md)
3. **Implementation Guide**: [Implementation Guide](implementation_guide.md)
4. **Testing Strategy**: [Testing Strategy](testing_strategy.md)
5. **Upgrade Path**: [Upgrade Path](upgrade_path.md)
6. **Monitoring and Analytics**: [Monitoring and Analytics](monitoring_analytics.md)
7. **Hardware Detection**: [Hardware Detection](hardware_detection.md)
8. **Model Registry**: [Model Registry](model_registry.md)
9. **Implementation Timeline**: [Implementation Timeline](implementation_timeline.md)

## Feature Comparison

| Feature | Clary AI Lite | Clary AI Standard | Clary AI Professional |
|---------|---------------|-------------------|------------------------|
| **Document Processing** |
| Basic Document Extraction | ✅ | ✅ | ✅ |
| Advanced Document Extraction | ❌ | ✅ | ✅ |
| Table Extraction | ❌ | ✅ | ✅ |
| Custom Templates | ❌ | ❌ | ✅ |
| **AI Models** |
| Pre-integrated LLM | ❌ | ✅ (Phi-4 Multimodal) | ✅ (Llama 3 8B) |
| Custom LLM Integration | ✅ (BYO) | ✅ | ✅ |
| Cloud LLM Support | ❌ | ❌ | ✅ |
| **Processing Limits** |
| Daily Document Limit | 50 | 500 | Unlimited |
| Monthly Document Limit | 1,000 | 10,000 | Unlimited |

## Hardware Requirements

### Clary AI Lite

- **CPU**: 2+ cores
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 5GB for installation, plus storage for documents
- **GPU**: Not required

### Clary AI Standard

- **CPU**: 4+ cores
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB for installation (including models), plus storage for documents
- **GPU**: Optional, improves performance

### Clary AI Professional

- **CPU**: 8+ cores
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 20GB for installation (including models), plus storage for documents
- **GPU**: Recommended for optimal performance

## Upgrade Path

Clary AI is designed to allow seamless upgrades between tiers:

1. **Lite to Standard Upgrade**:
   - User obtains a new Standard tier license key
   - The license key is validated with the license server
   - The container is restarted with the new tier configuration
   - The Standard tier container automatically downloads the Phi-4 Multimodal model

2. **Standard to Professional Upgrade**:
   - User obtains a new Professional tier license key
   - The license key is validated with the license server
   - The container is restarted with the new tier configuration
   - The Professional tier container automatically downloads the Llama 3 8B model
   - User is prompted to configure cloud LLM connections

## Monitoring and Analytics

Clary AI includes comprehensive monitoring and analytics:

1. **Usage Tracking**: Track how customers use each tier
2. **Performance Monitoring**: Identify bottlenecks and optimize performance
3. **Error Tracking**: Detect and diagnose errors
4. **License Validation**: Monitor license usage and compliance
5. **User Feedback**: Gather user feedback to guide development

## Implementation Timeline

The implementation of the Clary AI tiered approach is divided into several phases:

1. **Phase 1**: Repository Structure and Documentation (Weeks 1-2)
2. **Phase 2**: Feature Flags and Tier-Specific Functionality (Weeks 3-4)
3. **Phase 3**: Model Registry and Hardware Detection (Weeks 5-6)
4. **Phase 4**: Monitoring, Analytics, and Testing (Weeks 7-8)
5. **Phase 5**: Documentation and Release Preparation (Weeks 9-10)

## Conclusion

The Clary AI tiered approach provides a flexible and scalable solution for document processing with agentic capabilities. By offering three tiers (Lite, Standard, Professional), Clary AI can meet the needs of a wide range of users, from small businesses to large enterprises.

The repository strategy, with a private core repository and public tier-specific repositories, ensures that proprietary code remains protected while allowing users to access the appropriate tier for their needs. The implementation of feature flags, Docker configurations, and the model registry provides a robust foundation for the tiered approach.

Comprehensive documentation, testing, monitoring, and analytics ensure that Clary AI is reliable, performant, and user-friendly across all tiers.
