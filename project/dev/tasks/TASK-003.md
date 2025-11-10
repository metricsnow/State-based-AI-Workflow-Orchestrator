# TASK-003: Basic DAG Creation with Traditional Operators

## Task Information
- **Task ID**: TASK-003
- **Created**: 2025-01-27
- **Status**: Waiting
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 4-5 hours
- **Actual Time**: TBD
- **Type**: Feature
- **Dependencies**: TASK-002 ✅
- **Parent PRD**: `project/docs/prd_phase1.md` - Milestone 1.1

## Task Description
Create a basic Airflow DAG with 3-4 tasks using traditional operators (PythonOperator, BashOperator) demonstrating ETL pattern. This DAG validates Airflow functionality and serves as a foundation before migrating to TaskFlow API.

## Problem Statement
We need a working DAG to validate Airflow setup and demonstrate basic orchestration capabilities. This DAG will be migrated to TaskFlow API in a subsequent task.

## Requirements

### Functional Requirements
- [ ] At least one DAG with 3-4 tasks
- [ ] Tasks demonstrate ETL pattern (Extract, Transform, Load)
- [ ] Tasks have clear dependencies
- [ ] DAG visible in Airflow UI
- [ ] Tasks execute successfully
- [ ] Task logs accessible and readable
- [ ] DAG can be paused/unpaused via UI

### Technical Requirements
- [ ] DAG uses traditional operators (PythonOperator, BashOperator)
- [ ] Tasks pass data via XCom
- [ ] Proper task dependencies defined
- [ ] DAG follows Airflow best practices
- [ ] Error handling implemented
- [ ] Type hints where applicable
- [ ] Docstrings for all tasks

## Implementation Plan

### Phase 1: Analysis
- [ ] Review Airflow DAG best practices
- [ ] Design ETL workflow structure
- [ ] Plan task dependencies
- [ ] Review XCom usage patterns

### Phase 2: Planning
- [ ] Design DAG structure
- [ ] Define task functions
- [ ] Plan data flow between tasks
- [ ] Design error handling

### Phase 3: Implementation
- [ ] Create DAG file (`dags/example_etl_dag.py`)
- [ ] Implement extract task
- [ ] Implement transform task
- [ ] Implement load task
- [ ] Define task dependencies
- [ ] Add error handling
- [ ] Add docstrings and type hints

### Phase 4: Testing
- [ ] Verify DAG appears in Airflow UI
- [ ] Trigger DAG execution
- [ ] Verify all tasks complete successfully
- [ ] Verify task dependencies respected
- [ ] Check task logs for errors
- [ ] Test DAG pause/unpause

### Phase 5: Documentation
- [ ] Document DAG structure
- [ ] Document task purposes
- [ ] Document data flow

## Technical Implementation

### DAG Structure
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from typing import Dict, List

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def extract_data(**context) -> Dict:
    """Extract data from source."""
    print("Extracting data...")
    data = [1, 2, 3, 4, 5]
    return {'data': data}

def transform_data(**context) -> Dict:
    """Transform extracted data."""
    ti = context['ti']
    extracted_data = ti.xcom_pull(task_ids='extract')
    print(f"Transforming data: {extracted_data}")
    
    transformed = [x * 2 for x in extracted_data['data']]
    return {'transformed_data': transformed}

def load_data(**context) -> None:
    """Load transformed data."""
    ti = context['ti']
    transformed_data = ti.xcom_pull(task_ids='transform')
    print(f"Loading data: {transformed_data}")

with DAG(
    'example_etl_dag',
    default_args=default_args,
    description='Example ETL DAG using traditional operators',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['example', 'etl'],
) as dag:
    
    extract = PythonOperator(
        task_id='extract',
        python_callable=extract_data,
    )
    
    transform = PythonOperator(
        task_id='transform',
        python_callable=transform_data,
    )
    
    load = PythonOperator(
        task_id='load',
        python_callable=load_data,
    )
    
    # Define dependencies
    extract >> transform >> load
```

## Testing

### Manual Testing
- [ ] Verify DAG appears in Airflow UI
- [ ] Trigger DAG execution manually
- [ ] Verify all tasks complete successfully
- [ ] Check task execution order
- [ ] Verify XCom data passing
- [ ] Test DAG pause/unpause functionality
- [ ] Review task logs

### Automated Testing
- [ ] DAG structure validation tests
- [ ] Task dependency validation
- [ ] XCom data passing tests
- [ ] DAG import tests

## Acceptance Criteria
- [ ] DAG visible in Airflow UI
- [ ] DAG contains 3-4 tasks with clear dependencies
- [ ] All tasks execute successfully when triggered
- [ ] Task dependencies respected (extract → transform → load)
- [ ] Task logs accessible and readable
- [ ] DAG can be paused/unpaused via UI
- [ ] XCom data passing working correctly
- [ ] No syntax or import errors
- [ ] Code follows PEP8 and includes docstrings

## Dependencies
- **External**: Apache Airflow 2.8.4+
- **Internal**: TASK-002 (Airflow configuration)

## Risks and Mitigation

### Risk 1: XCom Size Limitations
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Keep data small for example, document XCom size limits

### Risk 2: Task Execution Failures
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Implement proper error handling, add retry logic

### Risk 3: DAG Not Appearing in UI
- **Probability**: Low
- **Impact**: High
- **Mitigation**: Check DAG folder path, verify DAG syntax, check scheduler logs

## Task Status
- [ ] Analysis Complete
- [ ] Planning Complete
- [ ] Implementation Complete
- [ ] Testing Complete
- [ ] Documentation Complete
- [ ] Quality Validation Complete

## Notes
- This DAG will be migrated to TaskFlow API in TASK-005
- Keep example simple for validation purposes
- Follow Airflow best practices for DAG structure

