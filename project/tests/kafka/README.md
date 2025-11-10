# Kafka Tests

Tests for Kafka producers, consumers, and event streaming.

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

### `test_producer.py` (To Be Implemented)
Kafka producer functionality tests.

**Status**: Planned for TASK-011

### `test_consumer.py` (To Be Implemented)
Kafka consumer functionality tests.

**Status**: Planned for TASK-012

## Status

- ✅ **Event Schema Tests** (TASK-010): Complete - 26 tests passing
- ⏳ **Producer Tests** (TASK-011): Planned
- ⏳ **Consumer Tests** (TASK-012): Planned

## Running Tests

```bash
# Run all Kafka tests
pytest project/tests/kafka/ -v

# Run only event schema tests
pytest project/tests/kafka/test_events.py -v

# Run with coverage
pytest project/tests/kafka/test_events.py --cov=workflow_events --cov-report=term-missing
```

## Event Schema Module

The event schema is implemented in `project/workflow_events/`:

- **schema.py**: Pydantic models for event validation
- **schema_utils.py**: JSON schema generation utilities
- **__init__.py**: Module exports

See [Event Schema Guide](../../docs/event-schema-guide.md) for complete documentation.

