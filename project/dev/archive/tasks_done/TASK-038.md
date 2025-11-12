# TASK-038: Create Unified LLM Factory with Model Toggle (Ollama/OpenAI)

## Task Information
- **Task ID**: TASK-038
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
Create a unified LLM factory that allows toggling between Ollama and OpenAI models via environment variables. Default to the cheapest OpenAI model (`gpt-3.5-turbo`) for cost optimization. This provides flexibility to switch between local (Ollama) and cloud (OpenAI) LLM providers based on requirements, cost, and performance needs.

## Problem Statement
The current implementation (TASK-033) only supports Ollama. Production systems need flexibility to choose between local and cloud LLM providers. A unified factory pattern allows switching providers via configuration without code changes. Defaulting to the cheapest OpenAI model (`gpt-3.5-turbo`) optimizes costs while maintaining quality.

## Requirements

### Functional Requirements
- [ ] Unified LLM factory supporting both Ollama and OpenAI
- [ ] Environment variable toggle for LLM provider selection
- [ ] Default to cheapest OpenAI model (`gpt-3.5-turbo`)
- [ ] Seamless switching between providers
- [ ] Configuration via environment variables
- [ ] Backward compatibility with existing Ollama integration
- [ ] Error handling for missing credentials
- [ ] Fallback mechanism (OpenAI → Ollama if OpenAI fails)

### Technical Requirements
- [ ] Factory pattern implementation
- [ ] Environment variable: `LLM_PROVIDER` (values: `ollama`, `openai`, `auto`)
- [ ] Environment variable: `OPENAI_API_KEY` (from .env)
- [ ] Environment variable: `OPENAI_MODEL` (default: `gpt-3.5-turbo`)
- [ ] Integration with `langchain-openai` package
- [ ] Integration with existing `langchain_ollama_integration`
- [ ] Unified interface for both providers
- [ ] Logging and monitoring
- [ ] Configuration validation

## Implementation Plan

### Phase 1: Analysis
- [ ] Review existing Ollama integration (TASK-033)
- [ ] Review OpenAI LangChain integration patterns
- [ ] Review cheapest OpenAI model options (`gpt-3.5-turbo`, `gpt-4o-mini`)
- [ ] Design unified factory interface
- [ ] Plan configuration management
- [ ] Plan fallback mechanism

### Phase 2: Planning
- [ ] Design unified LLM factory structure
- [ ] Plan provider selection logic
- [ ] Plan configuration loading
- [ ] Plan error handling and fallback
- [ ] Plan integration with existing workflows

### Phase 3: Implementation
- [ ] Add `langchain-openai` to requirements.txt
- [ ] Create unified LLM factory module
- [ ] Implement provider selection logic
- [ ] Implement OpenAI LLM creation
- [ ] Implement fallback mechanism
- [ ] Add configuration validation
- [ ] Update existing integration to use factory
- [ ] Add logging and monitoring

### Phase 4: Testing
- [ ] Test OpenAI LLM initialization
- [ ] Test Ollama LLM initialization
- [ ] Test provider switching
- [ ] Test fallback mechanism
- [ ] Test configuration validation
- [ ] Test with existing LangGraph workflows
- [ ] Test error handling

### Phase 5: Documentation
- [ ] Document unified factory usage
- [ ] Document environment variables
- [ ] Document provider selection
- [ ] Document fallback behavior
- [ ] Update .env.example with new variables

## Technical Implementation

### Requirements Update
```txt
# Add to requirements.txt
langchain-openai>=0.1.0
```

