"""Event processing logic for LangGraph workflows.

This module handles conversion of Kafka workflow events to LangGraph state
and execution of LangGraph workflows.
"""

import asyncio
import logging
from typing import Any, Dict

from workflow_events import WorkflowEvent, EventType
from langgraph_workflows.state import MultiAgentState
from langgraph_workflows.multi_agent_workflow import multi_agent_graph

logger = logging.getLogger(__name__)


def event_to_multi_agent_state(event: WorkflowEvent) -> MultiAgentState:
    """Convert WorkflowEvent to MultiAgentState for LangGraph execution.
    
    Extracts task information and metadata from the workflow event and creates
    a properly structured MultiAgentState for LangGraph workflow execution.
    
    Args:
        event: WorkflowEvent from Kafka containing workflow trigger data.
    
    Returns:
        MultiAgentState initialized with event data for workflow execution.
    """
    payload_data = event.payload.data
    
    # Extract task from payload, default to generic task if not provided
    task = payload_data.get("task", "process_workflow")
    
    # If payload has nested 'data' with 'task', use that
    if isinstance(payload_data.get("data"), dict):
        task = payload_data.get("data", {}).get("task", task)
    
    # Build metadata from event
    metadata: Dict[str, Any] = {
        "event_id": str(event.event_id),
        "workflow_id": event.workflow_id,
        "workflow_run_id": event.workflow_run_id,
        "source": event.source.value,
        "timestamp": event.timestamp.isoformat() if hasattr(event.timestamp, 'isoformat') else str(event.timestamp),
    }
    
    # Add any additional metadata from event metadata
    if hasattr(event.metadata, 'model_dump'):
        metadata.update(event.metadata.model_dump())
    elif isinstance(event.metadata, dict):
        metadata.update(event.metadata)
    
    return MultiAgentState(
        messages=[],
        task=task,
        agent_results={},
        current_agent="orchestrator",
        completed=False,
        metadata=metadata,
    )


class WorkflowProcessor:
    """Processes workflow events by executing LangGraph workflows.
    
    This class handles the execution of LangGraph workflows triggered by
    Kafka workflow events. It converts events to state, executes workflows,
    and handles errors gracefully.
    
    Attributes:
        None - stateless processor for workflow execution.
    """
    
    async def process_workflow_event(self, event: WorkflowEvent) -> Dict[str, Any]:
        """Process a workflow event by executing LangGraph workflow.
        
        Converts the workflow event to LangGraph state, executes the workflow
        asynchronously, and returns the result. Errors are logged but don't
        stop the consumer from processing other events.
        
        Args:
            event: WorkflowEvent to process.
        
        Returns:
            Dictionary containing workflow execution result.
        
        Raises:
            Exception: If workflow execution fails (logged but not re-raised).
        """
        try:
            logger.info(
                f"Processing workflow event: {event.event_id} "
                f"for workflow: {event.workflow_id}"
            )
            
            # Convert event to LangGraph state
            initial_state = event_to_multi_agent_state(event)
            
            # Create thread ID from event ID for checkpointing
            thread_id = str(event.event_id)
            config = {"configurable": {"thread_id": thread_id}}
            
            # Execute workflow in thread pool to avoid blocking event loop
            # LangGraph workflows are synchronous, so we run them in a thread
            logger.debug(
                f"Executing LangGraph workflow with thread_id: {thread_id}"
            )
            result = await asyncio.to_thread(
                multi_agent_graph.invoke,
                initial_state,
                config=config,
            )
            
            logger.info(
                f"Workflow completed successfully: {event.event_id}, "
                f"completed: {result.get('completed', False)}"
            )
            
            # TODO: Publish result to result topic (TASK-028)
            return result
        
        except Exception as e:
            logger.error(
                f"Error processing workflow event {event.event_id}: {e}",
                exc_info=True,
            )
            # Re-raise to allow caller to handle (e.g., dead letter queue)
            raise

