# LangChain-Ollama Integration Guide

## Overview

This guide documents the LangChain-Ollama integration setup (TASK-026) for using Ollama LLM models with LangChain and LangGraph workflows.

## Package Installation

### Requirements

The `langchain-ollama` package is included in `requirements.txt`:

```txt
# Ollama Integration (TASK-026: Phase 3)
langchain-ollama>=0.1.0
```

### Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Install from requirements.txt
pip install -r requirements.txt

# Or install directly
pip install "langchain-ollama>=0.1.0"
```

### Verification

```bash
# Verify package installation
python -c "from langchain_ollama import OllamaLLM; print('✓ Import successful')"

# Check package version
python -c "from importlib.metadata import version; print(f'langchain-ollama: {version(\"langchain-ollama\")}')"
```

**Expected Output**:
```
✓ Import successful
langchain-ollama: 1.0.0
```

## Import Patterns

### ✅ CORRECT Import (Use This)

```python
# Primary import path (recommended)
from langchain_ollama import OllamaLLM

# Alternative import path (also valid)
from langchain_ollama.llms import OllamaLLM
```

### ❌ INCORRECT Import (Deprecated - Do Not Use)

```python
# DEPRECATED - Do not use
# from langchain_community.llms import Ollama
```

**Note**: The `langchain_community.llms.Ollama` import is deprecated. Always use `langchain_ollama.OllamaLLM` instead.

## Basic Usage

### Initialization

```python
from langchain_ollama import OllamaLLM

# Basic initialization
llm = OllamaLLM(
    model="llama2",
    base_url="http://localhost:11434",
    temperature=0.7
)

# With Docker environment
llm = OllamaLLM(
    model="llama2:13b",
    base_url="http://ollama:11434",  # Use service name in Docker
    temperature=0.7
)
```

### Configuration

**Model Selection**:
- Default: `llama2`
- Available models: `llama2`, `llama2:7b`, `llama2:13b`, `mistral`, etc.
- Use `ollama list` to see available models

**Base URL**:
- Local development: `http://localhost:11434`
- Docker environment: `http://ollama:11434` (service name)
- Custom: Set via `OLLAMA_BASE_URL` environment variable

**Temperature**:
- Default: `0.7`
- Range: `0.0` (deterministic) to `1.0` (creative)

### Environment Variables

```bash
# .env file
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2:13b
DOCKER_ENV=false  # Set to "true" when running in Docker
```

## Integration with LangChain

### Basic Chain

```python
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

# Initialize Ollama LLM
llm = OllamaLLM(
    model="llama2",
    base_url="http://localhost:11434",
    temperature=0.7
)

# Create prompt template
prompt = PromptTemplate(
    input_variables=["task"],
    template="You are a helpful assistant. Task: {task}"
)

# Create chain
chain = LLMChain(llm=llm, prompt=prompt)

# Run inference
result = chain.run("Analyze this data: [1, 2, 3, 4, 5]")
print(result)
```

## Integration with LangGraph

### LLM Node in LangGraph Workflow

```python
from langgraph.graph import StateGraph, START, END
from langchain_ollama import OllamaLLM
from typing import TypedDict

class LLMState(TypedDict):
    input: str
    output: str
    status: str

def llm_node(state: LLMState) -> LLMState:
    """Node that uses Ollama LLM"""
    llm = OllamaLLM(
        model="llama2",
        base_url="http://localhost:11434",
        temperature=0.7
    )
    
    input_text = state.get("input", "")
    output = llm.invoke(input_text)
    
    return {
        "input": input_text,
        "output": output,
        "status": "completed"
    }

# Build workflow
workflow = StateGraph(LLMState)
workflow.add_node("llm_processing", llm_node)
workflow.add_edge(START, "llm_processing")
workflow.add_edge("llm_processing", END)

# Compile and run
app = workflow.compile()
result = app.invoke({"input": "Hello, world!", "output": "", "status": "processing"})
```

## Compatibility

### LangChain Compatibility

`OllamaLLM` inherits from `BaseLLM` in `langchain_core`, making it fully compatible with:
- LangChain chains
- LangGraph workflows
- LangChain prompts and templates
- LangChain callbacks and monitoring

### Version Requirements

- **langchain-ollama**: >=0.1.0 (installed: 1.0.0)
- **langchain**: >=0.2.0 (compatible with 1.0.5+)
- **langchain-core**: >=0.2.0 (compatible with 1.0.4+)
- **langgraph**: >=0.6.0 (compatible with 1.0.3+)

### Dependency Verification

```python
# Verify compatibility
from langchain_ollama import OllamaLLM
from langchain_core.language_models.llms import BaseLLM

# Check inheritance
assert issubclass(OllamaLLM, BaseLLM), "OllamaLLM should inherit from BaseLLM"
```

## Testing

### Production Tests

Comprehensive tests are available in `project/tests/langgraph/test_langchain_ollama_integration.py`:

```bash
# Run all langchain-ollama integration tests
pytest project/tests/langgraph/test_langchain_ollama_integration.py -v
```

**Test Coverage** (13 tests):
- Package import verification
- Version requirement validation
- OllamaLLM class attributes
- Real initialization (no mocks)
- Dependency verification
- LangChain compatibility
- Requirements.txt validation

**All tests run under production conditions - NO MOCKS, NO PLACEHOLDERS.**

## Troubleshooting

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'langchain_ollama'`

**Solution**:
```bash
# Ensure venv is activated
source venv/bin/activate

# Install package
pip install "langchain-ollama>=0.1.0"

# Verify installation
python -c "from langchain_ollama import OllamaLLM"
```

### Connection Errors

**Error**: Connection refused when initializing OllamaLLM

**Solution**:
1. Verify Ollama service is running:
   ```bash
   # Local
   curl http://localhost:11434/api/tags
   
   # Docker
   docker-compose ps ollama
   docker exec airflow-ollama curl http://localhost:11434/api/tags
   ```

2. Check base URL:
   - Local: `http://localhost:11434`
   - Docker: `http://ollama:11434` (service name)

### Model Not Found

**Error**: Model not available

**Solution**:
```bash
# List available models
ollama list

# Pull required model
ollama pull llama2

# Or in Docker
docker exec airflow-ollama ollama pull llama2
```

### Version Compatibility

**Error**: Version conflicts

**Solution**:
```bash
# Check installed versions
pip list | grep langchain

# Verify compatibility
pip check

# Reinstall if needed
pip install --upgrade langchain-ollama
```

## Best Practices

1. **Always use correct import**: `from langchain_ollama import OllamaLLM`
2. **Configure base URL based on environment**: Local vs Docker
3. **Use environment variables** for configuration
4. **Test imports** before using in production code
5. **Verify Ollama service** is running before initialization
6. **Handle connection errors** gracefully in production code

## Related Documentation

- **TASK-026**: Update Requirements with LangChain-Ollama Integration
- **TASK-025**: Ollama Service Docker Integration
- **TASK-033**: Set Up Ollama with LangChain Integration (Implementation)
- **Setup Guide**: `project/docs/setup-guide.md`
- **Testing Guide**: `project/tests/langgraph/README.md`

## Next Steps

After completing TASK-026:
1. ✅ Package installed and verified
2. **TASK-033**: Implement Ollama LangChain integration module
3. **TASK-034**: Create LangGraph node with Ollama LLM
4. **TASK-035**: Integrate LLM inference in LangGraph workflows

See `project/dev/tasks/` for task details.

