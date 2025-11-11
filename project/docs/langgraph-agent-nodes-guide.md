# LangGraph Agent Nodes Guide

Complete guide to specialized agent nodes for LangGraph multi-agent workflows.

## Overview

Specialized agent nodes are the building blocks of multi-agent workflows. Each agent performs distinct tasks and updates state correctly, enabling orchestrator-worker collaboration patterns. This guide covers the agent nodes implemented in `project/langgraph_workflows/agent_nodes.py`.

## Agent Nodes

### data_agent

Specialized agent for data processing tasks. Processes data based on the task in state and routes to the analysis agent.

```python
from langgraph_workflows.agent_nodes import data_agent
from langgraph_workflows.state import MultiAgentState

state: MultiAgentState = {
    "messages": [],
    "task": "Process customer data for monthly analytics report",
    "agent_results": {},
    "current_agent": "data",
    "completed": False,
    "metadata": {}
}

result = data_agent(state)
# result["agent_results"]["data"] contains processed data
# result["current_agent"] == "analysis"
```

**Functionality**:
- Reads task from state
- Creates processed data result
- Updates `agent_results` with "data" key
- Routes to analysis agent by setting `current_agent` to "analysis"

**State Updates**:
- `agent_results`: Merged with new data result under "data" key
- `current_agent`: Set to "analysis" for routing

**Result Format**:
```python
{
    "agent": "data",
    "result": "data_processed",
    "data": {
        "processed": True,
        "task": "Process customer data for monthly analytics report"
    }
}
```

### analysis_agent

Specialized agent for analysis tasks. Performs analysis on data processed by the data agent and routes back to orchestrator.

```python
from langgraph_workflows.agent_nodes import analysis_agent
from langgraph_workflows.state import MultiAgentState

state: MultiAgentState = {
    "messages": [],
    "task": "Process customer data for monthly analytics report",
    "agent_results": {
        "data": {
            "agent": "data",
            "result": "data_processed",
            "data": {"processed": True}
        }
    },
    "current_agent": "analysis",
    "completed": False,
    "metadata": {}
}

result = analysis_agent(state)
# result["agent_results"]["analysis"] contains analysis result
# result["current_agent"] == "orchestrator"
```

**Functionality**:
- Reads data agent results from state
- Creates analysis result referencing data source
- Updates `agent_results` with "analysis" key
- Routes to orchestrator by setting `current_agent` to "orchestrator"

**State Updates**:
- `agent_results`: Merged with new analysis result under "analysis" key
- `current_agent`: Set to "orchestrator" for routing

**Result Format**:
```python
{
    "agent": "analysis",
    "result": "analysis_complete",
    "analysis": {
        "status": "success",
        "data_source": {
            "agent": "data",
            "result": "data_processed",
            "data": {"processed": True}
        }
    }
}
```

## Error Handling Versions

### data_agent_with_error_handling

Enhanced version of `data_agent` with comprehensive error handling.

```python
from langgraph_workflows.agent_nodes import data_agent_with_error_handling

result = data_agent_with_error_handling(state)
```

**Error Handling**:
- Catches exceptions during data processing
- Returns error state with error information
- Routes to orchestrator for error handling (not analysis agent)

**Error Result Format**:
```python
{
    "agent": "data",
    "result": "error",
    "error": "Error message"
}
```

### analysis_agent_with_error_handling

Enhanced version of `analysis_agent` with comprehensive error handling.

```python
from langgraph_workflows.agent_nodes import analysis_agent_with_error_handling

result = analysis_agent_with_error_handling(state)
```

**Error Handling**:
- Detects data agent errors in state
- Catches exceptions during analysis
- Returns error state with error information
- Routes to orchestrator for error handling

**Error Detection**:
- Checks if data agent result has `result == "error"`
- Propagates error to orchestrator if data processing failed

## State Update Patterns

### Agent Results Aggregation

Agent results are properly aggregated using the `merge_agent_results` reducer:

```python
# Initial state
state = {
    "agent_results": {},
    # ... other fields
}

# After data_agent
result1 = data_agent(state)
# result1["agent_results"] = {"data": {...}}

# After analysis_agent
updated_state = {**state, **result1, "agent_results": result1["agent_results"]}
result2 = analysis_agent(updated_state)
# result2["agent_results"] = {"data": {...}, "analysis": {...}}
```

### Current Agent Routing

Agents update `current_agent` to route to the next agent:

```python
# Data agent routes to analysis
result = data_agent(state)
assert result["current_agent"] == "analysis"

# Analysis agent routes to orchestrator
result = analysis_agent(updated_state)
assert result["current_agent"] == "orchestrator"
```

### State Update Format

All agents return dictionaries with state updates (not full state):

```python
result = data_agent(state)
# Returns: {"agent_results": {...}, "current_agent": "analysis"}
# Does NOT return: {"messages": ..., "task": ..., "completed": ...}
```

This allows LangGraph reducers to properly merge updates with existing state.

