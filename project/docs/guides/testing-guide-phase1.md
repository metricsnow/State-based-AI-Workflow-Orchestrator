# Testing Guide: Phase 1 - Docker Compose Environment

## Overview

This guide provides comprehensive testing procedures for the Docker Compose environment setup (TASK-001).

**Status**: ✅ Testing suite implemented with modular structure

## Testing Philosophy

**CRITICAL**: All tests run against the **production environment** - **NEVER with placeholders or mocks**.

### Core Principles

- **Real Services Only**: Tests connect to actual PostgreSQL, Kafka, Zookeeper, and Airflow services
- **Production Docker Containers**: Tests use real Docker containers from `docker-compose.yml`
- **Real Database Connections**: Tests use PostgreSQL (never SQLite or test databases)
- **Real Kafka Brokers**: Tests interact with actual Kafka brokers (not mocked or in-memory)
- **Real Airflow Instances**: Tests execute against actual Airflow services (not test databases)

### Why Production Environment?

1. **Accuracy**: Tests validate actual production behavior, not simulated behavior
2. **Reliability**: Tests catch real integration issues that mocks would miss
3. **Confidence**: Passing tests guarantee production readiness
4. **No Surprises**: What works in tests works in production

**No placeholders. No mocks. Production environment only.**

### Test Optimization Strategy

While maintaining production conditions, tests are optimized for speed using **faster timeouts and reduced wait times**:

- **Real Services**: All tests use real Kafka, real databases, real Airflow instances
- **Optimized Timeouts**: Reduced timeouts for faster test execution (e.g., Kafka timeout: 2s instead of 30s)
- **Faster Polling**: Reduced polling intervals (0.1s instead of 1.0s) for quicker test completion
- **Configurable**: All optimizations can be overridden via environment variables

**Test Configuration** (see `project/tests/conftest.py`):
- `TEST_KAFKA_TIMEOUT`: Kafka timeout in seconds (default: 2s, production: 30s)
- `TEST_WORKFLOW_TIMEOUT`: Workflow execution timeout in seconds (default: 5s, production: 300s)
- `TEST_POLL_INTERVAL`: Polling interval in seconds (default: 0.1s, production: 1.0s)
- `TEST_RETRY_DELAY`: Retry delay in seconds (default: 0.05s, production: 1.0s)
- `TEST_MAX_WAIT_ITERATIONS`: Maximum wait iterations (default: 10, production: 20)

**Available Test Fixtures**:
- `fast_retry_config`: Optimized retry configuration
- `fast_consumer_config`: Optimized Kafka consumer configuration
- `fast_poll_interval`: Fast polling interval
- `fast_max_wait_iterations`: Reduced wait iterations
- `fast_wait_loop`: Helper for fast wait loops

## Test Suite Structure

The test suite is organized by module in `project/tests/`:

```
project/tests/
├── infrastructure/          # Docker Compose & infrastructure tests
│   ├── test_docker_compose.py   # Configuration tests (11 tests)
│   ├── test_services.py         # Service health tests
│   ├── test_networking.py       # Network connectivity tests
│   └── test_volumes.py          # Volume persistence tests
├── airflow/                # Airflow tests (Phase 1.2+) ✅ 93 tests
│   ├── test_dag_imports.py         # DAG import validation (8 tests)
│   ├── test_dag_structure.py       # DAG structure validation (13 tests)
│   ├── test_task_functions.py      # Task function unit tests (16 tests)
│   ├── test_xcom_data_passing.py   # XCom data passing (36 tests) ✅ TASK-006
│   └── test_airflow_init.py        # Airflow initialization (13 tests)
└── kafka/                  # Kafka tests (Phase 1.3+) ✅ 53 tests
    ├── test_events.py              # Event schema validation (26 tests) ✅ TASK-010
    ├── test_producer.py            # Producer integration tests (12 tests) ✅ TASK-011
    └── test_consumer.py            # Consumer integration tests (15 tests) ✅ TASK-012
```

See `project/tests/README.md` for detailed test suite documentation.

## Pre-Flight Testing

### Automated Pre-Flight Checks

**Option 1: Pytest Test Suite** (Recommended)
```bash
source venv/bin/activate
pip install -r project/tests/infrastructure/requirements-test.txt
pytest project/tests/infrastructure/test_docker_compose.py -v
```

