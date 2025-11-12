# Product Requirements Document: Phase 2 - AI Workflow Foundation

**Project**: AI-Powered Workflow Orchestration for Trading Operations  
**Phase**: Phase 2 - AI Workflow Foundation  
**Version**: 1.0  
**Date**: 2025-01-27  
**Author**: Mission Planner Agent  
**Status**: Draft  
**Parent PRD**: `project/docs/prd.md`

---

## Document Control

- **Phase Name**: AI Workflow Foundation
- **Phase Number**: 2
- **Version**: 1.0
- **Author**: Mission Planner Agent
- **Last Updated**: 2025-01-27
- **Status**: Draft
- **Dependencies**: Phase 1 (Foundation & Core Orchestration)
- **Duration Estimate**: 2-3 weeks
- **Team Size**: 1-2 developers

---

## Executive Summary

### Phase Vision
Establish the AI workflow foundation using LangGraph for stateful agent workflows and multi-agent systems. This phase creates the core AI orchestration capabilities that will integrate with the traditional orchestration layer in Phase 3.

### Key Objectives
1. **LangGraph Stateful Workflows**: Implement stateful agent workflows with checkpointing
2. **Multi-Agent Systems**: Create collaborative multi-agent workflows
3. **State Management**: Implement robust state management patterns
4. **Checkpointing**: Configure persistence for workflow state

### Success Metrics
- **Stateful Workflows**: LangGraph workflows execute with state persistence
- **Multi-Agent Collaboration**: 2-3 agents collaborate successfully on tasks
- **Checkpointing**: Workflow state persists across executions
- **Conditional Routing**: Dynamic routing based on state conditions

---

## Phase Overview

### Scope
This phase establishes the AI workflow infrastructure:
- LangGraph stateful workflow implementation
- Multi-agent system architecture
- State management and checkpointing
- Conditional routing patterns

### Out of Scope
- Integration with Airflow (Phase 3)
- Local LLM deployment (Phase 3)
- Production deployment (Phase 4)
- Advanced LangGraph features (Phase 6)

### Phase Dependencies
- **Prerequisites**: Phase 1 completed (Kafka events available)
- **External Dependencies**: LangGraph, LangChain
- **Internal Dependencies**: Event schema from Phase 1

---

## Technical Architecture

### Phase 2 Architecture

```
┌─────────────────────────────────────┐
│      LangGraph Workflow Engine     │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────────────────────┐  │
│  │     StateGraph Builder       │  │
│  │  - State Definition          │  │
│  │  - Node Registration        │  │
│  │  - Edge Configuration       │  │
│  └──────────────┬───────────────┘  │
│                 │                   │
│  ┌──────────────▼───────────────┐  │
│  │   Compiled Graph            │  │
│  │  - Checkpointing            │  │
│  │  - State Persistence        │  │
│  └──────────────┬───────────────┘  │
│                 │                   │
│  ┌──────────────▼───────────────┐  │
│  │   Agent Nodes                │  │
│  │  - Agent 1 (Specialized)    │  │
│  │  - Agent 2 (Specialized)    │  │
│  │  - Agent 3 (Orchestrator)   │  │
│  └──────────────┬───────────────┘  │
│                 │                   │
│  ┌──────────────▼───────────────┐  │
│  │   Checkpoint Store           │  │
│  │  - InMemorySaver (dev)      │  │
│  │  - Redis (future)            │  │
│  └──────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

### Technology Stack

#### AI Orchestration Layer
- **LangGraph** (Trust Score: 9.2)
  - Version: 0.6.0+ (latest stable)
  - Components: StateGraph, Checkpointing, Multi-Agent
  - State Management: TypedDict with reducers

#### LLM Integration
- **LangChain** (Trust Score: 7.5)
  - Version: 0.2.0+ (compatible with LangGraph)
  - Components: LLM integration, Tool integration
  - Model Support: OpenAI, Ollama (Phase 3), vLLM (Phase 5)

### State Management Pattern

**State Definition**:
```python
from typing import Annotated, TypedDict
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class WorkflowState(TypedDict):
    messages: Annotated[list, add_messages]
    task_data: dict
    agent_results: dict
    workflow_status: str
    metadata: dict
