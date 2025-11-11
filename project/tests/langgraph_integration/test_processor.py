"""Tests for workflow event processor.

Tests event-to-state conversion and workflow execution.
"""

import pytest
from uuid import uuid4

from workflow_events import (
    WorkflowEvent,
    EventType,
    EventSource,
    WorkflowEventPayload,
    WorkflowEventMetadata,
)
from langgraph_integration.processor import (
    event_to_multi_agent_state,
    WorkflowProcessor,
)
from langgraph_workflows.state import MultiAgentState


class TestEventToStateConversion:
    """Test conversion of WorkflowEvent to MultiAgentState."""

    def test_event_to_state_basic(self) -> None:
        """Test basic event to state conversion."""
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test_workflow",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(data={"task": "test_task"}),
            metadata=WorkflowEventMetadata(environment="dev", version="1.0"),
        )
        
        state = event_to_multi_agent_state(event)
        
        # TypedDict doesn't support isinstance, check structure instead
        assert isinstance(state, dict)
        assert "task" in state
        assert "current_agent" in state
        assert "completed" in state
        assert "messages" in state
        assert "agent_results" in state
        assert "metadata" in state
        
        assert state["task"] == "test_task"
        assert state["current_agent"] == "orchestrator"
        assert state["completed"] is False
        assert state["messages"] == []
        assert state["agent_results"] == {}
        assert "event_id" in state["metadata"]
        assert state["metadata"]["workflow_id"] == "test_workflow"

    def test_event_to_state_nested_task(self) -> None:
        """Test event with nested task in payload.data."""
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test_workflow",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(
                data={"data": {"task": "nested_task"}, "other": "value"}
            ),
            metadata=WorkflowEventMetadata(environment="dev", version="1.0"),
        )
        
        state = event_to_multi_agent_state(event)
        
        assert state["task"] == "nested_task"

    def test_event_to_state_default_task(self) -> None:
        """Test event without task defaults to 'process_workflow'."""
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test_workflow",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(data={"other": "value"}),
            metadata=WorkflowEventMetadata(environment="dev", version="1.0"),
        )
        
        state = event_to_multi_agent_state(event)
        
        assert state["task"] == "process_workflow"

    def test_event_to_state_metadata(self) -> None:
        """Test event metadata is properly included in state."""
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test_workflow",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(data={"task": "test_task"}),
            metadata=WorkflowEventMetadata(environment="prod", version="2.0"),
        )
        
        state = event_to_multi_agent_state(event)
        
        assert state["metadata"]["workflow_id"] == "test_workflow"
        assert state["metadata"]["workflow_run_id"] == "run_123"
        assert state["metadata"]["source"] == "airflow"
        assert "event_id" in state["metadata"]


class TestWorkflowProcessor:
    """Test WorkflowProcessor execution."""

    @pytest.mark.asyncio
    async def test_process_workflow_event_success(self) -> None:
        """Test successful workflow event processing."""
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test_workflow",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(
                data={"task": "test_task", "data": {"input": "test"}}
            ),
            metadata=WorkflowEventMetadata(environment="dev", version="1.0"),
        )
        
        # Processor without result_producer (for testing)
        processor = WorkflowProcessor(result_producer=None)
        result = await processor.process_workflow_event(event)
        
        assert result is not None
        assert isinstance(result, dict)
        # Workflow should complete (multi-agent workflow completes by design)
        assert "completed" in result or "agent_results" in result

    @pytest.mark.asyncio
    async def test_process_workflow_event_invalid_state(self) -> None:
        """Test processor handles invalid event data gracefully."""
        # Create event with minimal data
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test_workflow",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(data={}),
            metadata=WorkflowEventMetadata(environment="dev", version="1.0"),
        )
        
        # Processor without result_producer (for testing)
        processor = WorkflowProcessor(result_producer=None)
        # Should not raise - workflow should handle default state
        result = await processor.process_workflow_event(event)
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_extract_result(self) -> None:
        """Test result extraction from workflow state."""
        processor = WorkflowProcessor()
        
        workflow_result = {
            "completed": True,
            "agent_results": {"agent1": "result1"},
            "task": "test_task",
            "metadata": {"key": "value"},
            "other_field": "ignored",
        }
        
        result = processor._extract_result(workflow_result)
        
        assert result["completed"] is True
        assert result["agent_results"] == {"agent1": "result1"}
        assert result["task"] == "test_task"
        assert result["metadata"] == {"key": "value"}
        assert "other_field" not in result

