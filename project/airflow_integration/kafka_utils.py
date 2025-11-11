"""
Kafka Utilities for Airflow Integration

This module provides reusable utilities for publishing workflow events to Kafka
from Airflow tasks. Includes functions for task completion events, DAG completion
events, and general workflow event publishing.

Key Features:
- Automatic context extraction from Airflow tasks
- Error handling that doesn't fail Airflow tasks
- Environment variable configuration
- Reusable producer management
"""

import os
import logging
from typing import Dict, Any, Optional

from workflow_events import (
    WorkflowEventProducer,
    WorkflowEvent,
    EventType,
    EventSource,
    WorkflowEventPayload,
    WorkflowEventMetadata,
)

logger = logging.getLogger(__name__)


def get_kafka_producer(
    bootstrap_servers: Optional[str] = None,
) -> WorkflowEventProducer:
    """Get Kafka producer instance.

    Creates a Kafka producer instance using configuration from environment variables.
    Falls back to default localhost:9092 if not configured.

    Args:
        bootstrap_servers: Kafka broker address. If None, reads from
            KAFKA_BOOTSTRAP_SERVERS environment variable or defaults to 'localhost:9092'

    Returns:
        WorkflowEventProducer instance

    Raises:
        Exception: If producer creation fails (should be caught by caller)
    """
    if bootstrap_servers is None:
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

    try:
        producer = WorkflowEventProducer(bootstrap_servers=bootstrap_servers)
        logger.debug(f"Created Kafka producer for {bootstrap_servers}")
        return producer
    except Exception as e:
        logger.error(f"Failed to create Kafka producer: {e}")
        raise


def publish_workflow_event(
    event_type: EventType,
    workflow_id: str,
    workflow_run_id: str,
    payload: Dict[str, Any],
    metadata: Optional[Dict[str, str]] = None,
    topic: str = "workflow-events",
    bootstrap_servers: Optional[str] = None,
) -> bool:
    """Publish a workflow event to Kafka.

    Generic function for publishing any type of workflow event to Kafka.
    Handles errors gracefully and logs failures without raising exceptions.

    Args:
        event_type: Type of workflow event (EventType enum)
        workflow_id: Identifier of the workflow (e.g., DAG ID)
        workflow_run_id: Identifier of the specific workflow run
        payload: Event payload data (will be wrapped in WorkflowEventPayload)
        metadata: Optional metadata dictionary. If None, uses default metadata
            from environment variables
        topic: Kafka topic name (default: 'workflow-events')
        bootstrap_servers: Kafka broker address. If None, uses get_kafka_producer default

    Returns:
        True if event was published successfully, False otherwise

    Note:
        This function never raises exceptions. All errors are logged and False is returned.
        This ensures Airflow tasks don't fail due to Kafka publishing issues.
    """
    producer = None
    try:
        producer = get_kafka_producer(bootstrap_servers=bootstrap_servers)

        # Build metadata
        if metadata is None:
            environment = os.getenv("ENVIRONMENT", "dev")
            version = os.getenv("EVENT_SCHEMA_VERSION", "1.0")
            event_metadata = WorkflowEventMetadata(
                environment=environment, version=version
            )
        else:
            event_metadata = WorkflowEventMetadata(**metadata)

        # Create event
        event = WorkflowEvent(
            event_type=event_type,
            source=EventSource.AIRFLOW,
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
            payload=WorkflowEventPayload(data=payload),
            metadata=event_metadata,
        )

        # Publish event
        success = producer.publish_event(event, topic=topic)
        if success:
            logger.info(
                f"Published {event_type.value} event for workflow {workflow_id}, "
                f"run {workflow_run_id}"
            )
        else:
            logger.warning(
                f"Failed to publish {event_type.value} event for workflow {workflow_id}, "
                f"run {workflow_run_id}"
            )

        return success

    except Exception as e:
        logger.error(
            f"Error publishing workflow event {event_type.value} for "
            f"workflow {workflow_id}, run {workflow_run_id}: {e}",
            exc_info=True,
        )
        return False
    finally:
        if producer:
            try:
                producer.close()
            except Exception as e:
                logger.warning(f"Error closing producer: {e}")


