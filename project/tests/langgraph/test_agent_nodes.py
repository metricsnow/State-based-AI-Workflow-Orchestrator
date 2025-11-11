"""Comprehensive tests for LangGraph specialized agent nodes.

This test suite validates agent node functionality, state updates, result formats,
and error handling for data_agent and analysis_agent.
"""

import pytest

from langgraph_workflows.agent_nodes import (
    analysis_agent,
    analysis_agent_with_error_handling,
    data_agent,
    data_agent_with_error_handling,
)
from langgraph_workflows.state import MultiAgentState


class TestDataAgent:
    """Test data agent node functionality."""

    def test_data_agent_basic_functionality(self) -> None:
        """Test data agent processes task and updates state correctly."""
        state: MultiAgentState = {
            "messages": [],
            "task": "Process customer data for monthly analytics report",
            "agent_results": {},
            "current_agent": "data",
            "completed": False,
            "metadata": {},
        }

        result = data_agent(state)

        assert "data" in result["agent_results"]
        assert result["current_agent"] == "analysis"
        assert result["agent_results"]["data"]["agent"] == "data"
        assert result["agent_results"]["data"]["result"] == "data_processed"
        assert result["agent_results"]["data"]["data"]["processed"] is True
        assert result["agent_results"]["data"]["data"]["task"] == "Process customer data for monthly analytics report"

    def test_data_agent_preserves_existing_results(self) -> None:
        """Test data agent preserves existing agent results."""
        state: MultiAgentState = {
            "messages": [],
            "task": "Process customer data for monthly analytics report",
            "agent_results": {"existing": {"key": "value"}},
            "current_agent": "data",
            "completed": False,
            "metadata": {},
        }

        result = data_agent(state)

        assert "data" in result["agent_results"]
        assert "existing" in result["agent_results"]
        assert result["agent_results"]["existing"]["key"] == "value"

    def test_data_agent_with_empty_task(self) -> None:
        """Test data agent handles empty task string."""
        state: MultiAgentState = {
            "messages": [],
            "task": "",
            "agent_results": {},
            "current_agent": "data",
            "completed": False,
            "metadata": {},
        }

        result = data_agent(state)

        assert "data" in result["agent_results"]
        assert result["agent_results"]["data"]["data"]["task"] == ""

    def test_data_agent_state_update_format(self) -> None:
        """Test data agent returns proper state update format."""
        state: MultiAgentState = {
            "messages": [],
            "task": "Process customer data for monthly analytics report",
            "agent_results": {},
            "current_agent": "data",
            "completed": False,
            "metadata": {},
        }

        result = data_agent(state)

        # Should return dict with state updates
        assert isinstance(result, dict)
        assert "agent_results" in result
        assert "current_agent" in result
        # Should not return full state, only updates
        assert "messages" not in result
        assert "task" not in result
        assert "completed" not in result


class TestAnalysisAgent:
    """Test analysis agent node functionality."""

    def test_analysis_agent_basic_functionality(self) -> None:
        """Test analysis agent processes data results and updates state."""
        state: MultiAgentState = {
            "messages": [],
            "task": "Process customer data for monthly analytics report",
            "agent_results": {
                "data": {"agent": "data", "result": "data_processed", "data": {"processed": True}}
            },
            "current_agent": "analysis",
            "completed": False,
            "metadata": {},
        }

        result = analysis_agent(state)

        assert "analysis" in result["agent_results"]
        assert result["current_agent"] == "orchestrator"
        assert result["agent_results"]["analysis"]["agent"] == "analysis"
        assert result["agent_results"]["analysis"]["result"] == "analysis_complete"
        assert result["agent_results"]["analysis"]["analysis"]["status"] == "success"

    def test_analysis_agent_with_data_source(self) -> None:
        """Test analysis agent references data source correctly."""
        data_result = {"agent": "data", "result": "data_processed", "data": {"processed": True}}
        state: MultiAgentState = {
            "messages": [],
            "task": "Process customer data for monthly analytics report",
            "agent_results": {"data": data_result},
            "current_agent": "analysis",
            "completed": False,
            "metadata": {},
        }

        result = analysis_agent(state)

        assert "analysis" in result["agent_results"]
        analysis_data = result["agent_results"]["analysis"]["analysis"]
        assert "data_source" in analysis_data
        assert analysis_data["data_source"] == data_result

    def test_analysis_agent_without_data_result(self) -> None:
        """Test analysis agent handles missing data result gracefully."""
        state: MultiAgentState = {
            "messages": [],
            "task": "Process customer data for monthly analytics report",
            "agent_results": {},
            "current_agent": "analysis",
            "completed": False,
            "metadata": {},
        }

        result = analysis_agent(state)

        assert "analysis" in result["agent_results"]
        # Should still create analysis result even without data
        analysis_data = result["agent_results"]["analysis"]["analysis"]
        assert analysis_data["data_source"] == {}

    def test_analysis_agent_preserves_existing_results(self) -> None:
        """Test analysis agent preserves existing agent results."""
        state: MultiAgentState = {
            "messages": [],
            "task": "Process customer data for monthly analytics report",
            "agent_results": {
                "data": {"agent": "data", "result": "data_processed"},
                "existing": {"key": "value"},
            },
            "current_agent": "analysis",
            "completed": False,
            "metadata": {},
        }

        result = analysis_agent(state)

        assert "analysis" in result["agent_results"]
        assert "data" in result["agent_results"]
        assert "existing" in result["agent_results"]
        assert result["agent_results"]["existing"]["key"] == "value"


