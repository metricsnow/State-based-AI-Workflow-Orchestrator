"""State definitions and reducers for LangGraph workflows.

This module defines TypedDict state schemas with proper reducers for state management
in LangGraph workflows. Reducers specify how state updates are applied, enabling
proper state aggregation and message handling.

Example:
    ```python
    from langgraph_workflows.state import WorkflowState, SimpleState

    # Create a workflow state
    state: WorkflowState = {
        "messages": [],
        "task_data": {},
        "agent_results": {},
        "workflow_status": "initialized",
        "metadata": {}
    }

    # Validate state
    from langgraph_workflows.state import validate_state
    assert validate_state(state)
    ```
"""

from typing import Annotated, Any

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


def merge_dicts(x: dict[str, Any], y: dict[str, Any]) -> dict[str, Any]:
    """Merge two dictionaries, with y taking precedence for conflicts.

    This reducer function is used for dictionary fields in state schemas to ensure
    that updates merge with existing values rather than replacing them entirely.

    Args:
        x: The existing dictionary value.
        y: The new dictionary value to merge.

    Returns:
        A new dictionary containing merged values from x and y, with y values
        taking precedence for conflicting keys.

    Example:
        ```python
        existing = {"a": 1, "b": 2}
        update = {"b": 3, "c": 4}
        result = merge_dicts(existing, update)
        # result = {"a": 1, "b": 3, "c": 4}
        ```
    """
    return {**x, **y}


def last_value(x: str, y: str) -> str:
    """Return the last value (y).

    This reducer function is used for status fields where the latest value should
    overwrite previous values.

    Args:
        x: The existing string value (ignored).
        y: The new string value.

    Returns:
        The new string value (y).

    Example:
        ```python
        result = last_value("initialized", "processing")
        # result = "processing"
        ```
    """
    return y


class WorkflowState(TypedDict):
    """State schema for LangGraph workflows.

    This state schema is designed for complex workflows with message handling,
    task data, agent results, workflow status tracking, and metadata.

    Attributes:
        messages: List of messages with add_messages reducer for proper message handling.
            The add_messages reducer appends messages rather than replacing them.
        task_data: Dictionary for storing task-specific data. Uses merge_dicts reducer
            to merge updates rather than replace.
        agent_results: Dictionary for storing results from different agents. Uses
            merge_dicts reducer to aggregate results.
        workflow_status: String tracking the current workflow status. Uses last_value
            reducer so the latest status overwrites previous values.
        metadata: Dictionary for storing additional metadata. Uses merge_dicts reducer
            to merge metadata updates.
    """

    messages: Annotated[list[Any], add_messages]
    task_data: Annotated[dict[str, Any], merge_dicts]
    agent_results: Annotated[dict[str, Any], merge_dicts]
    workflow_status: Annotated[str, last_value]
    metadata: Annotated[dict[str, Any], merge_dicts]


class SimpleState(TypedDict):
    """Simple state for basic workflows.

    This is a simplified state schema for basic workflows that don't require
    complex message handling or multiple agent coordination.

    Attributes:
        data: Dictionary for storing workflow data. Uses merge_dicts reducer to
            merge updates rather than replace.
        status: String tracking the workflow status. Uses last_value reducer so
            the latest status overwrites previous values.
    """

    data: Annotated[dict[str, Any], merge_dicts]
    status: Annotated[str, last_value]


def validate_state(state: WorkflowState) -> bool:
    """Validate state structure and required fields.

    Checks that the state contains all required fields for WorkflowState.
    This is useful for runtime validation before processing state.

    Args:
        state: The state dictionary to validate.

    Returns:
        True if state contains all required fields, False otherwise.

    Example:
        ```python
        state: WorkflowState = {
            "messages": [],
            "task_data": {},
            "agent_results": {},
            "workflow_status": "initialized",
            "metadata": {}
        }
        assert validate_state(state)  # True

        invalid_state = {"messages": []}
        assert not validate_state(invalid_state)  # False
        ```
    """
    required_fields = ["messages", "task_data", "workflow_status"]
    for field in required_fields:
        if field not in state:
            return False
    return True


def validate_simple_state(state: SimpleState) -> bool:
    """Validate simple state structure and required fields.

    Checks that the state contains all required fields for SimpleState.

    Args:
        state: The state dictionary to validate.

    Returns:
        True if state contains all required fields, False otherwise.

    Example:
        ```python
        state: SimpleState = {
            "data": {},
            "status": "initialized"
        }
        assert validate_simple_state(state)  # True
        ```
    """
    required_fields = ["data", "status"]
    for field in required_fields:
        if field not in state:
            return False
    return True

