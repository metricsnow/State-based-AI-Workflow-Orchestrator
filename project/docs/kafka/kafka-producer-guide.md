# Kafka Producer Guide

## Overview

This guide documents the Kafka producer implementation for publishing workflow events to Kafka topics. The producer provides a reliable, type-safe interface for event publishing with comprehensive error handling and connection management.

## Installation

The producer requires the `kafka-python` library:

```bash
pip install kafka-python
```

## Quick Start

### Basic Usage

```python
from workflow_events import (
    WorkflowEventProducer,
    WorkflowEvent,
    EventType,
    EventSource,
    WorkflowEventPayload,
    WorkflowEventMetadata,
)

# Create producer
producer = WorkflowEventProducer(bootstrap_servers="localhost:9092")

# Create event
event = WorkflowEvent(
    event_type=EventType.WORKFLOW_COMPLETED,
    source=EventSource.AIRFLOW,
    workflow_id="example_dag",
    workflow_run_id="run_123",
    payload=WorkflowEventPayload(data={"status": "success", "count": 100}),
    metadata=WorkflowEventMetadata(environment="dev"),
)

# Publish event
success = producer.publish_event(event)
if success:
    print("Event published successfully")

# Close producer
producer.close()
```

### Using Context Manager

```python
with WorkflowEventProducer(bootstrap_servers="localhost:9092") as producer:
    event = WorkflowEvent(
        event_type=EventType.WORKFLOW_TRIGGERED,
        source=EventSource.AIRFLOW,
        workflow_id="example_dag",
        workflow_run_id="run_456",
        payload=WorkflowEventPayload(data={"status": "triggered"}),
        metadata=WorkflowEventMetadata(environment="dev"),
    )
    producer.publish_event(event)
    # Producer automatically closes when exiting context
```

## Producer Configuration

### Default Configuration

The producer uses sensible defaults for reliability:

```python
producer = WorkflowEventProducer()
# Equivalent to:
# WorkflowEventProducer(
#     bootstrap_servers="localhost:9092",
#     acks="all",
#     retries=3,
#     max_in_flight_requests_per_connection=1,
#     request_timeout_ms=30000,
#     delivery_timeout_ms=120000,
# )
```

### Custom Configuration

```python
producer = WorkflowEventProducer(
    bootstrap_servers="kafka:9092",
    acks="1",  # Wait for leader acknowledgment only
    retries=5,  # More retries for unreliable networks
    max_in_flight_requests_per_connection=2,  # Allow parallel requests
    request_timeout_ms=60000,  # Longer timeout
    delivery_timeout_ms=180000,  # Longer delivery timeout
)
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `bootstrap_servers` | str | `"localhost:9092"` | Kafka broker address |
| `acks` | str | `"all"` | Acknowledgment requirement (`"0"`, `"1"`, `"all"`) |
| `retries` | int | `3` | Number of retry attempts |
| `max_in_flight_requests_per_connection` | int | `1` | Max in-flight requests per connection |
| `request_timeout_ms` | int | `30000` | Request timeout in milliseconds |
| `delivery_timeout_ms` | int | `120000` | Delivery timeout in milliseconds |

## Publishing Events

### Basic Publishing

```python
event = WorkflowEvent(
    event_type=EventType.WORKFLOW_COMPLETED,
    source=EventSource.AIRFLOW,
    workflow_id="example_dag",
    workflow_run_id="run_123",
    payload=WorkflowEventPayload(data={"status": "success"}),
    metadata=WorkflowEventMetadata(environment="dev"),
)

success = producer.publish_event(event)
```

### Custom Topic

```python
success = producer.publish_event(event, topic="custom-topic")
```

### Custom Timeout

```python
success = producer.publish_event(event, timeout=30)  # 30 seconds
```

### Return Value

The `publish_event()` method returns:
- `True`: Event published successfully
- `False`: Publishing failed (error logged)

## Error Handling

### Connection Errors

```python
try:
    producer = WorkflowEventProducer(bootstrap_servers="invalid:9092")
except KafkaError as e:
    print(f"Failed to connect: {e}")
```

### Publishing Errors

```python
success = producer.publish_event(event)
if not success:
    # Error already logged, handle failure
    print("Failed to publish event")
```

### Timeout Errors

```python
from kafka.errors import KafkaTimeoutError

try:
    success = producer.publish_event(event, timeout=1)  # Very short timeout
except KafkaTimeoutError:
    print("Publish operation timed out")
```

## Connection Management

### Flush Pending Messages

```python
# Flush all pending messages (waits indefinitely)
producer.flush()

# Flush with timeout
try:
    producer.flush(timeout=5.0)  # 5 seconds
except KafkaTimeoutError:
    print("Flush timed out")
```

### Close Producer

```python
# Close producer (automatically flushes before closing)
producer.close()
```

### Context Manager

The producer supports Python's context manager protocol for automatic resource management:

```python
with WorkflowEventProducer() as producer:
    # Publish events
    producer.publish_event(event1)
    producer.publish_event(event2)
    # Producer automatically flushes and closes
```

## Best Practices

### 1. Use Context Manager

Always use the context manager when possible to ensure proper cleanup:

```python
with WorkflowEventProducer() as producer:
    producer.publish_event(event)
```

### 2. Handle Errors Gracefully

```python
success = producer.publish_event(event)
if not success:
    # Log error or retry
    logger.error(f"Failed to publish event {event.event_id}")
```

### 3. Flush Before Closing

The producer automatically flushes before closing, but you can flush explicitly:

```python
producer.publish_event(event1)
producer.publish_event(event2)
producer.flush()  # Ensure all messages are sent
producer.close()
```

### 4. Reuse Producer Instances

Create one producer instance and reuse it for multiple events:

```python
producer = WorkflowEventProducer()

