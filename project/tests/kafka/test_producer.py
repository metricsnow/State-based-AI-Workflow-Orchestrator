"""
Tests for Kafka producer implementation.

Tests cover:
- Producer initialization and configuration
- Event publishing functionality
- Error handling and retries
- Connection management
- Serialization
"""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest
from kafka.errors import KafkaError, KafkaTimeoutError

from workflow_events import (
    EventType,
    EventSource,
    WorkflowEvent,
    WorkflowEventPayload,
    WorkflowEventMetadata,
    WorkflowEventProducer,
)


class TestProducerInitialization:
    """Test producer initialization and configuration."""

    @patch("workflow_events.producer.KafkaProducer")
    def test_producer_initialization_defaults(self, mock_kafka_producer):
        """Test producer initialization with default parameters."""
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance

        producer = WorkflowEventProducer()

        mock_kafka_producer.assert_called_once()
        call_kwargs = mock_kafka_producer.call_args[1]
        assert call_kwargs["bootstrap_servers"] == ["localhost:9092"]
        assert call_kwargs["acks"] == "all"
        assert call_kwargs["retries"] == 3
        assert call_kwargs["max_in_flight_requests_per_connection"] == 1
        assert "value_serializer" in call_kwargs
        assert producer.bootstrap_servers == "localhost:9092"
        assert producer.producer == mock_producer_instance

    @patch("workflow_events.producer.KafkaProducer")
    def test_producer_initialization_custom_servers(self, mock_kafka_producer):
        """Test producer initialization with custom bootstrap servers."""
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance

        producer = WorkflowEventProducer(bootstrap_servers="kafka:9092")

        call_kwargs = mock_kafka_producer.call_args[1]
        assert call_kwargs["bootstrap_servers"] == ["kafka:9092"]
        assert producer.bootstrap_servers == "kafka:9092"

    @patch("workflow_events.producer.KafkaProducer")
    def test_producer_initialization_custom_config(self, mock_kafka_producer):
        """Test producer initialization with custom configuration."""
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance

        producer = WorkflowEventProducer(
            bootstrap_servers="kafka:9092",
            acks="1",
            retries=5,
            max_in_flight_requests_per_connection=2,
        )

        call_kwargs = mock_kafka_producer.call_args[1]
        assert call_kwargs["acks"] == "1"
        assert call_kwargs["retries"] == 5
        assert call_kwargs["max_in_flight_requests_per_connection"] == 2

    @patch("workflow_events.producer.KafkaProducer")
    def test_producer_initialization_connection_failure(self, mock_kafka_producer):
        """Test producer initialization with connection failure."""
        mock_kafka_producer.side_effect = KafkaError("Connection failed")

        with pytest.raises(KafkaError) as exc_info:
            WorkflowEventProducer()

        assert "Failed to connect to Kafka" in str(exc_info.value)


class TestEventSerialization:
    """Test event serialization."""

    def test_serialize_event(self):
        """Test event serialization to JSON bytes."""
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_COMPLETED,
            source=EventSource.AIRFLOW,
            workflow_id="test_dag",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(data={"status": "success"}),
            metadata=WorkflowEventMetadata(environment="dev"),
        )

        # Use the static method directly
        serialized = WorkflowEventProducer._serialize_event(event.model_dump())

        assert isinstance(serialized, bytes)
        deserialized = json.loads(serialized.decode("utf-8"))
        assert deserialized["event_type"] == "workflow.completed"
        assert deserialized["workflow_id"] == "test_dag"

    def test_serialize_event_invalid_data(self):
        """Test serialization with invalid data raises error."""
        # Create data that can't be serialized
        invalid_data = {"circular": {}}
        invalid_data["circular"] = invalid_data  # Circular reference

        with pytest.raises(ValueError) as exc_info:
            WorkflowEventProducer._serialize_event(invalid_data)

        assert "Failed to serialize event" in str(exc_info.value)


