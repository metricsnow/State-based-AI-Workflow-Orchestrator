"""Integration tests for error handling and retry mechanisms."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from workflow_events import WorkflowEvent, EventType, EventSource, WorkflowEventPayload, WorkflowEventMetadata
from langgraph_integration.consumer import LangGraphKafkaConsumer
from langgraph_integration.processor import WorkflowProcessor
from langgraph_integration.retry import RetryConfig
from langgraph_integration.dead_letter import DeadLetterQueue
from langgraph_integration.config import ConsumerConfig


class TestConsumerErrorHandling:
    """Integration tests for consumer error handling."""
    
    @pytest.mark.asyncio
    async def test_consumer_with_retry_and_dlq(self):
        """Test that consumer uses retry and DLQ for failed events."""
        config = ConsumerConfig(
            bootstrap_servers="localhost:9092",
            topic="test-topic",
            group_id="test-group"
        )
        
        consumer = LangGraphKafkaConsumer(config=config)
        
        # Verify retry config and DLQ are initialized
        assert consumer.retry_config is not None
        assert isinstance(consumer.retry_config, RetryConfig)
        assert consumer.dlq is not None
        assert isinstance(consumer.dlq, DeadLetterQueue)
    
    @pytest.mark.asyncio
    async def test_process_event_with_transient_error_retry(self):
        """Test that transient errors trigger retries."""
        config = ConsumerConfig(
            bootstrap_servers="localhost:9092",
            topic="test-topic",
            group_id="test-group"
        )
        
        consumer = LangGraphKafkaConsumer(config=config)
        
        # Create a mock processor that fails then succeeds
        call_count = 0
        
        async def mock_process(event):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Connection failed")
            return {"completed": True}
        
        consumer.processor.process_workflow_event = mock_process
        
        # Create test event
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test-workflow",
            workflow_run_id="test-run-123",
            payload=WorkflowEventPayload(data={"task": "test"}),
            metadata=WorkflowEventMetadata(environment="dev", version="1.0")
        )
        
        # Mock DLQ and result producer
        consumer.dlq.start = AsyncMock()
        consumer.dlq.stop = AsyncMock()
        consumer.dlq.publish_failed_event = AsyncMock()
        consumer.result_producer.start = AsyncMock()
        consumer.result_producer.stop = AsyncMock()
        consumer.result_producer.publish_result = AsyncMock()
        
        await consumer.dlq.start()
        await consumer.result_producer.start()
        
        # Process event - should succeed after retries
        result = await consumer._process_event_with_error_handling(event)
        assert result is not None
        assert call_count == 3  # Initial + 2 retries
        
        # DLQ should not be called (event succeeded)
        consumer.dlq.publish_failed_event.assert_not_called()
        
        await consumer.dlq.stop()
        await consumer.result_producer.stop()
    
    @pytest.mark.asyncio
    async def test_process_event_with_permanent_error_no_retry(self):
        """Test that permanent errors don't trigger retries."""
        config = ConsumerConfig(
            bootstrap_servers="localhost:9092",
            topic="test-topic",
            group_id="test-group"
        )
        
        consumer = LangGraphKafkaConsumer(config=config)
        
        # Create a mock processor that fails with permanent error
        call_count = 0
        
        async def mock_process(event):
            nonlocal call_count
            call_count += 1
            raise ValueError("Invalid value")
        
        consumer.processor.process_workflow_event = mock_process
        
        # Create test event
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test-workflow",
            workflow_run_id="test-run-123",
            payload=WorkflowEventPayload(data={"task": "test"}),
            metadata=WorkflowEventMetadata(environment="dev", version="1.0")
        )
        
        # Mock DLQ and result producer
        consumer.dlq.start = AsyncMock()
        consumer.dlq.stop = AsyncMock()
        consumer.dlq.publish_failed_event = AsyncMock()
        consumer.result_producer.start = AsyncMock()
        consumer.result_producer.stop = AsyncMock()
        consumer.result_producer.publish_result = AsyncMock()
        
        await consumer.dlq.start()
        await consumer.result_producer.start()
        
        # Process event - should fail immediately (no retries for permanent errors)
        await consumer._process_event_with_error_handling(event)
        
        # Should only be called once (no retries)
        assert call_count == 1
        
        # DLQ should be called
        consumer.dlq.publish_failed_event.assert_called_once()
        
        # Error result should be published
        consumer.result_producer.publish_result.assert_called_once()
        call_args = consumer.result_producer.publish_result.call_args
        assert call_args[1]["status"] == "error"
        
        await consumer.dlq.stop()
        await consumer.result_producer.stop()
    
    @pytest.mark.asyncio
    async def test_process_event_max_retries_exceeded_dlq(self):
        """Test that events are sent to DLQ after max retries exceeded."""
        config = ConsumerConfig(
            bootstrap_servers="localhost:9092",
            topic="test-topic",
            group_id="test-group"
        )
        
        consumer = LangGraphKafkaConsumer(config=config)
        consumer.retry_config = RetryConfig(max_retries=2, initial_delay=0.1, jitter=False)
        
        # Create a mock processor that always fails with transient error
        call_count = 0
        
        async def mock_process(event):
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Connection failed")
        
        consumer.processor.process_workflow_event = mock_process
        
        # Create test event
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test-workflow",
            workflow_run_id="test-run-123",
            payload=WorkflowEventPayload(data={"task": "test"}),
            metadata=WorkflowEventMetadata(environment="dev", version="1.0")
        )
        
        # Mock DLQ and result producer
        consumer.dlq.start = AsyncMock()
        consumer.dlq.stop = AsyncMock()
        consumer.dlq.publish_failed_event = AsyncMock()
        consumer.result_producer.start = AsyncMock()
        consumer.result_producer.stop = AsyncMock()
        consumer.result_producer.publish_result = AsyncMock()
        
        await consumer.dlq.start()
        await consumer.result_producer.start()
        
        # Process event - should fail after retries
        await consumer._process_event_with_error_handling(event)
        
        # Should be called max_retries + 1 times (initial + retries)
        assert call_count == 3  # Initial + 2 retries
        
        # DLQ should be called
        consumer.dlq.publish_failed_event.assert_called_once()
        dlq_call_args = consumer.dlq.publish_failed_event.call_args
        assert dlq_call_args[1]["retry_count"] == 2
        assert dlq_call_args[1]["error"].__class__.__name__ == "ConnectionError"
        
        # Error result should be published
        consumer.result_producer.publish_result.assert_called_once()
        call_args = consumer.result_producer.publish_result.call_args
        assert call_args[1]["status"] == "error"
        assert "retries" in call_args[1]["error"]
        
        await consumer.dlq.stop()
        await consumer.result_producer.stop()
    
    @pytest.mark.asyncio
    async def test_dlq_publish_failure_handled_gracefully(self):
        """Test that DLQ publish failures don't crash consumer."""
        config = ConsumerConfig(
            bootstrap_servers="localhost:9092",
            topic="test-topic",
            group_id="test-group"
        )
        
        consumer = LangGraphKafkaConsumer(config=config)
        
        # Create a mock processor that always fails
        async def mock_process(event):
            raise ConnectionError("Connection failed")
        
        consumer.processor.process_workflow_event = mock_process
        consumer.retry_config = RetryConfig(max_retries=0, initial_delay=0.1)
        
        # Create test event
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test-workflow",
            workflow_run_id="test-run-123",
            payload=WorkflowEventPayload(data={"task": "test"}),
            metadata=WorkflowEventMetadata(environment="dev", version="1.0")
        )
        
        # Mock DLQ to fail on publish
        consumer.dlq.start = AsyncMock()
        consumer.dlq.stop = AsyncMock()
        consumer.dlq.publish_failed_event = AsyncMock(side_effect=Exception("DLQ publish failed"))
        consumer.result_producer.start = AsyncMock()
        consumer.result_producer.stop = AsyncMock()
        consumer.result_producer.publish_result = AsyncMock()
        
        await consumer.dlq.start()
        await consumer.result_producer.start()
        
        # Process event - should handle DLQ failure gracefully
        await consumer._process_event_with_error_handling(event)
        
        # DLQ should have been called (and failed)
        consumer.dlq.publish_failed_event.assert_called_once()
        
        # Error result should still be published
        consumer.result_producer.publish_result.assert_called_once()
        
        await consumer.dlq.stop()
        await consumer.result_producer.stop()
    
    @pytest.mark.asyncio
    async def test_consumer_start_stop_with_dlq(self):
        """Test that consumer starts and stops DLQ properly."""
        config = ConsumerConfig(
            bootstrap_servers="localhost:9092",
            topic="test-topic",
            group_id="test-group"
        )
        
        consumer = LangGraphKafkaConsumer(config=config)
        
        # Mock all components
        consumer.consumer = AsyncMock()
        consumer.consumer.start = AsyncMock()
        consumer.consumer.stop = AsyncMock()
        consumer.result_producer.start = AsyncMock()
        consumer.result_producer.stop = AsyncMock()
        consumer.dlq.start = AsyncMock()
        consumer.dlq.stop = AsyncMock()
        
        # Start consumer
        await consumer.start()
        
        # Verify DLQ was started
        consumer.dlq.start.assert_called_once()
        consumer.result_producer.start.assert_called_once()
        
        # Stop consumer
        await consumer.stop()
        
        # Verify DLQ was stopped
        consumer.dlq.stop.assert_called_once()
        consumer.result_producer.stop.assert_called_once()