def publish_task_completion_event(
    task_id: str,
    dag_id: str,
    dag_run_id: str,
    task_result: Optional[Any] = None,
    task_status: str = "success",
    error_message: Optional[str] = None,
    topic: str = "workflow-events",
    bootstrap_servers: Optional[str] = None,
) -> bool:
    """Publish a task completion event to Kafka.

    Convenience function for publishing task completion events from Airflow tasks.
    Extracts workflow information and publishes appropriate event type based on status.

    Args:
        task_id: Airflow task ID
        dag_id: Airflow DAG ID
        dag_run_id: Airflow DAG run ID
        task_result: Optional task result data to include in payload
        task_status: Task status ('success', 'failed', etc.)
        error_message: Optional error message if task failed
        topic: Kafka topic name (default: 'workflow-events')
        bootstrap_servers: Kafka broker address. If None, uses get_kafka_producer default

    Returns:
        True if event was published successfully, False otherwise

    Note:
        This function never raises exceptions. All errors are logged and False is returned.
    """
    try:
        # Build payload
        payload: Dict[str, Any] = {
            "task_id": task_id,
            "status": task_status,
        }

        if task_result is not None:
            # Try to serialize task result
            if isinstance(task_result, dict):
                payload["result"] = task_result
            elif isinstance(task_result, (str, int, float, bool)):
                payload["result"] = task_result
            else:
                # For complex types, convert to string representation
                payload["result"] = str(task_result)

        if error_message:
            payload["error"] = error_message

        # Determine event type based on status
        if task_status == "success":
            event_type = EventType.WORKFLOW_COMPLETED
        else:
            event_type = EventType.WORKFLOW_FAILED

        return publish_workflow_event(
            event_type=event_type,
            workflow_id=dag_id,
            workflow_run_id=dag_run_id,
            payload=payload,
            topic=topic,
            bootstrap_servers=bootstrap_servers,
        )

    except Exception as e:
        logger.error(
            f"Error publishing task completion event for task {task_id}, "
            f"DAG {dag_id}, run {dag_run_id}: {e}",
            exc_info=True,
        )
        return False


def publish_dag_completion_event(
    dag_id: str,
    dag_run_id: str,
    dag_status: str = "success",
    task_results: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None,
    topic: str = "workflow-events",
    bootstrap_servers: Optional[str] = None,
) -> bool:
    """Publish a DAG completion event to Kafka.

    Convenience function for publishing DAG completion events from Airflow DAGs.
    Publishes appropriate event type based on DAG run status.

    Args:
        dag_id: Airflow DAG ID
        dag_run_id: Airflow DAG run ID
        dag_status: DAG run status ('success', 'failed', etc.)
        task_results: Optional dictionary of task results to include in payload
        error_message: Optional error message if DAG failed
        topic: Kafka topic name (default: 'workflow-events')
        bootstrap_servers: Kafka broker address. If None, uses get_kafka_producer default

    Returns:
        True if event was published successfully, False otherwise

    Note:
        This function never raises exceptions. All errors are logged and False is returned.
    """
    try:
        # Build payload
        payload: Dict[str, Any] = {
            "dag_id": dag_id,
            "status": dag_status,
        }

        if task_results:
            payload["task_results"] = task_results

        if error_message:
            payload["error"] = error_message

        # Determine event type based on status
        if dag_status == "success":
            event_type = EventType.WORKFLOW_COMPLETED
        else:
            event_type = EventType.WORKFLOW_FAILED

        return publish_workflow_event(
            event_type=event_type,
            workflow_id=dag_id,
            workflow_run_id=dag_run_id,
            payload=payload,
            topic=topic,
            bootstrap_servers=bootstrap_servers,
        )

    except Exception as e:
        logger.error(
            f"Error publishing DAG completion event for DAG {dag_id}, "
            f"run {dag_run_id}: {e}",
            exc_info=True,
        )
        return False

