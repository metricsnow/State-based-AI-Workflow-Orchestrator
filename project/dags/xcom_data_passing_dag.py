"""
XCom Data Passing DAG using TaskFlow API.

This DAG demonstrates comprehensive data passing patterns with TaskFlow API:
- Simple value passing (int, str, float)
- Dictionary data passing
- List data passing
- Multiple outputs (multiple_outputs=True)
- Data validation
- Error handling for invalid data

DAG Structure:
- simple_value_demo: Demonstrates simple value passing (int)
- dict_demo: Demonstrates dictionary passing
- list_demo: Demonstrates list passing
- multiple_outputs_demo: Demonstrates multiple_outputs pattern
- validation_demo: Demonstrates data validation
- error_handling_demo: Demonstrates error handling

Implementation Notes:
- TaskFlow API automatically handles XCom serialization/deserialization
- Type hints enable data validation and IDE support
- Multiple outputs allow returning dictionaries that are unpacked
- Error handling prevents invalid data from propagating
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Any

from airflow.decorators import dag, task


@dag(
    dag_id='xcom_data_passing_dag',
    description='Comprehensive XCom data passing patterns with TaskFlow API',
    schedule=timedelta(days=1),
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['xcom', 'data-passing', 'taskflow', 'example'],
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
)
def xcom_data_passing_dag():
    """
    Comprehensive XCom data passing demonstration DAG.
    
    This DAG demonstrates all data passing patterns required by TASK-006:
    1. Simple value passing
    2. Dictionary passing
    3. List passing
    4. Multiple outputs
    5. Data validation
    6. Error handling
    """
    
    # ============================================================================
    # Pattern 1: Simple Value Passing
    # ============================================================================
    
    @task
    def extract_simple_value() -> int:
        """
        Extract a simple integer value.
        
        Returns:
            Simple integer value
        """
        print("Extracting simple value: 42")
        return 42
    
    @task
    def process_simple_value(value: int) -> int:
        """
        Process a simple integer value.
        
        Args:
            value: Integer value from extract_simple_value task
            
        Returns:
            Processed integer value (multiplied by 2)
        """
        print(f"Received simple value: {value}")
        result = value * 2
        print(f"Processed value: {result}")
        return result
    
    @task
    def consume_simple_value(value: int) -> None:
        """
        Consume a simple integer value.
        
        Args:
            value: Integer value from process_simple_value task
        """
        print(f"Consuming simple value: {value}")
        assert value == 84, f"Expected 84, got {value}"
    
    # ============================================================================
    # Pattern 2: Dictionary Data Passing
    # ============================================================================
    
    @task
    def extract_dict() -> Dict[str, List[int]]:
        """
        Extract data as a dictionary.
        
        Returns:
            Dictionary containing list of integers
        """
        print("Extracting dictionary data...")
        data = {"data": [1, 2, 3, 4, 5]}
        print(f"Extracted dictionary: {data}")
        return data
    
    @task
    def transform_dict(data: Dict[str, List[int]]) -> Dict[str, List[int]]:
        """
        Transform dictionary data.
        
        Args:
            data: Dictionary containing list of integers
            
        Returns:
            Transformed dictionary with multiplied values
        """
        print(f"Received dictionary: {data}")
        transformed = {"transformed": [x * 2 for x in data["data"]]}
        print(f"Transformed dictionary: {transformed}")
        return transformed
    
    @task
    def consume_dict(data: Dict[str, List[int]]) -> None:
        """
        Consume dictionary data.
        
        Args:
            data: Transformed dictionary from transform_dict task
        """
        print(f"Consuming dictionary: {data}")
        assert "transformed" in data
        assert data["transformed"] == [2, 4, 6, 8, 10]
    
    # ============================================================================
    # Pattern 3: List Data Passing
    # ============================================================================
    
    @task
    def extract_list() -> List[int]:
        """
        Extract data as a list.
        
        Returns:
            List of integers
        """
        print("Extracting list data...")
        data = [10, 20, 30, 40, 50]
        print(f"Extracted list: {data}")
        return data
    
    @task
    def transform_list(data: List[int]) -> List[int]:
        """
        Transform list data.
        
        Args:
            data: List of integers from extract_list task
            
        Returns:
            Transformed list (values squared)
        """
        print(f"Received list: {data}")
        transformed = [x * x for x in data]
        print(f"Transformed list: {transformed}")
        return transformed
    
    @task
    def consume_list(data: List[int]) -> None:
        """
        Consume list data.
        
        Args:
            data: Transformed list from transform_list task
        """
        print(f"Consuming list: {data}")
        assert data == [100, 400, 900, 1600, 2500]
    
    # ============================================================================
    # Pattern 4: Multiple Outputs (multiple_outputs=True)
    # ============================================================================
    
    @task(multiple_outputs=True)
    def extract_multiple() -> Dict[str, Any]:
        """
        Extract multiple values using multiple_outputs.
        
        Returns:
            Dictionary that will be unpacked into multiple XCom values
        """
        print("Extracting multiple values...")
        result = {
            "count": 100,
            "data": [1, 2, 3],
            "status": "success",
            "metadata": {"version": "1.0", "environment": "dev"}
        }
        print(f"Extracted multiple values: {result}")
        return result
    
    @task
    def process_multiple(
        count: int,
        data: List[int],
        status: str,
        metadata: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Process multiple values received from multiple_outputs.
        
        Args:
            count: Integer value from extract_multiple
            data: List value from extract_multiple
            status: String value from extract_multiple
            metadata: Dictionary value from extract_multiple
            
        Returns:
            Dictionary with processed results
        """
        print(f"Received multiple values:")
        print(f"  count: {count}")
        print(f"  data: {data}")
        print(f"  status: {status}")
        print(f"  metadata: {metadata}")
        
        result = {
            "processed": True,
            "total": count * len(data),
            "status": status,
            "version": metadata.get("version", "unknown")
        }
        print(f"Processed result: {result}")
        return result
    
    @task
    def consume_multiple(result: Dict[str, Any]) -> None:
        """
        Consume processed multiple values.
        
        Args:
            result: Processed result from process_multiple task
        """
        print(f"Consuming multiple values result: {result}")
        assert result["processed"] is True
        assert result["total"] == 300  # 100 * 3
    
    # ============================================================================
    # Pattern 5: Data Validation
    # ============================================================================
    
    @task
    def extract_for_validation() -> Dict[str, Any]:
        """
        Extract data that will be validated.
        
        Returns:
            Dictionary with data to validate
        """
        print("Extracting data for validation...")
        return {
            "data": [1, 2, 3, 4, 5],
            "count": 5,
            "valid": True
        }
    
    @task
    def validate_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data structure and content.
        
        Args:
            data: Dictionary to validate
            
        Returns:
            Validated dictionary
            
        Raises:
            ValueError: If data is invalid
        """
        print(f"Validating data: {data}")
        
        # Validation checks
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        if "data" not in data:
            raise ValueError("Data must contain 'data' key")
        
        if not isinstance(data["data"], list):
            raise ValueError("Data['data'] must be a list")
        
        if len(data["data"]) == 0:
            raise ValueError("Data['data'] must not be empty")
        
        if "count" not in data:
            raise ValueError("Data must contain 'count' key")
        
        if data["count"] != len(data["data"]):
            raise ValueError("Data count must match data length")
        
        print("Data validation passed")
        return data
    
    @task
    def consume_validated(data: Dict[str, Any]) -> None:
        """
        Consume validated data.
        
        Args:
            data: Validated dictionary from validate_data task
        """
        print(f"Consuming validated data: {data}")
        assert data["valid"] is True
        assert len(data["data"]) == data["count"]
    
    # ============================================================================
    # Pattern 6: Error Handling for Invalid Data
    # ============================================================================
    
    @task
    def extract_invalid_data() -> Dict[str, Any]:
        """
        Extract data that will trigger validation error.
        
        Returns:
            Dictionary with invalid structure
        """
        print("Extracting invalid data (for error handling demo)...")
        # Intentionally return invalid data structure
        return {
            "invalid": "data",
            # Missing required "data" key
        }
    
    @task
    def handle_invalid_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle invalid data with error handling.
        
        Args:
            data: Potentially invalid dictionary
            
        Returns:
            Dictionary with error information or processed data
            
        Note:
            This task demonstrates error handling patterns.
            In production, you might want to fail the task or use
            a different error handling strategy.
        """
        print(f"Handling data (may be invalid): {data}")
        
        try:
            # Attempt validation
            if "data" not in data:
                error_msg = "Missing required 'data' key"
                print(f"Validation error: {error_msg}")
                return {
                    "error": True,
                    "message": error_msg,
                    "original_data": data
                }
            
            # If valid, process normally
            return {
                "error": False,
                "processed": True,
                "data": data
            }
            
        except Exception as e:
            print(f"Error handling data: {e}")
            return {
                "error": True,
                "message": str(e),
                "original_data": data
            }
    
    @task
    def consume_error_handling(result: Dict[str, Any]) -> None:
        """
        Consume result from error handling task.
        
        Args:
            result: Result from handle_invalid_data task
        """
        print(f"Consuming error handling result: {result}")
        # This task should receive error information, not fail
        assert "error" in result
        if result["error"]:
            print(f"Error was handled gracefully: {result['message']}")
    
    # ============================================================================
    # Task Dependencies and Data Flow
    # ============================================================================
    
    # Simple value passing chain
    simple_value = extract_simple_value()
    processed_value = process_simple_value(simple_value)
    consume_simple_value(processed_value)
    
    # Dictionary passing chain
    dict_data = extract_dict()
    transformed_dict = transform_dict(dict_data)
    consume_dict(transformed_dict)
    
    # List passing chain
    list_data = extract_list()
    transformed_list = transform_list(list_data)
    consume_list(transformed_list)
    
    # Multiple outputs chain
    multiple_data = extract_multiple()
    processed_multiple = process_multiple(
        count=multiple_data["count"],
        data=multiple_data["data"],
        status=multiple_data["status"],
        metadata=multiple_data["metadata"]
    )
    consume_multiple(processed_multiple)
    
    # Validation chain
    validation_data = extract_for_validation()
    validated = validate_data(validation_data)
    consume_validated(validated)
    
    # Error handling chain
    invalid_data = extract_invalid_data()
    error_result = handle_invalid_data(invalid_data)
    consume_error_handling(error_result)


# Invoke the DAG function to register it with Airflow
xcom_data_passing_dag()