## Integration with MultiAgentState

Agent nodes are designed to work with `MultiAgentState`:

```python
from langgraph_workflows.state import MultiAgentState
from langgraph_workflows.agent_nodes import data_agent, analysis_agent

# Create initial state
state: MultiAgentState = {
    "messages": [],
    "task": "Process customer data for monthly analytics report",
    "agent_results": {},
    "current_agent": "data",
    "completed": False,
    "metadata": {}
}

# Execute data agent
data_result = data_agent(state)
updated_state = {
    **state,
    **data_result,
    "agent_results": data_result["agent_results"],
    "current_agent": data_result["current_agent"]
}

# Execute analysis agent
analysis_result = analysis_agent(updated_state)
final_state = {
    **updated_state,
    **analysis_result,
    "agent_results": analysis_result["agent_results"],
    "current_agent": analysis_result["current_agent"]
}
```

## Best Practices

### 1. Use Proper State Updates

Always return state updates (not full state) to work correctly with reducers:

```python
# ✅ Correct
return {
    "agent_results": {**existing, "data": result},
    "current_agent": "analysis"
}

# ❌ Incorrect
return {
    "messages": state["messages"],
    "task": state["task"],
    "agent_results": {**existing, "data": result},
    "current_agent": "analysis",
    "completed": state["completed"],
    "metadata": state["metadata"]
}
```

### 2. Namespace Agent Results

Always namespace agent results by agent name:

```python
# ✅ Correct
return {
    "agent_results": {
        **agent_results,
        "data": processed_data  # Namespaced by agent name
    }
}

# ❌ Incorrect
return {
    "agent_results": {
        **agent_results,
        "result": processed_data  # Not namespaced
    }
}
```

### 3. Handle Missing Data Gracefully

Check for missing data before processing:

```python
def analysis_agent(state: MultiAgentState) -> dict[str, Any]:
    agent_results = state.get("agent_results", {})
    data_result = agent_results.get("data", {})
    
    # Handle missing data gracefully
    if not data_result:
        # Return appropriate result or error
        pass
```

### 4. Use Error Handling Versions

For production workflows, use error handling versions:

```python
from langgraph_workflows.agent_nodes import (
    data_agent_with_error_handling,
    analysis_agent_with_error_handling
)

# Use error handling versions in production
result = data_agent_with_error_handling(state)
```

## Testing

All agent nodes are comprehensively tested with production conditions:

**Test Coverage**:
- Data agent functionality (4 tests)
- Analysis agent functionality (4 tests)
- Error handling (4 tests)
- State update patterns (3 tests)
- Result format consistency (1 test)

**Total**: 16 tests, all passing

**Run Tests**:
```bash
pytest project/tests/langgraph/test_agent_nodes.py -v
```

**Test Philosophy**:
- ✅ Real LangGraph components (no mocks)
- ✅ Production-like test data (no placeholders)
- ✅ Actual state updates (not stubbed)
- ✅ Real reducer functions (not mocked)

## Usage Examples

### Basic Workflow

```python
from langgraph_workflows.agent_nodes import data_agent, analysis_agent
from langgraph_workflows.state import MultiAgentState

# Initialize state
state: MultiAgentState = {
    "messages": [],
    "task": "Process customer data for monthly analytics report",
    "agent_results": {},
    "current_agent": "data",
    "completed": False,
    "metadata": {}
}

# Execute data agent
data_result = data_agent(state)
print(f"Data processed: {data_result['agent_results']['data']}")
print(f"Next agent: {data_result['current_agent']}")

# Update state
updated_state = {
    **state,
    **data_result,
    "agent_results": data_result["agent_results"],
    "current_agent": data_result["current_agent"]
}

# Execute analysis agent
analysis_result = analysis_agent(updated_state)
print(f"Analysis complete: {analysis_result['agent_results']['analysis']}")
print(f"Next agent: {analysis_result['current_agent']}")
```

### With Error Handling

```python
from langgraph_workflows.agent_nodes import (
    data_agent_with_error_handling,
    analysis_agent_with_error_handling
)

# Execute with error handling
data_result = data_agent_with_error_handling(state)

if data_result["agent_results"]["data"].get("result") == "error":
    print(f"Error: {data_result['agent_results']['data']['error']}")
else:
    # Continue with analysis
    updated_state = {**state, **data_result, ...}
    analysis_result = analysis_agent_with_error_handling(updated_state)
```

## Related Documentation

- [LangGraph State Guide](./langgraph-state-guide.md) - MultiAgentState definition and reducers
- [LangGraph Conditional Routing Guide](./langgraph-conditional-routing-guide.md) - Routing between agents
- [Task Documentation](../dev/tasks/TASK-021.md) - Specialized Agent Nodes Implementation

## Task Status

- ✅ TASK-021: Specialized Agent Nodes Implementation (Complete)
- TASK-022: Orchestrator Agent Node Implementation (Next)
- TASK-023: Multi-Agent StateGraph Configuration (Planned)

