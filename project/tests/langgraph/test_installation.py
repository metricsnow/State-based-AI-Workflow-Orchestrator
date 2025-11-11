"""Test that all required packages can be imported and meet version requirements.

This test verifies the LangGraph development environment setup (TASK-014).
"""

import sys
from importlib import import_module
from importlib.metadata import version

import pytest


def test_core_package_imports() -> None:
    """Test that all required core packages can be imported."""
    packages = [
        "langgraph",
        "langchain",
        "langchain_core",
        "pydantic",
        "typing_extensions",
    ]

    for package in packages:
        try:
            import_module(package)
        except ImportError as e:
            pytest.fail(f"Failed to import {package}: {e}")


def test_langgraph_components() -> None:
    """Test that specific LangGraph components can be imported."""
    try:
        from langgraph.graph import StateGraph, START, END
        from langgraph.checkpoint.memory import InMemorySaver

        # Verify components are callable/importable
        assert StateGraph is not None
        assert START is not None
        assert END is not None
        assert InMemorySaver is not None
    except ImportError as e:
        pytest.fail(f"Failed to import LangGraph components: {e}")


def test_package_versions() -> None:
    """Test that installed packages meet minimum version requirements."""
    from packaging import version as version_parser

    # Check LangGraph version
    langgraph_version_str = version("langgraph")
    langgraph_version = version_parser.parse(langgraph_version_str)
    assert langgraph_version >= version_parser.parse(
        "0.6.0"
    ), f"langgraph version {langgraph_version_str} < 0.6.0"

    # Check LangChain version
    langchain_version_str = version("langchain")
    langchain_version = version_parser.parse(langchain_version_str)
    assert langchain_version >= version_parser.parse(
        "0.2.0"
    ), f"langchain version {langchain_version_str} < 0.2.0"

    # Check LangChain Core version
    langchain_core_version_str = version("langchain-core")
    langchain_core_version = version_parser.parse(langchain_core_version_str)
    assert langchain_core_version >= version_parser.parse(
        "0.2.0"
    ), f"langchain-core version {langchain_core_version_str} < 0.2.0"

    # Check Pydantic version
    pydantic_version_str = version("pydantic")
    pydantic_version = version_parser.parse(pydantic_version_str)
    assert pydantic_version >= version_parser.parse(
        "2.0.0"
    ), f"pydantic version {pydantic_version_str} < 2.0.0"

    # Check typing-extensions version
    typing_extensions_version_str = version("typing-extensions")
    typing_extensions_version = version_parser.parse(typing_extensions_version_str)
    assert typing_extensions_version >= version_parser.parse(
        "4.8.0"
    ), f"typing-extensions version {typing_extensions_version_str} < 4.8.0"


def test_development_dependencies() -> None:
    """Test that development dependencies are available."""
    try:
        import pytest
        import pytest_asyncio
        import black
        import mypy

        # Verify they're importable
        assert pytest is not None
        assert pytest_asyncio is not None
        assert black is not None
        assert mypy is not None
    except ImportError as e:
        pytest.fail(f"Failed to import development dependency: {e}")


def test_virtual_environment() -> None:
    """Test that we're running in a virtual environment."""
    # Check if Python executable is in a venv directory
    python_path = sys.executable
    assert "venv" in python_path or ".venv" in python_path, (
        f"Not running in virtual environment. Python path: {python_path}"
    )

