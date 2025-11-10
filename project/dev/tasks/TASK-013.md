# TASK-013: Airflow-Kafka Integration

## Task Information
- **Task ID**: TASK-013
- **Created**: 2025-01-27
- **Status**: Waiting
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 4-5 hours
- **Actual Time**: TBD
- **Type**: Integration
- **Dependencies**: TASK-005 ✅, TASK-011 ✅
- **Parent PRD**: `project/docs/prd_phase1.md` - Milestone 1.3

## Task Description
Integrate Kafka producer into Airflow TaskFlow DAGs. Create reusable task decorator or utility for publishing workflow events to Kafka. Implement event publishing in existing DAGs to demonstrate end-to-end workflow event flow.

## Problem Statement
Airflow tasks need to publish workflow events to Kafka upon completion. This integration enables event-driven coordination between Airflow and other systems (LangGraph in Phase 2).

## Requirements

### Functional Requirements
- [ ] Kafka producer integrated into Airflow tasks
- [ ] Workflow events published on task completion
- [ ] Event publishing on DAG completion
- [ ] Error handling for Kafka publishing failures
- [ ] Reusable utility for event publishing
- [ ] Example DAG demonstrating integration

### Technical Requirements
- [ ] Kafka producer accessible in Airflow tasks
- [ ] Event schema integration
- [ ] Proper error handling
- [ ] TaskFlow API compatibility
- [ ] Configuration management

## Implementation Plan

### Phase 1: Analysis
- [ ] Review Airflow-Kafka integration patterns
- [ ] Design integration approach
- [ ] Plan reusable utilities
- [ ] Identify integration points

### Phase 2: Planning
- [ ] Design integration utilities
- [ ] Plan task decorator/function
- [ ] Design error handling
- [ ] Plan configuration

### Phase 3: Implementation
- [ ] Create Airflow-Kafka integration module
- [ ] Implement event publishing utility
- [ ] Create task decorator for event publishing
- [ ] Integrate into existing DAGs
- [ ] Add error handling
- [ ] Add configuration

### Phase 4: Testing
- [ ] Test event publishing from tasks
- [ ] Test error handling
- [ ] Verify events in Kafka
- [ ] Test with multiple DAGs

### Phase 5: Documentation
- [ ] Document integration approach
- [ ] Document usage examples
- [ ] Document configuration

## Technical Implementation

### Integration Utility
```python
from airflow.decorators import task
from typing import Callable, Any
from workflow_events import WorkflowEventProducer, WorkflowEvent, EventType, EventSource
import os

def get_kafka_producer():
    """Get Kafka producer instance."""
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    return WorkflowEventProducer(bootstrap_servers=bootstrap_servers)

@task
def publish_workflow_event(
    event_type: EventType,
    workflow_id: str,
    workflow_run_id: str,
    payload: dict,
    **context
):
    """Publish workflow event to Kafka."""
    producer = get_kafka_producer()
    
    try:
        event = WorkflowEvent(
            event_type=event_type,
            source=EventSource.AIRFLOW,
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
            payload={"data": payload},
            metadata={
                "environment": os.getenv("ENVIRONMENT", "dev"),
                "version": "1.0"
            }
        )
        
        producer.publish_event(event, topic='workflow-events')
        producer.close()
        
    except Exception as e:
        # Log error but don't fail the task
        print(f"Failed to publish event: {e}")
        producer.close()
```

### DAG Integration Example
```python
from airflow.decorators import dag, task
from datetime import datetime
from workflow_events import EventType

@dag(
    dag_id="example_kafka_integration",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
)
def example_kafka_dag():
    @task
    def process_data():
        """Process data."""
        result = {"status": "success", "count": 100}
        return result
    
    @task
    def publish_completion_event(**context):
        """Publish workflow completion event."""
        from workflow_integration import publish_workflow_event
        
        dag_run = context['dag_run']
        result = context['ti'].xcom_pull(task_ids='process_data')
        
        publish_workflow_event(
            event_type=EventType.WORKFLOW_COMPLETED,
            workflow_id=dag_run.dag_id,
            workflow_run_id=dag_run.run_id,
            payload=result
        )
    
    processed = process_data()
    publish_completion_event()(processed)

example_kafka_dag()
```

## Testing

### Manual Testing
- [ ] Test event publishing from Airflow task
- [ ] Verify events in Kafka
- [ ] Test error handling
- [ ] Test with multiple DAGs
- [ ] Verify event schema

### Automated Testing
- [ ] Integration tests
- [ ] Mock Kafka tests
- [ ] Error handling tests

## Acceptance Criteria
- [ ] Kafka producer integrated into Airflow
- [ ] Events published on task completion
- [ ] Events published on DAG completion
- [ ] Error handling working
- [ ] Reusable utility created
- [ ] Example DAG working
- [ ] Events visible in Kafka
- [ ] Tests passing
- [ ] Documentation complete

## Dependencies
- **External**: Apache Airflow, kafka-python
- **Internal**: TASK-005 (TaskFlow DAGs), TASK-011 (Kafka producer)

## Risks and Mitigation

### Risk 1: Kafka Connection Failures
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Implement retry logic, handle errors gracefully, don't fail tasks

### Risk 2: Event Publishing Delays
- **Probability**: Low
- **Impact**: Low
- **Mitigation**: Use async publishing, optimize producer configuration

### Risk 3: Configuration Management
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Use environment variables, document configuration

## Task Status
- [ ] Analysis Complete
- [ ] Planning Complete
- [ ] Implementation Complete
- [ ] Testing Complete
- [ ] Documentation Complete
- [ ] Quality Validation Complete

## Notes
- Don't fail Airflow tasks if Kafka publishing fails
- Use environment variables for configuration
- Keep integration simple and reusable
- Document all integration patterns

