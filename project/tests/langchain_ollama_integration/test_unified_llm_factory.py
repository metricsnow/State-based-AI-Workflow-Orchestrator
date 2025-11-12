"""Production tests for unified LLM factory with Ollama and OpenAI support.

This test suite validates the unified LLM factory implementation using PRODUCTION conditions only.
NO MOCKS, NO PLACEHOLDERS - all tests use real LLM instances.

CRITICAL: All tests use real packages, real imports, and real initialization.

IMPORTANT: OpenAI tests are DISABLED BY DEFAULT to prevent API costs during automatic testing.
To enable OpenAI tests (for manual/production testing only):
  export ENABLE_OPENAI_TESTS=true
  pytest project/tests/langchain_ollama_integration/test_unified_llm_factory.py

TASK-038: Create Unified LLM Factory with Model Toggle (Ollama/OpenAI)
"""

import os
import socket
import time

import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from langchain_ollama_integration import (
    create_llm,
    create_ollama_llm,
    create_openai_llm,
    get_llm,
    get_llm_provider,
    get_openai_model,
    get_ollama_model,
)


def get_fastest_test_model() -> str:
    """Get the fastest available model for tests.
    
    Returns:
        Model name string. Uses fastest available model for test execution.
        Override with TEST_OLLAMA_MODEL env var if needed.
    """
    test_model = os.getenv("TEST_OLLAMA_MODEL")
    if test_model:
        return test_model
    
    # Use fastest small model for quick tests
    return "gemma3:1b"


def check_ollama_available() -> bool:
    """Check if Ollama service is available (fast check without LLM call)."""
    try:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        if "localhost" in base_url or "127.0.0.1" in base_url:
            host = "localhost"
            port = 11434
        else:
            # Extract host and port from URL
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 11434
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_openai_available() -> bool:
    """Check if OpenAI API key is available and tests are enabled.
    
    OpenAI tests are disabled by default to prevent API costs during automatic testing.
    Set ENABLE_OPENAI_TESTS=true to enable OpenAI tests (for manual/production testing only).
    """
    # Check if OpenAI tests are explicitly enabled
    enable_tests = os.getenv("ENABLE_OPENAI_TESTS", "false").lower() == "true"
    if not enable_tests:
        return False
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    return api_key is not None and api_key != "" and api_key != "your_openai_api_key_here"


class TestProviderSelection:
    """Tests for LLM provider selection logic (no mocks - real functions only)."""

    def test_get_llm_provider_default(self):
        """Test default provider is OpenAI."""
        print("\n[TEST] Testing default provider selection...")
        start_time = time.time()
        
        # Save original value
        original = os.getenv("LLM_PROVIDER")
        try:
            # Clear LLM_PROVIDER to test default
            if "LLM_PROVIDER" in os.environ:
                del os.environ["LLM_PROVIDER"]
            
            provider = get_llm_provider()
            elapsed = time.time() - start_time
            
            assert provider == "openai"
            print(f"[PASS] Default provider is OpenAI (took {elapsed:.3f}s)")
        finally:
            # Restore original value
            if original:
                os.environ["LLM_PROVIDER"] = original

    def test_get_llm_provider_ollama(self):
        """Test provider selection for Ollama."""
        print("\n[TEST] Testing Ollama provider selection...")
        start_time = time.time()
        
        original = os.getenv("LLM_PROVIDER")
        try:
            os.environ["LLM_PROVIDER"] = "ollama"
            provider = get_llm_provider()
            elapsed = time.time() - start_time
            
            assert provider == "ollama"
            print(f"[PASS] Provider selection works for Ollama (took {elapsed:.3f}s)")
        finally:
            if original:
                os.environ["LLM_PROVIDER"] = original
            elif "LLM_PROVIDER" in os.environ:
                del os.environ["LLM_PROVIDER"]

    def test_get_llm_provider_openai(self):
        """Test provider selection for OpenAI."""
        print("\n[TEST] Testing OpenAI provider selection...")
        start_time = time.time()
        
        original = os.getenv("LLM_PROVIDER")
        try:
            os.environ["LLM_PROVIDER"] = "openai"
            provider = get_llm_provider()
            elapsed = time.time() - start_time
            
            assert provider == "openai"
            print(f"[PASS] Provider selection works for OpenAI (took {elapsed:.3f}s)")
        finally:
            if original:
                os.environ["LLM_PROVIDER"] = original
            elif "LLM_PROVIDER" in os.environ:
                del os.environ["LLM_PROVIDER"]

    def test_get_llm_provider_auto(self):
        """Test provider selection for auto mode."""
        print("\n[TEST] Testing auto provider selection...")
        start_time = time.time()
        
        original = os.getenv("LLM_PROVIDER")
        try:
            os.environ["LLM_PROVIDER"] = "auto"
            provider = get_llm_provider()
            elapsed = time.time() - start_time
            
            assert provider == "auto"
            print(f"[PASS] Provider selection works for auto mode (took {elapsed:.3f}s)")
        finally:
            if original:
                os.environ["LLM_PROVIDER"] = original
            elif "LLM_PROVIDER" in os.environ:
                del os.environ["LLM_PROVIDER"]


