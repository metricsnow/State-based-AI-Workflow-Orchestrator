# TASK-036: Model Download and Validation

## Task Information
- **Task ID**: TASK-036
- **Created**: 2025-01-27
- **Status**: Waiting
- **Priority**: Medium
- **Agent**: Mission Executor
- **Estimated Time**: 2-3 hours
- **Actual Time**: TBD
- **Type**: Setup
- **Dependencies**: TASK-025 ✅
- **Parent PRD**: `project/docs/prd_phase3.md` - Milestone 1.7

## Task Description
Create scripts and documentation for downloading and validating Ollama models. Ensure at least one model (llama2) is downloaded and validated. Provide scripts for model management.

## Problem Statement
Ollama models need to be downloaded before use. The PRD mentions downloading models (line 308) but doesn't provide automation or validation. This task creates scripts and processes for model management.

## Requirements

### Functional Requirements
- [ ] Script to download Ollama models
- [ ] Script to validate model availability
- [ ] Script to list available models
- [ ] At least one model downloaded (llama2)
- [ ] Model validation working
- [ ] Documentation for model management

### Technical Requirements
- [ ] Ollama CLI integration
- [ ] Model validation logic
- [ ] Error handling for download failures
- [ ] Configuration for model selection
- [ ] Logging and monitoring

## Implementation Plan

### Phase 1: Analysis
- [ ] Review Ollama model management
- [ ] Review model download requirements
- [ ] Design model management scripts
- [ ] Plan validation logic

### Phase 2: Planning
- [ ] Plan download script
- [ ] Plan validation script
- [ ] Plan model listing script
- [ ] Plan error handling

### Phase 3: Implementation
- [ ] Create model download script
- [ ] Create model validation script
- [ ] Create model listing script
- [ ] Add error handling
- [ ] Download default model (llama2)

### Phase 4: Testing
- [ ] Test model download
- [ ] Test model validation
- [ ] Test model listing
- [ ] Test error handling

### Phase 5: Documentation
- [ ] Document model management
- [ ] Document model download process
- [ ] Document model validation
- [ ] Document model selection

## Technical Implementation

### Model Download Script
```python
# project/scripts/download_ollama_model.py
#!/usr/bin/env python3
"""Script to download Ollama models."""

import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_model(model_name: str = "llama2:13b") -> bool:
    """Download Ollama model.
    
    Args:
        model_name: Model name to download (default: llama2:13b)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Downloading Ollama model: {model_name}")
        
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"Model downloaded successfully: {model_name}")
        logger.debug(f"Output: {result.stdout}")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download model {model_name}: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False
    
    except FileNotFoundError:
        logger.error("Ollama not found. Is Ollama installed and in PATH?")
        return False


def validate_model(model_name: str) -> bool:
    """Validate that model is available.
    
    Args:
        model_name: Model name to validate
    
    Returns:
        True if model is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        models = result.stdout
        return model_name in models
    
    except Exception as e:
        logger.error(f"Failed to validate model: {e}")
        return False


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "llama2:13b"
    
    if download_model(model):
        if validate_model(model):
            print(f"Model {model} downloaded and validated successfully")
            sys.exit(0)
        else:
            print(f"Model {model} downloaded but validation failed")
            sys.exit(1)
    else:
        print(f"Failed to download model {model}")
        sys.exit(1)
```

### Model Validation Script
```python
# project/scripts/validate_ollama_models.py
#!/usr/bin/env python3
"""Script to validate Ollama models."""

import subprocess
import sys
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_models() -> List[str]:
    """List available Ollama models.
    
    Returns:
        List of model names
    """
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse model names from output
        lines = result.stdout.strip().split("\n")[1:]  # Skip header
        models = []
        for line in lines:
            if line.strip():
                model_name = line.split()[0]
                models.append(model_name)
        
        return models
    
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return []


def validate_model(model_name: str) -> bool:
    """Validate that model is available and can be used.
    
    Args:
        model_name: Model name to validate
    
    Returns:
        True if model is valid, False otherwise
    """
    models = list_models()
    
    if model_name not in models:
        logger.warning(f"Model {model_name} not found in available models")
        return False
    
    # Try to run a simple inference to validate
    try:
        result = subprocess.run(
            ["ollama", "run", model_name, "Say 'OK'"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True
        )
        
        logger.info(f"Model {model_name} validated successfully")
        return True
    
    except subprocess.TimeoutExpired:
        logger.error(f"Model {model_name} validation timed out")
        return False
    
    except Exception as e:
        logger.error(f"Model {model_name} validation failed: {e}")
        return False


if __name__ == "__main__":
    required_models = ["llama2:13b"]
    
    if len(sys.argv) > 1:
        required_models = sys.argv[1:]
    
    all_valid = True
    for model in required_models:
        if validate_model(model):
            print(f"✓ Model {model} is valid")
        else:
            print(f"✗ Model {model} is invalid or not available")
            all_valid = False
    
    sys.exit(0 if all_valid else 1)
```

### Docker Setup Script
```bash
# project/scripts/setup-ollama-models.sh
#!/bin/bash
# Script to set up Ollama models in Docker container

set -e

MODEL=${1:-"llama2:13b"}
CONTAINER=${2:-"airflow-ollama"}

echo "Setting up Ollama model: $MODEL in container: $CONTAINER"

# Check if container is running
if ! docker ps | grep -q "$CONTAINER"; then
    echo "Error: Container $CONTAINER is not running"
    exit 1
fi

# Download model
echo "Downloading model: $MODEL"
docker exec $CONTAINER ollama pull $MODEL

# Validate model
echo "Validating model: $MODEL"
docker exec $CONTAINER ollama list | grep -q "$MODEL" || {
    echo "Error: Model $MODEL not found after download"
    exit 1
}

echo "Model $MODEL set up successfully"
```

## Testing

### Manual Testing
- [ ] Run download script: `python scripts/download_ollama_model.py llama2:13b`
- [ ] Run validation script: `python scripts/validate_ollama_models.py llama2:13b`
- [ ] Test in Docker: `./scripts/setup-ollama-models.sh llama2:13b`
- [ ] Verify model available: `ollama list`
- [ ] Test model inference: `ollama run llama2:13b "Hello"`

### Automated Testing
- [ ] Unit tests for download script
- [ ] Unit tests for validation script
- [ ] Integration tests with Ollama
- [ ] Test error handling

## Acceptance Criteria
- [ ] Script to download Ollama models
- [ ] Script to validate model availability
- [ ] Script to list available models
- [ ] At least one model downloaded (llama2)
- [ ] Model validation working
- [ ] Documentation for model management
- [ ] Scripts tested and working
- [ ] Docker setup script working

## Dependencies
- **External**: Ollama CLI
- **Internal**: TASK-025 (Ollama service)

## Risks and Mitigation

### Risk 1: Model Download Failures
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Implement retry logic, handle network errors, provide clear error messages

### Risk 2: Large Model Sizes
- **Probability**: High
- **Impact**: Medium
- **Mitigation**: Document model sizes, recommend smaller models for testing, provide disk space requirements

### Risk 3: Model Validation Timeout
- **Probability**: Low
- **Impact**: Low
- **Mitigation**: Set appropriate timeout, handle timeout errors gracefully

## Task Status
- [ ] Analysis Complete
- [ ] Planning Complete
- [ ] Implementation Complete
- [ ] Testing Complete
- [ ] Documentation Complete

## Notes
- Start with smaller models (llama2:7b) for testing
- Document model sizes and disk space requirements
- Provide both Python scripts and shell scripts
- Support Docker and local installations
- Consider model caching for faster setup

