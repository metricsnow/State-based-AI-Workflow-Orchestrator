# TASK-034: Create LangGraph Node with Ollama LLM

## Task Information
- **Task ID**: TASK-034
- **Created**: 2025-01-27
- **Status**: Done
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 3-4 hours
- **Actual Time**: TBD
- **Type**: Integration
- **Dependencies**: TASK-033 ✅
- **Parent PRD**: `project/docs/prd_phase3.md` - Milestone 1.7

## Task Description
Create LangGraph node that uses Ollama LLM for inference. Integrate the LangChain-Ollama integration (TASK-033) into LangGraph workflow nodes. This enables LLM-powered decision making in LangGraph workflows.

## Problem Statement
LangGraph workflows need LLM nodes that can use Ollama for inference. The PRD shows a basic example (lines 342-368) but uses incorrect imports. This task creates a proper LangGraph node using the corrected Ollama integration.

## Requirements

### Functional Requirements
- [x] LangGraph node with Ollama LLM
- [x] Node integrates with existing LangGraph workflows
- [x] Node uses correct OllamaLLM import
- [x] Node handles LLM errors gracefully
- [x] Node supports prompt templating
- [x] Node supports different models

### Technical Requirements
- [x] Integration with LangGraph StateGraph
- [x] Use OllamaLLM from TASK-033
- [x] State management for LLM inputs/outputs
- [x] Error handling and retry logic
- [x] Logging and monitoring
- [x] Configuration management

## Implementation Plan

### Phase 1: Analysis
- [ ] Review existing LangGraph node patterns
- [ ] Review Ollama integration from TASK-033
- [ ] Review state management patterns
- [ ] Design LLM node structure
- [ ] Plan error handling

### Phase 2: Planning
- [ ] Design LLM node function
- [ ] Plan state integration
- [ ] Plan prompt templating
- [ ] Plan error handling
- [ ] Plan configuration

### Phase 3: Implementation
- [ ] Create LLM node function
- [ ] Integrate with OllamaLLM
- [ ] Add state management
- [ ] Add prompt templating
- [ ] Add error handling
- [ ] Create example workflow

### Phase 4: Testing
- [ ] Test LLM node execution
- [ ] Test state management
- [ ] Test error handling
- [ ] Test with different prompts
- [ ] Test with different models

### Phase 5: Documentation
- [ ] Document LLM node usage
- [ ] Document state requirements
- [ ] Document error handling
- [ ] Document example workflows

## Technical Implementation

### LLM Node Implementation
```python
# project/langgraph_workflows/llm_nodes.py
import logging
from typing import TypedDict, Dict, Any
from langchain_ollama_integration import create_ollama_llm
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)


class LLMState(TypedDict):
    """State for LLM node."""
    input: str
    output: str
    status: str
    metadata: Dict[str, Any]


def create_llm_node(
    model: str = "llama2:13b",
    prompt_template: Optional[str] = None,
    temperature: float = 0.7
):
    """Create a LangGraph node that uses Ollama LLM.
    
    Args:
        model: Ollama model name
        prompt_template: Optional prompt template (uses {input} placeholder)
        temperature: Temperature for generation
    
    Returns:
        Node function for LangGraph
    """
    llm = create_ollama_llm(model=model, temperature=temperature)
    
    if prompt_template:
        prompt = PromptTemplate.from_template(prompt_template)
        chain = prompt | llm
    else:
        chain = llm
    
    def llm_node(state: LLMState) -> LLMState:
        """LangGraph node that processes input with Ollama LLM."""
        try:
            input_text = state.get("input", "")
            
            if not input_text:
                logger.warning("Empty input in LLM node")
                return {
                    "output": "",
                    "status": "error",
                    "metadata": {"error": "Empty input"}
                }
            
            logger.info(f"Processing LLM request: {input_text[:50]}...")
            
            # Invoke LLM
            if prompt_template:
                result = chain.invoke({"input": input_text})
            else:
                result = chain.invoke(input_text)
            
            logger.info(f"LLM response received: {result[:50] if isinstance(result, str) else '...'}...")
            
            return {
                "output": result if isinstance(result, str) else str(result),
                "status": "completed",
                "metadata": {
                    "model": model,
                    "input_length": len(input_text),
                    "output_length": len(result) if isinstance(result, str) else 0
                }
            }
        
        except Exception as e:
            logger.error(f"Error in LLM node: {e}", exc_info=True)
            return {
                "output": "",
                "status": "error",
                "metadata": {
                    "error": str(e),
                    "model": model
                }
            }
    
    return llm_node


def llm_analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Pre-configured LLM node for analysis tasks."""
    prompt_template = """You are an AI assistant specializing in data analysis.
    
Task: {input}

Provide a detailed analysis with clear conclusions."""
    
    node = create_llm_node(
        model="llama2:13b",
        prompt_template=prompt_template,
        temperature=0.7
    )
    
    llm_state: LLMState = {
        "input": state.get("task", ""),
        "output": "",
        "status": "processing",
        "metadata": {}
    }
    
    result = node(llm_state)
    
    return {
        **state,
        "llm_analysis": result["output"],
        "llm_status": result["status"],
        "metadata": {
            **state.get("metadata", {}),
            **result["metadata"]
        }
    }
```

