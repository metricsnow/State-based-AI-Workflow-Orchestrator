"""Retry utility with exponential backoff for async operations.

This module provides retry mechanisms with exponential backoff and jitter
for handling transient errors in async Kafka operations and workflow processing.
"""

import asyncio
import logging
import random
from typing import Callable, TypeVar, Optional

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry mechanism.
    
    Attributes:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        max_delay: Maximum delay in seconds between retries (default: 60.0)
        exponential_base: Base for exponential backoff calculation (default: 2.0)
        jitter: Whether to add random jitter to delay (default: True)
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """Initialize retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds before first retry
            max_delay: Maximum delay in seconds between retries
            exponential_base: Base for exponential backoff calculation
            jitter: Whether to add random jitter to delay
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


def is_transient_error(exception: Exception) -> bool:
    """Determine if error is transient (retryable).
    
    Transient errors are typically network-related issues that may resolve
    on retry, such as connection errors, timeouts, and temporary OS errors.
    
    Args:
        exception: Exception to check
        
    Returns:
        True if error is transient and should be retried, False otherwise
    """
    transient_errors = (
        ConnectionError,
        TimeoutError,
        OSError,
        asyncio.TimeoutError,
    )
    
    # Check exception type
    if isinstance(exception, transient_errors):
        return True
    
    # Check exception name for Kafka-specific errors
    error_name = type(exception).__name__
    transient_error_names = (
        'KafkaTimeoutError',
        'KafkaConnectionError',
        'NetworkError',
    )
    
    if any(name in error_name for name in transient_error_names):
        return True
    
    return False


async def retry_async(
    func: Callable[..., T],
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs
) -> T:
    """Retry async function with exponential backoff.
    
    Retries an async function with exponential backoff and optional jitter.
    Only retries on transient errors; permanent errors are raised immediately.
    
    Args:
        func: Async function to retry
        *args: Positional arguments for the function
        config: RetryConfig instance. If None, uses default configuration
        **kwargs: Keyword arguments for the function
        
    Returns:
        Return value from the function
        
    Raises:
        Exception: Last exception encountered if all retries are exhausted
    """
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(config.max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            # Don't retry if not transient error
            if not is_transient_error(e):
                logger.error(
                    f"Non-transient error, not retrying: {type(e).__name__}: {e}"
                )
                raise
            
            # Don't retry on last attempt
            if attempt >= config.max_retries:
                logger.error(
                    f"Max retries ({config.max_retries}) exceeded: "
                    f"{type(e).__name__}: {e}",
                    exc_info=True
                )
                raise
            
            # Calculate delay with exponential backoff
            delay = min(
                config.initial_delay * (config.exponential_base ** attempt),
                config.max_delay
            )
            
            # Add jitter to avoid thundering herd problem
            if config.jitter:
                delay = delay * (0.5 + random.random() * 0.5)
            
            logger.warning(
                f"Retry attempt {attempt + 1}/{config.max_retries} "
                f"after {delay:.2f}s: {type(e).__name__}: {e}"
            )
            
            await asyncio.sleep(delay)
    
    # Should not reach here, but handle just in case
    if last_exception:
        raise last_exception
    raise RuntimeError("Retry failed without exception")

