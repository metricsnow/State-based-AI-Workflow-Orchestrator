# LangGraph Conditional Routing Guide

Complete guide to conditional routing in LangGraph StateGraph workflows, including routing functions, conditional edges, and dynamic workflow execution patterns.

## Overview

Conditional routing enables dynamic workflow execution paths based on state conditions. This guide covers the conditional routing implementation in `project/langgraph_workflows/conditional_workflow.py`.

## Conditional Routing Concepts

### What is Conditional Routing?

Conditional routing allows workflows to dynamically choose the next node to execute based on the current state. Unlike fixed edges that always route to the same node, conditional edges evaluate state and route to different nodes based on conditions.

### Key Components

1. **Routing Function**: Examines state and returns the next node name
2. **Conditional Edges**: Connect nodes with dynamic routing logic
3. **Routing Map**: Maps routing function return values to actual node names

## Implementation

### Routing Function

The routing function (`should_continue`) examines the current state and determines the next node:

```python
from langgraph_workflows.conditional_workflow import should_continue
from langgraph_workflows.state import SimpleState

def should_continue(state: SimpleState) -> str:
    """Route to next node based on state conditions."""
    status = state.get("status", "")
    
    if status == "processing":
        return "node_b"
    elif status == "completed":
        return "end"
    elif status == "error":
        return "error_handler"
    else:
        return "node_a"
```

**Routing Logic**:
- `"processing"` → routes to `node_b` for further processing
- `"completed"` → routes to `END` to terminate workflow
- `"error"` → routes to `error_handler` for error handling
- Default → routes to `node_a` for initial processing

### Conditional Node Functions

#### node_a_conditional

Modified node that preserves certain statuses for conditional routing:

```python
from langgraph_workflows.conditional_workflow import node_a_conditional

def node_a_conditional(state: SimpleState) -> SimpleState:
    """Conditional node_a that preserves or sets status based on state."""
    current_status = state.get("status", "")
    current_data = state.get("data", {})
    
    # Preserve "completed" and "error" statuses for conditional routing
    if current_status in ("completed", "error"):
        new_status = current_status
    else:
        new_status = "processing"
    
    return {
        "data": {**current_data, "step": "a", "processed": True},
        "status": new_status,
    }
```

#### error_handler

Dedicated error handling node:

```python
from langgraph_workflows.conditional_workflow import error_handler

def error_handler(state: SimpleState) -> SimpleState:
    """Error handler node that processes error states."""
    current_data = state.get("data", {})
    return {
        "data": {**current_data, "error_handled": True, "step": "error_handler"},
        "status": "error_handled",
    }
```

### Graph Construction

Building a StateGraph with conditional routing:

```python
from langgraph.graph import END, START, StateGraph
from langgraph_workflows.conditional_workflow import (
    node_a_conditional,
    node_b,
    error_handler,
    should_continue,
)
from langgraph_workflows.state import SimpleState

# Build graph with conditional routing
workflow = StateGraph(SimpleState)

# Add nodes
workflow.add_node("node_a", node_a_conditional)
workflow.add_node("node_b", node_b)
workflow.add_node("error_handler", error_handler)

# Add fixed edges: START -> node_a
workflow.add_edge(START, "node_a")

# Add conditional edge from node_a
workflow.add_conditional_edges(
    "node_a",
    should_continue,
    {
        "node_b": "node_b",
        "end": END,
        "error_handler": "error_handler",
        "node_a": "node_a",  # Default case
    },
)

# Add final edges
workflow.add_edge("node_b", END)
workflow.add_edge("error_handler", END)

# Compile graph
graph = workflow.compile()
```

### Routing Map

The routing map maps routing function return values to actual node names:

```python
ROUTING_MAP = {
    "node_b": "node_b",        # Route to node_b
    "end": END,                 # Route to END (terminate)
    "error_handler": "error_handler",  # Route to error handler
    "node_a": "node_a",         # Default route
}
```

**Important**: The routing map keys must match the return values from the routing function.

## Usage Examples

### Basic Conditional Workflow Execution

```python
from langgraph_workflows.conditional_workflow import execute_conditional_workflow

# Normal flow: initialized -> node_a -> node_b -> END
result = execute_conditional_workflow({"input": "test"}, "initialized")
assert result["status"] == "completed"
assert result["data"]["finalized"] is True

# Processing flow: processing -> node_a -> node_b -> END
result = execute_conditional_workflow({"input": "test"}, "processing")
assert result["status"] == "completed"
assert result["data"]["finalized"] is True

# Completed flow: completed -> node_a -> END (skips node_b)
result = execute_conditional_workflow({"input": "test"}, "completed")
assert result["status"] == "completed"
assert "finalized" not in result["data"]

# Error flow: error -> node_a -> error_handler -> END
result = execute_conditional_workflow({"input": "test"}, "error")
assert result["status"] == "error_handled"
assert result["data"]["error_handled"] is True
```

### Direct Graph Invocation

```python
from langgraph_workflows.conditional_workflow import graph
from langgraph_workflows.state import SimpleState

# Create initial state
initial_state: SimpleState = {
    "data": {"input": "test"},
    "status": "processing",
}

# Execute workflow
result = graph.invoke(initial_state)

# Verify result
assert result["status"] == "completed"
assert result["data"]["finalized"] is True
```

### Custom Routing Logic

You can create custom routing functions for different scenarios:

