"""Basic LangGraph StateGraph workflow with two nodes.

This module implements a simple StateGraph workflow with two nodes that update state.
This establishes the foundation for stateful workflows in the system.

Example:
    ```python
    from langgraph_workflows.basic_workflow import execute_workflow

    # Execute the workflow
    result = execute_workflow({"input": "test"})
    assert result["status"] == "completed"
    assert result["data"]["finalized"] is True
    ```
"""

from langgraph.graph import END, START, StateGraph

from langgraph_workflows.state import SimpleState


def node_a(state: SimpleState) -> SimpleState:
    """First node that processes initial state.

    This node takes the initial state and processes it, setting the status to
    "processing" and adding initial processing information to the data field.

    Args:
        state: The current workflow state.

    Returns:
        A state update dictionary with processed data and status set to "processing".

    Example:
        ```python
        state: SimpleState = {"data": {}, "status": "initial"}
        result = node_a(state)
        assert result["status"] == "processing"
        assert "processed" in result["data"]
        ```
    """
    return {
        "data": {"step": "a", "processed": True},
        "status": "processing",
    }


def node_b(state: SimpleState) -> SimpleState:
    """Second node that processes node_a output.

    This node takes the state from node_a and finalizes the processing,
    setting the status to "completed" and adding finalization information.

    Args:
        state: The current workflow state (should contain node_a's output).

    Returns:
        A state update dictionary with finalized data and status set to "completed".

    Example:
        ```python
        state: SimpleState = {
            "data": {"step": "a", "processed": True},
            "status": "processing"
        }
        result = node_b(state)
        assert result["status"] == "completed"
        assert result["data"]["finalized"] is True
        ```
    """
    current_data = state.get("data", {})
    return {
        "data": {**current_data, "step": "b", "finalized": True},
        "status": "completed",
    }


# Build the StateGraph
workflow = StateGraph(SimpleState)

# Add nodes to the graph
workflow.add_node("node_a", node_a)
workflow.add_node("node_b", node_b)

# Add edges: START -> node_a -> node_b -> END
workflow.add_edge(START, "node_a")
workflow.add_edge("node_a", "node_b")
workflow.add_edge("node_b", END)

# Compile the graph (without checkpointing for now)
graph = workflow.compile()


def execute_workflow(initial_data: dict) -> dict:
    """Execute the basic workflow.

    This function creates an initial state from the provided data and executes
    the compiled graph, returning the final state after all nodes have executed.

    Args:
        initial_data: Dictionary containing initial data for the workflow.

    Returns:
        The final state dictionary after workflow execution.

    Example:
        ```python
        result = execute_workflow({"input": "test"})
        assert result["status"] == "completed"
        assert result["data"]["finalized"] is True
        assert result["data"]["step"] == "b"
        ```
    """
    initial_state: SimpleState = {
        "data": initial_data,
        "status": "initialized",
    }

    result = graph.invoke(initial_state)
    return result

