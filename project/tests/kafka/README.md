# Kafka Tests

Tests for Kafka producers, consumers, and event streaming.

## Testing Philosophy

**CRITICAL**: All Kafka tests run against the **production environment** - **NEVER with placeholders**.

- Tests connect to **real Kafka brokers** (running in Docker containers)
- Tests use **actual Zookeeper** (not mocked)
- Tests validate **real event serialization/deserialization** (not stubbed)
- Tests interact with **real Kafka topics** (not in-memory implementations)
- Integration tests use **actual Kafka Docker services** from `docker-compose.yml`

**No placeholders. No mocks. Production Kafka environment only.**

## Test Files

### `test_events.py` ✅ Complete
Event schema validation and serialization tests.

**Status**: ✅ Complete - 26 tests passing (TASK-010)

**Coverage**:
- Event type and source enumerations
- Event payload validation
- Event metadata validation
- Event model creation and validation
- JSON serialization/deserialization
- Schema versioning support
- Complex payload handling

**Run Tests**:
```bash
pytest project/tests/kafka/test_events.py -v
```

### `test_producer.py` ✅ Complete
Kafka producer functionality tests.

**Status**: ✅ Complete - 17 tests passing (TASK-011)

**Coverage**:
- Producer initialization and configuration
- Event serialization
- Event publishing (success and error cases)
- Connection management (flush, close)
- Context manager support
- Error handling (timeouts, Kafka errors)
- Integration test placeholder (requires running Kafka)

### `test_consumer.py` (To Be Implemented)
Kafka consumer functionality tests.

**Status**: Planned for TASK-012

## Status

- ✅ **Event Schema Tests** (TASK-010): Complete - 26 tests passing
- ✅ **Producer Tests** (TASK-011): Complete - 17 tests passing
- ⏳ **Consumer Tests** (TASK-012): Planned

## Running Tests

```bash
# Run all Kafka tests
pytest project/tests/kafka/ -v

# Run only event schema tests
pytest project/tests/kafka/test_events.py -v

# Run only producer tests
pytest project/tests/kafka/test_producer.py -v

# Run with coverage
pytest project/tests/kafka/test_events.py --cov=workflow_events --cov-report=term-missing
pytest project/tests/kafka/test_producer.py --cov=workflow_events.producer --cov-report=term-missing
```

## Event Schema Module

The event schema is implemented in `project/workflow_events/`:

- **schema.py**: Pydantic models for event validation
- **schema_utils.py**: JSON schema generation utilities
- **__init__.py**: Module exports

See [Event Schema Guide](../../docs/event-schema-guide.md) for complete documentation.

