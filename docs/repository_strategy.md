# Repository Strategy for Clary AI Tiered Approach

This document outlines the repository strategy for implementing the Clary AI tiered approach (Lite, Standard, Professional) using separate repositories while maintaining a private core repository.

## Repository Structure

### Private Core Repository

The private core repository contains all the shared code and proprietary components of Clary AI:

- **Repository Name**: `claryai-core`
- **Visibility**: Private
- **Content**:
  - Core processing engine
  - Agentic orchestration layer
  - Extraction service
  - API gateway
  - Web interface
  - License validator
  - Shared utilities and libraries
  - Common documentation
  - Test suites

### Public Tier-Specific Repositories

Each tier has its own public repository that contains tier-specific configurations and documentation:

#### Clary AI Lite Repository

- **Repository Name**: `claryai-lite`
- **Visibility**: Public
- **Content**:
  - `Dockerfile.lite` (references core repository)
  - Tier-specific documentation
  - Setup guides
  - Example configurations
  - Lite-specific tests
  - README with feature list and limitations

#### Clary AI Standard Repository

- **Repository Name**: `claryai-standard`
- **Visibility**: Public
- **Content**:
  - `Dockerfile.standard` (references core repository)
  - Tier-specific documentation
  - Setup guides
  - Example configurations
  - Standard-specific tests
  - README with feature list and advantages over Lite

#### Clary AI Professional Repository

- **Repository Name**: `claryai-professional`
- **Visibility**: Public
- **Content**:
  - `Dockerfile.professional` (references core repository)
  - Tier-specific documentation
  - Setup guides
  - Example configurations
  - Professional-specific tests
  - README with feature list and advantages over Standard

## Implementation Strategy

### Git Submodules Approach

We'll use Git submodules to include the core repository in each tier-specific repository:

1. **Core Repository Setup**:
   ```bash
   # Initialize core repository
   git init claryai-core
   cd claryai-core
   # Add existing code
   git add .
   git commit -m "Initial commit of core repository"
   # Push to private repository
   git remote add origin git@github.com:your-org/claryai-core.git
   git push -u origin main
   ```

2. **Tier Repository Setup**:
   ```bash
   # Initialize tier repository
   git init claryai-lite
   cd claryai-lite
   # Add core repository as submodule
   git submodule add git@github.com:your-org/claryai-core.git core
   # Add tier-specific files
   cp core/Dockerfile.lite ./Dockerfile
   # Create tier-specific documentation
   mkdir docs
   # Commit and push
   git add .
   git commit -m "Initial commit of Lite repository"
   git remote add origin git@github.com:your-org/claryai-lite.git
   git push -u origin main
   ```

3. **Submodule Management**:
   ```bash
   # Update submodule to latest version
   git submodule update --remote
   git add core
   git commit -m "Update core submodule"
   git push
   ```

### Alternative: CI/CD Pipeline Approach

As an alternative to Git submodules, we can use CI/CD pipelines to build Docker images:

1. **Core Repository**:
   - Contains all code and Dockerfiles
   - CI/CD pipeline builds base images and pushes to private registry

2. **Tier Repositories**:
   - Contain only documentation and configuration
   - CI/CD pipeline pulls base image from private registry
   - Adds tier-specific configuration
   - Builds and pushes public images

## Feature Flag Implementation

To control which features are available in each tier, we'll use environment variables and configuration settings:

1. **Environment Variables**:
   ```
   # Lite tier
   TIER=lite
   LLM_INTEGRATION=false
   
   # Standard tier
   TIER=standard
   LLM_INTEGRATION=true
   LLM_MODEL=phi-4-multimodal
   
   # Professional tier
   TIER=professional
   LLM_INTEGRATION=true
   LLM_MODEL=llama-3-8b
   CLOUD_LLM_SUPPORT=true
   ```

2. **Feature Checks in Code**:
   ```python
   # Example feature check
   def check_feature_available(feature_name, tier):
       tier_features = {
           "lite": ["basic_extraction"],
           "standard": ["basic_extraction", "advanced_extraction", "table_extraction"],
           "professional": ["basic_extraction", "advanced_extraction", "table_extraction", "custom_templates"],
       }
       return feature_name in tier_features.get(tier, [])
   ```

## Version Control Strategy

1. **Semantic Versioning**:
   - Core repository uses semantic versioning (e.g., 1.2.3)
   - Tier repositories reference specific versions of core

2. **Release Branches**:
   - `main` branch for active development
   - `release-x.y.z` branches for releases
   - `hotfix-x.y.z` branches for urgent fixes

3. **Tagging**:
   - Tag each release with version number
   - Include tier in tag for tier-specific repositories

## Documentation Strategy

1. **Core Documentation**:
   - Architecture overview
   - API documentation
   - Development guides
   - Contribution guidelines

2. **Tier-Specific Documentation**:
   - Installation guides
   - Configuration options
   - Feature lists
   - Upgrade paths
   - Hardware requirements

## Benefits of This Approach

1. **License Control**: Each tier can have its own licensing terms
2. **Simplified Distribution**: Users only need to access the repository for their specific tier
3. **Cleaner Versioning**: Each tier can have its own versioning strategy
4. **Marketing Differentiation**: Clear separation between product tiers for marketing purposes
5. **Security**: Core proprietary code remains in the private repository
6. **Maintainability**: Changes to core code automatically propagate to all tiers
7. **Scalability**: Easy to add new tiers or modify existing ones
