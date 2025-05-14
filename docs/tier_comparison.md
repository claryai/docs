# Clary AI Tier Comparison

This document provides a detailed comparison of the different tiers of Clary AI: Lite, Standard, and Professional.

## Feature Comparison Matrix

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
| **Support** |
| Community Support | ✅ | ✅ | ✅ |
| Email Support | ❌ | ✅ | ✅ |
| Priority Support | ❌ | ❌ | ✅ |
| **Deployment** |
| Docker Deployment | ✅ | ✅ | ✅ |
| Kubernetes Support | ❌ | ✅ | ✅ |
| High Availability | ❌ | ❌ | ✅ |
| **Additional Features** |
| API Access | ✅ (Limited) | ✅ | ✅ |
| Batch Processing | ❌ | ✅ | ✅ |
| Workflow Automation | ❌ | ❌ | ✅ |

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

## Target Markets

### Clary AI Lite

- **Target Users**: Small businesses, individual professionals, developers
- **Use Cases**:
  - Basic document data extraction
  - Integration with existing systems
  - Development and testing
- **Industries**: Any industry with basic document processing needs

### Clary AI Standard

- **Target Users**: Medium-sized businesses, accounting firms, legal offices
- **Use Cases**:
  - Regular document processing
  - Invoice and receipt processing
  - Contract analysis
  - Form data extraction
- **Industries**: Accounting, legal, healthcare, real estate

### Clary AI Professional

- **Target Users**: Large enterprises, high-volume processing operations
- **Use Cases**:
  - High-volume document processing
  - Complex document understanding
  - Integration with enterprise systems
  - Custom document templates
- **Industries**: Financial services, insurance, healthcare, government

## Pricing Strategy

### Clary AI Lite

- **Model**: Free tier with usage limits
- **Pricing**: Free for up to 1,000 documents per month
- **Overage**: Pay-as-you-go for additional documents

### Clary AI Standard

- **Model**: Subscription-based
- **Pricing**: $X per month for up to 10,000 documents
- **Overage**: Additional documents at $Y per 1,000 documents

### Clary AI Professional

- **Model**: Enterprise pricing
- **Pricing**: Custom pricing based on volume and requirements
- **Additional**: Volume discounts available

## Upgrade Path

### Lite to Standard Upgrade

- **Process**: Simple license key upgrade
- **Data Migration**: Automatic, no data loss
- **Configuration**: Minimal changes required
- **Benefits**:
  - Pre-integrated Phi-4 Multimodal model
  - Advanced document extraction
  - Table extraction
  - Higher processing limits

### Standard to Professional Upgrade

- **Process**: License key upgrade
- **Data Migration**: Automatic, no data loss
- **Configuration**: Some configuration changes may be required
- **Benefits**:
  - More powerful Llama 3 8B model
  - Cloud LLM support
  - Custom templates
  - Unlimited processing
  - Priority support
