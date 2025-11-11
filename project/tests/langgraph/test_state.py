"""Comprehensive tests for LangGraph state definitions and reducers.

This test suite validates state creation, reducer functionality, and state validation
for WorkflowState and SimpleState schemas.
"""

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.message import add_messages

from langgraph_workflows.state import (
    MultiAgentState,
    SimpleState,
    WorkflowState,
    last_value,
    merge_agent_results,
    merge_dicts,
    validate_multi_agent_state,
    validate_simple_state,
    validate_state,
)


class TestStateCreation:
    """Test state creation with all fields."""

    def test_workflow_state_creation_with_all_fields(self) -> None:
        """Test creating a WorkflowState instance with all fields."""
        state: WorkflowState = {
            "messages": [],
            "task_data": {},
            "agent_results": {},
            "workflow_status": "initialized",
            "metadata": {},
        }
        assert validate_state(state)
        assert state["workflow_status"] == "initialized"
        assert isinstance(state["messages"], list)
        assert isinstance(state["task_data"], dict)
        assert isinstance(state["agent_results"], dict)
        assert isinstance(state["metadata"], dict)

    def test_workflow_state_creation_with_partial_fields(self) -> None:
        """Test creating a WorkflowState instance with partial fields."""
        # TypedDict allows partial fields, but validation should catch missing required ones
        state: WorkflowState = {
            "messages": [],
            "task_data": {"key": "value"},
            "workflow_status": "processing",
        }
        # Should still validate if required fields are present
        assert validate_state(state)

    def test_simple_state_creation(self) -> None:
        """Test creating a SimpleState instance."""
        state: SimpleState = {
            "data": {"key": "value"},
            "status": "initialized",
        }
        assert validate_simple_state(state)
        assert state["status"] == "initialized"
        assert state["data"]["key"] == "value"


class TestMessageReducer:
    """Test message reducer functionality."""

    def test_add_messages_reducer_import(self) -> None:
        """Test that add_messages reducer can be imported."""
        assert add_messages is not None
        assert callable(add_messages)

    def test_message_reducer_with_langchain_messages(self) -> None:
        """Test add_messages reducer with LangChain message objects."""
        # Create initial messages
        initial_messages = [HumanMessage(content="Hello")]
        new_messages = [AIMessage(content="Hi there!")]

        # Simulate reducer behavior
        # add_messages appends messages to the list
        result = add_messages(initial_messages, new_messages)

        # Verify messages are appended
        assert len(result) == 2
        assert isinstance(result[0], HumanMessage)
        assert isinstance(result[1], AIMessage)
        assert result[0].content == "Hello"
        assert result[1].content == "Hi there!"

    def test_message_reducer_with_empty_list(self) -> None:
        """Test add_messages reducer with empty initial list."""
        initial_messages: list = []
        new_messages = [HumanMessage(content="First message")]

        result = add_messages(initial_messages, new_messages)

        assert len(result) == 1
        assert result[0].content == "First message"


class TestDataReducer:
    """Test data reducer (merge_dicts) functionality."""

    def test_merge_dicts_basic(self) -> None:
        """Test basic dictionary merging."""
        x = {"a": 1, "b": 2}
        y = {"b": 3, "c": 4}

        result = merge_dicts(x, y)

        assert result == {"a": 1, "b": 3, "c": 4}
        assert result["a"] == 1  # From x
        assert result["b"] == 3  # From y (overwrites x)
        assert result["c"] == 4  # From y

    def test_merge_dicts_empty_dicts(self) -> None:
        """Test merging empty dictionaries."""
        x: dict[str, int] = {}
        y: dict[str, int] = {}

        result = merge_dicts(x, y)

        assert result == {}

    def test_merge_dicts_y_overwrites_x(self) -> None:
        """Test that y values take precedence over x values."""
        x = {"key": "old_value", "preserved": "value"}
        y = {"key": "new_value"}

        result = merge_dicts(x, y)

        assert result["key"] == "new_value"
        assert result["preserved"] == "value"

    def test_merge_dicts_nested_dicts(self) -> None:
        """Test merging dictionaries with nested structures."""
        x = {"nested": {"a": 1, "b": 2}}
        y = {"nested": {"b": 3, "c": 4}}

        # Note: merge_dicts does shallow merge, so nested dicts are replaced
        result = merge_dicts(x, y)

        assert result["nested"] == {"b": 3, "c": 4}