**Option 2: Shell Script**
```bash
./project/scripts/test-docker-compose.sh
```

Both methods validate:
- Docker Compose file syntax
- .env file existence and FERNET_KEY configuration
- Required directory structure
- Docker and Docker Compose installation
- Port availability
- Service definitions

**Test Results**: ✅ 11/11 configuration tests passing

### Manual Pre-Flight Checks

1. **Verify Docker is running**:
   ```bash
   docker ps
   ```

2. **Check Docker Compose version**:
   ```bash
   docker-compose --version
   ```

3. **Verify .env file exists**:
   ```bash
   ls -la .env
   ```

4. **Generate FERNET_KEY if needed**:
   ```bash
   source venv/bin/activate
   ./project/scripts/generate-fernet-key.sh
   ```

## Service Startup Testing

### Start All Services

```bash
docker-compose up -d
```

### Verify Service Status

```bash
docker-compose ps
```

Expected output should show all services as "healthy" or "running":
- `airflow-postgres`: healthy
- `airflow-zookeeper`: healthy
- `airflow-kafka`: healthy
- `airflow-webserver`: healthy
- `airflow-scheduler`: running

### Check Service Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler
docker-compose logs kafka
```

## Service Health Validation

### PostgreSQL Health Check

```bash
docker-compose exec postgres pg_isready -U airflow
```

Expected: `postgres:5432 - accepting connections`

### Zookeeper Health Check

```bash
docker-compose exec zookeeper nc -z localhost 2181
```

Expected: Exit code 0 (success)

### Kafka Health Check

```bash
docker-compose exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

Expected: List of API versions (no errors)

### Airflow Webserver Health Check

```bash
curl http://localhost:8080/health
```

Expected: HTTP 200 response

Or access in browser: http://localhost:8080

### Airflow Scheduler Check

```bash
docker-compose logs airflow-scheduler | tail -20
```

Expected: No critical errors, scheduler running

## Network Connectivity Testing

### Test Service-to-Service Communication

```bash
# Test Airflow to PostgreSQL
docker-compose exec airflow-webserver ping -c 2 postgres

# Test Kafka to Zookeeper
docker-compose exec kafka ping -c 2 zookeeper
```

### Test External Access

```bash
# Test Airflow UI
curl -I http://localhost:8080

# Test Kafka (requires kafka-python or kafkacat)
# Install: pip install kafka-python
python3 -c "from kafka import KafkaProducer; p = KafkaProducer(bootstrap_servers=['localhost:9092']); print('Kafka accessible')"
```

## Volume Persistence Testing

### Test PostgreSQL Volume

```bash
# Create test data
docker-compose exec postgres psql -U airflow -d airflow -c "CREATE TABLE test_table (id INT);"

# Stop services
docker-compose down

# Start services again
docker-compose up -d

# Wait for services to be healthy
sleep 30

# Verify data persists
docker-compose exec postgres psql -U airflow -d airflow -c "SELECT * FROM test_table;"
```

Expected: Table and data should still exist

## Service Restart Testing

### Test Individual Service Restart

```bash
# Restart a service
docker-compose restart airflow-webserver

# Verify it recovers
docker-compose ps airflow-webserver
```

### Test Full Stack Restart

```bash
# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Verify all services recover
docker-compose ps
```

## Integration Testing

### Kafka Integration Tests

**CRITICAL**: All Kafka tests use real Kafka brokers - NO MOCKS, NO PLACEHOLDERS.

```bash
# Ensure Kafka is running
docker-compose ps kafka

# Run all Kafka integration tests (53 tests)
pytest project/tests/kafka/ -v

# Run producer tests (12 tests - all use real Kafka)
pytest project/tests/kafka/test_producer.py -v

# Run consumer tests (15 tests - all use real Kafka)
pytest project/tests/kafka/test_consumer.py -v
```

**Test Coverage**:
- Producer initialization and connection to real Kafka
- Event publishing to real Kafka topics
- Consumer initialization and connection to real Kafka
- Event consumption from real Kafka topics
- End-to-end publish → consume flow verification
- Offset management with real Kafka
- Connection management (flush, close, context managers)

All tests connect to Kafka at `localhost:9092` and use actual Docker containers.

### Test Airflow Database Connection

```bash
docker-compose exec airflow-webserver airflow db check
```

Expected: Database connection successful

### Test Kafka Topic Creation

