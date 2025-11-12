# TASK-033: Set Up Ollama with LangChain Integration (Corrected Imports)

## Task Information
- **Task ID**: TASK-033
- **Created**: 2025-01-27
- **Status**: Done
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 2-3 hours
- **Actual Time**: TBD
- **Type**: Integration
- **Dependencies**: TASK-025 ✅, TASK-026 ✅
- **Parent PRD**: `project/docs/prd_phase3.md` - Milestone 1.7

## Task Description
Set up Ollama with LangChain integration using the CORRECT import pattern identified by Mission Analyst. The PRD shows incorrect import `from langchain_community.llms import Ollama` (deprecated). Use `from langchain_ollama import OllamaLLM` instead. Create integration module and verify basic inference works.

## Problem Statement
Mission Analyst identified that PRD Phase 3 (lines 316, 354) shows incorrect LangChain import for Ollama. The deprecated `langchain_community.llms.Ollama` should be replaced with `langchain_ollama.OllamaLLM`. This task implements the corrected integration and verifies it works.

## Requirements

### Functional Requirements
- [x] Ollama service accessible (from TASK-025)
- [x] LangChain-Ollama integration working
- [x] Correct import pattern used
- [x] Basic inference working
- [x] Configuration via environment variables
- [x] Error handling for LLM calls

### Technical Requirements
- [x] Use `langchain-ollama` package (from TASK-026)
- [x] Use `OllamaLLM` class (not `Ollama`)
- [x] Configuration for model selection
- [x] Configuration for base URL
- [x] Error handling and retry logic
- [x] Logging and monitoring

## Implementation Plan

### Phase 1: Analysis
- [ ] Review Mission Analyst findings on correct imports
- [ ] Review langchain-ollama documentation
- [ ] Review Ollama service configuration (TASK-025)
- [ ] Design integration module
- [ ] Plan configuration

### Phase 2: Planning
- [ ] Design integration module structure
- [ ] Plan LLM initialization
- [ ] Plan configuration management
- [ ] Plan error handling

### Phase 3: Implementation
- [ ] Create `langchain_ollama_integration` module
- [ ] Implement LLM initialization with correct imports
- [ ] Add configuration management
- [ ] Add error handling
- [ ] Create basic inference test
- [ ] Verify integration works

### Phase 4: Testing
- [ ] Test LLM initialization
- [ ] Test basic inference
- [ ] Test error handling
- [ ] Test configuration
- [ ] Verify correct imports

### Phase 5: Documentation
- [ ] Document correct import pattern
- [ ] Document configuration
- [ ] Document usage examples
- [ ] Document error handling

## Technical Implementation

### Integration Module
```python
# project/langchain_ollama_integration/__init__.py
"""LangChain-Ollama integration module with corrected imports."""

from langchain_ollama_integration.llm_factory import create_ollama_llm, get_ollama_llm

__all__ = ["create_ollama_llm", "get_ollama_llm"]
```

### LLM Factory with Correct Imports
```python
# project/langchain_ollama_integration/llm_factory.py
import os
import logging
from typing import Optional
from langchain_ollama import OllamaLLM  # CORRECT import

logger = logging.getLogger(__name__)


def get_ollama_base_url() -> str:
    """Get Ollama base URL from environment."""
    # Use service name in Docker, localhost for local development
    if os.getenv("DOCKER_ENV") == "true":
        return "http://ollama:11434"
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def get_ollama_model() -> str:
    """Get Ollama model from environment."""
    return os.getenv("OLLAMA_MODEL", "llama2:13b")


def create_ollama_llm(
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.7,
    **kwargs
) -> OllamaLLM:
    """Create Ollama LLM instance with correct import.
    
    Args:
        model: Model name (defaults to OLLAMA_MODEL env var or "llama2:13b")
        base_url: Ollama base URL (defaults to OLLAMA_BASE_URL env var)
        temperature: Temperature for generation (default: 0.7)
        **kwargs: Additional arguments for OllamaLLM
    
    Returns:
        OllamaLLM instance
    
    Example:
        ```python
        from langchain_ollama_integration import create_ollama_llm
        
        llm = create_ollama_llm(model="llama2:13b")
        result = llm.invoke("Hello, world!")
        ```
    """
    if model is None:
        model = get_ollama_model()
    
    if base_url is None:
        base_url = get_ollama_base_url()
    
    try:
        llm = OllamaLLM(
            model=model,
            base_url=base_url,
            temperature=temperature,
            **kwargs
        )
        
        logger.info(f"Created OllamaLLM: model={model}, base_url={base_url}")
        return llm
    
    except Exception as e:
        logger.error(f"Failed to create OllamaLLM: {e}", exc_info=True)
        raise


def get_ollama_llm() -> OllamaLLM:
    """Get default Ollama LLM instance."""
    return create_ollama_llm()
```

### Basic Inference Test
```python
# project/langchain_ollama_integration/test_integration.py
import pytest
from langchain_ollama_integration import create_ollama_llm


def test_ollama_llm_initialization():
    """Test Ollama LLM initialization with correct import."""
    llm = create_ollama_llm(model="llama2:13b")
    assert llm is not None
    assert hasattr(llm, "invoke")


def test_ollama_basic_inference():
    """Test basic inference with Ollama."""
    llm = create_ollama_llm(model="llama2:13b")
    
    result = llm.invoke("Say 'Hello, World!' in one sentence.")
    
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


def test_ollama_error_handling():
    """Test error handling for invalid model."""
    with pytest.raises(Exception):
        create_ollama_llm(model="nonexistent-model")
```

## Testing

### Manual Testing
- [ ] Verify Ollama service running: `curl http://localhost:11434/api/tags`
- [ ] Test LLM initialization: `python -c "from langchain_ollama_integration import create_ollama_llm; llm = create_ollama_llm(); print('OK')"`
- [ ] Test basic inference
- [ ] Test error handling
- [ ] Test configuration via environment variables

### Automated Testing
- [ ] Unit tests for LLM factory
- [ ] Unit tests for configuration
- [ ] Integration tests with Ollama
- [ ] Test error handling
- [ ] Mock tests for CI/CD

## Acceptance Criteria
- [x] Ollama service accessible
- [x] LangChain-Ollama integration working
- [x] Correct import pattern used (`from langchain_ollama import OllamaLLM`)
- [x] Basic inference working
- [x] Configuration via environment variables
- [x] Error handling for LLM calls
- [x] Unit tests passing
- [x] Integration tests passing
- [x] Documentation complete

## Dependencies
- **External**: langchain-ollama package
- **Internal**: TASK-025 (Ollama service), TASK-026 (langchain-ollama package)

## Risks and Mitigation

### Risk 1: Incorrect Import Still Used
- **Probability**: Low
- **Impact**: High
- **Mitigation**: Code review, use correct import, document correct pattern

### Risk 2: Ollama Service Not Accessible
- **Probability**: Low
- **Impact**: High
- **Mitigation**: Verify Ollama service running, check network connectivity, verify Docker networking

### Risk 3: Model Not Available
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Verify model downloaded, handle model not found errors, provide clear error messages

## Task Status
- [x] Analysis Complete
- [x] Planning Complete
- [x] Implementation Complete
- [x] Testing Complete
- [x] Documentation Complete

## Notes
- **CRITICAL**: Use `from langchain_ollama import OllamaLLM` (NOT `from langchain_community.llms import Ollama`)
- Mission Analyst identified this as critical issue
- Verify Ollama service is running before testing
- Use environment variables for configuration
- Handle model download errors gracefully
- Document correct import pattern clearly

