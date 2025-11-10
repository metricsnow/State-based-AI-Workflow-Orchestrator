# TASK-005: Migrate DAGs to TaskFlow API

## Task Information
- **Task ID**: TASK-005
- **Created**: 2025-01-27
- **Status**: Waiting
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 4-6 hours
- **Actual Time**: TBD
- **Type**: Refactor
- **Dependencies**: TASK-003 ✅, TASK-004 ✅
- **Parent PRD**: `project/docs/prd_phase1.md` - Milestone 1.2

## Task Description
Migrate existing DAGs from traditional operators to modern TaskFlow API using `@dag` and `@task` decorators. This migration improves code maintainability, testability, and follows Airflow best practices.

## Problem Statement
Traditional operator-based DAGs are harder to test, maintain, and don't leverage Airflow's modern TaskFlow API which provides automatic XCom management, type hints, and Python-native syntax.

## Requirements

### Functional Requirements
- [ ] All DAGs use `@dag` decorator
- [ ] All tasks use `@task` decorator
- [ ] Tasks pass data via function arguments (automatic XCom)
- [ ] Type hints used for data structures
- [ ] DAGs execute successfully with TaskFlow API
- [ ] Backward compatibility maintained (same functionality)

### Technical Requirements
- [ ] Migrate from PythonOperator to `@task` decorator
- [ ] Migrate from DAG context manager to `@dag` decorator
- [ ] Implement automatic XCom data passing
- [ ] Add type hints to task functions
- [ ] Update task dependencies (automatic via function calls)
- [ ] Follow TaskFlow API best practices

## Implementation Plan

### Phase 1: Analysis
- [ ] Review TaskFlow API documentation
- [ ] Analyze existing DAG structure
- [ ] Plan migration strategy
- [ ] Identify XCom usage patterns

### Phase 2: Planning
- [ ] Design TaskFlow DAG structure
- [ ] Plan data flow with function arguments
- [ ] Design type hints
- [ ] Plan testing approach

### Phase 3: Implementation
- [ ] Migrate DAG definition to `@dag` decorator
- [ ] Migrate tasks to `@task` decorator
- [ ] Update data passing to function arguments
- [ ] Add type hints
- [ ] Update task dependencies
- [ ] Remove manual XCom calls
- [ ] Update imports

### Phase 4: Testing
- [ ] Verify DAG imports without errors
- [ ] Test DAG execution
- [ ] Verify data passing between tasks
- [ ] Run existing unit tests
- [ ] Compare output with original DAG

### Phase 5: Documentation
- [ ] Document TaskFlow API patterns used
- [ ] Document migration changes
- [ ] Update code comments

## Technical Implementation

### TaskFlow API Migration Example

**Before (Traditional Operators)**:
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

def extract_data(**context):
    return {'data': [1, 2, 3, 4, 5]}

def transform_data(**context):
    ti = context['ti']
    data = ti.xcom_pull(task_ids='extract')
    return {'transformed': [x * 2 for x in data['data']]}

with DAG(...) as dag:
    extract = PythonOperator(task_id='extract', python_callable=extract_data)
    transform = PythonOperator(task_id='transform', python_callable=transform_data)
    extract >> transform
```

**After (TaskFlow API)**:
```python
from airflow.decorators import dag, task
from datetime import datetime
from typing import Dict, List

@dag(
    dag_id="example_taskflow",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
)
def example_taskflow():
    @task
    def extract() -> Dict[str, List[int]]:
        """Extract data from source."""
        return {"data": [1, 2, 3, 4, 5]}
    
    @task
    def transform(data: Dict[str, List[int]]) -> Dict[str, List[int]]:
        """Transform extracted data."""
        return {"transformed": [x * 2 for x in data["data"]]}
    
    # Automatic dependency management
    extracted = extract()
    transformed = transform(extracted)

example_taskflow()
```

### Key Changes
1. Replace `DAG()` context manager with `@dag` decorator
2. Replace `PythonOperator` with `@task` decorator
3. Remove `**context` parameter, use function arguments
4. Remove manual `xcom_pull` calls
5. Add type hints for data structures
6. Automatic dependencies via function calls

## Testing

### Manual Testing
- [ ] Verify DAG appears in Airflow UI
- [ ] Trigger DAG execution
- [ ] Verify all tasks complete successfully
- [ ] Verify data passing between tasks
- [ ] Check task logs

### Automated Testing
- [ ] Run existing DAG structure tests
- [ ] Run task function unit tests
- [ ] Add TaskFlow-specific tests
- [ ] Verify type hints work correctly

## Acceptance Criteria
- [ ] All DAGs migrated to TaskFlow API
- [ ] All tasks use `@task` decorator
- [ ] All DAGs use `@dag` decorator
- [ ] Type hints added to all task functions
- [ ] Data passing via function arguments (no manual XCom)
- [ ] DAGs execute successfully
- [ ] All existing tests pass
- [ ] Code follows TaskFlow API best practices
- [ ] Documentation updated

## Dependencies
- **External**: Apache Airflow 2.8.4+ (TaskFlow API support)
- **Internal**: TASK-003 (Basic DAG), TASK-004 (Testing framework)

## Risks and Mitigation

### Risk 1: XCom Size Limitations
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Keep data small, document limitations, use external storage for large data

### Risk 2: Learning Curve
- **Probability**: Medium
- **Impact**: Low
- **Mitigation**: Reference official TaskFlow documentation, start with simple examples

### Risk 3: Type Hint Complexity
- **Probability**: Low
- **Impact**: Low
- **Mitigation**: Use simple types initially, add complexity gradually

## Task Status
- [ ] Analysis Complete
- [ ] Planning Complete
- [ ] Implementation Complete
- [ ] Testing Complete
- [ ] Documentation Complete
- [ ] Quality Validation Complete

## Notes
- TaskFlow API is the recommended approach for new DAGs
- Automatic XCom management simplifies code
- Type hints improve code quality and IDE support
- Reference: `/apache/airflow` MCP Context7 documentation

