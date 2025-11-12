"""Debug version of integration tests with detailed logging."""

import asyncio
import os
import time
import pytest
import sys
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


def print_status(step: str, details: str = ""):
    """Print status with timestamp."""
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{timestamp}] {step}", file=sys.stderr, flush=True)
    if details:
        print(f"  -> {details}", file=sys.stderr, flush=True)


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


class TestConsumerIntegrationDebug:
    """Debug version of integration tests with detailed logging."""

    @pytest.mark.asyncio
    async def test_consumer_start_stop_debug(self, consumer_config):
        """Test consumer can start and stop with detailed logging."""
        print_status("TEST START", f"test_consumer_start_stop_debug")
        print_status("STEP 1", f"Creating consumer with topic: {consumer_config.topic}")
        consumer = LangGraphKafkaConsumer(config=consumer_config)
        
        try:
            print_status("STEP 2", "Starting consumer...")
            await consumer.start()
            print_status("STEP 3", f"Consumer started. Running: {consumer.running}")
            assert consumer.running is True
            assert consumer.consumer is not None
            print_status("STEP 4", "Consumer is running and ready")
        finally:
            print_status("STEP 5", "Stopping consumer...")
            await consumer.stop()
            print_status("STEP 6", f"Consumer stopped. Running: {consumer.running}")
            assert consumer.running is False
        print_status("TEST COMPLETE", "test_consumer_start_stop_debug")

    @pytest.mark.asyncio
    async def test_consumer_processes_event_debug(
        self, consumer_config, kafka_bootstrap_servers
    ):
        """Test consumer processes events with detailed logging."""
        print_status("TEST START", f"test_consumer_processes_event_debug")
        print_status("STEP 1", f"Creating event producer for topic: {consumer_config.topic}")
        
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
        
        print_status("STEP 2", f"Publishing event: {event.event_id}")
        success = producer.publish_event(event, topic=consumer_config.topic)
        print_status("STEP 3", f"Event published: {success}")
        assert success is True
        
        producer.close()
        print_status("STEP 4", "Producer closed")
        
        # Start consumer
        print_status("STEP 5", "Creating consumer...")
        consumer = LangGraphKafkaConsumer(config=consumer_config)
        processed_events = []
        
        # Override processor to capture processed events
        original_process = consumer.processor.process_workflow_event
        
        async def capture_process(event):
            print_status("PROCESSING", f"Processing event: {event.event_id}")
            result = await original_process(event)
            processed_events.append(event.event_id)
            print_status("PROCESSED", f"Event processed: {event.event_id}, total: {len(processed_events)}")
            return result
        
        consumer.processor.process_workflow_event = capture_process
        
        try:
            print_status("STEP 6", "Starting consumer...")
            await consumer.start()
            print_status("STEP 7", f"Consumer started. Running: {consumer.running}")
            
            # Create consumption task
            print_status("STEP 8", "Creating consume_and_process task...")
            consume_task = asyncio.create_task(consumer.consume_and_process())
            print_status("STEP 9", "Consume task created, waiting for events...")
            
            # Wait for event to be processed (with fast timeout)
            fast_poll_interval = float(os.getenv("TEST_POLL_INTERVAL", "0.1"))
            max_iterations = int(os.getenv("TEST_MAX_WAIT_ITERATIONS", "10"))
            
            for i in range(max_iterations):
                print_status("WAIT", f"Waiting... ({i+1}/{max_iterations}), processed: {len(processed_events)}")
                await asyncio.sleep(fast_poll_interval)
                if processed_events:
                    print_status("SUCCESS", f"Event processed! Total: {len(processed_events)}")
                    break
            
            # Cancel consumption
            print_status("STEP 10", "Stopping consumer (setting running=False)...")
            consumer.running = False
            print_status("STEP 11", "Cancelling consume task...")
            consume_task.cancel()
            try:
                print_status("STEP 12", "Waiting for task cancellation...")
                await consume_task
                print_status("STEP 13", "Task cancelled successfully")
            except asyncio.CancelledError:
                print_status("STEP 13", "Task cancellation caught (expected)")
                pass
            
            # Verify event was processed
            print_status("STEP 14", f"Verifying results. Processed events: {len(processed_events)}")
            assert len(processed_events) > 0, f"No events processed. Processed: {processed_events}"
            assert event.event_id in processed_events or str(event.event_id) in [
                str(eid) for eid in processed_events
            ]
            print_status("STEP 15", "Verification passed")
        
        finally:
            print_status("STEP 16", "Stopping consumer...")
            await consumer.stop()
            print_status("STEP 17", f"Consumer stopped. Running: {consumer.running}")
        print_status("TEST COMPLETE", "test_consumer_processes_event_debug")

    @pytest.mark.asyncio
    async def test_result_flow_debug(
        self,
        consumer_config,
        test_results_topic,
        kafka_bootstrap_servers,
    ):
        """Test end-to-end result flow with detailed logging."""
        print_status("TEST START", f"test_result_flow_debug")
        
        # Set result topic for producer
        import os
        original_topic = os.getenv("KAFKA_WORKFLOW_RESULTS_TOPIC")
        os.environ["KAFKA_WORKFLOW_RESULTS_TOPIC"] = test_results_topic
        print_status("STEP 1", f"Set result topic: {test_results_topic}")
        
        try:
            # Create and publish test event
            print_status("STEP 2", "Creating event producer...")
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
            print_status("STEP 3", f"Created event: {correlation_id}")
            
            # Publish event
            print_status("STEP 4", f"Publishing event to topic: {consumer_config.topic}")
            success = producer.publish_event(event, topic=consumer_config.topic)
            print_status("STEP 5", f"Event published: {success}")
            assert success is True
            producer.close()
            print_status("STEP 6", "Producer closed")
            
            # Start consumer
            print_status("STEP 7", "Creating consumer...")
            consumer = LangGraphKafkaConsumer(config=consumer_config)
            
            try:
                print_status("STEP 8", "Starting consumer...")
                await consumer.start()
                print_status("STEP 9", f"Consumer started. Running: {consumer.running}")
                
                # Create consumption task
                print_status("STEP 10", "Creating consume_and_process task...")
                consume_task = asyncio.create_task(consumer.consume_and_process())
                print_status("STEP 11", "Consume task created")
                
                # Give consumer time to process event
                # Fast wait for event processing
                fast_poll_interval = float(os.getenv("TEST_POLL_INTERVAL", "0.1"))
                print_status("STEP 12", f"Waiting {fast_poll_interval * 10:.1f} seconds for event processing...")
                await asyncio.sleep(fast_poll_interval * 10)  # 1s instead of 5s
                print_status("STEP 13", "Wait complete")
                
                # Stop consumer
                print_status("STEP 14", "Stopping consumer...")
                consumer.running = False
                consume_task.cancel()
                try:
                    await consume_task
                except asyncio.CancelledError:
                    pass
                print_status("STEP 15", "Consumer stopped")
                
                # Poll for result
                print_status("STEP 16", f"Creating result poller for topic: {test_results_topic}")
                poller = WorkflowResultPoller(
                    bootstrap_servers=kafka_bootstrap_servers,
                    topic=test_results_topic,
                    timeout=30,
                )
                
                print_status("STEP 17", f"Polling for result with correlation_id: {correlation_id}")
                result = poller.poll_for_result(
                    correlation_id=correlation_id,
                    workflow_id="test_workflow",
                )
                
                print_status("STEP 18", f"Poll result: {result is not None}")
                assert result is not None, "Result should not be None"
                assert result["correlation_id"] == str(correlation_id)
                assert result["workflow_id"] == "test_workflow"
                assert result["status"] == "success"
                print_status("STEP 19", "All assertions passed")
            
            finally:
                print_status("STEP 20", "Stopping consumer in finally...")
                await consumer.stop()
                print_status("STEP 21", "Consumer stopped")
        
        finally:
            # Restore original topic
            print_status("STEP 22", "Restoring environment...")
            if original_topic:
                os.environ["KAFKA_WORKFLOW_RESULTS_TOPIC"] = original_topic
            elif "KAFKA_WORKFLOW_RESULTS_TOPIC" in os.environ:
                del os.environ["KAFKA_WORKFLOW_RESULTS_TOPIC"]
            print_status("STEP 23", "Environment restored")
        print_status("TEST COMPLETE", "test_result_flow_debug")

