# TASK-032: End-to-End Integration Testing for Airflow-LangGraph Integration

## Task Information
- **Task ID**: TASK-032
- **Created**: 2025-01-27
- **Status**: Waiting
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 6-8 hours
- **Actual Time**: TBD
- **Type**: Testing
- **Dependencies**: TASK-027 ✅, TASK-028 ✅, TASK-029 ✅, TASK-030 ✅, TASK-031 ✅
- **Parent PRD**: `project/docs/prd_phase3.md` - Milestone 1.6

## Task Description
Create comprehensive end-to-end integration tests for the complete Airflow-LangGraph integration flow. Test the full pipeline: Airflow task → Kafka event → LangGraph consumer → Workflow execution → Result publishing → Airflow result retrieval.

## Problem Statement
End-to-end testing is required to validate that all components of the Airflow-LangGraph integration work together correctly. This ensures the integration meets all acceptance criteria for Milestone 1.6 and is ready for production use.

## Requirements

### Functional Requirements
- [ ] End-to-end test: Airflow → Kafka → LangGraph → Result
- [ ] Test event-driven coordination
- [ ] Test error recovery
- [ ] Test timeout handling
- [ ] Test retry mechanisms
- [ ] Test dead letter queue
- [ ] Test with different event types
- [ ] Test with different workflow types

### Technical Requirements
- [ ] Integration test suite
- [ ] Test fixtures for Kafka
- [ ] Test fixtures for Airflow
- [ ] Test fixtures for LangGraph
- [ ] Mock/stub external dependencies
- [ ] Test coverage >80%
- [ ] Test documentation

## Implementation Plan

### Phase 1: Analysis
- [ ] Review Milestone 1.6 acceptance criteria
- [ ] Identify end-to-end test scenarios
- [ ] Plan test structure
- [ ] Design test fixtures
- [ ] Plan test data

### Phase 2: Planning
- [ ] Design integration test suite structure
- [ ] Plan test scenarios
- [ ] Design test fixtures
- [ ] Plan test execution strategy
- [ ] Plan test data management

### Phase 3: Implementation
- [ ] Create integration test module
- [ ] Implement test fixtures
- [ ] Implement end-to-end test scenarios
- [ ] Implement error scenario tests
- [ ] Implement timeout tests
- [ ] Implement retry tests

### Phase 4: Testing
- [ ] Run all integration tests
- [ ] Verify test coverage
- [ ] Validate acceptance criteria
- [ ] Fix any test failures
- [ ] Performance testing

### Phase 5: Documentation
- [ ] Document test scenarios
- [ ] Document test execution
- [ ] Document acceptance criteria validation

## Technical Implementation

### Test Structure
```python
# project/tests/integration/test_airflow_langgraph_integration.py
import pytest
import asyncio
import uuid
from datetime import datetime
from unittest.mock import patch, MagicMock

from workflow_events import WorkflowEventProducer, EventType, EventSource
from langgraph_integration.consumer import LangGraphKafkaConsumer
from langgraph_integration.processor import WorkflowProcessor
from airflow_integration.langgraph_trigger import trigger_langgraph_workflow


class TestAirflowLangGraphIntegration:
    """End-to-end integration tests for Airflow-LangGraph integration."""
    
    @pytest.fixture
    def kafka_consumer(self):
        """Fixture for Kafka consumer."""
        consumer = LangGraphKafkaConsumer(
            bootstrap_servers="localhost:9092",
            topic="workflow-events-test"
        )
        yield consumer
        asyncio.run(consumer.stop())
    
    @pytest.fixture
    def event_producer(self):
        """Fixture for event producer."""
        return WorkflowEventProducer(bootstrap_servers="localhost:9092")
    
    def test_end_to_end_workflow_execution(self, kafka_consumer, event_producer):
        """Test complete workflow: Airflow → Kafka → LangGraph → Result."""
        # Start consumer
        asyncio.run(kafka_consumer.start())
        
        # Create test event
        event = event_producer.publish_workflow_event(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test_workflow",
            workflow_run_id="test_run_123",
            payload={
                "data": {
                    "task": "test_task",
                    "data": {"test": "data"}
                }
            }
        )
        
        correlation_id = event.event_id
        
        # Wait for processing (with timeout)
        import time
        max_wait = 60
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            # Check result topic
            result = self._poll_for_result(correlation_id)
            if result:
                assert result["status"] == "success"
                assert "result" in result
                return
        
        pytest.fail("Result not received within timeout")
    
    def test_error_handling_and_recovery(self, kafka_consumer, event_producer):
        """Test error handling and recovery mechanisms."""
        # Test with invalid event data
        # Test retry mechanism
        # Test dead letter queue
        pass
    
    def test_timeout_handling(self):
        """Test timeout handling in result polling."""
        # Test timeout when result not received
        # Test timeout configuration
        pass
    
    def test_retry_mechanisms(self):
        """Test retry mechanisms for transient errors."""
        # Test retry with transient errors
        # Test retry limits
        # Test backoff strategies
        pass
    
    def test_dead_letter_queue(self):
        """Test dead letter queue for failed events."""
        # Test DLQ publishing
        # Test DLQ event structure
        pass
    
    def _poll_for_result(self, correlation_id):
        """Helper to poll for result."""
        from airflow_integration.result_poller import WorkflowResultPoller
        poller = WorkflowResultPoller(
            bootstrap_servers="localhost:9092",
            topic="workflow-results-test",
            timeout=10
        )
        return poller.poll_for_result(correlation_id)
```

