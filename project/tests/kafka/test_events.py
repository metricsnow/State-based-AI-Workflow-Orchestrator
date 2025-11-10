"""
Tests for workflow event schema validation and serialization.

Tests cover:
- Event creation and validation
- Schema validation (valid and invalid events)
- JSON serialization/deserialization
- Schema versioning support
- Event type enumeration
"""

import json
from datetime import datetime
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from workflow_events import (
    EventType,
    EventSource,
    WorkflowEvent,
    WorkflowEventPayload,
    WorkflowEventMetadata,
)


class TestEventEnums:
    """Test event type and source enumerations."""

    def test_event_type_enum(self):
        """Test EventType enum values."""
        assert EventType.WORKFLOW_TRIGGERED == "workflow.triggered"
        assert EventType.WORKFLOW_COMPLETED == "workflow.completed"
        assert EventType.WORKFLOW_FAILED == "workflow.failed"

    def test_event_source_enum(self):
        """Test EventSource enum values."""
        assert EventSource.AIRFLOW == "airflow"
        assert EventSource.LANGGRAPH == "langgraph"
        assert EventSource.FASTAPI == "fastapi"


class TestWorkflowEventPayload:
    """Test WorkflowEventPayload model."""

    def test_valid_payload(self):
        """Test creating valid payload."""
        payload = WorkflowEventPayload(data={"status": "success", "count": 100})
        assert payload.data == {"status": "success", "count": 100}

    def test_empty_payload(self):
        """Test payload with empty data."""
        payload = WorkflowEventPayload(data={})
        assert payload.data == {}

    def test_nested_payload(self):
        """Test payload with nested data."""
        payload = WorkflowEventPayload(
            data={"workflow": {"id": "test", "status": "running"}}
        )
        assert payload.data["workflow"]["id"] == "test"


class TestWorkflowEventMetadata:
    """Test WorkflowEventMetadata model."""

    def test_valid_metadata(self):
        """Test creating valid metadata."""
        metadata = WorkflowEventMetadata(environment="dev", version="1.0")
        assert metadata.environment == "dev"
        assert metadata.version == "1.0"

    def test_default_version(self):
        """Test default version is set."""
        metadata = WorkflowEventMetadata(environment="prod")
        assert metadata.version == "1.0"

    def test_invalid_environment(self):
        """Test invalid environment raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowEventMetadata(environment="invalid")
        errors = exc_info.value.errors()
        assert any("pattern" in str(error["type"]).lower() for error in errors)

    def test_valid_environments(self):
        """Test all valid environment values."""
        for env in ["dev", "staging", "prod"]:
            metadata = WorkflowEventMetadata(environment=env)
            assert metadata.environment == env


class TestWorkflowEvent:
    """Test WorkflowEvent model."""

    def test_create_event_with_defaults(self):
        """Test creating event with default values."""
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test_dag",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(data={"test": "data"}),
            metadata=WorkflowEventMetadata(environment="dev"),
        )

        assert isinstance(event.event_id, UUID)
        assert isinstance(event.timestamp, datetime)
        assert event.event_type == EventType.WORKFLOW_TRIGGERED
        assert event.source == EventSource.AIRFLOW
        assert event.workflow_id == "test_dag"
        assert event.workflow_run_id == "run_123"

    def test_create_event_with_explicit_values(self):
        """Test creating event with explicit values."""
        event_id = uuid4()
        timestamp = datetime(2025, 1, 27, 10, 0, 0)

        event = WorkflowEvent(
            event_id=event_id,
            event_type=EventType.WORKFLOW_COMPLETED,
            timestamp=timestamp,
            source=EventSource.AIRFLOW,
            workflow_id="example_dag",
            workflow_run_id="run_456",
            payload=WorkflowEventPayload(data={"status": "success"}),
            metadata=WorkflowEventMetadata(environment="prod", version="1.0"),
        )

        assert event.event_id == event_id
        assert event.timestamp == timestamp
        assert event.event_type == EventType.WORKFLOW_COMPLETED
        assert event.metadata.environment == "prod"

    def test_invalid_event_type(self):
        """Test invalid event type raises validation error."""
        with pytest.raises(ValidationError):
            WorkflowEvent(
                event_type="invalid.type",  # type: ignore
                source=EventSource.AIRFLOW,
                workflow_id="test",
                workflow_run_id="run_123",
                payload=WorkflowEventPayload(data={}),
                metadata=WorkflowEventMetadata(environment="dev"),
            )

    def test_invalid_source(self):
        """Test invalid source raises validation error."""
        with pytest.raises(ValidationError):
            WorkflowEvent(
                event_type=EventType.WORKFLOW_TRIGGERED,
                source="invalid_source",  # type: ignore
                workflow_id="test",
                workflow_run_id="run_123",
                payload=WorkflowEventPayload(data={}),
                metadata=WorkflowEventMetadata(environment="dev"),
            )

    def test_missing_required_fields(self):
        """Test missing required fields raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowEvent(
                event_type=EventType.WORKFLOW_TRIGGERED,
                source=EventSource.AIRFLOW,
                # Missing workflow_id, workflow_run_id, payload, metadata
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0


class TestEventSerialization:
    """Test event serialization and deserialization."""

    def test_serialize_to_dict(self):
        """Test serializing event to dictionary."""
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_COMPLETED,
            source=EventSource.AIRFLOW,
            workflow_id="test_dag",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(data={"result": "success"}),
            metadata=WorkflowEventMetadata(environment="dev"),
        )

        event_dict = event.model_dump()
        assert isinstance(event_dict, dict)
        assert isinstance(event_dict["event_id"], str)  # UUID serialized to string
        assert isinstance(event_dict["timestamp"], str)  # datetime serialized to ISO
        assert event_dict["event_type"] == "workflow.completed"
        assert event_dict["source"] == "airflow"

    def test_serialize_to_json(self):
        """Test serializing event to JSON string."""
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test_dag",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(data={"status": "running"}),
            metadata=WorkflowEventMetadata(environment="dev"),
        )

        json_str = event.model_dump_json()
        assert isinstance(json_str, str)

        # Verify JSON is valid
        parsed = json.loads(json_str)
        assert parsed["event_type"] == "workflow.triggered"
        assert parsed["source"] == "airflow"
        assert isinstance(parsed["event_id"], str)
        assert isinstance(parsed["timestamp"], str)

    def test_deserialize_from_json(self):
        """Test deserializing event from JSON string."""
        json_data = {
            "event_id": str(uuid4()),
            "event_type": "workflow.completed",
            "timestamp": "2025-01-27T10:00:00",
            "source": "airflow",
            "workflow_id": "test_dag",
            "workflow_run_id": "run_123",
            "payload": {"data": {"status": "success"}},
            "metadata": {"environment": "dev", "version": "1.0"},
        }

        json_str = json.dumps(json_data)
        event = WorkflowEvent.model_validate_json(json_str)

        assert event.event_type == EventType.WORKFLOW_COMPLETED
        assert event.source == EventSource.AIRFLOW
        assert event.workflow_id == "test_dag"
        assert event.payload.data == {"status": "success"}

    def test_deserialize_from_dict(self):
        """Test deserializing event from dictionary."""
        event_dict = {
            "event_id": str(uuid4()),
            "event_type": "workflow.failed",
            "timestamp": "2025-01-27T10:00:00",
            "source": "langgraph",
            "workflow_id": "workflow_123",
            "workflow_run_id": "run_456",
            "payload": {"data": {"error": "Task failed"}},
            "metadata": {"environment": "prod", "version": "1.0"},
        }

        event = WorkflowEvent.model_validate(event_dict)

        assert event.event_type == EventType.WORKFLOW_FAILED
        assert event.source == EventSource.LANGGRAPH
        assert event.payload.data == {"error": "Task failed"}

    def test_round_trip_serialization(self):
        """Test round-trip serialization (dict -> event -> dict)."""
        original_dict = {
            "event_id": str(uuid4()),
            "event_type": "workflow.triggered",
            "timestamp": "2025-01-27T10:00:00",
            "source": "fastapi",
            "workflow_id": "api_workflow",
            "workflow_run_id": "run_789",
            "payload": {"data": {"action": "start"}},
            "metadata": {"environment": "staging", "version": "1.0"},
        }

        # Create event from dict
        event = WorkflowEvent.model_validate(original_dict)

        # Serialize back to dict
        serialized_dict = event.model_dump()

        # Compare key fields (UUID and timestamp may have different formats)
        assert serialized_dict["event_type"] == original_dict["event_type"]
        assert serialized_dict["source"] == original_dict["source"]
        assert serialized_dict["workflow_id"] == original_dict["workflow_id"]
        assert serialized_dict["workflow_run_id"] == original_dict["workflow_run_id"]
        assert serialized_dict["payload"] == original_dict["payload"]
        assert serialized_dict["metadata"] == original_dict["metadata"]