```

**State Reducers**:
- `add_messages`: For message history
- `operator.add`: For numeric aggregations
- Custom reducers for complex state updates

---

## Detailed Milestones

### Milestone 1.4: LangGraph Stateful Workflow

**Objective**: Create basic LangGraph stateful agent workflow with checkpointing

#### Requirements
- Create StateGraph with basic state management
- Implement conditional routing
- Configure checkpointing for state persistence
- Execute workflow successfully

#### Technical Specifications

**StateGraph Creation**:
```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
    data: dict
    status: str

def node_a(state: State):
    return {"messages": [{"role": "user", "content": "Processing..."}], "status": "processing"}

def node_b(state: State):
    return {"status": "completed", "data": {"result": "success"}}

def should_continue(state: State) -> str:
    if state.get("status") == "processing":
        return "node_b"
    return "end"

# Build graph
workflow = StateGraph(State)
workflow.add_node("node_a", node_a)
workflow.add_node("node_b", node_b)
workflow.add_edge(START, "node_a")
workflow.add_conditional_edges("node_a", should_continue, {"node_b": "node_b", "end": END})
workflow.add_edge("node_b", END)

# Compile with checkpointing
checkpointer = InMemorySaver()
graph = workflow.compile(checkpointer=checkpointer)
```

**Checkpointing Configuration**:
- **Development**: InMemorySaver (in-memory persistence)
- **Production**: Redis or PostgreSQL checkpointers (Phase 4)
- **Thread ID**: Unique identifier for workflow instances

#### Acceptance Criteria
- [ ] StateGraph created with TypedDict state definition
- [ ] At least 2 nodes implemented with state updates
- [ ] Conditional routing implemented and working
- [ ] Checkpointing configured (InMemorySaver)
- [ ] Workflow executes successfully
- [ ] State persists across workflow steps
- [ ] Workflow can be resumed from checkpoint
- [ ] State updates use proper reducers

#### Testing Requirements
- **Unit Tests**:
  - Test state definition and reducers
  - Test node functions independently
  - Test conditional routing logic
  - Test checkpoint save/load

- **Integration Tests**:
  - Test complete workflow execution
  - Test state persistence across steps
  - Test workflow resumption from checkpoint
  - Test error handling and recovery

#### Dependencies
- Python 3.11+
- Python virtual environment (venv) - always use venv for local development
- LangGraph installed (with venv activated: `pip install langgraph`)
- LangChain installed (with venv activated: `pip install langchain`)

#### Risks and Mitigation
- **Risk**: State management complexity
  - **Mitigation**: Start with simple state, use official examples, incrementally add complexity
- **Risk**: Checkpointing performance
  - **Mitigation**: Use InMemorySaver for development, optimize for production later

---

### Milestone 1.5: LangGraph Multi-Agent System

**Objective**: Implement basic LangGraph multi-agent collaboration

#### Requirements
- Create 2-3 specialized agents as LangGraph nodes
- Configure StateGraph with multiple agent nodes
- Implement agent collaboration on tasks
- Implement conditional routing between agents
- Manage state for multi-agent coordination

#### Technical Specifications

**Multi-Agent Architecture**:
```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class MultiAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    task: str
    agent_results: dict
    current_agent: str
    completed: bool

def data_agent(state: MultiAgentState):
    """Specialized agent for data processing"""
    # Process data
    result = {"agent": "data", "result": "data_processed"}
    return {
        "agent_results": {**state.get("agent_results", {}), "data": result},
        "current_agent": "analysis"
    }

def analysis_agent(state: MultiAgentState):
    """Specialized agent for analysis"""
    # Analyze data
    result = {"agent": "analysis", "result": "analysis_complete"}
    return {
        "agent_results": {**state.get("agent_results", {}), "analysis": result},
        "current_agent": "orchestrator"
    }

def orchestrator_agent(state: MultiAgentState):
    """Orchestrator agent coordinates workflow"""
    results = state.get("agent_results", {})
    if "data" in results and "analysis" in results:
        return {"completed": True, "current_agent": "end"}
    return {"current_agent": "data"}

def route_to_agent(state: MultiAgentState) -> str:
    """Route to appropriate agent based on state"""
    current = state.get("current_agent", "data")
    if current == "end" or state.get("completed"):
        return "end"
    return current

# Build multi-agent graph
workflow = StateGraph(MultiAgentState)
workflow.add_node("data_agent", data_agent)
workflow.add_node("analysis_agent", analysis_agent)
workflow.add_node("orchestrator", orchestrator_agent)