for event in events:
    producer.publish_event(event)

producer.close()
```

### 5. Use Appropriate Configuration

For production, use `acks="all"` for maximum reliability:

```python
producer = WorkflowEventProducer(
    bootstrap_servers="kafka:9092",
    acks="all",  # Wait for all replicas
    retries=3,
)
```

## Integration Examples

### Airflow Integration

```python
from airflow.decorators import task
from workflow_events import (
    WorkflowEventProducer,
    WorkflowEvent,
    EventType,
    EventSource,
    WorkflowEventPayload,
    WorkflowEventMetadata,
)

@task
def publish_completion_event(**context):
    """Publish workflow completion event."""
    dag_run = context["dag_run"]
    
    event = WorkflowEvent(
        event_type=EventType.WORKFLOW_COMPLETED,
        source=EventSource.AIRFLOW,
        workflow_id=dag_run.dag_id,
        workflow_run_id=dag_run.run_id,
        payload=WorkflowEventPayload(data={"status": "success"}),
        metadata=WorkflowEventMetadata(environment="dev"),
    )
    
    with WorkflowEventProducer() as producer:
        producer.publish_event(event)
```

### FastAPI Integration

```python
from fastapi import FastAPI
from workflow_events import (
    WorkflowEventProducer,
    WorkflowEvent,
    EventType,
    EventSource,
    WorkflowEventPayload,
    WorkflowEventMetadata,
)

app = FastAPI()
producer = WorkflowEventProducer()

@app.post("/workflow/trigger")
async def trigger_workflow(workflow_id: str):
    event = WorkflowEvent(
        event_type=EventType.WORKFLOW_TRIGGERED,
        source=EventSource.FASTAPI,
        workflow_id=workflow_id,
        workflow_run_id=f"run_{uuid.uuid4()}",
        payload=WorkflowEventPayload(data={"triggered_by": "api"}),
        metadata=WorkflowEventMetadata(environment="prod"),
    )
    
    success = producer.publish_event(event)
    return {"published": success}
```

## Logging

The producer uses Python's logging module. Configure logging to see producer activity:

```python
import logging

logging.basicConfig(level=logging.INFO)
# Producer logs will show:
# - Connection status
# - Event publishing results
# - Errors and warnings
```

## Testing

### Unit Tests

Comprehensive unit tests are available in `project/tests/kafka/test_producer.py`:

```bash
# Run producer tests
pytest project/tests/kafka/test_producer.py -v
```

### Integration Tests

Integration tests require a running Kafka instance:

```bash
# Start Kafka
docker-compose up -d kafka

# Run integration tests
pytest project/tests/kafka/test_producer.py::TestProducerIntegration -v
```

## Troubleshooting

### Connection Failures

**Problem**: Producer fails to connect to Kafka

**Solutions**:
1. Verify Kafka is running: `docker-compose ps kafka`
2. Check bootstrap servers address: `localhost:9092` (host) or `kafka:9092` (Docker network)
3. Verify network connectivity: `telnet localhost 9092`
4. Check Kafka logs: `docker-compose logs kafka`

### Publishing Failures

**Problem**: Events not being published

**Solutions**:
1. Check return value: `success = producer.publish_event(event)`
2. Review logs for error messages
3. Verify topic exists or auto-creation is enabled
4. Check Kafka broker logs for errors
5. Verify event serialization: `event.model_dump()`

### Timeout Errors

**Problem**: `KafkaTimeoutError` when publishing

**Solutions**:
1. Increase timeout: `producer.publish_event(event, timeout=30)`
2. Check Kafka broker performance
3. Verify network latency
4. Check Kafka broker logs for bottlenecks

### Serialization Errors

**Problem**: Events fail to serialize

**Solutions**:
1. Verify event is valid: `event.model_dump()` should work
2. Check for circular references in payload data
3. Ensure all data types are JSON-serializable
4. Use Pydantic models for payload data

## Performance Considerations

### Batch Publishing

For high-throughput scenarios, publish multiple events before flushing:

```python
producer = WorkflowEventProducer()

for event in events:
    producer.publish_event(event)

producer.flush()  # Flush all at once
producer.close()
```

### Connection Pooling

The producer reuses connections automatically. Create one producer instance per process/thread:

```python
# Good: Reuse producer
producer = WorkflowEventProducer()
for event in events:
    producer.publish_event(event)
producer.close()

# Bad: Create new producer for each event
for event in events:
    producer = WorkflowEventProducer()
    producer.publish_event(event)
    producer.close()
```

## Security

For production deployments, consider:

1. **SASL Authentication**: Configure SASL credentials
2. **SSL/TLS**: Enable SSL for encrypted connections
3. **ACLs**: Configure Kafka ACLs for topic access control
4. **Network Security**: Use VPN or private networks

Example with SASL:

```python
from kafka import KafkaProducer

# Note: kafka-python SASL configuration would be passed to KafkaProducer
# This is a placeholder for future enhancement
producer = WorkflowEventProducer(
    bootstrap_servers="kafka:9092",
    # SASL configuration would go here
)
```

## Related Documentation

- [Event Schema Guide](event-schema-guide.md) - Event schema definition
- [Kafka Setup Guide](kafka-setup-guide.md) - Kafka infrastructure setup
- [PRD Phase 1](prd_phase1.md) - Overall architecture
- [Testing Guide](testing-guide-phase1.md) - Testing procedures

## References

- [kafka-python Documentation](https://github.com/dpkp/kafka-python)
- [Apache Kafka Producer Documentation](https://kafka.apache.org/documentation/#producerconfigs)
- [TASK-011: Kafka Producer Implementation](../dev/tasks/TASK-011.md)