class TestEventPublishing:
    """Test event publishing functionality."""

    @patch("workflow_events.producer.KafkaProducer")
    def test_publish_event_success(self, mock_kafka_producer):
        """Test successful event publishing."""
        # Setup mocks
        mock_producer_instance = MagicMock()
        mock_future = MagicMock()
        mock_record_metadata = Mock()
        mock_record_metadata.topic = "workflow-events"
        mock_record_metadata.partition = 0
        mock_record_metadata.offset = 123
        mock_future.get.return_value = mock_record_metadata
        mock_producer_instance.send.return_value = mock_future
        mock_kafka_producer.return_value = mock_producer_instance

        # Create producer and event
        producer = WorkflowEventProducer()
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_COMPLETED,
            source=EventSource.AIRFLOW,
            workflow_id="test_dag",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(data={"status": "success"}),
            metadata=WorkflowEventMetadata(environment="dev"),
        )

        # Publish event
        result = producer.publish_event(event)

        assert result is True
        mock_producer_instance.send.assert_called_once()
        call_args = mock_producer_instance.send.call_args
        assert call_args[0][0] == "workflow-events"
        mock_future.get.assert_called_once_with(timeout=10)

    @patch("workflow_events.producer.KafkaProducer")
    def test_publish_event_custom_topic(self, mock_kafka_producer):
        """Test event publishing to custom topic."""
        mock_producer_instance = MagicMock()
        mock_future = MagicMock()
        mock_record_metadata = Mock()
        mock_record_metadata.topic = "custom-topic"
        mock_record_metadata.partition = 0
        mock_record_metadata.offset = 456
        mock_future.get.return_value = mock_record_metadata
        mock_producer_instance.send.return_value = mock_future
        mock_kafka_producer.return_value = mock_producer_instance

        producer = WorkflowEventProducer()
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test_dag",
            workflow_run_id="run_456",
            payload=WorkflowEventPayload(data={"status": "triggered"}),
            metadata=WorkflowEventMetadata(environment="dev"),
        )

        result = producer.publish_event(event, topic="custom-topic")

        assert result is True
        call_args = mock_producer_instance.send.call_args
        assert call_args[0][0] == "custom-topic"

    @patch("workflow_events.producer.KafkaProducer")
    def test_publish_event_timeout(self, mock_kafka_producer):
        """Test event publishing with timeout error."""
        mock_producer_instance = MagicMock()
        mock_future = MagicMock()
        mock_future.get.side_effect = KafkaTimeoutError("Timeout")
        mock_producer_instance.send.return_value = mock_future
        mock_kafka_producer.return_value = mock_producer_instance

        producer = WorkflowEventProducer()
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_COMPLETED,
            source=EventSource.AIRFLOW,
            workflow_id="test_dag",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(data={"status": "success"}),
            metadata=WorkflowEventMetadata(environment="dev"),
        )

        result = producer.publish_event(event)

        assert result is False

    @patch("workflow_events.producer.KafkaProducer")
    def test_publish_event_kafka_error(self, mock_kafka_producer):
        """Test event publishing with Kafka error."""
        mock_producer_instance = MagicMock()
        mock_future = MagicMock()
        mock_future.get.side_effect = KafkaError("Broker error")
        mock_producer_instance.send.return_value = mock_future
        mock_kafka_producer.return_value = mock_producer_instance

        producer = WorkflowEventProducer()
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_COMPLETED,
            source=EventSource.AIRFLOW,
            workflow_id="test_dag",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(data={"status": "success"}),
            metadata=WorkflowEventMetadata(environment="dev"),
        )

        result = producer.publish_event(event)

        assert result is False

    @patch("workflow_events.producer.KafkaProducer")
    def test_publish_event_not_connected(self, mock_kafka_producer):
        """Test publishing when producer is not connected."""
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance

        producer = WorkflowEventProducer()
        producer.producer = None  # Simulate disconnected state

        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_COMPLETED,
            source=EventSource.AIRFLOW,
            workflow_id="test_dag",
            workflow_run_id="run_123",
            payload=WorkflowEventPayload(data={"status": "success"}),
            metadata=WorkflowEventMetadata(environment="dev"),
        )

        with pytest.raises(KafkaError) as exc_info:
            producer.publish_event(event)

        assert "Producer not connected" in str(exc_info.value)


class TestConnectionManagement:
    """Test connection management."""

    @patch("workflow_events.producer.KafkaProducer")
    def test_flush(self, mock_kafka_producer):
        """Test flushing pending messages."""
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance

        producer = WorkflowEventProducer()
        producer.flush()

        mock_producer_instance.flush.assert_called_once_with(timeout=None)

    @patch("workflow_events.producer.KafkaProducer")
    def test_flush_with_timeout(self, mock_kafka_producer):
        """Test flushing with timeout."""
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance

        producer = WorkflowEventProducer()
        producer.flush(timeout=5.0)

        mock_producer_instance.flush.assert_called_once_with(timeout=5.0)

    @patch("workflow_events.producer.KafkaProducer")
    def test_flush_timeout_error(self, mock_kafka_producer):
        """Test flush timeout error handling."""
        mock_producer_instance = MagicMock()
        mock_producer_instance.flush.side_effect = KafkaTimeoutError("Flush timeout")
        mock_kafka_producer.return_value = mock_producer_instance

        producer = WorkflowEventProducer()

        with pytest.raises(KafkaTimeoutError):
            producer.flush()

    @patch("workflow_events.producer.KafkaProducer")
    def test_close(self, mock_kafka_producer):
        """Test closing producer connection."""
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance

        producer = WorkflowEventProducer()
        producer.close()

        mock_producer_instance.flush.assert_called_once()
        mock_producer_instance.close.assert_called_once()
        assert producer.producer is None

    @patch("workflow_events.producer.KafkaProducer")
    def test_close_with_flush_error(self, mock_kafka_producer):
        """Test close handles flush errors gracefully."""
        mock_producer_instance = MagicMock()
        mock_producer_instance.flush.side_effect = Exception("Flush error")
        mock_kafka_producer.return_value = mock_producer_instance

        producer = WorkflowEventProducer()
        producer.close()

        # Should still close and set producer to None
        mock_producer_instance.close.assert_called_once()
        assert producer.producer is None

    @patch("workflow_events.producer.KafkaProducer")
    def test_context_manager(self, mock_kafka_producer):
        """Test producer as context manager."""
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance

        with WorkflowEventProducer() as producer:
            assert producer.producer is not None

        # Should be closed after context exit
        mock_producer_instance.flush.assert_called_once()
        mock_producer_instance.close.assert_called_once()


class TestProducerIntegration:
    """Integration tests for producer (require real Kafka)."""

    @pytest.mark.integration
    def test_publish_event_to_kafka(self):
        """Test publishing event to real Kafka instance."""
        # This test requires a running Kafka instance
        # Run with: pytest -m integration
        producer = WorkflowEventProducer(bootstrap_servers="localhost:9092")

        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_COMPLETED,
            source=EventSource.AIRFLOW,
            workflow_id="test_dag",
            workflow_run_id="run_integration_test",
            payload=WorkflowEventPayload(data={"status": "success", "test": True}),
            metadata=WorkflowEventMetadata(environment="dev"),
        )

        try:
            result = producer.publish_event(event)
            assert result is True
        finally:
            producer.close()

