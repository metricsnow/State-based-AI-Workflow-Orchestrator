"""
Task Decorators for Airflow-Kafka Integration

This module provides decorators for automatically publishing workflow events
from Airflow tasks. Includes decorators for task completion events and
DAG completion events.
"""

import logging
from typing import Callable, Any, Optional
from functools import wraps

from airflow.decorators import task
from airflow.models import TaskInstance

from .kafka_utils import publish_task_completion_event

logger = logging.getLogger(__name__)


def with_kafka_event_publishing(
    event_type: Optional[str] = None,
    topic: str = "workflow-events",
    bootstrap_servers: Optional[str] = None,
):
    """Decorator to automatically publish Kafka events for task completion.

    This decorator wraps a TaskFlow task function and automatically publishes
    a workflow event to Kafka when the task completes (success or failure).

    Args:
        event_type: Optional event type override. If None, uses default based on task status
        topic: Kafka topic name (default: 'workflow-events')
        bootstrap_servers: Kafka broker address. If None, uses default from environment

    Returns:
        Decorated function that publishes events on completion

    Example:
        ```python
        @task
        @with_kafka_event_publishing()
        def my_task(**context):
            # Task logic here
            return result
        ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract context if available
            context = kwargs.get("context") or {}
            ti: Optional[TaskInstance] = context.get("ti")
            dag_run = context.get("dag_run")

            # Get task and DAG information
            task_id = None
            dag_id = None
            dag_run_id = None

            if ti:
                task_id = ti.task_id
                dag_id = ti.dag_id
                dag_run_id = ti.dag_run_id
            elif dag_run:
                dag_id = dag_run.dag_id
                dag_run_id = dag_run.run_id

            # Execute the original function
            result = None
            task_status = "success"
            error_message = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                task_status = "failed"
                error_message = str(e)
                logger.error(f"Task {task_id} failed: {e}", exc_info=True)
                raise
            finally:
                # Publish event regardless of success/failure
                if task_id and dag_id and dag_run_id:
                    try:
                        publish_task_completion_event(
                            task_id=task_id,
                            dag_id=dag_id,
                            dag_run_id=dag_run_id,
                            task_result=result,
                            task_status=task_status,
                            error_message=error_message,
                            topic=topic,
                            bootstrap_servers=bootstrap_servers,
                        )
                    except Exception as e:
                        # Don't fail the task if event publishing fails
                        logger.warning(
                            f"Failed to publish event for task {task_id}: {e}",
                            exc_info=True,
                        )

        return wrapper

    return decorator


def publish_event_from_context(
    event_type: str,
    payload: dict,
    topic: str = "workflow-events",
    bootstrap_servers: Optional[str] = None,
    **context,
) -> bool:
    """Helper function to publish workflow events from within Airflow tasks.

    This function extracts DAG and task information from Airflow context
    and publishes a workflow event to Kafka.

    Args:
        event_type: Event type string (e.g., 'workflow.completed', 'workflow.failed')
        payload: Event payload dictionary
        topic: Kafka topic name (default: 'workflow-events')
        bootstrap_servers: Kafka broker address. If None, uses default from environment
        **context: Airflow context variables (ti, dag_run, etc.)

    Returns:
        True if event was published successfully, False otherwise

    Example:
        ```python
        @task
        def my_task(**context):
            # Task logic here
            result = process_data()
            
            # Publish event
            from airflow_integration import publish_event_from_context
            from workflow_events import EventType
            
            publish_event_from_context(
                event_type=EventType.WORKFLOW_COMPLETED.value,
                payload={"result": result},
                **context
            )
            
            return result
        ```
    """
    from workflow_events import EventType
    from .kafka_utils import publish_workflow_event

    try:
        # Extract context information
        ti = context.get("ti")
        dag_run = context.get("dag_run")

        if not ti and not dag_run:
            logger.warning("No context information available for event publishing")
            return False

        # Get workflow information
        if ti:
            workflow_id = ti.dag_id
            workflow_run_id = ti.dag_run_id
        elif dag_run:
            workflow_id = dag_run.dag_id
            workflow_run_id = dag_run.run_id
        else:
            logger.warning("Could not determine workflow ID and run ID")
            return False

        # Convert event_type string to EventType enum
        try:
            event_type_enum = EventType(event_type)
        except ValueError:
            logger.error(f"Invalid event type: {event_type}")
            return False

        # Publish event
        return publish_workflow_event(
            event_type=event_type_enum,
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
            payload=payload,
            topic=topic,
            bootstrap_servers=bootstrap_servers,
        )

    except Exception as e:
        logger.error(f"Error publishing event from context: {e}", exc_info=True)
        return False