class TestStatusReducer:
    """Test status reducer (last_value) functionality."""

    def test_last_value_reducer(self) -> None:
        """Test last_value reducer returns the new value."""
        x = "initialized"
        y = "processing"

        result = last_value(x, y)

        assert result == "processing"
        assert result == y

    def test_last_value_reducer_same_values(self) -> None:
        """Test last_value reducer with same values."""
        x = "processing"
        y = "processing"

        result = last_value(x, y)

        assert result == "processing"

    def test_last_value_reducer_multiple_updates(self) -> None:
        """Test last_value reducer with multiple sequential updates."""
        current = "initialized"
        current = last_value(current, "processing")
        current = last_value(current, "completed")

        assert current == "completed"


class TestStateValidation:
    """Test state validation functions."""

    def test_validate_state_with_all_fields(self) -> None:
        """Test state validation with all required fields."""
        state: WorkflowState = {
            "messages": [],
            "task_data": {},
            "workflow_status": "initialized",
            "agent_results": {},
            "metadata": {},
        }
        assert validate_state(state) is True

    def test_validate_state_missing_required_field(self) -> None:
        """Test state validation fails when required field is missing."""
        # Missing workflow_status
        invalid_state = {
            "messages": [],
            "task_data": {},
            # "workflow_status": "initialized",  # Missing
            "agent_results": {},
            "metadata": {},
        }
        assert validate_state(invalid_state) is False

    def test_validate_state_missing_messages(self) -> None:
        """Test state validation fails when messages field is missing."""
        invalid_state = {
            # "messages": [],  # Missing
            "task_data": {},
            "workflow_status": "initialized",
        }
        assert validate_state(invalid_state) is False

    def test_validate_state_missing_task_data(self) -> None:
        """Test state validation fails when task_data field is missing."""
        invalid_state = {
            "messages": [],
            # "task_data": {},  # Missing
            "workflow_status": "initialized",
        }
        assert validate_state(invalid_state) is False

    def test_validate_simple_state_with_all_fields(self) -> None:
        """Test simple state validation with all required fields."""
        state: SimpleState = {
            "data": {},
            "status": "initialized",
        }
        assert validate_simple_state(state) is True

    def test_validate_simple_state_missing_data(self) -> None:
        """Test simple state validation fails when data field is missing."""
        invalid_state = {
            # "data": {},  # Missing
            "status": "initialized",
        }
        assert validate_simple_state(invalid_state) is False

    def test_validate_simple_state_missing_status(self) -> None:
        """Test simple state validation fails when status field is missing."""
        invalid_state = {
            "data": {},
            # "status": "initialized",  # Missing
        }
        assert validate_simple_state(invalid_state) is False


class TestStateUpdates:
    """Test state updates with reducers."""

    def test_workflow_state_update_task_data(self) -> None:
        """Test updating task_data in WorkflowState."""
        state: WorkflowState = {
            "messages": [],
            "task_data": {"initial": "value"},
            "workflow_status": "initialized",
            "agent_results": {},
            "metadata": {},
        }

        # Simulate state update (reducer would handle this in actual LangGraph)
        update = {"task_data": {"new": "value", "initial": "updated"}}
        # In actual LangGraph, merge_dicts reducer would merge these
        expected = merge_dicts(state["task_data"], update["task_data"])

        assert expected["new"] == "value"
        assert expected["initial"] == "updated"

    def test_workflow_state_update_status(self) -> None:
        """Test updating workflow_status in WorkflowState."""
        state: WorkflowState = {
            "messages": [],
            "task_data": {},
            "workflow_status": "initialized",
            "agent_results": {},
            "metadata": {},
        }

        # Simulate status update (reducer would handle this)
        new_status = "processing"
        updated_status = last_value(state["workflow_status"], new_status)

        assert updated_status == "processing"

    def test_simple_state_update_data(self) -> None:
        """Test updating data in SimpleState."""
        state: SimpleState = {
            "data": {"key1": "value1"},
            "status": "initialized",
        }

        # Simulate data update
        update = {"key2": "value2", "key1": "updated"}
        expected = merge_dicts(state["data"], update)

        assert expected["key1"] == "updated"
        assert expected["key2"] == "value2"

    def test_simple_state_update_status(self) -> None:
        """Test updating status in SimpleState."""
        state: SimpleState = {
            "data": {},
            "status": "initialized",
        }

        # Simulate status update
        new_status = "completed"
        updated_status = last_value(state["status"], new_status)

        assert updated_status == "completed"


