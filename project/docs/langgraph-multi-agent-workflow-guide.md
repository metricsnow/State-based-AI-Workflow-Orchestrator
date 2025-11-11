# LangGraph Multi-Agent Workflow Guide

Complete guide to multi-agent workflow configuration with LangGraph StateGraph, orchestrator-worker pattern, and checkpointing.

## Overview

The multi-agent workflow implements a complete LangGraph StateGraph with multiple agent nodes (orchestrator, data_agent, analysis_agent) and conditional routing between agents. The workflow supports checkpointing for state persistence and enables resumable multi-agent collaboration. This guide covers the workflow implementation in `project/langgraph_workflows/multi_agent_workflow.py`.

## Workflow Architecture

### Graph Structure

```
┌─────────────┐
│    START    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Orchestrator│
│   Agent     │
└──────┬──────┘
       │
       ├─── Conditional Routing ───┐
       │                            │
       ▼                            ▼
┌──────────┐                  ┌──────────┐
│   Data   │                  │ Analysis │
│  Agent   │                  │  Agent   │
└────┬─────┘                  └────┬─────┘
     │                              │
     └────────── Fixed Edges ───────┘
                 │
                 ▼
          ┌─────────────┐
          │ Orchestrator │
          │   Agent      │
          └──────┬───────┘
                 │
                 ├─── Routes to END when complete
                 │
                 ▼
            ┌─────────┐
            │   END   │
            └─────────┘
```

### Components

- **Orchestrator Agent**: Coordinates workflow execution, evaluates agent results, determines next steps
- **Data Agent**: Processes data based on task requirements
- **Analysis Agent**: Performs analysis on processed data
- **StateGraph**: LangGraph StateGraph with MultiAgentState schema
- **Checkpointing**: InMemorySaver for state persistence
- **Conditional Routing**: Dynamic routing based on orchestrator decisions

## Core Functions

### multi_agent_graph

The compiled LangGraph StateGraph ready for execution with checkpointing enabled.

```python
from langgraph_workflows.multi_agent_workflow import multi_agent_graph
from langgraph_workflows.state import MultiAgentState
import uuid

# Create configuration with thread_id for checkpointing
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

# Create initial state
initial_state: MultiAgentState = {
    "messages": [],
    "task": "Process and analyze customer transaction data",
    "agent_results": {},
    "current_agent": "orchestrator",
    "completed": False,
    "metadata": {}
}

# Execute workflow
result = multi_agent_graph.invoke(initial_state, config=config)

# Verify completion
assert result["completed"] is True
assert "data" in result["agent_results"]
assert "analysis" in result["agent_results"]
```

**Graph Configuration**:
- **State Schema**: MultiAgentState (TypedDict with proper reducers)
- **Nodes**: orchestrator, data_agent, analysis_agent
- **Edges**: 
  - Fixed: START → orchestrator
  - Conditional: orchestrator → (data_agent | analysis_agent | END)
  - Fixed: data_agent → orchestrator, analysis_agent → orchestrator
- **Checkpointer**: InMemorySaver for state persistence

### execute_multi_agent_workflow

Convenient helper function for executing the multi-agent workflow with automatic thread_id generation.

```python
from langgraph_workflows.multi_agent_workflow import execute_multi_agent_workflow

# Execute with auto-generated thread_id
result, thread_id = execute_multi_agent_workflow("Process and analyze data")
print(f"Thread ID: {thread_id}")
print(f"Completed: {result['completed']}")

# Execute with custom thread_id
custom_thread_id = "my-workflow-123"
result, thread_id = execute_multi_agent_workflow("Process data", custom_thread_id)
assert thread_id == custom_thread_id
```

**Functionality**:
- Auto-generates thread_id if not provided
- Creates proper initial state with all required fields
- Invokes graph with checkpointing configuration
- Returns final state and thread_id for checkpoint tracking

**Parameters**:
- `task`: The task string to be processed by the workflow
- `thread_id`: Optional thread ID for checkpoint tracking (auto-generated if None)

**Returns**:
- Tuple of (final_state, thread_id)

## Workflow Execution Pattern

