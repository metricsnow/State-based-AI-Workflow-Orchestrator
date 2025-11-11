# TASK-027: Create Async LangGraph Kafka Consumer Service

## Task Information
- **Task ID**: TASK-027
- **Created**: 2025-01-27
- **Status**: Waiting
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 6-8 hours
- **Actual Time**: TBD
- **Type**: Integration
- **Dependencies**: TASK-025 ✅, TASK-026 ✅
- **Parent PRD**: `project/docs/prd_phase3.md` - Milestone 1.6

## Task Description
Create an async Kafka consumer service that consumes workflow events from Kafka and triggers LangGraph workflows. This addresses Mission Analyst's finding that the PRD shows a synchronous blocking consumer pattern which is unsuitable for production. Implement async pattern using `aiokafka` for non-blocking event consumption.

## Problem Statement
The PRD Phase 3 shows a synchronous Kafka consumer pattern (lines 176-204) that blocks execution. Mission Analyst identified this as a high-priority issue. Production systems require async, non-blocking consumers that can handle multiple events concurrently and integrate with LangGraph's async capabilities.

## Requirements

### Functional Requirements
- [ ] Async Kafka consumer service implemented
- [ ] Consumes events from `workflow-events` topic
- [ ] Triggers LangGraph workflows on event consumption
- [ ] Non-blocking event processing
- [ ] Error handling for consumer failures
- [ ] Graceful shutdown handling
- [ ] Logging for monitoring and debugging

### Technical Requirements
- [ ] Use `aiokafka` for async Kafka operations
- [ ] Async/await pattern throughout
- [ ] Integration with existing LangGraph workflows
- [ ] Event schema validation using existing `WorkflowEvent` model
- [ ] Proper error handling and retry logic
- [ ] Configuration via environment variables
- [ ] Service can run as background process

## Implementation Plan

### Phase 1: Analysis
- [ ] Review Mission Analyst findings on async patterns
- [ ] Review existing LangGraph workflow interfaces
- [ ] Review existing event schema (`WorkflowEvent`)
- [ ] Review aiokafka documentation and patterns
- [ ] Design async consumer architecture

### Phase 2: Planning
- [ ] Design async consumer service structure
- [ ] Plan event processing workflow
- [ ] Plan error handling strategy
- [ ] Plan integration with LangGraph workflows
- [ ] Plan configuration management

### Phase 3: Implementation
- [ ] Create `langgraph_integration` module structure
- [ ] Implement async Kafka consumer class
- [ ] Implement event processing logic
- [ ] Integrate with LangGraph workflow execution
- [ ] Add error handling and retry logic
- [ ] Add logging and monitoring
- [ ] Add configuration management
- [ ] Create service entry point

### Phase 4: Testing
- [ ] Unit tests for consumer class
- [ ] Integration tests with Kafka
- [ ] Test event processing
- [ ] Test error handling
- [ ] Test graceful shutdown
- [ ] Test concurrent event processing

### Phase 5: Documentation
- [ ] Document consumer service architecture
- [ ] Document configuration options
- [ ] Document usage patterns
- [ ] Document error handling

## Technical Implementation

### Module Structure
```
project/langgraph_integration/
├── __init__.py
├── consumer.py          # Async Kafka consumer
├── processor.py         # Event processing logic
├── config.py            # Configuration management
└── service.py           # Service entry point
```