### Unified LLM Factory
```python
# project/langchain_ollama_integration/llm_factory.py (update)
import os
import logging
from typing import Optional, Literal, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


def get_llm_provider() -> Literal["ollama", "openai", "auto"]:
    """Get LLM provider from environment variable.
    
    Returns:
        Provider name: 'ollama', 'openai', or 'auto'
        Default: 'openai' (cheapest option)
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    valid_providers = ["ollama", "openai", "auto"]
    
    if provider not in valid_providers:
        logger.warning(
            f"Invalid LLM_PROVIDER '{provider}'. "
            f"Valid options: {valid_providers}. Using default: 'openai'"
        )
        return "openai"
    
    return provider


def get_openai_model() -> str:
    """Get OpenAI model from environment variable.
    
    Returns:
        Model name (default: 'gpt-3.5-turbo' - cheapest option)
    """
    return os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")


def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from environment variable.
    
    Returns:
        API key or None if not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not found in environment variables")
    return api_key


def get_ollama_base_url() -> str:
    """Get Ollama base URL from environment."""
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
    """Create Ollama LLM instance."""
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


def create_openai_llm(
    model: Optional[str] = None,
    temperature: float = 0.7,
    **kwargs
) -> ChatOpenAI:
    """Create OpenAI LLM instance.
    
    Args:
        model: Model name (defaults to OPENAI_MODEL env var or 'gpt-3.5-turbo')
        temperature: Temperature for generation (default: 0.7)
        **kwargs: Additional arguments for ChatOpenAI
    
    Returns:
        ChatOpenAI instance
    
    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    api_key = get_openai_api_key()
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables. "
            "Please set it in .env file."
        )
    
    if model is None:
        model = get_openai_model()
    
    try:
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            openai_api_key=api_key,
            **kwargs
        )
        logger.info(f"Created ChatOpenAI: model={model}")
        return llm
    except Exception as e:
        logger.error(f"Failed to create ChatOpenAI: {e}", exc_info=True)
        raise


def create_llm(
    provider: Optional[Literal["ollama", "openai", "auto"]] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    fallback: bool = True,
    **kwargs
) -> Union[OllamaLLM, ChatOpenAI]:
    """Create LLM instance based on provider configuration.
    
    This is the unified factory function that creates the appropriate LLM
    based on environment configuration or explicit provider selection.
    
    Args:
        provider: Explicit provider override ('ollama', 'openai', 'auto')
                  If None, uses LLM_PROVIDER env var (default: 'openai')
        model: Model name override (provider-specific)
        temperature: Temperature for generation (default: 0.7)
        fallback: If True, fallback to Ollama if OpenAI fails (default: True)
        **kwargs: Additional arguments for LLM initialization
    
    Returns:
        LLM instance (OllamaLLM or ChatOpenAI)
    
    Raises:
        ValueError: If provider is invalid or credentials missing
        RuntimeError: If all providers fail and fallback disabled
    
    Example:
        ```python
        from langchain_ollama_integration import create_llm
        
        # Use default (OpenAI gpt-3.5-turbo)
        llm = create_llm()
        
        # Explicitly use OpenAI
        llm = create_llm(provider="openai", model="gpt-4o-mini")
        
        # Explicitly use Ollama
        llm = create_llm(provider="ollama", model="llama2:7b")
        
        # Auto mode (try OpenAI, fallback to Ollama)
        llm = create_llm(provider="auto")
        ```
    """
    if provider is None:
        provider = get_llm_provider()
    
    # Auto mode: try OpenAI first, fallback to Ollama
    if provider == "auto":
        try:
            logger.info("Auto mode: Attempting OpenAI first")
            return create_openai_llm(model=model, temperature=temperature, **kwargs)
        except Exception as e:
            logger.warning(f"OpenAI failed in auto mode: {e}")
            if fallback:
                logger.info("Falling back to Ollama")
                return create_ollama_llm(model=model, temperature=temperature, **kwargs)
            else:
                raise RuntimeError(f"Auto mode failed: OpenAI error and fallback disabled")
    
    # Explicit provider selection
    if provider == "openai":
        try:
            return create_openai_llm(model=model, temperature=temperature, **kwargs)
        except Exception as e:
            if fallback:
                logger.warning(f"OpenAI failed, falling back to Ollama: {e}")
                return create_ollama_llm(model=model, temperature=temperature, **kwargs)
            raise
    
    elif provider == "ollama":
        return create_ollama_llm(model=model, temperature=temperature, **kwargs)
    
    else:
        raise ValueError(f"Invalid provider: {provider}. Must be 'ollama', 'openai', or 'auto'")


def get_llm() -> Union[OllamaLLM, ChatOpenAI]:
    """Get default LLM instance using configuration.
    
    Returns:
        Default LLM instance based on LLM_PROVIDER env var
        Default: OpenAI gpt-3.5-turbo (cheapest option)
    """
    return create_llm()
```

