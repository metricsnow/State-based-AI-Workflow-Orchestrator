"""
Tests for Airflow-Kafka Integration

This module contains tests for the Airflow-Kafka integration utilities.
All tests run against real Kafka instances - NO MOCKS, NO PLACEHOLDERS.

CRITICAL: All tests use production Kafka environment from docker-compose.yml
"""

import os
import pytest
from typing import Dict, Any

from workflow_events import (
    EventType,
    EventSource,
    WorkflowEvent,
    WorkflowEventPayload,
    WorkflowEventMetadata,
    WorkflowEventConsumer,
)
from airflow_integration import (
    get_kafka_producer,
    publish_workflow_event,
    publish_task_completion_event,
    publish_dag_completion_event,
    publish_event_from_taskflow_context,
)


@pytest.fixture(scope="module")
def kafka_bootstrap_servers():
    """Fixture providing Kafka bootstrap servers from environment or default."""
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


@pytest.fixture(scope="module")
def kafka_topic():
    """Fixture providing Kafka topic name for testing."""
    return "workflow-events"


class TestGetKafkaProducer:
    """Test get_kafka_producer function with real Kafka."""

    def test_get_kafka_producer_default(self, kafka_bootstrap_servers):
        """Test getting producer with default configuration."""
        producer = None
        try:
            producer = get_kafka_producer()
            assert producer is not None
            assert producer.bootstrap_servers == kafka_bootstrap_servers
            assert producer.producer is not None
        finally:
            if producer:
                producer.close()

    def test_get_kafka_producer_explicit(self, kafka_bootstrap_servers):
        """Test getting producer with explicit bootstrap_servers."""
        producer = None
        try:
            producer = get_kafka_producer(bootstrap_servers=kafka_bootstrap_servers)
            assert producer is not None
            assert producer.bootstrap_servers == kafka_bootstrap_servers
        finally:
            if producer:
                producer.close()

    def test_get_kafka_producer_connection(self, kafka_bootstrap_servers):
        """Test producer can connect to real Kafka."""
        producer = None
        try:
            producer = get_kafka_producer(bootstrap_servers=kafka_bootstrap_servers)
            # Test connection by attempting to get metadata
            # If connection fails, producer will raise exception
            assert producer.producer is not None
        finally:
            if producer:
                producer.close()


class TestPublishWorkflowEvent:
    """Test publish_workflow_event function with real Kafka."""

    @pytest.fixture(autouse=True)
    def setup_environment(self):
        """Set environment variables for testing."""
        os.environ["ENVIRONMENT"] = "dev"
        os.environ["EVENT_SCHEMA_VERSION"] = "1.0"
        yield
        # Cleanup
        if "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]
        if "EVENT_SCHEMA_VERSION" in os.environ:
            del os.environ["EVENT_SCHEMA_VERSION"]

    def test_publish_workflow_event_success(
        self, kafka_bootstrap_servers, kafka_topic
    ):
        """Test successful event publishing to real Kafka."""
        result = publish_workflow_event(
            event_type=EventType.WORKFLOW_COMPLETED,
            workflow_id="test_dag",
            workflow_run_id="run_123",
            payload={"status": "success", "test": True},
            topic=kafka_topic,
            bootstrap_servers=kafka_bootstrap_servers,
        )

        assert result is True

    def test_publish_workflow_event_failed(
        self, kafka_bootstrap_servers, kafka_topic
    ):
        """Test publishing failed workflow event to real Kafka."""
        result = publish_workflow_event(
            event_type=EventType.WORKFLOW_FAILED,
            workflow_id="test_dag",
            workflow_run_id="run_456",
            payload={"status": "failed", "error": "Test error"},
            topic=kafka_topic,
            bootstrap_servers=kafka_bootstrap_servers,
        )

        assert result is True

    def test_publish_workflow_event_with_metadata(
        self, kafka_bootstrap_servers, kafka_topic
    ):
        """Test publishing event with custom metadata to real Kafka."""
        result = publish_workflow_event(
            event_type=EventType.WORKFLOW_COMPLETED,
            workflow_id="test_dag",
            workflow_run_id="run_789",
            payload={"status": "success"},
            metadata={"environment": "dev", "version": "1.0"},
            topic=kafka_topic,
            bootstrap_servers=kafka_bootstrap_servers,
        )

        assert result is True

    def test_publish_workflow_event_verify_consumption(
        self, kafka_bootstrap_servers, kafka_topic
    ):
        """Test that published events can be consumed from real Kafka."""
        # Publish event
        publish_result = publish_workflow_event(
            event_type=EventType.WORKFLOW_COMPLETED,
            workflow_id="test_dag",
            workflow_run_id="run_verify",
            payload={"status": "success", "verification": True},
            topic=kafka_topic,
            bootstrap_servers=kafka_bootstrap_servers,
        )

        assert publish_result is True

        # Consume event to verify it was published
        consumer = None
        try:
            consumer = WorkflowEventConsumer(
                bootstrap_servers=kafka_bootstrap_servers,
                group_id="test-verification-group-unique",
                auto_offset_reset="earliest",
            )

            # Subscribe to topic
            consumer.subscribe([kafka_topic])

            # Poll for the message (with timeout)
            events_received = []
            import time

            start_time = time.time()
            timeout = 10  # 10 seconds timeout

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
                                    and event.workflow_run_id == "run_verify"
                                ):
                                    events_received.append(event)
                            except Exception as e:
                                # Skip invalid messages
                                pass

                if events_received:
                    break

            # Verify event was received
            assert len(events_received) > 0, "No events received from Kafka"
            event = events_received[0]
            assert event.workflow_id == "test_dag"
            assert event.workflow_run_id == "run_verify"
            assert event.payload.data["verification"] is True

        finally:
            if consumer:
                consumer.close()


