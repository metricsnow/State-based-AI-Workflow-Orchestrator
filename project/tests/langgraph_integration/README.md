# LangGraph Integration Tests

Tests for LangGraph Kafka integration, including async consumer, result publishing, and end-to-end workflow execution.

## Testing Philosophy

**CRITICAL**: Integration tests run against **production environment** - **NEVER with placeholders or mocks**.

- Integration tests connect to **real Kafka brokers** (running in Docker containers)
- Integration tests use **actual Kafka topics** (not in-memory implementations)
- Integration tests validate **real event consumption and processing**
- Integration tests verify **real result publishing and polling**

**Unit Tests**: Some unit tests use mocks for fast testing, but all functionality is validated in integration tests with real Kafka.

### Test Optimization

Tests use **real services with optimized timeouts** for faster execution:

- **Real Kafka**: All integration tests use real Kafka brokers (no mocks)
- **Optimized Timeouts**: Faster timeouts (Kafka: 2s, Workflow: 5s) for speed
- **Faster Polling**: Reduced polling intervals (0.1s) for quicker completion
- **Configurable**: All settings can be overridden via environment variables

**Test Configuration** (see `project/tests/conftest.py`):
- `TEST_KAFKA_TIMEOUT`: Kafka timeout (default: 2s)
- `TEST_WORKFLOW_TIMEOUT`: Workflow timeout (default: 5s)
- `TEST_POLL_INTERVAL`: Polling interval (default: 0.1s)
- `TEST_RETRY_DELAY`: Retry delay (default: 0.05s)
- `TEST_MAX_WAIT_ITERATIONS`: Max wait iterations (default: 10)

**Available Fixtures**:
- `fast_retry_config`: Optimized retry configuration
- `fast_consumer_config`: Optimized Kafka consumer config
- `fast_poll_interval`: Fast polling interval
- `fast_max_wait_iterations`: Reduced wait iterations
- `fast_wait_loop`: Helper for fast wait loops

## Test Files

### `test_config.py` ✅ Complete
Configuration management tests for ConsumerConfig.

**Status**: ✅ Complete
**Coverage**: Configuration loading from environment variables

### `test_consumer.py` ✅ Complete
Async Kafka consumer unit tests with real Kafka.

**Status**: ✅ Complete
**CRITICAL**: Uses real Kafka brokers - NO MOCKS, NO PLACEHOLDERS
**Coverage**:
- Consumer initialization
- Consumer start/stop lifecycle
- Event consumption
- Error handling

**Run Tests**:
```bash
pytest project/tests/langgraph_integration/test_consumer.py -v
```

### `test_consumer_integration.py` ✅ Complete (TASK-027)
Integration tests for async Kafka consumer with real Kafka.

**Status**: ✅ Complete - TASK-027
**CRITICAL**: All tests use production Kafka environment - NO MOCKS, NO PLACEHOLDERS
**Coverage**:
- Consumer startup and shutdown
- Event processing from real Kafka
- Workflow execution triggered by events
- Concurrent event processing
- Error handling and recovery

**Run Tests**:
```bash
# Ensure Kafka is running
docker-compose ps kafka

# Run integration tests
pytest project/tests/langgraph_integration/test_consumer_integration.py -v
```

### `test_processor.py` ✅ Complete
Event processing and workflow execution tests.

**Status**: ✅ Complete
**Coverage**:
- Event-to-state conversion
- Workflow execution
- Result extraction
- Error handling

**Run Tests**:
```bash
pytest project/tests/langgraph_integration/test_processor.py -v
```

### `test_result_producer.py` ⚠️ Unit Tests (TASK-028)
Result producer unit tests with mocked Kafka producer.

**Status**: ✅ Complete - TASK-028
**Note**: Uses mocks for fast unit testing. Functionality validated in `test_result_integration.py` with real Kafka.
**Coverage**:
- Producer initialization
- Result publishing
- Error handling
- Configuration

**Run Tests**:
```bash
pytest project/tests/langgraph_integration/test_result_producer.py -v
```

### `test_result_integration.py` ✅ Complete (TASK-028)
End-to-end result flow integration tests with real Kafka.

**Status**: ✅ Complete - TASK-028
**CRITICAL**: All tests use production Kafka environment - NO MOCKS, NO PLACEHOLDERS
**Coverage**:
- End-to-end result flow (trigger → process → result → poll)
- Correlation ID matching
- Timeout behavior
- Multiple result polling

**Run Tests**:
```bash
# Ensure Kafka is running
docker-compose ps kafka

# Run integration tests
pytest project/tests/langgraph_integration/test_result_integration.py -v
```

## Test Categories

### Integration Tests (Production Conditions)
These tests use real Kafka and production conditions:
- ✅ `test_consumer_integration.py` - Real Kafka consumer
- ✅ `test_result_integration.py` - Real Kafka end-to-end result flow
- ✅ `test_consumer.py` - Real Kafka consumer

### Unit Tests (Fast Testing with Mocks)
These tests use mocks for fast unit testing (validated by integration tests):
- ⚠️ `test_result_producer.py` - Mocked Kafka producer

## Running Tests

### Run All Integration Tests
```bash
# Ensure Kafka is running
docker-compose ps kafka

# Run all tests
pytest project/tests/langgraph_integration/ -v
```

### Run Only Integration Tests (Real Kafka)
```bash
# Run integration tests with real Kafka
pytest project/tests/langgraph_integration/test_consumer_integration.py -v
pytest project/tests/langgraph_integration/test_result_integration.py -v
```

### Run with Coverage
```bash
pytest project/tests/langgraph_integration/ \
  --cov=langgraph_integration \
  --cov-report=term-missing \
  --cov-report=html
```

## Test Dependencies

- **Kafka**: Must be running (via Docker Compose)
- **LangGraph**: LangGraph workflows must be installed
- **aiokafka**: Async Kafka client library

## Status

- **Total Tests**: 30+ tests
- **Integration Tests**: All use real Kafka - NO MOCKS, NO PLACEHOLDERS
- **Unit Tests**: Some use mocks (validated by integration tests)
- **Coverage**: Integration tests cover end-to-end workflow execution

## Related Documentation

- **[LangGraph Kafka Integration Guide](../../docs/langgraph-kafka-integration-guide.md)** - Complete integration guide
- **[Event Schema Guide](../../docs/event-schema-guide.md)** - WorkflowEvent schema documentation
- **[Kafka Producer Guide](../../docs/kafka-producer-guide.md)** - Publishing events to Kafka
- **[End-to-End Integration Tests](../integration/)** - Complete pipeline tests (Airflow → Kafka → LangGraph → Result) (TASK-032)

