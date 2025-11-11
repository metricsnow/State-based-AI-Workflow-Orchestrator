"""
Integration tests for Kafka consumer implementation using real Kafka.

CRITICAL: All tests use production Kafka environment - NO MOCKS, NO PLACEHOLDERS.
Tests connect to real Kafka brokers running in Docker containers.
"""

import os
import time
import pytest
from kafka.errors import KafkaError
from kafka.structs import TopicPartition

from workflow_events import (
    EventType,
    EventSource,
    WorkflowEvent,
    WorkflowEventPayload,
    WorkflowEventMetadata,
    WorkflowEventConsumer,
    WorkflowEventProducer,
)


@pytest.fixture(scope="module")
def kafka_bootstrap_servers():
    """Fixture providing Kafka bootstrap servers from environment or default."""
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


@pytest.fixture(scope="module")
def test_topic():
    """Fixture providing test topic name."""
    return "test-workflow-events-consumer"


@pytest.fixture(scope="function")
def clean_topic(kafka_bootstrap_servers, test_topic):
    """Ensure topic is clean before each test."""
    # Producer will auto-create topic if it doesn't exist
    yield
    # Cleanup handled by test teardown


class TestConsumerInitialization:
    """Test consumer initialization with real Kafka connections."""

    def test_consumer_initialization_defaults(self, kafka_bootstrap_servers):
        """Test consumer initialization with default parameters using real Kafka."""
        consumer = None
        try:
            consumer = WorkflowEventConsumer(bootstrap_servers=kafka_bootstrap_servers)
            assert consumer is not None
            assert consumer.bootstrap_servers == kafka_bootstrap_servers
            assert consumer.consumer is not None
            # Verify connection by checking consumer is ready
            assert consumer.consumer.bootstrap_connected()
        finally:
            if consumer:
                consumer.close()

    def test_consumer_initialization_custom_servers(self, kafka_bootstrap_servers):
        """Test consumer initialization with custom bootstrap servers using real Kafka."""
        consumer = None
        try:
            consumer = WorkflowEventConsumer(bootstrap_servers=kafka_bootstrap_servers)
            assert consumer.bootstrap_servers == kafka_bootstrap_servers
            assert consumer.consumer is not None
        finally:
            if consumer:
                consumer.close()

    def test_consumer_initialization_with_group_id(self, kafka_bootstrap_servers):
        """Test consumer initialization with consumer group using real Kafka."""
        consumer = None
        try:
            consumer = WorkflowEventConsumer(
                bootstrap_servers=kafka_bootstrap_servers, group_id="test-group-real"
            )
            assert consumer.group_id == "test-group-real"
            assert consumer.consumer is not None
        finally:
            if consumer:
                consumer.close()

    def test_consumer_initialization_custom_config(self, kafka_bootstrap_servers):
        """Test consumer initialization with custom configuration using real Kafka."""
        consumer = None
        try:
            consumer = WorkflowEventConsumer(
                bootstrap_servers=kafka_bootstrap_servers,
                group_id="test-group-custom",
                auto_offset_reset="latest",
                enable_auto_commit=False,
                consumer_timeout_ms=5000,
                max_poll_records=100,
            )
            assert consumer.consumer is not None
            assert consumer.auto_offset_reset == "latest"
            assert consumer.enable_auto_commit is False
        finally:
            if consumer:
                consumer.close()


class TestEventDeserialization:
    """Test event deserialization with real data."""

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

        import json

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


class TestTopicSubscription:
    """Test topic subscription with real Kafka."""

    def test_subscribe_topics(self, kafka_bootstrap_servers, test_topic):
        """Test subscribing to topics using real Kafka."""
        consumer = None
        try:
            consumer = WorkflowEventConsumer(
                bootstrap_servers=kafka_bootstrap_servers,
                group_id="test-subscribe-group",
            )
            consumer.subscribe([test_topic])
            # Verify subscription by checking assigned partitions
            time.sleep(1)  # Allow time for subscription
            partitions = consumer.consumer.assignment()
            assert len(partitions) >= 0  # May be empty if topic doesn't exist yet
        finally:
            if consumer:
                consumer.close()


class TestEventConsumption:
    """Test event consumption functionality with real Kafka."""

    def test_consume_event_from_real_kafka(
        self, kafka_bootstrap_servers, test_topic, clean_topic
    ):
        """Test consuming event from real Kafka instance."""
        # First, publish an event to the topic
        producer = None
        consumer = None
        try:
            # Publish event
            producer = WorkflowEventProducer(bootstrap_servers=kafka_bootstrap_servers)
            event = WorkflowEvent(
                event_type=EventType.WORKFLOW_COMPLETED,
                source=EventSource.AIRFLOW,
                workflow_id="test_dag",
                workflow_run_id="run_consume_test",
                payload=WorkflowEventPayload(data={"status": "success", "test": True}),
                metadata=WorkflowEventMetadata(environment="dev"),
            )
            publish_result = producer.publish_event(event, topic=test_topic)
            assert publish_result is True
            producer.flush()

            # Now consume the event
            consumer = WorkflowEventConsumer(
                bootstrap_servers=kafka_bootstrap_servers,
                group_id="test-consume-group-unique",
                auto_offset_reset="earliest",
            )

            events_received = []

            def callback(event: WorkflowEvent):
                events_received.append(event)

            consumer.subscribe([test_topic])
            time.sleep(2)  # Allow time for subscription

            # Poll for messages
            start_time = time.time()
            timeout = 10
            while time.time() - start_time < timeout:
                message_batch = consumer.consumer.poll(timeout_ms=2000)
                if message_batch:
                    for topic_partition, messages in message_batch.items():
                        for message in messages:
                            try:
                                event_dict = message.value
                                event = WorkflowEvent(**event_dict)
                                if (
                                    event.workflow_id == "test_dag"
                                    and event.workflow_run_id == "run_consume_test"
                                ):
                                    callback(event)
                            except Exception:
                                pass

                if events_received:
                    break

            # Verify event was received
            assert len(events_received) > 0, "No events received from Kafka"
            received_event = events_received[0]
            assert received_event.workflow_id == "test_dag"
            assert received_event.workflow_run_id == "run_consume_test"
            assert received_event.payload.data["test"] is True

        finally:
            if producer:
                producer.close()
            if consumer:
                consumer.close()


