"""
Shared pytest fixtures for all test modules.

This module provides common fixtures used across all test modules,
including path fixtures, DAG fixtures, and test data fixtures.
"""
import os
import pytest
from pathlib import Path
from airflow.models import DagBag


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def root_directory() -> Path:
    """Return the repository root directory (parent of project/)."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def dags_folder(project_root) -> Path:
    """Return the DAGs folder path."""
    return project_root / "dags"


@pytest.fixture(scope="session")
def dag_bag(dags_folder) -> DagBag:
    """
    Create a DagBag instance for testing.
    
    This fixture loads all DAGs from the dags folder and makes
    them available for testing. It's scoped to session to avoid
    reloading DAGs for each test.
    """
    return DagBag(dag_folder=str(dags_folder), include_examples=False)


@pytest.fixture
def sample_extracted_data() -> dict:
    """Fixture providing sample extracted data for testing."""
    return {'data': [1, 2, 3, 4, 5]}


@pytest.fixture
def sample_transformed_data() -> dict:
    """Fixture providing sample transformed data for testing."""
    return {'transformed_data': [2, 4, 6, 8, 10]}

