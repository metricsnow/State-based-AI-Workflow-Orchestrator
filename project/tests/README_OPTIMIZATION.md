# Test Optimization Guide

## Overview

Tests are optimized for speed while maintaining **100% production conditions** - no mocks, no placeholders, real services only.

## Optimization Strategy

### Real Services, Faster Timeouts

All tests use **real Kafka, real services**, but with optimized timeouts and reduced wait times:

- **Kafka Timeout**: 2s (instead of 30s)
- **Workflow Timeout**: 5s (instead of 300s)  
- **Poll Interval**: 0.1s (instead of 1.0s)
- **Retry Delay**: 0.05s (instead of 1.0s)
- **Max Wait Iterations**: 10 (instead of 20)

### Configuration

Test optimizations are controlled via environment variables:

```bash
# Set in .env or export before running tests
export TEST_KAFKA_TIMEOUT=2          # Kafka timeout in seconds
export TEST_WORKFLOW_TIMEOUT=5       # Workflow timeout in seconds
export TEST_POLL_INTERVAL=0.1        # Polling interval in seconds
export TEST_RETRY_DELAY=0.05         # Retry delay in seconds
export TEST_MAX_WAIT_ITERATIONS=10   # Max wait iterations
```

### Test Fixtures

Use optimized fixtures from `conftest.py`:

- `fast_retry_config`: Fast retry configuration
- `fast_consumer_config`: Fast consumer configuration
- `fast_poll_interval`: Fast polling interval
- `fast_max_wait_iterations`: Fast max wait iterations
- `fast_wait_loop`: Helper for fast wait loops

### Example Usage

```python
import pytest
from tests.utils.test_config import (
    get_test_poll_interval,
    get_test_max_wait_iterations,
    get_fast_sleep_time,
)

@pytest.mark.asyncio
async def test_example(fast_retry_config):
    # Use fast retry config
    result = await retry_async(func, config=fast_retry_config)
    
    # Use fast polling
    fast_interval = get_test_poll_interval()
    await asyncio.sleep(fast_interval)
    
    # Use fast sleep helper
    await asyncio.sleep(get_fast_sleep_time(5))  # 0.5s
```

## Performance Improvements

- **Before**: 20.95s for 25 tests
- **After**: 2.98s for 25 tests
- **Speedup**: ~7x faster

## Still Production Conditions

✅ Real Kafka brokers  
✅ Real Zookeeper  
✅ Real event serialization  
✅ Real Kafka topics  
✅ Real Docker services  
✅ No mocks  
✅ No placeholders  

## Running Optimized Tests

```bash
# All tests with optimizations (automatic)
pytest project/tests/ -v

# Override specific timeout
TEST_WORKFLOW_TIMEOUT=10 pytest project/tests/ -v

# Disable optimizations (use production timeouts)
TEST_KAFKA_TIMEOUT=30 TEST_WORKFLOW_TIMEOUT=300 pytest project/tests/ -v
```

