# Kafka Consumer Guide

## Overview

This guide documents the Kafka consumer implementation for consuming workflow events from Kafka topics. The consumer provides a reliable, type-safe interface for event consumption with comprehensive error handling, offset management, and consumer group support.

## Installation

The consumer requires the `kafka-python` library:

```bash
pip install kafka-python
```

## Quick Start

### Basic Usage

```python
from workflow_events import (
    WorkflowEventConsumer,
    WorkflowEvent,
    EventType,
    EventSource,
)

def process_event(event: WorkflowEvent):
    """Process workflow event."""
    print(f"Received event: {event.event_type} from {event.source}")
    print(f"Workflow: {event.workflow_id}, Run: {event.workflow_run_id}")
    print(f"Payload: {event.payload.data}")

# Create consumer
consumer = WorkflowEventConsumer(
    bootstrap_servers="localhost:9092",
    group_id="workflow-processor"
)

# Consume events
consumer.consume_events(
    callback=process_event,
    topics=["workflow-events"]
)
```

### Using Context Manager

```python
from workflow_events import WorkflowEventConsumer, WorkflowEvent

def process_event(event: WorkflowEvent):
    """Process workflow event."""
    print(f"Event: {event.event_id}")

with WorkflowEventConsumer(
    bootstrap_servers="localhost:9092",
    group_id="workflow-processor"
) as consumer:
    consumer.consume_events(
        callback=process_event,
        topics=["workflow-events"]
    )
    # Consumer automatically closes when exiting context
```

### Manual Polling

```python
from workflow_events import WorkflowEventConsumer, WorkflowEvent

consumer = WorkflowEventConsumer(
    bootstrap_servers="localhost:9092",
    group_id="workflow-processor"
)

consumer.subscribe(["workflow-events"])

# Poll for messages
messages = consumer.poll(timeout_ms=1000)

for topic_partition, records in messages.items():
    for record in records:
        event = WorkflowEvent.model_validate(record.value)
        print(f"Received event: {event.event_id}")

# Commit offsets
consumer.commit()
consumer.close()
```

## Consumer Configuration

### Default Configuration

The consumer uses sensible defaults for reliability:

```python
consumer = WorkflowEventConsumer()
# Equivalent to:
# WorkflowEventConsumer(
#     bootstrap_servers="localhost:9092",
#     group_id=None,
#     auto_offset_reset="earliest",
#     enable_auto_commit=True,
#     consumer_timeout_ms=1000,
#     max_poll_records=None
# )
```

### Configuration Options

- **bootstrap_servers**: Kafka broker address (default: `"localhost:9092"`)
- **group_id**: Consumer group ID (optional, enables consumer groups)
- **auto_offset_reset**: Offset reset policy (`"earliest"`, `"latest"`, `"none"`)
- **enable_auto_commit**: Whether to auto-commit offsets (default: `True`)
- **consumer_timeout_ms**: Consumer timeout in milliseconds (default: `1000`)
- **max_poll_records**: Maximum number of records per poll (optional)

### Consumer Groups

Consumer groups enable parallel processing and load balancing:

```python
# Multiple consumers in the same group will share partitions
consumer1 = WorkflowEventConsumer(
    bootstrap_servers="localhost:9092",
    group_id="workflow-processor"
)

consumer2 = WorkflowEventConsumer(
    bootstrap_servers="localhost:9092",
    group_id="workflow-processor"  # Same group ID
)

# Both consumers will share the workload
```

## Event Processing

### Callback Function

The callback function receives a `WorkflowEvent` instance:

```python
def process_event(event: WorkflowEvent):
    """Process workflow event."""
    if event.event_type == EventType.WORKFLOW_COMPLETED:
        print(f"Workflow {event.workflow_id} completed")
    elif event.event_type == EventType.WORKFLOW_FAILED:
        print(f"Workflow {event.workflow_id} failed")
        # Handle failure
```

### Error Handling

The consumer handles errors gracefully:

- **Deserialization errors**: Logged and skipped, processing continues
- **Callback errors**: Logged and skipped, processing continues
- **Kafka errors**: Logged and raised

```python
def process_event(event: WorkflowEvent):
    """Process workflow event with error handling."""
    try:
        # Your processing logic
        process_workflow(event)
    except Exception as e:
        logger.error(f"Error processing event {event.event_id}: {e}")
        # Consumer will continue processing other events
```

## Offset Management

### Auto-Commit (Default)

By default, offsets are automatically committed:

```python
consumer = WorkflowEventConsumer(
    enable_auto_commit=True  # Default
)
```