### Execution Sequence

1. **Start**: Workflow begins at orchestrator node
2. **Orchestrator Evaluation**: Orchestrator evaluates state and determines next agent
3. **Agent Execution**: Selected agent processes task and updates state
4. **Return to Orchestrator**: Agent routes back to orchestrator
5. **Repeat**: Orchestrator evaluates again and routes to next agent or END
6. **Completion**: Workflow terminates when all agents complete

### State Flow Example

```python
from langgraph_workflows.multi_agent_workflow import execute_multi_agent_workflow

# Execute complete workflow
result, thread_id = execute_multi_agent_workflow("Process and analyze Q4 2024 financial data")

# Workflow execution sequence:
# 1. START → orchestrator
# 2. orchestrator evaluates → routes to data_agent
# 3. data_agent executes → processes data → routes to orchestrator
# 4. orchestrator evaluates → routes to analysis_agent
# 5. analysis_agent executes → performs analysis → routes to orchestrator
# 6. orchestrator evaluates → detects completion → routes to END

# Verify results
assert result["completed"] is True
assert result["task"] == "Process and analyze Q4 2024 financial data"
assert "data" in result["agent_results"]
assert "analysis" in result["agent_results"]

# Check agent results structure
data_result = result["agent_results"]["data"]
analysis_result = result["agent_results"]["analysis"]

assert data_result["agent"] == "data"
assert data_result["result"] == "data_processed"
assert analysis_result["agent"] == "analysis"
assert analysis_result["result"] == "analysis_complete"
```

## Graph Configuration Details

### StateGraph Construction

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph_workflows.state import MultiAgentState
from langgraph_workflows.agent_nodes import data_agent, analysis_agent
from langgraph_workflows.orchestrator_agent import orchestrator_agent, route_to_agent

# Create checkpointer
checkpointer = InMemorySaver()

# Build graph
workflow = StateGraph(MultiAgentState)

# Add nodes
workflow.add_node("orchestrator", orchestrator_agent)
workflow.add_node("data_agent", data_agent)
workflow.add_node("analysis_agent", analysis_agent)

# Add fixed edge: START → orchestrator
workflow.add_edge(START, "orchestrator")

# Add conditional edge: orchestrator → (data_agent | analysis_agent | END)
workflow.add_conditional_edges(
    "orchestrator",
    route_to_agent,
    {
        "data": "data_agent",
        "analysis": "analysis_agent",
        "end": END,
    },
)

# Add fixed edges: agents → orchestrator
workflow.add_edge("data_agent", "orchestrator")
workflow.add_edge("analysis_agent", "orchestrator")

# Compile with checkpointing
multi_agent_graph = workflow.compile(checkpointer=checkpointer)
```

### Node Registration

All nodes must be registered before adding edges:

1. **Orchestrator Node**: Central coordination node
2. **Data Agent Node**: Data processing node
3. **Analysis Agent Node**: Analysis processing node

### Edge Configuration

**Fixed Edges**:
- `START → orchestrator`: Workflow always starts at orchestrator
- `data_agent → orchestrator`: Data agent returns to orchestrator after execution
- `analysis_agent → orchestrator`: Analysis agent returns to orchestrator after execution

**Conditional Edge**:
- `orchestrator → (data_agent | analysis_agent | END)`: Orchestrator routes based on state evaluation
  - Routes to `data_agent` if data processing not completed
  - Routes to `analysis_agent` if data completed but analysis not completed
  - Routes to `END` if all agents completed

### Checkpointing Configuration

The graph is compiled with `InMemorySaver` checkpointer for state persistence:

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
multi_agent_graph = workflow.compile(checkpointer=checkpointer)
```

**Checkpointing Features**:
- State persistence across workflow steps
- Thread ID-based checkpoint tracking
- State resumption from checkpoints (future enhancement)
- In-memory storage (development/testing)
- Production checkpointers (Redis/PostgreSQL) in Phase 4

## Usage Examples

### Basic Workflow Execution

