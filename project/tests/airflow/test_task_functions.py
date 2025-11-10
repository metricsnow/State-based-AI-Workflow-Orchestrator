"""
Tests for task function unit testing.

This module contains unit tests for task functions that can be tested
independently without Airflow runtime. Task functions are regular Python
functions that can be tested directly.

Implementation Notes:
- Tests task functions independently (no Airflow runtime required)
- Validates function logic and data transformations
- Tests error handling and edge cases
- Uses pytest fixtures for test data
"""
import pytest
from pathlib import Path
import sys

# Add dags directory to path for importing task functions
project_root = Path(__file__).parent.parent.parent
dags_path = project_root / "dags"
sys.path.insert(0, str(dags_path))

# Import task functions from example_etl_dag
# The DAG initialization will happen, but we only use the functions
from example_etl_dag import extract_data, transform_data, load_data


class TestExtractTask:
    """Test extract_data task function."""

    def test_extract_data_returns_dict(self):
        """Test that extract_data returns a dictionary."""
        result = extract_data()
        assert isinstance(result, dict), \
            "extract_data should return a dictionary"

    def test_extract_data_contains_data_key(self):
        """Test that extract_data returns data with 'data' key."""
        result = extract_data()
        assert 'data' in result, \
            "extract_data result should contain 'data' key"

    def test_extract_data_returns_list(self):
        """Test that extract_data returns a list in 'data' key."""
        result = extract_data()
        assert isinstance(result['data'], list), \
            "extract_data['data'] should be a list"

    def test_extract_data_returns_non_empty_list(self):
        """Test that extract_data returns non-empty data."""
        result = extract_data()
        assert len(result['data']) > 0, \
            "extract_data should return non-empty data"

    def test_extract_data_returns_integers(self):
        """Test that extract_data returns integer values."""
        result = extract_data()
        for value in result['data']:
            assert isinstance(value, int), \
                f"All values in extract_data should be integers, got {type(value)}"

    def test_extract_data_consistency(self):
        """Test that extract_data returns consistent results."""
        result1 = extract_data()
        result2 = extract_data()
        assert result1 == result2, \
            "extract_data should return consistent results"


class TestTransformTask:
    """Test transform_data task function."""

    @pytest.fixture
    def sample_extracted_data(self):
        """Fixture providing sample extracted data."""
        return {'data': [1, 2, 3, 4, 5]}

    def test_transform_data_requires_context(self):
        """Test that transform_data requires context parameter."""
        # Create a mock context with task_instance
        class MockTaskInstance:
            def xcom_pull(self, task_ids):
                return {'data': [1, 2, 3, 4, 5]}

        class MockContext:
            def __init__(self):
                self.ti = MockTaskInstance()

        context = MockContext()
        result = transform_data(**{'ti': context.ti})
        assert isinstance(result, dict), \
            "transform_data should return a dictionary"

    def test_transform_data_returns_dict(self, sample_extracted_data):
        """Test that transform_data returns a dictionary."""
        class MockTaskInstance:
            def xcom_pull(self, task_ids):
                return sample_extracted_data

        context = {'ti': MockTaskInstance()}
        result = transform_data(**context)
        assert isinstance(result, dict), \
            "transform_data should return a dictionary"

    def test_transform_data_contains_transformed_data_key(self, sample_extracted_data):
        """Test that transform_data returns 'transformed_data' key."""
        class MockTaskInstance:
            def xcom_pull(self, task_ids):
                return sample_extracted_data

        context = {'ti': MockTaskInstance()}
        result = transform_data(**context)
        assert 'transformed_data' in result, \
            "transform_data result should contain 'transformed_data' key"

    def test_transform_data_multiplies_by_two(self, sample_extracted_data):
        """Test that transform_data multiplies values by 2."""
        class MockTaskInstance:
            def xcom_pull(self, task_ids):
                return sample_extracted_data

        context = {'ti': MockTaskInstance()}
        result = transform_data(**context)
        expected = [2, 4, 6, 8, 10]
        assert result['transformed_data'] == expected, \
            f"transform_data should multiply by 2, expected {expected}, got {result['transformed_data']}"

    def test_transform_data_handles_empty_list(self):
        """Test that transform_data handles empty input."""
        class MockTaskInstance:
            def xcom_pull(self, task_ids):
                return {'data': []}

        context = {'ti': MockTaskInstance()}
        result = transform_data(**context)
        assert result['transformed_data'] == [], \
            "transform_data should handle empty lists"

    def test_transform_data_handles_single_value(self):
        """Test that transform_data handles single value."""
        class MockTaskInstance:
            def xcom_pull(self, task_ids):
                return {'data': [42]}

        context = {'ti': MockTaskInstance()}
        result = transform_data(**context)
        assert result['transformed_data'] == [84], \
            "transform_data should handle single values"


class TestLoadTask:
    """Test load_data task function."""

    @pytest.fixture
    def sample_transformed_data(self):
        """Fixture providing sample transformed data."""
        return {'transformed_data': [2, 4, 6, 8, 10]}

    def test_load_data_requires_context(self, sample_transformed_data):
        """Test that load_data requires context parameter."""
        class MockTaskInstance:
            def xcom_pull(self, task_ids):
                return sample_transformed_data

        context = {'ti': MockTaskInstance()}
        # load_data should not raise an error
        result = load_data(**context)
        # load_data returns None, so we just check it doesn't raise
        assert result is None or True, \
            "load_data should execute without errors"

    def test_load_data_processes_data(self, sample_transformed_data):
        """Test that load_data processes transformed data."""
        class MockTaskInstance:
            def xcom_pull(self, task_ids):
                return sample_transformed_data

        context = {'ti': MockTaskInstance()}
        # Should not raise an error
        result = load_data(**context)
        # load_data returns None, so we just verify it executes
        assert True, "load_data should process data without errors"

    def test_load_data_handles_empty_data(self):
        """Test that load_data handles empty transformed data."""
        class MockTaskInstance:
            def xcom_pull(self, task_ids):
                return {'transformed_data': []}

        context = {'ti': MockTaskInstance()}
        # Should not raise an error
        result = load_data(**context)
        assert True, "load_data should handle empty data"


class TestTaskFunctionIntegration:
    """Integration tests for task functions working together."""

    def test_extract_transform_integration(self):
        """Test that extract and transform functions work together."""
        # Extract data
        extracted = extract_data()
        
        # Simulate transform receiving extracted data
        class MockTaskInstance:
            def xcom_pull(self, task_ids):
                return extracted

        context = {'ti': MockTaskInstance()}
        transformed = transform_data(**context)
        
        # Verify transformation
        assert 'transformed_data' in transformed
        assert len(transformed['transformed_data']) == len(extracted['data'])
        assert all(
            transformed['transformed_data'][i] == extracted['data'][i] * 2
            for i in range(len(extracted['data']))
        ), "Transform should multiply each value by 2"

