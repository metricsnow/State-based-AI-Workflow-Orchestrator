"""
Tests for XCom data passing patterns.

This module contains unit tests for the xcom_data_passing_dag that validate:
- Simple value passing (int, str, float)
- Dictionary data passing
- List data passing
- Multiple outputs (multiple_outputs=True)
- Data validation
- Error handling for invalid data

Implementation Notes:
- Tests task functions independently (no Airflow runtime required)
- Validates data passing patterns and transformations
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

# Import DAG function
from xcom_data_passing_dag import xcom_data_passing_dag

# Extract task functions from the DAG function
dag_instance = xcom_data_passing_dag()

# Extract task functions for testing
# Simple value passing
extract_simple_value_task = dag_instance.get_task('extract_simple_value')
process_simple_value_task = dag_instance.get_task('process_simple_value')
consume_simple_value_task = dag_instance.get_task('consume_simple_value')

# Dictionary passing
extract_dict_task = dag_instance.get_task('extract_dict')
transform_dict_task = dag_instance.get_task('transform_dict')
consume_dict_task = dag_instance.get_task('consume_dict')

# List passing
extract_list_task = dag_instance.get_task('extract_list')
transform_list_task = dag_instance.get_task('transform_list')
consume_list_task = dag_instance.get_task('consume_list')

# Multiple outputs
extract_multiple_task = dag_instance.get_task('extract_multiple')
process_multiple_task = dag_instance.get_task('process_multiple')
consume_multiple_task = dag_instance.get_task('consume_multiple')

# Validation
extract_for_validation_task = dag_instance.get_task('extract_for_validation')
validate_data_task = dag_instance.get_task('validate_data')
consume_validated_task = dag_instance.get_task('consume_validated')

# Error handling
extract_invalid_data_task = dag_instance.get_task('extract_invalid_data')
handle_invalid_data_task = dag_instance.get_task('handle_invalid_data')
consume_error_handling_task = dag_instance.get_task('consume_error_handling')

# Extract Python functions
extract_simple_value_fn = extract_simple_value_task.python_callable
process_simple_value_fn = process_simple_value_task.python_callable
consume_simple_value_fn = consume_simple_value_task.python_callable

extract_dict_fn = extract_dict_task.python_callable
transform_dict_fn = transform_dict_task.python_callable
consume_dict_fn = consume_dict_task.python_callable

extract_list_fn = extract_list_task.python_callable
transform_list_fn = transform_list_task.python_callable
consume_list_fn = consume_list_task.python_callable

extract_multiple_fn = extract_multiple_task.python_callable
process_multiple_fn = process_multiple_task.python_callable
consume_multiple_fn = consume_multiple_task.python_callable

extract_for_validation_fn = extract_for_validation_task.python_callable
validate_data_fn = validate_data_task.python_callable
consume_validated_fn = consume_validated_task.python_callable

extract_invalid_data_fn = extract_invalid_data_task.python_callable
handle_invalid_data_fn = handle_invalid_data_task.python_callable
consume_error_handling_fn = consume_error_handling_task.python_callable


class TestSimpleValuePassing:
    """Test simple value passing pattern (int)."""

    def test_extract_simple_value_returns_int(self):
        """Test that extract_simple_value returns an integer."""
        result = extract_simple_value_fn()
        assert isinstance(result, int), \
            "extract_simple_value should return an integer"

    def test_extract_simple_value_returns_42(self):
        """Test that extract_simple_value returns 42."""
        result = extract_simple_value_fn()
        assert result == 42, \
            f"extract_simple_value should return 42, got {result}"

    def test_process_simple_value_multiplies_by_two(self):
        """Test that process_simple_value multiplies value by 2."""
        input_value = 42
        result = process_simple_value_fn(input_value)
        assert result == 84, \
            f"process_simple_value should multiply by 2, expected 84, got {result}"

    def test_consume_simple_value_accepts_int(self):
        """Test that consume_simple_value accepts integer value."""
        value = 84
        # Should not raise an error
        result = consume_simple_value_fn(value)
        assert result is None

    def test_simple_value_chain(self):
        """Test complete simple value passing chain."""
        extracted = extract_simple_value_fn()
        processed = process_simple_value_fn(extracted)
        consume_simple_value_fn(processed)
        # If we get here without errors, the chain works


class TestDictionaryPassing:
    """Test dictionary data passing pattern."""

    @pytest.fixture
    def sample_dict(self):
        """Fixture providing sample dictionary."""
        return {"data": [1, 2, 3, 4, 5]}

    def test_extract_dict_returns_dict(self):
        """Test that extract_dict returns a dictionary."""
        result = extract_dict_fn()
        assert isinstance(result, dict), \
            "extract_dict should return a dictionary"

    def test_extract_dict_contains_data_key(self):
        """Test that extract_dict returns data with 'data' key."""
        result = extract_dict_fn()
        assert "data" in result, \
            "extract_dict result should contain 'data' key"

    def test_transform_dict_multiplies_values(self, sample_dict):
        """Test that transform_dict multiplies values by 2."""
        result = transform_dict_fn(sample_dict)
        assert "transformed" in result, \
            "transform_dict should return 'transformed' key"
        assert result["transformed"] == [2, 4, 6, 8, 10], \
            f"transform_dict should multiply by 2, got {result['transformed']}"

    def test_consume_dict_validates_structure(self):
        """Test that consume_dict validates dictionary structure."""
        data = {"transformed": [2, 4, 6, 8, 10]}
        result = consume_dict_fn(data)
        assert result is None

    def test_dict_chain(self):
        """Test complete dictionary passing chain."""
        extracted = extract_dict_fn()
        transformed = transform_dict_fn(extracted)
        consume_dict_fn(transformed)
        # If we get here without errors, the chain works


class TestListPassing:
    """Test list data passing pattern."""

    @pytest.fixture
    def sample_list(self):
        """Fixture providing sample list."""
        return [10, 20, 30, 40, 50]

    def test_extract_list_returns_list(self):
        """Test that extract_list returns a list."""
        result = extract_list_fn()
        assert isinstance(result, list), \
            "extract_list should return a list"

    def test_extract_list_returns_integers(self):
        """Test that extract_list returns list of integers."""
        result = extract_list_fn()
        assert all(isinstance(x, int) for x in result), \
            "extract_list should return list of integers"

    def test_transform_list_squares_values(self, sample_list):
        """Test that transform_list squares each value."""
        result = transform_list_fn(sample_list)
        assert result == [100, 400, 900, 1600, 2500], \
            f"transform_list should square values, got {result}"

    def test_consume_list_validates_content(self):
        """Test that consume_list validates list content."""
        data = [100, 400, 900, 1600, 2500]
        result = consume_list_fn(data)
        assert result is None

    def test_list_chain(self):
        """Test complete list passing chain."""
        extracted = extract_list_fn()
        transformed = transform_list_fn(extracted)
        consume_list_fn(transformed)
        # If we get here without errors, the chain works


class TestMultipleOutputs:
    """Test multiple outputs pattern (multiple_outputs=True)."""

    def test_extract_multiple_returns_dict(self):
        """Test that extract_multiple returns a dictionary."""
        result = extract_multiple_fn()
        assert isinstance(result, dict), \
            "extract_multiple should return a dictionary"

    def test_extract_multiple_contains_all_keys(self):
        """Test that extract_multiple returns all required keys."""
        result = extract_multiple_fn()
        required_keys = ["count", "data", "status", "metadata"]
        for key in required_keys:
            assert key in result, \
                f"extract_multiple should contain '{key}' key"

    def test_extract_multiple_has_correct_types(self):
        """Test that extract_multiple returns correct types."""
        result = extract_multiple_fn()
        assert isinstance(result["count"], int), \
            "count should be an integer"
        assert isinstance(result["data"], list), \
            "data should be a list"
        assert isinstance(result["status"], str), \
            "status should be a string"
        assert isinstance(result["metadata"], dict), \
            "metadata should be a dictionary"

    def test_process_multiple_accepts_unpacked_values(self):
        """Test that process_multiple accepts unpacked values."""
        # Simulate multiple_outputs unpacking
        multiple_result = extract_multiple_fn()
        result = process_multiple_fn(
            count=multiple_result["count"],
            data=multiple_result["data"],
            status=multiple_result["status"],
            metadata=multiple_result["metadata"]
        )
        assert isinstance(result, dict), \
            "process_multiple should return a dictionary"
        assert result["processed"] is True, \
            "process_multiple should set processed=True"

    def test_process_multiple_calculates_total(self):
        """Test that process_multiple calculates total correctly."""
        multiple_result = extract_multiple_fn()
        result = process_multiple_fn(
            count=multiple_result["count"],
            data=multiple_result["data"],
            status=multiple_result["status"],
            metadata=multiple_result["metadata"]
        )
        assert result["total"] == 300, \
            f"process_multiple should calculate total=300, got {result['total']}"

    def test_consume_multiple_validates_result(self):
        """Test that consume_multiple validates processed result."""
        result = {
            "processed": True,
            "total": 300,
            "status": "success",
            "version": "1.0"
        }
        consume_result = consume_multiple_fn(result)
        assert consume_result is None

    def test_multiple_outputs_chain(self):
        """Test complete multiple outputs chain."""
        multiple_data = extract_multiple_fn()
        processed = process_multiple_fn(
            count=multiple_data["count"],
            data=multiple_data["data"],
            status=multiple_data["status"],
            metadata=multiple_data["metadata"]
        )
        consume_multiple_fn(processed)
        # If we get here without errors, the chain works


class TestDataValidation:
    """Test data validation pattern."""

    def test_extract_for_validation_returns_dict(self):
        """Test that extract_for_validation returns a dictionary."""
        result = extract_for_validation_fn()
        assert isinstance(result, dict), \
            "extract_for_validation should return a dictionary"

    def test_validate_data_accepts_valid_data(self):
        """Test that validate_data accepts valid data."""
        valid_data = {
            "data": [1, 2, 3, 4, 5],
            "count": 5,
            "valid": True
        }
        result = validate_data_fn(valid_data)
        assert result == valid_data, \
            "validate_data should return valid data unchanged"

    def test_validate_data_rejects_missing_data_key(self):
        """Test that validate_data rejects data missing 'data' key."""
        invalid_data = {"count": 5}
        with pytest.raises(ValueError, match="Data must contain 'data' key"):
            validate_data_fn(invalid_data)

    def test_validate_data_rejects_non_dict(self):
        """Test that validate_data rejects non-dictionary input."""
        with pytest.raises(ValueError, match="Data must be a dictionary"):
            validate_data_fn("not a dict")

    def test_validate_data_rejects_empty_list(self):
        """Test that validate_data rejects empty data list."""
        invalid_data = {
            "data": [],
            "count": 0
        }
        with pytest.raises(ValueError, match="Data\['data'\] must not be empty"):
            validate_data_fn(invalid_data)

    def test_validate_data_rejects_count_mismatch(self):
        """Test that validate_data rejects count mismatch."""
        invalid_data = {
            "data": [1, 2, 3],
            "count": 5  # Mismatch: count != len(data)
        }
        with pytest.raises(ValueError, match="Data count must match data length"):
            validate_data_fn(invalid_data)

    def test_consume_validated_accepts_validated_data(self):
        """Test that consume_validated accepts validated data."""
        validated_data = {
            "data": [1, 2, 3, 4, 5],
            "count": 5,
            "valid": True
        }
        result = consume_validated_fn(validated_data)
        assert result is None

    def test_validation_chain(self):
        """Test complete validation chain."""
        extracted = extract_for_validation_fn()
        validated = validate_data_fn(extracted)
        consume_validated_fn(validated)
        # If we get here without errors, the chain works


class TestErrorHandling:
    """Test error handling for invalid data."""

    def test_extract_invalid_data_returns_invalid_structure(self):
        """Test that extract_invalid_data returns invalid data structure."""
        result = extract_invalid_data_fn()
        assert isinstance(result, dict), \
            "extract_invalid_data should return a dictionary"
        assert "data" not in result, \
            "extract_invalid_data should return data without 'data' key"

    def test_handle_invalid_data_handles_missing_key(self):
        """Test that handle_invalid_data handles missing key gracefully."""
        invalid_data = {"invalid": "data"}
        result = handle_invalid_data_fn(invalid_data)
        assert isinstance(result, dict), \
            "handle_invalid_data should return a dictionary"
        assert result["error"] is True, \
            "handle_invalid_data should set error=True for invalid data"
        assert "message" in result, \
            "handle_invalid_data should include error message"

    def test_handle_invalid_data_handles_valid_data(self):
        """Test that handle_invalid_data handles valid data correctly."""
        valid_data = {
            "data": [1, 2, 3],
            "count": 3
        }
        result = handle_invalid_data_fn(valid_data)
        assert isinstance(result, dict), \
            "handle_invalid_data should return a dictionary"
        assert result["error"] is False, \
            "handle_invalid_data should set error=False for valid data"

    def test_consume_error_handling_accepts_error_result(self):
        """Test that consume_error_handling accepts error result."""
        error_result = {
            "error": True,
            "message": "Missing required 'data' key",
            "original_data": {"invalid": "data"}
        }
        result = consume_error_handling_fn(error_result)
        assert result is None

    def test_error_handling_chain(self):
        """Test complete error handling chain."""
        invalid_data = extract_invalid_data_fn()
        error_result = handle_invalid_data_fn(invalid_data)
        consume_error_handling_fn(error_result)
        # If we get here without errors, the chain works


class TestDataPassingIntegration:
    """Integration tests for all data passing patterns."""

    def test_all_patterns_work_independently(self):
        """Test that all data passing patterns work independently."""
        # Simple value
        simple = process_simple_value_fn(extract_simple_value_fn())
        assert simple == 84

        # Dictionary
        dict_result = transform_dict_fn(extract_dict_fn())
        assert "transformed" in dict_result

        # List
        list_result = transform_list_fn(extract_list_fn())
        assert len(list_result) == 5

        # Multiple outputs
        multiple = extract_multiple_fn()
        processed = process_multiple_fn(
            count=multiple["count"],
            data=multiple["data"],
            status=multiple["status"],
            metadata=multiple["metadata"]
        )
        assert processed["processed"] is True

        # Validation
        validated = validate_data_fn(extract_for_validation_fn())
        assert validated["valid"] is True

        # Error handling
        error_result = handle_invalid_data_fn(extract_invalid_data_fn())
        assert error_result["error"] is True
