# Unified LLM Factory Guide

Complete guide to the unified LLM factory (TASK-038) supporting both Ollama and OpenAI providers.

## Overview

The unified LLM factory provides a single interface for creating LLM instances from multiple providers (Ollama and OpenAI) with seamless switching via environment variables. This enables flexible provider selection based on requirements, cost, and performance needs.

**Status**: ✅ TASK-038 Complete - Unified factory implemented and tested

**Key Features**:
- Unified interface for Ollama and OpenAI providers
- Environment-based provider selection
- Default to cheapest OpenAI model (`gpt-4o-mini`) for cost optimization
- Automatic fallback mechanism (OpenAI → Ollama)
- Backward compatible with existing Ollama code
- Cost protection for automated testing

## Installation

The required packages are included in `requirements.txt`:

```txt
# Ollama Integration
langchain-ollama>=0.1.0

# OpenAI Integration
langchain-openai>=0.1.0
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root with the following variables:

```bash
# LLM Provider Configuration
# Options: 'ollama', 'openai', 'auto' (default: 'openai' - cheapest)
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
# Cheapest OpenAI model (default: gpt-4o-mini)
OPENAI_MODEL=gpt-4o-mini

# Ollama Configuration (fallback/local option)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest

# Docker Environment Flag
DOCKER_ENV=false
```

## Usage

### Basic Usage

```python
from langchain_ollama_integration import create_llm, get_llm

# Use default (OpenAI gpt-4o-mini - cheapest)
llm = create_llm()

# Or use convenience function
llm = get_llm()

# Invoke LLM
result = llm.invoke("Say hello")
```

### Provider Selection

```python
from langchain_ollama_integration import create_llm

# Explicitly use OpenAI
llm = create_llm(provider="openai", model="gpt-4o-mini")

# Explicitly use Ollama
llm = create_llm(provider="ollama", model="llama3.2:latest")

# Auto mode (try OpenAI, fallback to Ollama if OpenAI fails)
llm = create_llm(provider="auto")
```

### Provider-Specific Functions

```python
from langchain_ollama_integration import (
    create_ollama_llm,
    create_openai_llm,
    get_ollama_llm,
)

# Create Ollama LLM
ollama_llm = create_ollama_llm(model="llama3.2:latest")

# Create OpenAI LLM
openai_llm = create_openai_llm(model="gpt-4o-mini")

# Get default Ollama LLM
default_ollama = get_ollama_llm()
```

## Configuration Functions

### Provider Selection

```python
from langchain_ollama_integration import get_llm_provider

# Get current provider from environment
provider = get_llm_provider()  # Returns: 'ollama', 'openai', or 'auto'
```

### Model Configuration

```python
from langchain_ollama_integration import (
    get_openai_model,
    get_ollama_model,
)

# Get OpenAI model (default: 'gpt-4o-mini')
openai_model = get_openai_model()

# Get Ollama model (default: 'llama3.2:latest')
ollama_model = get_ollama_model()
```

## Cost Optimization

### Default Model

The factory defaults to `gpt-4o-mini`, which is currently the cheapest OpenAI model:

- **gpt-4o-mini**: ~$0.15/$0.60 per million tokens (input/output)
- **gpt-3.5-turbo**: ~$0.50/$1.50 per million tokens (input/output)

`gpt-4o-mini` is approximately **70% cheaper** for input tokens and **60% cheaper** for output tokens.

### Cost Protection for Testing

OpenAI tests are **disabled by default** to prevent API costs during automatic testing:

```bash
# Default: OpenAI tests are skipped
pytest project/tests/langchain_ollama_integration/test_unified_llm_factory.py

# Enable OpenAI tests (for manual/production testing only)
export ENABLE_OPENAI_TESTS=true
pytest project/tests/langchain_ollama_integration/test_unified_llm_factory.py
```

## Fallback Mechanism

The factory supports automatic fallback when OpenAI is unavailable:

```python
# Auto mode: tries OpenAI first, falls back to Ollama if OpenAI fails
llm = create_llm(provider="auto")

