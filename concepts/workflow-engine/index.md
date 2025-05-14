---
title: 'Workflow Engine'
description: 'Understanding Clary AI workflow engine capabilities'
---

# Workflow Engine

Clary AI's Workflow Engine is a powerful system that allows you to create, manage, and execute document processing workflows.

## Key Features

### Workflow Definition

Define complex document processing workflows using a simple YAML-based configuration language or through the API.

### Task Orchestration

Orchestrate a series of tasks to be executed in sequence or in parallel, with dependencies between tasks.

### Error Handling

Robust error handling capabilities, including retry mechanisms, fallbacks, and error reporting.

### Checkpointing

Workflows can be checkpointed at various stages, allowing for resumption from the last successful checkpoint in case of failures.

### Monitoring

Real-time monitoring of workflow execution, with detailed logs and status updates.

### Templates

Pre-defined workflow templates for common document processing tasks, which can be customized to your specific needs.

## Workflow Components

### Tasks

Tasks are the basic building blocks of workflows. Each task performs a specific operation, such as:

- Document parsing
- Text extraction
- Entity recognition
- Classification
- Summarization
- And more

### Connectors

Connectors allow workflows to interact with external systems, such as:

- Databases
- Storage systems
- APIs
- Notification services
- And more

### Triggers

Triggers initiate workflow execution based on specific events, such as:

- Document upload
- API call
- Scheduled time
- External event
- And more

## Example Workflow

Here's a simple example of a workflow definition:

```yaml
name: Invoice Processing
version: 1.0.0
description: Extract information from invoices

triggers:
  - type: document_upload
    filter:
      mime_types: [application/pdf]

tasks:
  - id: parse_document
    type: document_parser
    config:
      output_format: json

  - id: extract_invoice_data
    type: entity_extraction
    depends_on: [parse_document]
    config:
      entities:
        - invoice_number
        - date
        - total_amount
        - vendor_name
        - line_items

  - id: store_results
    type: database_connector
    depends_on: [extract_invoice_data]
    config:
      connection: default_database
      table: invoices

error_handling:
  retry:
    max_attempts: 3
    backoff: exponential
```

## Integration with AI Models

The Workflow Engine is tightly integrated with Clary AI's [AI Models](/concepts/ai-models/index), allowing you to leverage advanced AI capabilities in your workflows.

## Next Steps

- [Learn about Document Processing](/concepts/document-processing/index)
- [Explore AI Models used in Clary AI](/concepts/ai-models/index)
- [Check out the API Reference](/api-reference/overview)
