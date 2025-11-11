# LangGraph State Definition Guide

Complete guide to LangGraph state definitions, reducers, and state management patterns.

## Overview

LangGraph workflows require well-defined state schemas with proper reducers to manage state updates correctly. This guide covers the state definitions implemented in `project/langgraph_workflows/state.py`.

## State Schemas

### WorkflowState

Complex state schema for multi-agent workflows with message handling, task data, agent results, workflow status tracking, and metadata.

```python
from langgraph_workflows.state import WorkflowState

state: WorkflowState = {
    "messages": [],
    "task_data": {},
    "agent_results": {},
    "workflow_status": "initialized",
    "metadata": {}
}
```

**Fields**:
- `messages`: `Annotated[list[Any], add_messages]` - Message list with add_messages reducer
- `task_data`: `Annotated[dict[str, Any], merge_dicts]` - Task data with merge reducer
- `agent_results`: `Annotated[dict[str, Any], merge_dicts]` - Agent results with merge reducer
- `workflow_status`: `Annotated[str, last_value]` - Status with last_value reducer
- `metadata`: `Annotated[dict[str, Any], merge_dicts]` - Metadata with merge reducer

### SimpleState

Simplified state schema for basic workflows that don't require complex message handling or multiple agent coordination.

```python
from langgraph_workflows.state import SimpleState

state: SimpleState = {
    "data": {},
    "status": "initialized"
}
```

**Fields**:
- `data`: `Annotated[dict[str, Any], merge_dicts]` - Workflow data with merge reducer
- `status`: `Annotated[str, last_value]` - Status with last_value reducer

### MultiAgentState

State schema for multi-agent LangGraph workflows with orchestrator-worker patterns. Supports agent coordination, result aggregation, and workflow management.

```python
from langgraph_workflows.state import MultiAgentState

state: MultiAgentState = {
    "messages": [],
    "task": "process_data",
    "agent_results": {},
    "current_agent": "orchestrator",
    "completed": False,
    "metadata": {}
}
```

**Fields**:
- `messages`: `Annotated[list[Any], add_messages]` - Message list with add_messages reducer
- `task`: `Annotated[str, last_value]` - Current task string with last_value reducer
- `agent_results`: `Annotated[dict[str, Any], merge_agent_results]` - Agent results with merge reducer
- `current_agent`: `Annotated[str, last_value]` - Current active agent with last_value reducer
- `completed`: `Annotated[bool, last_value]` - Workflow completion status with last_value reducer
- `metadata`: `Annotated[dict[str, Any], merge_dicts]` - Metadata with merge reducer

## Reducers

Reducers specify how state updates are applied. They enable proper state aggregation and prevent overwriting existing values.

### add_messages

Built-in LangGraph reducer for message lists. Appends messages rather than replacing them.

```python
from langgraph.graph.message import add_messages

messages: Annotated[list[Any], add_messages]
```

**Usage**: Automatically handles message appending in LangGraph workflows.

### merge_dicts

Custom reducer for dictionary fields. Merges dictionaries with new values taking precedence.

```python
from langgraph_workflows.state import merge_dicts

def merge_dicts(x: dict[str, Any], y: dict[str, Any]) -> dict[str, Any]:
    """Merge two dictionaries, with y taking precedence for conflicts."""
    return {**x, **y}
```

**Usage**:
```python
existing = {"a": 1, "b": 2}
update = {"b": 3, "c": 4}
result = merge_dicts(existing, update)
# result = {"a": 1, "b": 3, "c": 4}
```

### last_value

Custom reducer for status fields. Returns the latest value, overwriting previous values.

```python
from langgraph_workflows.state import last_value

def last_value(x: str, y: str) -> str:
    """Return the last value (y)."""
    return y
```

**Usage**:
```python
current = last_value("initialized", "processing")
# current = "processing"
```

### merge_agent_results

Custom reducer for agent results aggregation. Merges agent results dictionaries with new values taking precedence.

```python
from langgraph_workflows.state import merge_agent_results

def merge_agent_results(x: dict[str, Any], y: dict[str, Any]) -> dict[str, Any]:
    """Merge agent results, with y taking precedence for conflicts."""
    return {**x, **y}
```

**Usage**:
```python
existing = {"data": {"agent": "data", "result": "processed"}}
update = {"analysis": {"agent": "analysis", "result": "complete"}}
result = merge_agent_results(existing, update)
# result = {
#     "data": {"agent": "data", "result": "processed"},
#     "analysis": {"agent": "analysis", "result": "complete"}
# }
```

## State Validation

### validate_state

Validates WorkflowState structure and required fields.

```python
from langgraph_workflows.state import validate_state, WorkflowState

state: WorkflowState = {
    "messages": [],
    "task_data": {},
    "workflow_status": "initialized",
    "agent_results": {},
    "metadata": {}
}

assert validate_state(state)  # True
```

**Required Fields**:
- `messages`
- `task_data`
- `workflow_status`

