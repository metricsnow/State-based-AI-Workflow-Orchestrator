"""
Shared pytest fixtures for all test modules.

This module provides common fixtures used across all test modules,
including path fixtures, DAG fixtures, and test data fixtures.

OPTIMIZED FOR TESTING: Uses real services with faster timeouts for speed.
All tests still use production conditions (real Kafka, real services),
but with optimized timeouts and reduced wait times.
"""
import os
import pytest
from pathlib import Path
from airflow.models import DagBag

# Test-optimized settings (still production, just faster)
# These can be overridden via environment variables
TEST_KAFKA_TIMEOUT = int(os.getenv("TEST_KAFKA_TIMEOUT", "2"))  # 2s instead of 30s
TEST_WORKFLOW_TIMEOUT = int(os.getenv("TEST_WORKFLOW_TIMEOUT", "5"))  # 5s instead of 300s
TEST_POLL_INTERVAL = float(os.getenv("TEST_POLL_INTERVAL", "0.1"))  # 0.1s instead of 1.0s
TEST_RETRY_DELAY = float(os.getenv("TEST_RETRY_DELAY", "0.05"))  # 0.05s instead of 1.0s
TEST_MAX_WAIT_ITERATIONS = int(os.getenv("TEST_MAX_WAIT_ITERATIONS", "10"))  # 10 instead of 20


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


# ============================================================================
# OPTIMIZED TEST FIXTURES - Real services with faster timeouts
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def set_test_environment_variables():
    """Set test-optimized environment variables for all tests.
    
    Uses real services but with faster timeouts for speed.
    Still production conditions, just optimized for testing.
    """
    # Store original values
    original_values = {}
    test_vars = {
        "WORKFLOW_EXECUTION_TIMEOUT": str(TEST_WORKFLOW_TIMEOUT),
        "KAFKA_REQUEST_TIMEOUT_MS": str(TEST_KAFKA_TIMEOUT * 1000),
        "KAFKA_CONSUMER_TIMEOUT_MS": str(TEST_KAFKA_TIMEOUT * 1000),
    }
    
    # Save originals
    for key, value in test_vars.items():
        original_values[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield
    
    # Restore originals
    for key, original_value in original_values.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture(scope="session")
def test_kafka_bootstrap_servers():
    """Kafka bootstrap servers for testing (real Kafka, optimized settings)."""
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


@pytest.fixture
def fast_retry_config():
    """Fast retry configuration for tests (still production, just faster)."""
    from langgraph_integration.retry import RetryConfig
    
    return RetryConfig(
        max_retries=2,  # Reduced from 3 for speed
        initial_delay=TEST_RETRY_DELAY,  # 0.05s instead of 1.0s
        max_delay=5.0,  # Reduced from 60.0s
        exponential_base=2.0,
        jitter=False,  # Disable jitter for predictable timing in tests
    )


@pytest.fixture
def fast_consumer_config(test_kafka_bootstrap_servers):
    """Fast consumer configuration for tests (real Kafka, optimized timeouts)."""
    from langgraph_integration.config import ConsumerConfig
    from uuid import uuid4
    
    return ConsumerConfig(
        bootstrap_servers=test_kafka_bootstrap_servers,
        topic=f"test-topic-{uuid4().hex[:8]}",
        group_id=f"test-group-{uuid4().hex[:8]}",
        auto_offset_reset="earliest",
        session_timeout_ms=TEST_KAFKA_TIMEOUT * 1000,  # Faster timeout (2s)
        heartbeat_interval_ms=1000,  # Faster heartbeat (1s)
        max_poll_records=10,  # Smaller batches for faster processing
    )


@pytest.fixture
def fast_poll_interval():
    """Fast polling interval for result polling tests."""
    return TEST_POLL_INTERVAL


@pytest.fixture
def fast_max_wait_iterations():
    """Fast max wait iterations for event processing tests."""
    return TEST_MAX_WAIT_ITERATIONS


@pytest.fixture
def fast_wait_loop(fast_poll_interval, fast_max_wait_iterations):
    """Helper fixture for fast wait loops in tests."""
    import asyncio
    
    async def wait_for_condition(condition_func, description="condition"):
        """Wait for condition with fast polling."""
        for i in range(fast_max_wait_iterations):
            if await condition_func() if asyncio.iscoroutinefunction(condition_func) else condition_func():
                return True
            await asyncio.sleep(fast_poll_interval)
        return False
    
    return wait_for_condition

