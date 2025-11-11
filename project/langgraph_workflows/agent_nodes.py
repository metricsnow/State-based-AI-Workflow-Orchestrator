"""Specialized agent nodes for LangGraph multi-agent workflows.

This module implements specialized agent nodes that perform distinct tasks in
multi-agent workflows. Each agent updates state correctly and returns results
that can be aggregated and used by other agents or the orchestrator.

Example:
    ```python
    from langgraph_workflows.agent_nodes import data_agent, analysis_agent
    from langgraph_workflows.state import MultiAgentState

    # Create initial state
    state: MultiAgentState = {
        "messages": [],
        "task": "process_data",
        "agent_results": {},
        "current_agent": "data",
        "completed": False,
        "metadata": {}
    }

    # Execute data agent
    result = data_agent(state)
    # result["agent_results"]["data"] contains processed data
    # result["current_agent"] == "analysis"
    ```
"""

from typing import Any

from langgraph_workflows.state import MultiAgentState


def data_agent(state: MultiAgentState) -> dict[str, Any]:
    """Specialized agent for data processing tasks.

    This agent processes data based on the task in the state. It creates
    a processed data result and updates the state to route to the analysis agent.

    Args:
        state: The current multi-agent state containing task and agent results.

    Returns:
        A dictionary containing state updates:
        - agent_results: Updated with data agent result under "data" key
        - current_agent: Set to "analysis" to route to next agent

    Example:
        ```python
        state: MultiAgentState = {
            "messages": [],
            "task": "process_data",
            "agent_results": {},
            "current_agent": "data",
            "completed": False,
            "metadata": {}
        }
        result = data_agent(state)
        assert "data" in result["agent_results"]
        assert result["current_agent"] == "analysis"
        ```
    """
    task = state.get("task", "")
    agent_results = state.get("agent_results", {})

    # Process data (simplified for Phase 2 - no LLM calls yet)
    processed_data = {
        "agent": "data",
        "result": "data_processed",
        "data": {"processed": True, "task": task},
    }

    return {
        "agent_results": {
            **agent_results,
            "data": processed_data,
        },
        "current_agent": "analysis",
    }


def analysis_agent(state: MultiAgentState) -> dict[str, Any]:
    """Specialized agent for analysis tasks.

    This agent performs analysis on data processed by the data agent. It reads
    the data agent results from state and creates an analysis result. Updates
    the state to route back to the orchestrator.

    Args:
        state: The current multi-agent state containing agent results from
            previous agents.

    Returns:
        A dictionary containing state updates:
        - agent_results: Updated with analysis agent result under "analysis" key
        - current_agent: Set to "orchestrator" to route back to orchestrator

    Example:
        ```python
        state: MultiAgentState = {
            "messages": [],
            "task": "analyze_data",
            "agent_results": {
                "data": {"agent": "data", "result": "data_processed"}
            },
            "current_agent": "analysis",
            "completed": False,
            "metadata": {}
        }
        result = analysis_agent(state)
        assert "analysis" in result["agent_results"]
        assert result["current_agent"] == "orchestrator"
        ```
    """
    agent_results = state.get("agent_results", {})
    data_result = agent_results.get("data", {})

    # Perform analysis (simplified for Phase 2 - no LLM calls yet)
    analysis_result = {
        "agent": "analysis",
        "result": "analysis_complete",
        "analysis": {
            "status": "success",
            "data_source": data_result,
        },
    }

    return {
        "agent_results": {
            **agent_results,
            "analysis": analysis_result,
        },
        "current_agent": "orchestrator",
    }


def data_agent_with_error_handling(state: MultiAgentState) -> dict[str, Any]:
    """Data agent with comprehensive error handling.

    This is an enhanced version of data_agent that includes error handling
    to gracefully handle failures during data processing. On error, it updates
    the state with error information and routes to orchestrator for error handling.

    Args:
        state: The current multi-agent state containing task and agent results.

    Returns:
        A dictionary containing state updates:
        - On success: agent_results with data result, current_agent set to "analysis"
        - On error: agent_results with error information, current_agent set to "orchestrator"

    Example:
        ```python
        state: MultiAgentState = {
            "messages": [],
            "task": "process_data",
            "agent_results": {},
            "current_agent": "data",
            "completed": False,
            "metadata": {}
        }
        result = data_agent_with_error_handling(state)
        # Handles errors gracefully
        ```
    """
    try:
        task = state.get("task", "")
        agent_results = state.get("agent_results", {})

        # Process data (simplified for Phase 2)
        processed_data = {
            "agent": "data",
            "result": "data_processed",
            "data": {"processed": True, "task": task},
        }

        return {
            "agent_results": {
                **agent_results,
                "data": processed_data,
            },
            "current_agent": "analysis",
        }
    except Exception as e:
        # Error handling: return error state and route to orchestrator
        return {
            "agent_results": {
                **state.get("agent_results", {}),
                "data": {"error": str(e), "agent": "data", "result": "error"},
            },
            "current_agent": "orchestrator",
        }


def analysis_agent_with_error_handling(state: MultiAgentState) -> dict[str, Any]:
    """Analysis agent with comprehensive error handling.

    This is an enhanced version of analysis_agent that includes error handling
    to gracefully handle failures during analysis. On error, it updates the
    state with error information and routes to orchestrator for error handling.

    Args:
        state: The current multi-agent state containing agent results from
            previous agents.

    Returns:
        A dictionary containing state updates:
        - On success: agent_results with analysis result, current_agent set to "orchestrator"
        - On error: agent_results with error information, current_agent set to "orchestrator"

    Example:
        ```python
        state: MultiAgentState = {
            "messages": [],
            "task": "analyze_data",
            "agent_results": {
                "data": {"agent": "data", "result": "data_processed"}
            },
            "current_agent": "analysis",
            "completed": False,
            "metadata": {}
        }
        result = analysis_agent_with_error_handling(state)
        # Handles errors gracefully
        ```
    """
    try:
        agent_results = state.get("agent_results", {})
        data_result = agent_results.get("data", {})

        # Check if data agent had an error
        if isinstance(data_result, dict) and data_result.get("result") == "error":
            # Propagate error to orchestrator
            return {
                "agent_results": {
                    **agent_results,
                    "analysis": {
                        "error": "Cannot analyze: data processing failed",
                        "agent": "analysis",
                        "result": "error",
                    },
                },
                "current_agent": "orchestrator",
            }

        # Perform analysis (simplified for Phase 2)
        analysis_result = {
            "agent": "analysis",
            "result": "analysis_complete",
            "analysis": {
                "status": "success",
                "data_source": data_result,
            },
        }

        return {
            "agent_results": {
                **agent_results,
                "analysis": analysis_result,
            },
            "current_agent": "orchestrator",
        }
    except Exception as e:
        # Error handling: return error state and route to orchestrator
        return {
            "agent_results": {
                **state.get("agent_results", {}),
                "analysis": {
                    "error": str(e),
                    "agent": "analysis",
                    "result": "error",
                },
            },
            "current_agent": "orchestrator",
        }

