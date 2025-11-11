"""
Example ETL DAG using TaskFlow API with Kafka Integration.

This DAG demonstrates a basic Extract, Transform, Load (ETL) pattern
using TaskFlow API with @dag and @task decorators. Migrated from
traditional operators in TASK-005. Enhanced with Kafka event publishing
in TASK-013.

DAG Structure:
- extract: Extracts sample data
- transform: Transforms extracted data (multiplies by 2)
- validate: Validates transformed data (BashOperator via @task.bash)
- load: Loads transformed data
- publish_completion: Publishes workflow completion event to Kafka

Data Flow:
- extract returns data automatically via XCom
- transform receives data via function argument (automatic XCom)
- validate checks data format
- load receives data via function argument (automatic XCom)
- publish_completion publishes event to Kafka

TaskFlow API Benefits:
- Automatic XCom management
- Type hints for better IDE support
- Python-native syntax
- Automatic dependency management via function calls

Kafka Integration:
- Workflow events published to Kafka topic 'workflow-events'
- Events published on task completion and DAG completion
- Error handling ensures tasks don't fail if Kafka publishing fails
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Any

from airflow.decorators import dag, task
from workflow_events import EventType
from airflow_integration import publish_event_from_taskflow_context


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
    def load(transformed_data: Dict[str, List[int]]) -> Dict[str, Any]:
        """
        Load transformed data.
        
        This function receives transformed data from the transform task
        automatically via TaskFlow API and simulates loading it to a destination.
        
        Args:
            transformed_data: Dictionary containing transformed data from transform task
        
        Returns:
            Dictionary with load results
        """
        print(f"Received transformed data: {transformed_data}")
        
        # Simulate loading data
        data_to_load = transformed_data['transformed_data']
        print(f"Loading {len(data_to_load)} records to destination...")
        print(f"Data loaded successfully: {data_to_load}")
        
        # In a real scenario, this would write to database, file, or API
        load_result = {
            "status": "success",
            "records_loaded": len(data_to_load),
            "data": data_to_load
        }
        return load_result
    
    @task
    def publish_completion(load_result: Dict[str, Any], **context) -> None:
        """
        Publish workflow completion event to Kafka.
        
        This task publishes a workflow completion event to Kafka after all
        ETL tasks have completed successfully. Demonstrates Kafka integration
        with Airflow TaskFlow API.
        
        Args:
            load_result: Result from load task
            **context: Airflow context variables (dag_run, ti, etc.)
        
        Returns:
            None
        """
        print("Publishing workflow completion event to Kafka...")
        
        # Publish completion event
        publish_event_from_taskflow_context(
            event_type=EventType.WORKFLOW_COMPLETED,
            payload={
                "status": "success",
                "etl_result": load_result,
                "message": "ETL workflow completed successfully"
            },
            **context
        )
        
        print("Workflow completion event published successfully")
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
    # publish_completion runs after load completes
    transformed >> validated >> loaded
    publish_completion(loaded)


# Invoke the DAG function to register it with Airflow
example_etl_dag()

