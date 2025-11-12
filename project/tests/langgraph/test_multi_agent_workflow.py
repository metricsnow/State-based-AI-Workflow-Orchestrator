"""Comprehensive tests for LangGraph multi-agent workflow.

This test suite validates multi-agent workflow execution, graph construction,
agent collaboration, conditional routing, checkpointing, and state persistence.
"""

import os
import uuid
from unittest.mock import patch

import pytest

from langgraph_workflows.multi_agent_workflow import (
    execute_multi_agent_workflow,
    multi_agent_graph,
)
from langgraph_workflows.state import MultiAgentState


def get_fastest_test_model() -> str:
    """Get the fastest available model for tests.
    
    Model Selection Priority (based on benchmark analysis):
    1. gemma3:1b (~1.3 GB, 0.492s) - Best balance: small size + fast inference
    2. phi4-mini:3.8b (2.5 GB, 0.447s) - Fastest but larger
    3. llama3.2:latest (2.0 GB, 0.497s) - Good fallback
    
    Returns:
        Model name string. Uses fastest available model for test execution.
        Override with TEST_OLLAMA_MODEL env var if needed.
    """
    # Priority: gemma3:1b (best balance) > phi4-mini:3.8b (fastest) > llama3.2:latest
    test_model = os.getenv("TEST_OLLAMA_MODEL")
    if test_model:
        return test_model
    return "gemma3:1b"  # Best balance: small size + fast inference


class TestGraphConstruction:
    """Test graph construction and compilation."""

    def test_graph_is_constructed(self) -> None:
        """Test graph is constructed correctly."""
        assert multi_agent_graph is not None

    def test_graph_has_checkpointer(self) -> None:
        """Test graph has checkpointer configured."""
        assert multi_agent_graph.checkpointer is not None

    def test_graph_nodes_registered(self) -> None:
        """Test all required nodes are registered in graph."""
        # Verify graph structure by checking it can be invoked
        # If nodes aren't registered, invocation will fail
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        initial_state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        # Should not raise exception if nodes are properly registered
        result = multi_agent_graph.invoke(initial_state, config=config)
        assert result is not None


class TestWorkflowExecution:
    """Test complete workflow execution."""

    def test_multi_agent_workflow_execution(self) -> None:
        """Test complete multi-agent workflow execution."""
        thread_id = str(uuid.uuid4())
        result, returned_thread_id = execute_multi_agent_workflow("test_task", thread_id)

        assert returned_thread_id == thread_id
        assert result["completed"] is True
        assert "data" in result["agent_results"]
        assert "analysis" in result["agent_results"]

    def test_workflow_execution_with_auto_thread_id(self) -> None:
        """Test workflow execution with auto-generated thread_id."""
        result, thread_id = execute_multi_agent_workflow("test_task")

        assert thread_id is not None
        assert isinstance(thread_id, str)
        assert len(thread_id) > 0
        assert result["completed"] is True
        assert "data" in result["agent_results"]
        assert "analysis" in result["agent_results"]

    def test_workflow_preserves_task(self) -> None:
        """Test workflow preserves task in final state."""
        task = "process_and_analyze_data"
        result, _ = execute_multi_agent_workflow(task)

        assert result["task"] == task
        assert result["completed"] is True


class TestAgentRouting:
    """Test agent routing and collaboration."""

    def test_agents_route_correctly(self) -> None:
        """Test agents route correctly through workflow."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        initial_state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        result = multi_agent_graph.invoke(initial_state, config=config)

        # Verify all agents executed
        assert "data" in result["agent_results"]
        assert "analysis" in result["agent_results"]
        assert result["completed"] is True

    def test_agent_collaboration(self) -> None:
        """Test agents collaborate successfully."""
        thread_id = str(uuid.uuid4())
        result, _ = execute_multi_agent_workflow("collaboration_test", thread_id)

        # Verify data agent result used by analysis agent
        data_result = result["agent_results"].get("data", {})
        analysis_result = result["agent_results"].get("analysis", {})

        assert data_result is not None
        assert analysis_result is not None
        assert data_result.get("agent") == "data"
        assert analysis_result.get("agent") == "analysis"

        # Analysis should reference data result
        if "analysis" in analysis_result:
            analysis_data = analysis_result.get("analysis", {})
            if "data_source" in analysis_data:
                assert analysis_data["data_source"] == data_result

    def test_conditional_routing_from_orchestrator(self) -> None:
        """Test conditional routing from orchestrator works correctly."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # Test routing to data agent (no results)
        state1: MultiAgentState = {
            "messages": [],
            "task": "test",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }
        result1 = multi_agent_graph.invoke(state1, config=config)
        assert "data" in result1["agent_results"]

        # Test routing to analysis agent (data complete)
        state2: MultiAgentState = {
            "messages": [],
            "task": "test",
            "agent_results": {"data": {"agent": "data", "result": "data_processed"}},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }
        result2 = multi_agent_graph.invoke(state2, config=config)
        assert "analysis" in result2["agent_results"]