class TestOpenAIConfiguration:
    """Tests for OpenAI configuration functions (no mocks)."""

    def test_get_openai_model_default(self):
        """Test default OpenAI model is gpt-4o-mini (cheapest)."""
        print("\n[TEST] Testing default OpenAI model...")
        start_time = time.time()
        
        original = os.getenv("OPENAI_MODEL")
        try:
            if "OPENAI_MODEL" in os.environ:
                del os.environ["OPENAI_MODEL"]
            
            model = get_openai_model()
            elapsed = time.time() - start_time
            
            assert model == "gpt-4o-mini"
            print(f"[PASS] Default OpenAI model is gpt-4o-mini (cheapest) (took {elapsed:.3f}s)")
        finally:
            if original:
                os.environ["OPENAI_MODEL"] = original

    def test_get_openai_model_custom(self):
        """Test custom OpenAI model from environment."""
        print("\n[TEST] Testing custom OpenAI model...")
        start_time = time.time()
        
        original = os.getenv("OPENAI_MODEL")
        try:
            os.environ["OPENAI_MODEL"] = "gpt-4o-mini"
            model = get_openai_model()
            elapsed = time.time() - start_time
            
            assert model == "gpt-4o-mini"
            print(f"[PASS] Custom OpenAI model retrieved correctly (took {elapsed:.3f}s)")
        finally:
            if original:
                os.environ["OPENAI_MODEL"] = original
            elif "OPENAI_MODEL" in os.environ:
                del os.environ["OPENAI_MODEL"]


class TestOllamaLLMCreation:
    """Tests for Ollama LLM creation (PRODUCTION - real instances)."""

    def test_create_ollama_llm_real(self):
        """Test Ollama LLM creation with real instance."""
        print("\n[TEST] Testing real Ollama LLM creation...")
        start_time = time.time()
        
        if not check_ollama_available():
            print("[SKIP] Ollama service not available")
            pytest.skip("Ollama service not available")
        
        print("[STATUS] Ollama service available - creating real LLM instance...")
        llm = create_ollama_llm(model=get_fastest_test_model())
        
        elapsed = time.time() - start_time
        assert llm is not None
        assert hasattr(llm, "invoke")
        print(f"[PASS] Real Ollama LLM created successfully (took {elapsed:.3f}s)")

    def test_create_ollama_llm_inference(self):
        """Test Ollama LLM with real inference."""
        print("\n[TEST] Testing real Ollama LLM inference...")
        start_time = time.time()
        
        if not check_ollama_available():
            print("[SKIP] Ollama service not available")
            pytest.skip("Ollama service not available")
        
        print("[STATUS] Creating real Ollama LLM and testing inference...")
        llm = create_ollama_llm(model=get_fastest_test_model())
        
        inference_start = time.time()
        result = llm.invoke("Say OK")
        inference_time = time.time() - inference_start
        
        total_time = time.time() - start_time
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        print(f"[PASS] Real inference successful: '{result[:30]}...' (inference: {inference_time:.3f}s, total: {total_time:.3f}s)")


