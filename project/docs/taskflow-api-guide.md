# TaskFlow API Guide

## Overview

This guide documents the TaskFlow API implementation for Airflow DAGs, completed in TASK-005.

**Status**: ✅ Complete - All DAGs migrated to TaskFlow API

## What is TaskFlow API?

TaskFlow API is Airflow's modern approach to defining DAGs using Python decorators (`@dag` and `@task`). It provides:

- **Automatic XCom Management**: Data passing between tasks is handled automatically
- **Type Hints**: Better IDE support and code quality
- **Python-Native Syntax**: Cleaner, more readable code
- **Automatic Dependencies**: Task dependencies managed via function calls
- **Better Testability**: Task functions are regular Python functions

## Migration Summary

### Before (Traditional Operators)

```python
from airflow import DAG
from airflow.operators.python import PythonOperator

def extract_data(**context):
    return {'data': [1, 2, 3, 4, 5]}

def transform_data(**context):
    ti = context['ti']
    data = ti.xcom_pull(task_ids='extract')
    return {'transformed': [x * 2 for x in data['data']]}

with DAG('example_etl_dag', ...) as dag:
    extract = PythonOperator(task_id='extract', python_callable=extract_data)
    transform = PythonOperator(task_id='transform', python_callable=transform_data)
    extract >> transform
```

### After (TaskFlow API)

```python
from airflow.decorators import dag, task
from typing import Dict, List

@dag(dag_id='example_etl_dag', ...)
def example_etl_dag():
    @task
    def extract() -> Dict[str, List[int]]:
        return {'data': [1, 2, 3, 4, 5]}
    
    @task
    def transform(data: Dict[str, List[int]]) -> Dict[str, List[int]]:
        return {'transformed': [x * 2 for x in data['data']]}
    
    extracted = extract()
    transformed = transform(extracted)

example_etl_dag()
```

## Key Changes

### 1. DAG Definition

**Before**: `with DAG(...) as dag:`
**After**: `@dag(...)` decorator on a function

### 2. Task Definition

**Before**: `PythonOperator(task_id='extract', python_callable=extract_data)`
**After**: `@task` decorator on a function

### 3. Data Passing

**Before**: Manual XCom pulls using `ti.xcom_pull(task_ids='extract')`
**After**: Automatic via function arguments `transform(extracted)`

### 4. Dependencies

**Before**: Explicit dependency operators `extract >> transform`
**After**: Automatic via function calls (dependencies inferred from function arguments)

### 5. Type Hints

**Before**: No type hints
**After**: Full type hints for better IDE support and validation

## TaskFlow API Features Used

### Basic Task Decorator

```python
@task
def my_task() -> str:
    return "Hello, World!"
```

### Task with Data Passing

```python
@task
def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    # Data automatically received from upstream task
    return {'processed': data}
```

### Bash Task

```python
@task.bash
def validate() -> str:
    return 'echo "Validation passed"'
```

### Multiple Outputs

```python
@task(multiple_outputs=True)
def extract_multiple() -> Dict[str, Any]:
    return {
        'count': 100,
        'data': [1, 2, 3],
        'status': 'success'
    }
```

## Benefits Achieved

1. **Code Quality**: Type hints improve IDE support and catch errors early
2. **Maintainability**: Cleaner, more Pythonic code
3. **Testability**: Task functions can be tested independently
4. **Automatic XCom**: No manual XCom management needed
5. **Better Documentation**: Function signatures document data flow

## Testing with TaskFlow API

### Unit Testing Task Functions

TaskFlow API makes testing easier because task functions are regular Python functions:

```python
from example_etl_dag import example_etl_dag

# Get DAG instance
dag = example_etl_dag()

# Extract task function
extract_task = dag.get_task('extract')
extract_function = extract_task.python_callable

# Test directly
result = extract_function()
assert result == {'data': [1, 2, 3, 4, 5]}
```

### Integration Testing

```python
from airflow.models import DagBag

dag_bag = DagBag(dag_folder='project/dags', include_examples=False)
dag = dag_bag.get_dag('example_etl_dag')

# Verify TaskFlow operators
from airflow.operators.python import PythonDecoratedOperator
assert isinstance(dag.get_task('extract'), PythonDecoratedOperator)
```

## Migration Checklist

