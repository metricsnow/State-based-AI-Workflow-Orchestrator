# Ollama Model Management Guide

## Overview

This guide documents the Ollama model management scripts and processes for downloading, validating, and managing Ollama models in the project.

**Status**: ✅ TASK-036 Complete - Model management scripts implemented and tested

## Scripts Overview

The project includes three scripts for managing Ollama models:

1. **`download_ollama_model.py`** - Download and validate Ollama models
2. **`validate_ollama_models.py`** - Validate existing Ollama models
3. **`setup-ollama-models.sh`** - Docker setup script for model management

## Script Locations

All scripts are located in `project/scripts/`:

```
project/scripts/
├── download_ollama_model.py
├── validate_ollama_models.py
└── setup-ollama-models.sh
```

## Model Download Script

### Purpose

Downloads Ollama models using the Ollama CLI and validates that the download was successful.

### Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Download default model (llama2:13b)
python project/scripts/download_ollama_model.py

# Download specific model
python project/scripts/download_ollama_model.py llama2:7b
python project/scripts/download_ollama_model.py llama3.2:latest
```

### Features

- Downloads models using `ollama pull` command
- Validates model availability after download
- Comprehensive error handling
- Logging for debugging
- Exit codes for automation (0 = success, 1 = failure)

### Example Output

```bash
$ python project/scripts/download_ollama_model.py llama3.2:latest
2025-11-12 10:32:00,000 - __main__ - INFO - Downloading Ollama model: llama3.2:latest
2025-11-12 10:32:30,000 - __main__ - INFO - Model downloaded successfully: llama3.2:latest
Model llama3.2:latest downloaded and validated successfully
```

### Error Handling

The script handles common errors:

- **Ollama not found**: Checks if Ollama CLI is in PATH
- **Download failures**: Catches subprocess errors and provides clear messages
- **Validation failures**: Verifies model is available after download

## Model Validation Script

### Purpose

Validates that Ollama models are available and can be used for inference. Checks model availability and optionally runs a test inference.

### Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Validate default model (llama2:13b)
python project/scripts/validate_ollama_models.py

# Validate specific model
python project/scripts/validate_ollama_models.py llama3.2:latest

# Validate multiple models
python project/scripts/validate_ollama_models.py llama3.2:latest gemma3:1b
```

### Features

- Lists all available models
- Validates model availability
- Optional test inference to verify functionality
- Supports multiple model validation
- Clear success/failure indicators (✓/✗)

### Example Output

```bash
$ python project/scripts/validate_ollama_models.py llama3.2:latest
2025-11-12 10:32:36,529 - __main__ - INFO - Model llama3.2:latest found in available models
2025-11-12 10:32:36,529 - __main__ - INFO - Testing inference with model llama3.2:latest...
2025-11-12 10:32:40,615 - __main__ - INFO - Model llama3.2:latest validated successfully
✓ Model llama3.2:latest is valid
```

### Validation Process

1. **List Models**: Retrieves list of available models using `ollama list`
2. **Check Availability**: Verifies model name exists in available models
3. **Test Inference** (optional): Runs a simple inference test to verify functionality
4. **Report Results**: Provides clear success/failure status

### Error Handling

- **Model not found**: Lists available models for reference
- **Inference timeout**: Handles timeout errors (30 second default)
- **Inference failures**: Catches and reports inference errors

## Docker Setup Script

### Purpose

Downloads and validates Ollama models in a Docker container. Useful for setting up models in containerized environments.

### Usage

```bash
# Make script executable (first time only)
chmod +x project/scripts/setup-ollama-models.sh

# Setup default model (llama2:13b) in default container (airflow-ollama)
./project/scripts/setup-ollama-models.sh

# Setup specific model
./project/scripts/setup-ollama-models.sh llama3.2:latest

# Setup model in specific container
./project/scripts/setup-ollama-models.sh llama3.2:latest airflow-ollama
```

### Features