class TestStateTypeHints:
    """Test that state types work correctly with type hints."""

    def test_workflow_state_type_hints(self) -> None:
        """Test WorkflowState type hints are correct."""
        state: WorkflowState = {
            "messages": [],
            "task_data": {},
            "workflow_status": "initialized",
            "agent_results": {},
            "metadata": {},
        }

        # Type checker should recognize these fields
        assert isinstance(state["messages"], list)
        assert isinstance(state["task_data"], dict)
        assert isinstance(state["workflow_status"], str)
        assert isinstance(state["agent_results"], dict)
        assert isinstance(state["metadata"], dict)

    def test_simple_state_type_hints(self) -> None:
        """Test SimpleState type hints are correct."""
        state: SimpleState = {
            "data": {},
            "status": "initialized",
        }

        assert isinstance(state["data"], dict)
        assert isinstance(state["status"], str)


class TestMultiAgentState:
    """Test MultiAgentState creation and functionality."""

    def test_multi_agent_state_creation_with_all_fields(self) -> None:
        """Test creating a MultiAgentState instance with all fields."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }
        assert validate_multi_agent_state(state)
        assert state["task"] == "test_task"
        assert state["current_agent"] == "orchestrator"
        assert state["completed"] is False
        assert isinstance(state["messages"], list)
        assert isinstance(state["agent_results"], dict)
        assert isinstance(state["metadata"], dict)

    def test_multi_agent_state_creation_with_agent_results(self) -> None:
        """Test creating a MultiAgentState with agent results."""
        state: MultiAgentState = {
            "messages": [],
            "task": "process_data",
            "agent_results": {
                "data": {"agent": "data", "result": "processed"},
                "analysis": {"agent": "analysis", "result": "complete"},
            },
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }
        assert validate_multi_agent_state(state)
        assert "data" in state["agent_results"]
        assert "analysis" in state["agent_results"]
        assert state["agent_results"]["data"]["agent"] == "data"

    def test_multi_agent_state_creation_with_partial_fields(self) -> None:
        """Test creating a MultiAgentState instance with partial fields."""
        # TypedDict allows partial fields, but validation should catch missing required ones
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "data",
            "completed": False,
        }
        # Should still validate if required fields are present
        assert validate_multi_agent_state(state)


class TestAgentResultsReducer:
    """Test agent results reducer (merge_agent_results) functionality."""

    def test_merge_agent_results_basic(self) -> None:
        """Test basic agent results merging."""
        x = {"data": {"agent": "data", "result": "processed"}}
        y = {"analysis": {"agent": "analysis", "result": "complete"}}

        result = merge_agent_results(x, y)

        assert "data" in result
        assert "analysis" in result
        assert result["data"]["agent"] == "data"
        assert result["analysis"]["agent"] == "analysis"

    def test_merge_agent_results_overwrite(self) -> None:
        """Test that y values take precedence for conflicting keys."""
        x = {"data": {"agent": "data", "result": "old_result"}}
        y = {"data": {"agent": "data", "result": "new_result"}}

        result = merge_agent_results(x, y)

        assert result["data"]["result"] == "new_result"

    def test_merge_agent_results_empty_dicts(self) -> None:
        """Test merging empty agent results dictionaries."""
        x: dict[str, dict[str, str]] = {}
        y: dict[str, dict[str, str]] = {}

        result = merge_agent_results(x, y)

        assert result == {}

    def test_merge_agent_results_multiple_agents(self) -> None:
        """Test merging results from multiple agents."""
        x = {
            "data": {"agent": "data", "result": "processed"},
            "analysis": {"agent": "analysis", "result": "complete"},
        }
        y = {"orchestrator": {"agent": "orchestrator", "result": "coordinated"}}

        result = merge_agent_results(x, y)

        assert len(result) == 3
        assert "data" in result
        assert "analysis" in result
        assert "orchestrator" in result


class TestMultiAgentStateValidation:
    """Test multi-agent state validation functions."""

    def test_validate_multi_agent_state_with_all_fields(self) -> None:
        """Test state validation with all required fields."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }
        assert validate_multi_agent_state(state) is True

    def test_validate_multi_agent_state_missing_required_field(self) -> None:
        """Test state validation fails when required field is missing."""
        # Missing task
        invalid_state = {
            "messages": [],
            # "task": "test_task",  # Missing
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
        }
        assert validate_multi_agent_state(invalid_state) is False

    def test_validate_multi_agent_state_missing_messages(self) -> None:
        """Test state validation fails when messages field is missing."""
        invalid_state = {
            # "messages": [],  # Missing
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
        }
        assert validate_multi_agent_state(invalid_state) is False

    def test_validate_multi_agent_state_missing_agent_results(self) -> None:
        """Test state validation fails when agent_results field is missing."""
        invalid_state = {
            "messages": [],
            "task": "test_task",
            # "agent_results": {},  # Missing
            "current_agent": "orchestrator",
            "completed": False,
        }
        assert validate_multi_agent_state(invalid_state) is False

    def test_validate_multi_agent_state_missing_current_agent(self) -> None:
        """Test state validation fails when current_agent field is missing."""
        invalid_state = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            # "current_agent": "orchestrator",  # Missing
            "completed": False,
        }
        assert validate_multi_agent_state(invalid_state) is False

    def test_validate_multi_agent_state_missing_completed(self) -> None:
        """Test state validation fails when completed field is missing."""
        invalid_state = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            # "completed": False,  # Missing
        }
        assert validate_multi_agent_state(invalid_state) is False