```bash
docker-compose exec kafka kafka-topics --create \
  --topic test-topic \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1

# List topics
docker-compose exec kafka kafka-topics --list \
  --bootstrap-server localhost:9092
```

Expected: `test-topic` appears in list

## Performance Testing

### Check Resource Usage

```bash
docker stats --no-stream
```

Monitor:
- CPU usage per container
- Memory usage per container
- Network I/O

### Check Service Startup Time

```bash
time docker-compose up -d
```

Expected: All services start within 2-3 minutes

## Troubleshooting Tests

### Test Service Dependencies

```bash
# Stop PostgreSQL and verify Airflow fails gracefully
docker-compose stop postgres
docker-compose logs airflow-webserver | tail -10

# Restart PostgreSQL
docker-compose start postgres
```

### Test Health Check Failures

```bash
# Manually fail a health check
docker-compose exec postgres pg_ctl stop

# Verify dependent services handle failure
docker-compose ps
```

## Cleanup Testing

### Test Clean Shutdown

```bash
docker-compose down
```

Verify:
- All containers stopped
- Network removed
- Volumes preserved (for postgres_data)

### Test Complete Cleanup

```bash
docker-compose down -v
```

**Warning**: This removes all volumes including database data!

## Acceptance Criteria Validation

Use this checklist to validate TASK-001 completion:

- [ ] Docker Compose file syntax valid
- [ ] All services start successfully
- [ ] All health checks passing
- [ ] Airflow webserver accessible at http://localhost:8080
- [ ] Airflow scheduler running
- [ ] Kafka accessible on port 9092
- [ ] PostgreSQL database initialized
- [ ] Services can communicate via Docker network
- [ ] Volume persistence working
- [ ] Service restart works correctly
- [ ] .env.example file created
- [ ] Documentation complete

## Running Tests with Pytest

### Configuration Tests (Fast, No Services Required)
```bash
pytest project/tests/infrastructure/test_docker_compose.py -v
```

**Expected**: 11 tests passing

### Integration Tests (Requires Running Services)
```bash
# Start services first
docker-compose up -d

# Run integration tests
pytest project/tests/infrastructure/test_services.py -v
pytest project/tests/infrastructure/test_networking.py -v
pytest project/tests/infrastructure/test_volumes.py -v
```

### Run All Infrastructure Tests
```bash
pytest project/tests/infrastructure/ -v
```

### Run with Markers
```bash
pytest project/tests/infrastructure/ -m health    # Health check tests
pytest project/tests/infrastructure/ -m network  # Network tests
pytest project/tests/infrastructure/ -m volume    # Volume tests
pytest project/tests/infrastructure/ -m integration  # All integration tests
```

## Test Results Template

```markdown
## Test Results - [Date]

### Pre-Flight Checks (pytest)
- [x] Docker Compose syntax: PASS (11/11 tests)
- [x] .env file: PASS
- [x] Directories: PASS
- [x] Docker installed: PASS
- [x] Ports available: PASS

### Service Startup
- [ ] All services started: PASS/FAIL
- [ ] Health checks passing: PASS/FAIL
- [ ] No errors in logs: PASS/FAIL

### Integration
- [ ] Airflow UI accessible: PASS/FAIL
- [ ] Kafka accessible: PASS/FAIL
- [ ] Database connection: PASS/FAIL

### Persistence
- [ ] Volume persistence: PASS/FAIL
- [ ] Service restart: PASS/FAIL

### Notes
[Any issues or observations]
```

## Test Suite Documentation

For detailed test suite documentation, see:
- **Main Test Suite**: `project/tests/README.md`
- **Infrastructure Tests**: `project/tests/infrastructure/README.md`
- **Pytest Configuration**: `pytest.ini`

## Airflow DAG Testing (TASK-004, TASK-006, TASK-007, TASK-008)

### Overview

Comprehensive test suite for Airflow DAG validation and testing.

**Status**: ✅ Complete - 108 tests passing, 97% coverage for TaskFlow DAGs

**Note**: DAGs have been migrated to TaskFlow API (TASK-005). XCom data passing patterns implemented (TASK-006). Comprehensive unit tests created (TASK-007). Integration tests for DAG execution implemented (TASK-008). Tests have been updated to work with TaskFlow decorators.

### Running Airflow Tests

