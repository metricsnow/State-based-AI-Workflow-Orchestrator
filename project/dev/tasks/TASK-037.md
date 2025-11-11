# TASK-037: LLM Integration Testing

## Task Information
- **Task ID**: TASK-037
- **Created**: 2025-01-27
- **Status**: Waiting
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 4-6 hours
- **Actual Time**: TBD
- **Type**: Testing
- **Dependencies**: TASK-033 ✅, TASK-034 ✅, TASK-035 ✅, TASK-036 ✅
- **Parent PRD**: `project/docs/prd_phase3.md` - Milestone 1.7

## Task Description
Create comprehensive tests for LLM integration in LangGraph workflows. Test Ollama LLM initialization, inference, error handling, and integration with workflows. Validate all acceptance criteria for Milestone 1.7.

## Problem Statement
Comprehensive testing is required to validate that LLM integration works correctly in LangGraph workflows. This ensures the integration meets all acceptance criteria for Milestone 1.7 and is ready for production use.

## Requirements

### Functional Requirements
- [ ] Test Ollama LLM initialization
- [ ] Test basic inference
- [ ] Test LLM node execution
- [ ] Test LLM integration in workflows
- [ ] Test error handling
- [ ] Test model validation
- [ ] Test with different models
- [ ] Test with different prompts

### Technical Requirements
- [ ] Unit tests for LLM integration
- [ ] Integration tests with workflows
- [ ] Mock LLM tests for CI/CD
- [ ] Test error scenarios
- [ ] Test coverage >80%
- [ ] Test documentation

## Implementation Plan

### Phase 1: Analysis
- [ ] Review Milestone 1.7 acceptance criteria
- [ ] Identify test scenarios
- [ ] Plan test structure
- [ ] Design test fixtures
- [ ] Plan mock strategies

### Phase 2: Planning
- [ ] Design test suite structure
- [ ] Plan unit tests
- [ ] Plan integration tests
- [ ] Plan mock strategies
- [ ] Plan test data

### Phase 3: Implementation
- [ ] Create test module
- [ ] Implement unit tests
- [ ] Implement integration tests
- [ ] Implement mock tests
- [ ] Implement error scenario tests

### Phase 4: Testing
- [ ] Run all tests
- [ ] Verify test coverage
- [ ] Validate acceptance criteria
- [ ] Fix any test failures

### Phase 5: Documentation
- [ ] Document test scenarios
- [ ] Document test execution
- [ ] Document acceptance criteria validation

## Technical Implementation

