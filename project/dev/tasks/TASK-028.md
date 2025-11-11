# TASK-028: Create Result Return Mechanism (Kafka Result Topic)

## Task Information
- **Task ID**: TASK-028
- **Created**: 2025-01-27
- **Status**: Waiting
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 4-6 hours
- **Actual Time**: TBD
- **Type**: Integration
- **Dependencies**: TASK-027 ✅
- **Parent PRD**: `project/docs/prd_phase3.md` - Milestone 1.6

## Task Description
Create result return mechanism for LangGraph workflows to publish results back to Kafka. Implement result topic producer and Airflow polling/callback mechanism. This addresses Mission Analyst's finding that the PRD lacks a clear pattern for returning results to Airflow tasks.

## Problem Statement
Mission Analyst identified that PRD Phase 3 shows result publishing (lines 215-231) but lacks a clear mechanism for Airflow tasks to receive results. Airflow tasks need either polling or callback mechanism to retrieve workflow results. Implement result topic pattern with correlation IDs for matching requests to responses.

## Requirements

### Functional Requirements
- [ ] Result topic created (`workflow-results`)
- [ ] LangGraph workflow publishes results to result topic
- [ ] Results include correlation ID (event_id from trigger event)
- [ ] Airflow task can poll for results
- [ ] Airflow task can use callback pattern (optional)
- [ ] Timeout mechanism for result retrieval
- [ ] Error handling for missing results

### Technical Requirements
- [ ] Result event schema defined
- [ ] Async result producer in LangGraph integration
- [ ] Result consumer/poller for Airflow tasks
- [ ] Correlation ID matching
- [ ] Timeout configuration
- [ ] Error handling and retry logic

## Implementation Plan

### Phase 1: Analysis
- [ ] Review Mission Analyst findings on result return mechanism
- [ ] Review existing event schema
- [ ] Design result event schema
- [ ] Design correlation ID pattern
- [ ] Design polling vs callback patterns

### Phase 2: Planning
- [ ] Design result event schema
- [ ] Plan result producer implementation
- [ ] Plan Airflow result poller
- [ ] Plan timeout mechanism
- [ ] Plan error handling

### Phase 3: Implementation
- [ ] Extend event schema with result event type
- [ ] Implement result producer in LangGraph integration
- [ ] Implement result poller for Airflow tasks
- [ ] Add correlation ID matching
- [ ] Add timeout mechanism
- [ ] Add error handling

### Phase 4: Testing
- [ ] Test result publishing from LangGraph
- [ ] Test result polling from Airflow
- [ ] Test correlation ID matching
- [ ] Test timeout mechanism
- [ ] Test error handling

### Phase 5: Documentation
- [ ] Document result return pattern
- [ ] Document result event schema
- [ ] Document polling mechanism
- [ ] Document timeout configuration

## Technical Implementation

### Result Event Schema Extension
```python
# project/workflow_events/schema.py (extension)
class EventType(str, Enum):
    """Enumeration of workflow event types."""
    WORKFLOW_TRIGGERED = "workflow.triggered"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_RESULT = "workflow.result"  # NEW

class WorkflowResultEvent(BaseModel):
    """Result event for workflow results."""
    correlation_id: UUID = Field(..., description="Event ID from trigger event")
    workflow_id: str = Field(..., description="Workflow identifier")
    workflow_run_id: str = Field(..., description="Workflow run identifier")
    result: Dict[str, Any] = Field(..., description="Workflow result data")
    status: str = Field(..., description="Result status: success, failure, error")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error: Optional[str] = Field(None, description="Error message if status is error")
```

### Result Producer in LangGraph Integration
```python
# project/langgraph_integration/processor.py (extension)
import asyncio
from aiokafka import AIOKafkaProducer
import json
from workflow_events import WorkflowEvent, WorkflowResultEvent

class ResultProducer:
    """Async producer for workflow results."""
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer: Optional[AIOKafkaProducer] = None
    
    async def start(self):
        """Start the producer."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()
    
    async def stop(self):
        """Stop the producer."""
        if self.producer:
            await self.producer.stop()
    
    async def publish_result(
        self,
        correlation_id: UUID,
        workflow_id: str,
        workflow_run_id: str,
        result: Dict[str, Any],
        status: str = "success",
        error: Optional[str] = None
    ):
        """Publish workflow result to result topic."""
        result_event = WorkflowResultEvent(
            correlation_id=correlation_id,
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
            result=result,
            status=status,
            error=error
        )
        
        await self.producer.send(
            "workflow-results",
            result_event.model_dump(mode="json")
        )
        await self.producer.flush()
```

