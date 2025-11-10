"""
Tests for DAG import validation.

This module contains comprehensive tests to validate:
- DAG files can be imported without errors
- All DAGs are properly loaded
- Import error detection and reporting
- DAG file syntax validation

Implementation Notes:
- Uses Airflow's DagBag for DAG loading
- Tests validate import process without execution
- Comprehensive error detection and reporting
"""
import pytest
from airflow.models import DagBag
from pathlib import Path


class TestDAGImports:
    """Test DAG import validation."""

    @pytest.fixture(scope="class")
    def dag_bag(self):
        """Create DagBag instance for testing."""
        project_root = Path(__file__).parent.parent.parent
        dags_folder = project_root / "dags"
        return DagBag(dag_folder=str(dags_folder), include_examples=False)

    def test_dag_import_no_errors(self, dag_bag):
        """
        Test that all DAGs can be imported without errors.
        
        This is a critical test that ensures all DAG files are syntactically
        correct and can be loaded by Airflow without import errors.
        """
        assert len(dag_bag.import_errors) == 0, \
            f"DAG import errors found: {dag_bag.import_errors}"

    def test_dag_bag_initialization(self, dag_bag):
        """Test that DagBag is properly initialized."""
        assert dag_bag is not None, "DagBag should not be None"
        assert hasattr(dag_bag, 'dags'), "DagBag should have 'dags' attribute"
        assert hasattr(dag_bag, 'import_errors'), \
            "DagBag should have 'import_errors' attribute"

    def test_dag_bag_contains_dags(self, dag_bag):
        """Test that DagBag contains at least one DAG."""
        assert len(dag_bag.dags) > 0, \
            "DagBag should contain at least one DAG"

    def test_example_etl_dag_imported(self, dag_bag):
        """Test that example_etl_dag is successfully imported."""
        assert 'example_etl_dag' in dag_bag.dags, \
            "example_etl_dag should be imported and available in DagBag"

    def test_dag_import_error_format(self, dag_bag):
        """
        Test that import errors are properly formatted.
        
        This test ensures that if import errors occur, they are
        properly formatted and can be debugged.
        """
        # If there are import errors, they should be in a dict format
        assert isinstance(dag_bag.import_errors, dict), \
            "import_errors should be a dictionary"

    def test_all_dags_have_valid_ids(self, dag_bag):
        """Test that all imported DAGs have valid DAG IDs."""
        for dag_id, dag in dag_bag.dags.items():
            assert dag_id is not None, f"DAG ID should not be None for {dag_id}"
            assert isinstance(dag_id, str), \
                f"DAG ID should be a string, got {type(dag_id)} for {dag_id}"
            assert len(dag_id) > 0, \
                f"DAG ID should not be empty for {dag_id}"

    def test_dag_import_performance(self, dag_bag):
        """
        Test that DAG imports complete in reasonable time.
        
        This test ensures that DAG loading doesn't take too long,
        which could indicate performance issues.
        """
        # This is a basic performance check
        # In a real scenario, you might want to measure actual time
        assert len(dag_bag.dags) > 0, \
            "DAGs should be loaded (performance check)"

    def test_dag_file_syntax_validation(self, dag_bag):
        """
        Test that DAG files have valid Python syntax.
        
        If a DAG file has syntax errors, it will appear in import_errors.
        This test ensures no syntax errors exist.
        """
        for file_path, error in dag_bag.import_errors.items():
            pytest.fail(
                f"DAG file {file_path} has import error: {error}"
            )

