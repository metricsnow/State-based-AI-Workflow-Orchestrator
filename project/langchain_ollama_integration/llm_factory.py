"""LLM factory for creating Ollama LLM instances with correct imports."""

import os
import logging
from typing import Optional

from langchain_ollama import OllamaLLM  # CORRECT import

logger = logging.getLogger(__name__)


def get_ollama_base_url() -> str:
    """Get Ollama base URL from environment.
    
    Returns:
        Base URL string. Uses service name in Docker, localhost for local development.
    """
    # Use service name in Docker, localhost for local development
    if os.getenv("DOCKER_ENV") == "true":
        return "http://ollama:11434"
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def get_ollama_model() -> str:
    """Get Ollama model from environment.
    
    Returns:
        Model name string. Defaults to "llama2:13b" if not set.
    """
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

