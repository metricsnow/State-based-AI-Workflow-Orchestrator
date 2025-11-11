"""Airflow task function for triggering LangGraph workflows via Kafka.

This module provides a reusable Airflow task function that triggers LangGraph
workflows by publishing events to Kafka and polling for results. Integrates
the existing Airflow-Kafka integration (Phase 1) with LangGraph workflow
triggering and result retrieval mechanisms (Phase 3).

Key Features:
- Publishes workflow trigger events to Kafka
- Polls for workflow results with timeout
- Error handling for timeouts and failures
- TaskFlow API compatibility
- Automatic context extraction from Airflow
"""

import logging
import os
from typing import Any, Dict, Optional
from uuid import UUID

from airflow.decorators import task
from workflow_events import (
    WorkflowEvent,
    WorkflowEventProducer,
    EventType,
    EventSource,
    WorkflowEventPayload,
    WorkflowEventMetadata,
)
from airflow_integration.result_poller import WorkflowResultPoller

logger = logging.getLogger(__name__)


def _trigger_langgraph_workflow_impl(
    task_data: Dict[str, Any],
    workflow_id: Optional[str] = None,
    timeout: int = 300,
    **context,
) -> Dict[str, Any]:
    """Internal implementation of trigger_langgraph_workflow.
    
    This function contains the core logic and can be tested independently
    of the @task decorator. The @task decorated function calls this.
    
    Args:
        task_data: Data to pass to LangGraph workflow
        workflow_id: Optional workflow ID override
        timeout: Timeout in seconds for result polling
        **context: Airflow context
    
    Returns:
        Dict containing workflow result data
    
    Raises:
        ValueError: If Airflow context is not available
        RuntimeError: If workflow execution failed or event publishing failed
        TimeoutError: If result not received within timeout period
    """
    # Extract DAG context
    dag_run = context.get("dag_run")
    dag = context.get("dag")
    
    if not dag_run or not dag:
        error_msg = "Airflow context not available. Ensure this function is called from within a DAG."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Use DAG ID as workflow_id if not provided
    if workflow_id is None:
        workflow_id = dag.dag_id
    
    workflow_run_id = dag_run.run_id
    
    # Get Kafka configuration
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    event_topic = os.getenv("KAFKA_WORKFLOW_EVENTS_TOPIC", "workflow-events")
    
    # Create event payload
    # The payload structure matches what LangGraph processor expects
    payload_data = {
        "task": task_data.get("task", "process_workflow"),
        "data": task_data,
    }
    
    # Create workflow event
    environment = os.getenv("ENVIRONMENT", "dev")
    version = os.getenv("EVENT_SCHEMA_VERSION", "1.0")
    
    event = WorkflowEvent(
        event_type=EventType.WORKFLOW_TRIGGERED,
        source=EventSource.AIRFLOW,
        workflow_id=workflow_id,
        workflow_run_id=workflow_run_id,
        payload=WorkflowEventPayload(data=payload_data),
        metadata=WorkflowEventMetadata(environment=environment, version=version),
    )
    
    correlation_id = event.event_id
    
    logger.info(
        f"Triggering LangGraph workflow: workflow_id={workflow_id}, "
        f"workflow_run_id={workflow_run_id}, correlation_id={correlation_id}"
    )
    
    # Publish trigger event
    producer = None
    try:
        producer = WorkflowEventProducer(bootstrap_servers=bootstrap_servers)
        
        success = producer.publish_event(event, topic=event_topic, timeout=10)
        
        if not success:
            error_msg = f"Failed to publish workflow trigger event: correlation_id={correlation_id}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        logger.info(
            f"Published workflow trigger event: correlation_id={correlation_id}, "
            f"workflow_id={workflow_id}"
        )
    
    except Exception as e:
        error_msg = f"Failed to publish workflow event: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e
    
    finally:
        if producer:
            try:
                producer.close()
            except Exception as e:
                logger.warning(f"Error closing producer: {e}")
    
    # Poll for result
    try:
        result_topic = os.getenv("KAFKA_WORKFLOW_RESULTS_TOPIC", "workflow-results")
        
        poller = WorkflowResultPoller(
            bootstrap_servers=bootstrap_servers,
            topic=result_topic,
            timeout=timeout,
        )
        
        logger.info(
            f"Polling for result: correlation_id={correlation_id}, "
            f"timeout={timeout}s"
        )
        
        result = poller.poll_for_result(
            correlation_id=correlation_id,
            workflow_id=workflow_id,
        )
        
        if result is None:
            error_msg = (
                f"Workflow result not received within {timeout} seconds. "
                f"correlation_id={correlation_id}, workflow_id={workflow_id}"
            )
            logger.error(error_msg)
            raise TimeoutError(error_msg)
        
        # Check result status
        result_status = result.get("status")
        if result_status != "success":
            error_msg = result.get("error", "Unknown error")
            full_error = (
                f"Workflow execution failed: status={result_status}, "
                f"error={error_msg}, correlation_id={correlation_id}"
            )
            logger.error(full_error)
            raise RuntimeError(full_error)
        
        # Extract result data
        result_data = result.get("result", {})
        
        logger.info(
            f"Workflow completed successfully: correlation_id={correlation_id}, "
            f"workflow_id={workflow_id}"
        )
        
        return result_data
    
    except TimeoutError:
        # Re-raise timeout errors as-is
        raise
    
    except RuntimeError:
        # Re-raise runtime errors as-is
        raise
    
    except Exception as e:
        error_msg = f"Error retrieving workflow result: {e}, correlation_id={correlation_id}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e


@task
def trigger_langgraph_workflow(
    task_data: Dict[str, Any],
    workflow_id: Optional[str] = None,
    timeout: int = 300,
    **context,
) -> Dict[str, Any]:
    """Trigger LangGraph workflow via Kafka and wait for result.
    
    This is the Airflow @task decorated function that calls the internal
    implementation. The decorator makes this function usable as an Airflow task.
    
    Args:
        task_data: Data to pass to LangGraph workflow (included in event payload).
            Should contain workflow-specific data like task description, input data, etc.
        workflow_id: Optional workflow ID override. If None, uses DAG ID from context.
        timeout: Timeout in seconds for result polling (default: 300 seconds / 5 minutes).
        **context: Airflow context (automatically provided by TaskFlow API).
            Contains 'dag_run', 'dag', 'ti', etc.
    
    Returns:
        Dict containing workflow result data with keys:
            - 'completed': Boolean indicating workflow completion
            - 'agent_results': Dictionary of agent results
            - 'task': Task description
            - 'metadata': Additional metadata
    
    Raises:
        ValueError: If Airflow context is not available
        RuntimeError: If workflow execution failed or event publishing failed
        TimeoutError: If result not received within timeout period
    
    Example:
        ```python
        from airflow_integration.langgraph_trigger import trigger_langgraph_workflow
        
        @dag(...)
        def my_dag():
            @task
            def prepare_data():
                return {
                    "task": "analyze_trading_data",
                    "data": {"symbol": "AAPL", "date_range": "2025-01-01:2025-01-31"}
                }
            
            data = prepare_data()
            result = trigger_langgraph_workflow(
                task_data=data,
                timeout=600  # 10 minutes
            )
        ```
    """
    return _trigger_langgraph_workflow_impl(
        task_data=task_data,
        workflow_id=workflow_id,
        timeout=timeout,
        **context,
    )

