#!/usr/bin/env python3
"""Script to validate Ollama models.

This script validates that Ollama models are available and can be used
for inference. It checks model availability and optionally runs a test
inference to ensure the model is functional.

Usage:
    python validate_ollama_models.py [model_name ...]

Examples:
    python validate_ollama_models.py llama2:13b
    python validate_ollama_models.py llama2:13b llama2:7b
"""

import subprocess
import sys
import logging
from typing import List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
                # Extract model name (first column)
                parts = line.split()
                if parts:
                    model_name = parts[0]
                    models.append(model_name)
        
        return models
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list models: {e}")
        logger.error(f"Error output: {e.stderr}")
        return []
    
    except FileNotFoundError:
        logger.error("Ollama not found. Is Ollama installed and in PATH?")
        return []
    
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return []


def validate_model(model_name: str, test_inference: bool = True) -> bool:
    """Validate that model is available and can be used.
    
    Args:
        model_name: Model name to validate
        test_inference: If True, run a test inference to validate functionality
    
    Returns:
        True if model is valid, False otherwise
    """
    models = list_models()
    
    if model_name not in models:
        logger.warning(f"Model {model_name} not found in available models")
        logger.info(f"Available models: {', '.join(models) if models else 'None'}")
        return False
    
    logger.info(f"Model {model_name} found in available models")
    
    # Optionally test inference
    if test_inference:
        try:
            logger.info(f"Testing inference with model {model_name}...")
            result = subprocess.run(
                ["ollama", "run", model_name, "Say 'OK'"],
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            
            logger.info(f"Model {model_name} validated successfully")
            logger.debug(f"Inference output: {result.stdout}")
            return True
        
        except subprocess.TimeoutExpired:
            logger.error(f"Model {model_name} validation timed out")
            return False
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Model {model_name} inference test failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
        
        except Exception as e:
            logger.error(f"Model {model_name} validation failed: {e}")
            return False
    
    return True


def main() -> int:
    """Main entry point for the script.
    
    Returns:
        Exit code (0 if all models valid, 1 if any invalid)
    """
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
    
    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())