class TestOpenAILLMCreation:
    """Tests for OpenAI LLM creation (PRODUCTION - real instances)."""

    def test_create_openai_llm_missing_api_key(self):
        """Test OpenAI LLM creation fails without API key."""
        print("\n[TEST] Testing OpenAI LLM creation without API key...")
        start_time = time.time()
        
        original = os.getenv("OPENAI_API_KEY")
        try:
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            
            with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
                create_openai_llm()
            
            elapsed = time.time() - start_time
            print(f"[PASS] Correctly raises error without API key (took {elapsed:.3f}s)")
        finally:
            if original:
                os.environ["OPENAI_API_KEY"] = original

    def test_create_openai_llm_real(self):
        """Test OpenAI LLM creation with real instance (if API key available and tests enabled).
        
        NOTE: OpenAI tests are disabled by default to prevent API costs.
        Set ENABLE_OPENAI_TESTS=true to enable (for manual/production testing only).
        """
        print("\n[TEST] Testing real OpenAI LLM creation...")
        start_time = time.time()
        
        if not check_openai_available():
            print("[SKIP] OpenAI tests disabled by default (set ENABLE_OPENAI_TESTS=true to enable)")
            pytest.skip("OpenAI tests disabled to prevent API costs. Set ENABLE_OPENAI_TESTS=true to enable.")
        
        print("[STATUS] OpenAI API key available - creating real LLM instance...")
        llm = create_openai_llm()
        
        elapsed = time.time() - start_time
        assert llm is not None
        assert hasattr(llm, "invoke")
        print(f"[PASS] Real OpenAI LLM created successfully (took {elapsed:.3f}s)")

    def test_create_openai_llm_inference(self):
        """Test OpenAI LLM with real inference (if API key available and tests enabled).
        
        NOTE: OpenAI tests are disabled by default to prevent API costs.
        Set ENABLE_OPENAI_TESTS=true to enable (for manual/production testing only).
        """
        print("\n[TEST] Testing real OpenAI LLM inference...")
        start_time = time.time()
        
        if not check_openai_available():
            print("[SKIP] OpenAI tests disabled by default (set ENABLE_OPENAI_TESTS=true to enable)")
            pytest.skip("OpenAI tests disabled to prevent API costs. Set ENABLE_OPENAI_TESTS=true to enable.")
        
        print("[STATUS] Creating real OpenAI LLM and testing inference...")
        llm = create_openai_llm()
        
        inference_start = time.time()
        result = llm.invoke("Say OK")
        inference_time = time.time() - inference_start
        
        total_time = time.time() - start_time
        assert result is not None
        assert hasattr(result, "content") or isinstance(result, str)
        print(f"[PASS] Real inference successful (inference: {inference_time:.3f}s, total: {total_time:.3f}s)")


