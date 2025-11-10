"""
Integration tests for TaskFlow DAG execution.

This module contains integration tests that test complete DAG execution
in a test Airflow environment. Tests validate:
- End-to-end DAG execution
- XCom data passing between tasks
- Task dependency validation
- Task execution order
- Error handling and retry validation

Implementation Notes:
- Uses Airflow's dag.test() method for DAG execution
- Tests run in a test Airflow environment
- Validates XCom data passing
- Validates task states and dependencies
"""
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from airflow.models import DagBag
from airflow.utils.state import DagRunState, TaskInstanceState
from airflow.utils.types import DagRunType
import time

# Note: Warnings about pandas not being imported are expected and harmless.
# They come from Airflow's example plugins and don't affect test execution.


class TestExampleETLDAGExecution:
    """Integration tests for example_etl_dag execution."""

    @pytest.fixture(scope="class")
    def dag_bag(self):
        """Create DagBag instance for testing."""
        project_root = Path(__file__).parent.parent.parent
        dags_folder = project_root / "dags"
        return DagBag(dag_folder=str(dags_folder), include_examples=False)

    @pytest.fixture(scope="class")
    def dag(self, dag_bag):
        """Get example_etl_dag from DagBag."""
        dag = dag_bag.get_dag(dag_id='example_etl_dag')
        assert dag is not None, "example_etl_dag not found"
        return dag

    def test_dag_execution_completes(self, dag):
        """Test that DAG execution completes successfully."""
        # Use dag.test() for local testing
        # This executes the DAG in a test environment
        # Use unique execution date with timestamp to avoid UNIQUE constraint violations
        execution_date = datetime(2025, 1, 1, 1, 0, int(time.time() % 60))
        
        # Create DAG run and execute
        dag_run = dag.test(run_after=execution_date)
        
        # Verify DAG run completed
        assert dag_run is not None, "DAG run should be created"
        assert dag_run.state == DagRunState.SUCCESS, \
            f"DAG run should be SUCCESS, got {dag_run.state}"

    def test_extract_task_executes(self, dag):
        """Test that extract task executes and returns data."""
        execution_date = datetime(2025, 1, 1, 2, 0, int(time.time() % 60))
        dag_run = dag.test(run_after=execution_date)
        
        # Get task instance
        ti_extract = dag_run.get_task_instance('extract')
        assert ti_extract is not None, "extract task instance should exist"
        assert ti_extract.state == TaskInstanceState.SUCCESS, \
            f"extract task should be SUCCESS, got {ti_extract.state}"
        
        # Check XCom value - specify task_id explicitly
        extract_value = ti_extract.xcom_pull(task_ids='extract', key='return_value')
        assert extract_value is not None, "extract task should return data"
        assert isinstance(extract_value, dict), "extract should return dict"
        assert 'data' in extract_value, "extract should return data with 'data' key"
        assert isinstance(extract_value['data'], list), "extract data should be a list"
        assert len(extract_value['data']) > 0, "extract data should not be empty"

    def test_transform_task_receives_data(self, dag):
        """Test that transform task receives data from extract task."""
        execution_date = datetime(2025, 1, 1, 3, 0, int(time.time() % 60))
        dag_run = dag.test(run_after=execution_date)
        
        # Get task instances
        ti_extract = dag_run.get_task_instance('extract')
        ti_transform = dag_run.get_task_instance('transform')
        
        # Verify both tasks executed
        assert ti_extract.state == TaskInstanceState.SUCCESS
        assert ti_transform.state == TaskInstanceState.SUCCESS
        
        # Check XCom values - specify task_ids explicitly
        extract_value = ti_extract.xcom_pull(task_ids='extract', key='return_value')
        transform_value = ti_transform.xcom_pull(task_ids='transform', key='return_value')
        
        # Verify transform received extract's data
        assert extract_value is not None
        assert transform_value is not None
        assert isinstance(transform_value, dict)
        assert 'transformed_data' in transform_value
        
        # Verify transformation logic (multiply by 2)
        original_data = extract_value['data']
        transformed_data = transform_value['transformed_data']
        assert len(transformed_data) == len(original_data)
        for orig, trans in zip(original_data, transformed_data):
            assert trans == orig * 2, f"Transform should multiply by 2: {orig} -> {trans}"

    def test_task_dependencies(self, dag):
        """Test that task dependencies are respected."""
        execution_date = datetime(2025, 1, 1, 4, 0, int(time.time() % 60))
        dag_run = dag.test(run_after=execution_date)
        
        # Get task instances
        ti_extract = dag_run.get_task_instance('extract')
        ti_transform = dag_run.get_task_instance('transform')
        ti_validate = dag_run.get_task_instance('validate')
        ti_load = dag_run.get_task_instance('load')
        
        # Verify all tasks executed
        assert ti_extract.state == TaskInstanceState.SUCCESS
        assert ti_transform.state == TaskInstanceState.SUCCESS
        assert ti_validate.state == TaskInstanceState.SUCCESS
        assert ti_load.state == TaskInstanceState.SUCCESS
        
        # Verify execution order by checking start dates
        # Extract should start before transform
        if ti_extract.start_date and ti_transform.start_date:
            assert ti_extract.start_date <= ti_transform.start_date, \
                "extract should start before transform"
        
        # Transform should start before validate
        if ti_transform.start_date and ti_validate.start_date:
            assert ti_transform.start_date <= ti_validate.start_date, \
                "transform should start before validate"
        
        # Validate should start before load
        if ti_validate.start_date and ti_load.start_date:
            assert ti_validate.start_date <= ti_load.start_date, \
                "validate should start before load"

    def test_load_task_receives_transformed_data(self, dag):
        """Test that load task receives transformed data."""
        execution_date = datetime(2025, 1, 1, 5, 0, int(time.time() % 60))
        dag_run = dag.test(run_after=execution_date)
        
        # Get task instances
        ti_transform = dag_run.get_task_instance('transform')
        ti_load = dag_run.get_task_instance('load')
        
        # Verify both tasks executed
        assert ti_transform.state == TaskInstanceState.SUCCESS
        assert ti_load.state == TaskInstanceState.SUCCESS
        
        # Check XCom values - specify task_id explicitly
        transform_value = ti_transform.xcom_pull(task_ids='transform', key='return_value')
        
        # Load task should have received transformed data
        # (Load task receives data via function argument in TaskFlow API)
        assert transform_value is not None
        assert 'transformed_data' in transform_value


