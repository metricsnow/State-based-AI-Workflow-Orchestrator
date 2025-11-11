# TASK-029: Integrate LangGraph Workflow with Kafka Consumer

## Task Information
- **Task ID**: TASK-029
- **Created**: 2025-01-27
- **Status**: Done
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 4-6 hours
- **Actual Time**: TBD
- **Type**: Integration
- **Dependencies**: TASK-027 ✅, TASK-028 ✅
- **Parent PRD**: `project/docs/prd_phase3.md` - Milestone 1.6

## Task Description
Integrate existing LangGraph workflows (from Phase 2) with the Kafka consumer service. Connect event consumption to workflow execution and result publishing. Ensure proper state conversion and error handling.

## Problem Statement
The Kafka consumer service (TASK-027) needs to execute existing LangGraph workflows when events are consumed. This task connects the consumer to the workflows and ensures proper integration with state management, checkpointing, and result publishing.

## Requirements

### Functional Requirements
- [ ] Kafka consumer triggers LangGraph workflows
- [ ] Event data converted to LangGraph state
- [ ] Workflow execution integrated
- [ ] Results published to result topic
- [ ] Error handling for workflow failures
- [ ] Checkpointing preserved
- [ ] State management working

### Technical Requirements
- [ ] Integration with existing `multi_agent_graph`
- [ ] State conversion from event to `MultiAgentState`
- [ ] Thread ID management (use event_id)
- [ ] Result extraction from workflow state
- [ ] Error handling and logging
- [ ] Configuration management

## Implementation Plan

### Phase 1: Analysis
- [ ] Review existing LangGraph workflows
- [ ] Review MultiAgentState structure
- [ ] Review event schema structure
- [ ] Design state conversion logic
- [ ] Design workflow execution pattern

### Phase 2: Planning
- [ ] Plan state conversion implementation
- [ ] Plan workflow execution integration
- [ ] Plan result extraction
- [ ] Plan error handling

### Phase 3: Implementation
- [ ] Implement state conversion function
- [ ] Integrate workflow execution in consumer
- [ ] Implement result extraction
- [ ] Add error handling
- [ ] Add logging and monitoring
- [ ] Test with existing workflows

### Phase 4: Testing
- [ ] Test state conversion
- [ ] Test workflow execution
- [ ] Test result extraction
- [ ] Test error handling
- [ ] Test with different event types
- [ ] Integration tests

### Phase 5: Documentation
- [ ] Document integration pattern
- [ ] Document state conversion
- [ ] Document workflow execution
- [ ] Document error handling

## Technical Implementation

### State Conversion
```python
# project/langgraph_integration/processor.py
from workflow_events import WorkflowEvent
from langgraph_workflows.state import MultiAgentState

def event_to_multi_agent_state(event: WorkflowEvent) -> MultiAgentState:
    """Convert WorkflowEvent to MultiAgentState."""
    payload_data = event.payload.data
    
    return MultiAgentState(
        messages=[],
        task=payload_data.get("task", "process_workflow"),
        agent_results={},
        current_agent="orchestrator",
        completed=False,
        metadata={
            "event_id": str(event.event_id),
            "workflow_id": event.workflow_id,
            "workflow_run_id": event.workflow_run_id,
            "source": event.source.value,
            "timestamp": event.timestamp.isoformat()
        }
    )
```