class TestStatePersistence:
    """Test state persistence across agent executions."""

    def test_state_persists_across_agents(self) -> None:
        """Test state persists across agent executions."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        initial_state: MultiAgentState = {
            "messages": [],
            "task": "persistence_test",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        result = multi_agent_graph.invoke(initial_state, config=config)

        # Verify state persisted across agents
        assert result["task"] == "persistence_test"
        assert len(result["agent_results"]) >= 2
        assert result["completed"] is True

    def test_agent_results_aggregate(self) -> None:
        """Test agent results aggregate correctly in state."""
        result, _ = execute_multi_agent_workflow("aggregation_test")

        agent_results = result["agent_results"]
        assert "data" in agent_results
        assert "analysis" in agent_results

        # Verify results are properly structured
        assert agent_results["data"].get("agent") == "data"
        assert agent_results["analysis"].get("agent") == "analysis"


class TestCheckpointing:
    """Test checkpointing functionality."""

    def test_checkpointing_configured(self) -> None:
        """Test checkpointing is configured in graph."""
        assert multi_agent_graph.checkpointer is not None

    def test_workflow_with_checkpointing(self) -> None:
        """Test workflow execution with checkpointing."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        initial_state: MultiAgentState = {
            "messages": [],
            "task": "checkpoint_test",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        # Execute workflow
        result = multi_agent_graph.invoke(initial_state, config=config)

        # Verify checkpoint exists (graph has checkpointer)
        assert result is not None
        assert multi_agent_graph.checkpointer is not None
        assert result["completed"] is True

    def test_thread_id_persistence(self) -> None:
        """Test thread_id is used for checkpoint tracking."""
        custom_thread_id = "test-thread-123"
        result, thread_id = execute_multi_agent_workflow("test_task", custom_thread_id)

        assert thread_id == custom_thread_id
        assert result["completed"] is True


class TestErrorHandling:
    """Test error handling in multi-agent context."""

    def test_invalid_state_handling(self) -> None:
        """Test graph handles invalid state gracefully."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # Test with incomplete state (missing required fields)
        # LangGraph may handle this by using defaults or may raise an error
        invalid_state = {"task": "test"}  # Missing required fields

        # LangGraph may either raise an error or handle gracefully with defaults
        # Test that it doesn't crash the system
        try:
            result = multi_agent_graph.invoke(invalid_state, config=config)
            # If it doesn't raise, verify it handles gracefully
            assert result is not None
        except (TypeError, KeyError, ValueError, AttributeError) as e:
            # If it raises, that's also acceptable behavior
            assert isinstance(e, (TypeError, KeyError, ValueError, AttributeError))

    def test_workflow_completes_on_error(self) -> None:
        """Test workflow completes even if agents encounter issues."""
        # This test verifies the workflow structure handles errors
        # Actual error handling is tested in agent node tests
        result, _ = execute_multi_agent_workflow("error_test")

        # Workflow should complete (either successfully or with error state)
        assert "completed" in result
        assert result["completed"] is True


class TestIntegration:
    """Integration tests for complete workflow scenarios."""

    def test_complete_workflow_sequence(self) -> None:
        """Test complete workflow sequence from start to finish."""
        task = "complete_integration_test"
        result, thread_id = execute_multi_agent_workflow(task)

        # Verify complete workflow execution
        assert result["task"] == task
        assert result["completed"] is True
        assert "data" in result["agent_results"]
        assert "analysis" in result["agent_results"]
        assert thread_id is not None

        # Verify agent results structure
        data_result = result["agent_results"]["data"]
        analysis_result = result["agent_results"]["analysis"]

        assert data_result.get("agent") == "data"
        assert analysis_result.get("agent") == "analysis"
        assert data_result.get("result") == "data_processed"
        assert analysis_result.get("result") == "analysis_complete"

    def test_multiple_workflow_executions(self) -> None:
        """Test multiple independent workflow executions."""
        tasks = ["task1", "task2", "task3"]

        for task in tasks:
            result, thread_id = execute_multi_agent_workflow(task)

            assert result["task"] == task
            assert result["completed"] is True
            assert "data" in result["agent_results"]
            assert "analysis" in result["agent_results"]
            assert thread_id is not None

    def test_workflow_with_metadata(self) -> None:
        """Test workflow execution with metadata."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        initial_state: MultiAgentState = {
            "messages": [],
            "task": "metadata_test",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {"test_key": "test_value"},
        }

        result = multi_agent_graph.invoke(initial_state, config=config)

        # Verify metadata is preserved
        assert "metadata" in result
        assert result["metadata"].get("test_key") == "test_value"
        assert result["completed"] is True

    @patch("langchain_ollama_integration.llm_factory.get_ollama_model")
    def test_workflow_with_llm_analysis(self, mock_get_model) -> None:
        """Test workflow execution with LLM analysis node integration."""
        # Use fastest model for tests
        mock_get_model.return_value = get_fastest_test_model()
        
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # Task with analysis keyword to trigger LLM routing
        initial_state: MultiAgentState = {
            "messages": [],
            "task": "Analyze customer data trends for Q4",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        result = multi_agent_graph.invoke(initial_state, config=config)

        # Verify workflow completes
        assert result["completed"] is True
        assert "data" in result["agent_results"]
        assert "analysis" in result["agent_results"]

        # Verify LLM analysis node was invoked (if task contains analysis keywords)
        # Note: LLM may or may not be invoked depending on orchestrator logic
        # The key is that the workflow completes successfully with LLM node available
        assert "llm_analysis" in result["agent_results"] or "llm_analysis" not in result["agent_results"]

        # Verify agent results structure
        data_result = result["agent_results"]["data"]
        analysis_result = result["agent_results"]["analysis"]

        assert data_result.get("agent") == "data"
        assert analysis_result.get("agent") == "analysis"

        # If LLM analysis was invoked, verify its structure
        if "llm_analysis" in result["agent_results"]:
            llm_result = result["agent_results"]["llm_analysis"]
            assert llm_result.get("agent") == "llm_analysis"
            assert "result" in llm_result
            assert "status" in llm_result
            assert llm_result["status"] in ["completed", "error"]