### Manual Commit

For more control, disable auto-commit and commit manually:

```python
consumer = WorkflowEventConsumer(
    enable_auto_commit=False
)

consumer.subscribe(["workflow-events"])

messages = consumer.poll(timeout_ms=1000)

for topic_partition, records in messages.items():
    for record in records:
        event = WorkflowEvent.model_validate(record.value)
        process_event(event)

# Commit after processing
consumer.commit()
```

### Seek to Specific Offset

Seek to a specific offset in a partition:

```python
from kafka.structs import TopicPartition

consumer = WorkflowEventConsumer()
consumer.subscribe(["workflow-events"])

# Seek to offset 100 in partition 0
tp = TopicPartition("workflow-events", 0)
consumer.seek(tp, 100)
```

### Get Current Position

Get the current offset position:

```python
from kafka.structs import TopicPartition

consumer = WorkflowEventConsumer()
consumer.subscribe(["workflow-events"])

tp = TopicPartition("workflow-events", 0)
position = consumer.position(tp)
print(f"Current position: {position}")
```

## Advanced Usage

### Multiple Topics

Subscribe to multiple topics:

```python
consumer = WorkflowEventConsumer(
    bootstrap_servers="localhost:9092",
    group_id="workflow-processor"
)

consumer.consume_events(
    callback=process_event,
    topics=["workflow-events", "workflow-alerts", "workflow-metrics"]
)
```

### Custom Timeout

Set a custom timeout for consumption:

```python
consumer = WorkflowEventConsumer(
    consumer_timeout_ms=5000  # 5 seconds
)

consumer.consume_events(
    callback=process_event,
    topics=["workflow-events"],
    timeout_ms=10000  # Override with 10 seconds
)
```

### Batch Processing

Process events in batches using polling:

```python
consumer = WorkflowEventConsumer(
    bootstrap_servers="localhost:9092",
    group_id="workflow-processor",
    max_poll_records=100  # Process up to 100 records per poll
)

consumer.subscribe(["workflow-events"])

while True:
    messages = consumer.poll(timeout_ms=1000)
    
    if not messages:
        continue
    
    events = []
    for topic_partition, records in messages.items():
        for record in records:
            event = WorkflowEvent.model_validate(record.value)
            events.append(event)
    
    # Process batch
    process_batch(events)
    
    # Commit after processing batch
    consumer.commit()
```

## Error Handling

### Connection Errors

Handle connection errors during initialization:

```python
try:
    consumer = WorkflowEventConsumer(
        bootstrap_servers="localhost:9092"
    )
except KafkaError as e:
    print(f"Failed to connect to Kafka: {e}")
    # Handle connection failure
```

### Deserialization Errors

Deserialization errors are automatically handled:

```python
# Invalid event data is logged and skipped
# Processing continues with next event
consumer.consume_events(
    callback=process_event,
    topics=["workflow-events"]
)
```

### Callback Errors

Callback errors are logged and processing continues:

```python
def process_event(event: WorkflowEvent):
    """Process event - errors are caught by consumer."""
    # If this raises an exception, it's logged and processing continues
    process_workflow(event)
```

## Best Practices

1. **Use Consumer Groups**: Enable parallel processing and load balancing
2. **Handle Errors Gracefully**: Implement error handling in callback functions
3. **Monitor Consumer Lag**: Track consumer lag to ensure timely processing
4. **Commit Offsets Carefully**: Commit offsets after successful processing
5. **Use Context Managers**: Ensure proper cleanup with context managers
6. **Set Appropriate Timeouts**: Configure timeouts based on your use case
7. **Validate Events**: The consumer automatically validates events using Pydantic

## Testing

See [Kafka Tests README](../../tests/kafka/README.md) for testing information.

## API Reference

### WorkflowEventConsumer

#### Methods

- `subscribe(topics: List[str])`: Subscribe to Kafka topics
- `consume_events(callback, topics, timeout_ms)`: Consume events and call callback
- `poll(timeout_ms)`: Poll for new messages
- `commit(offsets)`: Commit offsets
- `seek(partition, offset)`: Seek to specific offset
- `position(partition)`: Get current position
- `close(timeout_ms)`: Close consumer connection

#### Context Manager

The consumer supports context manager protocol:

```python
with WorkflowEventConsumer() as consumer:
    consumer.consume_events(callback, topics)
```

## See Also

- [Kafka Producer Guide](./kafka-producer-guide.md)
- [Event Schema Guide](./event-schema-guide.md)
- [Kafka Setup Guide](./kafka-setup-guide.md)

