"""Unified LLM factory for creating Ollama and OpenAI LLM instances.

This module provides a unified factory pattern for creating LLM instances
from multiple providers (Ollama and OpenAI) with seamless switching via
environment variables. Defaults to OpenAI gpt-4o-mini for cost optimization.
"""

import os
import logging
from typing import Optional, Literal, Union

from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI

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
        Model name (default: 'gpt-4o-mini' - cheapest OpenAI model)
        Note: gpt-4o-mini is currently the most cost-effective OpenAI model.
    """
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from environment variable.
    
    Returns:
        API key or None if not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not found in environment variables")
    return api_key


def create_openai_llm(
    model: Optional[str] = None,
    temperature: float = 0.7,
    **kwargs
) -> ChatOpenAI:
    """Create OpenAI LLM instance.
    
    Args:
        model: Model name (defaults to OPENAI_MODEL env var or 'gpt-4o-mini')
        temperature: Temperature for generation (default: 0.7)
        **kwargs: Additional arguments for ChatOpenAI
    
    Returns:
        ChatOpenAI instance
    
    Raises:
        ValueError: If OPENAI_API_KEY is not set
    
    Example:
        ```python
        from langchain_ollama_integration import create_openai_llm
        
        llm = create_openai_llm(model="gpt-4o-mini")
        result = llm.invoke("Hello, world!")
        ```
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
        
        # Use default (OpenAI gpt-4o-mini - cheapest)
        llm = create_llm()
        
        # Explicitly use OpenAI
        llm = create_llm(provider="openai", model="gpt-4o-mini")
        
        # Explicitly use Ollama
        llm = create_llm(provider="ollama", model="llama3.2:latest")
        
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
                raise RuntimeError(
                    "Auto mode failed: OpenAI error and fallback disabled"
                )
    
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
        raise ValueError(
            f"Invalid provider: {provider}. Must be 'ollama', 'openai', or 'auto'"
        )


def get_llm() -> Union[OllamaLLM, ChatOpenAI]:
    """Get default LLM instance using configuration.
    
    Returns:
        Default LLM instance based on LLM_PROVIDER env var
        Default: OpenAI gpt-4o-mini (cheapest option)
    """
    return create_llm()

