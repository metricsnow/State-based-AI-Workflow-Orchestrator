"""Integration tests for result producer with real Kafka.

CRITICAL: All tests use production Kafka environment - NO MOCKS, NO PLACEHOLDERS.
Tests connect to real Kafka brokers running in Docker containers.
"""

import asyncio
import os
import pytest
from uuid import uuid4
from kafka.errors import KafkaError

from workflow_events import WorkflowResultEvent
from langgraph_integration.result_producer import ResultProducer
from kafka import KafkaConsumer
import json


@pytest.fixture(scope="module")
def kafka_bootstrap_servers():
    """Fixture providing Kafka bootstrap servers from environment or default."""
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


@pytest.fixture(scope="function")
def test_results_topic():
    """Fixture providing unique test results topic name for each test."""
    return f"test-workflow-results-{uuid4().hex[:8]}"


class TestResultProducerInitialization:
    """Test result producer initialization with real Kafka connections."""

    def test_producer_init_defaults(self) -> None:
        """Test producer initialization with defaults using real Kafka."""
        producer = ResultProducer()
        
        assert producer.bootstrap_servers in ["localhost:9092", os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")]
        assert producer.topic in ["workflow-results", os.getenv("KAFKA_WORKFLOW_RESULTS_TOPIC", "workflow-results")]
        assert producer.producer is None

    def test_producer_init_custom(self) -> None:
        """Test producer initialization with custom values using real Kafka."""
        producer = ResultProducer(
            bootstrap_servers="kafka:9092",
            topic="custom-results",
        )
        
        assert producer.bootstrap_servers == "kafka:9092"
        assert producer.topic == "custom-results"

    @pytest.mark.asyncio
    async def test_producer_start(self, kafka_bootstrap_servers) -> None:
        """Test producer start with real Kafka."""
        producer = ResultProducer(bootstrap_servers=kafka_bootstrap_servers)
        
        try:
            await producer.start()
            
            assert producer.producer is not None
        finally:
            await producer.stop()

    @pytest.mark.asyncio
    async def test_producer_stop(self, kafka_bootstrap_servers) -> None:
        """Test producer stop with real Kafka."""
        producer = ResultProducer(bootstrap_servers=kafka_bootstrap_servers)
        
        await producer.start()
        assert producer.producer is not None
        
        await producer.stop()
        assert producer.producer is None

    @pytest.mark.asyncio
    async def test_producer_stop_no_producer(self) -> None:
        """Test producer stop when producer not started."""
        producer = ResultProducer()
        
        # Should not raise
        await producer.stop()


class TestResultPublishing:
    """Test result publishing functionality with real Kafka."""

    @pytest.mark.asyncio
    async def test_publish_result_success(
        self, kafka_bootstrap_servers, test_results_topic
    ) -> None:
        """Test successful result publishing with real Kafka."""
        producer = ResultProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=test_results_topic,
        )
        
        try:
            await producer.start()
            
            correlation_id = uuid4()
            result_data = {"completed": True, "agent_results": {}}
            
            await producer.publish_result(
                correlation_id=correlation_id,
                workflow_id="test_workflow",
                workflow_run_id="run_123",
                result=result_data,
                status="success",
            )
            
            # Verify message was published by consuming it
            await asyncio.sleep(1)  # Give Kafka time to propagate
            
            consumer = KafkaConsumer(
                test_results_topic,
                bootstrap_servers=[kafka_bootstrap_servers],
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                consumer_timeout_ms=5000,
            )
            
            try:
                message = next(consumer)
                result = message.value
                
                assert result["correlation_id"] == str(correlation_id)
                assert result["workflow_id"] == "test_workflow"
                assert result["status"] == "success"
                assert result["result"]["completed"] is True
            finally:
                consumer.close()
                
        finally:
            await producer.stop()

    @pytest.mark.asyncio
    async def test_publish_result_error(
        self, kafka_bootstrap_servers, test_results_topic
    ) -> None:
        """Test result publishing with error status using real Kafka."""
        producer = ResultProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=test_results_topic,
        )
        
        try:
            await producer.start()
            
            correlation_id = uuid4()
            
            await producer.publish_result(
                correlation_id=correlation_id,
                workflow_id="test_workflow",
                workflow_run_id="run_123",
                result={},
                status="error",
                error="Test error message",
            )
            
            # Verify message was published
            await asyncio.sleep(1)
            
            consumer = KafkaConsumer(
                test_results_topic,
                bootstrap_servers=[kafka_bootstrap_servers],
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                consumer_timeout_ms=5000,
            )
            
            try:
                message = next(consumer)
                result = message.value
                
                assert result["status"] == "error"
                assert result["error"] == "Test error message"
            finally:
                consumer.close()
                
        finally:
            await producer.stop()

    @pytest.mark.asyncio
    async def test_publish_result_not_started(self) -> None:
        """Test publish result when producer not started raises RuntimeError."""
        producer = ResultProducer()
        
        correlation_id = uuid4()
        
        with pytest.raises(RuntimeError, match="Producer not started"):
            await producer.publish_result(
                correlation_id=correlation_id,
                workflow_id="test_workflow",
                workflow_run_id="run_123",
                result={},
            )

    @pytest.mark.asyncio
    async def test_publish_result_multiple_results(
        self, kafka_bootstrap_servers, test_results_topic
    ) -> None:
        """Test publishing multiple results using real Kafka."""
        producer = ResultProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=test_results_topic,
        )
        
        try:
            await producer.start()
            
            correlation_id_1 = uuid4()
            correlation_id_2 = uuid4()
            
            await producer.publish_result(
                correlation_id=correlation_id_1,
                workflow_id="test_workflow_1",
                workflow_run_id="run_123",
                result={"task": "task_1"},
                status="success",
            )
            
            await producer.publish_result(
                correlation_id=correlation_id_2,
                workflow_id="test_workflow_2",
                workflow_run_id="run_456",
                result={"task": "task_2"},
                status="success",
            )
            
            # Verify both messages were published
            await asyncio.sleep(1)
            
            consumer = KafkaConsumer(
                test_results_topic,
                bootstrap_servers=[kafka_bootstrap_servers],
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                consumer_timeout_ms=5000,
            )
            
            try:
                messages = list(consumer)
                assert len(messages) == 2
                
                results = [msg.value for msg in messages]
                correlation_ids = [r["correlation_id"] for r in results]
                
                assert str(correlation_id_1) in correlation_ids
                assert str(correlation_id_2) in correlation_ids
            finally:
                consumer.close()
                
        finally:
            await producer.stop()

    @pytest.mark.asyncio
    async def test_publish_result_with_workflow_result_event(
        self, kafka_bootstrap_servers, test_results_topic
    ) -> None:
        """Test publishing result using WorkflowResultEvent model with real Kafka."""
        producer = ResultProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=test_results_topic,
        )
        
        try:
            await producer.start()
            
            correlation_id = uuid4()
            result_data = {"agent_results": {"agent1": "result1"}}
            
            # Create result event to verify schema
            result_event = WorkflowResultEvent(
                correlation_id=correlation_id,
                workflow_id="test_workflow",
                workflow_run_id="run_123",
                result=result_data,
                status="success",
            )
            
            # Publish using producer
            await producer.publish_result(
                correlation_id=correlation_id,
                workflow_id="test_workflow",
                workflow_run_id="run_123",
                result=result_data,
                status="success",
            )
            
            # Verify message matches schema
            await asyncio.sleep(1)
            
            consumer = KafkaConsumer(
                test_results_topic,
                bootstrap_servers=[kafka_bootstrap_servers],
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                consumer_timeout_ms=5000,
            )
            
            try:
                message = next(consumer)
                result = message.value
                
                # Validate against schema
                parsed_event = WorkflowResultEvent.model_validate(result)
                assert parsed_event.correlation_id == correlation_id
                assert parsed_event.workflow_id == "test_workflow"
                assert parsed_event.status == "success"
            finally:
                consumer.close()
                
        finally:
            await producer.stop()
