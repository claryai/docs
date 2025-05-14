# Testing Strategy for Clary AI Tiered Approach

This document outlines the testing strategy for the Clary AI tiered approach, ensuring that each tier (Lite, Standard, Professional) functions correctly and provides the expected features.

## Testing Goals

1. **Feature Verification**: Ensure each tier provides exactly the features it should
2. **Tier Isolation**: Verify that higher-tier features are not accessible in lower tiers
3. **Upgrade Path**: Test the upgrade process between tiers
4. **Performance**: Validate performance across different hardware configurations
5. **Security**: Ensure proper access controls and license validation

## Test Environments

### Core Repository Tests

The core repository should include comprehensive tests for all components:

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test interactions between components
3. **API Tests**: Test API endpoints and responses
4. **Feature Flag Tests**: Test feature flag functionality

### Tier-Specific Tests

Each tier repository should include tests specific to that tier:

1. **Tier Configuration Tests**: Verify tier-specific configurations
2. **Feature Availability Tests**: Check that expected features are available
3. **Feature Restriction Tests**: Verify that higher-tier features are not accessible
4. **Docker Build Tests**: Ensure Docker images build correctly
5. **End-to-End Tests**: Test complete workflows

## Test Implementation

### Core Repository Test Structure

```
core/
├── tests/
│   ├── unit/
│   │   ├── test_document_processing.py
│   │   ├── test_extraction.py
│   │   ├── test_api.py
│   │   └── test_feature_flags.py
│   ├── integration/
│   │   ├── test_workflow.py
│   │   ├── test_api_integration.py
│   │   └── test_model_integration.py
│   └── api/
│       ├── test_document_endpoints.py
│       ├── test_template_endpoints.py
│       └── test_user_endpoints.py
```

### Tier Repository Test Structure

```
tier/
├── tests/
│   ├── test_docker_build.py
│   ├── test_tier_configuration.py
│   ├── test_feature_availability.py
│   └── test_end_to_end.py
```

## Test Automation

### CI/CD Integration

Each repository should have CI/CD pipelines that run tests automatically:

1. **Pull Request Tests**: Run tests on every pull request
2. **Merge Tests**: Run tests after merging to main branch
3. **Nightly Tests**: Run comprehensive tests nightly
4. **Release Tests**: Run all tests before creating a release

### Test Matrix

Test across different configurations:

1. **Operating Systems**: Linux, macOS, Windows
2. **Hardware Configurations**: Minimum, recommended, high-end
3. **Database Versions**: PostgreSQL 12, 13, 14
4. **Docker Versions**: Latest, LTS

## Feature Flag Testing

Test feature flags to ensure they correctly control access to features:

```python
# Example feature flag test
def test_feature_flag_controls_access():
    # Test with lite tier
    with set_environment_variables(TIER="lite"):
        assert not has_access_to_feature("advanced_extraction")
    
    # Test with standard tier
    with set_environment_variables(TIER="standard"):
        assert has_access_to_feature("advanced_extraction")
        assert not has_access_to_feature("custom_templates")
    
    # Test with professional tier
    with set_environment_variables(TIER="professional"):
        assert has_access_to_feature("advanced_extraction")
        assert has_access_to_feature("custom_templates")
```

## API Key Testing

Test API key validation and tier-based access control:

```python
# Example API key test
def test_api_key_tier_controls_access():
    # Create API keys for different tiers
    lite_key = create_api_key(tier="lite")
    standard_key = create_api_key(tier="standard")
    professional_key = create_api_key(tier="professional")
    
    # Test basic extraction endpoint
    for key in [lite_key, standard_key, professional_key]:
        response = client.post("/api/v1/extract/basic", headers={"X-API-Key": key})
        assert response.status_code == 200
    
    # Test advanced extraction endpoint
    response = client.post("/api/v1/extract/advanced", headers={"X-API-Key": lite_key})
    assert response.status_code == 403
    
    for key in [standard_key, professional_key]:
        response = client.post("/api/v1/extract/advanced", headers={"X-API-Key": key})
        assert response.status_code == 200
    
    # Test custom template endpoint
    for key in [lite_key, standard_key]:
        response = client.post("/api/v1/templates/custom", headers={"X-API-Key": key})
        assert response.status_code == 403
    
    response = client.post("/api/v1/templates/custom", headers={"X-API-Key": professional_key})
    assert response.status_code == 200
```