**Prerequisites**:
```bash
# Activate virtual environment
source venv/bin/activate

# Install Airflow (if not already installed)
pip install apache-airflow==3.0.6 pytest pytest-cov

# Initialize Airflow database
export AIRFLOW_HOME=/tmp/airflow_test
airflow db migrate
```

**Run All Airflow Tests**:
```bash
# Set environment variables
export AIRFLOW_HOME=/tmp/airflow_test
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/project/dags

# Run all tests
pytest project/tests/airflow/ -v

# Run with coverage
pytest project/tests/airflow/ --cov=project/dags --cov-report=term-missing
```

**Test Results**:
- ✅ **Total Tests**: 108 tests (all Airflow tests)
- ✅ **TaskFlow Unit Tests**: 62 tests (TASK-007)
- ✅ **Integration Tests**: 13 tests (TASK-008)
- ✅ **Status**: All passing (108/108)
- ✅ **Coverage**: 97% for TaskFlow DAG code (exceeds 80% requirement)
- ✅ **Execution Time**: ~1 second for unit tests, ~3-4 seconds for integration tests

### Test Categories

1. **DAG Import Tests** (8 tests): Validate DAG files can be imported without errors
2. **DAG Structure Tests** (13 tests): Validate DAG structure, tasks, dependencies (TaskFlow API)
3. **Task Function Tests** (16 tests): ✅ Unit tests for task functions (no Airflow runtime, TaskFlow API) - TASK-007
4. **XCom Data Passing Tests** (36 tests): ✅ Comprehensive XCom data passing patterns (TASK-006)
   - Simple value passing (5 tests)
   - Dictionary passing (5 tests)
   - List passing (5 tests)
   - Multiple outputs (7 tests)
   - Data validation (8 tests)
   - Error handling (5 tests)
   - Integration (1 test)
5. **TaskFlow DAG Structure Tests** (10 tests): ✅ TaskFlow DAG structure validation (TASK-007)
6. **DAG Execution Integration Tests** (13 tests): ✅ Complete DAG execution with `dag.test()` method (TASK-008)
   - End-to-end DAG execution (2 tests)
   - Task execution and XCom validation (5 tests for example_etl_dag)
   - XCom data passing validation (8 tests for xcom_data_passing_dag)
     - Simple value passing
     - Dictionary passing
     - List passing
     - Multiple outputs passing
     - Data validation
     - Error handling
     - All tasks execution
7. **Airflow Init Tests** (13 tests): Airflow initialization and configuration

**TaskFlow API Migration**: All DAGs now use `@dag` and `@task` decorators. Task functions receive data via function arguments instead of manual XCom pulls.

**XCom Data Passing (TASK-006)**: Comprehensive data passing patterns implemented with full test coverage. See `xcom_data_passing_dag.py` for all patterns.

**Integration Testing (TASK-008)**: Complete DAG execution tests using `dag.test()` method:
- Tests end-to-end DAG execution in test environment
- Validates XCom data passing between tasks
- Validates task dependencies and execution order
- Tests error handling patterns
- Uses unique execution dates to prevent database conflicts
- Always specify `task_ids` explicitly when retrieving XCom values

For detailed integration test documentation, see `project/tests/airflow/README.md`.

**Unit Tests (TASK-007)**: Comprehensive unit tests for all TaskFlow DAGs with 97% coverage. Tests run independently without Airflow runtime. See `test_task_functions.py`, `test_xcom_data_passing.py`, and `test_taskflow_dag_structure.py`.

### Running Specific Test Files

```bash
# DAG import tests
pytest project/tests/airflow/test_dag_imports.py -v

# DAG structure tests
pytest project/tests/airflow/test_dag_structure.py -v

# Task function unit tests (no Airflow runtime needed)
pytest project/tests/airflow/test_task_functions.py -v

# XCom data passing tests (TASK-006 - 36 tests)
pytest project/tests/airflow/test_xcom_data_passing.py -v

# TaskFlow DAG structure tests (TASK-007 - 10 tests)
pytest project/tests/airflow/test_taskflow_dag_structure.py -v

# All TaskFlow unit tests (TASK-007 - 62 tests)
pytest project/tests/airflow/test_task_functions.py project/tests/airflow/test_xcom_data_passing.py project/tests/airflow/test_taskflow_dag_structure.py -v --cov=project/dags --cov-report=term-missing

# DAG execution integration tests (TASK-008 - 13 tests)
pytest project/tests/airflow/test_dag_execution.py -v
```

