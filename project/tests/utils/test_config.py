"""
Test configuration utilities for optimized test execution.

Provides test-optimized settings that use real services but with faster timeouts.
All tests still use production conditions (real Kafka, real services),
but with optimized timeouts and reduced wait times for speed.
"""

import os
from typing import Optional


# Test-optimized settings (still production, just faster)
# These can be overridden via environment variables
TEST_KAFKA_TIMEOUT = int(os.getenv("TEST_KAFKA_TIMEOUT", "2"))  # 2s instead of 30s
TEST_WORKFLOW_TIMEOUT = int(os.getenv("TEST_WORKFLOW_TIMEOUT", "5"))  # 5s instead of 300s
TEST_POLL_INTERVAL = float(os.getenv("TEST_POLL_INTERVAL", "0.1"))  # 0.1s instead of 1.0s
TEST_RETRY_DELAY = float(os.getenv("TEST_RETRY_DELAY", "0.05"))  # 0.05s instead of 1.0s
TEST_MAX_WAIT_ITERATIONS = int(os.getenv("TEST_MAX_WAIT_ITERATIONS", "10"))  # 10 instead of 20


def get_test_kafka_timeout() -> int:
    """Get test-optimized Kafka timeout in seconds."""
    return TEST_KAFKA_TIMEOUT


def get_test_workflow_timeout() -> int:
    """Get test-optimized workflow execution timeout in seconds."""
    return TEST_WORKFLOW_TIMEOUT


def get_test_poll_interval() -> float:
    """Get test-optimized polling interval in seconds."""
    return TEST_POLL_INTERVAL


def get_test_retry_delay() -> float:
    """Get test-optimized retry delay in seconds."""
    return TEST_RETRY_DELAY


def get_test_max_wait_iterations() -> int:
    """Get test-optimized max wait iterations."""
    return TEST_MAX_WAIT_ITERATIONS


def get_fast_sleep_time(multiplier: float = 1.0) -> float:
    """Get fast sleep time for tests.
    
    Args:
        multiplier: Multiplier for base poll interval (default: 1.0)
    
    Returns:
        Sleep time in seconds
    """
    return TEST_POLL_INTERVAL * multiplier

