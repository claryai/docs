# Monitoring and Analytics for Clary AI

This document outlines the monitoring and analytics strategy for Clary AI, including usage tracking, performance monitoring, and feedback mechanisms across all tiers.

## Monitoring Goals

1. **Usage Tracking**: Track how customers use each tier
2. **Performance Monitoring**: Identify bottlenecks and optimize performance
3. **Error Tracking**: Detect and diagnose errors
4. **License Validation**: Monitor license usage and compliance
5. **User Feedback**: Gather user feedback to guide development

## Implementation Strategy

### Usage Tracking

Track key metrics for each tier:

1. **Document Processing**:
   - Number of documents processed
   - Types of documents processed
   - Processing time per document
   - Success/failure rate

2. **Feature Usage**:
   - Features used per document
   - Feature usage frequency
   - Feature success/failure rate

3. **API Usage**:
   - API endpoint calls
   - API response times
   - API error rates

4. **User Activity**:
   - Active users
   - Session duration
   - User actions
   - User workflows

#### Implementation

```python
# Usage tracking middleware
@app.middleware("http")
async def track_usage(request: Request, call_next):
    # Record start time
    start_time = time.time()
    
    # Get API key from request
    api_key = request.headers.get("X-API-Key")
    
    # Get user and tier
    user = None
    tier = "unknown"
    if api_key:
        user = get_user_from_api_key(api_key)
        if user:
            tier = user.tier
    
    # Process request
    response = await call_next(request)
    
    # Record end time
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Log usage
    logger.info(
        f"API call: {request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Time: {processing_time:.4f}s "
        f"Tier: {tier} "
        f"User: {user.id if user else 'anonymous'}"
    )
    
    # Record metrics
    metrics.record_api_call(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        processing_time=processing_time,
        tier=tier,
        user_id=user.id if user else None
    )
    
    return response
```

### Performance Monitoring

Monitor system performance across all tiers:

1. **System Metrics**:
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network I/O

2. **Application Metrics**:
   - Request latency
   - Processing time
   - Queue length
   - Error rate

3. **Model Metrics**:
   - Inference time
   - Memory usage
   - GPU utilization
   - Model loading time

#### Implementation

```python
# Performance monitoring service
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()
    
    def record_metric(self, name, value, tags=None):
        if tags is None:
            tags = {}
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            "timestamp": time.time(),
            "value": value,
            "tags": tags
        })
    
    def get_metrics(self, name=None, start_time=None, end_time=None, tags=None):
        if start_time is None:
            start_time = self.start_time
        
        if end_time is None:
            end_time = time.time()
        
        if name is None:
            # Return all metrics
            return {
                metric_name: [
                    m for m in metric_values
                    if start_time <= m["timestamp"] <= end_time
                    and (tags is None or all(m["tags"].get(k) == v for k, v in tags.items()))
                ]
                for metric_name, metric_values in self.metrics.items()
            }
        
        if name not in self.metrics:
            return []
        
        return [
            m for m in self.metrics[name]
            if start_time <= m["timestamp"] <= end_time
            and (tags is None or all(m["tags"].get(k) == v for k, v in tags.items()))
        ]
    
    def get_summary(self, name, start_time=None, end_time=None, tags=None):
        metrics = self.get_metrics(name, start_time, end_time, tags)
        
        if not metrics:
            return None
        
        values = [m["value"] for m in metrics]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "p50": sorted(values)[len(values) // 2],
            "p95": sorted(values)[int(len(values) * 0.95)],
            "p99": sorted(values)[int(len(values) * 0.99)]
        }
```

### Error Tracking

Track and analyze errors across all tiers:

1. **Error Logging**:
   - Error type
   - Error message
   - Stack trace
   - Context information

2. **Error Analysis**:
   - Error frequency
   - Error patterns
   - Error impact
   - Error resolution

#### Implementation

```python
# Error tracking middleware
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    # Generate error ID
    error_id = str(uuid.uuid4())
    
    # Get API key from request
    api_key = request.headers.get("X-API-Key")
    
    # Get user and tier
    user = None
    tier = "unknown"
    if api_key:
        user = get_user_from_api_key(api_key)
        if user:
            tier = user.tier
    
    # Log error
    logger.error(
        f"Error ID: {error_id} "
        f"Type: {type(exc).__name__} "
        f"Message: {str(exc)} "
        f"Path: {request.url.path} "
        f"Method: {request.method} "
        f"Tier: {tier} "
        f"User: {user.id if user else 'anonymous'}"
    )
    
    # Record error details
    error_tracker.record_error(
        error_id=error_id,
        error_type=type(exc).__name__,
        error_message=str(exc),
        stack_trace=traceback.format_exc(),
        request_path=request.url.path,
        request_method=request.method,
        tier=tier,
        user_id=user.id if user else None,
        timestamp=datetime.now()
    )
    
    # Return error response
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "error_id": error_id,
            "message": "An unexpected error occurred. Please contact support with this error ID."
        }
    )
```

