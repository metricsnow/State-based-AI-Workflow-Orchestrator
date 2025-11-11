"""
Task Helper Functions for Airflow-Kafka Integration

This module provides helper functions for publishing workflow events from
Airflow TaskFlow tasks. These functions are designed to work seamlessly with
TaskFlow API context access patterns.
"""

import logging
from typing import Dict, Any, Optional

from workflow_events import EventType

from .kafka_utils import publish_workflow_event

logger = logging.getLogger(__name__)


def publish_event_from_taskflow_context(
    event_type: EventType,
    payload: Dict[str, Any],
    topic: str = "workflow-events",
    bootstrap_servers: Optional[str] = None,
    dag_id: Optional[str] = None,
    dag_run_id: Optional[str] = None,
    **kwargs,
) -> bool:
    """Publish workflow event from TaskFlow task context.

    This helper function is designed to work with Airflow TaskFlow API tasks.
    It can extract DAG and run information from context variables passed as
    keyword arguments, or accept them explicitly.

    Args:
        event_type: EventType enum value (e.g., EventType.WORKFLOW_COMPLETED)
        payload: Event payload dictionary
        topic: Kafka topic name (default: 'workflow-events')
        bootstrap_servers: Kafka broker address. If None, uses default from environment
        dag_id: Optional DAG ID. If None, tries to extract from context kwargs
        dag_run_id: Optional DAG run ID. If None, tries to extract from context kwargs
        **kwargs: Additional context variables (dag_run, ti, etc.)

    Returns:
        True if event was published successfully, False otherwise

    Example:
        ```python
        @task
        def my_task(**context):
            # Task logic here
            result = process_data()
            
            # Publish event using context
            from airflow_integration import publish_event_from_taskflow_context
            from workflow_events import EventType
            
            publish_event_from_taskflow_context(
                event_type=EventType.WORKFLOW_COMPLETED,
                payload={"result": result},
                **context
            )
            
            return result
        ```

    Example with explicit DAG info:
        ```python
        @task
        def my_task(dag_run=None, **context):
            result = process_data()
            
            publish_event_from_taskflow_context(
                event_type=EventType.WORKFLOW_COMPLETED,
                payload={"result": result},
                dag_id=dag_run.dag_id if dag_run else None,
                dag_run_id=dag_run.run_id if dag_run else None,
            )
            
            return result
        ```
    """
    try:
        # Try to extract DAG information from context
        if not dag_id or not dag_run_id:
            dag_run = kwargs.get("dag_run")
            ti = kwargs.get("ti")

            if dag_run:
                dag_id = dag_run.dag_id
                dag_run_id = dag_run.run_id
            elif ti:
                dag_id = ti.dag_id
                dag_run_id = ti.dag_run_id

        if not dag_id or not dag_run_id:
            logger.warning(
                "Could not determine DAG ID and run ID from context. "
                "Event will not be published."
            )
            return False

        # Publish event
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
            f"Error publishing event from TaskFlow context: {e}",
            exc_info=True,
        )
        return False