## Model Integration Testing

Test model integration for different tiers:

```python
# Example model integration test
def test_model_integration_by_tier():
    # Test lite tier (no pre-integrated LLM)
    with set_environment_variables(TIER="lite"):
        model_manager = ModelManager()
        available_models = model_manager.get_models_for_tier("lite")
        assert len(available_models) == 0
    
    # Test standard tier (Phi-4 Multimodal)
    with set_environment_variables(TIER="standard"):
        model_manager = ModelManager()
        available_models = model_manager.get_models_for_tier("standard")
        assert "phi-4-multimodal" in available_models
        assert "llama-3-8b" not in available_models
    
    # Test professional tier (all models)
    with set_environment_variables(TIER="professional"):
        model_manager = ModelManager()
        available_models = model_manager.get_models_for_tier("professional")
        assert "phi-4-multimodal" in available_models
        assert "llama-3-8b" in available_models
```

## Docker Build Testing

Test Docker builds for each tier:

```python
# Example Docker build test
def test_docker_build():
    # Build Docker image
    result = subprocess.run(["docker", "build", "-t", "claryai-test", "-f", "Dockerfile", "."], capture_output=True)
    assert result.returncode == 0
    
    # Run container
    container = subprocess.run(["docker", "run", "-d", "--name", "claryai-test-container", "claryai-test"], capture_output=True)
    container_id = container.stdout.decode().strip()
    
    try:
        # Check container is running
        result = subprocess.run(["docker", "ps", "-q", "--filter", f"id={container_id}"], capture_output=True)
        assert result.stdout.decode().strip() == container_id
        
        # Check tier environment variable
        result = subprocess.run(["docker", "exec", container_id, "printenv", "TIER"], capture_output=True)
        assert result.stdout.decode().strip() == "lite"  # Adjust for each tier
    finally:
        # Clean up
        subprocess.run(["docker", "rm", "-f", container_id])
```

## End-to-End Testing

Test complete workflows for each tier:

```python
# Example end-to-end test
def test_document_processing_workflow():
    # Start services
    subprocess.run(["docker-compose", "up", "-d"])
    
    try:
        # Wait for services to be ready
        wait_for_services()
        
        # Upload document
        with open("test_document.pdf", "rb") as f:
            response = requests.post(
                "http://localhost:8000/api/v1/documents",
                files={"file": f},
                headers={"X-API-Key": API_KEY}
            )
        assert response.status_code == 200
        document_id = response.json()["id"]
        
        # Process document
        response = requests.post(
            f"http://localhost:8000/api/v1/documents/{document_id}/process",
            headers={"X-API-Key": API_KEY}
        )
        assert response.status_code == 200
        
        # Get results
        response = requests.get(
            f"http://localhost:8000/api/v1/documents/{document_id}/results",
            headers={"X-API-Key": API_KEY}
        )
        assert response.status_code == 200
        results = response.json()
        
        # Verify results based on tier
        if TIER == "lite":
            assert "basic_extraction" in results
            assert "advanced_extraction" not in results
        elif TIER == "standard":
            assert "basic_extraction" in results
            assert "advanced_extraction" in results
            assert "custom_templates" not in results
        elif TIER == "professional":
            assert "basic_extraction" in results
            assert "advanced_extraction" in results
            assert "custom_templates" in results
    finally:
        # Clean up
        subprocess.run(["docker-compose", "down"])
```

## Test Reporting

Generate comprehensive test reports:

1. **Coverage Reports**: Measure code coverage
2. **Test Results**: Report pass/fail status
3. **Performance Metrics**: Report performance metrics
4. **Regression Analysis**: Compare with previous test runs

## Continuous Improvement

Regularly review and improve the testing strategy:

1. **Test Review**: Review tests during code reviews
2. **Test Maintenance**: Update tests as features change
3. **Test Expansion**: Add new tests for new features
4. **Automation Improvement**: Improve test automation
