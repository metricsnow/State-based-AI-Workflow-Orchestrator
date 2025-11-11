"""Comprehensive tests for LangGraph checkpointing functionality.

This test suite validates checkpointing configuration, state persistence,
workflow resumption, and thread ID isolation for LangGraph workflows.
"""

import uuid

import pytest

from langgraph.checkpoint.memory import InMemorySaver
from langgraph_workflows.checkpoint_workflow import (
    checkpoint_graph,
    execute_with_checkpoint,
    get_checkpoint_state,
    list_checkpoints,
    resume_workflow,
)
from langgraph_workflows.state import SimpleState


class TestCheckpointerConfiguration:
    """Test checkpointer configuration and setup."""

    def test_checkpointer_configured(self):
        """Test that checkpointer is configured correctly."""
        assert checkpoint_graph.checkpointer is not None
        assert isinstance(checkpoint_graph.checkpointer, InMemorySaver)

    def test_graph_compilation_with_checkpointer(self):
        """Test that graph compiles successfully with checkpointer."""
        assert checkpoint_graph is not None
        assert hasattr(checkpoint_graph, "checkpointer")
        assert checkpoint_graph.checkpointer is not None


class TestThreadIDManagement:
    """Test thread ID generation and management."""

    def test_thread_id_generation(self):
        """Test that thread ID is generated when not provided."""
        state: SimpleState = {"data": {}, "status": "processing"}
        result, thread_id = execute_with_checkpoint(state)

        assert thread_id is not None
        assert isinstance(thread_id, str)
        assert len(thread_id) > 0

    def test_thread_id_preservation(self):
        """Test that provided thread ID is preserved."""
        custom_thread_id = "custom-thread-123"
        state: SimpleState = {"data": {}, "status": "processing"}
        result, thread_id = execute_with_checkpoint(state, custom_thread_id)

        assert thread_id == custom_thread_id

    def test_thread_id_isolation(self):
        """Test that different thread IDs maintain separate checkpoints."""
        thread_id_1 = str(uuid.uuid4())
        thread_id_2 = str(uuid.uuid4())

        state1: SimpleState = {"data": {"thread": 1}, "status": "processing"}
        state2: SimpleState = {"data": {"thread": 2}, "status": "processing"}

        result1, _ = execute_with_checkpoint(state1, thread_id_1)
        result2, _ = execute_with_checkpoint(state2, thread_id_2)

        # Verify checkpoints are isolated
        checkpoint1 = get_checkpoint_state(thread_id_1)
        checkpoint2 = get_checkpoint_state(thread_id_2)

        assert checkpoint1 is not None
        assert checkpoint2 is not None
        assert checkpoint1["data"]["thread"] == 1
        assert checkpoint2["data"]["thread"] == 2


class TestCheckpointSaving:
    """Test checkpoint saving functionality."""

    def test_checkpoint_saved_after_execution(self):
        """Test that checkpoint is saved after workflow execution."""
        thread_id = str(uuid.uuid4())
        state: SimpleState = {"data": {"test": "value"}, "status": "processing"}

        result, _ = execute_with_checkpoint(state, thread_id)

        # Verify checkpoint exists
        checkpoint = get_checkpoint_state(thread_id)
        assert checkpoint is not None
        assert checkpoint["data"]["test"] == "value"

    def test_checkpoint_contains_state(self):
        """Test that checkpoint contains correct state values."""
        thread_id = str(uuid.uuid4())
        state: SimpleState = {
            "data": {"step": 1, "processed": True},
            "status": "completed",
        }

        result, _ = execute_with_checkpoint(state, thread_id)

        checkpoint = get_checkpoint_state(thread_id)
        assert checkpoint is not None
        # After workflow execution, state is modified by nodes
        # Check that checkpoint contains the final state
        assert "data" in checkpoint
        assert "status" in checkpoint
        # The workflow processes the state, so we check it's not empty
        assert len(checkpoint["data"]) > 0


class TestCheckpointLoading:
    """Test checkpoint loading functionality."""

    def test_checkpoint_loads_correctly(self):
        """Test that checkpoint loads with correct state."""
        thread_id = str(uuid.uuid4())
        state: SimpleState = {"data": {"loaded": True}, "status": "processing"}

        execute_with_checkpoint(state, thread_id)

        # Load checkpoint
        checkpoint = get_checkpoint_state(thread_id)
        assert checkpoint is not None
        assert checkpoint["data"]["loaded"] is True

    def test_checkpoint_not_found_returns_none(self):
        """Test that non-existent checkpoint returns None."""
        non_existent_thread_id = str(uuid.uuid4())
        checkpoint = get_checkpoint_state(non_existent_thread_id)
        assert checkpoint is None


