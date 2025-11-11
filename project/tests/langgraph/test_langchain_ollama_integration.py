"""Test langchain-ollama package integration (TASK-026).

This test verifies the langchain-ollama package installation and integration.
All tests run under production conditions - NO MOCKS, NO PLACEHOLDERS.

CRITICAL: All tests use real packages, real imports, and real initialization.
"""

import sys
from importlib import import_module
from importlib.metadata import version
from pathlib import Path

import pytest
from packaging import version as version_parser


def test_langchain_ollama_package_import() -> None:
    """Test that langchain-ollama package can be imported (PRODUCTION)."""
    try:
        langchain_ollama = import_module("langchain_ollama")
        assert langchain_ollama is not None, "langchain_ollama module is None"
    except ImportError as e:
        pytest.fail(f"Failed to import langchain_ollama package: {e}")


def test_ollama_llm_import_primary() -> None:
    """Test primary import path: from langchain_ollama import OllamaLLM (PRODUCTION)."""
    try:
        from langchain_ollama import OllamaLLM

        # Verify class is available and not None
        assert OllamaLLM is not None, "OllamaLLM class is None"
        assert callable(OllamaLLM), "OllamaLLM is not callable"
    except ImportError as e:
        pytest.fail(f"Failed to import OllamaLLM from langchain_ollama: {e}")


def test_ollama_llm_import_alternative() -> None:
    """Test alternative import path: from langchain_ollama.llms import OllamaLLM (PRODUCTION)."""
    try:
        from langchain_ollama.llms import OllamaLLM

        # Verify class is available and not None
        assert OllamaLLM is not None, "OllamaLLM class is None"
        assert callable(OllamaLLM), "OllamaLLM is not callable"
    except ImportError as e:
        pytest.fail(f"Failed to import OllamaLLM from langchain_ollama.llms: {e}")


def test_langchain_ollama_version_requirement() -> None:
    """Test that langchain-ollama meets minimum version requirement >=0.1.0 (PRODUCTION)."""
    try:
        langchain_ollama_version_str = version("langchain-ollama")
        langchain_ollama_version = version_parser.parse(langchain_ollama_version_str)
        min_version = version_parser.parse("0.1.0")

        assert langchain_ollama_version >= min_version, (
            f"langchain-ollama version {langchain_ollama_version_str} < 0.1.0"
        )
    except Exception as e:
        pytest.fail(f"Failed to check langchain-ollama version: {e}")


def test_ollama_llm_class_attributes() -> None:
    """Test that OllamaLLM class has expected attributes (PRODUCTION)."""
    from langchain_ollama import OllamaLLM

    # Verify class has expected attributes/methods
    assert hasattr(OllamaLLM, "__init__"), "OllamaLLM missing __init__"
    assert hasattr(OllamaLLM, "invoke"), "OllamaLLM missing invoke method"


def test_ollama_llm_initialization_minimal() -> None:
    """Test OllamaLLM initialization with minimal parameters (PRODUCTION - no mocks)."""
    from langchain_ollama import OllamaLLM

    # Initialize with real parameters (no mocks)
    # Note: This will fail if Ollama service is not running, but that's expected
    # We're testing that the class can be instantiated, not that it connects
    try:
        llm = OllamaLLM(
            model="llama2",
            base_url="http://localhost:11434",
        )

        # Verify instance is created
        assert llm is not None, "OllamaLLM instance is None"
        assert isinstance(llm, OllamaLLM), "Instance is not OllamaLLM type"

        # Verify attributes are set
        assert hasattr(llm, "model"), "OllamaLLM missing model attribute"
        assert hasattr(llm, "base_url"), "OllamaLLM missing base_url attribute"
    except Exception as e:
        # If Ollama service is not running, that's OK for this test
        # We're testing class instantiation, not service connectivity
        pytest.fail(f"Failed to initialize OllamaLLM: {e}")


