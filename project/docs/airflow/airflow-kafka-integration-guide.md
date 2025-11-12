# Airflow-Kafka Integration Guide

This guide explains how to integrate Kafka event publishing into Airflow DAGs using the `airflow_integration` module.

## Overview

The Airflow-Kafka integration module provides utilities for publishing workflow events to Kafka from Airflow tasks. This enables event-driven coordination between Airflow and other systems (e.g., LangGraph in Phase 2).

## Key Features

- **Reusable Utilities**: Simple functions for publishing workflow events
- **TaskFlow API Support**: Designed to work seamlessly with Airflow TaskFlow API
- **Error Handling**: Graceful error handling that doesn't fail Airflow tasks
- **Environment Configuration**: Configuration via environment variables
- **Context Extraction**: Automatic extraction of DAG and run information from Airflow context

## Installation

The `airflow_integration` module is part of the project and doesn't require separate installation. Ensure the following dependencies are installed:

- `kafka-python` (from `workflow_events` module)
- `pydantic` (from `workflow_events` module)
- Apache Airflow 2.8.4+

## Configuration

### Environment Variables

Configure Kafka connection via environment variables:

```bash
# Kafka broker address (default: localhost:9092)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Environment for event metadata (default: dev)
# Must be one of: dev, staging, prod
ENVIRONMENT=dev

# Event schema version (default: 1.0)
EVENT_SCHEMA_VERSION=1.0
```

### Docker Compose

If using Docker Compose, Kafka is available at `localhost:9092` by default. The Airflow containers can access Kafka through the shared network.

## Usage

### Basic Usage: Publishing Events from Tasks

The simplest way to publish events is using the `publish_event_from_taskflow_context` helper function:

```python
from airflow.decorators import dag, task
from workflow_events import EventType
from airflow_integration import publish_event_from_taskflow_context

@dag(
    dag_id='example_dag',
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
)
def example_dag():
    @task
    def process_data(**context):
        """Process data and publish completion event."""
        # Your task logic here
        result = {"status": "success", "count": 100}
        
        # Publish completion event
        publish_event_from_taskflow_context(
            event_type=EventType.WORKFLOW_COMPLETED,
            payload={
                "status": "success",
                "result": result
            },
            **context
        )
        
        return result
    
    process_data()

example_dag()
```

### Publishing Task Completion Events

Use `publish_task_completion_event` for automatic task completion events:

```python
from airflow_integration import publish_task_completion_event

@task
def my_task(**context):
    try:
        result = process_data()
        
        # Publish success event
        publish_task_completion_event(
            task_id=context['ti'].task_id,
            dag_id=context['ti'].dag_id,
            dag_run_id=context['ti'].dag_run_id,
            task_result=result,
            task_status="success"
        )
        
        return result
    except Exception as e:
        # Publish failure event
        publish_task_completion_event(
            task_id=context['ti'].task_id,
            dag_id=context['ti'].dag_id,
            dag_run_id=context['ti'].dag_run_id,
            task_status="failed",
            error_message=str(e)
        )
        raise
```

### Publishing DAG Completion Events

Use `publish_dag_completion_event` for DAG-level completion events:

```python
from airflow_integration import publish_dag_completion_event

# In a DAG completion callback or final task
publish_dag_completion_event(
    dag_id="example_dag",
    dag_run_id="run_123",
    dag_status="success",
    task_results={"task1": "success", "task2": "success"}
)
```

### Advanced Usage: Custom Event Publishing

For more control, use `publish_workflow_event` directly:

```python
from airflow_integration import publish_workflow_event
from workflow_events import EventType

publish_workflow_event(
    event_type=EventType.WORKFLOW_TRIGGERED,
    workflow_id="example_dag",
    workflow_run_id="run_123",
    payload={
        "custom_data": "value",
        "metadata": {"key": "value"}
    },
    metadata={
        "environment": "prod",
        "version": "1.0"
    },
    topic="workflow-events"
)
```

## Integration Example

See `project/dags/example_etl_dag.py` for a complete example of Kafka integration in an ETL DAG:

```python
@task
def publish_completion(load_result: Dict[str, Any], **context) -> None:
    """Publish workflow completion event to Kafka."""
    publish_event_from_taskflow_context(
        event_type=EventType.WORKFLOW_COMPLETED,
        payload={
            "status": "success",
            "etl_result": load_result,
            "message": "ETL workflow completed successfully"
        },
        **context
    )
```

## Error Handling

All integration functions are designed to **never fail Airflow tasks**. If Kafka publishing fails:

1. Errors are logged with full traceback
2. Functions return `False` to indicate failure
3. Airflow tasks continue execution normally

This ensures that Kafka connectivity issues don't break your workflows.

## Event Schema

Events follow the `WorkflowEvent` schema defined in `workflow_events.schema`:

- **event_id**: Unique UUID for the event
- **event_type**: Type of event (WORKFLOW_TRIGGERED, WORKFLOW_COMPLETED, WORKFLOW_FAILED)
- **timestamp**: ISO 8601 timestamp
- **source**: Event source (AIRFLOW, LANGGRAPH, FASTAPI)
- **workflow_id**: DAG ID or workflow identifier
- **workflow_run_id**: DAG run ID or workflow run identifier
- **payload**: Workflow-specific data
- **metadata**: Environment and version information

## Testing

Comprehensive tests are available in `project/tests/airflow/test_kafka_integration.py`:

```bash
# Run integration tests (requires running Kafka)
pytest project/tests/airflow/test_kafka_integration.py -v
```

### Testing Philosophy

**CRITICAL**: All Kafka integration tests run against the **production environment** - **NEVER with placeholders or mocks**.

- Tests connect to **real Kafka brokers** (running in Docker containers)
- Tests use **actual Kafka topics** (not mocked)
- Tests validate **real event publishing and consumption**
- Tests verify **end-to-end publish → consume flow** with real Kafka
- All producer/consumer connections are **real connections**

**No placeholders. No mocks. Production Kafka environment only.**

### Test Coverage

The test suite includes **15 comprehensive tests**:

1. **Producer Tests** (3 tests):
   - Producer creation with default configuration
   - Producer creation with explicit bootstrap servers
   - Producer connection to real Kafka

2. **Event Publishing Tests** (4 tests):
   - Successful event publishing
   - Failed workflow event publishing
   - Event publishing with custom metadata
   - End-to-end verification (publish → consume from real Kafka)

3. **Task Completion Events** (2 tests):
   - Success status events
   - Failed status events

4. **DAG Completion Events** (2 tests):
   - Success status events
   - Failed status events

5. **TaskFlow Context Integration** (3 tests):
   - Publishing with dag_run context
   - Publishing with ti (TaskInstance) context
   - Publishing with explicit DAG IDs
   - Error handling for missing context

### Prerequisites

Before running tests, ensure Kafka is running:

```bash
# Check Kafka status
docker-compose ps kafka

# Start Kafka if not running
docker-compose up -d kafka zookeeper
```

### Running Tests

```bash
# Run all Kafka integration tests
pytest project/tests/airflow/test_kafka_integration.py -v

# Run specific test class
pytest project/tests/airflow/test_kafka_integration.py::TestPublishWorkflowEvent -v

# Run with coverage
pytest project/tests/airflow/test_kafka_integration.py --cov=project/airflow_integration --cov-report=term-missing
```

## Best Practices

1. **Use Helper Functions**: Prefer `publish_event_from_taskflow_context` over direct producer usage
2. **Error Handling**: Always handle errors gracefully - functions won't raise exceptions
3. **Environment Variables**: Use environment variables for configuration, never hardcode
4. **Event Payloads**: Keep payloads simple and serializable (dicts, lists, primitives)
5. **Context Passing**: Always pass `**context` to helper functions for automatic context extraction

## Troubleshooting

### Events Not Published

1. Check Kafka connectivity: `docker-compose ps` to verify Kafka is running
2. Check environment variables: Ensure `KAFKA_BOOTSTRAP_SERVERS` is set correctly
3. Check logs: Look for error messages in Airflow task logs
4. Verify topic exists: Kafka topic `workflow-events` should exist (auto-created on first publish)

### Validation Errors

If you see Pydantic validation errors:
- Ensure `ENVIRONMENT` is one of: `dev`, `staging`, `prod`
- Check that payload data is serializable (no complex objects)

### Connection Errors

If Kafka connection fails:
- Verify Kafka is running: `docker-compose ps kafka`
- Check network connectivity from Airflow containers
- Verify `KAFKA_BOOTSTRAP_SERVERS` is accessible from Airflow

## LangGraph Workflow Integration

### Triggering LangGraph Workflows from Airflow

The `trigger_langgraph_workflow` function provides a complete integration pattern for triggering LangGraph workflows from Airflow tasks. This function:

1. Publishes a `WORKFLOW_TRIGGERED` event to Kafka
2. Waits for the LangGraph workflow to process the event
3. Polls for the workflow result
4. Returns the result to the Airflow task

**Status**: ✅ TASK-030 Complete

### Usage

