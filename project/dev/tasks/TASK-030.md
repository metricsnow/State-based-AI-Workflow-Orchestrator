# TASK-030: Create Airflow Task for Triggering LangGraph Workflows

## Task Information
- **Task ID**: TASK-030
- **Created**: 2025-01-27
- **Status**: Waiting
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 3-4 hours
- **Actual Time**: TBD
- **Type**: Integration
- **Dependencies**: TASK-028 ✅, TASK-029 ✅
- **Parent PRD**: `project/docs/prd_phase3.md` - Milestone 1.6

## Task Description
Create Airflow task function that triggers LangGraph workflows via Kafka event publishing and polls for results. This integrates the existing Airflow-Kafka integration (Phase 1) with the new LangGraph workflow triggering and result retrieval mechanisms.

## Problem Statement
Airflow tasks need a simple, reusable way to trigger LangGraph workflows and retrieve results. This task creates a helper function that combines event publishing (existing) with result polling (TASK-028) to provide a complete integration pattern for Airflow DAGs.

## Requirements

### Functional Requirements
- [ ] Airflow task function to trigger LangGraph workflow
- [ ] Event publishing to Kafka
- [ ] Result polling with timeout
- [ ] Error handling for timeouts and failures
- [ ] Reusable utility function
- [ ] TaskFlow API compatibility
- [ ] Example DAG demonstrating usage

### Technical Requirements
- [ ] Integration with existing `airflow_integration` module
- [ ] Use existing `WorkflowEventProducer`
- [ ] Use `WorkflowResultPoller` from TASK-028
- [ ] Proper error handling and logging
- [ ] Configuration via environment variables
- [ ] Type hints and documentation

## Implementation Plan

### Phase 1: Analysis
- [ ] Review existing Airflow-Kafka integration
- [ ] Review result poller from TASK-028
- [ ] Review event schema
- [ ] Design task function interface
- [ ] Plan error handling

### Phase 2: Planning
- [ ] Design task function signature
- [ ] Plan event publishing integration
- [ ] Plan result polling integration
- [ ] Plan error handling
- [ ] Plan configuration

### Phase 3: Implementation
- [ ] Create `trigger_langgraph_workflow` function
- [ ] Integrate event publishing
- [ ] Integrate result polling
- [ ] Add error handling
- [ ] Add logging
- [ ] Create example DAG

### Phase 4: Testing
- [ ] Test function with valid workflow
- [ ] Test timeout handling
- [ ] Test error handling
- [ ] Test with example DAG
- [ ] Integration tests

### Phase 5: Documentation
- [ ] Document function usage
- [ ] Document parameters
- [ ] Document error handling
- [ ] Document example DAG

## Technical Implementation

### Task Function Implementation
```python
# project/airflow_integration/langgraph_trigger.py
import logging
from typing import Dict, Any, Optional
from uuid import UUID

from airflow.decorators import task
from workflow_events import WorkflowEventProducer, EventType, EventSource
from airflow_integration.result_poller import WorkflowResultPoller
import os

logger = logging.getLogger(__name__)


@task
def trigger_langgraph_workflow(
    task_data: Dict[str, Any],
    workflow_id: Optional[str] = None,
    timeout: int = 300,
    **context
) -> Dict[str, Any]:
    """Trigger LangGraph workflow via Kafka and wait for result.
    
    Args:
        task_data: Data to pass to LangGraph workflow (included in event payload)
        workflow_id: Optional workflow ID override (defaults to DAG ID)
        timeout: Timeout in seconds for result polling (default: 300)
        **context: Airflow context (automatically provided)
    
    Returns:
        Dict containing workflow result data
    
    Raises:
        TimeoutError: If result not received within timeout
        RuntimeError: If workflow execution failed
    """
    # Extract DAG context
    dag_run = context.get('dag_run')
    dag = context.get('dag')
    
    if not dag_run or not dag:
        raise ValueError("Airflow context not available")
    
    # Use DAG ID as workflow_id if not provided
    if workflow_id is None:
        workflow_id = dag.dag_id
    
    workflow_run_id = dag_run.run_id
    
    # Create event payload
    payload = {
        "task": task_data.get("task", "process_workflow"),
        "data": task_data
    }
    
    # Publish trigger event
    try:
        producer = WorkflowEventProducer()
        event = producer.publish_workflow_event(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
            payload={"data": payload},
            metadata={
                "environment": os.getenv("ENVIRONMENT", "dev"),
                "version": "1.0"
            }
        )
        
        correlation_id = event.event_id
        logger.info(
            f"Published workflow trigger event: {correlation_id} "
            f"for workflow: {workflow_id}"
        )
    
    except Exception as e:
        logger.error(f"Failed to publish workflow event: {e}", exc_info=True)
        raise RuntimeError(f"Failed to trigger workflow: {e}")
    
    finally:
        producer.close()
    
    # Poll for result
    try:
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        poller = WorkflowResultPoller(
            bootstrap_servers=bootstrap_servers,
            timeout=timeout
        )
        
        result = poller.poll_for_result(
            correlation_id=correlation_id,
            workflow_id=workflow_id
        )
        
        if result is None:
            raise TimeoutError(
                f"Workflow result not received within {timeout} seconds "
                f"for correlation_id: {correlation_id}"
            )
        
        # Check result status
        if result.get("status") != "success":
            error_msg = result.get("error", "Unknown error")
            raise RuntimeError(f"Workflow execution failed: {error_msg}")
        
        logger.info(f"Workflow completed successfully: {correlation_id}")
        return result.get("result", {})
    
    except TimeoutError:
        logger.error(
            f"Timeout waiting for workflow result: {correlation_id}",
            exc_info=True
        )
        raise
    
    except Exception as e:
        logger.error(
            f"Error retrieving workflow result: {e}",
            exc_info=True
        )
        raise
```