# Explicit OpenAI with fallback
llm = create_llm(provider="openai", fallback=True)
```

## Integration with LangGraph

The unified factory is integrated into LangGraph LLM nodes:

```python
from langgraph_workflows.llm_nodes import create_llm_node

# Create node with default provider (from environment)
node = create_llm_node()

# Create node with explicit provider
node = create_llm_node(provider="openai", model="gpt-4o-mini")

# Create node with Ollama
node = create_llm_node(provider="ollama", model="llama3.2:latest")
```

## Backward Compatibility

All existing Ollama-specific functions continue to work:

```python
from langchain_ollama_integration import (
    create_ollama_llm,
    get_ollama_llm,
    get_ollama_model,
    get_ollama_base_url,
)

# All existing code continues to work
llm = create_ollama_llm(model="llama3.2:latest")
```

## Testing

### Running Tests

```bash
# Run all tests (OpenAI tests skipped by default)
pytest project/tests/langchain_ollama_integration/test_unified_llm_factory.py

# Enable OpenAI tests (for manual testing)
export ENABLE_OPENAI_TESTS=true
pytest project/tests/langchain_ollama_integration/test_unified_llm_factory.py
```

### Test Coverage

- Provider selection (default, ollama, openai, auto)
- OpenAI configuration (default model, custom model)
- Real Ollama LLM creation and inference
- Real OpenAI LLM creation (when enabled)
- Unified factory with explicit providers
- Auto mode fallback mechanism
- Error handling (invalid provider, missing API key)
- Backward compatibility

**Test Results**: 20 tests (16 passed, 4 skipped by default)

## API Reference

### Main Functions

- `create_llm(provider, model, temperature, fallback, **kwargs)` - Unified factory function
- `get_llm()` - Get default LLM instance
- `create_ollama_llm(model, base_url, temperature, **kwargs)` - Create Ollama LLM
- `create_openai_llm(model, temperature, **kwargs)` - Create OpenAI LLM
- `get_llm_provider()` - Get provider from environment
- `get_openai_model()` - Get OpenAI model from environment
- `get_ollama_model()` - Get Ollama model from environment

### Environment Variables

- `LLM_PROVIDER` - Provider selection ('ollama', 'openai', 'auto', default: 'openai')
- `OPENAI_API_KEY` - OpenAI API key (required for OpenAI provider)
- `OPENAI_MODEL` - OpenAI model name (default: 'gpt-4o-mini')
- `OLLAMA_BASE_URL` - Ollama base URL (default: 'http://localhost:11434')
- `OLLAMA_MODEL` - Ollama model name (default: 'llama3.2:latest')
- `ENABLE_OPENAI_TESTS` - Enable OpenAI tests (default: 'false')

## Related Documentation

- **[LangChain LLM Integration Guide](langchain-ollama-integration-guide.md)** - Complete integration guide
- **[LangGraph LLM Nodes Guide](langgraph-llm-nodes-guide.md)** - LLM nodes for LangGraph workflows
- **[LLM Test Optimization Guide](llm-test-optimization-guide.md)** - Test optimization strategies

## Troubleshooting

### OpenAI API Key Not Found

**Error**: `OPENAI_API_KEY not found in environment variables`

**Solution**: Set `OPENAI_API_KEY` in your `.env` file or environment variables.

### OpenAI Tests Skipped

**Issue**: OpenAI tests are skipped during automatic testing

**Solution**: This is by design to prevent API costs. Set `ENABLE_OPENAI_TESTS=true` to enable for manual testing.

### Fallback Not Working

**Issue**: Fallback to Ollama not working when OpenAI fails

**Solution**: Ensure `fallback=True` is set (default) and Ollama service is available.

## Best Practices

1. **Use environment variables** for configuration
2. **Default to cheapest model** (`gpt-4o-mini`) for cost optimization
3. **Enable fallback** for production reliability
4. **Disable OpenAI tests** in CI/CD to prevent costs
5. **Use auto mode** for flexible provider selection
6. **Test with Ollama** for local development (no costs)

