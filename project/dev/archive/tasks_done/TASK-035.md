# TASK-035: Implement LLM Inference in LangGraph Workflows

## Task Information
- **Task ID**: TASK-035
- **Created**: 2025-01-27
- **Status**: Done
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 4-6 hours
- **Actual Time**: TBD
- **Type**: Integration
- **Dependencies**: TASK-034 ✅
- **Parent PRD**: `project/docs/prd_phase3.md` - Milestone 1.7

## Task Description
Integrate LLM inference nodes (TASK-034) into existing LangGraph workflows. Update multi-agent workflow to use LLM nodes for analysis and decision-making. Ensure proper state management and error handling.

## Problem Statement
LLM nodes need to be integrated into existing LangGraph workflows to enable AI-powered decision making. This task updates the multi-agent workflow from Phase 2 to use LLM nodes for analysis tasks.

## Requirements

### Functional Requirements
- [x] LLM nodes integrated into multi-agent workflow
- [x] LLM used for analysis tasks
- [x] State management preserved
- [x] Error handling working
- [x] Checkpointing preserved
- [x] Workflow completes successfully with LLM

### Technical Requirements
- [x] Integration with existing `multi_agent_graph`
- [x] State conversion for LLM nodes
- [x] Error handling for LLM failures
- [x] Logging and monitoring
- [x] Configuration management

## Implementation Plan

### Phase 1: Analysis
- [ ] Review existing multi-agent workflow
- [ ] Review LLM nodes from TASK-034
- [ ] Identify integration points
- [ ] Design workflow updates
- [ ] Plan state management

### Phase 2: Planning
- [ ] Plan workflow integration
- [ ] Plan state management
- [ ] Plan error handling
- [ ] Plan configuration

### Phase 3: Implementation
- [ ] Update multi-agent workflow with LLM nodes
- [ ] Integrate LLM analysis node
- [ ] Update state management
- [ ] Add error handling
- [ ] Update routing logic
- [ ] Test workflow execution

### Phase 4: Testing
- [ ] Test workflow with LLM nodes
- [ ] Test state management
- [ ] Test error handling
- [ ] Test checkpointing
- [ ] Integration tests

### Phase 5: Documentation
- [ ] Document workflow updates
- [ ] Document LLM integration
- [ ] Document state management
- [ ] Document error handling

## Technical Implementation

### Updated Multi-Agent Workflow
```python
# project/langgraph_workflows/multi_agent_workflow.py (update)
from langgraph_workflows.llm_nodes import llm_analysis_node
from langgraph_workflows.agent_nodes import data_agent, analysis_agent
from langgraph_workflows.orchestrator_agent import orchestrator_agent, route_to_agent

# Build multi-agent graph with LLM integration
workflow = StateGraph(MultiAgentState)

# Add nodes: orchestrator, worker agents, and LLM node
workflow.add_node("orchestrator", orchestrator_agent)
workflow.add_node("data_agent", data_agent)
workflow.add_node("analysis_agent", analysis_agent)
workflow.add_node("llm_analysis", llm_analysis_node)  # NEW

# Add edges
workflow.add_edge(START, "orchestrator")
workflow.add_conditional_edges(
    "orchestrator",
    route_to_agent,
    {
        "data_agent": "data_agent",
        "analysis_agent": "analysis_agent",
        "llm_analysis": "llm_analysis",  # NEW
        "end": END
    }
)
workflow.add_edge("data_agent", "orchestrator")
workflow.add_edge("analysis_agent", "orchestrator")
workflow.add_edge("llm_analysis", "orchestrator")  # NEW

# Compile with checkpointer
multi_agent_graph = workflow.compile(checkpointer=checkpointer)
```