def test_ollama_llm_initialization_with_temperature() -> None:
    """Test OllamaLLM initialization with temperature parameter (PRODUCTION - no mocks)."""
    from langchain_ollama import OllamaLLM

    # Initialize with temperature parameter (real initialization)
    try:
        llm = OllamaLLM(
            model="llama2",
            base_url="http://localhost:11434",
            temperature=0.7,
        )

        assert llm is not None, "OllamaLLM instance is None"
        assert hasattr(llm, "temperature"), "OllamaLLM missing temperature attribute"
    except Exception as e:
        pytest.fail(f"Failed to initialize OllamaLLM with temperature: {e}")


def test_ollama_dependency_installed() -> None:
    """Test that ollama dependency package is installed (PRODUCTION)."""
    try:
        ollama = import_module("ollama")
        assert ollama is not None, "ollama module is None"
    except ImportError as e:
        pytest.fail(f"Failed to import ollama dependency: {e}")


def test_requirements_txt_contains_langchain_ollama() -> None:
    """Test that requirements.txt contains langchain-ollama>=0.1.0 (PRODUCTION)."""
    # Get project root (assuming tests are in project/tests/)
    project_root = Path(__file__).parent.parent.parent.parent
    requirements_file = project_root / "requirements.txt"

    assert requirements_file.exists(), f"requirements.txt not found at {requirements_file}"

    # Read requirements.txt
    requirements_content = requirements_file.read_text()

    # Check for langchain-ollama entry
    assert "langchain-ollama" in requirements_content, (
        "langchain-ollama not found in requirements.txt"
    )

    # Check for version constraint >=0.1.0
    assert "langchain-ollama>=0.1.0" in requirements_content or (
        "langchain-ollama" in requirements_content and ">=0.1.0" in requirements_content
    ), "langchain-ollama version constraint >=0.1.0 not found in requirements.txt"


def test_langchain_compatibility() -> None:
    """Test that langchain-ollama is compatible with existing LangChain packages (PRODUCTION)."""
    # Import both packages to verify compatibility
    try:
        import langchain
        from langchain_ollama import OllamaLLM

        # Verify both can be imported together
        assert langchain is not None
        assert OllamaLLM is not None

        # Verify no import conflicts - check actual base class
        from langchain_core.language_models.llms import BaseLLM

        # OllamaLLM inherits from BaseLLM (verified via MRO inspection)
        assert issubclass(OllamaLLM, BaseLLM), "OllamaLLM is not a subclass of BaseLLM"

        # Verify it has the invoke method (LangChain interface)
        assert hasattr(OllamaLLM, "invoke"), "OllamaLLM missing invoke method"
    except ImportError as e:
        pytest.fail(f"LangChain compatibility check failed: {e}")


def test_no_dependency_conflicts() -> None:
    """Test that there are no dependency conflicts (PRODUCTION check)."""
    # Import all related packages to verify no conflicts
    try:
        import langchain
        import langchain_core
        from langchain_ollama import OllamaLLM
        import ollama

        # Verify all can coexist
        assert langchain is not None
        assert langchain_core is not None
        assert OllamaLLM is not None
        assert ollama is not None
    except ImportError as e:
        pytest.fail(f"Dependency conflict detected: {e}")


def test_virtual_environment_active() -> None:
    """Test that we're running in a virtual environment (PRODUCTION requirement)."""
    python_path = sys.executable
    assert "venv" in python_path or ".venv" in python_path, (
        f"Not running in virtual environment. Python path: {python_path}"
    )


def test_package_metadata() -> None:
    """Test that langchain-ollama package has proper metadata (PRODUCTION)."""
    try:
        langchain_ollama_version = version("langchain-ollama")
        assert langchain_ollama_version is not None
        assert len(langchain_ollama_version) > 0
    except Exception as e:
        pytest.fail(f"Failed to get langchain-ollama package metadata: {e}")

