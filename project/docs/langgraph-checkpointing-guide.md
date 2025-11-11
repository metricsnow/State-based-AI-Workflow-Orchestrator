# LangGraph Checkpointing Guide

Complete guide to LangGraph checkpointing with InMemorySaver, state persistence, and workflow resumption.

## Overview

Checkpointing enables state persistence across workflow executions and allows workflows to be resumed from previous checkpoints. This guide covers the checkpointing implementation in `project/langgraph_workflows/checkpoint_workflow.py`.

## Checkpointing Configuration

### InMemorySaver Checkpointer

The `InMemorySaver` checkpointer provides in-memory state persistence for development and testing. For production, use Redis or PostgreSQL checkpointers (Phase 4).

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph

# Create checkpointer
checkpointer = InMemorySaver()

# Compile graph with checkpointer
workflow = StateGraph(SimpleState)
# ... add nodes and edges ...
graph = workflow.compile(checkpointer=checkpointer)
```

## Core Functions

### execute_with_checkpoint()

Execute workflow with checkpointing enabled. Automatically generates thread_id if not provided.

```python
from langgraph_workflows.checkpoint_workflow import execute_with_checkpoint
from langgraph_workflows.state import SimpleState

# Execute with auto-generated thread_id
state: SimpleState = {
    "data": {"input": "test"},
    "status": "processing"
}
result, thread_id = execute_with_checkpoint(state)

# Execute with custom thread_id
custom_thread_id = "my-workflow-123"
result, thread_id = execute_with_checkpoint(state, custom_thread_id)
assert thread_id == custom_thread_id
```

**Parameters**:
- `initial_state`: The initial state dictionary for the workflow
- `thread_id`: Optional thread ID for checkpoint tracking. If None, a new UUID is generated

**Returns**:
- Tuple containing (final_state, thread_id)

### resume_workflow()

Resume workflow from checkpoint using thread_id. Supports state merging with checkpointed state.

```python
from langgraph_workflows.checkpoint_workflow import resume_workflow

# First execution
state1: SimpleState = {"data": {"step": 1}, "status": "processing"}
result1, thread_id = execute_with_checkpoint(state1)

# Resume from checkpoint with additional state
state2: SimpleState = {"data": {"step": 2}, "status": "processing"}
result2 = resume_workflow(thread_id, state2)

# Resume without additional state (uses checkpointed state)
result3 = resume_workflow(thread_id)
```

**Parameters**:
- `thread_id`: The thread ID of the checkpoint to resume from
- `additional_state`: Optional state updates to merge with checkpointed state

**Returns**:
- Final state dictionary after workflow resumption

**Raises**:
- `ValueError`: If thread_id is invalid or checkpoint not found

### get_checkpoint_state()

Retrieve checkpointed state without executing workflow. Useful for inspection and debugging.

```python
from langgraph_workflows.checkpoint_workflow import get_checkpoint_state

# Get checkpoint state
checkpoint_state = get_checkpoint_state(thread_id)

if checkpoint_state:
    print(f"Current status: {checkpoint_state['status']}")
    print(f"Data: {checkpoint_state['data']}")
else:
    print("No checkpoint found")
```

**Parameters**:
- `thread_id`: The thread ID of the checkpoint to retrieve

**Returns**:
- Checkpointed state dictionary, or None if no checkpoint exists

### list_checkpoints()

List all checkpoints for a given thread_id. Enables inspection of workflow execution history.

```python
from langgraph_workflows.checkpoint_workflow import list_checkpoints

# List all checkpoints
checkpoints = list_checkpoints(thread_id)

for checkpoint in checkpoints:
    print(f"Checkpoint ID: {checkpoint['id']}")
    print(f"Timestamp: {checkpoint['ts']}")
```

**Parameters**:
- `thread_id`: The thread ID to list checkpoints for

**Returns**:
- List of checkpoint dictionaries

## Thread ID Management

### Automatic Generation

Thread IDs are automatically generated as UUIDs when not provided:

```python
result, thread_id = execute_with_checkpoint(state)
# thread_id is a UUID string like "550e8400-e29b-41d4-a716-446655440000"
```

### Custom Thread IDs

Provide custom thread IDs for workflow tracking:

```python
custom_id = "workflow-123"
result, thread_id = execute_with_checkpoint(state, custom_id)
assert thread_id == custom_id
```

### Thread Isolation

Different thread IDs maintain separate checkpoints:

```python
# Thread 1
state1: SimpleState = {"data": {"thread": 1}, "status": "processing"}
result1, thread_id_1 = execute_with_checkpoint(state1)

# Thread 2
state2: SimpleState = {"data": {"thread": 2}, "status": "processing"}
result2, thread_id_2 = execute_with_checkpoint(state2)

# Checkpoints are isolated
checkpoint1 = get_checkpoint_state(thread_id_1)
checkpoint2 = get_checkpoint_state(thread_id_2)

assert checkpoint1["data"]["thread"] == 1
assert checkpoint2["data"]["thread"] == 2
```

## State Persistence

### Persistence Across Steps

State persists across multiple workflow invocations with the same thread_id:

```python
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

# First invocation
state1: SimpleState = {"data": {"step": 1}, "status": "processing"}
result1 = checkpoint_graph.invoke(state1, config=config)

# Second invocation (state persists)
state2: SimpleState = {"data": {"step": 2}, "status": "processing"}
result2 = checkpoint_graph.invoke(state2, config=config)

# State is merged using reducers
assert "step" in result2["data"]
```

### State Merging

State updates are merged using reducers:
- Dictionary fields (`data`, `metadata`): Merged using `merge_dicts` reducer
- Status fields: Replaced using `last_value` reducer

```python
# Initial state
state1: SimpleState = {
    "data": {"a": 1, "b": 2},
    "status": "initialized"
}

