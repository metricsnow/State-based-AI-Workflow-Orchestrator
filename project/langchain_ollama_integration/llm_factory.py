"""LLM factory for creating Ollama LLM instances with correct imports."""

import os
import logging
from typing import Optional

from langchain_ollama import OllamaLLM  # CORRECT import

logger = logging.getLogger(__name__)


def get_ollama_base_url() -> str:
    """Get Ollama base URL from environment.
    
    Returns:
        Base URL string. Defaults to localhost (local Ollama instance).
        Set OLLAMA_BASE_URL env var to override, or DOCKER_ENV=true for Docker service name.
    """
    # Check for explicit override first
    if os.getenv("OLLAMA_BASE_URL"):
        return os.getenv("OLLAMA_BASE_URL")
    
    # Use Docker service name only if explicitly in Docker environment
    if os.getenv("DOCKER_ENV") == "true":
        return "http://ollama:11434"
    
    # Default to localhost (local Ollama instance) for all projects
    return "http://localhost:11434"


def get_ollama_model() -> str:
    """Get Ollama model from environment.
    
    Returns:
        Model name string. Defaults to "llama3.2:latest" if not set (available in local Ollama).
        Local models available: llama3.2:latest, qwen2.5vl:7b, magistral:24b, phi4-reasoning:14b,
        qwen3:14b, qwen3:32b, phi4-mini:3.8b, mistral-small3.2:24b, devstral:24b, granite4:latest,
        deepseek-r1:32b, gpt-oss:20b, embeddinggemma:300m, qwen3-embedding:8b
    """
    return os.getenv("OLLAMA_MODEL", "llama3.2:latest")


def create_ollama_llm(
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.7,
    **kwargs
) -> OllamaLLM:
    """Create Ollama LLM instance with correct import.
    
    Args:
        model: Model name (defaults to OLLAMA_MODEL env var or "llama2")
        base_url: Ollama base URL (defaults to OLLAMA_BASE_URL env var)
        temperature: Temperature for generation (default: 0.7)
        **kwargs: Additional arguments for OllamaLLM
    
    Returns:
        OllamaLLM instance
    
    Raises:
        Exception: If LLM creation fails
    
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
    """Get default Ollama LLM instance.
    
    Returns:
        Default OllamaLLM instance using environment configuration
    """
    return create_ollama_llm()

