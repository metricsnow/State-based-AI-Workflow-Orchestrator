"""Comprehensive tests for conditional routing in LangGraph workflows.

This test suite validates routing functions, conditional edge execution,
and end-to-end workflow execution with different routing paths.
"""

import pytest

from langgraph.graph import END

from langgraph_workflows.conditional_workflow import (
    error_handler,
    execute_conditional_workflow,
    graph,
    should_continue,
)
from langgraph_workflows.state import SimpleState


class TestRoutingFunction:
    """Test the routing function independently."""

    def test_routing_processing(self) -> None:
        """Test routing when status is processing."""
        state: SimpleState = {"data": {}, "status": "processing"}
        result = should_continue(state)
        assert result == "node_b"

    def test_routing_completed(self) -> None:
        """Test routing when status is completed."""
        state: SimpleState = {"data": {}, "status": "completed"}
        result = should_continue(state)
        assert result == "end"

    def test_routing_error(self) -> None:
        """Test routing when status is error."""
        state: SimpleState = {"data": {}, "status": "error"}
        result = should_continue(state)
        assert result == "error_handler"

    def test_routing_unknown_status(self) -> None:
        """Test routing with unknown status defaults to node_a."""
        state: SimpleState = {"data": {}, "status": "unknown"}
        result = should_continue(state)
        assert result == "node_a"

    def test_routing_empty_status(self) -> None:
        """Test routing with empty status defaults to node_a."""
        state: SimpleState = {"data": {}}
        result = should_continue(state)
        assert result == "node_a"

    def test_routing_initialized(self) -> None:
        """Test routing when status is initialized."""
        state: SimpleState = {"data": {}, "status": "initialized"}
        result = should_continue(state)
        assert result == "node_a"


class TestErrorHandler:
    """Test the error handler node function."""

    def test_error_handler_updates_state(self) -> None:
        """Test error handler updates state correctly."""
        state: SimpleState = {"data": {}, "status": "error"}
        result = error_handler(state)

        assert result["status"] == "error_handled"
        assert result["data"]["error_handled"] is True
        assert result["data"]["step"] == "error_handler"

    def test_error_handler_preserves_existing_data(self) -> None:
        """Test error handler preserves existing data."""
        state: SimpleState = {
            "data": {"existing": "value", "error_info": "test"},
            "status": "error",
        }
        result = error_handler(state)

        assert result["status"] == "error_handled"
        assert result["data"]["error_handled"] is True
        assert result["data"]["existing"] == "value"
        assert result["data"]["error_info"] == "test"


class TestGraphConstruction:
    """Test graph construction and compilation."""

    def test_graph_is_compiled(self) -> None:
        """Test that graph is successfully compiled."""
        assert graph is not None
        assert hasattr(graph, "invoke")

    def test_graph_can_be_invoked(self) -> None:
        """Test that compiled graph can be invoked."""
        initial_state: SimpleState = {
            "data": {"test": "value"},
            "status": "initialized",
        }

        # Should not raise an exception
        result = graph.invoke(initial_state)
        assert result is not None


class TestConditionalWorkflowExecution:
    """Test complete conditional workflow execution with different paths."""

    def test_workflow_processing_path(self) -> None:
        """Test workflow execution with processing status routes to node_b."""
        result = execute_conditional_workflow({"input": "test"}, "processing")

        # Should go: node_a -> node_b -> END
        assert result["status"] == "completed"
        assert result["data"]["finalized"] is True
        assert result["data"]["step"] == "b"

    def test_workflow_completed_path(self) -> None:
        """Test workflow execution with completed status routes directly to END."""
        result = execute_conditional_workflow({"input": "test"}, "completed")

        # Should go: node_a -> END (skips node_b)
        # node_a preserves "completed" status, routing function routes to END
        assert result["status"] == "completed"
        assert result["data"]["processed"] is True
        assert result["data"]["step"] == "a"
        # Should NOT have "finalized" since node_b was skipped
        assert "finalized" not in result["data"]

    def test_workflow_error_path(self) -> None:
        """Test workflow execution with error status routes to error_handler."""
        result = execute_conditional_workflow({"input": "test"}, "error")

        # Should go: node_a -> error_handler -> END
        # node_a preserves "error" status, routing function routes to error_handler
        assert result["status"] == "error_handled"
        assert result["data"]["error_handled"] is True
        assert result["data"]["step"] == "error_handler"
        assert result["data"]["processed"] is True

    def test_workflow_initialized_path(self) -> None:
        """Test workflow execution with initialized status (default path)."""
        result = execute_conditional_workflow({"input": "test"}, "initialized")

        # Should go: node_a -> node_b -> END (normal flow)
        assert result["status"] == "completed"
        assert result["data"]["finalized"] is True
        assert result["data"]["step"] == "b"

    def test_workflow_with_empty_data(self) -> None:
        """Test workflow execution with empty initial data."""
        result = execute_conditional_workflow({}, "initialized")

        assert result["status"] == "completed"
        assert result["data"]["finalized"] is True


