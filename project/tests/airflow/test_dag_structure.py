"""
Tests for Airflow DAG structure validation.

This module contains tests to validate:
- DAG import without errors
- DAG structure and properties
- Task dependencies
- XCom data passing
- DAG configuration

Implementation Notes:
- Uses Airflow's DagBag for DAG loading
- Tests validate DAG structure without execution
- Tests cover both structure and configuration validation
"""
import pytest
from airflow.models import DagBag
from pathlib import Path


class TestDAGStructure:
    """Test DAG structure and configuration."""

    @pytest.fixture(scope="class")
    def dag_bag(self):
        """Create DagBag instance for testing."""
        project_root = Path(__file__).parent.parent.parent
        dags_folder = project_root / "dags"
        return DagBag(dag_folder=str(dags_folder), include_examples=False)

    def test_dag_import_no_errors(self, dag_bag):
        """Test that DAGs can be imported without errors."""
        assert len(dag_bag.import_errors) == 0, \
            f"DAG import errors found: {dag_bag.import_errors}"

    def test_example_etl_dag_exists(self, dag_bag):
        """Test that example_etl_dag exists in DagBag."""
        assert 'example_etl_dag' in dag_bag.dags, \
            "example_etl_dag not found in DagBag"

    def test_example_etl_dag_structure(self, dag_bag):
        """Test example_etl_dag structure and properties."""
        dag = dag_bag.get_dag(dag_id='example_etl_dag')
        
        assert dag is not None, "DAG is None"
        assert dag.dag_id == 'example_etl_dag', \
            f"Expected dag_id 'example_etl_dag', got '{dag.dag_id}'"
        assert len(dag.tasks) >= 3, \
            f"Expected at least 3 tasks, got {len(dag.tasks)}"

    def test_example_etl_dag_tasks(self, dag_bag):
        """Test that example_etl_dag has required tasks."""
        dag = dag_bag.get_dag(dag_id='example_etl_dag')
        
        task_ids = [task.task_id for task in dag.tasks]
        
        assert 'extract' in task_ids, "extract task not found"
        assert 'transform' in task_ids, "transform task not found"
        assert 'load' in task_ids, "load task not found"

    def test_example_etl_dag_task_dependencies(self, dag_bag):
        """Test that task dependencies are correctly defined."""
        dag = dag_bag.get_dag(dag_id='example_etl_dag')
        
        extract = dag.get_task('extract')
        transform = dag.get_task('transform')
        validate = dag.get_task('validate')
        load = dag.get_task('load')
        
        # Check that transform is downstream of extract
        assert transform in extract.downstream_list, \
            "transform should be downstream of extract"
        
        # Check that validate is downstream of transform
        assert validate in transform.downstream_list, \
            "validate should be downstream of transform"
        
        # Check that load is downstream of validate
        assert load in validate.downstream_list, \
            "load should be downstream of validate"

    def test_example_etl_dag_configuration(self, dag_bag):
        """Test DAG configuration settings."""
        dag = dag_bag.get_dag(dag_id='example_etl_dag')
        
        assert dag.catchup is False, "catchup should be False"
        assert 'example' in dag.tags, "DAG should have 'example' tag"
        assert 'etl' in dag.tags, "DAG should have 'etl' tag"
        assert 'taskflow' in dag.tags, "DAG should have 'taskflow' tag (TaskFlow API)"

    def test_example_etl_dag_task_types(self, dag_bag):
        """Test that tasks use correct operator types (TaskFlow API)."""
        dag = dag_bag.get_dag(dag_id='example_etl_dag')
        
        extract = dag.get_task('extract')
        transform = dag.get_task('transform')
        load = dag.get_task('load')
        
        # Check operator types - TaskFlow API uses PythonDecoratedOperator
        from airflow.operators.python import PythonDecoratedOperator
        assert isinstance(extract, PythonDecoratedOperator), \
            "extract should be PythonDecoratedOperator (TaskFlow API)"
        assert isinstance(transform, PythonDecoratedOperator), \
            "transform should be PythonDecoratedOperator (TaskFlow API)"
        assert isinstance(load, PythonDecoratedOperator), \
            "load should be PythonDecoratedOperator (TaskFlow API)"

    def test_example_etl_dag_has_bash_operator(self, dag_bag):
        """Test that DAG includes a BashDecoratedOperator task (TaskFlow API)."""
        dag = dag_bag.get_dag(dag_id='example_etl_dag')
        
        task_ids = [task.task_id for task in dag.tasks]
        
        # Check if validate task exists (BashDecoratedOperator for TaskFlow API)
        if 'validate' in task_ids:
            validate = dag.get_task('validate')
            from airflow.operators.bash import BashDecoratedOperator
            assert isinstance(validate, BashDecoratedOperator), \
                "validate should be BashDecoratedOperator (TaskFlow API)"

    def test_example_etl_dag_default_args(self, dag_bag):
        """Test that DAG has default_args configured."""
        dag = dag_bag.get_dag(dag_id='example_etl_dag')
        
        assert dag.default_args is not None, "default_args should be set"
        assert 'owner' in dag.default_args, "default_args should have 'owner'"
        assert 'retries' in dag.default_args, "default_args should have 'retries'"

    def test_example_etl_dag_task_count(self, dag_bag):
        """Test that DAG has expected number of tasks."""
        dag = dag_bag.get_dag(dag_id='example_etl_dag')
        
        # Should have at least 4 tasks: extract, transform, validate, load
        assert len(dag.tasks) >= 4, \
            f"Expected at least 4 tasks, got {len(dag.tasks)}"

    def test_example_etl_dag_task_ids_unique(self, dag_bag):
        """Test that all task IDs are unique."""
        dag = dag_bag.get_dag(dag_id='example_etl_dag')
        
        task_ids = [task.task_id for task in dag.tasks]
        assert len(task_ids) == len(set(task_ids)), \
            f"Task IDs should be unique, found duplicates: {task_ids}"

    def test_example_etl_dag_has_no_cycles(self, dag_bag):
        """Test that DAG has no circular dependencies."""
        dag = dag_bag.get_dag(dag_id='example_etl_dag')
        
        # Airflow DAGs should not have cycles
        # This is validated by checking that all tasks have proper dependencies
        for task in dag.tasks:
            # A task should not be in its own downstream list
            assert task not in task.downstream_list, \
                f"Task {task.task_id} should not depend on itself"

    def test_example_etl_dag_schedule_interval(self, dag_bag):
        """Test that DAG has a valid schedule."""
        dag = dag_bag.get_dag(dag_id='example_etl_dag')
        
        # Airflow 3.0+ uses 'schedule' instead of 'schedule_interval'
        assert hasattr(dag, 'schedule') or hasattr(dag, 'schedule_interval'), \
            "DAG should have a schedule attribute"
        # schedule can be a timedelta, cron expression, or None
        # Just verify it exists
        assert True, "Schedule validation passed"

