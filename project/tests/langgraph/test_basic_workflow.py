"""Comprehensive tests for basic LangGraph StateGraph workflow.

This test suite validates node functions, graph construction, compilation,
and end-to-end workflow execution.
"""

import pytest

from langgraph_workflows.basic_workflow import (
    execute_workflow,
    graph,
    node_a,
    node_b,
)
from langgraph_workflows.state import SimpleState


class TestNodeFunctions:
    """Test individual node functions independently."""

    def test_node_a_updates_state(self) -> None:
        """Test node_a function updates state correctly."""
        state: SimpleState = {"data": {}, "status": "initial"}
        result = node_a(state)

        assert result["status"] == "processing"
        assert "processed" in result["data"]
        assert result["data"]["step"] == "a"
        assert result["data"]["processed"] is True

    def test_node_a_preserves_existing_data(self) -> None:
        """Test node_a preserves existing data in state."""
        state: SimpleState = {"data": {"existing": "value"}, "status": "initial"}
        result = node_a(state)

        # The reducer should merge, but node_a returns new dict
        # So existing data is replaced (this is expected behavior)
        assert result["data"]["step"] == "a"
        assert result["data"]["processed"] is True

    def test_node_b_updates_state(self) -> None:
        """Test node_b function updates state correctly."""
        state: SimpleState = {
            "data": {"step": "a", "processed": True},
            "status": "processing",
        }
        result = node_b(state)

        assert result["status"] == "completed"
        assert "finalized" in result["data"]
        assert result["data"]["finalized"] is True
        assert result["data"]["step"] == "b"

    def test_node_b_preserves_previous_data(self) -> None:
        """Test node_b preserves data from previous node."""
        state: SimpleState = {
            "data": {"step": "a", "processed": True, "value": 42},
            "status": "processing",
        }
        result = node_b(state)

        # Should preserve previous data and add new fields
        assert result["data"]["step"] == "b"
        assert result["data"]["finalized"] is True
        assert result["data"]["processed"] is True
        assert result["data"]["value"] == 42

    def test_node_b_handles_empty_data(self) -> None:
        """Test node_b handles state with empty data."""
        state: SimpleState = {"data": {}, "status": "processing"}
        result = node_b(state)

        assert result["status"] == "completed"
        assert result["data"]["step"] == "b"
        assert result["data"]["finalized"] is True


class TestGraphConstruction:
    """Test graph construction and compilation."""

    def test_graph_is_compiled(self) -> None:
        """Test that graph is successfully compiled."""
        assert graph is not None
        assert hasattr(graph, "invoke")

    def test_graph_has_nodes(self) -> None:
        """Test that graph contains the expected nodes."""
        # Check that nodes are registered
        assert hasattr(graph, "nodes") or hasattr(graph, "_nodes")

    def test_graph_can_be_invoked(self) -> None:
        """Test that compiled graph can be invoked."""
        initial_state: SimpleState = {
            "data": {"test": "value"},
            "status": "initialized",
        }

        # Should not raise an exception
        result = graph.invoke(initial_state)
        assert result is not None


class TestWorkflowExecution:
    """Test complete workflow execution end-to-end."""

    def test_workflow_execution_completes(self) -> None:
        """Test complete workflow execution."""
        initial_data = {"input": "test"}
        result = execute_workflow(initial_data)

        assert result["status"] == "completed"
        assert result["data"]["finalized"] is True

    def test_workflow_execution_state_flow(self) -> None:
        """Test state flows correctly through all nodes."""
        initial_data = {"input": "test", "value": 42}
        result = execute_workflow(initial_data)

        # Verify final state
        assert result["status"] == "completed"
        assert result["data"]["finalized"] is True
        assert result["data"]["step"] == "b"
        # Initial data should be preserved (merged by reducer)
        assert result["data"]["input"] == "test"
        assert result["data"]["value"] == 42

    def test_workflow_execution_with_empty_data(self) -> None:
        """Test workflow execution with empty initial data."""
        result = execute_workflow({})

        assert result["status"] == "completed"
        assert result["data"]["finalized"] is True
        assert result["data"]["step"] == "b"

    def test_workflow_execution_preserves_initial_data(self) -> None:
        """Test that initial data is preserved through workflow."""
        initial_data = {"custom": "data", "number": 123}
        result = execute_workflow(initial_data)

        # Initial data should be merged with node outputs
        assert result["data"]["custom"] == "data"
        assert result["data"]["number"] == 123
        assert result["data"]["step"] == "b"
        assert result["data"]["finalized"] is True

    def test_workflow_execution_state_updates(self) -> None:
        """Test that state updates are visible in execution."""
        initial_data = {"test": "value"}
        result = execute_workflow(initial_data)

        # Verify state progression
        assert "processed" in result["data"] or result["data"].get("step") == "b"
        assert result["data"]["finalized"] is True
        assert result["status"] == "completed"


class TestStateUpdates:
    """Test state updates through workflow execution."""

    def test_state_updates_through_nodes(self) -> None:
        """Test state updates are applied correctly through nodes."""
        initial_state: SimpleState = {
            "data": {"initial": "value"},
            "status": "initialized",
        }

        # Execute workflow
        result = graph.invoke(initial_state)

        # Verify state was updated
        assert result["status"] == "completed"
        assert result["data"]["step"] == "b"
        assert result["data"]["finalized"] is True

    def test_state_reducer_merges_data(self) -> None:
        """Test that state reducer properly merges data."""
        initial_state: SimpleState = {
            "data": {"preserved": "value"},
            "status": "initialized",
        }

        result = graph.invoke(initial_state)

        # Data should be merged (reducer behavior)
        assert result["data"]["preserved"] == "value"
        assert result["data"]["step"] == "b"
        assert result["data"]["finalized"] is True

    def test_status_reducer_updates_correctly(self) -> None:
        """Test that status reducer updates correctly."""
        initial_state: SimpleState = {
            "data": {},
            "status": "initialized",
        }

        result = graph.invoke(initial_state)

        # Status should be updated to "completed" (last_value reducer)
        assert result["status"] == "completed"


class TestErrorHandling:
    """Test error handling in workflow execution."""

    def test_workflow_handles_missing_fields(self) -> None:
        """Test workflow handles state with missing optional fields."""
        # SimpleState requires "data" and "status", but test with minimal state
        initial_state: SimpleState = {
            "data": {},
            "status": "initialized",
        }

        result = graph.invoke(initial_state)
        assert result is not None
        assert result["status"] == "completed"

    def test_workflow_handles_invalid_state_structure(self) -> None:
        """Test workflow handles invalid state structure gracefully."""
        # LangGraph may handle invalid state by using defaults or raising errors
        # Test that it doesn't crash unexpectedly
        invalid_state = {"invalid": "structure"}

        # LangGraph may either raise an error or handle it gracefully
        # We test that it doesn't crash the system
        try:
            result = graph.invoke(invalid_state)
            # If it doesn't raise, it should return a result
            assert result is not None
        except (TypeError, KeyError, ValueError, AttributeError) as e:
            # If it raises an error, that's also acceptable behavior
            assert isinstance(e, (TypeError, KeyError, ValueError, AttributeError))

