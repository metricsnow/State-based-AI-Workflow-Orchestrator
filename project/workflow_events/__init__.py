"""
Workflow Events Module

This module provides event schema definitions for workflow events published to Kafka.
Includes Pydantic models for type-safe event validation and serialization.
"""

from .schema import (
    EventType,
    EventSource,
    WorkflowEventPayload,
    WorkflowEventMetadata,
    WorkflowEvent,
)
from .schema_utils import (
    generate_json_schema,
    save_json_schema,
    get_validation_schema,
    get_serialization_schema,
)
from .producer import WorkflowEventProducer

__all__ = [
    "EventType",
    "EventSource",
    "WorkflowEventPayload",
    "WorkflowEventMetadata",
    "WorkflowEvent",
    "WorkflowEventProducer",
    "generate_json_schema",
    "save_json_schema",
    "get_validation_schema",
    "get_serialization_schema",
]