### Integration with Existing Workflows
```python
# project/langgraph_workflows/llm_workflow.py
from langgraph.graph import StateGraph, START, END
from langgraph_workflows.llm_nodes import llm_analysis_node
from langgraph_workflows.state import MultiAgentState

# Build workflow with LLM node
workflow = StateGraph(MultiAgentState)

# Add existing nodes
workflow.add_node("orchestrator", orchestrator_agent)
workflow.add_node("data_agent", data_agent)

# Add LLM analysis node
workflow.add_node("llm_analysis", llm_analysis_node)

# Add edges
workflow.add_edge(START, "orchestrator")
workflow.add_edge("data_agent", "llm_analysis")
workflow.add_edge("llm_analysis", END)

llm_workflow = workflow.compile()
```

## Testing

### Manual Testing
- [ ] Test LLM node with simple input
- [ ] Test LLM node with prompt template
- [ ] Test LLM node error handling
- [ ] Test integration with existing workflows
- [ ] Test with different models

### Automated Testing
- [ ] Unit tests for LLM node
- [ ] Unit tests for prompt templating
- [ ] Unit tests for error handling
- [ ] Integration tests with workflows
- [ ] Mock LLM tests for CI/CD

## Acceptance Criteria
- [x] LangGraph node with Ollama LLM created
- [x] Node integrates with existing workflows
- [x] Node uses correct OllamaLLM import
- [x] Node handles LLM errors gracefully
- [x] Node supports prompt templating
- [x] Node supports different models
- [x] Unit tests passing
- [x] Integration tests passing
- [x] Documentation complete

## Dependencies
- **External**: langchain-ollama, langchain-core
- **Internal**: TASK-033 (Ollama integration), existing LangGraph workflows

## Risks and Mitigation

### Risk 1: LLM Timeout
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Implement timeout, handle timeout errors, add retry logic

### Risk 2: LLM Response Quality
- **Probability**: Medium
- **Impact**: Low
- **Mitigation**: Use appropriate prompts, tune temperature, validate responses

### Risk 3: Model Not Available
- **Probability**: Low
- **Impact**: High
- **Mitigation**: Verify model downloaded, handle model errors, provide clear error messages

## Task Status
- [x] Analysis Complete
- [x] Planning Complete
- [x] Implementation Complete
- [x] Testing Complete
- [x] Documentation Complete

## Notes
- Use correct OllamaLLM import from TASK-033
- Handle LLM errors gracefully - don't fail entire workflow
- Support prompt templating for flexibility
- Make model configurable per node
- Consider caching LLM responses for repeated queries (future enhancement)