class TestPublishTaskCompletionEvent:
    """Test publish_task_completion_event function with real Kafka."""

    def test_publish_task_completion_success(
        self, kafka_bootstrap_servers, kafka_topic
    ):
        """Test publishing task completion event with success status to real Kafka."""
        result = publish_task_completion_event(
            task_id="test_task",
            dag_id="test_dag",
            dag_run_id="run_task_success",
            task_result={"data": [1, 2, 3]},
            task_status="success",
            topic=kafka_topic,
            bootstrap_servers=kafka_bootstrap_servers,
        )

        assert result is True

    def test_publish_task_completion_failed(
        self, kafka_bootstrap_servers, kafka_topic
    ):
        """Test publishing task completion event with failed status to real Kafka."""
        result = publish_task_completion_event(
            task_id="test_task",
            dag_id="test_dag",
            dag_run_id="run_task_failed",
            task_status="failed",
            error_message="Task failed",
            topic=kafka_topic,
            bootstrap_servers=kafka_bootstrap_servers,
        )

        assert result is True


class TestPublishDagCompletionEvent:
    """Test publish_dag_completion_event function with real Kafka."""

    def test_publish_dag_completion_success(
        self, kafka_bootstrap_servers, kafka_topic
    ):
        """Test publishing DAG completion event with success status to real Kafka."""
        result = publish_dag_completion_event(
            dag_id="test_dag",
            dag_run_id="run_dag_success",
            dag_status="success",
            task_results={"task1": "success", "task2": "success"},
            topic=kafka_topic,
            bootstrap_servers=kafka_bootstrap_servers,
        )

        assert result is True

    def test_publish_dag_completion_failed(
        self, kafka_bootstrap_servers, kafka_topic
    ):
        """Test publishing DAG completion event with failed status to real Kafka."""
        result = publish_dag_completion_event(
            dag_id="test_dag",
            dag_run_id="run_dag_failed",
            dag_status="failed",
            error_message="DAG failed",
            topic=kafka_topic,
            bootstrap_servers=kafka_bootstrap_servers,
        )

        assert result is True


class TestPublishEventFromTaskflowContext:
    """Test publish_event_from_taskflow_context function with real Kafka."""

    def test_publish_with_dag_run_context(
        self, kafka_bootstrap_servers, kafka_topic
    ):
        """Test publishing event with dag_run context to real Kafka."""
        # Create simple dag_run object with required attributes
        # This is a real Python object, not a mock - just a data container
        class DagRunContext:
            def __init__(self):
                self.dag_id = "test_dag"
                self.run_id = "run_context_test"

        dag_run_context = DagRunContext()

        result = publish_event_from_taskflow_context(
            event_type=EventType.WORKFLOW_COMPLETED,
            payload={"status": "success", "context": "dag_run"},
            dag_run=dag_run_context,
            topic=kafka_topic,
            bootstrap_servers=kafka_bootstrap_servers,
        )

        assert result is True

    def test_publish_with_ti_context(self, kafka_bootstrap_servers, kafka_topic):
        """Test publishing event with ti (TaskInstance) context to real Kafka."""
        # Create simple ti object with required attributes
        # This is a real Python object, not a mock - just a data container
        class TaskInstanceContext:
            def __init__(self):
                self.dag_id = "test_dag"
                self.dag_run_id = "run_ti_test"

        ti_context = TaskInstanceContext()

        result = publish_event_from_taskflow_context(
            event_type=EventType.WORKFLOW_COMPLETED,
            payload={"status": "success", "context": "ti"},
            ti=ti_context,
            topic=kafka_topic,
            bootstrap_servers=kafka_bootstrap_servers,
        )

        assert result is True

    def test_publish_with_explicit_ids(
        self, kafka_bootstrap_servers, kafka_topic
    ):
        """Test publishing event with explicit DAG ID and run ID to real Kafka."""
        result = publish_event_from_taskflow_context(
            event_type=EventType.WORKFLOW_COMPLETED,
            payload={"status": "success", "explicit": True},
            dag_id="explicit_dag",
            dag_run_id="explicit_run",
            topic=kafka_topic,
            bootstrap_servers=kafka_bootstrap_servers,
        )

        assert result is True

    def test_publish_without_context(self, kafka_bootstrap_servers, kafka_topic):
        """Test publishing event without context information (should fail gracefully)."""
        result = publish_event_from_taskflow_context(
            event_type=EventType.WORKFLOW_COMPLETED,
            payload={"status": "success"},
            topic=kafka_topic,
            bootstrap_servers=kafka_bootstrap_servers,
        )

        # Should return False when context is missing
        assert result is False