### Updated Module Exports
```python
# project/langchain_ollama_integration/__init__.py (update)
"""Unified LangChain LLM integration module with Ollama and OpenAI support."""

from langchain_ollama_integration.llm_factory import (
    create_llm,
    get_llm,
    create_ollama_llm,
    create_openai_llm,
    get_llm_provider,
    get_openai_model,
    get_ollama_model,
)

__all__ = [
    "create_llm",
    "get_llm",
    "create_ollama_llm",
    "create_openai_llm",
    "get_llm_provider",
    "get_openai_model",
    "get_ollama_model",
]
```

### Environment Variables (.env.example)
```bash
# LLM Provider Configuration
# Options: 'ollama', 'openai', 'auto' (default: 'openai' - cheapest)
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo  # Cheapest OpenAI model (default)

# Ollama Configuration (fallback/local option)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2:13b
```

### Integration with Existing Code
```python
# Update existing LangGraph nodes to use unified factory
# project/langgraph_workflows/llm_nodes.py (update)

from langchain_ollama_integration import create_llm  # Updated import

def create_llm_node(
    model: Optional[str] = None,
    prompt_template: Optional[str] = None,
    temperature: float = 0.7,
    provider: Optional[str] = None  # NEW: Allow provider override
):
    """Create a LangGraph node that uses unified LLM factory."""
    # Use unified factory - automatically selects provider from env
    llm = create_llm(provider=provider, model=model, temperature=temperature)
    
    # ... rest of implementation
```

## Testing

### Manual Testing
- [ ] Test with `LLM_PROVIDER=openai` (default)
- [ ] Test with `LLM_PROVIDER=ollama`
- [ ] Test with `LLM_PROVIDER=auto`
- [ ] Test OpenAI with `gpt-3.5-turbo`
- [ ] Test OpenAI with `gpt-4o-mini` (alternative cheap option)
- [ ] Test fallback mechanism (OpenAI fails → Ollama)
- [ ] Test error handling (missing API key)
- [ ] Test with existing LangGraph workflows
- [ ] Verify backward compatibility

### Automated Testing
- [ ] Unit tests for provider selection
- [ ] Unit tests for OpenAI LLM creation
- [ ] Unit tests for Ollama LLM creation
- [ ] Unit tests for fallback mechanism
- [ ] Unit tests for configuration validation
- [ ] Integration tests with workflows
- [ ] Mock tests for CI/CD (no API keys required)

## Acceptance Criteria
- [ ] Unified LLM factory supporting Ollama and OpenAI
- [ ] Environment variable toggle working (`LLM_PROVIDER`)
- [ ] Default to cheapest OpenAI model (`gpt-3.5-turbo`)
- [ ] Seamless switching between providers
- [ ] Configuration via environment variables
- [ ] Backward compatibility with existing Ollama integration
- [ ] Error handling for missing credentials
- [ ] Fallback mechanism working (OpenAI → Ollama)
- [ ] Integration with existing LangGraph workflows
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Documentation complete
- [ ] .env.example updated

## Dependencies
- **External**: langchain-openai package
- **Internal**: TASK-033 (Ollama integration), existing LangGraph workflows

## Risks and Mitigation

### Risk 1: OpenAI API Key Not Set
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: Clear error messages, fallback to Ollama, validate in factory, document in .env.example

### Risk 2: Cost Overruns with OpenAI
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Default to cheapest model (`gpt-3.5-turbo`), document costs, provide Ollama fallback

### Risk 3: Provider Switching Complexity
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Unified interface, clear documentation, comprehensive testing

### Risk 4: Backward Compatibility Issues
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Maintain existing function signatures, add new functions, test existing workflows

## Task Status
- [x] Analysis Complete
- [x] Planning Complete
- [x] Implementation Complete
- [x] Testing Complete
- [x] Documentation Complete

## Notes
- **DEFAULT**: Use OpenAI `gpt-3.5-turbo` (cheapest option) as default
- **FALLBACK**: Automatic fallback to Ollama if OpenAI fails
- **COST OPTIMIZATION**: Default to cheapest model to minimize costs
- **FLEXIBILITY**: Allow switching providers via environment variable
- **BACKWARD COMPATIBLE**: Existing Ollama code continues to work
- **SECURITY**: All credentials from .env file only
- **AUTO MODE**: Try OpenAI first, fallback to Ollama if needed
- Consider adding cost tracking/monitoring in future enhancement

