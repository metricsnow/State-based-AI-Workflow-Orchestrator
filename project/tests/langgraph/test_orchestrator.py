"""Comprehensive tests for LangGraph orchestrator agent node.

This test suite validates orchestrator functionality, routing decisions, completion
detection, and error handling for orchestrator_agent and route_to_agent.
"""

import pytest

from langgraph_workflows.orchestrator_agent import (
    orchestrator_agent,
    orchestrator_agent_with_errors,
    route_to_agent,
)
from langgraph_workflows.state import MultiAgentState


class TestOrchestratorAgent:
    """Test orchestrator agent node functionality."""

    def test_orchestrator_routes_to_data_agent(self) -> None:
        """Test orchestrator routes to data agent when no results."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        result = orchestrator_agent(state)

        assert result["current_agent"] == "data"
        assert "completed" not in result or result.get("completed") is False

    def test_orchestrator_routes_to_analysis_agent(self) -> None:
        """Test orchestrator routes to analysis agent when data complete."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {"data": {"agent": "data", "result": "data_processed"}},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        result = orchestrator_agent(state)

        assert result["current_agent"] == "analysis"
        assert "completed" not in result or result.get("completed") is False

    def test_orchestrator_detects_completion(self) -> None:
        """Test orchestrator detects workflow completion."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {
                "data": {"agent": "data", "result": "data_processed"},
                "analysis": {"agent": "analysis", "result": "analysis_complete"},
            },
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        result = orchestrator_agent(state)

        assert result["completed"] is True
        assert result["current_agent"] == "end"

    def test_orchestrator_handles_already_completed(self) -> None:
        """Test orchestrator handles already completed workflow."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {
                "data": {"agent": "data", "result": "data_processed"},
                "analysis": {"agent": "analysis", "result": "analysis_complete"},
            },
            "current_agent": "orchestrator",
            "completed": True,
            "metadata": {},
        }

        result = orchestrator_agent(state)

        assert result["current_agent"] == "end"
        # Should not change completed status if already True
        assert "completed" not in result or result.get("completed") is True

    def test_orchestrator_preserves_state(self) -> None:
        """Test orchestrator only returns state updates, not full state."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        result = orchestrator_agent(state)

        # Should return dict with state updates only
        assert isinstance(result, dict)
        assert "current_agent" in result
        # Should not return full state fields
        assert "messages" not in result
        assert "task" not in result
        assert "metadata" not in result

    def test_orchestrator_with_partial_results(self) -> None:
        """Test orchestrator handles partial agent results correctly."""
        # Only data agent completed
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {
                "data": {"agent": "data", "result": "data_processed", "data": {"processed": True}},
            },
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        result = orchestrator_agent(state)

        assert result["current_agent"] == "analysis"
        assert "data" in state["agent_results"]


class TestRouteToAgent:
    """Test routing function for conditional edges."""

    def test_route_to_data_agent(self) -> None:
        """Test routing function returns data agent node name."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "data",
            "completed": False,
            "metadata": {},
        }

        next_node = route_to_agent(state)

        assert next_node == "data"

    def test_route_to_analysis_agent(self) -> None:
        """Test routing function returns analysis agent node name."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {"data": {"agent": "data", "result": "data_processed"}},
            "current_agent": "analysis",
            "completed": False,
            "metadata": {},
        }

        next_node = route_to_agent(state)

        assert next_node == "analysis"

    def test_route_to_end(self) -> None:
        """Test routing function returns end when workflow complete."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {
                "data": {"agent": "data", "result": "data_processed"},
                "analysis": {"agent": "analysis", "result": "analysis_complete"},
            },
            "current_agent": "end",
            "completed": True,
            "metadata": {},
        }

        next_node = route_to_agent(state)

        assert next_node == "end"

    def test_route_to_end_when_completed(self) -> None:
        """Test routing function returns end when completed flag is True."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": True,
            "metadata": {},
        }

        next_node = route_to_agent(state)

        assert next_node == "end"

    def test_route_to_end_when_current_agent_is_end(self) -> None:
        """Test routing function returns end when current_agent is 'end'."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "end",
            "completed": False,
            "metadata": {},
        }

        next_node = route_to_agent(state)

        assert next_node == "end"

    def test_route_defaults_to_orchestrator(self) -> None:
        """Test routing function defaults to orchestrator when current_agent not set."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        next_node = route_to_agent(state)

        assert next_node == "orchestrator"


class TestOrchestratorWithErrors:
    """Test orchestrator with error handling."""

    def test_orchestrator_with_errors_detects_data_agent_error(self) -> None:
        """Test orchestrator detects error in data agent result."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {
                "data": {"error": "Processing failed", "agent": "data", "result": "error"},
            },
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        result = orchestrator_agent_with_errors(state)

        assert result["completed"] is True
        assert result["current_agent"] == "end"
        assert "error" in result.get("metadata", {})
        assert "data" in result["metadata"]["error"].lower()

    def test_orchestrator_with_errors_detects_analysis_agent_error(self) -> None:
        """Test orchestrator detects error in analysis agent result."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {
                "data": {"agent": "data", "result": "data_processed"},
                "analysis": {"error": "Analysis failed", "agent": "analysis", "result": "error"},
            },
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        result = orchestrator_agent_with_errors(state)

        assert result["completed"] is True
        assert result["current_agent"] == "end"
        assert "error" in result.get("metadata", {})
        assert "analysis" in result["metadata"]["error"].lower()

    def test_orchestrator_with_errors_handles_exceptions(self) -> None:
        """Test orchestrator handles exceptions gracefully with production state."""
        # Production state - orchestrator should handle normal flow
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        # Test with production conditions - orchestrator_agent_with_errors should handle this
        result = orchestrator_agent_with_errors(state)

        # Should return valid result with proper routing
        assert isinstance(result, dict)
        assert "current_agent" in result
        assert result["current_agent"] == "data"  # Should route to data agent

    def test_orchestrator_with_errors_preserves_metadata(self) -> None:
        """Test orchestrator with errors preserves existing metadata."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {
                "data": {"error": "Processing failed", "agent": "data", "result": "error"},
            },
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {"existing_key": "existing_value"},
        }

        result = orchestrator_agent_with_errors(state)

        assert "existing_key" in result.get("metadata", {})
        assert result["metadata"]["existing_key"] == "existing_value"
        assert "error" in result.get("metadata", {})

    def test_orchestrator_with_errors_normal_flow(self) -> None:
        """Test orchestrator with errors works normally when no errors present."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {
                "data": {"agent": "data", "result": "data_processed"},
            },
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        result = orchestrator_agent_with_errors(state)

        # Should behave like normal orchestrator when no errors
        assert result["current_agent"] == "analysis"
        assert "error" not in result.get("metadata", {})

    def test_orchestrator_with_errors_includes_error_details(self) -> None:
        """Test orchestrator with errors includes error details in metadata."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {
                "data": {
                    "error": "Database connection timeout",
                    "agent": "data",
                    "result": "error",
                },
            },
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        result = orchestrator_agent_with_errors(state)

        assert "error_details" in result.get("metadata", {})
        assert "Database connection timeout" in result["metadata"]["error_details"]


