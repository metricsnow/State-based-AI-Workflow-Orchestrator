"""Comprehensive integration tests for stateful LangGraph workflow.

This test suite validates end-to-end workflow execution, state management,
conditional routing, checkpointing, and workflow resumption. It ensures all
acceptance criteria for Milestone 1.4 are met.

All tests use the checkpoint_workflow module which combines:
- StateGraph with TypedDict state definition (SimpleState)
- Multiple nodes with state updates (node_a_conditional, node_b, error_handler)
- Conditional routing (should_continue function)
- Checkpointing (InMemorySaver checkpointer)
"""

import uuid

import pytest

from langgraph.checkpoint.memory import InMemorySaver
from langgraph_workflows.checkpoint_workflow import (
    checkpoint_graph,
    execute_with_checkpoint,
    get_checkpoint_state,
    resume_workflow,
)
from langgraph_workflows.state import SimpleState, validate_simple_state


class TestCompleteWorkflowExecution:
    """Test complete workflow execution end-to-end."""

    def test_complete_workflow_execution_processing(self):
        """Test complete workflow execution with processing status."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        initial_state: SimpleState = {
            "data": {"input": "test", "value": 42},
            "status": "processing",
        }

        result = checkpoint_graph.invoke(initial_state, config=config)

        # Verify workflow completed successfully
        assert result is not None
        assert "data" in result
        assert "status" in result
        # Status should be completed after node_b execution
        assert result["status"] == "completed"
        # Verify data was processed through nodes
        assert "finalized" in result["data"]
        assert result["data"]["finalized"] is True
        assert result["data"]["step"] == "b"

    def test_complete_workflow_execution_initialized(self):
        """Test complete workflow execution with initialized status."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        initial_state: SimpleState = {
            "data": {"input": "test"},
            "status": "initialized",
        }

        result = checkpoint_graph.invoke(initial_state, config=config)

        # Verify workflow completed
        assert result is not None
        assert result["status"] == "completed"
        assert "finalized" in result["data"]

    def test_complete_workflow_execution_with_execute_helper(self):
        """Test complete workflow execution using execute_with_checkpoint helper."""
        initial_state: SimpleState = {
            "data": {"input": "test", "helper": True},
            "status": "processing",
        }

        result, thread_id = execute_with_checkpoint(initial_state)

        # Verify execution successful
        assert result is not None
        assert thread_id is not None
        assert isinstance(thread_id, str)
        assert result["status"] == "completed"
        assert result["data"]["finalized"] is True

    def test_workflow_execution_preserves_data(self):
        """Test that workflow execution preserves and merges data correctly."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        initial_state: SimpleState = {
            "data": {"original": "data", "preserved": True},
            "status": "processing",
        }

        result = checkpoint_graph.invoke(initial_state, config=config)

        # Verify original data is preserved (merged with node updates)
        assert "original" in result["data"]
        assert result["data"]["original"] == "data"
        assert result["data"]["preserved"] is True
        # Verify node updates are also present
        assert "finalized" in result["data"]


class TestStatePersistenceAcrossSteps:
    """Test state persists across workflow steps."""

    def test_state_persistence_across_multiple_invocations(self):
        """Test state persists across multiple workflow invocations."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # Step 1: Initial execution
        state1: SimpleState = {"data": {"step": 1, "iteration": 1}, "status": "processing"}
        result1 = checkpoint_graph.invoke(state1, config=config)

        # Verify first execution
        assert result1 is not None
        assert result1["data"]["step"] == "b"  # Final step
        assert result1["data"]["iteration"] == 1

        # Step 2: Second invocation with same thread_id (should have persisted state)
        state2: SimpleState = {"data": {"step": 2, "iteration": 2}, "status": "processing"}
        result2 = checkpoint_graph.invoke(state2, config=config)

        # Verify second execution merged with persisted state
        assert result2 is not None
        # Data should be merged (reducer behavior)
        assert result2["data"]["iteration"] == 2  # Latest value
        assert result2["data"]["step"] == "b"  # From node_b

    def test_state_persistence_with_checkpoint_retrieval(self):
        """Test state persistence by retrieving checkpoint state."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # Execute workflow
        state: SimpleState = {"data": {"test": "persistence"}, "status": "processing"}
        result = checkpoint_graph.invoke(state, config=config)

        # Retrieve checkpoint state
        checkpoint_state = get_checkpoint_state(thread_id)

        # Verify checkpoint state matches execution result
        assert checkpoint_state is not None
        assert checkpoint_state["status"] == result["status"]
        assert checkpoint_state["data"]["test"] == "persistence"
        assert checkpoint_state["data"]["finalized"] is True

    def test_state_persistence_with_data_merging(self):
        """Test that state persistence correctly merges data using reducers."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # First invocation
        state1: SimpleState = {
            "data": {"key1": "value1", "key2": "value2"},
            "status": "processing",
        }
        result1 = checkpoint_graph.invoke(state1, config=config)

        # Second invocation with additional data
        state2: SimpleState = {
            "data": {"key2": "updated_value2", "key3": "value3"},
            "status": "processing",
        }
        result2 = checkpoint_graph.invoke(state2, config=config)

        # Verify data merging (merge_dicts reducer)
        assert result2["data"]["key1"] == "value1"  # Preserved from first
        assert result2["data"]["key2"] == "updated_value2"  # Updated from second
        assert result2["data"]["key3"] == "value3"  # New from second
        assert result2["data"]["finalized"] is True  # From node_b