workflow.add_edge(START, "orchestrator")
workflow.add_conditional_edges(
    "orchestrator",
    route_to_agent,
    {
        "data": "data_agent",
        "analysis": "analysis_agent",
        "end": END
    }
)
workflow.add_edge("data_agent", "orchestrator")
workflow.add_edge("analysis_agent", "orchestrator")

# Compile with checkpointing
checkpointer = InMemorySaver()
graph = workflow.compile(checkpointer=checkpointer)
```

**Agent Collaboration Patterns**:
- **Sequential**: Agents execute in sequence
- **Parallel**: Agents execute concurrently (future enhancement)
- **Orchestrator-Worker**: Central orchestrator delegates to workers
- **Supervisor**: Supervisor coordinates specialized agents

#### Acceptance Criteria
- [ ] 2-3 specialized agents created as LangGraph nodes
- [ ] StateGraph configured with multiple agent nodes
- [ ] Agents collaborate successfully on task
- [ ] Conditional routing between agents implemented
- [ ] State management for multi-agent coordination working
- [ ] Agent results aggregated in state
- [ ] Workflow completes successfully with all agents
- [ ] Checkpointing works for multi-agent workflows

#### Testing Requirements
- **Unit Tests**:
  - Test individual agent functions
  - Test state updates from each agent
  - Test routing logic
  - Test state aggregation

- **Integration Tests**:
  - Test complete multi-agent workflow
  - Test agent collaboration
  - Test state persistence across agents
  - Test error handling in multi-agent context

#### Dependencies
- Milestone 1.4 completed (LangGraph stateful workflow)
- Understanding of multi-agent patterns

#### Risks and Mitigation
- **Risk**: Agent coordination complexity
  - **Mitigation**: Start with simple orchestrator pattern, use clear state management
- **Risk**: State conflicts between agents
  - **Mitigation**: Use proper reducers, namespace agent results, implement idempotent updates

---

## Integration Points

### LangGraph → Kafka (Future Phase 3)

**Pattern**: LangGraph workflow consumes Kafka events, publishes results

**Preparation** (Phase 2):
- Design event consumption pattern
- Plan state initialization from events
- Design result publishing pattern

---

## Security Requirements (CRITICAL)

### Credential Management - MANDATORY

**ALL credentials MUST be stored in `.env` file. This is a MANDATORY security requirement.**

#### Requirements
- **ALL API keys, database credentials, secret keys, tokens, and passwords MUST be in `.env` file only**
- **NEVER hardcode credentials in source code**
- **NEVER commit `.env` file to version control** (already in `.gitignore`)
- **Always use environment variables loaded from `.env` file**
- **Create `.env.example` file with placeholder values as template**
- **Document all required environment variables in documentation**

#### Credential Types That Must Be in `.env`:
- LangGraph checkpoint store credentials
- LLM API keys (OpenAI, Anthropic, etc.)
- Ollama configuration
- Database passwords (if any)
- Any other sensitive configuration

#### Implementation Pattern:
```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access credentials from environment
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')
```

#### Validation:
- Code review must verify no hardcoded credentials
- All credential access must use `os.getenv()` or similar
- `.env.example` must list all required variables
- Documentation must specify all required environment variables

## Development Environment

### Python Dependencies

```txt
langgraph>=0.6.0
langchain>=0.2.0
langchain-core>=0.2.0
pydantic>=2.0.0
typing-extensions>=4.8.0
```

### Development Setup

**Always use venv for local development:**

```bash
# Create virtual environment (if not already created)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Verify activation (should show venv path)
which python  # macOS/Linux
# OR
where python  # Windows

# Install dependencies
pip install langgraph langchain langchain-core pydantic typing-extensions

