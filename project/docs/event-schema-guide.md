# Workflow Event Schema Guide

## Overview

This guide documents the workflow event schema used for events published to Kafka. The schema provides type-safe event definitions with validation, serialization, and versioning support.

## Event Schema Structure

### WorkflowEvent

The main event model representing a standardized workflow event:

```python
from workflow_events import WorkflowEvent, EventType, EventSource, WorkflowEventPayload, WorkflowEventMetadata

event = WorkflowEvent(
    event_type=EventType.WORKFLOW_COMPLETED,
    source=EventSource.AIRFLOW,
    workflow_id="example_dag",
    workflow_run_id="run_123",
    payload=WorkflowEventPayload(data={"status": "success", "count": 100}),
    metadata=WorkflowEventMetadata(environment="dev", version="1.0")
)
```

### Event Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_id` | UUID | No (auto-generated) | Unique identifier for the event |
| `event_type` | EventType | Yes | Type of workflow event |
| `timestamp` | datetime | No (auto-generated) | ISO 8601 timestamp when event was generated |
| `source` | EventSource | Yes | Source system that generated the event |
| `workflow_id` | str | Yes | Identifier of the workflow (e.g., DAG ID) |
| `workflow_run_id` | str | Yes | Identifier of the specific workflow run |
| `payload` | WorkflowEventPayload | Yes | Workflow-specific data payload |
| `metadata` | WorkflowEventMetadata | Yes | Event metadata (environment, version) |

## Event Types

The `EventType` enum defines the supported workflow event types:

- `WORKFLOW_TRIGGERED`: Workflow has been triggered/started
- `WORKFLOW_COMPLETED`: Workflow has completed successfully
- `WORKFLOW_FAILED`: Workflow has failed

```python
from workflow_events import EventType

# All event types
EventType.WORKFLOW_TRIGGERED  # "workflow.triggered"
EventType.WORKFLOW_COMPLETED  # "workflow.completed"
EventType.WORKFLOW_FAILED     # "workflow.failed"
```

## Event Sources

The `EventSource` enum defines the supported event sources:

- `AIRFLOW`: Events from Apache Airflow
- `LANGGRAPH`: Events from LangGraph workflows
- `FASTAPI`: Events from FastAPI applications

```python
from workflow_events import EventSource

# All event sources
EventSource.AIRFLOW     # "airflow"
EventSource.LANGGRAPH   # "langgraph"
EventSource.FASTAPI     # "fastapi"
```

## Payload Structure

The `WorkflowEventPayload` contains workflow-specific data in a flexible dictionary format:

```python
from workflow_events import WorkflowEventPayload

payload = WorkflowEventPayload(
    data={
        "status": "success",
        "count": 100,
        "tasks": [
            {"id": 1, "status": "completed"},
            {"id": 2, "status": "running"}
        ]
    }
)
```

## Metadata Structure

The `WorkflowEventMetadata` contains environment and version information:

```python
from workflow_events import WorkflowEventMetadata

metadata = WorkflowEventMetadata(
    environment="dev",  # Must be: "dev", "staging", or "prod"
    version="1.0"       # Schema version (default: "1.0")
)
```

### Environment Validation

The `environment` field is validated against a pattern:
- `dev`: Development environment
- `staging`: Staging environment
- `prod`: Production environment

## Serialization

### Serialize to Dictionary

```python
event_dict = event.model_dump()
# Returns: {
#     "event_id": "123e4567-e89b-12d3-a456-426614174000",
#     "event_type": "workflow.completed",
#     "timestamp": "2025-01-27T10:00:00",
#     ...
# }
```

### Serialize to JSON

```python
json_str = event.model_dump_json()
# Returns: '{"event_id":"...","event_type":"workflow.completed",...}'
```

### Deserialize from JSON

```python
json_data = '{"event_id":"...","event_type":"workflow.completed",...}'
event = WorkflowEvent.model_validate_json(json_data)
```

### Deserialize from Dictionary

```python
event_dict = {
    "event_id": "123e4567-e89b-12d3-a456-426614174000",
    "event_type": "workflow.completed",
    "timestamp": "2025-01-27T10:00:00",
    "source": "airflow",
    "workflow_id": "example_dag",
    "workflow_run_id": "run_123",
    "payload": {"data": {"status": "success"}},
    "metadata": {"environment": "dev", "version": "1.0"}
}
event = WorkflowEvent.model_validate(event_dict)
```