```python
from langgraph_workflows.multi_agent_workflow import execute_multi_agent_workflow

# Simple execution
result, thread_id = execute_multi_agent_workflow("Process customer data")

print(f"Workflow completed: {result['completed']}")
print(f"Thread ID: {thread_id}")
print(f"Data agent result: {result['agent_results']['data']}")
print(f"Analysis agent result: {result['agent_results']['analysis']}")
```

### Custom Thread ID

```python
from langgraph_workflows.multi_agent_workflow import execute_multi_agent_workflow

# Execute with custom thread_id for checkpoint tracking
custom_id = "customer-data-processing-2024-01-27"
result, thread_id = execute_multi_agent_workflow("Process customer data", custom_id)

assert thread_id == custom_id
```

### Direct Graph Invocation

```python
from langgraph_workflows.multi_agent_workflow import multi_agent_graph
from langgraph_workflows.state import MultiAgentState
import uuid

# Create configuration
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

# Create initial state
initial_state: MultiAgentState = {
    "messages": [],
    "task": "Process and analyze financial data for Q4 2024 report",
    "agent_results": {},
    "current_agent": "orchestrator",
    "completed": False,
    "metadata": {"source": "api", "priority": "high"}
}

# Execute workflow
result = multi_agent_graph.invoke(initial_state, config=config)

# Verify results
assert result["completed"] is True
assert result["metadata"]["source"] == "api"
assert result["metadata"]["priority"] == "high"
```

### Multiple Workflow Executions

```python
from langgraph_workflows.multi_agent_workflow import execute_multi_agent_workflow

# Execute multiple independent workflows
tasks = [
    "Process Q1 2024 financial data",
    "Process Q2 2024 financial data",
    "Process Q3 2024 financial data"
]

results = []
for task in tasks:
    result, thread_id = execute_multi_agent_workflow(task)
    results.append({
        "task": task,
        "thread_id": thread_id,
        "completed": result["completed"],
        "has_data": "data" in result["agent_results"],
        "has_analysis": "analysis" in result["agent_results"]
    })

# Verify all workflows completed
for r in results:
    assert r["completed"] is True
    assert r["has_data"] is True
    assert r["has_analysis"] is True
```

## Orchestrator-Worker Pattern

The workflow implements the orchestrator-worker collaboration pattern:

### Pattern Benefits

1. **Centralized Coordination**: Orchestrator manages workflow execution
2. **Specialized Agents**: Each agent focuses on specific tasks
3. **Dynamic Routing**: Orchestrator determines next steps based on state
4. **State Management**: Centralized state evaluation and updates
5. **Error Handling**: Orchestrator can detect and handle errors

### Pattern Implementation

```python
# Orchestrator evaluates state
orchestrator_result = orchestrator_agent(state)
# Returns: {"current_agent": "data"}

# Worker agent executes
data_result = data_agent(state)
# Returns: {"agent_results": {...}, "current_agent": "orchestrator"}

# Orchestrator evaluates again
orchestrator_result = orchestrator_agent(state)
# Returns: {"current_agent": "analysis"}

# Next worker agent executes
analysis_result = analysis_agent(state)
# Returns: {"agent_results": {...}, "current_agent": "orchestrator"}

# Orchestrator detects completion
orchestrator_result = orchestrator_agent(state)
# Returns: {"completed": True, "current_agent": "end"}
```

## State Management

### State Schema

The workflow uses `MultiAgentState` TypedDict with proper reducers:

```python
from langgraph_workflows.state import MultiAgentState

state: MultiAgentState = {
    "messages": [],  # Annotated with add_messages reducer
    "task": "Process data",  # Annotated with last_value reducer
    "agent_results": {},  # Annotated with merge_agent_results reducer
    "current_agent": "orchestrator",  # Annotated with last_value reducer
    "completed": False,  # Annotated with last_value reducer
    "metadata": {}  # Annotated with merge_dicts reducer
}
```

### State Updates

State updates follow LangGraph reducer patterns:

- **Messages**: Appended using `add_messages` reducer
- **Task**: Overwritten using `last_value` reducer
- **Agent Results**: Merged using `merge_agent_results` reducer
- **Current Agent**: Overwritten using `last_value` reducer
- **Completed**: Overwritten using `last_value` reducer
- **Metadata**: Merged using `merge_dicts` reducer

