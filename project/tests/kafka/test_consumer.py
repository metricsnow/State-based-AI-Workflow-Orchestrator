"""
Tests for Kafka consumer implementation.

Tests cover:
- Consumer initialization and configuration
- Event consumption functionality
- Error handling and deserialization
- Consumer group support
- Offset management
- Connection management
"""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest
from kafka.errors import KafkaError, KafkaTimeoutError
from kafka.structs import TopicPartition
from kafka.consumer.fetcher import ConsumerRecord

from workflow_events import (
    EventType,
    EventSource,
    WorkflowEvent,
    WorkflowEventPayload,
    WorkflowEventMetadata,
    WorkflowEventConsumer,
)


class TestConsumerInitialization:
    """Test consumer initialization and configuration."""

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_consumer_initialization_defaults(self, mock_kafka_consumer):
        """Test consumer initialization with default parameters."""
        mock_consumer_instance = MagicMock()
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer()

        mock_kafka_consumer.assert_called_once()
        call_kwargs = mock_kafka_consumer.call_args[1]
        assert call_kwargs["bootstrap_servers"] == ["localhost:9092"]
        assert call_kwargs["auto_offset_reset"] == "earliest"
        assert call_kwargs["enable_auto_commit"] is True
        assert call_kwargs["consumer_timeout_ms"] == 1000
        assert "value_deserializer" in call_kwargs
        assert "group_id" not in call_kwargs
        assert consumer.bootstrap_servers == "localhost:9092"
        assert consumer.consumer == mock_consumer_instance

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_consumer_initialization_custom_servers(self, mock_kafka_consumer):
        """Test consumer initialization with custom bootstrap servers."""
        mock_consumer_instance = MagicMock()
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer(bootstrap_servers="kafka:9092")

        call_kwargs = mock_kafka_consumer.call_args[1]
        assert call_kwargs["bootstrap_servers"] == ["kafka:9092"]
        assert consumer.bootstrap_servers == "kafka:9092"

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_consumer_initialization_with_group_id(self, mock_kafka_consumer):
        """Test consumer initialization with consumer group."""
        mock_consumer_instance = MagicMock()
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer(group_id="test-group")

        call_kwargs = mock_kafka_consumer.call_args[1]
        assert call_kwargs["group_id"] == "test-group"
        assert consumer.group_id == "test-group"

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_consumer_initialization_custom_config(self, mock_kafka_consumer):
        """Test consumer initialization with custom configuration."""
        mock_consumer_instance = MagicMock()
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer(
            bootstrap_servers="kafka:9092",
            group_id="test-group",
            auto_offset_reset="latest",
            enable_auto_commit=False,
            consumer_timeout_ms=5000,
            max_poll_records=100,
        )

        call_kwargs = mock_kafka_consumer.call_args[1]
        assert call_kwargs["auto_offset_reset"] == "latest"
        assert call_kwargs["enable_auto_commit"] is False
        assert call_kwargs["consumer_timeout_ms"] == 5000
        assert call_kwargs["max_poll_records"] == 100

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_consumer_initialization_connection_failure(self, mock_kafka_consumer):
        """Test consumer initialization with connection failure."""
        mock_kafka_consumer.side_effect = KafkaError("Connection failed")

        with pytest.raises(KafkaError) as exc_info:
            WorkflowEventConsumer()

        assert "Failed to connect to Kafka" in str(exc_info.value)


class TestEventDeserialization:
    """Test event deserialization."""

    def test_deserialize_event(self):
        """Test event deserialization from JSON bytes."""
        event_dict = {
            "event_id": "123e4567-e89b-12d3-a456-426614174000",
            "event_type": "workflow.completed",
            "timestamp": "2025-01-27T10:00:00",
            "source": "airflow",
            "workflow_id": "test_dag",
            "workflow_run_id": "run_123",
            "payload": {"data": {"status": "success"}},
            "metadata": {"environment": "dev", "version": "1.0"},
        }

        json_bytes = json.dumps(event_dict).encode("utf-8")
        deserialized = WorkflowEventConsumer._deserialize_event(json_bytes)

        assert deserialized["event_type"] == "workflow.completed"
        assert deserialized["workflow_id"] == "test_dag"

    def test_deserialize_event_invalid_json(self):
        """Test deserialization with invalid JSON raises error."""
        invalid_json = b"not valid json"

        with pytest.raises(ValueError) as exc_info:
            WorkflowEventConsumer._deserialize_event(invalid_json)

        assert "Failed to deserialize event" in str(exc_info.value)

    def test_deserialize_event_invalid_encoding(self):
        """Test deserialization with invalid encoding raises error."""
        invalid_bytes = b"\xff\xfe\x00\x01"  # Invalid UTF-8

        with pytest.raises(ValueError) as exc_info:
            WorkflowEventConsumer._deserialize_event(invalid_bytes)

        assert "Failed to deserialize event" in str(exc_info.value)


