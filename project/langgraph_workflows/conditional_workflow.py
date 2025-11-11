"""Conditional routing workflow for LangGraph StateGraph.

This module implements conditional routing in LangGraph StateGraph using conditional
edges. It enables dynamic workflow execution based on state conditions, allowing
workflows to adapt to different scenarios.

Example:
    ```python
    from langgraph_workflows.conditional_workflow import execute_conditional_workflow

    # Execute workflow with processing status
    result = execute_conditional_workflow({"input": "test"}, "processing")
    assert result["status"] == "completed"
    assert result["data"]["finalized"] is True

    # Execute workflow with completed status (routes directly to END)
    result = execute_conditional_workflow({"input": "test"}, "completed")
    assert result["status"] == "completed"
    ```
"""

from langgraph.graph import END, START, StateGraph

from langgraph_workflows.basic_workflow import node_b
from langgraph_workflows.state import SimpleState


def node_a_conditional(state: SimpleState) -> SimpleState:
    """Conditional node_a that preserves or sets status based on state.

    This node processes the initial state and sets the status appropriately.
    It preserves "completed" and "error" statuses to enable conditional routing,
    otherwise sets status to "processing" for normal flow.

    Args:
        state: The current workflow state.

    Returns:
        A state update dictionary with processed data and appropriate status.
    """
    current_status = state.get("status", "")
    current_data = state.get("data", {})

    # Preserve "completed" and "error" statuses for conditional routing
    # Otherwise, set to "processing" for normal flow
    if current_status in ("completed", "error"):
        new_status = current_status
    else:
        new_status = "processing"

    return {
        "data": {**current_data, "step": "a", "processed": True},
        "status": new_status,
    }


def should_continue(state: SimpleState) -> str:
    """Route to next node based on state conditions.

    This routing function examines the current state and determines the next node
    to execute. It supports multiple routing paths:
    - "processing" -> routes to node_b for further processing
    - "completed" -> routes to END to terminate workflow
    - "error" -> routes to error_handler for error handling
    - default -> routes to node_a for initial processing

    Args:
        state: The current workflow state containing status and data.

    Returns:
        A string representing the next node name to execute. Can be:
        - "node_b": Continue processing
        - "end": Terminate workflow (maps to END)
        - "error_handler": Handle errors
        - "node_a": Default initial processing

    Example:
        ```python
        state: SimpleState = {"data": {}, "status": "processing"}
        next_node = should_continue(state)
        assert next_node == "node_b"
        ```
    """
    status = state.get("status", "")

    if status == "processing":
        return "node_b"
    elif status == "completed":
        return "end"
    elif status == "error":
        return "error_handler"
    else:
        return "node_a"


def error_handler(state: SimpleState) -> SimpleState:
    """Error handler node that processes error states.

    This node handles error conditions in the workflow by updating the state
    to indicate error handling has occurred and setting appropriate status.

    Args:
        state: The current workflow state, potentially containing error information.

    Returns:
        A state update dictionary with error handling information and status
        set to "error_handled".

    Example:
        ```python
        state: SimpleState = {"data": {}, "status": "error"}
        result = error_handler(state)
        assert result["status"] == "error_handled"
        assert "error_handled" in result["data"]
        ```
    """
    current_data = state.get("data", {})
    return {
        "data": {**current_data, "error_handled": True, "step": "error_handler"},
        "status": "error_handled",
    }


# Build graph with conditional routing
workflow = StateGraph(SimpleState)

# Add nodes
workflow.add_node("node_a", node_a_conditional)
workflow.add_node("node_b", node_b)
workflow.add_node("error_handler", error_handler)

# Add fixed edges: START -> node_a
workflow.add_edge(START, "node_a")

# Add conditional edge from node_a
# The routing map maps routing function return values to actual node names
workflow.add_conditional_edges(
    "node_a",
    should_continue,
    {
        "node_b": "node_b",
        "end": END,
        "error_handler": "error_handler",
        "node_a": "node_a",  # Default case (shouldn't happen, but for completeness)
    },
)

# Add final edges
workflow.add_edge("node_b", END)
workflow.add_edge("error_handler", END)

# Compile graph (without checkpointing for now)
graph = workflow.compile()


def execute_conditional_workflow(initial_data: dict, initial_status: str = "initialized") -> dict:
    """Execute the conditional routing workflow.

    This function creates an initial state from the provided data and status,
    then executes the compiled graph with conditional routing. The workflow
    will route to different nodes based on the initial status.

    Args:
        initial_data: Dictionary containing initial data for the workflow.
        initial_status: Initial status string that determines routing behavior.
            Options: "initialized" (default), "processing", "completed", "error".

    Returns:
        The final state dictionary after workflow execution.

    Example:
        ```python
        # Normal flow: initialized -> node_a -> node_b -> END
        result = execute_conditional_workflow({"input": "test"}, "initialized")
        assert result["status"] == "completed"

        # Processing flow: processing -> node_a -> node_b -> END
        result = execute_conditional_workflow({"input": "test"}, "processing")
        assert result["status"] == "completed"

        # Completed flow: completed -> node_a -> END (skips node_b)
        result = execute_conditional_workflow({"input": "test"}, "completed")
        assert result["status"] == "completed"

        # Error flow: error -> node_a -> error_handler -> END
        result = execute_conditional_workflow({"input": "test"}, "error")
        assert result["status"] == "error_handled"
        ```
    """
    initial_state: SimpleState = {
        "data": initial_data,
        "status": initial_status,
    }

    result = graph.invoke(initial_state)
    return result