### Workflow Execution Integration
```python
# project/langgraph_integration/processor.py (extension)
import asyncio
from langgraph_workflows import multi_agent_graph
from langgraph_integration.result_producer import ResultProducer

class WorkflowProcessor:
    """Processes workflow events by executing LangGraph workflows."""
    
    def __init__(self, result_producer: ResultProducer):
        self.result_producer = result_producer
    
    async def process_workflow_event(self, event: WorkflowEvent):
        """Process workflow event by executing LangGraph workflow."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Processing workflow event: {event.event_id}")
            
            # Convert event to LangGraph state
            initial_state = event_to_multi_agent_state(event)
            
            # Create thread ID from event ID
            thread_id = str(event.event_id)
            config = {"configurable": {"thread_id": thread_id}}
            
            # Execute workflow (run in thread pool to avoid blocking)
            result = await asyncio.to_thread(
                multi_agent_graph.invoke,
                initial_state,
                config=config
            )
            
            # Extract result data
            result_data = self._extract_result(result)
            
            # Publish result
            await self.result_producer.publish_result(
                correlation_id=event.event_id,
                workflow_id=event.workflow_id,
                workflow_run_id=event.workflow_run_id,
                result=result_data,
                status="success"
            )
            
            logger.info(f"Workflow completed successfully: {event.event_id}")
            return result
        
        except Exception as e:
            logger.error(
                f"Error processing workflow event {event.event_id}: {e}",
                exc_info=True
            )
            
            # Publish error result
            await self.result_producer.publish_result(
                correlation_id=event.event_id,
                workflow_id=event.workflow_id,
                workflow_run_id=event.workflow_run_id,
                result={},
                status="error",
                error=str(e)
            )
            
            raise
    
    def _extract_result(self, workflow_result: dict) -> dict:
        """Extract result data from workflow state."""
        return {
            "completed": workflow_result.get("completed", False),
            "agent_results": workflow_result.get("agent_results", {}),
            "task": workflow_result.get("task", ""),
            "metadata": workflow_result.get("metadata", {})
        }
```

### Consumer Integration
```python
# project/langgraph_integration/consumer.py (update)
from langgraph_integration.processor import WorkflowProcessor, ResultProducer

class LangGraphKafkaConsumer:
    """Async Kafka consumer for LangGraph workflow events."""
    
    def __init__(self, ...):
        # ... existing code ...
        self.result_producer = ResultProducer(bootstrap_servers)
        self.workflow_processor = WorkflowProcessor(self.result_producer)
    
    async def start(self):
        """Start the consumer service."""
        # ... existing code ...
        await self.result_producer.start()
    
    async def stop(self):
        """Stop the consumer service gracefully."""
        # ... existing code ...
        await self.result_producer.stop()
    
    async def process_workflow_event(self, event: WorkflowEvent):
        """Process a workflow event by triggering LangGraph workflow."""
        await self.workflow_processor.process_workflow_event(event)
```

## Testing

### Manual Testing
- [ ] Start consumer service
- [ ] Publish workflow event
- [ ] Verify workflow executes
- [ ] Verify result published
- [ ] Test with different event payloads
- [ ] Test error handling

### Automated Testing
- [ ] Unit tests for state conversion
- [ ] Unit tests for workflow execution
- [ ] Unit tests for result extraction
- [ ] Integration tests with workflows
- [ ] Test error handling
- [ ] Test with different state types

## Acceptance Criteria
- [x] Kafka consumer triggers LangGraph workflows
- [x] Event data converted to LangGraph state correctly
- [x] Workflow execution integrated
- [x] Results published to result topic
- [x] Error handling for workflow failures
- [x] Checkpointing preserved
- [x] State management working
- [x] Unit tests passing
- [x] Integration tests passing
- [x] Documentation complete

## Dependencies
- **External**: None
- **Internal**: TASK-027 (Kafka consumer), TASK-028 (Result producer), existing LangGraph workflows (Phase 2)

## Risks and Mitigation

### Risk 1: State Conversion Errors
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: Validate state conversion, handle missing fields, add logging

### Risk 2: Workflow Execution Failures
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: Implement error handling, publish error results, log errors

### Risk 3: Result Extraction Issues
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Validate result structure, handle missing fields, add default values

## Task Status
- [x] Analysis Complete
- [x] Planning Complete
- [x] Implementation Complete
- [x] Testing Complete
- [x] Documentation Complete

## Notes
- Use existing `multi_agent_graph` from Phase 2
- Preserve checkpointing functionality
- Use event_id as thread_id for checkpointing
- Handle state conversion errors gracefully
- Extract all relevant result data for Airflow consumption

