"""Integration tests for result return mechanism with real Kafka.

CRITICAL: All tests use production Kafka environment - NO MOCKS, NO PLACEHOLDERS.
Tests connect to real Kafka brokers running in Docker containers.
"""

import asyncio
import os
import time
import pytest
from uuid import uuid4

from workflow_events import (
    EventType,
    EventSource,
    WorkflowEvent,
    WorkflowEventPayload,
    WorkflowEventMetadata,
    WorkflowEventProducer,
)
from langgraph_integration.consumer import LangGraphKafkaConsumer
from langgraph_integration.config import ConsumerConfig
from airflow_integration.result_poller import WorkflowResultPoller


@pytest.fixture(scope="module")
def kafka_bootstrap_servers():
    """Fixture providing Kafka bootstrap servers from environment or default."""
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


@pytest.fixture(scope="function")
def test_topic():
    """Fixture providing unique test topic name for each test."""
    return f"test-workflow-events-{uuid4().hex[:8]}"


@pytest.fixture(scope="function")
def test_results_topic():
    """Fixture providing unique test results topic name for each test."""
    return f"test-workflow-results-{uuid4().hex[:8]}"


@pytest.fixture(scope="function")
def consumer_config(kafka_bootstrap_servers, test_topic):
    """Fixture providing consumer configuration for tests."""
    return ConsumerConfig(
        bootstrap_servers=kafka_bootstrap_servers,
        topic=test_topic,
        group_id=f"test-group-{uuid4().hex[:8]}",
        auto_offset_reset="earliest",
    )


class TestResultReturnIntegration:
    """Integration tests for end-to-end result return mechanism."""

    @pytest.mark.asyncio
    async def test_end_to_end_result_flow(
        self,
        consumer_config,
        test_results_topic,
        kafka_bootstrap_servers,
    ):
        """Test complete flow: trigger event -> process -> result -> poll."""
        # Set result topic for producer
        import os
        original_topic = os.getenv("KAFKA_WORKFLOW_RESULTS_TOPIC")
        os.environ["KAFKA_WORKFLOW_RESULTS_TOPIC"] = test_results_topic
        
        try:
            # Create and publish test event
            producer = WorkflowEventProducer(
                bootstrap_servers=kafka_bootstrap_servers
            )
            
            event = WorkflowEvent(
                event_type=EventType.WORKFLOW_TRIGGERED,
                source=EventSource.AIRFLOW,
                workflow_id="test_workflow",
                workflow_run_id="run_123",
                payload=WorkflowEventPayload(
                    data={"task": "test_task", "data": {"input": "test"}}
                ),
                metadata=WorkflowEventMetadata(environment="dev", version="1.0"),
            )
            
            correlation_id = event.event_id
            
            # Publish event
            success = producer.publish_event(event, topic=consumer_config.topic)
            assert success is True
            producer.close()
            
            # Start consumer
            consumer = LangGraphKafkaConsumer(config=consumer_config)
            
            try:
                await consumer.start()
                
                # Give consumer time to process event
                await asyncio.sleep(5)
                
                # Poll for result
                poller = WorkflowResultPoller(
                    bootstrap_servers=kafka_bootstrap_servers,
                    topic=test_results_topic,
                    timeout=30,
                )
                
                result = poller.poll_for_result(
                    correlation_id=correlation_id,
                    workflow_id="test_workflow",
                )
                
                assert result is not None
                assert result["correlation_id"] == str(correlation_id)
                assert result["workflow_id"] == "test_workflow"
                assert result["status"] == "success"
                assert "result" in result
                assert result["result"]["task"] == "test_task"
            
            finally:
                await consumer.stop()
        
        finally:
            # Restore original topic
            if original_topic:
                os.environ["KAFKA_WORKFLOW_RESULTS_TOPIC"] = original_topic
            elif "KAFKA_WORKFLOW_RESULTS_TOPIC" in os.environ:
                del os.environ["KAFKA_WORKFLOW_RESULTS_TOPIC"]

    @pytest.mark.asyncio
    async def test_result_polling_timeout(
        self,
        test_results_topic,
        kafka_bootstrap_servers,
    ):
        """Test result polling times out when no result is available."""
        poller = WorkflowResultPoller(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=test_results_topic,
            timeout=2,  # Short timeout for test
        )
        
        correlation_id = uuid4()
        
        result = poller.poll_for_result(correlation_id=correlation_id)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_result_correlation_id_matching(
        self,
        consumer_config,
        test_results_topic,
        kafka_bootstrap_servers,
    ):
        """Test result polling matches correlation IDs correctly."""
        # Set result topic for producer
        import os
        original_topic = os.getenv("KAFKA_WORKFLOW_RESULTS_TOPIC")
        os.environ["KAFKA_WORKFLOW_RESULTS_TOPIC"] = test_results_topic
        
        try:
            # Create and publish two events
            producer = WorkflowEventProducer(
                bootstrap_servers=kafka_bootstrap_servers
            )
            
            event1 = WorkflowEvent(
                event_type=EventType.WORKFLOW_TRIGGERED,
                source=EventSource.AIRFLOW,
                workflow_id="test_workflow_1",
                workflow_run_id="run_123",
                payload=WorkflowEventPayload(
                    data={"task": "task_1"}
                ),
                metadata=WorkflowEventMetadata(environment="dev", version="1.0"),
            )
            
            event2 = WorkflowEvent(
                event_type=EventType.WORKFLOW_TRIGGERED,
                source=EventSource.AIRFLOW,
                workflow_id="test_workflow_2",
                workflow_run_id="run_456",
                payload=WorkflowEventPayload(
                    data={"task": "task_2"}
                ),
                metadata=WorkflowEventMetadata(environment="dev", version="1.0"),
            )
            
            correlation_id_1 = event1.event_id
            correlation_id_2 = event2.event_id
            
            # Publish both events
            producer.publish_event(event1, topic=consumer_config.topic)
            producer.publish_event(event2, topic=consumer_config.topic)
            producer.close()
            
            # Start consumer
            consumer = LangGraphKafkaConsumer(config=consumer_config)
            
            try:
                await consumer.start()
                
                # Give consumer time to process events
                await asyncio.sleep(8)
                
                # Poll for first result
                poller = WorkflowResultPoller(
                    bootstrap_servers=kafka_bootstrap_servers,
                    topic=test_results_topic,
                    timeout=30,
                )
                
                result1 = poller.poll_for_result(
                    correlation_id=correlation_id_1,
                )
                
                result2 = poller.poll_for_result(
                    correlation_id=correlation_id_2,
                )
                
                assert result1 is not None
                assert result1["correlation_id"] == str(correlation_id_1)
                assert result1["workflow_id"] == "test_workflow_1"
                
                assert result2 is not None
                assert result2["correlation_id"] == str(correlation_id_2)
                assert result2["workflow_id"] == "test_workflow_2"
            
            finally:
                await consumer.stop()
        
        finally:
            # Restore original topic
            if original_topic:
                os.environ["KAFKA_WORKFLOW_RESULTS_TOPIC"] = original_topic
            elif "KAFKA_WORKFLOW_RESULTS_TOPIC" in os.environ:
                del os.environ["KAFKA_WORKFLOW_RESULTS_TOPIC"]