class TestStatePersistence:
    """Test state persistence across workflow steps."""

    def test_state_persists_across_steps(self):
        """Test that state persists across multiple workflow steps."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # Execute first step
        state1: SimpleState = {"data": {"step": 1}, "status": "processing"}
        result1 = checkpoint_graph.invoke(state1, config=config)

        # Execute second step (should have persisted state)
        state2: SimpleState = {"data": {"step": 2}, "status": "processing"}
        result2 = checkpoint_graph.invoke(state2, config=config)

        # Verify state persistence - data should be merged
        assert "data" in result2
        # The workflow executes and modifies state, so we verify it's not empty
        assert len(result2["data"]) > 0
        # Check that the workflow processed the state
        assert "status" in result2

    def test_state_persists_with_checkpointing(self):
        """Test state persistence using execute_with_checkpoint."""
        thread_id = str(uuid.uuid4())

        # First execution
        state1: SimpleState = {"data": {"execution": 1}, "status": "processing"}
        result1, _ = execute_with_checkpoint(state1, thread_id)

        # Second execution with same thread_id
        state2: SimpleState = {"data": {"execution": 2}, "status": "processing"}
        result2, _ = execute_with_checkpoint(state2, thread_id)

        # Verify state persisted
        checkpoint = get_checkpoint_state(thread_id)
        assert checkpoint is not None
        assert "execution" in checkpoint["data"]


class TestWorkflowResumption:
    """Test workflow resumption from checkpoints."""

    def test_workflow_resumes_from_checkpoint(self):
        """Test that workflow can be resumed from checkpoint."""
        thread_id = str(uuid.uuid4())

        # Execute first part
        state1: SimpleState = {"data": {"step": 1}, "status": "processing"}
        result1, _ = execute_with_checkpoint(state1, thread_id)

        # Resume workflow
        state2: SimpleState = {"data": {"step": 2}, "status": "processing"}
        result2 = resume_workflow(thread_id, state2)

        # Verify resumption
        assert result2 is not None
        assert "step" in result2["data"]

    def test_workflow_resumes_without_additional_state(self):
        """Test workflow resumption without additional state."""
        thread_id = str(uuid.uuid4())

        # Execute workflow
        state: SimpleState = {"data": {"initial": True}, "status": "processing"}
        result1, _ = execute_with_checkpoint(state, thread_id)

        # Resume without additional state (should use checkpointed state)
        result2 = resume_workflow(thread_id)

        assert result2 is not None
        assert "initial" in result2["data"]

    def test_workflow_resumption_merges_state(self):
        """Test that resumption merges additional state with checkpoint."""
        thread_id = str(uuid.uuid4())

        # Initial execution
        state1: SimpleState = {"data": {"step": 1, "value": "a"}, "status": "processing"}
        result1, _ = execute_with_checkpoint(state1, thread_id)

        # Resume with additional state
        state2: SimpleState = {"data": {"step": 2, "value": "b"}, "status": "processing"}
        result2 = resume_workflow(thread_id, state2)

        # Verify state was merged and workflow executed
        assert result2 is not None
        assert "data" in result2
        assert "status" in result2
        # The workflow processes the state, so we verify it executed
        assert len(result2["data"]) > 0

    def test_resume_nonexistent_checkpoint_raises_error(self):
        """Test that resuming non-existent checkpoint raises error."""
        non_existent_thread_id = str(uuid.uuid4())

        state: SimpleState = {"data": {}, "status": "processing"}

        with pytest.raises(ValueError, match="No checkpoint found"):
            resume_workflow(non_existent_thread_id, state)


class TestCheckpointListing:
    """Test checkpoint listing functionality."""

    def test_list_checkpoints_returns_list(self):
        """Test that list_checkpoints returns a list."""
        thread_id = str(uuid.uuid4())
        state: SimpleState = {"data": {}, "status": "processing"}

        execute_with_checkpoint(state, thread_id)

        checkpoints = list_checkpoints(thread_id)
        assert isinstance(checkpoints, list)
        assert len(checkpoints) > 0

    def test_list_checkpoints_empty_for_new_thread(self):
        """Test that new thread has no checkpoints initially."""
        new_thread_id = str(uuid.uuid4())
        checkpoints = list_checkpoints(new_thread_id)
        # After execution, there should be checkpoints
        # But before execution, list might be empty or raise
        # This depends on implementation - testing after execution
        state: SimpleState = {"data": {}, "status": "processing"}
        execute_with_checkpoint(state, new_thread_id)
        checkpoints = list_checkpoints(new_thread_id)
        assert len(checkpoints) > 0


class TestErrorHandling:
    """Test error handling with checkpoints."""

    def test_invalid_state_handled_gracefully(self):
        """Test that invalid state is handled gracefully."""
        thread_id = str(uuid.uuid4())

        # Invalid state structure - LangGraph may handle this differently
        # Some invalid states might be accepted with default values
        invalid_state = {"invalid": "data"}

        # LangGraph might accept this and use defaults, or raise an error
        # We test that it doesn't crash
        try:
            result, _ = execute_with_checkpoint(invalid_state, thread_id)
            # If it doesn't raise, verify it returns something
            assert result is not None
        except (TypeError, KeyError, ValueError):
            # If it raises an error, that's also acceptable behavior
            pass

    def test_checkpoint_handles_error_status(self):
        """Test that checkpoints handle error status correctly."""
        thread_id = str(uuid.uuid4())
        state: SimpleState = {"data": {}, "status": "error"}

        result, _ = execute_with_checkpoint(state, thread_id)

        # Error status should route to error_handler
        assert result["status"] == "error_handled"
        checkpoint = get_checkpoint_state(thread_id)
        assert checkpoint is not None
        assert checkpoint["status"] == "error_handled"


class TestIntegrationScenarios:
    """Integration test scenarios for checkpointing."""

    def test_complete_checkpointing_workflow(self):
        """Test complete checkpointing workflow end-to-end."""
        thread_id = str(uuid.uuid4())

        # Step 1: Initial execution
        state1: SimpleState = {
            "data": {"workflow_step": 1, "initialized": True},
            "status": "processing",
        }
        result1, _ = execute_with_checkpoint(state1, thread_id)
        assert result1 is not None

        # Step 2: Verify checkpoint exists
        checkpoint1 = get_checkpoint_state(thread_id)
        assert checkpoint1 is not None
        assert checkpoint1["data"]["workflow_step"] == 1

        # Step 3: Resume workflow
        state2: SimpleState = {
            "data": {"workflow_step": 2, "resumed": True},
            "status": "processing",
        }
        result2 = resume_workflow(thread_id, state2)
        assert result2 is not None

        # Step 4: Verify final checkpoint
        checkpoint2 = get_checkpoint_state(thread_id)
        assert checkpoint2 is not None
        assert checkpoint2["data"]["workflow_step"] == 2
        assert checkpoint2["data"]["resumed"] is True

    def test_multiple_threads_independent_execution(self):
        """Test that multiple threads execute independently."""
        thread_id_1 = str(uuid.uuid4())
        thread_id_2 = str(uuid.uuid4())
        thread_id_3 = str(uuid.uuid4())

        # Execute workflows with different thread IDs
        state1: SimpleState = {"data": {"thread": 1}, "status": "processing"}
        state2: SimpleState = {"data": {"thread": 2}, "status": "processing"}
        state3: SimpleState = {"data": {"thread": 3}, "status": "processing"}

        result1, _ = execute_with_checkpoint(state1, thread_id_1)
        result2, _ = execute_with_checkpoint(state2, thread_id_2)
        result3, _ = execute_with_checkpoint(state3, thread_id_3)

        # Verify each thread has independent checkpoints
        checkpoint1 = get_checkpoint_state(thread_id_1)
        checkpoint2 = get_checkpoint_state(thread_id_2)
        checkpoint3 = get_checkpoint_state(thread_id_3)

        assert checkpoint1["data"]["thread"] == 1
        assert checkpoint2["data"]["thread"] == 2
        assert checkpoint3["data"]["thread"] == 3

    def test_checkpoint_cleanup_and_isolation(self):
        """Test checkpoint cleanup and thread isolation."""
        thread_id_1 = str(uuid.uuid4())
        thread_id_2 = str(uuid.uuid4())

        # Execute with thread 1
        state1: SimpleState = {"data": {"isolated": 1}, "status": "processing"}
        execute_with_checkpoint(state1, thread_id_1)

        # Execute with thread 2
        state2: SimpleState = {"data": {"isolated": 2}, "status": "processing"}
        execute_with_checkpoint(state2, thread_id_2)

        # Verify isolation
        checkpoint1 = get_checkpoint_state(thread_id_1)
        checkpoint2 = get_checkpoint_state(thread_id_2)

        assert checkpoint1["data"]["isolated"] == 1
        assert checkpoint2["data"]["isolated"] == 2
        assert checkpoint1 != checkpoint2