### Example DAG Usage
```python
# project/dags/langgraph_integration_dag.py
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow_integration.langgraph_trigger import trigger_langgraph_workflow

@dag(
    dag_id='langgraph_integration_example',
    description='Example DAG demonstrating LangGraph workflow integration',
    schedule=timedelta(days=1),
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['langgraph', 'integration', 'example'],
)
def langgraph_integration_dag():
    @task
    def prepare_data():
        """Prepare data for LangGraph workflow."""
        return {
            "task": "analyze_trading_data",
            "data": {
                "symbol": "AAPL",
                "date_range": "2025-01-01:2025-01-31",
                "analysis_type": "trend_analysis"
            }
        }
    
    @task
    def process_result(result: dict):
        """Process workflow result."""
        print(f"Workflow completed: {result.get('completed', False)}")
        print(f"Agent results: {result.get('agent_results', {})}")
        return result
    
    # Prepare data
    data = prepare_data()
    
    # Trigger LangGraph workflow and wait for result
    workflow_result = trigger_langgraph_workflow(
        task_data=data,
        timeout=600  # 10 minutes
    )
    
    # Process result
    process_result(workflow_result)

langgraph_integration_dag()
```

## Testing

### Manual Testing
- [ ] Test function with valid workflow data
- [ ] Test timeout handling
- [ ] Test error handling (workflow failure)
- [ ] Test with example DAG
- [ ] Verify event published
- [ ] Verify result retrieved

### Automated Testing
- [ ] Unit tests for function
- [ ] Mock Kafka tests
- [ ] Test timeout behavior
- [ ] Test error scenarios
- [ ] Integration tests with test DAG

## Acceptance Criteria
- [ ] Airflow task function created
- [ ] Event publishing integrated
- [ ] Result polling integrated
- [ ] Error handling implemented
- [ ] Timeout handling works
- [ ] Reusable utility function
- [ ] Example DAG created
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Documentation complete

## Dependencies
- **External**: Apache Airflow, kafka-python
- **Internal**: TASK-028 (Result poller), existing Airflow-Kafka integration (Phase 1)

## Risks and Mitigation

### Risk 1: Timeout Too Short
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Make timeout configurable, use reasonable defaults, document timeout requirements

### Risk 2: Result Not Found
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: Implement timeout, add retry logic, log correlation IDs, add monitoring

### Risk 3: Event Publishing Failures
- **Probability**: Low
- **Impact**: High
- **Mitigation**: Use existing error handling from Phase 1, add retry logic, log errors

## Task Status
- [ ] Analysis Complete
- [ ] Planning Complete
- [ ] Implementation Complete
- [ ] Testing Complete
- [ ] Documentation Complete

## Notes
- Reuse existing Airflow-Kafka integration from Phase 1
- Use result poller from TASK-028
- Make timeout configurable per task
- Handle both timeout and workflow failure errors
- Provide clear error messages for debugging