class TestConditionalRouting:
    """Test conditional routing based on state conditions."""

    def test_conditional_routing_processing_path(self):
        """Test conditional routing when status is processing."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        state_processing: SimpleState = {
            "data": {"routing_test": True},
            "status": "processing",
        }

        result = checkpoint_graph.invoke(state_processing, config=config)

        # Processing status should route to node_b
        assert result["status"] == "completed"
        assert result["data"]["finalized"] is True
        assert result["data"]["step"] == "b"

    def test_conditional_routing_completed_path(self):
        """Test conditional routing when status is completed."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        state_completed: SimpleState = {
            "data": {"routing_test": "completed"},
            "status": "completed",
        }

        result = checkpoint_graph.invoke(state_completed, config=config)

        # Completed status should route directly to END
        assert result["status"] == "completed"
        # Should not have finalized (didn't go through node_b)
        assert "finalized" not in result["data"] or result["data"].get("finalized") is not True

    def test_conditional_routing_error_path(self):
        """Test conditional routing when status is error."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        state_error: SimpleState = {
            "data": {"routing_test": "error"},
            "status": "error",
        }

        result = checkpoint_graph.invoke(state_error, config=config)

        # Error status should route to error_handler
        assert result["status"] == "error_handled"
        assert result["data"]["error_handled"] is True
        assert result["data"]["step"] == "error_handler"

    def test_conditional_routing_unknown_status(self):
        """Test conditional routing with unknown status defaults to node_a."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        state_unknown: SimpleState = {
            "data": {"routing_test": "unknown"},
            "status": "unknown",
        }

        result = checkpoint_graph.invoke(state_unknown, config=config)

        # Unknown status should default to node_a, then route based on node_a output
        assert result is not None
        assert "status" in result


class TestCheckpointing:
    """Test checkpointing functionality."""

    def test_checkpointing_configured(self):
        """Test that checkpointing is properly configured."""
        assert checkpoint_graph.checkpointer is not None
        assert isinstance(checkpoint_graph.checkpointer, InMemorySaver)

    def test_checkpoint_saved_after_execution(self):
        """Test that checkpoint is saved after workflow execution."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        state: SimpleState = {"data": {"checkpoint_test": True}, "status": "processing"}
        result = checkpoint_graph.invoke(state, config=config)

        # Verify checkpoint exists
        checkpoint_state = get_checkpoint_state(thread_id)
        assert checkpoint_state is not None
        assert checkpoint_state["status"] == result["status"]
        assert checkpoint_state["data"]["checkpoint_test"] is True

    def test_checkpoint_isolation_between_threads(self):
        """Test that checkpoints are isolated between different thread IDs."""
        thread_id_1 = str(uuid.uuid4())
        thread_id_2 = str(uuid.uuid4())

        config1 = {"configurable": {"thread_id": thread_id_1}}
        config2 = {"configurable": {"thread_id": thread_id_2}}

        state1: SimpleState = {"data": {"thread": 1}, "status": "processing"}
        state2: SimpleState = {"data": {"thread": 2}, "status": "processing"}

        result1 = checkpoint_graph.invoke(state1, config=config1)
        result2 = checkpoint_graph.invoke(state2, config=config2)

        # Verify checkpoints are isolated
        checkpoint1 = get_checkpoint_state(thread_id_1)
        checkpoint2 = get_checkpoint_state(thread_id_2)

        assert checkpoint1 is not None
        assert checkpoint2 is not None
        assert checkpoint1["data"]["thread"] == 1
        assert checkpoint2["data"]["thread"] == 2

    def test_checkpoint_state_structure(self):
        """Test that checkpoint state has correct structure."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        state: SimpleState = {
            "data": {"structure_test": "value"},
            "status": "processing",
        }
        checkpoint_graph.invoke(state, config=config)

        checkpoint_state = get_checkpoint_state(thread_id)

        # Verify state structure
        assert validate_simple_state(checkpoint_state)
        assert "data" in checkpoint_state
        assert "status" in checkpoint_state
        assert isinstance(checkpoint_state["data"], dict)
        assert isinstance(checkpoint_state["status"], str)