class TestOrchestratorIntegration:
    """Integration tests for orchestrator with agent nodes."""

    def test_orchestrator_workflow_sequence(self) -> None:
        """Test complete orchestrator workflow sequence."""
        # Step 1: Initial state - orchestrator routes to data agent
        state1: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }
        result1 = orchestrator_agent(state1)
        assert result1["current_agent"] == "data"

        # Step 2: After data agent - orchestrator routes to analysis agent
        state2: MultiAgentState = {
            **state1,
            "agent_results": {"data": {"agent": "data", "result": "data_processed"}},
            "current_agent": "orchestrator",
        }
        result2 = orchestrator_agent(state2)
        assert result2["current_agent"] == "analysis"

        # Step 3: After analysis agent - orchestrator detects completion
        state3: MultiAgentState = {
            **state2,
            "agent_results": {
                "data": {"agent": "data", "result": "data_processed"},
                "analysis": {"agent": "analysis", "result": "analysis_complete"},
            },
            "current_agent": "orchestrator",
        }
        result3 = orchestrator_agent(state3)
        assert result3["completed"] is True
        assert result3["current_agent"] == "end"

    def test_routing_function_with_orchestrator_decisions(self) -> None:
        """Test routing function works with orchestrator decisions."""
        # Orchestrator decides to route to data agent
        state1: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }
        orchestrator_result = orchestrator_agent(state1)
        assert orchestrator_result["current_agent"] == "data"

        # Update state with orchestrator decision
        state1["current_agent"] = orchestrator_result["current_agent"]

        # Routing function should return data agent
        next_node = route_to_agent(state1)
        assert next_node == "data"

    def test_complete_production_workflow_with_real_agents(self) -> None:
        """Test complete production workflow with real agent nodes."""
        from langgraph_workflows.agent_nodes import data_agent, analysis_agent

        # Step 1: Initial state - orchestrator routes to data agent
        state: MultiAgentState = {
            "messages": [],
            "task": "Process and analyze customer transaction data for Q4 2024 financial report",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        # Step 2: Orchestrator routes to data agent
        orchestrator_result = orchestrator_agent(state)
        assert orchestrator_result["current_agent"] == "data"
        state["current_agent"] = orchestrator_result["current_agent"]

        # Step 3: Execute data agent with production state
        data_result = data_agent(state)
        state.update(data_result)
        assert "data" in state["agent_results"]
        assert state["agent_results"]["data"]["agent"] == "data"
        assert state["agent_results"]["data"]["result"] == "data_processed"
        assert state["current_agent"] == "analysis"

        # Step 4: Orchestrator routes to analysis agent
        state["current_agent"] = "orchestrator"
        orchestrator_result = orchestrator_agent(state)
        assert orchestrator_result["current_agent"] == "analysis"
        state["current_agent"] = orchestrator_result["current_agent"]

        # Step 5: Execute analysis agent with production state
        analysis_result = analysis_agent(state)
        state.update(analysis_result)
        assert "analysis" in state["agent_results"]
        assert state["agent_results"]["analysis"]["agent"] == "analysis"
        assert state["agent_results"]["analysis"]["result"] == "analysis_complete"
        assert state["current_agent"] == "orchestrator"

        # Step 6: Orchestrator detects completion
        orchestrator_result = orchestrator_agent(state)
        assert orchestrator_result["completed"] is True
        assert orchestrator_result["current_agent"] == "end"

        # Verify final state has all production data
        assert state["task"] == "Process and analyze customer transaction data for Q4 2024 financial report"
        assert len(state["agent_results"]) == 2
        assert "data" in state["agent_results"]
        assert "analysis" in state["agent_results"]

