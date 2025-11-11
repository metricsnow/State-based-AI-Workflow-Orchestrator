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


def merge_agent_results(x: dict[str, Any], y: dict[str, Any]) -> dict[str, Any]:
    """Merge agent results, with y taking precedence for conflicts.

    This reducer function is used for agent_results field in MultiAgentState to ensure
    that agent results are properly aggregated. When multiple agents update results,
    their results are merged with newer results taking precedence for conflicts.

    Args:
        x: The existing agent results dictionary.
        y: The new agent results dictionary to merge.

    Returns:
        A new dictionary containing merged agent results from x and y, with y values
        taking precedence for conflicting keys.

    Example:
        ```python
        existing = {"data": {"agent": "data", "result": "processed"}}
        update = {"analysis": {"agent": "analysis", "result": "complete"}}
        result = merge_agent_results(existing, update)
        # result = {
        #     "data": {"agent": "data", "result": "processed"},
        #     "analysis": {"agent": "analysis", "result": "complete"}
        # }
        ```
    """
    return {**x, **y}


class MultiAgentState(TypedDict):
    """State schema for multi-agent LangGraph workflows.

    This state schema is designed for orchestrator-worker multi-agent patterns where
    multiple specialized agents collaborate on tasks. It supports agent coordination,
    result aggregation, and workflow management.

    Attributes:
        messages: List of messages with add_messages reducer for proper message handling.
            The add_messages reducer appends messages rather than replacing them.
        task: String representing the current task being processed by agents.
        agent_results: Dictionary for storing results from different agents. Uses
            merge_agent_results reducer to aggregate results from multiple agents.
        current_agent: String tracking the current active agent in the workflow.
            Uses last_value reducer so the latest agent overwrites previous values.
        completed: Boolean tracking workflow completion status. Uses last_value
            reducer so the latest completion status overwrites previous values.
        metadata: Dictionary for storing additional metadata. Uses merge_dicts reducer
            to merge metadata updates.
    """

    messages: Annotated[list[Any], add_messages]
    task: Annotated[str, last_value]
    agent_results: Annotated[dict[str, Any], merge_agent_results]
    current_agent: Annotated[str, last_value]
    completed: Annotated[bool, last_value]
    metadata: Annotated[dict[str, Any], merge_dicts]


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


def validate_multi_agent_state(state: MultiAgentState) -> bool:
    """Validate multi-agent state structure and required fields.

    Checks that the state contains all required fields for MultiAgentState.
    This is useful for runtime validation before processing state in multi-agent workflows.

    Args:
        state: The state dictionary to validate.

    Returns:
        True if state contains all required fields, False otherwise.

    Example:
        ```python
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {}
        }
        assert validate_multi_agent_state(state)  # True

        invalid_state = {"messages": []}
        assert not validate_multi_agent_state(invalid_state)  # False
        ```
    """
    required_fields = [
        "messages",
        "task",
        "agent_results",
        "current_agent",
        "completed",
    ]
    for field in required_fields:
        if field not in state:
            return False
    return True