class TestTopicSubscription:
    """Test topic subscription."""

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_subscribe_topics(self, mock_kafka_consumer):
        """Test subscribing to topics."""
        mock_consumer_instance = MagicMock()
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer()
        consumer.subscribe(["workflow-events", "test-topic"])

        mock_consumer_instance.subscribe.assert_called_once_with(
            ["workflow-events", "test-topic"]
        )

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_subscribe_not_connected(self, mock_kafka_consumer):
        """Test subscribing when consumer is not connected."""
        mock_consumer_instance = MagicMock()
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer()
        consumer.consumer = None  # Simulate disconnected state

        with pytest.raises(KafkaError) as exc_info:
            consumer.subscribe(["workflow-events"])

        assert "Consumer not connected" in str(exc_info.value)

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_subscribe_error(self, mock_kafka_consumer):
        """Test subscribe error handling."""
        mock_consumer_instance = MagicMock()
        mock_consumer_instance.subscribe.side_effect = Exception("Subscribe failed")
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer()

        with pytest.raises(KafkaError) as exc_info:
            consumer.subscribe(["workflow-events"])

        assert "Failed to subscribe to topics" in str(exc_info.value)


class TestEventConsumption:
    """Test event consumption functionality."""

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_consume_events_success(self, mock_kafka_consumer):
        """Test successful event consumption."""
        # Setup mocks
        mock_consumer_instance = MagicMock()
        mock_message = Mock(spec=ConsumerRecord)
        mock_message.topic = "workflow-events"
        mock_message.partition = 0
        mock_message.offset = 123
        mock_message.value = {
            "event_id": "123e4567-e89b-12d3-a456-426614174000",
            "event_type": "workflow.completed",
            "timestamp": "2025-01-27T10:00:00",
            "source": "airflow",
            "workflow_id": "test_dag",
            "workflow_run_id": "run_123",
            "payload": {"data": {"status": "success"}},
            "metadata": {"environment": "dev", "version": "1.0"},
        }

        # Mock iterator behavior
        mock_consumer_instance.__iter__ = Mock(return_value=iter([mock_message]))
        mock_consumer_instance.__next__ = Mock(return_value=mock_message)
        mock_kafka_consumer.return_value = mock_consumer_instance

        # Create consumer and callback
        consumer = WorkflowEventConsumer()
        callback_called = []

        def callback(event: WorkflowEvent):
            callback_called.append(event)

        # Consume events (will stop after one message due to iterator)
        try:
            consumer.consume_events(callback, ["workflow-events"])
        except StopIteration:
            pass  # Expected when iterator is exhausted

        # Verify callback was called
        assert len(callback_called) == 1
        assert callback_called[0].event_type == EventType.WORKFLOW_COMPLETED
        assert callback_called[0].workflow_id == "test_dag"

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_consume_events_deserialization_error(self, mock_kafka_consumer):
        """Test event consumption with deserialization error."""
        mock_consumer_instance = MagicMock()
        mock_message = Mock(spec=ConsumerRecord)
        mock_message.topic = "workflow-events"
        mock_message.partition = 0
        mock_message.offset = 123
        mock_message.value = {"invalid": "event"}  # Missing required fields

        mock_consumer_instance.__iter__ = Mock(return_value=iter([mock_message]))
        mock_consumer_instance.__next__ = Mock(return_value=mock_message)
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer()
        callback_called = []

        def callback(event: WorkflowEvent):
            callback_called.append(event)

        # Should continue processing despite deserialization error
        try:
            consumer.consume_events(callback, ["workflow-events"])
        except StopIteration:
            pass

        # Callback should not be called due to validation error
        assert len(callback_called) == 0

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_consume_events_callback_error(self, mock_kafka_consumer):
        """Test event consumption with callback error."""
        mock_consumer_instance = MagicMock()
        mock_message = Mock(spec=ConsumerRecord)
        mock_message.topic = "workflow-events"
        mock_message.partition = 0
        mock_message.offset = 123
        mock_message.value = {
            "event_id": "123e4567-e89b-12d3-a456-426614174000",
            "event_type": "workflow.completed",
            "timestamp": "2025-01-27T10:00:00",
            "source": "airflow",
            "workflow_id": "test_dag",
            "workflow_run_id": "run_123",
            "payload": {"data": {"status": "success"}},
            "metadata": {"environment": "dev", "version": "1.0"},
        }

        mock_consumer_instance.__iter__ = Mock(return_value=iter([mock_message]))
        mock_consumer_instance.__next__ = Mock(return_value=mock_message)
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer()

        def callback(event: WorkflowEvent):
            raise ValueError("Callback error")

        # Should continue processing despite callback error
        try:
            consumer.consume_events(callback, ["workflow-events"])
        except StopIteration:
            pass

        # Should not raise exception, just log error

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_consume_events_not_connected(self, mock_kafka_consumer):
        """Test consuming when consumer is not connected."""
        mock_consumer_instance = MagicMock()
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer()
        consumer.consumer = None  # Simulate disconnected state

        def callback(event: WorkflowEvent):
            pass

        with pytest.raises(KafkaError) as exc_info:
            consumer.consume_events(callback, ["workflow-events"])

        assert "Consumer not connected" in str(exc_info.value)