### Test Structure
```python
# project/tests/langgraph/test_llm_integration.py
import pytest
import uuid
from unittest.mock import patch, MagicMock

from langchain_ollama_integration import create_ollama_llm
from langgraph_workflows.llm_nodes import create_llm_node, llm_analysis_node
from langgraph_workflows.multi_agent_workflow import multi_agent_graph
from langgraph_workflows.state import MultiAgentState


class TestOllamaLLMIntegration:
    """Tests for Ollama LLM integration."""
    
    def test_ollama_llm_initialization(self):
        """Test Ollama LLM initialization."""
        llm = create_ollama_llm(model="llama2:13b")
        assert llm is not None
        assert hasattr(llm, "invoke")
    
    def test_ollama_basic_inference(self):
        """Test basic inference with Ollama."""
        llm = create_ollama_llm(model="llama2:13b")
        result = llm.invoke("Say 'Hello, World!'")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
    
    @patch('langchain_ollama_integration.llm_factory.create_ollama_llm')
    def test_ollama_llm_mock(self, mock_llm):
        """Test with mocked LLM for CI/CD."""
        mock_llm.return_value.invoke.return_value = "Mocked response"
        llm = create_ollama_llm(model="llama2:13b")
        result = llm.invoke("Test")
        assert result == "Mocked response"


class TestLLMNode:
    """Tests for LLM node in LangGraph."""
    
    def test_llm_node_creation(self):
        """Test LLM node creation."""
        node = create_llm_node(model="llama2:13b")
        assert node is not None
        assert callable(node)
    
    def test_llm_node_execution(self):
        """Test LLM node execution."""
        node = create_llm_node(model="llama2:13b")
        state = {
            "input": "Test input",
            "output": "",
            "status": "processing",
            "metadata": {}
        }
        result = node(state)
        assert result["status"] in ["completed", "error"]
        assert "output" in result
    
    def test_llm_node_error_handling(self):
        """Test LLM node error handling."""
        with patch('langchain_ollama_integration.llm_factory.create_ollama_llm') as mock_llm:
            mock_llm.side_effect = Exception("LLM error")
            node = create_llm_node(model="llama2:13b")
            state = {
                "input": "Test input",
                "output": "",
                "status": "processing",
                "metadata": {}
            }
            result = node(state)
            assert result["status"] == "error"
            assert "error" in result["metadata"]


class TestLLMWorkflowIntegration:
    """Tests for LLM integration in workflows."""
    
    def test_workflow_with_llm_node(self):
        """Test workflow execution with LLM node."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        initial_state: MultiAgentState = {
            "messages": [],
            "task": "Analyze this data: [1, 2, 3, 4, 5]",
            "agent_results": {},
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {}
        }
        
        result = multi_agent_graph.invoke(initial_state, config=config)
        
        assert result is not None
        assert "agent_results" in result
    
    def test_llm_analysis_in_workflow(self):
        """Test LLM analysis in multi-agent workflow."""
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        initial_state: MultiAgentState = {
            "messages": [],
            "task": "Perform AI analysis of trading data",
            "agent_results": {
                "data": {"agent": "data", "result": "Data processed"}
            },
            "current_agent": "orchestrator",
            "completed": False,
            "metadata": {}
        }
        
        result = multi_agent_graph.invoke(initial_state, config=config)
        
        # Verify LLM analysis may be included
        assert result is not None
        assert "agent_results" in result


class TestLLMErrorHandling:
    """Tests for LLM error handling."""
    
    def test_llm_timeout_handling(self):
        """Test LLM timeout handling."""
        # Test timeout scenario
        pass
    
    def test_llm_model_not_found(self):
        """Test handling of model not found error."""
        with pytest.raises(Exception):
            create_ollama_llm(model="nonexistent-model")
    
    def test_llm_service_unavailable(self):
        """Test handling of Ollama service unavailable."""
        # Test with invalid base URL
        with pytest.raises(Exception):
            create_ollama_llm(base_url="http://invalid:11434")


def test_milestone_1_7_acceptance_criteria():
    """Validate all Milestone 1.7 acceptance criteria."""
    # AC1: Ollama running locally (or in Docker)
    # (validated in TASK-025)
    
    # AC2: At least one model downloaded (llama2 or similar)
    # (validated in TASK-036)
    
    # AC3: LangChain integration with Ollama working
    # (validated in TASK-033)
    
    # AC4: Basic inference working (text generation)
    # (validated in inference tests)
    
    # AC5: LangGraph workflow uses Ollama LLM
    # (validated in workflow integration tests)
    
    # AC6: Model responses are reasonable
    # (validated in inference tests)
    
    # AC7: Error handling for LLM calls
    # (validated in error handling tests)
    pass
```

## Testing

### Test Execution
- [ ] Run all LLM integration tests
- [ ] Verify test coverage >80%
- [ ] Validate all tests pass
- [ ] Check for test failures
- [ ] Run mock tests for CI/CD

### Test Coverage
- [ ] LLM initialization coverage
- [ ] Inference coverage
- [ ] LLM node coverage
- [ ] Workflow integration coverage
- [ ] Error handling coverage
- [ ] Model validation coverage

## Acceptance Criteria
- [ ] Test Ollama LLM initialization
- [ ] Test basic inference
- [ ] Test LLM node execution
- [ ] Test LLM integration in workflows
- [ ] Test error handling
- [ ] Test model validation
- [ ] All Milestone 1.7 acceptance criteria validated
- [ ] Test coverage >80%
- [ ] All tests passing
- [ ] Documentation complete

## Dependencies
- **External**: pytest, pytest-asyncio
- **Internal**: TASK-033 through TASK-036 (all LLM integration components)

## Risks and Mitigation

### Risk 1: LLM Tests Slow
- **Probability**: High
- **Impact**: Low
- **Mitigation**: Use mocks for CI/CD, run real LLM tests separately, optimize test timeouts

### Risk 2: LLM Response Variability
- **Probability**: Medium
- **Impact**: Low
- **Mitigation**: Test for response structure, not exact content, use appropriate assertions

### Risk 3: Test Coverage Gaps
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Review acceptance criteria, add comprehensive test scenarios, use coverage tools

## Task Status
- [ ] Analysis Complete
- [ ] Planning Complete
- [ ] Implementation Complete
- [ ] Testing Complete
- [ ] Documentation Complete

## Notes
- Use mocks for CI/CD to avoid requiring Ollama service
- Run real LLM tests separately for integration validation
- Test response structure, not exact content
- Ensure all Milestone 1.7 acceptance criteria are validated
- Document test execution and requirements