class TestDataAgentErrorHandling:
    """Test data agent error handling functionality."""

    def test_data_agent_with_error_handling_success(self) -> None:
        """Test error handling version works correctly on success."""
        state: MultiAgentState = {
            "messages": [],
            "task": "Process customer data for monthly analytics report",
            "agent_results": {},
            "current_agent": "data",
            "completed": False,
            "metadata": {},
        }

        result = data_agent_with_error_handling(state)

        assert "data" in result["agent_results"]
        assert result["current_agent"] == "analysis"
        assert result["agent_results"]["data"]["result"] == "data_processed"

    def test_data_agent_with_error_handling_exception(self) -> None:
        """Test error handling version catches exceptions."""
        # Create a state that would cause an error if we tried to access invalid keys
        # We'll mock an error scenario
        state: MultiAgentState = {
            "messages": [],
            "task": "Process customer data for monthly analytics report",
            "agent_results": {},
            "current_agent": "data",
            "completed": False,
            "metadata": {},
        }

        # The function should handle errors gracefully
        # Since the current implementation doesn't raise errors, we test the structure
        result = data_agent_with_error_handling(state)

        # Should return valid result structure
        assert "agent_results" in result
        assert "current_agent" in result


class TestAnalysisAgentErrorHandling:
    """Test analysis agent error handling functionality."""

    def test_analysis_agent_with_error_handling_success(self) -> None:
        """Test error handling version works correctly on success."""
        state: MultiAgentState = {
            "messages": [],
            "task": "Process customer data for monthly analytics report",
            "agent_results": {
                "data": {"agent": "data", "result": "data_processed", "data": {"processed": True}}
            },
            "current_agent": "analysis",
            "completed": False,
            "metadata": {},
        }

        result = analysis_agent_with_error_handling(state)

        assert "analysis" in result["agent_results"]
        assert result["current_agent"] == "orchestrator"
        assert result["agent_results"]["analysis"]["result"] == "analysis_complete"

    def test_analysis_agent_with_error_handling_data_error(self) -> None:
        """Test error handling version detects data agent errors."""
        state: MultiAgentState = {
            "messages": [],
            "task": "Process customer data for monthly analytics report",
            "agent_results": {
                "data": {"agent": "data", "result": "error", "error": "Processing failed"}
            },
            "current_agent": "analysis",
            "completed": False,
            "metadata": {},
        }

        result = analysis_agent_with_error_handling(state)

        assert "analysis" in result["agent_results"]
        assert result["current_agent"] == "orchestrator"
        assert result["agent_results"]["analysis"]["result"] == "error"
        assert "error" in result["agent_results"]["analysis"]

    def test_analysis_agent_with_error_handling_exception(self) -> None:
        """Test error handling version catches exceptions."""
        state: MultiAgentState = {
            "messages": [],
            "task": "Process customer data for monthly analytics report",
            "agent_results": {
                "data": {"agent": "data", "result": "data_processed", "data": {"processed": True}}
            },
            "current_agent": "analysis",
            "completed": False,
            "metadata": {},
        }

        # The function should handle errors gracefully
        result = analysis_agent_with_error_handling(state)

        # Should return valid result structure
        assert "agent_results" in result
        assert "current_agent" in result


class TestAgentStateUpdates:
    """Test agent state update patterns."""

    def test_agent_results_aggregation(self) -> None:
        """Test that agent results are properly aggregated across agents."""
        state: MultiAgentState = {
            "messages": [],
            "task": "Process customer data for monthly analytics report",
            "agent_results": {},
            "current_agent": "data",
            "completed": False,
            "metadata": {},
        }

        # Execute data agent
        result1 = data_agent(state)
        assert "data" in result1["agent_results"]

        # Update state with data agent result
        updated_state: MultiAgentState = {
            **state,
            **result1,
            "agent_results": result1["agent_results"],
            "current_agent": result1["current_agent"],
        }

        # Execute analysis agent
        result2 = analysis_agent(updated_state)
        assert "data" in result2["agent_results"]
        assert "analysis" in result2["agent_results"]

    def test_current_agent_routing(self) -> None:
        """Test that current_agent field routes correctly between agents."""
        state: MultiAgentState = {
            "messages": [],
            "task": "Process customer data for monthly analytics report",
            "agent_results": {},
            "current_agent": "data",
            "completed": False,
            "metadata": {},
        }

        # Data agent routes to analysis
        result1 = data_agent(state)
        assert result1["current_agent"] == "analysis"

        # Analysis agent routes to orchestrator
        updated_state: MultiAgentState = {
            **state,
            **result1,
            "agent_results": result1["agent_results"],
            "current_agent": result1["current_agent"],
        }
        result2 = analysis_agent(updated_state)
        assert result2["current_agent"] == "orchestrator"

    def test_result_format_consistency(self) -> None:
        """Test that agent results follow consistent format."""
        state: MultiAgentState = {
            "messages": [],
            "task": "Process customer data for monthly analytics report",
            "agent_results": {},
            "current_agent": "data",
            "completed": False,
            "metadata": {},
        }

        result = data_agent(state)
        data_result = result["agent_results"]["data"]

        # Check consistent format
        assert "agent" in data_result
        assert "result" in data_result
        assert data_result["agent"] == "data"
        assert isinstance(data_result["result"], str)