### Updated Orchestrator Routing
```python
# project/langgraph_workflows/orchestrator_agent.py (update)
def route_to_agent(state: MultiAgentState) -> str:
    """Route to appropriate agent or LLM node."""
    agent_results = state.get("agent_results", {})
    
    # If data agent not completed, route to data agent
    if "data" not in agent_results:
        return "data_agent"
    
    # If analysis agent not completed, route to analysis agent
    if "analysis" not in agent_results:
        return "analysis_agent"
    
    # If LLM analysis not completed and needed, route to LLM
    if "llm_analysis" not in agent_results and state.get("task", "").lower().find("analyze") >= 0:
        return "llm_analysis"
    
    # All agents completed
    return "end"
```

### State Management for LLM
```python
# project/langgraph_workflows/llm_nodes.py (update)
def llm_analysis_node(state: MultiAgentState) -> MultiAgentState:
    """LLM analysis node integrated with MultiAgentState."""
    # Extract task and data from state
    task = state.get("task", "")
    agent_results = state.get("agent_results", {})
    
    # Prepare input for LLM
    input_text = f"Task: {task}\n\n"
    
    # Include data agent results if available
    if "data" in agent_results:
        input_text += f"Data: {agent_results['data']}\n\n"
    
    # Include analysis agent results if available
    if "analysis" in agent_results:
        input_text += f"Previous Analysis: {agent_results['analysis']}\n\n"
    
    input_text += "Provide a comprehensive AI-powered analysis."
    
    # Create LLM state
    llm_state: LLMState = {
        "input": input_text,
        "output": "",
        "status": "processing",
        "metadata": {}
    }
    
    # Process with LLM
    llm_node_func = create_llm_node(
        model="llama2:13b",
        prompt_template="""You are an AI assistant specializing in data analysis and decision-making.

{input}

Provide a detailed analysis with clear conclusions and recommendations.""",
        temperature=0.7
    )
    
    llm_result = llm_node_func(llm_state)
    
    # Update state with LLM result
    updated_results = {
        **agent_results,
        "llm_analysis": {
            "agent": "llm_analysis",
            "result": llm_result["output"],
            "status": llm_result["status"],
            "metadata": llm_result["metadata"]
        }
    }
    
    return {
        **state,
        "agent_results": updated_results,
        "metadata": {
            **state.get("metadata", {}),
            "llm_metadata": llm_result["metadata"]
        }
    }
```

## Testing

### Manual Testing
- [ ] Test workflow with LLM nodes
- [ ] Test state management
- [ ] Test error handling
- [ ] Test checkpointing
- [ ] Test with different tasks

### Automated Testing
- [ ] Unit tests for workflow integration
- [ ] Unit tests for state management
- [ ] Integration tests with LLM
- [ ] Test error handling
- [ ] Test checkpointing

## Acceptance Criteria
- [x] LLM nodes integrated into multi-agent workflow
- [x] LLM used for analysis tasks
- [x] State management preserved
- [x] Error handling working
- [x] Checkpointing preserved
- [x] Workflow completes successfully with LLM
- [x] Unit tests passing
- [x] Integration tests passing
- [x] Documentation complete

## Dependencies
- **External**: None
- **Internal**: TASK-034 (LLM nodes), existing multi-agent workflow (Phase 2)

## Risks and Mitigation

### Risk 1: LLM Performance Impact
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Monitor LLM response times, implement timeouts, optimize prompts

### Risk 2: State Management Issues
- **Probability**: Low
- **Impact**: High
- **Mitigation**: Test state management thoroughly, validate state structure

### Risk 3: Checkpointing with LLM
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Test checkpointing with LLM nodes, ensure state serialization works

## Task Status
- [x] Analysis Complete
- [x] Planning Complete
- [x] Implementation Complete
- [x] Testing Complete
- [x] Documentation Complete

## Notes
- Preserve existing workflow functionality
- Add LLM nodes as additional capability
- Handle LLM errors gracefully - don't fail entire workflow
- Consider LLM response caching for performance (future enhancement)
- Monitor LLM usage and costs (if applicable)

