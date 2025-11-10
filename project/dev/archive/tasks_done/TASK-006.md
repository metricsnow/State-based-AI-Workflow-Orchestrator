# TASK-006: Implement Data Passing with XCom

## Task Information
- **Task ID**: TASK-006
- **Created**: 2025-01-27
- **Status**: Done
- **Priority**: Medium
- **Agent**: Mission Executor
- **Estimated Time**: 2-3 hours
- **Actual Time**: TBD
- **Type**: Enhancement
- **Dependencies**: TASK-005 ✅
- **Parent PRD**: `project/docs/prd_phase1.md` - Milestone 1.2

## Task Description
Enhance TaskFlow DAGs with proper data passing patterns using XCom. Implement multiple data passing scenarios including simple values, dictionaries, and lists. Validate XCom data passing works correctly across all task dependencies.

## Problem Statement
While TaskFlow API handles XCom automatically, we need to validate and demonstrate proper data passing patterns, handle edge cases, and ensure data integrity across task boundaries.

## Requirements

### Functional Requirements
- [ ] Simple value passing between tasks
- [ ] Dictionary data passing
- [ ] List data passing
- [ ] Multiple return values (multiple_outputs)
- [ ] Data validation in receiving tasks
- [ ] Error handling for invalid data

### Technical Requirements
- [ ] Use TaskFlow API automatic XCom
- [ ] Implement type hints for data validation
- [ ] Add data validation logic
- [ ] Handle XCom size limitations
- [ ] Document data passing patterns

## Implementation Plan

### Phase 1: Analysis
- [ ] Review XCom best practices
- [ ] Identify data passing patterns needed
- [ ] Plan data validation approach
- [ ] Review XCom size limitations

### Phase 2: Planning
- [ ] Design data passing examples
- [ ] Plan validation logic
- [ ] Design error handling

### Phase 3: Implementation
- [ ] Create example DAG with simple value passing
- [ ] Create example with dictionary passing
- [ ] Create example with list passing
- [ ] Implement multiple_outputs pattern
- [ ] Add data validation
- [ ] Add error handling

### Phase 4: Testing
- [ ] Test simple value passing
- [ ] Test dictionary passing
- [ ] Test list passing
- [ ] Test multiple_outputs
- [ ] Test data validation
- [ ] Test error handling

### Phase 5: Documentation
- [ ] Document data passing patterns
- [ ] Document XCom limitations
- [ ] Document best practices

## Technical Implementation

### Simple Value Passing
```python
@task
def extract() -> int:
    return 42

@task
def process(value: int) -> int:
    return value * 2
```

### Dictionary Passing
```python
@task
def extract() -> Dict[str, List[int]]:
    return {"data": [1, 2, 3, 4, 5]}

@task
def transform(data: Dict[str, List[int]]) -> Dict[str, List[int]]:
    return {"transformed": [x * 2 for x in data["data"]]}
```

### Multiple Outputs
```python
@task(multiple_outputs=True)
def extract() -> Dict[str, Any]:
    return {
        "count": 100,
        "data": [1, 2, 3],
        "status": "success"
    }

@task
def process(count: int, data: List[int], status: str) -> Dict:
    return {"processed": True}
```

### Data Validation
```python
@task
def validate_data(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")
    if "data" not in data:
        raise ValueError("Data must contain 'data' key")
    return data
```

## Testing

### Manual Testing
- [ ] Test each data passing pattern
- [ ] Verify data integrity
- [ ] Test error handling
- [ ] Check XCom in Airflow UI

### Automated Testing
- [ ] Unit tests for data passing
- [ ] Validation tests
- [ ] Error handling tests

## Acceptance Criteria
- [ ] Simple value passing working
- [ ] Dictionary passing working
- [ ] List passing working
- [ ] Multiple outputs working
- [ ] Data validation implemented
- [ ] Error handling working
- [ ] All tests passing
- [ ] Documentation complete

## Dependencies
- **External**: Apache Airflow 2.8.4+
- **Internal**: TASK-005 (TaskFlow API migration)

## Risks and Mitigation

### Risk 1: XCom Size Limitations
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Document size limits, use external storage for large data, validate data size

### Risk 2: Type Mismatches
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Use type hints, implement validation, add error handling

## Task Status
- [x] Analysis Complete
  - [x] Reviewed XCom best practices via MCP Context7
  - [x] Identified data passing patterns needed
  - [x] Planned data validation approach
  - [x] Reviewed XCom size limitations (48KB default)
- [x] Planning Complete
  - [x] Designed data passing examples
  - [x] Planned validation logic
  - [x] Designed error handling
- [x] Implementation Complete
  - [x] Created xcom_data_passing_dag.py with all patterns
  - [x] Implemented simple value passing (int)
  - [x] Implemented dictionary passing
  - [x] Implemented list passing
  - [x] Implemented multiple_outputs pattern
  - [x] Added data validation logic
  - [x] Added error handling for invalid data
  - [x] All patterns use TaskFlow API automatic XCom
  - [x] Type hints added to all task functions
- [x] Testing Complete
  - [x] Created comprehensive unit tests (36 tests)
  - [x] All tests passing (36/36)
  - [x] Tested simple value passing
  - [x] Tested dictionary passing
  - [x] Tested list passing
  - [x] Tested multiple_outputs
  - [x] Tested data validation
  - [x] Tested error handling
  - [x] DAG imports successfully without errors
- [x] Documentation Complete
  - [x] Code comments and docstrings added
  - [x] Data passing patterns documented
  - [x] XCom limitations documented in code
  - [x] Best practices documented
- [x] Quality Validation Complete
  - [x] Code quality validated against Airflow TaskFlow API best practices
  - [x] All 36 unit tests passing
  - [x] Implementation follows TaskFlow API patterns correctly
  - [x] Type hints properly implemented
  - [x] Error handling comprehensive
  - [x] Documentation complete and accurate
  - [x] XCom data passing patterns validated
  - [x] DAG structure follows best practices

## Notes
- XCom has size limitations (default 48KB)
- Use external storage (S3, database) for large data
- Type hints help catch errors early
- TaskFlow API handles XCom automatically

