# Test Suite - Modular Structure

Comprehensive pytest-based test suite organized by module for the AI-Powered Workflow Orchestration project.

## Test Structure

```
project/tests/
├── __init__.py              # Package initialization
├── conftest.py              # Shared fixtures for all modules
├── infrastructure/          # Infrastructure and Docker Compose tests
│   ├── __init__.py
│   ├── conftest.py          # Infrastructure-specific fixtures
│   ├── test_docker_compose.py   # Docker Compose config tests
│   ├── test_services.py         # Service health tests
│   ├── test_networking.py       # Network connectivity tests
│   ├── test_volumes.py          # Volume persistence tests
│   └── README.md
├── airflow/                 # Airflow-specific tests (Phase 1.2+)
│   ├── __init__.py
│   ├── conftest.py          # Airflow-specific fixtures
│   ├── test_dag_structure.py    # DAG structure validation
│   ├── test_taskflow.py         # TaskFlow API tests
│   └── README.md
└── kafka/                   # Kafka-specific tests (Phase 1.3+)
    ├── __init__.py
    ├── conftest.py          # Kafka-specific fixtures
    ├── test_producer.py         # Producer tests
    ├── test_consumer.py         # Consumer tests
    ├── test_events.py            # Event schema tests
    └── README.md
```

## Module Organization

### Infrastructure Module (`infrastructure/`)
Tests for Docker Compose environment, service setup, networking, and volumes.

**Test Files**:
- `test_docker_compose.py`: Configuration and setup validation
- `test_services.py`: Service health and functionality
- `test_networking.py`: Network connectivity and ports
- `test_volumes.py`: Volume persistence

**Markers**: `@pytest.mark.docker`, `@pytest.mark.integration`

### Airflow Module (`airflow/`)
Tests for Airflow DAGs, TaskFlow API, and workflow execution.

**Test Files** (to be implemented):
- `test_dag_structure.py`: DAG structure validation
- `test_taskflow.py`: TaskFlow API implementation
- `test_dag_execution.py`: DAG execution and dependencies

**Markers**: `@pytest.mark.airflow`, `@pytest.mark.dag`

### Kafka Module (`kafka/`)
Tests for Kafka producers, consumers, and event streaming.

**Test Files** (to be implemented):
- `test_producer.py`: Kafka producer functionality
- `test_consumer.py`: Kafka consumer functionality
- `test_events.py`: Event schema validation

**Markers**: `@pytest.mark.kafka`, `@pytest.mark.events`

## Running Tests

### Run All Tests
```bash
pytest project/tests/
```

### Run by Module

**Infrastructure tests**:
```bash
pytest project/tests/infrastructure/
```

**Airflow tests** (when implemented):
```bash
pytest project/tests/airflow/
```

**Kafka tests** (when implemented):
```bash
pytest project/tests/kafka/
```

### Run by Marker

**Docker-related tests**:
```bash
pytest project/tests/ -m docker
```

**Integration tests**:
```bash
pytest project/tests/ -m integration
```

**Airflow tests**:
```bash
pytest project/tests/ -m airflow
```

**Kafka tests**:
```bash
pytest project/tests/ -m kafka
```

## Test Dependencies

Install test dependencies:
```bash
source venv/bin/activate
pip install -r project/tests/infrastructure/requirements-test.txt
```

## Module-Specific Documentation

- [Infrastructure Tests](infrastructure/README.md) - Docker Compose and service tests
- [Airflow Tests](airflow/README.md) - Airflow DAG and workflow tests (coming soon)
- [Kafka Tests](kafka/README.md) - Kafka producer/consumer tests (coming soon)

## Adding New Tests

When adding tests for a new module:

1. Create module directory: `project/tests/<module_name>/`
2. Add `__init__.py` with module description
3. Create `conftest.py` for module-specific fixtures
4. Add test files following `test_*.py` pattern
5. Update this README with module documentation

## Test Coverage Goals

- **Infrastructure**: >90% coverage
- **Airflow**: >80% coverage (target)
- **Kafka**: >80% coverage (target)
- **Overall**: >80% coverage

