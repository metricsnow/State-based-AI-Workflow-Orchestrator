"""Integration tests for result poller with real Kafka.

CRITICAL: All tests use production Kafka environment - NO MOCKS, NO PLACEHOLDERS.
Tests connect to real Kafka brokers running in Docker containers.
"""

import asyncio
import os
import time
import pytest
from uuid import uuid4

from workflow_events import WorkflowResultEvent
from airflow_integration.result_poller import WorkflowResultPoller
from langgraph_integration.result_producer import ResultProducer


@pytest.fixture(scope="module")
def kafka_bootstrap_servers():
    """Fixture providing Kafka bootstrap servers from environment or default."""
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


@pytest.fixture(scope="function")
def test_results_topic():
    """Fixture providing unique test results topic name for each test."""
    return f"test-workflow-results-{uuid4().hex[:8]}"


class TestWorkflowResultPollerInitialization:
    """Test result poller initialization with real Kafka connections."""

    def test_poller_init_defaults(self) -> None:
        """Test poller initialization with defaults using real Kafka."""
        poller = WorkflowResultPoller()
        
        assert poller.bootstrap_servers == "localhost:9092"
        assert poller.topic == "workflow-results"
        assert poller.timeout == 300
        assert poller.poll_interval == 1.0

    def test_poller_init_custom(self) -> None:
        """Test poller initialization with custom values using real Kafka."""
        poller = WorkflowResultPoller(
            bootstrap_servers="kafka:9092",
            topic="custom-results",
            timeout=600,
            poll_interval=2.0,
        )
        
        assert poller.bootstrap_servers == "kafka:9092"
        assert poller.topic == "custom-results"
        assert poller.timeout == 600
        assert poller.poll_interval == 2.0


class TestResultPolling:
    """Test result polling functionality with real Kafka."""

    @pytest.mark.asyncio
    async def test_poll_for_result_success(
        self, kafka_bootstrap_servers, test_results_topic
    ) -> None:
        """Test successful result polling with real Kafka."""
        correlation_id = uuid4()
        
        # Publish result using real producer
        producer = ResultProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=test_results_topic,
        )
        
        try:
            await producer.start()
            
            result_data = {"completed": True, "agent_results": {}}
            await producer.publish_result(
                correlation_id=correlation_id,
                workflow_id="test_workflow",
                workflow_run_id="run_123",
                result=result_data,
                status="success",
            )
            
            # Give Kafka time to propagate
            await asyncio.sleep(1)
            
        finally:
            await producer.stop()
        
        # Poll for result using real consumer
        poller = WorkflowResultPoller(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=test_results_topic,
            timeout=10,
        )
        result = poller.poll_for_result(correlation_id)
        
        assert result is not None
        assert result["correlation_id"] == str(correlation_id)
        assert result["status"] == "success"
        assert result["result"]["completed"] is True
        assert result["workflow_id"] == "test_workflow"

    @pytest.mark.asyncio
    async def test_poll_for_result_workflow_id_match(
        self, kafka_bootstrap_servers, test_results_topic
    ) -> None:
        """Test result polling with workflow_id matching using real Kafka."""
        correlation_id = uuid4()
        
        # Publish result
        producer = ResultProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=test_results_topic,
        )
        
        try:
            await producer.start()
            
            await producer.publish_result(
                correlation_id=correlation_id,
                workflow_id="test_workflow",
                workflow_run_id="run_123",
                result={"completed": True},
                status="success",
            )
            
            await asyncio.sleep(1)
            
        finally:
            await producer.stop()
        
        # Poll with workflow_id filter
        poller = WorkflowResultPoller(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=test_results_topic,
            timeout=10,
        )
        result = poller.poll_for_result(
            correlation_id, workflow_id="test_workflow"
        )
        
        assert result is not None
        assert result["workflow_id"] == "test_workflow"

    @pytest.mark.asyncio
    async def test_poll_for_result_workflow_id_mismatch(
        self, kafka_bootstrap_servers, test_results_topic
    ) -> None:
        """Test result polling with workflow_id mismatch continues polling using real Kafka."""
        correlation_id = uuid4()
        
        # Publish result with different workflow_id
        producer = ResultProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=test_results_topic,
        )
        
        try:
            await producer.start()
            
            await producer.publish_result(
                correlation_id=correlation_id,
                workflow_id="wrong_workflow",
                workflow_run_id="run_123",
                result={},
                status="success",
            )
            
            await asyncio.sleep(1)
            
        finally:
            await producer.stop()
        
        # Poll with different workflow_id - should not match
        poller = WorkflowResultPoller(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=test_results_topic,
            timeout=2,  # Short timeout
        )
        result = poller.poll_for_result(
            correlation_id, workflow_id="test_workflow"
        )
        
        # Should timeout and return None due to workflow_id mismatch
        assert result is None

    def test_poll_for_result_no_match(
        self, kafka_bootstrap_servers, test_results_topic
    ) -> None:
        """Test result polling when no matching result found using real Kafka."""
        correlation_id = uuid4()
        
        # Don't publish any result - poll should timeout
        poller = WorkflowResultPoller(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=test_results_topic,
            timeout=2,  # Short timeout for test
        )
        result = poller.poll_for_result(correlation_id)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_poll_for_result_error_status(
        self, kafka_bootstrap_servers, test_results_topic
    ) -> None:
        """Test result polling returns error status results using real Kafka."""
        correlation_id = uuid4()
        
        # Publish error result
        producer = ResultProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=test_results_topic,
        )
        
        try:
            await producer.start()
            
            await producer.publish_result(
                correlation_id=correlation_id,
                workflow_id="test_workflow",
                workflow_run_id="run_123",
                result={},
                status="error",
                error="Workflow execution failed",
            )
            
            await asyncio.sleep(1)
            
        finally:
            await producer.stop()
        
        # Poll for error result
        poller = WorkflowResultPoller(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=test_results_topic,
            timeout=10,
        )
        result = poller.poll_for_result(correlation_id)
        
        assert result is not None
        assert result["status"] == "error"
        assert result["error"] == "Workflow execution failed"

    @pytest.mark.asyncio
    async def test_poll_for_result_multiple_results(
        self, kafka_bootstrap_servers, test_results_topic
    ) -> None:
        """Test result polling with multiple results matches correct correlation_id using real Kafka."""
        correlation_id_1 = uuid4()
        correlation_id_2 = uuid4()
        
        # Publish two results
        producer = ResultProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=test_results_topic,
        )
        
        try:
            await producer.start()
            
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
            
            await asyncio.sleep(1)
            
        finally:
            await producer.stop()
        
        # Poll for first result
        poller = WorkflowResultPoller(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=test_results_topic,
            timeout=10,
        )
        
        result1 = poller.poll_for_result(correlation_id_1)
        result2 = poller.poll_for_result(correlation_id_2)
        
        assert result1 is not None
        assert result1["correlation_id"] == str(correlation_id_1)
        assert result1["workflow_id"] == "test_workflow_1"
        
        assert result2 is not None
        assert result2["correlation_id"] == str(correlation_id_2)
        assert result2["workflow_id"] == "test_workflow_2"
