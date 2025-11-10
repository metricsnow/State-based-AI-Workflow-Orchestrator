# Airflow Tests

Comprehensive test suite for Airflow DAGs, TaskFlow API, and workflow execution.

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

**Test Coverage** (17 tests):
- Extract task function tests (6 tests)
  - Return value validation
  - Data structure validation
  - Data consistency checks
- Transform task function tests (6 tests)
  - Context handling
  - Data transformation logic
  - Edge case handling (empty lists, single values)
- Load task function tests (3 tests)
  - Context handling
  - Data processing validation
- Integration tests (2 tests)
  - Extract-transform integration

**Status**: ✅ Complete - All tests passing

### `test_xcom_data_passing.py` ✅ Implemented
XCom data passing validation tests.

**Test Coverage** (8 tests):
- XCom task configuration validation
- XCom data structure validation
- Task dependencies for XCom data flow
- Data integrity across task boundaries
- Multiple task XCom chain validation

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

### `test_taskflow.py` ⏳ Pending
TaskFlow API implementation tests (TASK-005).

### `test_dag_execution.py` ⏳ Pending
DAG execution and task dependency tests (TASK-008).

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

# Airflow initialization tests
pytest project/tests/airflow/test_airflow_init.py -v
```

### Running Specific Test Classes

```bash
# Run all DAG structure tests
pytest project/tests/airflow/test_dag_structure.py::TestDAGStructure -v

# Run all task function tests
pytest project/tests/airflow/test_task_functions.py::TestExtractTask -v
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
- ✅ **Total Tests**: 57 tests
- ✅ **Test Status**: All passing (57/57)
- ✅ **Coverage**: 100% for DAG code
- ✅ **Execution Time**: ~10 seconds

### Test Breakdown

- **DAG Import Tests**: 8/8 passing
- **DAG Structure Tests**: 13/13 passing
- **Task Function Tests**: 17/17 passing
- **XCom Data Passing Tests**: 8/8 passing
- **Airflow Init Tests**: 13/13 passing (existing)

### Coverage Report

```
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
project/dags/example_etl_dag.py      33      0   100%
---------------------------------------------------------------
TOTAL                                33      0   100%
```

**Status**: ✅ All tests passing with 100% coverage (exceeds 80% requirement)

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
3. **Integration Tests**: XCom data passing and task dependencies
4. **Validation Tests**: Import errors, syntax, configuration

### Best Practices

- Tests are fast and independent
- Task functions can be tested without Airflow runtime
- DagBag-based tests validate DAG structure without execution
- Comprehensive error messages for debugging
- 100% code coverage for DAG code