### Airflow Result Poller
```python
# project/airflow_integration/result_poller.py
import time
import logging
from typing import Optional, Dict, Any
from uuid import UUID
from kafka import KafkaConsumer
import json

logger = logging.getLogger(__name__)

class WorkflowResultPoller:
    """Poller for retrieving workflow results from Kafka."""
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "workflow-results",
        timeout: int = 300,  # 5 minutes default
        poll_interval: float = 1.0  # 1 second
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.timeout = timeout
        self.poll_interval = poll_interval
    
    def poll_for_result(
        self,
        correlation_id: UUID,
        workflow_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Poll for workflow result with correlation ID."""
        consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            consumer_timeout_ms=self.timeout * 1000
        )
        
        start_time = time.time()
        
        try:
            for message in consumer:
                if time.time() - start_time > self.timeout:
                    logger.warning(f"Timeout waiting for result: {correlation_id}")
                    return None
                
                result_data = message.value
                
                # Match correlation ID
                if result_data.get("correlation_id") == str(correlation_id):
                    # Optional: match workflow_id if provided
                    if workflow_id and result_data.get("workflow_id") != workflow_id:
                        continue
                    
                    logger.info(f"Result found for correlation_id: {correlation_id}")
                    return result_data
                
                # Small delay to avoid tight loop
                time.sleep(self.poll_interval)
        
        except Exception as e:
            logger.error(f"Error polling for result: {e}", exc_info=True)
            return None
        
        finally:
            consumer.close()
        
        logger.warning(f"Result not found for correlation_id: {correlation_id}")
        return None
```

### Integration in Airflow Task
```python
# Example usage in Airflow task
from airflow_integration.result_poller import WorkflowResultPoller
from workflow_events import WorkflowEventProducer, EventType

@task
def trigger_and_wait_for_result(data: dict, **context):
    """Trigger workflow and wait for result."""
    # Publish trigger event
    producer = WorkflowEventProducer()
    event = producer.publish_workflow_event(
        event_type=EventType.WORKFLOW_TRIGGERED,
        workflow_id=context['dag'].dag_id,
        workflow_run_id=context['dag_run'].run_id,
        payload={"data": data}
    )
    
    correlation_id = event.event_id
    
    # Poll for result
    poller = WorkflowResultPoller(timeout=300)
    result = poller.poll_for_result(correlation_id)
    
    if result is None:
        raise Exception("Workflow result not received within timeout")
    
    if result.get("status") != "success":
        raise Exception(f"Workflow failed: {result.get('error')}")
    
    return result.get("result")
```

## Testing

### Manual Testing
- [ ] Publish result from LangGraph integration
- [ ] Verify result appears in `workflow-results` topic
- [ ] Test polling from Airflow task
- [ ] Test correlation ID matching
- [ ] Test timeout mechanism
- [ ] Test error handling

### Automated Testing
- [ ] Unit tests for result producer
- [ ] Unit tests for result poller
- [ ] Integration tests with Kafka
- [ ] Test correlation ID matching
- [ ] Test timeout behavior
- [ ] Test error scenarios

## Acceptance Criteria
- [ ] Result topic created and configured
- [ ] LangGraph workflow publishes results
- [ ] Results include correlation ID
- [ ] Airflow task can poll for results
- [ ] Correlation ID matching works
- [ ] Timeout mechanism works
- [ ] Error handling implemented
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Documentation complete

## Dependencies
- **External**: kafka-python, aiokafka
- **Internal**: TASK-027 (Kafka consumer), existing event schema, Airflow integration

## Risks and Mitigation

### Risk 1: Result Not Received
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: Implement timeout, add retry logic, log correlation IDs, add monitoring

### Risk 2: Correlation ID Mismatch
- **Probability**: Low
- **Impact**: High
- **Mitigation**: Use UUID for correlation, validate matching, add logging

### Risk 3: Polling Performance
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Use appropriate poll interval, consider callback pattern for high-volume scenarios

## Task Status
- [ ] Analysis Complete
- [ ] Planning Complete
- [ ] Implementation Complete
- [ ] Testing Complete
- [ ] Documentation Complete

## Notes
- **CRITICAL**: Mission Analyst identified missing result return mechanism
- Use correlation ID (event_id) to match requests to responses
- Implement timeout to prevent indefinite waiting
- Consider callback pattern for future enhancement (lower priority)
- Result topic: `workflow-results`
- Polling is simpler to implement than callback pattern initially