- [x] DAG migrated to `@dag` decorator
- [x] All tasks migrated to `@task` decorator
- [x] BashOperator migrated to `@task.bash`
- [x] Type hints added to all task functions
- [x] Manual XCom calls removed
- [x] Dependencies updated (automatic via function calls)
- [x] Imports updated
- [x] Tests updated for TaskFlow API
- [x] Documentation updated

## Best Practices

1. **Always use type hints**: Improves code quality and IDE support
2. **Use function arguments for data passing**: Let TaskFlow handle XCom automatically
3. **Keep task functions pure**: Easier to test and reason about
4. **Document function signatures**: Type hints serve as documentation
5. **Use `@task.bash` for bash commands**: Cleaner than BashOperator

## References

- **Airflow TaskFlow API Documentation**: https://airflow.apache.org/docs/apache-airflow/stable/concepts/taskflow.html
- **MCP Context7**: `/apache/airflow` - Official Airflow documentation
- **Task File**: `project/dev/tasks/TASK-005.md` - Complete migration details

## XCom Data Passing Patterns (TASK-006)

**Status**: ✅ Complete - Comprehensive XCom data passing patterns implemented

### Overview

TaskFlow API automatically handles XCom serialization and deserialization, making data passing between tasks seamless. The `xcom_data_passing_dag` demonstrates all data passing patterns.

### Data Passing Patterns

#### 1. Simple Value Passing

Pass simple types (int, str, float) between tasks:

```python
@task
def extract_simple_value() -> int:
    return 42

@task
def process_simple_value(value: int) -> int:
    return value * 2

# Automatic data passing
simple_value = extract_simple_value()
processed = process_simple_value(simple_value)
```

#### 2. Dictionary Passing

Pass dictionary data structures:

```python
@task
def extract_dict() -> Dict[str, List[int]]:
    return {"data": [1, 2, 3, 4, 5]}

@task
def transform_dict(data: Dict[str, List[int]]) -> Dict[str, List[int]]:
    return {"transformed": [x * 2 for x in data["data"]]}

# Automatic data passing
dict_data = extract_dict()
transformed = transform_dict(dict_data)
```

#### 3. List Passing

Pass list data structures:

```python
@task
def extract_list() -> List[int]:
    return [10, 20, 30, 40, 50]

@task
def transform_list(data: List[int]) -> List[int]:
    return [x * x for x in data]

# Automatic data passing
list_data = extract_list()
transformed = transform_list(list_data)
```

#### 4. Multiple Outputs

Return multiple values using `multiple_outputs=True`:

```python
@task(multiple_outputs=True)
def extract_multiple() -> Dict[str, Any]:
    return {
        "count": 100,
        "data": [1, 2, 3],
        "status": "success",
        "metadata": {"version": "1.0"}
    }

@task
def process_multiple(
    count: int,
    data: List[int],
    status: str,
    metadata: Dict[str, str]
) -> Dict[str, Any]:
    return {"processed": True, "total": count * len(data)}

# Multiple outputs are unpacked automatically
multiple_data = extract_multiple()
processed = process_multiple(
    count=multiple_data["count"],
    data=multiple_data["data"],
    status=multiple_data["status"],
    metadata=multiple_data["metadata"]
)
```

#### 5. Data Validation

Validate data structure and content:

```python
@task
def validate_data(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")
    if "data" not in data:
        raise ValueError("Data must contain 'data' key")
    return data

# Validation with error handling
validated = validate_data(extracted_data)
```

#### 6. Error Handling

Handle invalid data gracefully:

```python
@task
def handle_invalid_data(data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if "data" not in data:
            return {"error": True, "message": "Missing required 'data' key"}
        return {"error": False, "processed": True, "data": data}
    except Exception as e:
        return {"error": True, "message": str(e)}
```

### XCom Limitations

- **Size Limit**: Default 48KB per XCom value
- **Best Practice**: Use external storage (S3, database) for large data
- **Recommendation**: Keep XCom for metadata and data pointers

### Testing XCom Data Passing

All data passing patterns are tested in `test_xcom_data_passing.py`:

```bash
pytest project/tests/airflow/test_xcom_data_passing.py -v
```

**Test Results**: ✅ 36/36 tests passing

### Example DAG

See `project/dags/xcom_data_passing_dag.py` for complete implementation of all patterns.

## Next Steps

- ✅ TASK-006: Implement Data Passing with XCom - **COMPLETE**
- ✅ TASK-007: Unit Tests for TaskFlow DAGs - **COMPLETE** (62 tests, 97% coverage)
- TASK-008: Integration Testing for TaskFlow DAGs

