"""
Shared pytest fixtures for all test modules.
"""
import os
import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def root_directory() -> Path:
    """Return the repository root directory (parent of project/)."""
    return Path(__file__).parent.parent.parent