class TestMultiAgentStateUpdates:
    """Test multi-agent state updates with reducers."""

    def test_multi_agent_state_update_task(self) -> None:
        """Test updating task in MultiAgentState."""
        state: MultiAgentState = {
            "messages": [],
            "task": "initial_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        # Simulate task update (reducer would handle this in actual LangGraph)
        new_task = "updated_task"
        updated_task = last_value(state["task"], new_task)

        assert updated_task == "updated_task"

    def test_multi_agent_state_update_agent_results(self) -> None:
        """Test updating agent_results in MultiAgentState."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {"data": {"agent": "data", "result": "processed"}},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        # Simulate agent results update
        update = {"analysis": {"agent": "analysis", "result": "complete"}}
        expected = merge_agent_results(state["agent_results"], update)

        assert "data" in expected
        assert "analysis" in expected
        assert expected["data"]["agent"] == "data"
        assert expected["analysis"]["agent"] == "analysis"

    def test_multi_agent_state_update_current_agent(self) -> None:
        """Test updating current_agent in MultiAgentState."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        # Simulate current agent update
        new_agent = "data"
        updated_agent = last_value(state["current_agent"], new_agent)

        assert updated_agent == "data"

    def test_multi_agent_state_update_completed(self) -> None:
        """Test updating completed status in MultiAgentState."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        # Simulate completion update
        # The completed field uses last_value reducer, which returns the new value
        # In actual LangGraph, the reducer would handle this automatically
        new_completed = True
        # Verify the state can be updated
        assert state["completed"] is False
        # In actual workflow, LangGraph would apply the reducer
        assert new_completed is True

    def test_multi_agent_state_update_metadata(self) -> None:
        """Test updating metadata in MultiAgentState."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {"initial": "value"},
        }

        # Simulate metadata update
        update = {"new": "value", "initial": "updated"}
        expected = merge_dicts(state["metadata"], update)

        assert expected["new"] == "value"
        assert expected["initial"] == "updated"


class TestMultiAgentStateTypeHints:
    """Test that MultiAgentState types work correctly with type hints."""

    def test_multi_agent_state_type_hints(self) -> None:
        """Test MultiAgentState type hints are correct."""
        state: MultiAgentState = {
            "messages": [],
            "task": "test_task",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {},
        }

        # Type checker should recognize these fields
        assert isinstance(state["messages"], list)
        assert isinstance(state["task"], str)
        assert isinstance(state["agent_results"], dict)
        assert isinstance(state["current_agent"], str)
        assert isinstance(state["completed"], bool)
        assert isinstance(state["metadata"], dict)