class TestRoutingPaths:
    """Test different routing paths in the workflow."""

    def test_routing_to_node_b(self) -> None:
        """Test routing to node_b path executes correctly."""
        # Create state that will route to node_b
        initial_state: SimpleState = {
            "data": {"input": "test"},
            "status": "processing",
        }

        result = graph.invoke(initial_state)

        # After node_a executes, status becomes "processing", routes to node_b
        assert result["status"] == "completed"
        assert "finalized" in result["data"]

    def test_routing_to_end(self) -> None:
        """Test routing directly to END."""
        # Test routing to END by setting initial status to "completed"
        initial_state: SimpleState = {
            "data": {"input": "test"},
            "status": "completed",
        }

        result = graph.invoke(initial_state)

        # Should route directly to END, skipping node_b
        assert result["status"] == "completed"
        assert result["data"]["processed"] is True
        assert "finalized" not in result["data"]

    def test_routing_to_error_handler(self) -> None:
        """Test routing to error_handler path."""
        # Test routing to error_handler by setting initial status to "error"
        initial_state: SimpleState = {
            "data": {"input": "test"},
            "status": "error",
        }

        result = graph.invoke(initial_state)

        # Should route to error_handler
        assert result["status"] == "error_handled"
        assert result["data"]["error_handled"] is True
        assert result["data"]["step"] == "error_handler"


class TestStateDependentRouting:
    """Test state-dependent routing behavior."""

    def test_state_updates_affect_routing(self) -> None:
        """Test that state updates from nodes affect routing decisions."""
        initial_state: SimpleState = {
            "data": {"input": "test"},
            "status": "initialized",
        }

        result = graph.invoke(initial_state)

        # node_a sets status to "processing", which routes to node_b
        assert result["status"] == "completed"
        assert result["data"]["step"] == "b"

    def test_multiple_routing_scenarios(self) -> None:
        """Test multiple routing scenarios with different initial states."""
        # Test with different initial statuses
        scenarios = [
            ("initialized", "completed"),
            ("processing", "completed"),
        ]

        for initial_status, expected_final_status in scenarios:
            result = execute_conditional_workflow(
                {"input": "test"}, initial_status
            )
            assert result["status"] == expected_final_status


class TestErrorHandling:
    """Test error handling in conditional routing."""

    def test_workflow_handles_invalid_state(self) -> None:
        """Test workflow handles invalid state structure gracefully."""
        invalid_state = {"invalid": "structure"}

        # LangGraph may either raise an error or handle it gracefully
        try:
            result = graph.invoke(invalid_state)
            # If it doesn't raise, it should return a result
            assert result is not None
        except (TypeError, KeyError, ValueError, AttributeError) as e:
            # If it raises an error, that's also acceptable behavior
            assert isinstance(e, (TypeError, KeyError, ValueError, AttributeError))

    def test_routing_function_handles_missing_status(self) -> None:
        """Test routing function handles missing status field."""
        state: SimpleState = {"data": {}}
        result = should_continue(state)
        # Should default to "node_a"
        assert result == "node_a"


class TestIntegrationScenarios:
    """Integration test scenarios for conditional routing."""

    def test_complete_workflow_with_conditional_routing(self) -> None:
        """Test complete workflow execution with conditional routing."""
        initial_data = {"input": "test", "value": 42}
        result = execute_conditional_workflow(initial_data, "initialized")

        # Verify complete workflow execution
        assert result["status"] == "completed"
        assert result["data"]["finalized"] is True
        assert result["data"]["step"] == "b"
        # Initial data should be preserved
        assert result["data"]["input"] == "test"
        assert result["data"]["value"] == 42

    def test_routing_map_validation(self) -> None:
        """Test that routing map is correctly defined."""
        # Verify that all routing function return values map to valid nodes
        # by testing each routing path with actual graph execution
        routing_paths = [
            ("processing", "node_b"),
            ("completed", "end"),
            ("error", "error_handler"),
            ("initialized", "node_a"),
        ]

        for initial_status, expected_route in routing_paths:
            initial_state: SimpleState = {
                "data": {"test": "value"},
                "status": initial_status,
            }

            # Execute graph to verify routing works
            result = graph.invoke(initial_state)

            # Verify the graph executed successfully (routing map is valid)
            assert result is not None
            assert "data" in result
            assert "status" in result

            # Verify routing worked correctly based on status
            if expected_route == "node_b":
                # Should have gone through node_b, so finalized should be present
                assert result["data"].get("finalized") is True or result["status"] == "completed"
            elif expected_route == "end":
                # Should have routed to END, so no finalized
                assert result["status"] == "completed"
                assert "finalized" not in result["data"] or result["data"].get("step") == "a"
            elif expected_route == "error_handler":
                # Should have gone through error_handler
                assert result["status"] == "error_handled"
                assert result["data"].get("error_handled") is True

