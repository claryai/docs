# Development Roadmap

This document outlines the phased development approach for Clary AI, designed to allow incremental implementation and validation.

## Tiered Product Approach

Clary AI will be offered in three tiers:

1. **Clary AI Lite**: A lightweight version with no pre-integrated LLM, where users would need to configure their own model connections
2. **Clary AI Standard**: Mid-tier version pre-integrated with Phi-4 Multimodal for local document processing
3. **Clary AI Professional**: Premium version that connects to hosted/cloud LLM models for enhanced performance

## Implementation Roadmap

### Phase 1: Modular Architecture (1-2 months)

Focus: Building the foundation for tiered deployment

#### Goals
- Implement model registry and management system
- Create tiered Docker images
- Develop hardware detection and recommendation system

#### Tasks
- [x] Set up project structure and dependencies
- [x] Integrate Unstructured.io and Marker for document processing
- [x] Create API key management system
- [x] Implement tiered access control
- [ ] Develop model registry with tier-based access
- [ ] Create Docker configurations for each tier
- [ ] Implement hardware detection for model recommendations
- [ ] Build model download and management system
- [ ] Create documentation for tiered deployment

#### Deliverables
- Working tiered Docker images
- Model registry and management system
- Hardware detection and recommendation system
- Documentation for tiered deployment

### Phase 2: Streamlined Experience (2-3 months)

Focus: Improving user experience and model management

#### Goals
- Implement one-click model switching
- Add delta-update mechanism
- Create admin dashboard for model management

#### Tasks
- [ ] Develop model switching UI
- [ ] Implement delta-update mechanism for models
- [ ] Create admin dashboard for model management
- [ ] Add model performance metrics
- [ ] Implement model caching
- [ ] Add user preference storage
- [ ] Create documentation for model management

#### Deliverables
- One-click model switching
- Delta-update mechanism
- Admin dashboard for model management
- Model performance metrics
- Documentation for model management

### Phase 3: Optimization (3-4 months)

Focus: Optimizing performance and resource usage

#### Goals
- Implement model caching and preloading
- Add performance analytics
- Develop automatic fallback mechanisms

#### Tasks
- [ ] Implement model caching and preloading
- [ ] Add performance analytics
- [ ] Develop automatic fallback mechanisms
- [ ] Optimize memory usage
- [ ] Implement batch processing
- [ ] Add resource monitoring
- [ ] Create documentation for optimization

#### Deliverables
- Model caching and preloading
- Performance analytics
- Automatic fallback mechanisms
- Resource monitoring
- Documentation for optimization

## Technical Considerations

### Hardware Requirements

#### Clary AI Lite
- Minimum: 4GB RAM, 2 CPU cores
- Recommended: 8GB RAM, 4 CPU cores

#### Clary AI Standard
- Minimum: 8GB RAM, 4 CPU cores
- Recommended: 16GB RAM, 6 CPU cores, GPU with 4GB VRAM

#### Clary AI Professional
- Minimum: 16GB RAM, 6 CPU cores
- Recommended: 32GB RAM, 8 CPU cores, GPU with 8GB VRAM

### Model Integration

#### Clary AI Lite
- No pre-integrated models
- Support for connecting to external model servers
- Support for API-based model services

#### Clary AI Standard
- Pre-integrated Phi-4 Multimodal model
- Local model serving
- Basic model management

#### Clary AI Professional
- Pre-integrated Llama 3 8B model
- Support for cloud LLM connections
- Advanced model management
- Model versioning and updates

## Business Considerations

### Pricing Strategy

#### Clary AI Lite
- Free tier with limited document processing
- Pay-as-you-go option for additional documents

#### Clary AI Standard
- Monthly subscription
- Volume-based pricing
- Support for small to medium businesses

#### Clary AI Professional
- Enterprise pricing
- Volume discounts
- Priority support
- Custom integrations

### Licensing Model

All tiers use an API key activation model:
- API keys are tied to subscription plans
- API keys control access to features
- API keys track usage for billing
- API keys can be managed through the admin dashboard
