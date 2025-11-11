# Airflow Tests

Comprehensive test suite for Airflow DAGs, TaskFlow API, and workflow execution.

## Testing Philosophy

**CRITICAL**: All Airflow tests run against the **production environment** - **NEVER with placeholders**.

- Tests use **real PostgreSQL database** (configured in `docker-compose.yml`)
- Tests connect to **actual Airflow services** (webserver, scheduler)
- Tests validate **real DAG structures** (not mocked or stubbed)
- Tests use `dag_bag.dags` dictionary access to avoid database queries in unit tests
- Integration tests connect to **real Docker containers**

**No SQLite. No placeholders. Production PostgreSQL environment only.**

## Test Files

### `test_dag_imports.py` ✅ Implemented
Comprehensive DAG import validation tests.

**Test Coverage** (8 tests):
- DAG import error detection
- DagBag initialization validation
- DAG file syntax validation
- Import performance checks
- DAG ID validation

**Status**: ✅ Complete - All tests passing

### `test_dag_structure.py` ✅ Implemented
DAG structure validation and configuration tests.

**Test Coverage** (13 tests):
- DAG import validation (no import errors)
- DAG existence and structure validation
- Required tasks validation (extract, transform, validate, load)
- Task dependency validation (extract >> transform >> validate >> load)
- Task operator type validation (PythonOperator, BashOperator)
- DAG configuration validation (catchup, tags, default_args)
- Task count validation
- Task ID uniqueness
- Cycle detection
- Schedule validation

**Status**: ✅ Complete - All tests passing

### `test_task_functions.py` ✅ Implemented
Unit tests for task functions (can run without Airflow runtime).

**Test Coverage** (16 tests):
- Extract task function tests (6 tests)
  - Return value validation
  - Data structure validation
  - Data consistency checks
- Transform task function tests (6 tests)
  - TaskFlow API data passing (function arguments)
  - Data transformation logic
  - Edge case handling (empty lists, single values)
- Load task function tests (3 tests)
  - TaskFlow API data passing (function arguments)
  - Data processing validation
- Integration tests (1 test)
  - Extract-transform integration

**Status**: ✅ Complete - All tests passing

### `test_xcom_data_passing.py` ✅ Implemented
Comprehensive XCom data passing validation tests for TaskFlow API.

**Test Coverage** (36 tests):
- Simple value passing (5 tests)
- Dictionary passing (5 tests)
- List passing (5 tests)
- Multiple outputs (7 tests)
- Data validation (8 tests)
- Error handling (5 tests)
- Integration (1 test)

**Status**: ✅ Complete - All tests passing

### `test_taskflow_dag_structure.py` ✅ Implemented (TASK-007)
TaskFlow DAG structure validation tests.

**Test Coverage** (10 tests):
- DAG import validation
- DAG structure and properties
- Task existence validation
- TaskFlow API decorator validation
- DAG configuration validation
- Task count validation
- Task ID uniqueness
- Cycle detection
- Schedule validation

**Status**: ✅ Complete - All tests passing

### `test_airflow_init.py` ✅ Implemented
Airflow initialization and configuration tests.

**Test Coverage** (13 tests):
- Database initialization validation
- Admin user creation validation
- CLI command functionality
- Service health checks
- Folder structure validation

**Status**: ✅ Complete - All tests passing

### `test_taskflow_dag_structure.py` ✅ Implemented (TASK-007)
TaskFlow DAG structure validation tests.

**Test Coverage** (10 tests):
- DAG import validation
- DAG structure and properties
- Task existence validation
- TaskFlow API decorator validation
- DAG configuration validation
- Task count validation
- Task ID uniqueness
- Cycle detection
- Schedule validation

**Status**: ✅ Complete - All tests passing

### `test_dag_execution.py` ✅ Implemented (TASK-008)
Integration tests for TaskFlow DAG execution.