# Install development dependencies
pip install pytest pytest-asyncio black mypy
```

**Note**: Always activate venv before running any Python commands, installing packages, or running scripts.

---

## Testing Strategy

### Unit Testing
- **State Tests**: Validate state definitions and reducers
- **Node Tests**: Test agent functions independently
- **Routing Tests**: Test conditional routing logic
- **Checkpoint Tests**: Test checkpoint save/load

### Integration Testing
- **Workflow Tests**: Test complete workflow execution
- **Multi-Agent Tests**: Test agent collaboration
- **State Persistence Tests**: Test checkpointing across executions
- **Error Recovery Tests**: Test workflow recovery from failures

### Test Framework
- **pytest**: Primary testing framework
- **pytest-asyncio**: For async workflow testing
- **Mocking**: Mock LLM calls for testing

---

## Success Criteria

### Phase 2 Completion Criteria
- [ ] Both milestones completed and validated
- [ ] Stateful workflow executes with checkpointing
- [ ] Multi-agent system with 2-3 agents working
- [ ] Conditional routing implemented
- [ ] State management patterns documented
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] Documentation complete

### Quality Gates
- **Code Quality**: PEP8 compliance, type hints, docstrings
- **Test Coverage**: >80% for new code
- **Documentation**: All components documented
- **State Management**: Proper use of reducers and state updates

---

## Risk Assessment

### Technical Risks

**Risk 1: LangGraph Learning Curve**
- **Probability**: High
- **Impact**: Medium
- **Mitigation**: Use official documentation, start with simple examples, reference MCP Context7
- **Contingency**: Extend timeline, simplify initial implementation

**Risk 2: State Management Complexity**
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: Use TypedDict, proper reducers, start simple
- **Contingency**: Simplify state structure, use flat state initially

**Risk 3: Multi-Agent Coordination**
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Use proven patterns (orchestrator-worker), clear state management
- **Contingency**: Start with sequential agents, add parallelism later

### Operational Risks

**Risk 4: Checkpoint Storage Scalability**
- **Probability**: Low (Phase 2)
- **Impact**: Medium (Future)
- **Mitigation**: Use InMemorySaver for development, plan Redis/PostgreSQL for production
- **Contingency**: Optimize checkpoint size, implement cleanup strategies

---

## Dependencies and Prerequisites

### System Requirements
- **Python**: 3.11+
- **RAM**: 4GB+ (for LangGraph and checkpoints)
- **Disk Space**: 1GB+ (for dependencies and checkpoints)

### Software Dependencies
- LangGraph 0.6.0+
- LangChain 0.2.0+
- Python typing extensions

### External Dependencies
- None (standalone AI workflows, no LLM calls yet)

---

## Timeline and Effort Estimation

### Milestone Estimates
- **Milestone 1.4**: 4-6 days
- **Milestone 1.5**: 5-7 days

### Total Phase Estimate
- **Duration**: 2-3 weeks
- **Effort**: 50-70 hours
- **Team**: 1-2 developers

### Critical Path
1. Milestone 1.4 (Stateful Workflow) - Foundation
2. Milestone 1.5 (Multi-Agent) - Depends on 1.4

---

## Deliverables

### Code Deliverables
- [ ] LangGraph stateful workflow implementations
- [ ] Multi-agent system implementations
- [ ] State management patterns
- [ ] Checkpointing configuration
- [ ] Unit and integration tests

### Documentation Deliverables
- [ ] Phase 2 PRD (this document)
- [ ] LangGraph workflow development guide
- [ ] Multi-agent patterns documentation
- [ ] State management best practices
- [ ] Checkpointing guide

### Configuration Deliverables
- [ ] Python dependencies file (`requirements.txt`)
- [ ] State schema definitions
- [ ] Checkpoint configuration examples

---

## Next Phase Preview

**Phase 3: Integration & Local LLM** will build upon Phase 2 by:
- Integrating Airflow tasks with LangGraph workflows via Kafka
- Setting up local LLM deployment (Ollama)
- Creating end-to-end workflow from Airflow → Kafka → LangGraph
- Implementing event-driven coordination

**Prerequisites for Phase 3**:
- Phase 1 completed (Kafka events)
- Phase 2 completed (LangGraph workflows)
- Understanding of event-driven patterns

---

## Appendix

### A. LangGraph State Patterns

**Simple State**:
```python
class SimpleState(TypedDict):
    value: int
    status: str
```

**Message State**:
```python
class MessageState(TypedDict):
    messages: Annotated[list, add_messages]
```

**Complex State**:
```python
class ComplexState(TypedDict):
    messages: Annotated[list, add_messages]
    data: dict
    metadata: dict
    status: str
```

### B. Multi-Agent Patterns

**Orchestrator-Worker**:
- Central orchestrator delegates tasks to specialized workers
- Workers return results to orchestrator
- Orchestrator coordinates workflow completion

**Supervisor Pattern**:
- Supervisor monitors and coordinates agents
- Agents report status to supervisor
- Supervisor makes routing decisions

**Sequential Collaboration**:
- Agents execute in sequence
- Each agent processes output from previous
- Final agent produces workflow result

---

**PRD Phase 2 Version**: 1.0  
**Last Updated**: 2025-01-27  
**Next Review**: Upon Phase 2 completion