### validate_simple_state

Validates SimpleState structure and required fields.

```python
from langgraph_workflows.state import validate_simple_state, SimpleState

state: SimpleState = {
    "data": {},
    "status": "initialized"
}

assert validate_simple_state(state)  # True
```

**Required Fields**:
- `data`
- `status`

### validate_multi_agent_state

Validates MultiAgentState structure and required fields.

```python
from langgraph_workflows.state import validate_multi_agent_state, MultiAgentState

state: MultiAgentState = {
    "messages": [],
    "task": "test_task",
    "agent_results": {},
    "current_agent": "orchestrator",
    "completed": False,
    "metadata": {}
}

assert validate_multi_agent_state(state)  # True
```

**Required Fields**:
- `messages`
- `task`
- `agent_results`
- `current_agent`
- `completed`

## Usage Examples

### Creating State

```python
from langgraph_workflows.state import WorkflowState, validate_state

# Create workflow state
state: WorkflowState = {
    "messages": [],
    "task_data": {"task_id": "task_123"},
    "agent_results": {},
    "workflow_status": "initialized",
    "metadata": {"environment": "dev"}
}

# Validate state
assert validate_state(state)
```

### Updating State

In LangGraph workflows, state updates are handled automatically by reducers:

```python
# Node function returns partial state update
def node_function(state: WorkflowState) -> dict:
    return {
        "task_data": {"new_key": "new_value"},
        "workflow_status": "processing"
    }

# LangGraph automatically applies reducers:
# - task_data: merge_dicts merges with existing
# - workflow_status: last_value replaces with "processing"
```

### State Updates with Reducers

```python
from langgraph_workflows.state import merge_dicts, last_value

# Dictionary merge
existing_data = {"key1": "value1"}
update_data = {"key2": "value2", "key1": "updated"}
merged = merge_dicts(existing_data, update_data)
# merged = {"key1": "updated", "key2": "value2"}

# Status update
current_status = "initialized"
new_status = last_value(current_status, "processing")
# new_status = "processing"
```

## Best Practices

1. **Always use reducers for fields that need aggregation**: Use `merge_dicts` for dictionaries, `add_messages` for message lists, `last_value` for status fields.

2. **Validate state before processing**: Use `validate_state()` or `validate_simple_state()` to ensure state structure is correct.

3. **Use appropriate state schema**: Use `WorkflowState` for complex workflows with task data, `MultiAgentState` for orchestrator-worker multi-agent patterns, `SimpleState` for basic workflows.

4. **Type hints are required**: Always use type hints (`WorkflowState`, `SimpleState`) for better IDE support and type checking.

5. **Test reducers independently**: Test reducer functions separately before using in workflows.

## Testing

Comprehensive tests are available in `project/tests/langgraph/test_state.py`:

```bash
# Run state tests
pytest project/tests/langgraph/test_state.py -v

# Run with coverage
pytest project/tests/langgraph/test_state.py --cov=project/langgraph_workflows/state --cov-report=term-missing
```

**Test Coverage**:
- State creation (6 tests: 3 WorkflowState, 3 MultiAgentState)
- Message reducer (3 tests)
- Data reducer (4 tests)
- Agent results reducer (4 tests)
- Status reducer (3 tests)
- State validation (12 tests: 7 WorkflowState, 5 MultiAgentState)
- State updates (9 tests: 4 WorkflowState, 5 MultiAgentState)
- Type hints (3 tests: 2 WorkflowState, 1 MultiAgentState)

**Total**: 45 tests, all passing

## Implementation Details

### File Structure

```
project/langgraph_workflows/
├── __init__.py          # Module initialization
└── state.py             # State definitions and reducers
```

### Dependencies

- `langgraph`: StateGraph and message handling
- `typing_extensions`: TypedDict support
- `pydantic`: Optional validation (if needed)

### Version Requirements

- LangGraph: 0.6.0+ (tested with 1.0.3)
- typing-extensions: 4.8.0+
- Python: 3.11+

## Related Documentation

- [LangGraph Official Documentation](https://langchain-ai.github.io/langgraph/)
- [State Management Patterns](https://langchain-ai.github.io/langgraph/concepts/low_level/#reducers)
- [Task Documentation](../dev/tasks/TASK-015.md) - State definitions
- [Task Documentation](../dev/tasks/TASK-020.md) - Multi-Agent State Structure

## Next Steps

- ✅ TASK-016: Basic StateGraph with Nodes Implementation (Complete)
- ✅ TASK-017: Conditional Routing Implementation (Complete)
- ✅ TASK-018: Checkpointing Configuration and Testing (Complete)
- ✅ TASK-019: Stateful Workflow Integration Tests (Complete)
- ✅ TASK-020: Multi-Agent State Structure Design (Complete)
- TASK-021: Specialized Agent Nodes Implementation

## Related Guides

- [LangGraph Conditional Routing Guide](langgraph-conditional-routing-guide.md) - Conditional routing patterns and implementation