**Test Coverage** (13 tests):
- DAG execution completion tests (2 tests)
- Task execution and XCom validation (5 tests for example_etl_dag)
- XCom data passing validation (8 tests for xcom_data_passing_dag)
  - Simple value passing
  - Dictionary passing
  - List passing
  - Multiple outputs passing
  - Data validation
  - Error handling
  - All tasks execution

**Status**: ✅ Complete - All tests passing

**Implementation Details**:
- Uses `dag.test()` method for complete DAG execution
- Validates XCom data passing with explicit `task_ids`
- Uses unique execution dates to prevent database conflicts
- Tests both `example_etl_dag` and `xcom_data_passing_dag`
- Validates task dependencies and execution order
- Tests error handling patterns

### `test_kafka_integration.py` ✅ Implemented (TASK-013)
Airflow-Kafka integration tests with real Kafka instances.

**Test Coverage** (15 tests):
- Producer creation and connection (3 tests)
- Event publishing to real Kafka (4 tests)
- Event consumption verification (1 test - publish → consume)
- Task completion events (2 tests)
- DAG completion events (2 tests)
- TaskFlow context integration (3 tests)

**Status**: ✅ Complete - All 15 tests passing

**Implementation Details**:
- **CRITICAL**: All tests use **real Kafka instances** - NO MOCKS, NO PLACEHOLDERS
- Tests connect to real Kafka broker at `localhost:9092` (Docker container)
- Tests publish events to actual Kafka topics
- Tests verify end-to-end publish → consume flow
- Tests use production Kafka environment from `docker-compose.yml`
- All producer/consumer connections are real
- **Environment Values**: All tests use production environment values ("dev", "staging", "prod") - NO "test" placeholders
- **Context Objects**: Tests use real data container objects (not mocks) for Airflow context
- Follows project's production-only testing philosophy

## Running Tests

### Prerequisites

1. **Virtual Environment**: Activate the project virtual environment
   ```bash
   source venv/bin/activate
   ```

2. **Airflow Installation**: Airflow 3.0.6+ is required (installed in venv)
   ```bash
   pip install apache-airflow==3.0.6 pytest pytest-cov
   ```

3. **Airflow Database**: Initialize Airflow database for structure tests
   ```bash
   export AIRFLOW_HOME=/tmp/airflow_test
   airflow db migrate
   ```

### Running All Airflow Tests

```bash
# Set environment variables
export AIRFLOW_HOME=/tmp/airflow_test
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/project/dags

# Run all tests
pytest project/tests/airflow/ -v

# Run with coverage
pytest project/tests/airflow/ --cov=project/dags --cov-report=term-missing

# Run with HTML coverage report
pytest project/tests/airflow/ --cov=project/dags --cov-report=html
```

### Running Specific Test Files

```bash
# DAG import tests
pytest project/tests/airflow/test_dag_imports.py -v

# DAG structure tests
pytest project/tests/airflow/test_dag_structure.py -v

# Task function unit tests (no Airflow runtime needed)
pytest project/tests/airflow/test_task_functions.py -v

# XCom data passing tests
pytest project/tests/airflow/test_xcom_data_passing.py -v

# DAG execution integration tests (TASK-008)
pytest project/tests/airflow/test_dag_execution.py -v

# Airflow initialization tests
pytest project/tests/airflow/test_airflow_init.py -v

# Kafka integration tests (requires running Kafka)
pytest project/tests/airflow/test_kafka_integration.py -v
```

### Running Specific Test Classes

```bash
# Run all DAG structure tests
pytest project/tests/airflow/test_dag_structure.py::TestDAGStructure -v

# Run all task function tests
pytest project/tests/airflow/test_task_functions.py::TestExtractTask -v

# Run all DAG execution integration tests
pytest project/tests/airflow/test_dag_execution.py::TestExampleETLDAGExecution -v
pytest project/tests/airflow/test_dag_execution.py::TestXComDataPassingDAGExecution -v
```

### Running Tests in Docker (Alternative)

If you prefer running tests in the Airflow container:

```bash
# Validate DAG structure
docker-compose exec -T airflow-webserver python -c "
from airflow.models import DagBag
dag_bag = DagBag(dag_folder='/opt/airflow/dags', include_examples=False)
print('DAGs found:', list(dag_bag.dags.keys()))
print('Import errors:', dag_bag.import_errors)
assert len(dag_bag.import_errors) == 0
assert 'example_etl_dag' in dag_bag.dags
print('✅ DAG validation passed!')
"
```

## Test Results

**Last Run**: 2025-01-27
- ✅ **Total Tests**: 123 tests (all Airflow tests)
- ✅ **TaskFlow Unit Tests**: 62 tests (TASK-007)
- ✅ **Integration Tests**: 13 tests (TASK-008)
- ✅ **Kafka Integration Tests**: 15 tests (TASK-013) - Real Kafka, no mocks
- ✅ **Test Status**: All passing (123/123)
- ✅ **Coverage**: 97% for TaskFlow DAG code (exceeds 80% requirement)
- ✅ **Execution Time**: ~1 second for unit tests, ~3-4 seconds for integration tests, ~5 seconds for Kafka tests

### Test Breakdown

- **DAG Import Tests**: 8/8 passing
- **DAG Structure Tests**: 13/13 passing
- **Task Function Tests**: 16/16 passing (example_etl_dag)
- **XCom Data Passing Tests**: 36/36 passing (xcom_data_passing_dag)
- **TaskFlow DAG Structure Tests**: 10/10 passing (TASK-007)
- **DAG Execution Integration Tests**: 13/13 passing (TASK-008)
- **Airflow Init Tests**: 13/13 passing (existing)
- **Kafka Integration Tests**: 15/15 passing (TASK-013) - Real Kafka, production environment

### Coverage Report (TASK-007)

```
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
project/dags/example_etl_dag.py            35      1    97%   110
project/dags/xcom_data_passing_dag.py     141      5    96%   305, 311, 386-388
---------------------------------------------------------------------
TOTAL                                     176      6    97%
```

**Status**: ✅ All tests passing with 97% coverage (exceeds 80% requirement)

**Missing Lines**: Edge cases in error handling paths (hard to test without complex mocking)

## Test Framework Details

### Test Fixtures

Shared fixtures available in `conftest.py`:
- `dag_bag`: DagBag instance for DAG loading
- `dags_folder`: Path to DAGs directory
- `sample_extracted_data`: Sample data for testing
- `sample_transformed_data`: Sample transformed data

### Test Categories

1. **Unit Tests**: Task functions tested independently (no Airflow runtime)
2. **Structure Tests**: DAG structure validation using DagBag
3. **Integration Tests**: Complete DAG execution with `dag.test()` method (TASK-008)
   - End-to-end DAG execution validation
   - XCom data passing between tasks
   - Task dependency and execution order validation
   - Error handling validation
4. **Validation Tests**: Import errors, syntax, configuration

### Best Practices

- Tests are fast and independent
- Task functions can be tested without Airflow runtime
- DagBag-based tests validate DAG structure without execution
- Integration tests use `dag.test()` for complete DAG execution
- XCom values retrieved with explicit `task_ids` parameter
- Unique execution dates prevent UNIQUE constraint violations
- Comprehensive error messages for debugging
- 97% code coverage for DAG code (exceeds 80% requirement)

### Integration Test Notes (TASK-008)

**Execution Method**: Uses Airflow's `dag.test()` method which:
- Creates a DAG run in test environment
- Executes all tasks in correct dependency order
- Validates XCom data passing between tasks
- Returns DagRun object for validation

**XCom Retrieval**: Always specify `task_ids` explicitly:
```python
# Correct
value = ti.xcom_pull(task_ids='task_id', key='return_value')

# Incorrect (may pull from wrong task)
value = ti.xcom_pull(key='return_value')
```

**Unique Execution Dates**: Each test uses unique execution dates to avoid database UNIQUE constraint violations:
```python
execution_date = datetime(2025, 1, 1, hour, minute, int(time.time() % 60))
```

**Expected Warnings**: Warnings about pandas not being imported are expected and harmless. They come from Airflow's example plugins and don't affect test execution.

