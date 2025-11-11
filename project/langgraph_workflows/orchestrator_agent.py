"""Orchestrator agent node for LangGraph multi-agent workflows.

This module implements the orchestrator agent that coordinates multi-agent workflow
execution. The orchestrator evaluates agent results, determines next steps, and
manages workflow completion. This enables orchestrator-worker pattern for multi-agent
collaboration.

Example:
    ```python
    from langgraph_workflows.orchestrator_agent import orchestrator_agent, route_to_agent
    from langgraph_workflows.state import MultiAgentState

    # Create initial state
    state: MultiAgentState = {
        "messages": [],
        "task": "process_and_analyze",
        "agent_results": {},
        "current_agent": "orchestrator",
        "completed": False,
        "metadata": {}
    }

    # Execute orchestrator
    result = orchestrator_agent(state)
    # result["current_agent"] == "data" (routes to data agent)
    ```
"""

from typing import Any

from langgraph_workflows.state import MultiAgentState


def orchestrator_agent(state: MultiAgentState) -> dict[str, Any]:
    """Orchestrator agent coordinates workflow execution.

    This agent evaluates the current state, checks which agents have completed
    their tasks, and determines the next agent to execute. It implements the
    orchestrator-worker pattern where the orchestrator coordinates specialized
    worker agents.

    The orchestrator follows this logic:
    1. If workflow is already completed, route to END
    2. If data agent hasn't completed, route to data agent
    3. If analysis agent hasn't completed, route to analysis agent
    4. If all agents completed, mark workflow as complete and route to END

    Args:
        state: The current multi-agent state containing agent results and
            workflow status.

    Returns:
        A dictionary containing state updates:
        - current_agent: The next agent to execute ("data", "analysis", or "end")
        - completed: True if workflow is complete, otherwise unchanged

    Example:
        ```python
        # Initial state - no agent results
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {}
        }
        result = orchestrator_agent(state)
        assert result["current_agent"] == "data"

        # After data agent completes
        state["agent_results"] = {"data": {"agent": "data", "result": "data_processed"}}
        result = orchestrator_agent(state)
        assert result["current_agent"] == "analysis"

        # After all agents complete
        state["agent_results"] = {
            "data": {"agent": "data", "result": "data_processed"},
            "analysis": {"agent": "analysis", "result": "analysis_complete"}
        }
        result = orchestrator_agent(state)
        assert result["completed"] is True
        assert result["current_agent"] == "end"
        ```
    """
    agent_results = state.get("agent_results", {})
    current_agent = state.get("current_agent", "orchestrator")
    completed = state.get("completed", False)

    # If already completed, route to end
    if completed:
        return {"current_agent": "end"}

    # Check if data agent has completed
    if "data" not in agent_results:
        return {"current_agent": "data"}

    # Check if analysis agent has completed
    if "analysis" not in agent_results:
        return {"current_agent": "analysis"}

    # All agents completed - mark workflow as complete
    return {
        "completed": True,
        "current_agent": "end",
    }


def route_to_agent(state: MultiAgentState) -> str:
    """Route to appropriate agent based on orchestrator decision.

    This routing function is used with conditional edges in LangGraph StateGraph.
    It reads the current_agent value set by the orchestrator and returns the
    appropriate node name for routing.

    Args:
        state: The current multi-agent state containing current_agent and
            completion status.

    Returns:
        A string representing the next node name:
        - "end": Terminate workflow (maps to END)
        - "data": Route to data agent node
        - "analysis": Route to analysis agent node
        - "orchestrator": Route back to orchestrator (default)

    Example:
        ```python
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "data",
            "completed": False,
            "metadata": {}
        }
        next_node = route_to_agent(state)
        assert next_node == "data"
        ```
    """
    current_agent = state.get("current_agent", "orchestrator")
    completed = state.get("completed", False)

    # If workflow is complete or current_agent is "end", terminate
    if current_agent == "end" or completed:
        return "end"

    # Return the current_agent value (set by orchestrator)
    return current_agent


def orchestrator_agent_with_errors(state: MultiAgentState) -> dict[str, Any]:
    """Orchestrator with comprehensive error handling.

    This is an enhanced version of orchestrator_agent that includes error detection
    and handling. It checks for errors in agent results and handles exceptions
    gracefully, ensuring the workflow can recover from failures.

    Error handling logic:
    1. Check all agent results for error indicators
    2. If any agent has an error, mark workflow as complete with error status
    3. Handle exceptions during orchestration logic
    4. Return appropriate state updates for error scenarios

    Args:
        state: The current multi-agent state containing agent results and
            workflow status.

    Returns:
        A dictionary containing state updates:
        - On success: Same as orchestrator_agent
        - On error: completed=True, current_agent="end", metadata with error info

    Example:
        ```python
        # State with error in data agent result
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {
                "data": {"error": "Processing failed", "agent": "data", "result": "error"}
            },
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {}
        }
        result = orchestrator_agent_with_errors(state)
        assert result["completed"] is True
        assert "error" in result.get("metadata", {})
        ```
    """
    try:
        agent_results = state.get("agent_results", {})

        # Check for errors in agent results
        for agent_name, result in agent_results.items():
            if isinstance(result, dict) and "error" in result:
                # Error detected - mark workflow as complete with error
                return {
                    "completed": True,
                    "current_agent": "end",
                    "metadata": {
                        **state.get("metadata", {}),
                        "error": f"Error in {agent_name} agent",
                        "error_details": result.get("error", "Unknown error"),
                    },
                }

        # No errors detected - proceed with normal orchestration logic
        return orchestrator_agent(state)

    except Exception as e:
        # Exception during orchestration - handle gracefully
        return {
            "completed": True,
            "current_agent": "end",
            "metadata": {
                **state.get("metadata", {}),
                "error": f"Orchestrator error: {str(e)}",
                "error_type": type(e).__name__,
            },
        }

