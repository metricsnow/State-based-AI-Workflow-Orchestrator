"""Unit tests for retry utility with exponential backoff."""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from langgraph_integration.retry import (
    retry_async,
    RetryConfig,
    is_transient_error,
)


class TestRetryConfig:
    """Tests for RetryConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = RetryConfig(
            max_retries=5,
            initial_delay=2.0,
            max_delay=120.0,
            exponential_base=3.0,
            jitter=False
        )
        assert config.max_retries == 5
        assert config.initial_delay == 2.0
        assert config.max_delay == 120.0
        assert config.exponential_base == 3.0
        assert config.jitter is False


class TestIsTransientError:
    """Tests for error classification."""
    
    def test_transient_errors(self):
        """Test that transient errors are identified correctly."""
        assert is_transient_error(ConnectionError("Connection failed")) is True
        assert is_transient_error(TimeoutError("Timeout")) is True
        assert is_transient_error(OSError("OS error")) is True
        assert is_transient_error(asyncio.TimeoutError()) is True
    
    def test_permanent_errors(self):
        """Test that permanent errors are identified correctly."""
        assert is_transient_error(ValueError("Invalid value")) is False
        assert is_transient_error(KeyError("Missing key")) is False
        assert is_transient_error(TypeError("Wrong type")) is False
    
    def test_kafka_error_names(self):
        """Test Kafka-specific error name detection."""
        class KafkaTimeoutError(Exception):
            pass
        
        class KafkaConnectionError(Exception):
            pass
        
        assert is_transient_error(KafkaTimeoutError("Timeout")) is True
        assert is_transient_error(KafkaConnectionError("Connection failed")) is True


class TestRetryAsync:
    """Tests for retry_async function."""
    
    @pytest.mark.asyncio
    async def test_successful_call_no_retry(self):
        """Test that successful calls don't retry."""
        call_count = 0
        
        async def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await retry_async(successful_func)
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_on_transient_error(self):
        """Test retry on transient error."""
        call_count = 0
        
        async def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Connection failed")
            return "success"
        
        config = RetryConfig(max_retries=3, initial_delay=0.1, jitter=False)
        result = await retry_async(failing_then_success, config=config)
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test that max retries are respected."""
        call_count = 0
        
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Connection failed")
        
        config = RetryConfig(max_retries=2, initial_delay=0.1, jitter=False)
        
        with pytest.raises(ConnectionError):
            await retry_async(always_fails, config=config)
        
        assert call_count == 3  # Initial + 2 retries
    
    @pytest.mark.asyncio
    async def test_non_transient_error_no_retry(self):
        """Test that non-transient errors don't retry."""
        call_count = 0
        
        async def permanent_failure():
            nonlocal call_count
            call_count += 1
            raise ValueError("Invalid value")
        
        config = RetryConfig(max_retries=3, initial_delay=0.1)
        
        with pytest.raises(ValueError):
            await retry_async(permanent_failure, config=config)
        
        assert call_count == 1  # No retries for permanent errors
    
    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test exponential backoff delay calculation."""
        delays = []
        
        async def record_delay():
            # This will be called by asyncio.sleep
            pass
        
        call_count = 0
        
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Connection failed")
            return "success"
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            config = RetryConfig(
                max_retries=3,
                initial_delay=1.0,
                exponential_base=2.0,
                jitter=False
            )
            await retry_async(failing_func, config=config)
            
            # Should have 2 retries (attempts 2 and 3)
            assert mock_sleep.call_count == 2
            # First retry: 1.0 * 2^0 = 1.0
            # Second retry: 1.0 * 2^1 = 2.0
            assert mock_sleep.call_args_list[0][0][0] == 1.0
            assert mock_sleep.call_args_list[1][0][0] == 2.0
    
    @pytest.mark.asyncio
    async def test_max_delay_cap(self):
        """Test that delays are capped at max_delay."""
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            call_count = 0
            
            async def failing_func():
                nonlocal call_count
                call_count += 1
                if call_count < 2:
                    raise ConnectionError("Connection failed")
                return "success"
            
            config = RetryConfig(
                max_retries=3,
                initial_delay=100.0,  # Large initial delay
                max_delay=10.0,  # But capped at 10.0
                exponential_base=2.0,
                jitter=False
            )
            await retry_async(failing_func, config=config)
            
            # Delay should be capped at max_delay
            assert mock_sleep.call_args_list[0][0][0] <= 10.0
    
    @pytest.mark.asyncio
    async def test_jitter(self):
        """Test that jitter adds randomness to delays."""
        delays = []
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            call_count = 0
            
            async def failing_func():
                nonlocal call_count
                call_count += 1
                if call_count < 2:
                    raise ConnectionError("Connection failed")
                return "success"
            
            config = RetryConfig(
                max_retries=3,
                initial_delay=1.0,
                exponential_base=2.0,
                jitter=True  # Enable jitter
            )
            await retry_async(failing_func, config=config)
            
            # With jitter, delay should be between 0.5 and 1.0 times base delay
            delay = mock_sleep.call_args_list[0][0][0]
            assert 0.5 <= delay <= 1.0
    
    @pytest.mark.asyncio
    async def test_function_with_args_and_kwargs(self):
        """Test retry with function arguments."""
        async def func_with_args(arg1, arg2, kwarg1=None):
            if arg1 == "fail":
                raise ConnectionError("Connection failed")
            return f"{arg1}-{arg2}-{kwarg1}"
        
        config = RetryConfig(max_retries=1, initial_delay=0.1, jitter=False)
        
        # First call fails, second succeeds
        call_count = 0
        original_func = func_with_args
        
        async def mock_func(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Connection failed")
            return await original_func(*args, **kwargs)
        
        result = await retry_async(
            mock_func,
            "success",
            "arg2",
            kwarg1="kwarg1",
            config=config
        )
        assert result == "success-arg2-kwarg1"
        assert call_count == 2

