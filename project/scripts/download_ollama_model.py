#!/usr/bin/env python3
"""Script to download Ollama models.

This script downloads Ollama models using the Ollama CLI and validates
that the download was successful.

Usage:
    python download_ollama_model.py [model_name]

Examples:
    python download_ollama_model.py llama2:13b
    python download_ollama_model.py llama2:7b
"""

import subprocess
import sys
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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


def main() -> int:
    """Main entry point for the script.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    model = sys.argv[1] if len(sys.argv) > 1 else "llama2:13b"
    
    if download_model(model):
        if validate_model(model):
            print(f"Model {model} downloaded and validated successfully")
            return 0
        else:
            print(f"Model {model} downloaded but validation failed")
            return 1
    else:
        print(f"Failed to download model {model}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

