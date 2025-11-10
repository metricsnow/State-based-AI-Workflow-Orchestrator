# TASK-012: Kafka Consumer Implementation

## Task Information
- **Task ID**: TASK-012
- **Created**: 2025-01-27
- **Status**: Waiting
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 3-4 hours
- **Actual Time**: TBD
- **Type**: Feature
- **Dependencies**: TASK-009 ✅, TASK-010 ✅, TASK-011 ✅
- **Parent PRD**: `project/docs/prd_phase1.md` - Milestone 1.3

## Task Description
Implement Kafka consumer for processing workflow events from Kafka topics. Create consumer wrapper class, implement event consumption, error handling, and event deserialization. Consumer will be used in Phase 3 for event processing.

## Problem Statement
A Kafka consumer is needed to consume workflow events from Kafka topics. The consumer must handle event deserialization, error handling, and follow Kafka best practices for reliability.

## Requirements

### Functional Requirements
- [ ] Kafka consumer class implemented
- [ ] Event consumption functionality
- [ ] Event deserialization (JSON)
- [ ] Error handling and retries
- [ ] Consumer group support
- [ ] Offset management
- [ ] Event processing callbacks

### Technical Requirements
- [ ] kafka-python library
- [ ] JSON deserialization
- [ ] Proper error handling
- [ ] Consumer group configuration
- [ ] Offset commit strategy
- [ ] Logging for debugging

## Implementation Plan

### Phase 1: Analysis
- [ ] Review Kafka consumer best practices
- [ ] Review kafka-python documentation
- [ ] Design consumer interface
- [ ] Plan error handling strategy

### Phase 2: Planning
- [ ] Design consumer class structure
- [ ] Plan configuration approach
- [ ] Design error handling
- [ ] Plan offset management

### Phase 3: Implementation
- [ ] Create consumer module
- [ ] Implement consumer class
- [ ] Implement event consumption
- [ ] Add error handling
- [ ] Add offset management
- [ ] Add logging
- [ ] Create configuration

### Phase 4: Testing
- [ ] Test consumer initialization
- [ ] Test event consumption
- [ ] Test event deserialization
- [ ] Test error handling
- [ ] Integration test with Kafka

### Phase 5: Documentation
- [ ] Document consumer usage
- [ ] Document configuration
- [ ] Document error handling

## Technical Implementation

### Consumer Implementation
```python
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import logging
from typing import Callable, Optional
from .event_schema import WorkflowEvent

logger = logging.getLogger(__name__)

class WorkflowEventConsumer:
    """Kafka consumer for workflow events."""
    
    def __init__(
        self,
        bootstrap_servers: str = 'localhost:9092',
        group_id: Optional[str] = None,
        auto_offset_reset: str = 'earliest',
        enable_auto_commit: bool = True
    ):
        """Initialize Kafka consumer."""
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset
        self.enable_auto_commit = enable_auto_commit
        self.consumer = None
        self._connect()
    
    def _connect(self):
        """Create Kafka consumer connection."""
        try:
            config = {
                'bootstrap_servers': [self.bootstrap_servers],
                'value_deserializer': lambda m: json.loads(m.decode('utf-8')),
                'auto_offset_reset': self.auto_offset_reset,
                'enable_auto_commit': self.enable_auto_commit,
            }
            
            if self.group_id:
                config['group_id'] = self.group_id
            
            self.consumer = KafkaConsumer(**config)
            logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def subscribe(self, topics: list):
        """Subscribe to Kafka topics."""
        if self.consumer:
            self.consumer.subscribe(topics)
            logger.info(f"Subscribed to topics: {topics}")
    
    def consume_events(self, callback: Callable[[WorkflowEvent], None], topics: list):
        """Consume events and call callback for each event."""
        self.subscribe(topics)
        
        try:
            for message in self.consumer:
                try:
                    # Deserialize event
                    event_dict = message.value
                    event = WorkflowEvent(**event_dict)
                    
                    # Process event
                    callback(event)
                    
                    logger.debug(f"Processed event: {event.event_id}")
                    
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
                    # Continue processing other events
                    continue
                    
        except KeyboardInterrupt:
            logger.info("Consumer interrupted")
        except Exception as e:
            logger.error(f"Consumer error: {e}")
            raise
        finally:
            self.close()
    
    def close(self):
        """Close consumer connection."""
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")
```

### Usage Example
```python
from workflow_events import WorkflowEventConsumer, WorkflowEvent

def process_event(event: WorkflowEvent):
    """Process workflow event."""
    print(f"Received event: {event.event_type} from {event.source}")
    print(f"Workflow: {event.workflow_id}, Run: {event.workflow_run_id}")

consumer = WorkflowEventConsumer(
    bootstrap_servers='localhost:9092',
    group_id='workflow-processor'
)

consumer.consume_events(
    callback=process_event,
    topics=['workflow-events']
)
```

## Testing

### Manual Testing
- [ ] Test consumer initialization
- [ ] Test event consumption
- [ ] Test event deserialization
- [ ] Verify events processed correctly
- [ ] Test error handling
- [ ] Test consumer group behavior

### Automated Testing
- [ ] Unit tests for consumer
- [ ] Mock Kafka tests
- [ ] Integration tests with real Kafka

## Acceptance Criteria
- [ ] Consumer class implemented
- [ ] Events can be consumed from Kafka
- [ ] Event deserialization working
- [ ] Error handling working
- [ ] Consumer group support working
- [ ] Offset management working
- [ ] Tests passing
- [ ] Documentation complete

## Dependencies
- **External**: kafka-python, pydantic
- **Internal**: TASK-009 (Kafka setup), TASK-010 (Event schema), TASK-011 (Producer)

## Risks and Mitigation

### Risk 1: Consumer Lag
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Monitor consumer lag, optimize processing, scale consumers

### Risk 2: Deserialization Errors
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Validate event schema, handle deserialization errors gracefully

### Risk 3: Offset Management
- **Probability**: Low
- **Impact**: High
- **Mitigation**: Use proper offset commit strategy, handle commit failures

## Task Status
- [ ] Analysis Complete
- [ ] Planning Complete
- [ ] Implementation Complete
- [ ] Testing Complete
- [ ] Documentation Complete
- [ ] Quality Validation Complete

## Notes
- Use consumer groups for parallel processing
- Handle deserialization errors gracefully
- Implement proper offset management
- Monitor consumer lag
- Reference: `/dpkp/kafka-python` MCP Context7 documentation