class TestUnifiedFactory:
    """Tests for unified LLM factory function (PRODUCTION - real instances)."""

    def test_create_llm_explicit_ollama(self):
        """Test unified factory with explicit Ollama provider (PRODUCTION)."""
        print("\n[TEST] Testing unified factory with explicit Ollama...")
        start_time = time.time()
        
        if not check_ollama_available():
            print("[SKIP] Ollama service not available")
            pytest.skip("Ollama service not available")
        
        print("[STATUS] Creating LLM with explicit Ollama provider...")
        llm = create_llm(provider="ollama", model=get_fastest_test_model())
        
        elapsed = time.time() - start_time
        assert llm is not None
        assert hasattr(llm, "invoke")
        print(f"[PASS] Unified factory with Ollama works (took {elapsed:.3f}s)")

    def test_create_llm_explicit_ollama_inference(self):
        """Test unified factory Ollama with real inference."""
        print("\n[TEST] Testing unified factory Ollama inference...")
        start_time = time.time()
        
        if not check_ollama_available():
            print("[SKIP] Ollama service not available")
            pytest.skip("Ollama service not available")
        
        print("[STATUS] Creating LLM and testing inference...")
        llm = create_llm(provider="ollama", model=get_fastest_test_model())
        
        inference_start = time.time()
        result = llm.invoke("Say OK")
        inference_time = time.time() - inference_start
        
        total_time = time.time() - start_time
        assert result is not None
        assert isinstance(result, str)
        print(f"[PASS] Unified factory Ollama inference successful (inference: {inference_time:.3f}s, total: {total_time:.3f}s)")

    def test_create_llm_explicit_openai(self):
        """Test unified factory with explicit OpenAI provider (PRODUCTION).
        
        NOTE: OpenAI tests are disabled by default to prevent API costs.
        Set ENABLE_OPENAI_TESTS=true to enable (for manual/production testing only).
        """
        print("\n[TEST] Testing unified factory with explicit OpenAI...")
        start_time = time.time()
        
        if not check_openai_available():
            print("[SKIP] OpenAI tests disabled by default (set ENABLE_OPENAI_TESTS=true to enable)")
            pytest.skip("OpenAI tests disabled to prevent API costs. Set ENABLE_OPENAI_TESTS=true to enable.")
        
        print("[STATUS] Creating LLM with explicit OpenAI provider...")
        llm = create_llm(provider="openai")
        
        elapsed = time.time() - start_time
        assert llm is not None
        assert hasattr(llm, "invoke")
        print(f"[PASS] Unified factory with OpenAI works (took {elapsed:.3f}s)")

    def test_create_llm_explicit_openai_inference(self):
        """Test unified factory OpenAI with real inference.
        
        NOTE: OpenAI tests are disabled by default to prevent API costs.
        Set ENABLE_OPENAI_TESTS=true to enable (for manual/production testing only).
        """
        print("\n[TEST] Testing unified factory OpenAI inference...")
        start_time = time.time()
        
        if not check_openai_available():
            print("[SKIP] OpenAI tests disabled by default (set ENABLE_OPENAI_TESTS=true to enable)")
            pytest.skip("OpenAI tests disabled to prevent API costs. Set ENABLE_OPENAI_TESTS=true to enable.")
        
        print("[STATUS] Creating LLM and testing inference...")
        llm = create_llm(provider="openai")
        
        inference_start = time.time()
        result = llm.invoke("Say OK")
        inference_time = time.time() - inference_start
        
        total_time = time.time() - start_time
        assert result is not None
        print(f"[PASS] Unified factory OpenAI inference successful (inference: {inference_time:.3f}s, total: {total_time:.3f}s)")

    def test_create_llm_auto_mode_ollama_fallback(self):
        """Test auto mode falls back to Ollama when OpenAI not available."""
        print("\n[TEST] Testing auto mode fallback to Ollama...")
        start_time = time.time()
        
        if not check_ollama_available():
            print("[SKIP] Ollama service not available")
            pytest.skip("Ollama service not available")
        
        # Ensure OpenAI is not available
        original_key = os.getenv("OPENAI_API_KEY")
        try:
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            
            print("[STATUS] Testing auto mode with OpenAI unavailable...")
            llm = create_llm(provider="auto", model=get_fastest_test_model())
            
            elapsed = time.time() - start_time
            assert llm is not None
            assert hasattr(llm, "invoke")
            print(f"[PASS] Auto mode correctly fell back to Ollama (took {elapsed:.3f}s)")
        finally:
            if original_key:
                os.environ["OPENAI_API_KEY"] = original_key

    def test_create_llm_invalid_provider(self):
        """Test unified factory raises error for invalid provider."""
        print("\n[TEST] Testing invalid provider error handling...")
        start_time = time.time()
        
        with pytest.raises(ValueError, match="Invalid provider"):
            create_llm(provider="invalid")
        
        elapsed = time.time() - start_time
        print(f"[PASS] Correctly raises error for invalid provider (took {elapsed:.3f}s)")

    def test_get_llm_convenience_function(self):
        """Test get_llm convenience function (PRODUCTION)."""
        print("\n[TEST] Testing get_llm convenience function...")
        start_time = time.time()
        
        # Test with Ollama if available (faster than OpenAI)
        if check_ollama_available():
            original = os.getenv("LLM_PROVIDER")
            try:
                os.environ["LLM_PROVIDER"] = "ollama"
                llm = get_llm()
                elapsed = time.time() - start_time
                assert llm is not None
                print(f"[PASS] get_llm works with Ollama (took {elapsed:.3f}s)")
            finally:
                if original:
                    os.environ["LLM_PROVIDER"] = original
                elif "LLM_PROVIDER" in os.environ:
                    del os.environ["LLM_PROVIDER"]
        else:
            print("[SKIP] Ollama not available, skipping get_llm test")
            pytest.skip("Ollama service not available")


class TestBackwardCompatibility:
    """Tests for backward compatibility with existing Ollama code (PRODUCTION)."""

    def test_create_ollama_llm_still_works(self):
        """Test existing create_ollama_llm function still works."""
        print("\n[TEST] Testing backward compatibility - create_ollama_llm...")
        start_time = time.time()
        
        if not check_ollama_available():
            print("[SKIP] Ollama service not available")
            pytest.skip("Ollama service not available")
        
        llm = create_ollama_llm(model=get_fastest_test_model())
        elapsed = time.time() - start_time
        
        assert llm is not None
        assert hasattr(llm, "invoke")
        print(f"[PASS] create_ollama_llm still works (took {elapsed:.3f}s)")

    def test_get_ollama_model_still_works(self):
        """Test existing get_ollama_model function still works."""
        print("\n[TEST] Testing backward compatibility - get_ollama_model...")
        start_time = time.time()
        
        original = os.getenv("OLLAMA_MODEL")
        try:
            os.environ["OLLAMA_MODEL"] = "test-model"
            model = get_ollama_model()
            elapsed = time.time() - start_time
            
            assert model == "test-model"
            print(f"[PASS] get_ollama_model still works (took {elapsed:.3f}s)")
        finally:
            if original:
                os.environ["OLLAMA_MODEL"] = original
            elif "OLLAMA_MODEL" in os.environ:
                del os.environ["OLLAMA_MODEL"]
