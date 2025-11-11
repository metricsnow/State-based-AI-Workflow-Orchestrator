# LangGraph Orchestrator Agent Guide

Complete guide to orchestrator agent node for LangGraph multi-agent workflows.

## Overview

The orchestrator agent coordinates multi-agent workflow execution by evaluating agent results, determining next steps, and managing workflow completion. This enables the orchestrator-worker collaboration pattern where specialized agents are coordinated by a central orchestrator. This guide covers the orchestrator implementation in `project/langgraph_workflows/orchestrator_agent.py`.

## Orchestrator Functions

### orchestrator_agent

Main orchestrator function that coordinates workflow execution by evaluating state and determining routing decisions.

```python
from langgraph_workflows.orchestrator_agent import orchestrator_agent
from langgraph_workflows.state import MultiAgentState

state: MultiAgentState = {
    "messages": [],
    "task": "Process and analyze customer transaction data for Q4 2024 financial report",
    "agent_results": {},
    "current_agent": "orchestrator",
    "completed": False,
    "metadata": {}
}

result = orchestrator_agent(state)
# result["current_agent"] == "data" (routes to data agent)
```

**Functionality**:
- Evaluates current state and agent results
- Determines which agent should execute next
- Routes to data agent if not completed
- Routes to analysis agent if data agent completed
- Detects workflow completion when all agents finished
- Returns state updates with routing decisions

**Orchestration Logic**:
1. If workflow already completed → route to END
2. If data agent hasn't completed → route to data agent
3. If analysis agent hasn't completed → route to analysis agent
4. If all agents completed → mark workflow complete and route to END

**State Updates**:
- `current_agent`: Set to next agent ("data", "analysis", or "end")
- `completed`: Set to True when all agents completed

**Example Workflow Sequence**:
```python
# Step 1: Initial state - orchestrator routes to data agent
state = {
    "agent_results": {},
    "current_agent": "orchestrator",
    "completed": False
}
result = orchestrator_agent(state)
assert result["current_agent"] == "data"

# Step 2: After data agent - orchestrator routes to analysis agent
state["agent_results"] = {"data": {"agent": "data", "result": "data_processed"}}
state["current_agent"] = "orchestrator"
result = orchestrator_agent(state)
assert result["current_agent"] == "analysis"

# Step 3: After analysis agent - orchestrator detects completion
state["agent_results"] = {
    "data": {"agent": "data", "result": "data_processed"},
    "analysis": {"agent": "analysis", "result": "analysis_complete"}
}
state["current_agent"] = "orchestrator"
result = orchestrator_agent(state)
assert result["completed"] is True
assert result["current_agent"] == "end"
```

### route_to_agent

Routing function for conditional edges in LangGraph StateGraph. Reads the current_agent value set by the orchestrator and returns the appropriate node name.

```python
from langgraph_workflows.orchestrator_agent import route_to_agent

state: MultiAgentState = {
    "current_agent": "data",
    "completed": False
}

next_node = route_to_agent(state)
# Returns: "data"
```

**Functionality**:
- Reads `current_agent` from state (set by orchestrator)
- Returns node name for LangGraph conditional edges
- Handles completion and end states
- Defaults to orchestrator if not set

**Routing Logic**:
- If `current_agent == "end"` or `completed == True` → returns "end"
- Otherwise → returns `current_agent` value

**Usage with Conditional Edges**:
```python
from langgraph.graph import StateGraph, START, END
from langgraph_workflows.orchestrator_agent import orchestrator_agent, route_to_agent

workflow = StateGraph(MultiAgentState)

# Add orchestrator node
workflow.add_node("orchestrator", orchestrator_agent)

# Add conditional edge from orchestrator
workflow.add_conditional_edges(
    "orchestrator",
    route_to_agent,
    {
        "data": "data_agent",
        "analysis": "analysis_agent",
        "end": END
    }
)
```

### orchestrator_agent_with_errors

Enhanced version with comprehensive error handling that detects errors in agent results and handles exceptions gracefully.

```python
from langgraph_workflows.orchestrator_agent import orchestrator_agent_with_errors

# State with error in data agent result
state: MultiAgentState = {
    "agent_results": {
        "data": {
            "error": "Database connection timeout",
            "agent": "data",
            "result": "error"
        }
    },
    "current_agent": "orchestrator",
    "completed": False,
    "metadata": {}
}

result = orchestrator_agent_with_errors(state)
# result["completed"] == True
# result["current_agent"] == "end"
# result["metadata"]["error"] contains error information
```

**Error Handling**:
- Scans all agent results for error indicators
- Detects errors by checking for `"error"` key in agent results
- Marks workflow as complete with error status
- Includes error details in metadata
- Handles exceptions during orchestration gracefully