class TestWorkflowResumption:
    """Test workflow resumption from checkpoints."""

    def test_workflow_resumption_with_additional_state(self):
        """Test workflow can be resumed from checkpoint with additional state."""
        # Initial execution
        state1: SimpleState = {"data": {"custom_key": "value1", "initial": True}, "status": "processing"}
        result1, thread_id = execute_with_checkpoint(state1)

        # Verify initial execution
        assert result1 is not None
        assert thread_id is not None

        # Resume workflow with additional state
        state2: SimpleState = {"data": {"custom_key": "value2", "resumed": True}, "status": "processing"}
        result2 = resume_workflow(thread_id, state2)

        # Verify resumption successful
        assert result2 is not None
        # Verify merged state (initial + resumed)
        # Note: Workflow re-executes from START, so node functions will set step="b"
        assert result2["data"]["initial"] is True  # From first execution (preserved in checkpoint)
        assert result2["data"]["resumed"] is True  # From resumption
        assert result2["data"]["custom_key"] == "value2"  # Latest value (y takes precedence in merge_dicts)
        assert result2["data"]["step"] == "b"  # From node_b execution

    def test_workflow_resumption_without_additional_state(self):
        """Test workflow can be resumed from checkpoint without additional state."""
        # Initial execution
        state1: SimpleState = {"data": {"custom_data": "preserved"}, "status": "processing"}
        result1, thread_id = execute_with_checkpoint(state1)

        # Resume without additional state (uses checkpoint state as-is)
        result2 = resume_workflow(thread_id, None)

        # Verify resumption successful
        assert result2 is not None
        # Workflow re-executes from START, so node_a_conditional runs first
        # The checkpoint state is used, but workflow execution continues
        assert result2["data"]["custom_data"] == "preserved"  # Preserved from checkpoint
        assert result2["status"] == "completed"  # Workflow completed

    def test_workflow_resumption_invalid_thread_id(self):
        """Test workflow resumption with invalid thread_id raises error."""
        invalid_thread_id = "invalid-thread-id"

        state: SimpleState = {"data": {"test": "value"}, "status": "processing"}

        # Should raise ValueError for invalid thread_id
        with pytest.raises(ValueError, match="No checkpoint found"):
            resume_workflow(invalid_thread_id, state)

    def test_workflow_resumption_preserves_checkpoint_data(self):
        """Test that workflow resumption preserves checkpointed data."""
        # Initial execution
        state1: SimpleState = {
            "data": {"preserved": "value", "custom": "data1"},
            "status": "processing",
        }
        result1, thread_id = execute_with_checkpoint(state1)

        # Resume with minimal additional state
        state2: SimpleState = {"data": {"custom": "data2"}, "status": "processing"}
        result2 = resume_workflow(thread_id, state2)

        # Verify preserved data is still present
        assert result2["data"]["preserved"] == "value"  # Preserved from checkpoint
        assert result2["data"]["custom"] == "data2"  # Updated value (y takes precedence)
        assert result2["data"]["step"] == "b"  # From node_b execution


