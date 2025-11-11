"""
Airflow-Kafka Integration Module

This module provides utilities for integrating Kafka event publishing into Airflow DAGs.
Includes reusable functions and decorators for publishing workflow events from Airflow tasks.
"""

from .kafka_utils import (
    get_kafka_producer,
    publish_workflow_event,
    publish_task_completion_event,
    publish_dag_completion_event,
)
from .task_helpers import publish_event_from_taskflow_context

__all__ = [
    "get_kafka_producer",
    "publish_workflow_event",
    "publish_task_completion_event",
    "publish_dag_completion_event",
    "publish_event_from_taskflow_context",
]