```python
from airflow.decorators import dag, task
from airflow_integration.langgraph_trigger import trigger_langgraph_workflow

@dag(
    dag_id="langgraph_workflow_example",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
)
def langgraph_workflow_dag():
    @task
    def prepare_data():
        """Prepare data for LangGraph workflow."""
        return {
            "task": "analyze_trading_data",
            "data": {
                "symbol": "AAPL",
                "date_range": "2025-01-01:2025-01-31",
            }
        }
    
    @task
    def trigger_workflow(task_data, **context):
        """Trigger LangGraph workflow and wait for result."""
        return trigger_langgraph_workflow(
            task_data=task_data,
            timeout=300,  # 5 minutes timeout
            **context
        )
    
    @task
    def process_result(workflow_result):
        """Process the workflow result."""
        print(f"Workflow completed: {workflow_result}")
        return workflow_result
    
    # Task dependencies
    data = prepare_data()
    result = trigger_workflow(data)
    process_result(result)

langgraph_workflow_dag()
```

### Function Parameters

- **`task_data`** (Dict[str, Any]): Data to pass to the LangGraph workflow. Should contain:
  - `task`: Task description/type
  - `data`: Workflow-specific data
- **`workflow_id`** (Optional[str]): Override workflow ID. Defaults to DAG ID from context.
- **`timeout`** (int): Timeout in seconds for result polling. Default: 300 seconds (5 minutes).
- **`**context`**: Airflow context (automatically provided by TaskFlow API).

### Return Value

Returns a dictionary containing the workflow result:
```python
{
    "completed": True,
    "agent_results": {...},
    "task": "...",
    "metadata": {...}
}
```

### Error Handling

The function handles various error scenarios:

- **Timeout**: Raises `TimeoutError` if result not received within timeout
- **Workflow Failure**: Raises `RuntimeError` if workflow execution failed
- **Event Publishing Failure**: Raises `RuntimeError` if event cannot be published
- **Missing Context**: Raises `ValueError` if Airflow context is not available

### Configuration

The function uses the same environment variables as other Kafka integration functions:

```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_WORKFLOW_EVENTS_TOPIC=workflow-events
KAFKA_WORKFLOW_RESULTS_TOPIC=workflow-results
```

### Example DAG

See `project/dags/langgraph_integration_dag.py` for a complete example demonstrating:
- Data preparation
- Workflow triggering
- Result processing
- Error handling

### Test Coverage

- ✅ 11 comprehensive tests (9 unit + 2 integration)
- ✅ All tests use production conditions (real Kafka, no mocks)
- ✅ Detailed status output for debugging
- ✅ All tests passing

## API Reference

### Functions

#### `get_kafka_producer(bootstrap_servers=None) -> WorkflowEventProducer`

Get a Kafka producer instance. Uses environment variable `KAFKA_BOOTSTRAP_SERVERS` if not provided.

#### `publish_workflow_event(...) -> bool`

Publish a generic workflow event to Kafka. Returns `True` on success, `False` on failure.

#### `publish_task_completion_event(...) -> bool`

Publish a task completion event. Automatically determines event type based on task status.

#### `publish_dag_completion_event(...) -> bool`

Publish a DAG completion event. Automatically determines event type based on DAG status.

#### `publish_event_from_taskflow_context(...) -> bool`

Publish an event from TaskFlow task context. Automatically extracts DAG and run information.

#### `trigger_langgraph_workflow(task_data, workflow_id=None, timeout=300, **context) -> Dict[str, Any]`

Trigger a LangGraph workflow from an Airflow task. Publishes a workflow trigger event to Kafka and polls for the result.

**Parameters**:
- `task_data` (Dict[str, Any]): Data to pass to LangGraph workflow
- `workflow_id` (Optional[str]): Override workflow ID (defaults to DAG ID)
- `timeout` (int): Timeout in seconds for result polling (default: 300)
- `**context`: Airflow context (automatically provided)

**Returns**: Dictionary containing workflow result data

**Raises**:
- `ValueError`: If Airflow context is not available
- `RuntimeError`: If event publishing or workflow execution fails
- `TimeoutError`: If result not received within timeout period

## Related Documentation

- [Kafka Producer Guide](kafka-producer-guide.md)
- [Kafka Consumer Guide](kafka-consumer-guide.md)
- [Event Schema Guide](event-schema-guide.md)
- [TaskFlow API Guide](taskflow-api-guide.md)
- [LangGraph Kafka Integration Guide](langgraph-kafka-integration-guide.md) - Complete LangGraph-Kafka integration documentation

