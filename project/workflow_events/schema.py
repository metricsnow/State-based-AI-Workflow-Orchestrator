"""
Workflow Event Schema Definitions

This module defines the event schema for workflow events published to Kafka.
Uses Pydantic for validation, serialization, and JSON schema generation.
"""

from enum import Enum
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_serializer, ConfigDict


class EventType(str, Enum):
    """Enumeration of workflow event types."""

    WORKFLOW_TRIGGERED = "workflow.triggered"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_RESULT = "workflow.result"


class EventSource(str, Enum):
    """Enumeration of workflow event sources."""

    AIRFLOW = "airflow"
    LANGGRAPH = "langgraph"
    FASTAPI = "fastapi"


class WorkflowEventPayload(BaseModel):
    """Payload structure for workflow events.

    Contains workflow-specific data in a flexible dictionary format.
    """

    data: Dict[str, Any] = Field(
        ...,
        description="Workflow-specific data payload",
        examples=[{"status": "success", "count": 100}],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"data": {"status": "success", "count": 100}},
                {"data": {"error": "Task failed", "retry_count": 3}},
            ]
        }
    )


class WorkflowEventMetadata(BaseModel):
    """Metadata structure for workflow events.

    Contains environment and version information for event tracking.
    """

    environment: str = Field(
        ...,
        pattern="^(dev|staging|prod)$",
        description="Environment where the event was generated",
        examples=["dev", "staging", "prod"],
    )
    version: str = Field(
        default="1.0",
        description="Schema version for event evolution",
        examples=["1.0"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"environment": "dev", "version": "1.0"},
                {"environment": "prod", "version": "1.0"},
            ]
        }
    )


class WorkflowEvent(BaseModel):
    """Main workflow event model.

    Represents a standardized event structure for workflow events published to Kafka.
    All fields are validated and serialized according to the schema definition.
    """

    event_id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for the event",
    )
    event_type: EventType = Field(
        ...,
        description="Type of workflow event",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="ISO 8601 timestamp when the event was generated",
    )
    source: EventSource = Field(
        ...,
        description="Source system that generated the event",
    )
    workflow_id: str = Field(
        ...,
        description="Identifier of the workflow (e.g., DAG ID or workflow ID)",
        examples=["example_dag", "workflow_123"],
    )
    workflow_run_id: str = Field(
        ...,
        description="Identifier of the specific workflow run",
        examples=["run_123", "2025-01-27T10:00:00"],
    )
    payload: WorkflowEventPayload = Field(
        ...,
        description="Workflow-specific data payload",
    )
    metadata: WorkflowEventMetadata = Field(
        ...,
        description="Event metadata including environment and version",
    )

    @field_serializer("event_id")
    def serialize_event_id(self, value: UUID) -> str:
        """Serialize UUID to string for JSON compatibility."""
        return str(value)

    @field_serializer("timestamp")
    def serialize_timestamp(self, value: datetime) -> str:
        """Serialize datetime to ISO 8601 format."""
        return value.isoformat()

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "event_id": "123e4567-e89b-12d3-a456-426614174000",
                    "event_type": "workflow.triggered",
                    "timestamp": "2025-01-27T10:00:00",
                    "source": "airflow",
                    "workflow_id": "example_dag",
                    "workflow_run_id": "run_123",
                    "payload": {"data": {"status": "success"}},
                    "metadata": {"environment": "dev", "version": "1.0"},
                }
            ]
        }
    )

    def model_dump_json(self, **kwargs) -> str:
        """Serialize model to JSON string with proper encoding."""
        return super().model_dump_json(**kwargs)

    @classmethod
    def model_validate_json(cls, json_data: str | bytes) -> "WorkflowEvent":
        """Deserialize JSON string to WorkflowEvent model."""
        return super().model_validate_json(json_data)


class WorkflowResultEvent(BaseModel):
    """Result event for workflow results.
    
    Represents a standardized result event structure for workflow results
    published to Kafka result topic. Used to return workflow execution results
    to Airflow tasks via correlation ID matching.
    
    Attributes:
        correlation_id: Event ID from the original trigger event (for matching)
        workflow_id: Identifier of the workflow
        workflow_run_id: Identifier of the specific workflow run
        result: Workflow result data dictionary
        status: Result status ('success', 'failure', 'error')
        timestamp: ISO 8601 timestamp when the result was generated
        error: Optional error message if status is 'error'
    """
    
    correlation_id: UUID = Field(
        ...,
        description="Event ID from trigger event (for correlation)",
    )
    workflow_id: str = Field(
        ...,
        description="Identifier of the workflow",
        examples=["example_dag", "workflow_123"],
    )
    workflow_run_id: str = Field(
        ...,
        description="Identifier of the specific workflow run",
        examples=["run_123", "2025-01-27T10:00:00"],
    )
    result: Dict[str, Any] = Field(
        ...,
        description="Workflow result data",
        examples=[{"completed": True, "agent_results": {}}],
    )
    status: str = Field(
        ...,
        description="Result status: success, failure, or error",
        pattern="^(success|failure|error)$",
        examples=["success", "failure", "error"],
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="ISO 8601 timestamp when the result was generated",
    )
    error: Optional[str] = Field(
        None,
        description="Error message if status is 'error'",
        examples=[None, "Workflow execution failed"],
    )
    
    @field_serializer("correlation_id")
    def serialize_correlation_id(self, value: UUID) -> str:
        """Serialize UUID to string for JSON compatibility."""
        return str(value)
    
    @field_serializer("timestamp")
    def serialize_timestamp(self, value: datetime) -> str:
        """Serialize datetime to ISO 8601 format."""
        return value.isoformat()
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
                    "workflow_id": "example_dag",
                    "workflow_run_id": "run_123",
                    "result": {"completed": True, "agent_results": {}},
                    "status": "success",
                    "timestamp": "2025-01-27T10:00:00",
                    "error": None,
                },
                {
                    "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
                    "workflow_id": "example_dag",
                    "workflow_run_id": "run_123",
                    "result": {},
                    "status": "error",
                    "timestamp": "2025-01-27T10:00:00",
                    "error": "Workflow execution failed",
                },
            ]
        }
    )
    
    def model_dump_json(self, **kwargs) -> str:
        """Serialize model to JSON string with proper encoding."""
        return super().model_dump_json(**kwargs)
    
    @classmethod
    def model_validate_json(cls, json_data: str | bytes) -> "WorkflowResultEvent":
        """Deserialize JSON string to WorkflowResultEvent model."""
        return super().model_validate_json(json_data)