### Async Consumer Implementation
```python
# project/langgraph_integration/consumer.py
import asyncio
import logging
from typing import Optional
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
import json

from workflow_events import WorkflowEvent, EventType
from langgraph_workflows import multi_agent_graph

logger = logging.getLogger(__name__)


class LangGraphKafkaConsumer:
    """Async Kafka consumer for LangGraph workflow events."""
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "workflow-events",
        group_id: str = "langgraph-consumer-group"
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.running = False
    
    async def start(self):
        """Start the consumer service."""
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True
        )
        await self.consumer.start()
        self.running = True
        logger.info(f"Kafka consumer started for topic: {self.topic}")
    
    async def stop(self):
        """Stop the consumer service gracefully."""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
        logger.info("Kafka consumer stopped")
    
    async def consume_and_process(self):
        """Main consumption loop - processes events asynchronously."""
        if not self.consumer:
            raise RuntimeError("Consumer not started")
        
        try:
            async for message in self.consumer:
                if not self.running:
                    break
                
                try:
                    event_data = message.value
                    event = WorkflowEvent(**event_data)
                    
                    if event.event_type == EventType.WORKFLOW_TRIGGERED:
                        # Process event asynchronously
                        asyncio.create_task(self.process_workflow_event(event))
                    else:
                        logger.debug(f"Ignoring event type: {event.event_type}")
                
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    # Continue processing other messages
        
        except KafkaError as e:
            logger.error(f"Kafka error: {e}", exc_info=True)
            raise
    
    async def process_workflow_event(self, event: WorkflowEvent):
        """Process a workflow event by triggering LangGraph workflow."""
        try:
            logger.info(f"Processing workflow event: {event.event_id}")
            
            # Convert event to LangGraph state
            initial_state = self._event_to_state(event)
            
            # Execute LangGraph workflow
            config = {"configurable": {"thread_id": str(event.event_id)}}
            result = await asyncio.to_thread(
                multi_agent_graph.invoke,
                initial_state,
                config=config
            )
            
            logger.info(f"Workflow completed: {event.event_id}")
            
            # TODO: Publish result (TASK-028)
            return result
        
        except Exception as e:
            logger.error(f"Error processing workflow event {event.event_id}: {e}", exc_info=True)
            raise
    
    def _event_to_state(self, event: WorkflowEvent):
        """Convert WorkflowEvent to LangGraph state."""
        from langgraph_workflows.state import MultiAgentState
        
        return MultiAgentState(
            messages=[],
            task=event.payload.data.get("task", "process_workflow"),
            agent_results={},
            current_agent="orchestrator",
            completed=False,
            metadata={"event_id": str(event.event_id), "workflow_id": event.workflow_id}
        )
```

### Service Entry Point
```python
# project/langgraph_integration/service.py
import asyncio
import logging
import signal
import os
from langgraph_integration.consumer import LangGraphKafkaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

consumer: LangGraphKafkaConsumer = None

def signal_handler(sig, frame):
    """Handle shutdown signals."""
    logger.info("Shutdown signal received")
    if consumer:
        asyncio.create_task(consumer.stop())

async def main():
    """Main service entry point."""
    global consumer
    
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.getenv("KAFKA_WORKFLOW_EVENTS_TOPIC", "workflow-events")
    group_id = os.getenv("KAFKA_CONSUMER_GROUP_ID", "langgraph-consumer-group")
    
    consumer = LangGraphKafkaConsumer(
        bootstrap_servers=bootstrap_servers,
        topic=topic,
        group_id=group_id
    )
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await consumer.start()
        await consumer.consume_and_process()
    except Exception as e:
        logger.error(f"Service error: {e}", exc_info=True)
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing

### Manual Testing
- [ ] Start Kafka and Zookeeper
- [ ] Start consumer service: `python -m langgraph_integration.service`
- [ ] Publish test event to Kafka
- [ ] Verify event consumed and processed
- [ ] Verify LangGraph workflow triggered
- [ ] Test graceful shutdown (SIGTERM)
- [ ] Test error handling (invalid events)

### Automated Testing
- [ ] Unit tests for consumer class
- [ ] Unit tests for event processing
- [ ] Integration tests with test Kafka
- [ ] Test async event processing
- [ ] Test error handling
- [ ] Test graceful shutdown

## Acceptance Criteria
- [ ] Async Kafka consumer service implemented
- [ ] Consumes events from `workflow-events` topic
- [ ] Triggers LangGraph workflows on event consumption
- [ ] Non-blocking event processing
- [ ] Error handling implemented
- [ ] Graceful shutdown working
- [ ] Logging and monitoring in place
- [ ] Configuration via environment variables
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Documentation complete

## Dependencies
- **External**: aiokafka
- **Internal**: TASK-025 (Ollama service), TASK-026 (langchain-ollama), existing LangGraph workflows, existing event schema

## Risks and Mitigation

### Risk 1: Async Complexity
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Use proven async patterns, test thoroughly, handle exceptions properly

### Risk 2: Kafka Connection Failures
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: Implement retry logic, handle connection errors gracefully, add health checks

### Risk 3: Event Processing Failures
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Implement error handling, log errors, continue processing other events, consider dead letter queue

## Task Status
- [ ] Analysis Complete
- [ ] Planning Complete
- [ ] Implementation Complete
- [ ] Testing Complete
- [ ] Documentation Complete

## Notes
- **CRITICAL**: Use async pattern (not synchronous as shown in PRD)
- Mission Analyst identified synchronous pattern as high-priority issue
- Use `aiokafka` for async Kafka operations
- Integrate with existing LangGraph workflows
- Handle errors gracefully - don't stop consumer on single event failure
- Consider implementing dead letter queue for failed events (future enhancement)

