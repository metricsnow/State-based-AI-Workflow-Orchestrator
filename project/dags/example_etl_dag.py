"""
Example ETL DAG using traditional Airflow operators.

This DAG demonstrates a basic Extract, Transform, Load (ETL) pattern
using PythonOperator and BashOperator. It serves as a foundation
before migrating to TaskFlow API in TASK-005.

DAG Structure:
- extract: Extracts sample data
- transform: Transforms extracted data (multiplies by 2)
- validate: Validates transformed data (BashOperator)
- load: Loads transformed data

Data Flow:
- extract returns data via XCom
- transform pulls data from extract via XCom
- validate checks data format
- load processes final data
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Default arguments for all tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def extract_data(**context) -> Dict[str, List[int]]:
    """
    Extract data from source.
    
    This function simulates extracting data from a data source.
    In a real scenario, this would connect to a database, API, or file.
    
    Args:
        **context: Airflow task context (unused in this example)
    
    Returns:
        Dict containing extracted data list
    """
    print("Extracting data from source...")
    # Simulate extracted data
    data = [1, 2, 3, 4, 5]
    print(f"Extracted {len(data)} records: {data}")
    return {'data': data}


def transform_data(**context) -> Dict[str, List[int]]:
    """
    Transform extracted data.
    
    This function pulls data from the extract task via XCom,
    transforms it (multiplies each value by 2), and returns
    the transformed data.
    
    Args:
        **context: Airflow task context containing task_instance
    
    Returns:
        Dict containing transformed data list
    """
    # Access task instance from context
    ti = context['ti']
    
    # Pull data from extract task via XCom
    extracted_data = ti.xcom_pull(task_ids='extract')
    print(f"Received data from extract task: {extracted_data}")
    
    # Transform data (multiply by 2)
    original_data = extracted_data['data']
    transformed = [x * 2 for x in original_data]
    
    print(f"Transformed {len(transformed)} records: {transformed}")
    return {'transformed_data': transformed}


def load_data(**context) -> None:
    """
    Load transformed data.
    
    This function pulls transformed data from the transform task
    via XCom and simulates loading it to a destination.
    
    Args:
        **context: Airflow task context containing task_instance
    
    Returns:
        None
    """
    # Access task instance from context
    ti = context['ti']
    
    # Pull transformed data from transform task via XCom
    transformed_data = ti.xcom_pull(task_ids='transform')
    print(f"Received transformed data: {transformed_data}")
    
    # Simulate loading data
    data_to_load = transformed_data['transformed_data']
    print(f"Loading {len(data_to_load)} records to destination...")
    print(f"Data loaded successfully: {data_to_load}")
    
    # In a real scenario, this would write to database, file, or API
    return None


# Define the DAG
# Note: Airflow 3.0+ uses 'schedule' instead of 'schedule_interval'
with DAG(
    'example_etl_dag',
    default_args=default_args,
    description='Example ETL DAG using traditional operators',
    schedule=timedelta(days=1),  # Changed from schedule_interval for Airflow 3.0+
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['example', 'etl', 'traditional-operators'],
) as dag:
    
    # Extract task
    extract = PythonOperator(
        task_id='extract',
        python_callable=extract_data,
        doc_md="""
        #### Extract Task
        Extracts sample data from a simulated data source.
        Returns data via XCom for downstream tasks.
        """,
    )
    
    # Transform task
    transform = PythonOperator(
        task_id='transform',
        python_callable=transform_data,
        doc_md="""
        #### Transform Task
        Transforms extracted data by multiplying each value by 2.
        Pulls data from extract task via XCom.
        """,
    )
    
    # Validate task (using BashOperator)
    validate = BashOperator(
        task_id='validate',
        bash_command='echo "Validating transformed data..." && echo "Validation passed"',
        doc_md="""
        #### Validate Task
        Validates the transformed data format.
        Uses BashOperator to demonstrate bash command execution.
        """,
    )
    
    # Load task
    load = PythonOperator(
        task_id='load',
        python_callable=load_data,
        doc_md="""
        #### Load Task
        Loads transformed data to destination.
        Pulls data from transform task via XCom.
        """,
    )
    
    # Define task dependencies
    # extract -> transform -> validate -> load
    extract >> transform >> validate >> load