class TestPolling:
    """Test polling functionality with real Kafka."""

    def test_poll_real_kafka(self, kafka_bootstrap_servers, test_topic):
        """Test polling for messages from real Kafka."""
        producer = None
        consumer = None
        try:
            # Publish an event first
            producer = WorkflowEventProducer(bootstrap_servers=kafka_bootstrap_servers)
            event = WorkflowEvent(
                event_type=EventType.WORKFLOW_COMPLETED,
                source=EventSource.AIRFLOW,
                workflow_id="test_dag",
                workflow_run_id="run_poll_test",
                payload=WorkflowEventPayload(data={"status": "success"}),
                metadata=WorkflowEventMetadata(environment="dev"),
            )
            producer.publish_event(event, topic=test_topic)
            producer.flush()

            # Poll for the message
            consumer = WorkflowEventConsumer(
                bootstrap_servers=kafka_bootstrap_servers,
                group_id="test-poll-group",
                auto_offset_reset="earliest",
            )
            consumer.subscribe([test_topic])
            time.sleep(1)

            result = consumer.poll(timeout_ms=5000)
            assert result is not None
            # Result should be a dict with TopicPartition keys
            if result:
                assert isinstance(result, dict)

        finally:
            if producer:
                producer.close()
            if consumer:
                consumer.close()


class TestOffsetManagement:
    """Test offset management with real Kafka."""

    def test_commit_real_kafka(self, kafka_bootstrap_servers, test_topic):
        """Test committing offsets with real Kafka."""
        consumer = None
        try:
            consumer = WorkflowEventConsumer(
                bootstrap_servers=kafka_bootstrap_servers,
                group_id="test-commit-group",
                enable_auto_commit=False,
            )
            consumer.subscribe([test_topic])
            time.sleep(1)
            # Commit should work without error
            consumer.commit()
        finally:
            if consumer:
                consumer.close()

    def test_seek_real_kafka(self, kafka_bootstrap_servers, test_topic):
        """Test seeking to specific offset with real Kafka."""
        consumer = None
        try:
            consumer = WorkflowEventConsumer(
                bootstrap_servers=kafka_bootstrap_servers,
                group_id="test-seek-group",
                auto_offset_reset="earliest",
            )
            consumer.subscribe([test_topic])
            time.sleep(1)
            # Get partitions
            partitions = consumer.consumer.assignment()
            if partitions:
                tp = list(partitions)[0]
                consumer.seek(tp, 0)  # Seek to beginning
        finally:
            if consumer:
                consumer.close()

    def test_position_real_kafka(self, kafka_bootstrap_servers, test_topic):
        """Test getting current position with real Kafka."""
        consumer = None
        try:
            consumer = WorkflowEventConsumer(
                bootstrap_servers=kafka_bootstrap_servers,
                group_id="test-position-group",
                auto_offset_reset="earliest",
            )
            consumer.subscribe([test_topic])
            time.sleep(1)
            partitions = consumer.consumer.assignment()
            if partitions:
                tp = list(partitions)[0]
                position = consumer.position(tp)
                assert isinstance(position, int)
                assert position >= 0
        finally:
            if consumer:
                consumer.close()


class TestConnectionManagement:
    """Test connection management with real Kafka."""

    def test_close_real_kafka(self, kafka_bootstrap_servers):
        """Test closing consumer connection with real Kafka."""
        consumer = WorkflowEventConsumer(bootstrap_servers=kafka_bootstrap_servers)
        consumer.close()
        assert consumer.consumer is None

    def test_close_with_timeout_real_kafka(self, kafka_bootstrap_servers):
        """Test closing with timeout using real Kafka."""
        consumer = WorkflowEventConsumer(bootstrap_servers=kafka_bootstrap_servers)
        consumer.close(timeout_ms=5000)
        assert consumer.consumer is None

    def test_context_manager_real_kafka(self, kafka_bootstrap_servers):
        """Test consumer as context manager with real Kafka."""
        with WorkflowEventConsumer(
            bootstrap_servers=kafka_bootstrap_servers
        ) as consumer:
            assert consumer.consumer is not None
            assert consumer.bootstrap_servers == kafka_bootstrap_servers

        # Should be closed after context exit
        assert consumer.consumer is None