- Checks if container is running
- Downloads model using `docker exec`
- Validates model after download
- Clear error messages
- Exit codes for automation

### Prerequisites

- Docker must be installed and running
- Target container must be running
- Container must have Ollama CLI available

### Example Output

```bash
$ ./project/scripts/setup-ollama-models.sh llama3.2:latest
Setting up Ollama model: llama3.2:latest in container: airflow-ollama
Downloading model: llama3.2:latest
Validating model: llama3.2:latest
Model llama3.2:latest set up successfully
```

### Error Handling

- **Container not running**: Checks container status before proceeding
- **Download failures**: Catches and reports download errors
- **Validation failures**: Verifies model exists after download

## Model Selection

### Recommended Models

For different use cases:

**Testing/Development**:
- `gemma3:1b` - Small, fast (1.3 GB, ~0.5s inference)
- `phi4-mini:3.8b` - Fast, medium size (2.5 GB, ~0.45s inference)
- `llama3.2:latest` - Good balance (2.0 GB, ~0.5s inference)

**Production**:
- `llama3.2:latest` - Good quality and performance
- `qwen3:14b` - Higher quality (9.3 GB)
- `magistral:24b` - Best quality (14 GB)

### Model Sizes

Common model sizes for planning:

- **Small (< 2 GB)**: `gemma3:1b` (815 MB), `llama3.2:latest` (2.0 GB)
- **Medium (2-10 GB)**: `phi4-mini:3.8b` (2.5 GB), `qwen3:14b` (9.3 GB)
- **Large (> 10 GB)**: `magistral:24b` (14 GB), `qwen3:32b` (20 GB)

### Checking Available Models

```bash
# List all available models
ollama list

# List models in Docker container
docker exec airflow-ollama ollama list
```

## Integration with Project

### Environment Variables

Model selection can be configured via environment variables:

```bash
# .env file
OLLAMA_MODEL=llama3.2:latest
OLLAMA_BASE_URL=http://localhost:11434
DOCKER_ENV=false
```

### Usage in Code

The model management scripts work with the existing LangChain-Ollama integration:

```python
from langchain_ollama_integration import create_ollama_llm

# Uses OLLAMA_MODEL from environment or default
llm = create_ollama_llm()

# Or specify model explicitly
llm = create_ollama_llm(model="llama3.2:latest")
```

## Troubleshooting

### Common Issues

**Issue**: "Ollama not found"
- **Solution**: Ensure Ollama is installed and in PATH
- **Check**: Run `which ollama` to verify installation

**Issue**: "Model download fails"
- **Solution**: Check network connection, verify model name is correct
- **Check**: Run `ollama list` to see available models

**Issue**: "Container not running"
- **Solution**: Start Docker container before running setup script
- **Check**: Run `docker ps` to verify container status

**Issue**: "Model validation timeout"
- **Solution**: Model may be slow to load, increase timeout or use smaller model
- **Check**: Verify model is actually downloaded and accessible

### Debugging

Enable debug logging:

```bash
# Python scripts
python project/scripts/download_ollama_model.py llama3.2:latest 2>&1 | grep DEBUG

# Or set logging level in script
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

1. **Download models before use**: Use download script to ensure models are available
2. **Validate models**: Run validation script to verify model functionality
3. **Use appropriate models**: Select models based on use case (testing vs production)
4. **Monitor disk space**: Large models require significant disk space
5. **Test in Docker**: Use Docker setup script for containerized environments
6. **Version control**: Document which models are used in each environment

## Related Documentation

- **[LangChain-Ollama Integration Guide](langchain-ollama-integration-guide.md)** - Using Ollama with LangChain
- **[LLM Test Optimization Guide](llm-test-optimization-guide.md)** - Model selection for testing
- **[Setup Guide](setup-guide.md)** - Environment setup instructions

## Task Reference

- **TASK-036**: Model Download and Validation (Complete)
- **TASK-033**: LangChain-Ollama Integration (Complete)
- **TASK-025**: Ollama Service Setup (Complete)