```python
def route_by_data_size(state: SimpleState) -> str:
    """Route based on data size."""
    data = state.get("data", {})
    data_size = len(str(data))
    
    if data_size > 1000:
        return "large_data_handler"
    elif data_size > 100:
        return "medium_data_handler"
    else:
        return "small_data_handler"

# Use in conditional edge
workflow.add_conditional_edges(
    "node_a",
    route_by_data_size,
    {
        "large_data_handler": "large_data_handler",
        "medium_data_handler": "medium_data_handler",
        "small_data_handler": "small_data_handler",
    },
)
```

## Routing Patterns

### Pattern 1: Status-Based Routing

Route based on workflow status:

```python
def route_by_status(state: SimpleState) -> str:
    status = state.get("status", "")
    if status == "completed":
        return "end"
    elif status == "error":
        return "error_handler"
    else:
        return "continue_processing"
```

### Pattern 2: Data-Based Routing

Route based on data content:

```python
def route_by_data(state: SimpleState) -> str:
    data = state.get("data", {})
    if "error" in data:
        return "error_handler"
    elif data.get("skip_processing"):
        return "end"
    else:
        return "process_data"
```

### Pattern 3: Multi-Condition Routing

Route based on multiple conditions:

```python
def route_by_multiple_conditions(state: SimpleState) -> str:
    status = state.get("status", "")
    data = state.get("data", {})
    
    if status == "error" or "error" in data:
        return "error_handler"
    elif status == "completed" and data.get("finalized"):
        return "end"
    elif data.get("requires_review"):
        return "review_node"
    else:
        return "continue_processing"
```

## Best Practices

1. **Always return valid node names**: Routing function must return values that exist in the routing map.

2. **Handle all possible states**: Ensure routing function handles all possible state values, including edge cases.

3. **Use descriptive routing values**: Use clear, descriptive names for routing return values (e.g., "error_handler" not "err").

4. **Validate routing map**: Ensure routing map keys match routing function return values exactly.

5. **Test all routing paths**: Test each possible routing path to ensure correct behavior.

6. **Preserve state for routing**: If routing depends on state values, ensure nodes preserve those values when needed.

7. **Document routing logic**: Clearly document what conditions lead to which routing paths.

## Error Handling

### Invalid Routing Values

If routing function returns a value not in the routing map, LangGraph will raise an error:

```python
# This will raise an error if "invalid_route" is not in routing map
def bad_routing_function(state: SimpleState) -> str:
    return "invalid_route"  # Not in routing map!

# Solution: Always return valid routing values
def good_routing_function(state: SimpleState) -> str:
    status = state.get("status", "")
    if status == "processing":
        return "node_b"  # Valid routing value
    else:
        return "end"  # Valid routing value
```

### Missing State Fields

Handle missing state fields gracefully:

```python
def safe_routing_function(state: SimpleState) -> str:
    # Use .get() with defaults
    status = state.get("status", "unknown")
    data = state.get("data", {})
    
    # Handle all cases
    if status == "processing":
        return "node_b"
    elif status == "completed":
        return "end"
    elif status == "error":
        return "error_handler"
    else:
        # Default route
        return "node_a"
```

## Testing

Comprehensive tests are available in `project/tests/langgraph/test_conditional_routing.py`:

```bash
# Run conditional routing tests
pytest project/tests/langgraph/test_conditional_routing.py -v

# Run with coverage
pytest project/tests/langgraph/test_conditional_routing.py --cov=project/langgraph_workflows/conditional_workflow --cov-report=term-missing
```

**Test Coverage**:
- Routing function tests (6 tests)
- Error handler tests (2 tests)
- Graph construction tests (2 tests)
- Workflow execution tests (5 tests)
- Routing path tests (3 tests)
- State-dependent routing tests (2 tests)
- Error handling tests (2 tests)
- Integration scenario tests (2 tests)

**Total**: 25 tests, all passing

### Test Examples

```python
def test_routing_processing():
    """Test routing when status is processing."""
    state: SimpleState = {"data": {}, "status": "processing"}
    result = should_continue(state)
    assert result == "node_b"

def test_workflow_processing_path():
    """Test workflow execution with processing status routes to node_b."""
    result = execute_conditional_workflow({"input": "test"}, "processing")
    assert result["status"] == "completed"
    assert result["data"]["finalized"] is True
```

## Implementation Details

### File Structure

```
project/langgraph_workflows/
├── __init__.py                    # Module initialization
├── state.py                       # State definitions
├── basic_workflow.py              # Basic workflow (TASK-016)
└── conditional_workflow.py       # Conditional routing workflow (TASK-017)
```

### Module Exports

```python
from langgraph_workflows.conditional_workflow import (
    node_a_conditional,      # Conditional node_a function
    error_handler,           # Error handler node
    should_continue,         # Routing function
    conditional_graph,       # Compiled StateGraph
    execute_conditional_workflow,  # Execution function
)
```

### Dependencies

- `langgraph`: StateGraph, conditional edges, START, END
- `langgraph_workflows.state`: SimpleState
- `langgraph_workflows.basic_workflow`: node_b

### Version Requirements

- LangGraph: 0.6.0+ (tested with 1.0.3)
- Python: 3.11+

## Related Documentation

- [LangGraph Official Documentation - Conditional Edges](https://langchain-ai.github.io/langgraph/how-tos/graph-api/#conditional-edges)
- [LangGraph State Guide](langgraph-state-guide.md) - State definitions and reducers
- [Task Documentation](../dev/tasks/TASK-017.md) - Implementation details

## Next Steps

- TASK-018: Checkpointing Configuration and Testing
- TASK-019: Stateful Workflow Integration Tests
- TASK-020: Multi-Agent State Structure Design