### Acceptance Criteria Validation
```python
def test_milestone_1_6_acceptance_criteria():
    """Validate all Milestone 1.6 acceptance criteria."""
    # AC1: Airflow task publishes event to Kafka successfully
    # (validated in event publishing tests)
    
    # AC2: LangGraph workflow consumes event from Kafka
    # (validated in consumer tests)
    
    # AC3: Workflow executes with event data
    # (validated in workflow execution tests)
    
    # AC4: Results returned to Airflow (via callback or polling)
    # (validated in result polling tests)
    
    # AC5: Error handling implemented for Kafka operations
    # (validated in error handling tests)
    
    # AC6: Event schema validated
    # (validated in event schema tests)
    
    # AC7: End-to-end workflow tested
    # (validated in end-to-end tests)
    pass
```

## Testing

### Test Execution
- [ ] Run all integration tests
- [ ] Verify test coverage >80%
- [ ] Validate all tests pass
- [ ] Check for test failures
- [ ] Performance testing

### Test Coverage
- [ ] End-to-end workflow coverage
- [ ] Error handling coverage
- [ ] Timeout handling coverage
- [ ] Retry mechanism coverage
- [ ] Dead letter queue coverage
- [ ] Event schema validation coverage

## Acceptance Criteria
- [ ] End-to-end test: Airflow → Kafka → LangGraph → Result
- [ ] Test event-driven coordination
- [ ] Test error recovery
- [ ] Test timeout handling
- [ ] Test retry mechanisms
- [ ] Test dead letter queue
- [ ] All Milestone 1.6 acceptance criteria validated
- [ ] Test coverage >80%
- [ ] All tests passing
- [ ] Documentation complete

## Dependencies
- **External**: pytest, pytest-asyncio, kafka-python
- **Internal**: TASK-027 through TASK-031 (all integration components)

## Risks and Mitigation

### Risk 1: Test Complexity
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Use proper test fixtures, isolate tests, use mocks where appropriate

### Risk 2: Flaky Tests
- **Probability**: Medium
- **Impact**: Low
- **Mitigation**: Use proper timeouts, handle async operations correctly, add retry logic for tests

### Risk 3: Test Coverage Gaps
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Review acceptance criteria, add comprehensive test scenarios, use coverage tools

## Task Status
- [ ] Analysis Complete
- [ ] Planning Complete
- [ ] Implementation Complete
- [ ] Testing Complete
- [ ] Documentation Complete

## Notes
- Ensure all Milestone 1.6 acceptance criteria are validated
- Use proper test fixtures for Kafka, Airflow, and LangGraph
- Test both success and error scenarios
- Document test scenarios and execution steps
- Consider performance testing for high-volume scenarios