### License Validation Monitoring

Monitor license usage and compliance:

1. **License Metrics**:
   - Active licenses
   - License validation attempts
   - License validation failures
   - License expiration

2. **Usage Compliance**:
   - Document processing limits
   - Feature usage limits
   - API call limits

#### Implementation

```python
# License validation monitoring
class LicenseMonitor:
    def __init__(self):
        self.validations = []
    
    def record_validation(self, api_key, container_id, valid, tier, message):
        self.validations.append({
            "timestamp": datetime.now(),
            "api_key_hash": hashlib.sha256(api_key.encode()).hexdigest(),
            "container_id": container_id,
            "valid": valid,
            "tier": tier,
            "message": message
        })
    
    def get_validation_stats(self, start_time=None, end_time=None):
        if start_time is None:
            start_time = datetime.min
        
        if end_time is None:
            end_time = datetime.max
        
        validations = [
            v for v in self.validations
            if start_time <= v["timestamp"] <= end_time
        ]
        
        total = len(validations)
        valid = sum(1 for v in validations if v["valid"])
        invalid = total - valid
        
        tier_counts = {}
        for v in validations:
            tier = v["tier"]
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        return {
            "total": total,
            "valid": valid,
            "invalid": invalid,
            "tier_counts": tier_counts
        }
```

### User Feedback

Gather user feedback to guide development:

1. **Feedback Mechanisms**:
   - In-app feedback forms
   - Feature request forms
   - Bug report forms
   - User surveys

2. **Feedback Analysis**:
   - Sentiment analysis
   - Feature popularity
   - Pain points
   - Improvement suggestions

#### Implementation

```python
# Feedback API endpoint
@app.post("/api/v1/feedback")
async def submit_feedback(
    feedback: FeedbackSchema,
    user: User = Depends(get_api_key)
):
    # Record feedback
    feedback_id = feedback_service.record_feedback(
        user_id=user.id,
        feedback_type=feedback.type,
        feedback_text=feedback.text,
        rating=feedback.rating,
        metadata=feedback.metadata
    )
    
    # Send notification if urgent
    if feedback.type == "bug" and feedback.rating <= 2:
        notification_service.send_notification(
            "Urgent bug report",
            f"User {user.id} reported a critical bug: {feedback.text}",
            ["support", "development"]
        )
    
    return {"id": feedback_id, "message": "Feedback submitted successfully"}
```

## Analytics Dashboard

Create a comprehensive analytics dashboard for each tier:

1. **Usage Dashboard**:
   - Document processing metrics
   - Feature usage metrics
   - API usage metrics
   - User activity metrics

2. **Performance Dashboard**:
   - System performance metrics
   - Application performance metrics
   - Model performance metrics
   - Error metrics

3. **License Dashboard**:
   - License validation metrics
   - Usage compliance metrics
   - License expiration metrics

4. **Feedback Dashboard**:
   - User feedback metrics
   - Feature request metrics
   - Bug report metrics
   - User satisfaction metrics

## Tier-Specific Monitoring

Implement tier-specific monitoring:

### Lite Tier Monitoring

- Focus on basic document processing metrics
- Track upgrade potential
- Monitor API usage within limits

### Standard Tier Monitoring

- Track model usage and performance
- Monitor advanced feature usage
- Track upgrade potential to Professional tier

### Professional Tier Monitoring

- Monitor cloud LLM usage and performance
- Track custom template usage
- Monitor enterprise feature usage

## Data Privacy and Compliance

Ensure monitoring and analytics comply with data privacy regulations:

1. **Data Anonymization**:
   - Remove personally identifiable information
   - Aggregate data where possible
   - Use secure hashing for identifiers

2. **Data Retention**:
   - Define data retention policies
   - Implement data purging mechanisms
   - Allow users to delete their data

3. **Consent Management**:
   - Obtain user consent for data collection
   - Allow users to opt out of analytics
   - Provide clear privacy policies

## Implementation Timeline

1. **Phase 1: Basic Monitoring**
   - Implement usage tracking
   - Set up error tracking
   - Create basic dashboards

2. **Phase 2: Advanced Monitoring**
   - Implement performance monitoring
   - Set up license validation monitoring
   - Create comprehensive dashboards

3. **Phase 3: Feedback and Analytics**
   - Implement feedback mechanisms
   - Set up analytics pipelines
   - Create feedback dashboards