**Error Detection Logic**:
```python
for agent_name, result in agent_results.items():
    if isinstance(result, dict) and "error" in result:
        # Error detected - mark workflow complete with error
        return {
            "completed": True,
            "current_agent": "end",
            "metadata": {
                **state.get("metadata", {}),
                "error": f"Error in {agent_name} agent",
                "error_details": result.get("error", "Unknown error")
            }
        }
```

**Error Result Format**:
```python
{
    "completed": True,
    "current_agent": "end",
    "metadata": {
        "error": "Error in data agent",
        "error_details": "Database connection timeout"
    }
}
```

## Orchestrator-Worker Pattern

The orchestrator implements the orchestrator-worker collaboration pattern:

### Pattern Overview

```
┌─────────────┐
│ Orchestrator│
│   Agent     │
└──────┬──────┘
       │
       ├─── Routes to ───┐
       │                 │
       ▼                 ▼
┌──────────┐      ┌──────────┐
│   Data   │      │ Analysis │
│  Agent   │      │  Agent   │
└────┬─────┘      └────┬─────┘
     │                  │
     └────── Returns ───┘
              │
              ▼
       ┌─────────────┐
       │ Orchestrator│
       │   Agent     │
       └─────────────┘
```

### Workflow Sequence

1. **Orchestrator evaluates state** → Determines next agent
2. **Routes to worker agent** → Data agent or analysis agent
3. **Worker agent executes** → Processes task and updates state
4. **Worker returns to orchestrator** → Updates current_agent to "orchestrator"
5. **Orchestrator evaluates again** → Checks completion or routes to next agent
6. **Workflow completes** → When all agents finished

### State Flow

```python
# Initial state
state = {
    "agent_results": {},
    "current_agent": "orchestrator",
    "completed": False
}

# Orchestrator routes to data agent
orchestrator_result = orchestrator_agent(state)
state["current_agent"] = orchestrator_result["current_agent"]  # "data"

# Data agent executes
data_result = data_agent(state)
state.update(data_result)
# state["agent_results"]["data"] = {...}
# state["current_agent"] = "analysis"

# Orchestrator routes to analysis agent
state["current_agent"] = "orchestrator"
orchestrator_result = orchestrator_agent(state)
state["current_agent"] = orchestrator_result["current_agent"]  # "analysis"

# Analysis agent executes
analysis_result = analysis_agent(state)
state.update(analysis_result)
# state["agent_results"]["analysis"] = {...}
# state["current_agent"] = "orchestrator"

# Orchestrator detects completion
orchestrator_result = orchestrator_agent(state)
# orchestrator_result["completed"] = True
# orchestrator_result["current_agent"] = "end"
```

## Integration with StateGraph

The orchestrator is designed to work with LangGraph StateGraph for multi-agent workflows:

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph_workflows.state import MultiAgentState
from langgraph_workflows.agent_nodes import data_agent, analysis_agent
from langgraph_workflows.orchestrator_agent import orchestrator_agent, route_to_agent

# Create checkpointer
checkpointer = InMemorySaver()

# Build multi-agent graph
workflow = StateGraph(MultiAgentState)

# Add nodes
workflow.add_node("orchestrator", orchestrator_agent)
workflow.add_node("data_agent", data_agent)
workflow.add_node("analysis_agent", analysis_agent)

# Add edges: START -> orchestrator
workflow.add_edge(START, "orchestrator")

# Add conditional edge from orchestrator
workflow.add_conditional_edges(
    "orchestrator",
    route_to_agent,
    {
        "data": "data_agent",
        "analysis": "analysis_agent",
        "end": END
    }
)

# Add edges back to orchestrator
workflow.add_edge("data_agent", "orchestrator")
workflow.add_edge("analysis_agent", "orchestrator")

# Compile with checkpointing
multi_agent_graph = workflow.compile(checkpointer=checkpointer)
```

## Best Practices

### 1. Use Orchestrator for Coordination

Always use orchestrator to coordinate agent execution rather than direct agent-to-agent routing:

```python
# ✅ Correct - Orchestrator coordinates
orchestrator_result = orchestrator_agent(state)
state["current_agent"] = orchestrator_result["current_agent"]
# Then route based on orchestrator decision

# ❌ Incorrect - Direct routing
state["current_agent"] = "data"  # Skip orchestrator
```

### 2. Evaluate All Agent Results

Orchestrator should evaluate all agent results before making decisions:

```python
# ✅ Correct - Check all agents
if "data" not in agent_results:
    return {"current_agent": "data"}
if "analysis" not in agent_results:
    return {"current_agent": "analysis"}

# ❌ Incorrect - Incomplete evaluation
if not agent_results:
    return {"current_agent": "data"}  # Doesn't check analysis
```

### 3. Handle Completion Properly

Always check completion status before routing:

```python
# ✅ Correct - Check completion first
if completed:
    return {"current_agent": "end"}

