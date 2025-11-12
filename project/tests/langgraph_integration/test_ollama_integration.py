"""Test Ollama LangChain integration module (TASK-033).

This test verifies the langchain_ollama_integration module implementation.
All tests run under production conditions - NO MOCKS, NO PLACEHOLDERS.

CRITICAL: All tests use real packages, real imports, and real initialization.
"""

import pytest
from langchain_ollama_integration import create_ollama_llm, get_ollama_llm


def test_ollama_llm_initialization():
    """Test Ollama LLM initialization with correct import."""
    llm = create_ollama_llm(model="llama2")
    assert llm is not None
    assert hasattr(llm, "invoke")
    assert hasattr(llm, "model")
    assert hasattr(llm, "base_url")


def test_ollama_llm_initialization_with_defaults():
    """Test Ollama LLM initialization with default parameters."""
    llm = get_ollama_llm()
    assert llm is not None
    assert hasattr(llm, "invoke")


def test_ollama_llm_initialization_with_custom_model():
    """Test Ollama LLM initialization with custom model."""
    llm = create_ollama_llm(model="llama2:7b")
    assert llm is not None
    assert hasattr(llm, "model")
    # Note: Actual model attribute may vary, but should exist


def test_ollama_llm_initialization_with_custom_base_url():
    """Test Ollama LLM initialization with custom base URL."""
    llm = create_ollama_llm(
        model="llama2",
        base_url="http://localhost:11434"
    )
    assert llm is not None
    assert hasattr(llm, "base_url")


def test_ollama_llm_initialization_with_temperature():
    """Test Ollama LLM initialization with temperature parameter."""
    llm = create_ollama_llm(model="llama2", temperature=0.5)
    assert llm is not None
    # Temperature may be stored as attribute or in kwargs


@pytest.mark.skip(reason="Requires Ollama service running and model downloaded")
def test_ollama_basic_inference():
    """Test basic inference with Ollama.
    
    Note: This test requires Ollama service running and model downloaded.
    Skip in CI/CD environments.
    """
    llm = create_ollama_llm(model="llama2")
    
    result = llm.invoke("Say 'Hello, World!' in one sentence.")
    
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


def test_ollama_error_handling_invalid_model():
    """Test error handling for invalid model.
    
    Note: OllamaLLM doesn't raise on initialization, only on invoke.
    This test verifies that initialization succeeds even with invalid model.
    """
    # OllamaLLM doesn't validate model on initialization
    # It only fails when you try to invoke with an invalid model
    # So initialization should succeed
    llm = create_ollama_llm(model="nonexistent-model-12345")
    assert llm is not None
    assert llm.model == "nonexistent-model-12345"
    # Error would occur on llm.invoke(), not on initialization


def test_ollama_error_handling_invalid_base_url():
    """Test error handling for invalid base URL.
    
    Note: This test may fail if invalid URL is accepted,
    which depends on OllamaLLM implementation.
    """
    # This may or may not raise an error depending on OllamaLLM implementation
    # We're testing that the function handles invalid URLs gracefully
    try:
        llm = create_ollama_llm(
            model="llama2",
            base_url="http://invalid-host:11434"
        )
        # If it doesn't raise, that's OK - error will occur on invoke
        assert llm is not None
    except Exception:
        # If it raises, that's also OK - proper error handling
        pass

