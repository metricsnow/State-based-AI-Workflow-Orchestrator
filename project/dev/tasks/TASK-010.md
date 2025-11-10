# TASK-010: Event Schema Definition

## Task Information
- **Task ID**: TASK-010
- **Created**: 2025-01-27
- **Status**: Waiting
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 2-3 hours
- **Actual Time**: TBD
- **Type**: Feature
- **Dependencies**: None
- **Parent PRD**: `project/docs/prd_phase1.md` - Milestone 1.3

## Task Description
Define and document the event schema for workflow events published to Kafka. Create schema validation, Python data classes, and JSON schema definitions. Ensure schema is versioned and extensible.

## Problem Statement
A standardized event schema is required for consistent event structure across all workflow events. This schema enables type safety, validation, and future schema evolution.

## Requirements

### Functional Requirements
- [ ] Event schema defined (JSON structure)
- [ ] Python data classes for events
- [ ] JSON schema validation
- [ ] Schema versioning support
- [ ] Event type enumeration
- [ ] Schema documentation

### Technical Requirements
- [ ] Pydantic models for validation
- [ ] JSON schema generation
- [ ] Type hints
- [ ] Schema versioning mechanism
- [ ] Event serialization/deserialization

## Implementation Plan

### Phase 1: Analysis
- [ ] Review PRD event schema requirements
- [ ] Design event structure
- [ ] Plan schema versioning
- [ ] Identify event types

### Phase 2: Planning
- [ ] Design event schema structure
- [ ] Plan Python data models
- [ ] Design validation approach
- [ ] Plan documentation

### Phase 3: Implementation
- [ ] Create event schema module
- [ ] Define Pydantic models
- [ ] Implement event types enum
- [ ] Add schema validation
- [ ] Create JSON schema
- [ ] Add serialization/deserialization

### Phase 4: Testing
- [ ] Test event creation
- [ ] Test schema validation
- [ ] Test serialization
- [ ] Test deserialization
- [ ] Test invalid events

### Phase 5: Documentation
- [ ] Document event schema
- [ ] Document event types
- [ ] Document validation rules
- [ ] Document versioning

## Technical Implementation

### Event Schema (from PRD)
```json
{
  "event_id": "uuid",
  "event_type": "workflow.triggered|workflow.completed|workflow.failed",
  "timestamp": "ISO 8601",
  "source": "airflow|langgraph|fastapi",
  "workflow_id": "dag_id or workflow_id",
  "workflow_run_id": "run_id",
  "payload": {
    "data": "workflow-specific data"
  },
  "metadata": {
    "environment": "dev|staging|prod",
    "version": "1.0"
  }
}
```

### Python Implementation
```python
from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class EventType(str, Enum):
    WORKFLOW_TRIGGERED = "workflow.triggered"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"

class EventSource(str, Enum):
    AIRFLOW = "airflow"
    LANGGRAPH = "langgraph"
    FASTAPI = "fastapi"

class WorkflowEventPayload(BaseModel):
    data: Dict[str, Any]

class WorkflowEventMetadata(BaseModel):
    environment: str = Field(..., pattern="^(dev|staging|prod)$")
    version: str = "1.0"

class WorkflowEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: EventSource
    workflow_id: str
    workflow_run_id: str
    payload: WorkflowEventPayload
    metadata: WorkflowEventMetadata

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
```

## Testing

### Manual Testing
- [ ] Create sample events
- [ ] Validate event structure
- [ ] Test serialization to JSON
- [ ] Test deserialization from JSON
- [ ] Test invalid events

### Automated Testing
- [ ] Unit tests for event models
- [ ] Validation tests
- [ ] Serialization tests
- [ ] Schema versioning tests

## Acceptance Criteria
- [ ] Event schema defined and documented
- [ ] Python data classes implemented
- [ ] JSON schema validation working
- [ ] Event serialization/deserialization working
- [ ] Schema versioning supported
- [ ] All event types defined
- [ ] Tests passing
- [ ] Documentation complete

## Dependencies
- **External**: pydantic
- **Internal**: None

## Risks and Mitigation

### Risk 1: Schema Evolution
- **Probability**: High
- **Impact**: Medium
- **Mitigation**: Implement versioning, design for extensibility, document migration path

### Risk 2: Validation Performance
- **Probability**: Low
- **Impact**: Low
- **Mitigation**: Use Pydantic (fast validation), optimize validation logic

## Task Status
- [x] Analysis Complete
  - [x] Reviewed PRD event schema requirements
  - [x] Designed event structure based on PRD specification
  - [x] Planned schema versioning approach
  - [x] Identified event types (triggered, completed, failed)
- [x] Planning Complete
  - [x] Designed event schema structure with Pydantic models
  - [x] Planned Python data models (BaseModel with Field validation)
  - [x] Designed validation approach using Pydantic
  - [x] Planned documentation structure
- [x] Implementation Complete
  - [x] Created workflow_events module with schema.py
  - [x] Defined Pydantic models (WorkflowEvent, WorkflowEventPayload, WorkflowEventMetadata)
  - [x] Implemented event types enum (EventType)
  - [x] Implemented event source enum (EventSource)
  - [x] Added schema validation with Pydantic Field constraints
  - [x] Created JSON schema generation utilities (schema_utils.py)
  - [x] Added serialization/deserialization methods
  - [x] Implemented custom field serializers for UUID and datetime
- [x] Testing Complete
  - [x] Created comprehensive unit tests (26 tests)
  - [x] All tests passing (26/26)
  - [x] Tested event creation with defaults and explicit values
  - [x] Tested schema validation (valid and invalid events)
  - [x] Tested JSON serialization/deserialization
  - [x] Tested round-trip serialization
  - [x] Tested schema versioning support
  - [x] Tested all event types and sources
- [x] Documentation Complete
  - [x] Created event-schema-guide.md with comprehensive documentation
  - [x] Documented event schema structure and fields
  - [x] Documented event types and sources
  - [x] Documented validation rules and examples
  - [x] Documented serialization/deserialization patterns
  - [x] Documented JSON schema generation
  - [x] Documented schema versioning approach
  - [x] Added code examples and best practices
- [ ] Quality Validation Complete (Pending Mission-QA review)

## Notes
- Use Pydantic for validation and serialization
- Design schema for future extensibility
- Document all event types
- Version schema for future changes

