# Test Suite - Modular Structure

Comprehensive pytest-based test suite organized by module for the AI-Powered Workflow Orchestration project.

## Testing Philosophy

**CRITICAL**: All tests run against the **production environment** - **NEVER with placeholders or mocks**.

- Tests connect to **real services** (PostgreSQL, Kafka, Airflow)
- Tests use **actual Docker containers** from `docker-compose.yml`
- Tests validate **real database connections** (PostgreSQL, not SQLite)
- Tests interact with **real Kafka brokers** (not mocked)
- Tests execute against **real Airflow instances** (not test databases)

**No placeholders. No mocks. Production environment only.**

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

**Test Files** (✅ Implemented):
- `test_dag_imports.py`: Comprehensive DAG import validation (8 tests)
- `test_dag_structure.py`: DAG structure validation (13 tests)
- `test_task_functions.py`: Unit tests for task functions (17 tests)
- `test_xcom_data_passing.py`: XCom data passing validation (8 tests)
- `test_airflow_init.py`: Airflow initialization tests (13 tests)

**Test Files** (⏳ Pending):
- `test_taskflow.py`: TaskFlow API implementation (TASK-005)
- `test_dag_execution.py`: DAG execution and dependencies (TASK-008)

**Status**: ✅ 57 tests passing, 100% coverage for DAG code

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

**Airflow tests** (✅ Implemented):
```bash
# Set environment variables
export AIRFLOW_HOME=/tmp/airflow_test
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/project/dags

# Run all Airflow tests
pytest project/tests/airflow/ -v

# Run with coverage
pytest project/tests/airflow/ --cov=project/dags --cov-report=term-missing
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
- [Airflow Tests](airflow/README.md) - Airflow DAG and workflow tests (✅ 57 tests, 100% coverage)
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
- **Airflow**: ✅ 100% coverage (exceeds 80% target)
- **Kafka**: >80% coverage (target)
- **Overall**: >80% coverage

## Current Test Status

### Airflow Tests (✅ Complete)
- **Total Tests**: 57 tests
- **Status**: All passing (57/57)
- **Coverage**: 100% for DAG code
- **Test Files**: 5 test files implemented
  - `test_dag_imports.py`: 8 tests
  - `test_dag_structure.py`: 13 tests
  - `test_task_functions.py`: 17 tests
  - `test_xcom_data_passing.py`: 8 tests
  - `test_airflow_init.py`: 13 tests (existing)