# ❌ Incorrect - Skip completion check
return {"current_agent": "data"}  # May route even if completed
```

### 4. Use Error Handling Version

For production workflows, use error handling version:

```python
from langgraph_workflows.orchestrator_agent import orchestrator_agent_with_errors

# Use error handling version in production
result = orchestrator_agent_with_errors(state)
```

### 5. Preserve State Updates

Orchestrator should only return state updates (not full state):

```python
# ✅ Correct - State updates only
return {
    "current_agent": "data",
    "completed": True  # if applicable
}

# ❌ Incorrect - Full state
return {
    "messages": state["messages"],
    "task": state["task"],
    "agent_results": state["agent_results"],
    "current_agent": "data",
    "completed": state["completed"],
    "metadata": state["metadata"]
}
```

## Testing

All orchestrator functions are comprehensively tested with production conditions:

**Test Coverage**:
- Orchestrator agent functionality (6 tests)
- Routing function (6 tests)
- Error handling (6 tests)
- Integration with real agents (3 tests)

**Total**: 21 tests, all passing

**Run Tests**:
```bash
pytest tests/langgraph/test_orchestrator.py -v
```

**Test Philosophy**:
- ✅ Real LangGraph components (no mocks)
- ✅ Production-like test data (no placeholders)
- ✅ Actual state updates (not stubbed)
- ✅ Real agent nodes (not mocked)
- ✅ Complete workflow integration tests

## Usage Examples

### Basic Orchestration

```python
from langgraph_workflows.orchestrator_agent import orchestrator_agent
from langgraph_workflows.state import MultiAgentState

# Initial state
state: MultiAgentState = {
    "messages": [],
    "task": "Process and analyze customer transaction data",
    "agent_results": {},
    "current_agent": "orchestrator",
    "completed": False,
    "metadata": {}
}

# Orchestrator routes to data agent
result = orchestrator_agent(state)
print(f"Next agent: {result['current_agent']}")  # "data"
```

### Complete Workflow with Orchestrator

```python
from langgraph_workflows.orchestrator_agent import orchestrator_agent
from langgraph_workflows.agent_nodes import data_agent, analysis_agent
from langgraph_workflows.state import MultiAgentState

# Step 1: Orchestrator routes to data agent
state: MultiAgentState = {
    "messages": [],
    "task": "Process and analyze customer transaction data for Q4 2024 financial report",
    "agent_results": {},
    "current_agent": "orchestrator",
    "completed": False,
    "metadata": {}
}

orchestrator_result = orchestrator_agent(state)
state["current_agent"] = orchestrator_result["current_agent"]  # "data"

# Step 2: Execute data agent
data_result = data_agent(state)
state.update(data_result)

# Step 3: Orchestrator routes to analysis agent
state["current_agent"] = "orchestrator"
orchestrator_result = orchestrator_agent(state)
state["current_agent"] = orchestrator_result["current_agent"]  # "analysis"

# Step 4: Execute analysis agent
analysis_result = analysis_agent(state)
state.update(analysis_result)

# Step 5: Orchestrator detects completion
state["current_agent"] = "orchestrator"
orchestrator_result = orchestrator_agent(state)
print(f"Workflow completed: {orchestrator_result['completed']}")  # True
print(f"Final agent: {orchestrator_result['current_agent']}")  # "end"
```

### With Error Handling

```python
from langgraph_workflows.orchestrator_agent import orchestrator_agent_with_errors

# State with error in agent result
state: MultiAgentState = {
    "agent_results": {
        "data": {
            "error": "Database connection timeout",
            "agent": "data",
            "result": "error"
        }
    },
    "current_agent": "orchestrator",
    "completed": False,
    "metadata": {}
}

result = orchestrator_agent_with_errors(state)

if result.get("completed") and "error" in result.get("metadata", {}):
    print(f"Error detected: {result['metadata']['error']}")
    print(f"Error details: {result['metadata']['error_details']}")
```

## Related Documentation

- [LangGraph State Guide](./langgraph-state-guide.md) - MultiAgentState definition and reducers
- [LangGraph Agent Nodes Guide](./langgraph-agent-nodes-guide.md) - Specialized agent nodes (data_agent, analysis_agent)
- [LangGraph Conditional Routing Guide](./langgraph-conditional-routing-guide.md) - Conditional routing patterns
- [Task Documentation](../dev/tasks/TASK-022.md) - Orchestrator Agent Node Implementation

## Task Status

- ✅ TASK-022: Orchestrator Agent Node Implementation (Complete)
- ✅ TASK-023: Multi-Agent StateGraph Configuration (Complete)
- TASK-024: Multi-Agent Collaboration Testing (Next)

## Related Workflow Documentation

For complete multi-agent workflow implementation with StateGraph configuration, see:
- [LangGraph Multi-Agent Workflow Guide](./langgraph-multi-agent-workflow-guide.md) - Complete workflow with StateGraph, checkpointing, and execution patterns

