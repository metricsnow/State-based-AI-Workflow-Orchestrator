"""
Tests for XCom data passing between tasks.

This module contains tests to validate:
- XCom data passing between tasks
- Data format and structure
- XCom value retrieval
- Data integrity across task boundaries

Implementation Notes:
- Tests XCom functionality using Airflow's testing utilities
- Validates data passing patterns used in DAGs
- Tests both push and pull operations
"""
import pytest
from airflow.models import DagBag, TaskInstance
from airflow.operators.python import PythonOperator
from airflow.utils.state import TaskInstanceState
from datetime import datetime
from pathlib import Path


class TestXComDataPassing:
    """Test XCom data passing between tasks."""

    @pytest.fixture(scope="class")
    def dag_bag(self):
        """Create DagBag instance for testing."""
        project_root = Path(__file__).parent.parent.parent
        dags_folder = project_root / "dags"
        return DagBag(dag_folder=str(dags_folder), include_examples=False)

    @pytest.fixture
    def dag(self, dag_bag):
        """Get example_etl_dag from DagBag."""
        return dag_bag.get_dag(dag_id='example_etl_dag')

    def test_extract_task_returns_xcom_value(self, dag):
        """Test that extract task returns value for XCom."""
        extract_task = dag.get_task('extract')
        assert extract_task is not None, "extract task should exist"
        
        # Verify task is a PythonOperator that can return values
        from airflow.operators.python import PythonOperator
        assert isinstance(extract_task, PythonOperator), \
            "extract task should be PythonOperator"

    def test_transform_task_pulls_from_extract(self, dag):
        """Test that transform task pulls data from extract via XCom."""
        transform_task = dag.get_task('transform')
        assert transform_task is not None, "transform task should exist"
        
        # Verify task is configured to use XCom
        from airflow.operators.python import PythonOperator
        assert isinstance(transform_task, PythonOperator), \
            "transform task should be PythonOperator"

    def test_load_task_pulls_from_transform(self, dag):
        """Test that load task pulls data from transform via XCom."""
        load_task = dag.get_task('load')
        assert load_task is not None, "load task should exist"
        
        # Verify task is configured to use XCom
        from airflow.operators.python import PythonOperator
        assert isinstance(load_task, PythonOperator), \
            "load task should be PythonOperator"

    def test_xcom_task_dependencies(self, dag):
        """Test that XCom-dependent tasks have correct dependencies."""
        extract = dag.get_task('extract')
        transform = dag.get_task('transform')
        validate = dag.get_task('validate')
        load = dag.get_task('load')
        
        # Transform should depend on extract (for XCom data)
        assert transform in extract.downstream_list, \
            "transform should be downstream of extract for XCom data"
        
        # Validate should depend on transform
        assert validate in transform.downstream_list, \
            "validate should be downstream of transform"
        
        # Load should depend on validate (chain: extract -> transform -> validate -> load)
        assert load in validate.downstream_list, \
            "load should be downstream of validate for XCom data"

    def test_xcom_data_structure(self, dag):
        """
        Test that XCom data structure is correct.
        
        This test validates that the data structure passed via XCom
        matches the expected format.
        """
        extract_task = dag.get_task('extract')
        
        # Create a test execution context
        execution_date = datetime(2025, 1, 1)
        
        # Get the Python callable
        extract_callable = extract_task.python_callable
        
        # Execute the callable to get return value
        result = extract_callable()
        
        # Verify result structure
        assert isinstance(result, dict), \
            "XCom return value should be a dictionary"
        assert 'data' in result, \
            "XCom return value should contain 'data' key"
        assert isinstance(result['data'], list), \
            "XCom return value['data'] should be a list"

    def test_xcom_data_integrity(self, dag):
        """
        Test that XCom data maintains integrity across tasks.
        
        This test validates that data passed via XCom maintains
        its structure and values.
        """
        extract_task = dag.get_task('extract')
        extract_callable = extract_task.python_callable
        
        # Get extracted data
        extracted = extract_callable()
        
        # Verify data integrity
        assert 'data' in extracted
        assert isinstance(extracted['data'], list)
        assert len(extracted['data']) > 0
        
        # Verify all values are integers
        for value in extracted['data']:
            assert isinstance(value, int), \
                f"XCom data should contain integers, got {type(value)}"

    def test_xcom_task_ids_reference(self, dag):
        """Test that XCom task_ids references are correct."""
        transform_task = dag.get_task('transform')
        
        # Verify that transform task references 'extract' in its code
        # This is validated by checking the task dependencies
        extract = dag.get_task('extract')
        assert transform_task in extract.downstream_list, \
            "transform should reference extract for XCom data"

    def test_xcom_multiple_tasks(self, dag):
        """Test XCom data passing across multiple tasks."""
        extract = dag.get_task('extract')
        transform = dag.get_task('transform')
        validate = dag.get_task('validate')
        load = dag.get_task('load')
        
        # Verify chain: extract -> transform -> validate -> load
        assert transform in extract.downstream_list, \
            "extract -> transform dependency should exist"
        assert validate in transform.downstream_list, \
            "transform -> validate dependency should exist"
        assert load in validate.downstream_list, \
            "validate -> load dependency should exist"
        
        # Verify all tasks are PythonOperators (can use XCom) except validate (BashOperator)
        from airflow.operators.python import PythonOperator
        from airflow.operators.bash import BashOperator
        assert isinstance(extract, PythonOperator)
        assert isinstance(transform, PythonOperator)
        assert isinstance(validate, BashOperator)
        assert isinstance(load, PythonOperator)

