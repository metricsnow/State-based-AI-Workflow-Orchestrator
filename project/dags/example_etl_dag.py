"""
Example ETL DAG using TaskFlow API.

This DAG demonstrates a basic Extract, Transform, Load (ETL) pattern
using TaskFlow API with @dag and @task decorators. Migrated from
traditional operators in TASK-005.

DAG Structure:
- extract: Extracts sample data
- transform: Transforms extracted data (multiplies by 2)
- validate: Validates transformed data (BashOperator via @task.bash)
- load: Loads transformed data

Data Flow:
- extract returns data automatically via XCom
- transform receives data via function argument (automatic XCom)
- validate checks data format
- load receives data via function argument (automatic XCom)

TaskFlow API Benefits:
- Automatic XCom management
- Type hints for better IDE support
- Python-native syntax
- Automatic dependency management via function calls
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

from airflow.decorators import dag, task


@dag(
    dag_id='example_etl_dag',
    description='Example ETL DAG using TaskFlow API',
    schedule=timedelta(days=1),
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['example', 'etl', 'taskflow'],
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
)
def example_etl_dag():
    """
    Example ETL DAG using TaskFlow API.
    
    This DAG demonstrates the TaskFlow API pattern with automatic
    XCom management and type hints.
    """
    
    @task
    def extract() -> Dict[str, List[int]]:
        """
        Extract data from source.
        
        This function simulates extracting data from a data source.
        In a real scenario, this would connect to a database, API, or file.
        
        Returns:
            Dict containing extracted data list
        """
        print("Extracting data from source...")
        # Simulate extracted data
        data = [1, 2, 3, 4, 5]
        print(f"Extracted {len(data)} records: {data}")
        return {'data': data}
    
    @task
    def transform(data: Dict[str, List[int]]) -> Dict[str, List[int]]:
        """
        Transform extracted data.
        
        This function receives data from the extract task automatically
        via TaskFlow API (no manual XCom needed). It transforms the data
        by multiplying each value by 2.
        
        Args:
            data: Dictionary containing extracted data from extract task
        
        Returns:
            Dict containing transformed data list
        """
        print(f"Received data from extract task: {data}")
        
        # Transform data (multiply by 2)
        original_data = data['data']
        transformed = [x * 2 for x in original_data]
        
        print(f"Transformed {len(transformed)} records: {transformed}")
        return {'transformed_data': transformed}
    
    @task.bash
    def validate() -> str:
        """
        Validate transformed data.
        
        This task validates the transformed data format using a bash command.
        Uses @task.bash decorator for bash command execution.
        
        Returns:
            Bash command string to execute
        """
        return 'echo "Validating transformed data..." && echo "Validation passed"'
    
    @task
    def load(transformed_data: Dict[str, List[int]]) -> None:
        """
        Load transformed data.
        
        This function receives transformed data from the transform task
        automatically via TaskFlow API and simulates loading it to a destination.
        
        Args:
            transformed_data: Dictionary containing transformed data from transform task
        
        Returns:
            None
        """
        print(f"Received transformed data: {transformed_data}")
        
        # Simulate loading data
        data_to_load = transformed_data['transformed_data']
        print(f"Loading {len(data_to_load)} records to destination...")
        print(f"Data loaded successfully: {data_to_load}")
        
        # In a real scenario, this would write to database, file, or API
        return None
    
    # Automatic dependency management via function calls
    # TaskFlow API automatically handles XCom and dependencies
    extracted = extract()
    transformed = transform(extracted)
    validated = validate()
    loaded = load(transformed)
    
    # Set explicit dependencies for validate and load
    # validate runs after transform (but doesn't need transform's data)
    # load runs after validate
    transformed >> validated >> loaded


# Invoke the DAG function to register it with Airflow
example_etl_dag()

