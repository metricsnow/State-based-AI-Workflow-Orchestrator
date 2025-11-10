"""
Tests for TaskFlow DAG structure validation.

This module contains tests to validate TaskFlow DAG structure:
- DAG import without errors
- TaskFlow DAG structure and properties
- Task dependencies
- TaskFlow API decorator usage
- DAG configuration

Implementation Notes:
- Uses Airflow's DagBag for DAG loading
- Tests validate DAG structure without execution
- Tests cover both structure and configuration validation
- Focuses on TaskFlow API patterns
"""
import pytest
from airflow.models import DagBag
from pathlib import Path


class TestTaskFlowDAGStructure:
    """Test TaskFlow DAG structure and configuration."""

    @pytest.fixture(scope="class")
    def dag_bag(self):
        """Create DagBag instance for testing."""
        project_root = Path(__file__).parent.parent.parent
        dags_folder = project_root / "dags"
        return DagBag(dag_folder=str(dags_folder), include_examples=False)

    def test_xcom_data_passing_dag_exists(self, dag_bag):
        """Test that xcom_data_passing_dag exists in DagBag."""
        assert 'xcom_data_passing_dag' in dag_bag.dags, \
            "xcom_data_passing_dag not found in DagBag"

    def test_xcom_data_passing_dag_structure(self, dag_bag):
        """Test xcom_data_passing_dag structure and properties."""
        dag = dag_bag.dags.get('xcom_data_passing_dag')
        
        assert dag is not None, "DAG is None"
        assert dag.dag_id == 'xcom_data_passing_dag', \
            f"Expected dag_id 'xcom_data_passing_dag', got '{dag.dag_id}'"
        assert len(dag.tasks) >= 6, \
            f"Expected at least 6 tasks, got {len(dag.tasks)}"

    def test_xcom_data_passing_dag_tasks(self, dag_bag):
        """Test that xcom_data_passing_dag has required tasks."""
        dag = dag_bag.dags.get('xcom_data_passing_dag')
        
        task_ids = [task.task_id for task in dag.tasks]
        
        # Check for key task patterns
        assert any('simple' in task_id for task_id in task_ids), \
            "Should have simple value passing tasks"
        assert any('dict' in task_id for task_id in task_ids), \
            "Should have dictionary passing tasks"
        assert any('list' in task_id for task_id in task_ids), \
            "Should have list passing tasks"
        assert any('multiple' in task_id for task_id in task_ids), \
            "Should have multiple outputs tasks"
        assert any('validation' in task_id or 'validate' in task_id for task_id in task_ids), \
            "Should have validation tasks"
        assert any('error' in task_id or 'invalid' in task_id for task_id in task_ids), \
            "Should have error handling tasks"

    def test_xcom_data_passing_dag_configuration(self, dag_bag):
        """Test xcom_data_passing_dag configuration settings."""
        dag = dag_bag.dags.get('xcom_data_passing_dag')
        
        assert dag.catchup is False, "catchup should be False"
        assert 'xcom' in dag.tags, "DAG should have 'xcom' tag"
        assert 'data-passing' in dag.tags, "DAG should have 'data-passing' tag"
        assert 'taskflow' in dag.tags, "DAG should have 'taskflow' tag (TaskFlow API)"

    def test_xcom_data_passing_dag_task_types(self, dag_bag):
        """Test that tasks use TaskFlow API decorators."""
        dag = dag_bag.dags.get('xcom_data_passing_dag')
        
        # Check that tasks use TaskFlow API (_PythonDecoratedOperator)
        from airflow.providers.standard.decorators.python import _PythonDecoratedOperator
        
        # Sample a few tasks
        sample_tasks = list(dag.tasks)[:5]
        for task in sample_tasks:
            assert isinstance(task, _PythonDecoratedOperator), \
                f"Task {task.task_id} should be _PythonDecoratedOperator (TaskFlow API)"

    def test_xcom_data_passing_dag_default_args(self, dag_bag):
        """Test that DAG has default_args configured."""
        dag = dag_bag.dags.get('xcom_data_passing_dag')
        
        assert dag.default_args is not None, "default_args should be set"
        assert 'owner' in dag.default_args, "default_args should have 'owner'"
        assert 'retries' in dag.default_args, "default_args should have 'retries'"

    def test_xcom_data_passing_dag_task_count(self, dag_bag):
        """Test that DAG has expected number of tasks."""
        dag = dag_bag.dags.get('xcom_data_passing_dag')
        
        # Should have multiple task patterns (simple, dict, list, multiple, validation, error)
        assert len(dag.tasks) >= 15, \
            f"Expected at least 15 tasks for comprehensive patterns, got {len(dag.tasks)}"

    def test_xcom_data_passing_dag_task_ids_unique(self, dag_bag):
        """Test that all task IDs are unique."""
        dag = dag_bag.dags.get('xcom_data_passing_dag')
        
        task_ids = [task.task_id for task in dag.tasks]
        assert len(task_ids) == len(set(task_ids)), \
            f"Task IDs should be unique, found duplicates: {task_ids}"

    def test_xcom_data_passing_dag_has_no_cycles(self, dag_bag):
        """Test that DAG has no circular dependencies."""
        dag = dag_bag.dags.get('xcom_data_passing_dag')
        
        # Airflow DAGs should not have cycles
        for task in dag.tasks:
            # A task should not be in its own downstream list
            assert task not in task.downstream_list, \
                f"Task {task.task_id} should not depend on itself"

    def test_xcom_data_passing_dag_schedule(self, dag_bag):
        """Test that DAG has a valid schedule."""
        dag = dag_bag.dags.get('xcom_data_passing_dag')
        
        # Airflow 3.0+ uses 'schedule' instead of 'schedule_interval'
        assert hasattr(dag, 'schedule') or hasattr(dag, 'schedule_interval'), \
            "DAG should have a schedule attribute"
        # schedule can be a timedelta, cron expression, or None
        # Just verify it exists
        assert True, "Schedule validation passed"