## JSON Schema Generation

Generate JSON schema for validation or serialization:

```python
from workflow_events.schema_utils import generate_json_schema, save_json_schema

# Generate validation schema
validation_schema = generate_json_schema(mode="validation")

# Generate serialization schema
serialization_schema = generate_json_schema(mode="serialization")

# Save schema to file
save_json_schema("workflow_event_schema.json", mode="validation")
```

## Schema Versioning

The schema supports versioning through the `metadata.version` field:

```python
event = WorkflowEvent(
    ...,
    metadata=WorkflowEventMetadata(environment="dev", version="1.0")
)
```

When evolving the schema:
1. Update the version in metadata
2. Maintain backward compatibility where possible
3. Document migration path for consumers

## Validation

Pydantic automatically validates all fields:

```python
from pydantic import ValidationError

try:
    event = WorkflowEvent(
        event_type="invalid.type",  # Invalid event type
        source=EventSource.AIRFLOW,
        workflow_id="test",
        workflow_run_id="run_123",
        payload=WorkflowEventPayload(data={}),
        metadata=WorkflowEventMetadata(environment="dev")
    )
except ValidationError as e:
    print(e.errors())
    # [{'type': 'enum', 'loc': ('event_type',), 'msg': 'Input should be ...', ...}]
```

## Examples

### Example 1: Airflow Workflow Completion Event

```python
from workflow_events import (
    WorkflowEvent,
    EventType,
    EventSource,
    WorkflowEventPayload,
    WorkflowEventMetadata
)

event = WorkflowEvent(
    event_type=EventType.WORKFLOW_COMPLETED,
    source=EventSource.AIRFLOW,
    workflow_id="example_etl_dag",
    workflow_run_id="run_2025-01-27T10:00:00",
    payload=WorkflowEventPayload(data={
        "status": "success",
        "tasks_completed": 5,
        "duration_seconds": 120
    }),
    metadata=WorkflowEventMetadata(environment="dev", version="1.0")
)

# Serialize for Kafka
json_str = event.model_dump_json()
```

### Example 2: LangGraph Workflow Triggered Event

```python
event = WorkflowEvent(
    event_type=EventType.WORKFLOW_TRIGGERED,
    source=EventSource.LANGGRAPH,
    workflow_id="trading_analysis_workflow",
    workflow_run_id="run_789",
    payload=WorkflowEventPayload(data={
        "input": {"symbol": "AAPL", "timeframe": "1h"},
        "workflow_type": "analysis"
    }),
    metadata=WorkflowEventMetadata(environment="prod", version="1.0")
)
```

### Example 3: Failed Workflow Event

```python
event = WorkflowEvent(
    event_type=EventType.WORKFLOW_FAILED,
    source=EventSource.AIRFLOW,
    workflow_id="data_processing_dag",
    workflow_run_id="run_456",
    payload=WorkflowEventPayload(data={
        "error": "Task timeout",
        "failed_task": "extract_data",
        "retry_count": 3
    }),
    metadata=WorkflowEventMetadata(environment="staging", version="1.0")
)
```

## Testing

Comprehensive unit tests are available in `project/tests/kafka/test_events.py`:

```bash
# Run event schema tests
pytest project/tests/kafka/test_events.py -v
```

Tests cover:
- Event creation and validation
- Schema validation (valid and invalid events)
- JSON serialization/deserialization
- Schema versioning support
- Event type and source enumeration

## Best Practices

1. **Always validate events**: Use Pydantic models for type safety
2. **Use enums**: Use `EventType` and `EventSource` enums instead of strings
3. **Version your schema**: Include version in metadata for evolution
4. **Handle validation errors**: Catch `ValidationError` when deserializing
5. **Document payload structure**: Document expected payload structure for each event type
6. **Test serialization**: Ensure events serialize correctly for Kafka

## References

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PRD Phase 1 - Event Schema](prd_phase1.md#event-schema)
- [Task 010: Event Schema Definition](../dev/tasks/TASK-010.md)