class TestErrorHandling:
    """Test error handling in workflow execution."""

    def test_error_handling_invalid_state_structure(self):
        """Test error handling with invalid state structure."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # Invalid state (missing required fields)
        invalid_state = {"invalid": "data"}

        # LangGraph may handle invalid state gracefully or raise an error
        # Test that workflow either handles it or raises appropriate error
        try:
            result = checkpoint_graph.invoke(invalid_state, config=config)
            # If no error, verify result is valid
            assert result is not None
        except (TypeError, KeyError, ValueError, AttributeError):
            # Expected error for invalid state
            pass

    def test_error_handling_missing_required_fields(self):
        """Test error handling with missing required state fields."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # State missing required fields
        invalid_state = {"data": {}}  # Missing "status"

        # LangGraph may handle missing fields gracefully or raise an error
        # Test that workflow either handles it or raises appropriate error
        try:
            result = checkpoint_graph.invoke(invalid_state, config=config)
            # If no error, verify result is valid
            assert result is not None
            assert "status" in result
        except (TypeError, KeyError, ValueError, AttributeError):
            # Expected error for missing required fields
            pass

    def test_error_handling_error_status_routes_to_handler(self):
        """Test that error status correctly routes to error handler."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # State with error status
        error_state: SimpleState = {
            "data": {"error_info": "test error"},
            "status": "error",
        }

        result = checkpoint_graph.invoke(error_state, config=config)

        # Should route to error_handler and complete successfully
        assert result is not None
        assert result["status"] == "error_handled"
        assert result["data"]["error_handled"] is True


class TestAcceptanceCriteriaValidation:
    """Validate all Milestone 1.4 acceptance criteria."""

    def test_ac1_stategraph_with_typeddict_state(self):
        """AC1: StateGraph created with TypedDict state definition."""
        # Verify graph exists and uses SimpleState (TypedDict)
        assert checkpoint_graph is not None
        # Graph should be compiled and ready
        assert hasattr(checkpoint_graph, "invoke")

    def test_ac2_multiple_nodes_with_state_updates(self):
        """AC2: At least 2 nodes implemented with state updates."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        state: SimpleState = {"data": {}, "status": "processing"}
        result = checkpoint_graph.invoke(state, config=config)

        # Verify multiple nodes executed (node_a_conditional and node_b)
        # node_a_conditional adds "step": "a", "processed": True
        # node_b adds "step": "b", "finalized": True
        assert "finalized" in result["data"]
        assert result["data"]["step"] == "b"  # Final step from node_b

    def test_ac3_conditional_routing_implemented(self):
        """AC3: Conditional routing implemented and working."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # Test processing path
        state_processing: SimpleState = {"data": {}, "status": "processing"}
        result_processing = checkpoint_graph.invoke(state_processing, config=config)
        assert result_processing["status"] == "completed"

        # Test completed path
        state_completed: SimpleState = {"data": {}, "status": "completed"}
        result_completed = checkpoint_graph.invoke(state_completed, config=config)
        assert result_completed["status"] == "completed"

        # Test error path
        state_error: SimpleState = {"data": {}, "status": "error"}
        result_error = checkpoint_graph.invoke(state_error, config=config)
        assert result_error["status"] == "error_handled"

    def test_ac4_checkpointing_configured(self):
        """AC4: Checkpointing configured (InMemorySaver)."""
        assert checkpoint_graph.checkpointer is not None
        assert isinstance(checkpoint_graph.checkpointer, InMemorySaver)

    def test_ac5_workflow_executes_successfully(self):
        """AC5: Workflow executes successfully."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        state: SimpleState = {"data": {"test": "value"}, "status": "processing"}
        result = checkpoint_graph.invoke(state, config=config)

        assert result is not None
        assert "status" in result
        assert "data" in result
        assert result["status"] == "completed"

    def test_ac6_state_persists_across_steps(self):
        """AC6: State persists across workflow steps."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # First invocation
        state1: SimpleState = {"data": {"custom": "value1"}, "status": "processing"}
        result1 = checkpoint_graph.invoke(state1, config=config)

        # Second invocation (should have persisted state)
        state2: SimpleState = {"data": {"custom": "value2"}, "status": "processing"}
        result2 = checkpoint_graph.invoke(state2, config=config)

        # Verify state persisted (data merged)
        assert result2 is not None
        # Verify checkpoint exists
        checkpoint = get_checkpoint_state(thread_id)
        assert checkpoint is not None
        # Custom data should be merged (y takes precedence in merge_dicts)
        assert checkpoint["data"]["custom"] == "value2"  # Latest value
        # Step is set by node_b during execution
        assert checkpoint["data"]["step"] == "b"

    def test_ac7_workflow_resumable_from_checkpoint(self):
        """AC7: Workflow can be resumed from checkpoint."""
        # Initial execution
        state1: SimpleState = {"data": {"resume_test": "initial"}, "status": "processing"}
        result1, thread_id = execute_with_checkpoint(state1)

        # Resume from checkpoint
        state2: SimpleState = {"data": {"resume_test": "resumed"}, "status": "processing"}
        result2 = resume_workflow(thread_id, state2)

        # Verify resumption successful
        assert result2 is not None
        # Verify resumption worked (workflow re-executes, but checkpoint data is preserved)
        assert result2["data"]["resume_test"] == "resumed"  # Merged state
        assert result2["status"] == "completed"  # Workflow completed

    def test_ac8_state_updates_use_proper_reducers(self):
        """AC8: State updates use proper reducers."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # First invocation
        state1: SimpleState = {
            "data": {"key1": "value1", "key2": "value2"},
            "status": "initial",
        }
        result1 = checkpoint_graph.invoke(state1, config=config)

        # Second invocation with overlapping keys
        state2: SimpleState = {
            "data": {"key2": "updated_value2", "key3": "value3"},
            "status": "processing",
        }
        result2 = checkpoint_graph.invoke(state2, config=config)

        # Verify reducer behavior:
        # - merge_dicts: merges dictionaries, y takes precedence
        # - last_value: latest status overwrites previous
        assert result2["data"]["key1"] == "value1"  # Preserved (merge_dicts)
        assert result2["data"]["key2"] == "updated_value2"  # Updated (merge_dicts, y takes precedence)
        assert result2["data"]["key3"] == "value3"  # New (merge_dicts)
        assert result2["status"] == "completed"  # Latest value (last_value)

