"""Checkpointing workflow for LangGraph StateGraph with state persistence.

This module implements checkpointing for LangGraph workflows using InMemorySaver.
It enables state persistence across workflow steps and workflow resumption from
checkpoints, making workflows durable and resumable.

Example:
    ```python
    from langgraph_workflows.checkpoint_workflow import (
        execute_with_checkpoint,
        resume_workflow,
        checkpoint_graph
    )

    # Execute workflow with checkpointing
    result, thread_id = execute_with_checkpoint(
        {"data": {"input": "test"}, "status": "processing"}
    )

    # Resume workflow from checkpoint
    result2 = resume_workflow(
        thread_id,
        {"data": {"step": 2}, "status": "processing"}
    )
    ```
"""

import uuid
from typing import Any

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from langgraph_workflows.basic_workflow import node_b
from langgraph_workflows.conditional_workflow import (
    error_handler,
    node_a_conditional,
    should_continue,
)
from langgraph_workflows.state import SimpleState


# Create checkpointer for state persistence
checkpointer = InMemorySaver()

# Build graph with conditional routing and checkpointing
workflow = StateGraph(SimpleState)

# Add nodes
workflow.add_node("node_a", node_a_conditional)
workflow.add_node("node_b", node_b)
workflow.add_node("error_handler", error_handler)

# Add fixed edges: START -> node_a
workflow.add_edge(START, "node_a")

# Add conditional edge from node_a
workflow.add_conditional_edges(
    "node_a",
    should_continue,
    {
        "node_b": "node_b",
        "end": END,
        "error_handler": "error_handler",
        "node_a": "node_a",
    },
)

# Add final edges
workflow.add_edge("node_b", END)
workflow.add_edge("error_handler", END)

# Compile graph with checkpointer
checkpoint_graph = workflow.compile(checkpointer=checkpointer)


def execute_with_checkpoint(
    initial_state: SimpleState, thread_id: str | None = None
) -> tuple[dict[str, Any], str]:
    """Execute workflow with checkpointing enabled.

    This function executes the workflow with checkpointing, allowing state to be
    persisted across invocations. If no thread_id is provided, a new UUID is
    generated. The same thread_id can be used to resume workflow execution from
    a previous checkpoint.

    Args:
        initial_state: The initial state dictionary for the workflow.
        thread_id: Optional thread ID for checkpoint tracking. If None, a new
            UUID is generated.

    Returns:
        A tuple containing:
        - The final state dictionary after workflow execution
        - The thread_id used for checkpoint tracking

    Example:
        ```python
        state: SimpleState = {
            "data": {"input": "test"},
            "status": "processing"
        }
        result, thread_id = execute_with_checkpoint(state)
        assert result["status"] == "completed"
        assert thread_id is not None
        ```
    """
    if thread_id is None:
        thread_id = str(uuid.uuid4())

    config = {"configurable": {"thread_id": thread_id}}

    result = checkpoint_graph.invoke(initial_state, config=config)
    return result, thread_id


def resume_workflow(
    thread_id: str, additional_state: SimpleState | None = None
) -> dict[str, Any]:
    """Resume workflow from checkpoint using thread_id.

    This function resumes workflow execution from a previous checkpoint identified
    by the thread_id. The workflow state is loaded from the checkpoint and the
    workflow continues execution. If additional_state is provided, it will be
    merged with the checkpointed state.

    Args:
        thread_id: The thread ID of the checkpoint to resume from.
        additional_state: Optional state updates to merge with checkpointed state.
            If None, the workflow resumes from the exact checkpointed state.

    Returns:
        The final state dictionary after workflow resumption.

    Raises:
        ValueError: If thread_id is invalid or checkpoint not found.

    Example:
        ```python
        # First execution
        state1: SimpleState = {"data": {"step": 1}, "status": "processing"}
        result1, thread_id = execute_with_checkpoint(state1)

        # Resume from checkpoint
        state2: SimpleState = {"data": {"step": 2}, "status": "processing"}
        result2 = resume_workflow(thread_id, state2)
        assert result2["data"]["step"] == 2
        ```
    """
    config = {"configurable": {"thread_id": thread_id}}

    # Get current state from checkpoint
    current_state = checkpoint_graph.get_state(config)

    # Check if checkpoint exists (values is None or empty dict means no checkpoint)
    if current_state.values is None or (
        isinstance(current_state.values, dict) and len(current_state.values) == 0
    ):
        raise ValueError(f"No checkpoint found for thread_id: {thread_id}")

    # Merge additional state if provided
    if additional_state is not None:
        # Merge additional state with checkpointed state
        merged_state: SimpleState = {
            "data": {
                **current_state.values.get("data", {}),
                **additional_state.get("data", {}),
            },
            "status": additional_state.get(
                "status", current_state.values.get("status", "")
            ),
        }
    else:
        merged_state = current_state.values

    # Continue workflow execution
    result = checkpoint_graph.invoke(merged_state, config=config)
    return result


def get_checkpoint_state(thread_id: str) -> dict[str, Any] | None:
    """Get the current state from checkpoint without executing workflow.

    This function retrieves the checkpointed state for a given thread_id without
    executing the workflow. Useful for inspecting workflow state or debugging.

    Args:
        thread_id: The thread ID of the checkpoint to retrieve.

    Returns:
        The checkpointed state dictionary, or None if no checkpoint exists.

    Example:
        ```python
        state: SimpleState = {"data": {"input": "test"}, "status": "processing"}
        result, thread_id = execute_with_checkpoint(state)

        # Get checkpoint state without executing
        checkpoint_state = get_checkpoint_state(thread_id)
        assert checkpoint_state is not None
        ```
    """
    config = {"configurable": {"thread_id": thread_id}}
    current_state = checkpoint_graph.get_state(config)

    # Check if checkpoint exists (values is None or empty dict means no checkpoint)
    if current_state.values is None or (
        isinstance(current_state.values, dict) and len(current_state.values) == 0
    ):
        return None

    return current_state.values


def list_checkpoints(thread_id: str) -> list[dict[str, Any]]:
    """List all checkpoints for a given thread_id.

    This function retrieves all checkpoints associated with a thread_id, allowing
    inspection of the workflow execution history.

    Args:
        thread_id: The thread ID to list checkpoints for.

    Returns:
        A list of checkpoint dictionaries, each containing checkpoint metadata.

    Example:
        ```python
        state: SimpleState = {"data": {"input": "test"}, "status": "processing"}
        result, thread_id = execute_with_checkpoint(state)

        # List all checkpoints
        checkpoints = list_checkpoints(thread_id)
        assert len(checkpoints) > 0
        ```
    """
    config = {"configurable": {"thread_id": thread_id}}
    checkpoints = list(checkpointer.list(config))
    return checkpoints