For detailed Airflow testing documentation, see:
- **Airflow Tests README**: `project/tests/airflow/README.md`
- **Main Test Suite**: `project/tests/README.md`

## Event Schema Testing (TASK-010)

### Overview

Comprehensive test suite for workflow event schema validation and serialization.

**Status**: ✅ Complete - 26 tests passing

**Module**: `project/workflow_events/` - Pydantic-based event schema definitions

### Running Event Schema Tests

**Prerequisites**:
```bash
# Activate virtual environment
source venv/bin/activate

# Ensure Pydantic is installed
pip install pydantic pytest
```

**Run All Event Schema Tests**:
```bash
# Run all event schema tests
pytest project/tests/kafka/test_events.py -v

# Run with verbose output and print statements
pytest project/tests/kafka/test_events.py -v -s

# Run Kafka integration tests with coverage
pytest project/tests/kafka/ --cov=workflow_events --cov-report=term-missing
```

**Test Results**:
- ✅ **Total Tests**: 26 tests
- ✅ **Status**: All passing (26/26)
- ✅ **Execution Time**: ~0.1 seconds
- ✅ **Coverage**: Event creation, validation, serialization, deserialization

### Test Categories

**Event Enums** (2 tests):
- Event type enumeration validation
- Event source enumeration validation

**Event Payload** (3 tests):
- Valid payload creation
- Empty payload handling
- Nested payload data

**Event Metadata** (4 tests):
- Valid metadata creation
- Default version handling
- Environment validation (dev/staging/prod)
- Invalid environment rejection

**Event Model** (5 tests):
- Event creation with defaults
- Event creation with explicit values
- Invalid event type rejection
- Invalid source rejection
- Missing required fields validation

**Serialization** (5 tests):
- Serialize to dictionary
- Serialize to JSON
- Deserialize from JSON
- Deserialize from dictionary
- Round-trip serialization

**Schema Versioning** (3 tests):
- Version field handling
- Custom version support
- Version in event metadata

**Validation** (4 tests):
- Empty workflow_id handling
- Complex nested payload data
- All event types validation
- All event sources validation

### Using Event Schema

**Import Event Models**:
```python
from workflow_events import (
    WorkflowEvent,
    EventType,
    EventSource,
    WorkflowEventPayload,
    WorkflowEventMetadata
)
```

**Create an Event**:
```python
event = WorkflowEvent(
    event_type=EventType.WORKFLOW_COMPLETED,
    source=EventSource.AIRFLOW,
    workflow_id="example_dag",
    workflow_run_id="run_123",
    payload=WorkflowEventPayload(data={"status": "success"}),
    metadata=WorkflowEventMetadata(environment="dev")
)
```

**Serialize to JSON**:
```python
json_str = event.model_dump_json()
```

**Deserialize from JSON**:
```python
event = WorkflowEvent.model_validate_json(json_str)
```

### Documentation

For complete event schema documentation, see:
- **[Event Schema Guide](event-schema-guide.md)** - Complete event schema documentation
- **[TASK-010](../dev/tasks/TASK-010.md)** - Implementation task details

## Next Steps

After successful testing:
1. ✅ TASK-001: Docker Compose Environment Setup - **COMPLETE**
2. ✅ TASK-002: Airflow Configuration and Initialization - **COMPLETE**
3. ✅ TASK-003: Basic DAG Creation - **COMPLETE**
4. ✅ TASK-004: DAG Validation and Testing - **COMPLETE** (57 tests, 100% coverage)
5. ✅ TASK-005: Migrate DAGs to TaskFlow API - **COMPLETE** (TaskFlow API implemented, all tests passing)
6. ✅ TASK-006: Implement Data Passing with XCom - **COMPLETE** (36 tests, all patterns implemented)
7. ✅ TASK-010: Event Schema Definition - **COMPLETE** (26 tests, Pydantic models, JSON schema)
8. ✅ TASK-007: Unit Tests for TaskFlow DAGs - **COMPLETE** (62 tests, 97% coverage)
9. ✅ TASK-009: Kafka Docker Setup - **COMPLETE**
10. Proceed to TASK-008: Integration Testing for TaskFlow DAGs (depends on TASK-007)
11. Proceed to TASK-011: Kafka Producer Implementation (depends on TASK-009, TASK-010)
12. Document any issues encountered
13. Run integration tests when services are started

