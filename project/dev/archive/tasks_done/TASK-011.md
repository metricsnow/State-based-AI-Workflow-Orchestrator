# TASK-011: Kafka Producer Implementation

## Task Information
- **Task ID**: TASK-011
- **Created**: 2025-01-27
- **Status**: Done
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 3-4 hours
- **Actual Time**: TBD
- **Type**: Feature
- **Dependencies**: TASK-009 ✅, TASK-010 ✅
- **Parent PRD**: `project/docs/prd_phase1.md` - Milestone 1.3

## Task Description
Implement Kafka producer for publishing workflow events to Kafka topics. Create producer wrapper class, implement event publishing, error handling, and connection management. Ensure producer follows best practices for reliability and performance.

## Problem Statement
A Kafka producer is needed to publish workflow events from Airflow tasks to Kafka topics. The producer must be reliable, handle errors gracefully, and follow Kafka best practices.

## Requirements

### Functional Requirements
- [ ] Kafka producer class implemented
- [ ] Event publishing functionality
- [ ] Connection management
- [ ] Error handling and retries
- [ ] Event serialization (JSON)
- [ ] Producer configuration
- [ ] Connection pooling/reuse

### Technical Requirements
- [ ] kafka-python library
- [ ] JSON serialization
- [ ] Proper error handling
- [ ] Connection retry logic
- [ ] Producer configuration (acks, retries)
- [ ] Logging for debugging

## Implementation Plan

### Phase 1: Analysis
- [ ] Review Kafka producer best practices
- [ ] Review kafka-python documentation
- [ ] Design producer interface
- [ ] Plan error handling strategy

### Phase 2: Planning
- [ ] Design producer class structure
- [ ] Plan configuration approach
- [ ] Design error handling
- [ ] Plan connection management

### Phase 3: Implementation
- [ ] Create producer module
- [ ] Implement producer class
- [ ] Implement event publishing
- [ ] Add error handling
- [ ] Add connection management
- [ ] Add logging
- [ ] Create configuration

### Phase 4: Testing
- [ ] Test producer initialization
- [ ] Test event publishing
- [ ] Test error handling
- [ ] Test connection retry
- [ ] Integration test with Kafka

### Phase 5: Documentation
- [ ] Document producer usage
- [ ] Document configuration
- [ ] Document error handling

## Technical Implementation

### Producer Implementation
```python
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging
from typing import Optional
from .event_schema import WorkflowEvent

logger = logging.getLogger(__name__)

class WorkflowEventProducer:
    """Kafka producer for workflow events."""
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        """Initialize Kafka producer."""
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self._connect()
    
    def _connect(self):
        """Create Kafka producer connection."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[self.bootstrap_servers],
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                acks='all',  # Wait for all replicas
                retries=3,
                max_in_flight_requests_per_connection=1,
            )
            logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def publish_event(self, event: WorkflowEvent, topic: str = 'workflow-events') -> bool:
        """Publish workflow event to Kafka topic."""
        try:
            # Serialize event to dict
            event_dict = event.dict()
            
            # Publish to Kafka
            future = self.producer.send(topic, value=event_dict)
            
            # Wait for confirmation
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"Event published: topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}"
            )
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error publishing event: {e}")
            return False
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False
    
    def flush(self):
        """Flush all pending messages."""
        if self.producer:
            self.producer.flush()
    
    def close(self):
        """Close producer connection."""
        if self.producer:
            self.flush()
            self.producer.close()
            logger.info("Kafka producer closed")
```

### Usage Example
```python
from workflow_events import WorkflowEventProducer, WorkflowEvent, EventType, EventSource

producer = WorkflowEventProducer(bootstrap_servers='localhost:9092')

event = WorkflowEvent(
    event_type=EventType.WORKFLOW_COMPLETED,
    source=EventSource.AIRFLOW,
    workflow_id="example_dag",
    workflow_run_id="run_123",
    payload={"data": {"status": "success"}},
    metadata={"environment": "dev", "version": "1.0"}
)

producer.publish_event(event)
producer.close()
```

## Testing

### Manual Testing
- [ ] Test producer initialization
- [ ] Test event publishing
- [ ] Verify events in Kafka
- [ ] Test error handling
- [ ] Test connection retry

### Automated Testing
- [ ] Unit tests for producer
- [ ] Mock Kafka tests
- [ ] Integration tests with real Kafka

## Acceptance Criteria
- [ ] Producer class implemented
- [ ] Events can be published to Kafka
- [ ] Error handling working
- [ ] Connection management working
- [ ] Events serialized correctly
- [ ] Producer configuration correct
- [ ] Tests passing
- [ ] Documentation complete

## Dependencies
- **External**: kafka-python, pydantic
- **Internal**: TASK-009 (Kafka setup), TASK-010 (Event schema)

## Risks and Mitigation

### Risk 1: Connection Failures
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: Implement retry logic, handle connection errors gracefully

### Risk 2: Message Loss
- **Probability**: Low
- **Impact**: High
- **Mitigation**: Use acks='all', implement proper error handling

### Risk 3: Serialization Errors
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Validate events before publishing, handle serialization errors

## Task Status
- [x] Analysis Complete
  - [x] Reviewed Kafka producer best practices via MCP Context7
  - [x] Reviewed kafka-python documentation (v2.2.15)
  - [x] Designed producer interface with error handling
  - [x] Planned error handling strategy (retries, timeouts, graceful degradation)
- [x] Planning Complete
  - [x] Designed producer class structure (WorkflowEventProducer)
  - [x] Planned configuration approach (constructor parameters with defaults)
  - [x] Designed error handling (KafkaError, KafkaTimeoutError handling)
  - [x] Planned connection management (context manager, flush, close)
- [x] Implementation Complete
  - [x] Created producer module (project/workflow_events/producer.py)
  - [x] Implemented producer class with all required features
  - [x] Implemented event publishing with Pydantic model_dump()
  - [x] Added comprehensive error handling
  - [x] Added connection management (flush, close, context manager)
  - [x] Added logging for debugging
  - [x] Created configuration with best practices (acks='all', retries=3)
- [x] Testing Complete
  - [x] Created comprehensive unit tests (17 tests)
  - [x] All unit tests passing
  - [x] Tested producer initialization
  - [x] Tested event publishing (success and error cases)
  - [x] Tested error handling (timeouts, Kafka errors)
  - [x] Tested connection management (flush, close, context manager)
  - [x] Created integration test placeholder (requires running Kafka)
- [x] Documentation Complete
  - [x] Documented producer usage in code (docstrings)
  - [x] Documented configuration options
  - [x] Documented error handling patterns
  - [x] Updated tests/kafka/README.md with producer test status
- [x] Quality Validation Complete
  - [x] All 17 unit tests passing
  - [x] No linting errors
  - [x] Code follows best practices from MCP Context7
  - [x] Error handling comprehensive and tested
  - [x] Connection management robust
  - [x] Producer exported in workflow_events.__init__

## Notes
- Use acks='all' for reliability
- Implement proper error handling
- Flush producer before closing
- Use connection pooling for performance
- Reference: `/dpkp/kafka-python` MCP Context7 documentation