### State Persistence

State persists across workflow steps via checkpointing:

```python
# State is automatically checkpointed after each node execution
result = multi_agent_graph.invoke(initial_state, config=config)

# State includes all agent results aggregated
assert "data" in result["agent_results"]
assert "analysis" in result["agent_results"]
assert result["task"] == initial_state["task"]  # Preserved
```

## Best Practices

### 1. Always Use Checkpointing

Enable checkpointing for state persistence:

```python
# ✅ Correct - Checkpointing enabled
config = {"configurable": {"thread_id": thread_id}}
result = multi_agent_graph.invoke(state, config=config)

# ❌ Incorrect - No checkpointing
result = multi_agent_graph.invoke(state)  # Missing config
```

### 2. Provide Complete Initial State

Always provide all required fields in initial state:

```python
# ✅ Correct - Complete state
initial_state: MultiAgentState = {
    "messages": [],
    "task": "Process data",
    "agent_results": {},
    "current_agent": "orchestrator",
    "completed": False,
    "metadata": {}
}

# ❌ Incorrect - Missing fields
initial_state = {"task": "Process data"}  # Missing required fields
```

### 3. Use Helper Function for Simplicity

Use `execute_multi_agent_workflow` for most use cases:

```python
# ✅ Correct - Simple and convenient
result, thread_id = execute_multi_agent_workflow("Process data")

# ❌ More complex - Direct invocation
config = {"configurable": {"thread_id": str(uuid.uuid4())}}
state = {...}  # Full state definition
result = multi_agent_graph.invoke(state, config=config)
```

### 4. Track Thread IDs

Store thread IDs for checkpoint tracking and resumption:

```python
# ✅ Correct - Track thread_id
result, thread_id = execute_multi_agent_workflow("Process data")
# Store thread_id for future resumption

# ❌ Incorrect - Discard thread_id
result, _ = execute_multi_agent_workflow("Process data")  # Lost thread_id
```

### 5. Verify Completion

Always verify workflow completion:

```python
# ✅ Correct - Verify completion
result, thread_id = execute_multi_agent_workflow("Process data")
assert result["completed"] is True
assert "data" in result["agent_results"]
assert "analysis" in result["agent_results"]

# ❌ Incorrect - Assume completion
result, _ = execute_multi_agent_workflow("Process data")
# No verification
```

## Testing

All workflow functions are comprehensively tested with production conditions:

**Test Coverage**:
- Graph construction (3 tests)
- Workflow execution (3 tests)
- Agent routing (3 tests)
- State persistence (2 tests)
- Checkpointing (3 tests)
- Error handling (2 tests)
- Integration (3 tests)

**Total**: 19 tests, all passing

**Run Tests**:
```bash
pytest project/tests/langgraph/test_multi_agent_workflow.py -v
```

**Test Philosophy**:
- ✅ Real LangGraph StateGraph (no mocks)
- ✅ Production-like test data (no placeholders)
- ✅ Actual checkpointing (InMemorySaver)
- ✅ Real agent nodes (not mocked)
- ✅ Complete workflow integration tests

## Related Documentation

- [LangGraph State Guide](./langgraph-state-guide.md) - MultiAgentState definition and reducers
- [LangGraph Agent Nodes Guide](./langgraph-agent-nodes-guide.md) - Specialized agent nodes (data_agent, analysis_agent)
- [LangGraph Orchestrator Guide](./langgraph-orchestrator-guide.md) - Orchestrator agent coordination
- [LangGraph Conditional Routing Guide](./langgraph-conditional-routing-guide.md) - Conditional routing patterns
- [LangGraph Checkpointing Guide](./langgraph-checkpointing-guide.md) - Checkpointing configuration
- [Task Documentation](../dev/tasks/TASK-023.md) - Multi-Agent StateGraph Configuration

## Task Status

- ✅ TASK-023: Multi-Agent StateGraph Configuration (Complete)
- TASK-024: Multi-Agent Collaboration Testing (Next)