class TestEventSchemaVersioning:
    """Test schema versioning support."""

    def test_version_field(self):
        """Test version field in metadata."""
        metadata = WorkflowEventMetadata(environment="dev", version="1.0")
        assert metadata.version == "1.0"

    def test_custom_version(self):
        """Test custom version value."""
        metadata = WorkflowEventMetadata(environment="dev", version="2.0")
        assert metadata.version == "2.0"

    def test_version_in_event(self):
        """Test version is included in event."""
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_COMPLETED,
            source=EventSource.AIRFLOW,
            workflow_id="test",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(data={}),
            metadata=WorkflowEventMetadata(environment="dev", version="1.5"),
        )

        assert event.metadata.version == "1.5"
        assert event.model_dump()["metadata"]["version"] == "1.5"


class TestEventValidation:
    """Test event validation edge cases."""

    def test_empty_workflow_id(self):
        """Test empty workflow_id is allowed (may be valid in some cases)."""
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(data={}),
            metadata=WorkflowEventMetadata(environment="dev"),
        )
        assert event.workflow_id == ""

    def test_complex_payload_data(self):
        """Test event with complex nested payload data."""
        complex_data = {
            "tasks": [
                {"id": 1, "status": "completed"},
                {"id": 2, "status": "running"},
            ],
            "metadata": {"start_time": "2025-01-27T10:00:00"},
        }

        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_COMPLETED,
            source=EventSource.AIRFLOW,
            workflow_id="complex_dag",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(data=complex_data),
            metadata=WorkflowEventMetadata(environment="dev"),
        )

        assert len(event.payload.data["tasks"]) == 2
        assert event.payload.data["metadata"]["start_time"] == "2025-01-27T10:00:00"

    def test_all_event_types(self):
        """Test creating events with all event types."""
        for event_type in EventType:
            event = WorkflowEvent(
                event_type=event_type,
                source=EventSource.AIRFLOW,
                workflow_id="test",
                workflow_run_id="run_123",
                payload=WorkflowEventPayload(data={}),
                metadata=WorkflowEventMetadata(environment="dev"),
            )
            assert event.event_type == event_type

    def test_all_event_sources(self):
        """Test creating events with all event sources."""
        for source in EventSource:
            event = WorkflowEvent(
                event_type=EventType.WORKFLOW_TRIGGERED,
                source=source,
                workflow_id="test",
                workflow_run_id="run_123",
                payload=WorkflowEventPayload(data={}),
                metadata=WorkflowEventMetadata(environment="dev"),
            )
            assert event.source == source

