"""Unit tests for dead letter queue."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from langgraph_integration.dead_letter import DeadLetterQueue


class TestDeadLetterQueue:
    """Tests for DeadLetterQueue class."""
    
    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Test starting and stopping the DLQ producer."""
        dlq = DeadLetterQueue(
            bootstrap_servers="localhost:9092",
            topic="test-dlq"
        )
        
        with patch('langgraph_integration.dead_letter.AIOKafkaProducer') as mock_producer_class:
            mock_producer = AsyncMock()
            mock_producer_class.return_value = mock_producer
            
            await dlq.start()
            assert dlq.producer is not None
            mock_producer.start.assert_called_once()
            
            await dlq.stop()
            mock_producer.stop.assert_called_once()
            assert dlq.producer is None
    
    @pytest.mark.asyncio
    async def test_publish_failed_event(self):
        """Test publishing a failed event to DLQ."""
        dlq = DeadLetterQueue(
            bootstrap_servers="localhost:9092",
            topic="test-dlq"
        )
        
        with patch('langgraph_integration.dead_letter.AIOKafkaProducer') as mock_producer_class:
            mock_producer = AsyncMock()
            mock_metadata = MagicMock()
            mock_metadata.topic = "test-dlq"
            mock_metadata.partition = 0
            mock_metadata.offset = 123
            mock_producer.send_and_wait.return_value = mock_metadata
            mock_producer_class.return_value = mock_producer
            
            await dlq.start()
            
            original_event = {
                "event_id": "test-event-123",
                "workflow_id": "test-workflow",
                "event_type": "WORKFLOW_TRIGGERED"
            }
            error = ConnectionError("Connection failed")
            
            await dlq.publish_failed_event(
                original_event=original_event,
                error=error,
                retry_count=3,
                context={"workflow_id": "test-workflow"}
            )
            
            # Verify send_and_wait was called
            mock_producer.send_and_wait.assert_called_once()
            call_args = mock_producer.send_and_wait.call_args
            
            # Verify topic
            assert call_args[0][0] == "test-dlq"
            
            # Verify DLQ event structure
            dlq_event = call_args[0][1]
            assert "dlq_id" in dlq_event
            assert "timestamp" in dlq_event
            assert dlq_event["original_event"] == original_event
            assert dlq_event["error"]["type"] == "ConnectionError"
            assert dlq_event["error"]["message"] == "Connection failed"
            assert dlq_event["retry_count"] == 3
            assert dlq_event["context"]["workflow_id"] == "test-workflow"
            
            await dlq.stop()
    
    @pytest.mark.asyncio
    async def test_publish_failed_event_not_started(self):
        """Test that publishing fails if producer not started."""
        dlq = DeadLetterQueue(
            bootstrap_servers="localhost:9092",
            topic="test-dlq"
        )
        
        original_event = {"event_id": "test-event-123"}
        error = ConnectionError("Connection failed")
        
        with pytest.raises(RuntimeError, match="not started"):
            await dlq.publish_failed_event(
                original_event=original_event,
                error=error,
                retry_count=3
            )
    
    @pytest.mark.asyncio
    async def test_publish_failed_event_kafka_error(self):
        """Test handling of Kafka errors during publish."""
        dlq = DeadLetterQueue(
            bootstrap_servers="localhost:9092",
            topic="test-dlq"
        )
        
        with patch('langgraph_integration.dead_letter.AIOKafkaProducer') as mock_producer_class:
            from aiokafka.errors import KafkaError
            
            mock_producer = AsyncMock()
            mock_producer.send_and_wait.side_effect = KafkaError("Kafka error")
            mock_producer_class.return_value = mock_producer
            
            await dlq.start()
            
            original_event = {"event_id": "test-event-123"}
            error = ConnectionError("Connection failed")
            
            with pytest.raises(KafkaError):
                await dlq.publish_failed_event(
                    original_event=original_event,
                    error=error,
                    retry_count=3
                )
            
            await dlq.stop()
    
    @pytest.mark.asyncio
    async def test_environment_variable_defaults(self):
        """Test that environment variables are used for defaults."""
        import os
        
        with patch.dict(os.environ, {
            "KAFKA_BOOTSTRAP_SERVERS": "env-bootstrap:9092",
            "KAFKA_DLQ_TOPIC": "env-dlq-topic"
        }):
            dlq = DeadLetterQueue()
            assert dlq.bootstrap_servers == "env-bootstrap:9092"
            assert dlq.topic == "env-dlq-topic"
    
    def test_custom_configuration(self):
        """Test custom configuration overrides."""
        dlq = DeadLetterQueue(
            bootstrap_servers="custom-bootstrap:9092",
            topic="custom-dlq-topic"
        )
        assert dlq.bootstrap_servers == "custom-bootstrap:9092"
        assert dlq.topic == "custom-dlq-topic"
    
    @pytest.mark.asyncio
    async def test_stop_handles_errors_gracefully(self):
        """Test that stop handles errors gracefully."""
        dlq = DeadLetterQueue(
            bootstrap_servers="localhost:9092",
            topic="test-dlq"
        )
        
        with patch('langgraph_integration.dead_letter.AIOKafkaProducer') as mock_producer_class:
            mock_producer = AsyncMock()
            mock_producer.stop.side_effect = Exception("Stop error")
            mock_producer_class.return_value = mock_producer
            
            await dlq.start()
            
            # Should not raise exception
            await dlq.stop()
            
            # Producer should still be None after error
            assert dlq.producer is None