# Update state
state2: SimpleState = {
    "data": {"b": 3, "c": 4},  # Merged: {"a": 1, "b": 3, "c": 4}
    "status": "processing"     # Replaced: "processing"
}
```

## Workflow Resumption

### Resuming with Additional State

Merge additional state with checkpointed state:

```python
# Initial execution
state1: SimpleState = {"data": {"step": 1, "value": "a"}, "status": "processing"}
result1, thread_id = execute_with_checkpoint(state1)

# Resume with additional state
state2: SimpleState = {"data": {"step": 2, "value": "b"}, "status": "processing"}
result2 = resume_workflow(thread_id, state2)

# State is merged: checkpointed state + additional state
assert result2["data"]["step"] == 2
assert result2["data"]["value"] == "b"
```

### Resuming Without Additional State

Resume using only checkpointed state:

```python
# Initial execution
state: SimpleState = {"data": {"initial": True}, "status": "processing"}
result1, thread_id = execute_with_checkpoint(state)

# Resume without additional state
result2 = resume_workflow(thread_id)

# Uses checkpointed state as-is
assert "initial" in result2["data"]
```

## Error Handling

### Non-Existent Checkpoints

Resuming from non-existent checkpoints raises ValueError:

```python
from langgraph_workflows.checkpoint_workflow import resume_workflow

non_existent_thread_id = str(uuid.uuid4())
state: SimpleState = {"data": {}, "status": "processing"}

try:
    resume_workflow(non_existent_thread_id, state)
except ValueError as e:
    print(f"Error: {e}")  # "No checkpoint found for thread_id: ..."
```

### Invalid State Handling

Invalid state structures are handled gracefully:

```python
# LangGraph may accept invalid states with defaults or raise errors
invalid_state = {"invalid": "data"}

try:
    result, _ = execute_with_checkpoint(invalid_state)
    # If accepted, verify it returns something
    assert result is not None
except (TypeError, KeyError, ValueError):
    # If error raised, that's acceptable behavior
    pass
```

## Complete Example

### End-to-End Checkpointing Workflow

```python
import uuid
from langgraph_workflows.checkpoint_workflow import (
    execute_with_checkpoint,
    resume_workflow,
    get_checkpoint_state,
    list_checkpoints
)
from langgraph_workflows.state import SimpleState

# Step 1: Initial execution
state1: SimpleState = {
    "data": {"workflow_step": 1, "initialized": True},
    "status": "processing"
}
result1, thread_id = execute_with_checkpoint(state1)
print(f"Thread ID: {thread_id}")
print(f"Result: {result1}")

# Step 2: Verify checkpoint exists
checkpoint1 = get_checkpoint_state(thread_id)
assert checkpoint1 is not None
assert checkpoint1["data"]["workflow_step"] == 1

# Step 3: Resume workflow
state2: SimpleState = {
    "data": {"workflow_step": 2, "resumed": True},
    "status": "processing"
}
result2 = resume_workflow(thread_id, state2)
print(f"Resumed result: {result2}")

# Step 4: Verify final checkpoint
checkpoint2 = get_checkpoint_state(thread_id)
assert checkpoint2["data"]["workflow_step"] == 2
assert checkpoint2["data"]["resumed"] is True

# Step 5: List all checkpoints
checkpoints = list_checkpoints(thread_id)
print(f"Total checkpoints: {len(checkpoints)}")
```

## Best Practices

1. **Use UUIDs for Thread IDs**: Generate unique thread IDs using `uuid.uuid4()` for production workflows
2. **Validate State Before Checkpointing**: Ensure state structure is valid before executing workflows
3. **Handle Checkpoint Errors**: Always handle `ValueError` when resuming from checkpoints
4. **Test Thread Isolation**: Verify different thread IDs maintain separate checkpoints
5. **Monitor Checkpoint State**: Use `get_checkpoint_state()` to inspect workflow state during debugging
6. **Production Checkpointers**: Use Redis or PostgreSQL checkpointers for production (Phase 4)

## Testing

Comprehensive tests are available in `project/tests/langgraph/test_checkpointing.py`:

```bash
# Run checkpointing tests
pytest project/tests/langgraph/test_checkpointing.py -v

# Run with coverage
pytest project/tests/langgraph/test_checkpointing.py --cov=project/langgraph_workflows/checkpoint_workflow --cov-report=term-missing
```

**Test Coverage**:
- 22 comprehensive tests covering all checkpointing functionality
- Checkpointer configuration tests
- Thread ID management tests
- Checkpoint saving/loading tests
- State persistence tests
- Workflow resumption tests
- Error handling tests
- Integration scenario tests

## Module Exports

The checkpointing module exports the following:

```python
from langgraph_workflows.checkpoint_workflow import (
    checkpoint_graph,        # Compiled StateGraph with checkpointing
    execute_with_checkpoint, # Workflow execution with checkpointing
    resume_workflow,         # Workflow resumption from checkpoint
    get_checkpoint_state,    # Retrieve checkpoint state
    list_checkpoints         # List checkpoints for thread_id
)
```

## Dependencies

- **LangGraph**: Required for StateGraph and checkpointing
- **InMemorySaver**: Development checkpointer (from `langgraph.checkpoint.memory`)
- **uuid**: For thread ID generation (Python standard library)

## Next Steps

- **TASK-019**: Stateful Workflow Integration Tests - Comprehensive integration tests for complete stateful workflow
- **TASK-020**: Multi-Agent State Structure Design - Design state structure for multi-agent workflows
- **Phase 4**: Production checkpointers (Redis, PostgreSQL) for persistent state storage

