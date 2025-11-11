"""
Integration tests for Kafka producer implementation using real Kafka.

CRITICAL: All tests use production Kafka environment - NO MOCKS, NO PLACEHOLDERS.
Tests connect to real Kafka brokers running in Docker containers.
"""

import os
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


@pytest.fixture(scope="module")
def kafka_bootstrap_servers():
    """Fixture providing Kafka bootstrap servers from environment or default."""
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


@pytest.fixture(scope="module")
def test_topic():
    """Fixture providing test topic name."""
    return "test-workflow-events-producer"


class TestProducerInitialization:
    """Test producer initialization with real Kafka connections."""

    def test_producer_initialization_defaults(self, kafka_bootstrap_servers):
        """Test producer initialization with default parameters using real Kafka."""
        producer = None
        try:
            producer = WorkflowEventProducer(bootstrap_servers=kafka_bootstrap_servers)
            assert producer is not None
            assert producer.bootstrap_servers == kafka_bootstrap_servers
            assert producer.producer is not None
            # Verify connection by checking producer is initialized
            # Producer will connect on first send, so just verify it exists
        finally:
            if producer:
                producer.close()

    def test_producer_initialization_custom_servers(self, kafka_bootstrap_servers):
        """Test producer initialization with custom bootstrap servers using real Kafka."""
        producer = None
        try:
            producer = WorkflowEventProducer(bootstrap_servers=kafka_bootstrap_servers)
            assert producer.bootstrap_servers == kafka_bootstrap_servers
            assert producer.producer is not None
        finally:
            if producer:
                producer.close()

    def test_producer_initialization_custom_config(self, kafka_bootstrap_servers):
        """Test producer initialization with custom configuration using real Kafka."""
        producer = None
        try:
            producer = WorkflowEventProducer(
                bootstrap_servers=kafka_bootstrap_servers,
                acks="1",
                retries=5,
                max_in_flight_requests_per_connection=2,
            )
            assert producer.producer is not None
            # Verify it can connect - producer will connect on first send
        finally:
            if producer:
                producer.close()


class TestEventSerialization:
    """Test event serialization with real data."""

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

        import json

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
    """Test event publishing functionality with real Kafka."""

    def test_publish_event_success_real_kafka(
        self, kafka_bootstrap_servers, test_topic
    ):
        """Test successful event publishing to real Kafka."""
        producer = None
        try:
            producer = WorkflowEventProducer(bootstrap_servers=kafka_bootstrap_servers)
            event = WorkflowEvent(
                event_type=EventType.WORKFLOW_COMPLETED,
                source=EventSource.AIRFLOW,
                workflow_id="test_dag",
                workflow_run_id="run_publish_success",
                payload=WorkflowEventPayload(data={"status": "success", "test": True}),
                metadata=WorkflowEventMetadata(environment="dev"),
            )

            result = producer.publish_event(event, topic=test_topic)
            assert result is True
            producer.flush()
        finally:
            if producer:
                producer.close()

    def test_publish_event_custom_topic_real_kafka(
        self, kafka_bootstrap_servers, test_topic
    ):
        """Test event publishing to custom topic using real Kafka."""
        producer = None
        try:
            producer = WorkflowEventProducer(bootstrap_servers=kafka_bootstrap_servers)
            event = WorkflowEvent(
                event_type=EventType.WORKFLOW_TRIGGERED,
                source=EventSource.AIRFLOW,
                workflow_id="test_dag",
                workflow_run_id="run_custom_topic",
                payload=WorkflowEventPayload(data={"status": "triggered"}),
                metadata=WorkflowEventMetadata(environment="dev"),
            )

            result = producer.publish_event(event, topic=test_topic)
            assert result is True
            producer.flush()
        finally:
            if producer:
                producer.close()

    def test_publish_event_default_topic_real_kafka(self, kafka_bootstrap_servers):
        """Test event publishing to default topic using real Kafka."""
        producer = None
        try:
            producer = WorkflowEventProducer(bootstrap_servers=kafka_bootstrap_servers)
            event = WorkflowEvent(
                event_type=EventType.WORKFLOW_COMPLETED,
                source=EventSource.AIRFLOW,
                workflow_id="test_dag",
                workflow_run_id="run_default_topic",
                payload=WorkflowEventPayload(data={"status": "success"}),
                metadata=WorkflowEventMetadata(environment="dev"),
            )

            result = producer.publish_event(event)
            assert result is True
            producer.flush()
        finally:
            if producer:
                producer.close()


class TestConnectionManagement:
    """Test connection management with real Kafka."""

    def test_flush_real_kafka(self, kafka_bootstrap_servers, test_topic):
        """Test flushing pending messages with real Kafka."""
        producer = None
        try:
            producer = WorkflowEventProducer(bootstrap_servers=kafka_bootstrap_servers)
            event = WorkflowEvent(
                event_type=EventType.WORKFLOW_COMPLETED,
                source=EventSource.AIRFLOW,
                workflow_id="test_dag",
                workflow_run_id="run_flush_test",
                payload=WorkflowEventPayload(data={"status": "success"}),
                metadata=WorkflowEventMetadata(environment="dev"),
            )
            producer.publish_event(event, topic=test_topic)
            producer.flush()
        finally:
            if producer:
                producer.close()

    def test_flush_with_timeout_real_kafka(self, kafka_bootstrap_servers, test_topic):
        """Test flushing with timeout using real Kafka."""
        producer = None
        try:
            producer = WorkflowEventProducer(bootstrap_servers=kafka_bootstrap_servers)
            event = WorkflowEvent(
                event_type=EventType.WORKFLOW_COMPLETED,
                source=EventSource.AIRFLOW,
                workflow_id="test_dag",
                workflow_run_id="run_flush_timeout",
                payload=WorkflowEventPayload(data={"status": "success"}),
                metadata=WorkflowEventMetadata(environment="dev"),
            )
            producer.publish_event(event, topic=test_topic)
            producer.flush(timeout=5.0)
        finally:
            if producer:
                producer.close()

    def test_close_real_kafka(self, kafka_bootstrap_servers):
        """Test closing producer connection with real Kafka."""
        producer = WorkflowEventProducer(bootstrap_servers=kafka_bootstrap_servers)
        producer.close()
        assert producer.producer is None

    def test_context_manager_real_kafka(self, kafka_bootstrap_servers, test_topic):
        """Test producer as context manager with real Kafka."""
        with WorkflowEventProducer(
            bootstrap_servers=kafka_bootstrap_servers
        ) as producer:
            assert producer.producer is not None
            event = WorkflowEvent(
                event_type=EventType.WORKFLOW_COMPLETED,
                source=EventSource.AIRFLOW,
                workflow_id="test_dag",
                workflow_run_id="run_context_test",
                payload=WorkflowEventPayload(data={"status": "success"}),
                metadata=WorkflowEventMetadata(environment="dev"),
            )
            result = producer.publish_event(event, topic=test_topic)
            assert result is True

        # Should be closed after context exit
        assert producer.producer is None