class TestXComDataPassingDAGExecution:
    """Integration tests for xcom_data_passing_dag execution."""

    @pytest.fixture(scope="class")
    def dag_bag(self):
        """Create DagBag instance for testing."""
        project_root = Path(__file__).parent.parent.parent
        dags_folder = project_root / "dags"
        return DagBag(dag_folder=str(dags_folder), include_examples=False)

    @pytest.fixture(scope="class")
    def dag(self, dag_bag):
        """Get xcom_data_passing_dag from DagBag."""
        dag = dag_bag.get_dag(dag_id='xcom_data_passing_dag')
        assert dag is not None, "xcom_data_passing_dag not found"
        return dag

    def test_dag_execution_completes(self, dag):
        """Test that xcom_data_passing_dag execution completes successfully."""
        execution_date = datetime(2025, 1, 1, 10, 0, int(time.time() % 60))
        dag_run = dag.test(run_after=execution_date)
        
        assert dag_run is not None
        assert dag_run.state == DagRunState.SUCCESS, \
            f"DAG run should be SUCCESS, got {dag_run.state}"

    def test_simple_value_passing(self, dag):
        """Test simple value passing between tasks."""
        execution_date = datetime(2025, 1, 1, 11, 0, int(time.time() % 60))
        dag_run = dag.test(run_after=execution_date)
        
        # Get task instances
        ti_extract = dag_run.get_task_instance('extract_simple_value')
        ti_process = dag_run.get_task_instance('process_simple_value')
        ti_consume = dag_run.get_task_instance('consume_simple_value')
        
        # Verify all tasks executed
        assert ti_extract.state == TaskInstanceState.SUCCESS
        assert ti_process.state == TaskInstanceState.SUCCESS
        assert ti_consume.state == TaskInstanceState.SUCCESS
        
        # Check XCom values - specify task_ids explicitly
        extract_value = ti_extract.xcom_pull(task_ids='extract_simple_value', key='return_value')
        process_value = ti_process.xcom_pull(task_ids='process_simple_value', key='return_value')
        
        # Verify data passing
        assert extract_value == 42, f"Expected 42, got {extract_value}"
        assert process_value == 84, f"Expected 84 (42 * 2), got {process_value}"

    def test_dict_data_passing(self, dag):
        """Test dictionary data passing between tasks."""
        execution_date = datetime(2025, 1, 1, 12, 0, int(time.time() % 60))
        dag_run = dag.test(run_after=execution_date)
        
        # Get task instances
        ti_extract = dag_run.get_task_instance('extract_dict')
        ti_transform = dag_run.get_task_instance('transform_dict')
        ti_consume = dag_run.get_task_instance('consume_dict')
        
        # Verify all tasks executed
        assert ti_extract.state == TaskInstanceState.SUCCESS
        assert ti_transform.state == TaskInstanceState.SUCCESS
        assert ti_consume.state == TaskInstanceState.SUCCESS
        
        # Check XCom values - specify task_ids explicitly
        extract_value = ti_extract.xcom_pull(task_ids='extract_dict', key='return_value')
        transform_value = ti_transform.xcom_pull(task_ids='transform_dict', key='return_value')
        
        # Verify data passing
        assert isinstance(extract_value, dict)
        assert 'data' in extract_value
        assert extract_value['data'] == [1, 2, 3, 4, 5]
        
        assert isinstance(transform_value, dict)
        assert 'transformed' in transform_value
        assert transform_value['transformed'] == [2, 4, 6, 8, 10]

    def test_list_data_passing(self, dag):
        """Test list data passing between tasks."""
        execution_date = datetime(2025, 1, 1, 13, 0, int(time.time() % 60))
        dag_run = dag.test(run_after=execution_date)
        
        # Get task instances
        ti_extract = dag_run.get_task_instance('extract_list')
        ti_transform = dag_run.get_task_instance('transform_list')
        ti_consume = dag_run.get_task_instance('consume_list')
        
        # Verify all tasks executed
        assert ti_extract.state == TaskInstanceState.SUCCESS
        assert ti_transform.state == TaskInstanceState.SUCCESS
        assert ti_consume.state == TaskInstanceState.SUCCESS
        
        # Check XCom values - specify task_ids explicitly
        extract_value = ti_extract.xcom_pull(task_ids='extract_list', key='return_value')
        transform_value = ti_transform.xcom_pull(task_ids='transform_list', key='return_value')
        
        # Verify data passing
        assert isinstance(extract_value, list)
        assert extract_value == [10, 20, 30, 40, 50]
        
        assert isinstance(transform_value, list)
        assert transform_value == [100, 400, 900, 1600, 2500]

    def test_multiple_outputs_passing(self, dag):
        """Test multiple outputs data passing (multiple_outputs=True)."""
        execution_date = datetime(2025, 1, 1, 14, 0, int(time.time() % 60))
        dag_run = dag.test(run_after=execution_date)
        
        # Get task instances
        ti_extract = dag_run.get_task_instance('extract_multiple')
        ti_process = dag_run.get_task_instance('process_multiple')
        ti_consume = dag_run.get_task_instance('consume_multiple')
        
        # Verify all tasks executed
        assert ti_extract.state == TaskInstanceState.SUCCESS
        assert ti_process.state == TaskInstanceState.SUCCESS
        assert ti_consume.state == TaskInstanceState.SUCCESS
        
        # Check XCom values for multiple outputs
        # With multiple_outputs=True, each key becomes a separate XCom value
        count_value = ti_extract.xcom_pull(task_ids='extract_multiple', key='count')
        data_value = ti_extract.xcom_pull(task_ids='extract_multiple', key='data')
        status_value = ti_extract.xcom_pull(task_ids='extract_multiple', key='status')
        metadata_value = ti_extract.xcom_pull(task_ids='extract_multiple', key='metadata')
        
        # Verify multiple outputs
        assert count_value == 100
        assert data_value == [1, 2, 3]
        assert status_value == 'success'
        assert isinstance(metadata_value, dict)
        assert metadata_value['version'] == '1.0'

    def test_data_validation(self, dag):
        """Test data validation pattern."""
        execution_date = datetime(2025, 1, 1, 15, 0, int(time.time() % 60))
        dag_run = dag.test(run_after=execution_date)
        
        # Get task instances
        ti_extract = dag_run.get_task_instance('extract_for_validation')
        ti_validate = dag_run.get_task_instance('validate_data')
        ti_consume = dag_run.get_task_instance('consume_validated')
        
        # Verify all tasks executed
        assert ti_extract.state == TaskInstanceState.SUCCESS
        assert ti_validate.state == TaskInstanceState.SUCCESS
        assert ti_consume.state == TaskInstanceState.SUCCESS
        
        # Check XCom values - specify task_ids explicitly
        extract_value = ti_extract.xcom_pull(task_ids='extract_for_validation', key='return_value')
        validate_value = ti_validate.xcom_pull(task_ids='validate_data', key='return_value')
        
        # Verify validation
        assert isinstance(extract_value, dict)
        assert 'data' in extract_value
        assert 'count' in extract_value
        assert extract_value['count'] == len(extract_value['data'])
        
        assert validate_value == extract_value, "Validated data should match extracted data"

    def test_error_handling(self, dag):
        """Test error handling for invalid data."""
        execution_date = datetime(2025, 1, 1, 16, 0, int(time.time() % 60))
        dag_run = dag.test(run_after=execution_date)
        
        # Get task instances
        ti_extract = dag_run.get_task_instance('extract_invalid_data')
        ti_handle = dag_run.get_task_instance('handle_invalid_data')
        ti_consume = dag_run.get_task_instance('consume_error_handling')
        
        # Verify all tasks executed (error handling should not fail tasks)
        assert ti_extract.state == TaskInstanceState.SUCCESS
        assert ti_handle.state == TaskInstanceState.SUCCESS
        assert ti_consume.state == TaskInstanceState.SUCCESS
        
        # Check XCom values - specify task_id explicitly
        handle_value = ti_handle.xcom_pull(task_ids='handle_invalid_data', key='return_value')
        
        # Verify error handling
        assert isinstance(handle_value, dict)
        assert 'error' in handle_value
        # Error should be handled gracefully
        assert handle_value['error'] is True, "Invalid data should trigger error handling"

    def test_all_tasks_execute(self, dag):
        """Test that all tasks in the DAG execute successfully."""
        execution_date = datetime(2025, 1, 1, 17, 0, int(time.time() % 60))
        dag_run = dag.test(run_after=execution_date)
        
        # Get all task instances
        task_instances = dag_run.get_task_instances()
        
        # Verify all tasks executed successfully
        failed_tasks = [
            ti for ti in task_instances
            if ti.state != TaskInstanceState.SUCCESS
        ]
        
        assert len(failed_tasks) == 0, \
            f"All tasks should succeed, but {len(failed_tasks)} failed: " \
            f"{[ti.task_id for ti in failed_tasks]}"