class TestPolling:
    """Test polling functionality."""

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_poll(self, mock_kafka_consumer):
        """Test polling for messages."""
        mock_consumer_instance = MagicMock()
        mock_message = Mock(spec=ConsumerRecord)
        mock_tp = TopicPartition("workflow-events", 0)
        mock_consumer_instance.poll.return_value = {mock_tp: [mock_message]}
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer()
        result = consumer.poll(timeout_ms=1000)

        mock_consumer_instance.poll.assert_called_once_with(timeout_ms=1000)
        assert result == {mock_tp: [mock_message]}

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_poll_not_connected(self, mock_kafka_consumer):
        """Test polling when consumer is not connected."""
        mock_consumer_instance = MagicMock()
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer()
        consumer.consumer = None

        with pytest.raises(KafkaError) as exc_info:
            consumer.poll()

        assert "Consumer not connected" in str(exc_info.value)


class TestOffsetManagement:
    """Test offset management."""

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_commit(self, mock_kafka_consumer):
        """Test committing offsets."""
        mock_consumer_instance = MagicMock()
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer()
        consumer.commit()

        mock_consumer_instance.commit.assert_called_once()

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_commit_with_offsets(self, mock_kafka_consumer):
        """Test committing specific offsets."""
        from kafka.structs import OffsetAndMetadata

        mock_consumer_instance = MagicMock()
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer()
        tp = TopicPartition("workflow-events", 0)
        offsets = {tp: OffsetAndMetadata(offset=100, metadata="processed", leader_epoch=None)}
        consumer.commit(offsets=offsets)

        mock_consumer_instance.commit.assert_called_once_with(offsets=offsets)

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_seek(self, mock_kafka_consumer):
        """Test seeking to specific offset."""
        mock_consumer_instance = MagicMock()
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer()
        tp = TopicPartition("workflow-events", 0)
        consumer.seek(tp, 100)

        mock_consumer_instance.seek.assert_called_once_with(tp, 100)

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_position(self, mock_kafka_consumer):
        """Test getting current position."""
        mock_consumer_instance = MagicMock()
        mock_consumer_instance.position.return_value = 150
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer()
        tp = TopicPartition("workflow-events", 0)
        position = consumer.position(tp)

        assert position == 150
        mock_consumer_instance.position.assert_called_once_with(tp)


class TestConnectionManagement:
    """Test connection management."""

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_close(self, mock_kafka_consumer):
        """Test closing consumer connection."""
        mock_consumer_instance = MagicMock()
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer()
        consumer.close()

        mock_consumer_instance.close.assert_called_once()
        assert consumer.consumer is None

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_close_with_timeout(self, mock_kafka_consumer):
        """Test closing with timeout."""
        mock_consumer_instance = MagicMock()
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer()
        consumer.close(timeout_ms=5000)

        mock_consumer_instance.close.assert_called_once_with(timeout_ms=5000)

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_close_with_error(self, mock_kafka_consumer):
        """Test close handles errors gracefully."""
        mock_consumer_instance = MagicMock()
        mock_consumer_instance.close.side_effect = Exception("Close error")
        mock_kafka_consumer.return_value = mock_consumer_instance

        consumer = WorkflowEventConsumer()
        consumer.close()

        # Should still set consumer to None
        assert consumer.consumer is None

    @patch("workflow_events.consumer.KafkaConsumer")
    def test_context_manager(self, mock_kafka_consumer):
        """Test consumer as context manager."""
        mock_consumer_instance = MagicMock()
        mock_kafka_consumer.return_value = mock_consumer_instance

        with WorkflowEventConsumer() as consumer:
            assert consumer.consumer is not None

        # Should be closed after context exit
        mock_consumer_instance.close.assert_called_once()


class TestConsumerIntegration:
    """Integration tests for consumer (require real Kafka)."""

    @pytest.mark.integration
    def test_consume_event_from_kafka(self):
        """Test consuming event from real Kafka instance."""
        # This test requires a running Kafka instance
        # Run with: pytest -m integration
        consumer = WorkflowEventConsumer(
            bootstrap_servers="localhost:9092", group_id="test-consumer-group"
        )

        events_received = []

        def callback(event: WorkflowEvent):
            events_received.append(event)

        try:
            # This will timeout after consumer_timeout_ms
            consumer.consume_events(callback, ["workflow-events"], timeout_ms=5000)
        except StopIteration:
            pass  # Expected on timeout
        finally:
            # Ensure consumer is closed
            consumer.close()

        # Verify consumer closed properly
        assert consumer.consumer is None

