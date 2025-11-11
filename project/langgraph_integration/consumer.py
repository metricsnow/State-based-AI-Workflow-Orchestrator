"""Async Kafka consumer for LangGraph workflow events.

This module provides an async Kafka consumer that consumes workflow events
from Kafka and triggers LangGraph workflows asynchronously.
"""

import asyncio
import json
import logging
from typing import Optional

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

from workflow_events import WorkflowEvent, EventType
from langgraph_integration.processor import WorkflowProcessor
from langgraph_integration.config import ConsumerConfig
from langgraph_integration.result_producer import ResultProducer
from langgraph_integration.retry import retry_async, RetryConfig, is_transient_error
from langgraph_integration.dead_letter import DeadLetterQueue

logger = logging.getLogger(__name__)


class LangGraphKafkaConsumer:
    """Async Kafka consumer for LangGraph workflow events.
    
    This consumer subscribes to workflow events from Kafka and triggers
    LangGraph workflows asynchronously. It uses aiokafka for non-blocking
    event consumption and processes events concurrently.
    
    Attributes:
        config: ConsumerConfig with Kafka connection settings.
        consumer: AIOKafkaConsumer instance (created on start).
        processor: WorkflowProcessor for executing LangGraph workflows.
        running: Boolean flag indicating if consumer is running.
    """
    
    def __init__(self, config: Optional[ConsumerConfig] = None):
        """Initialize async Kafka consumer.
        
        Args:
            config: ConsumerConfig instance. If None, creates default config
                from environment variables.
        """
        self.config = config or ConsumerConfig()
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.result_producer = ResultProducer(
            bootstrap_servers=self.config.bootstrap_servers
        )
        self.processor = WorkflowProcessor(result_producer=self.result_producer)
        self.dlq = DeadLetterQueue(
            bootstrap_servers=self.config.bootstrap_servers
        )
        self.retry_config = RetryConfig(max_retries=3)
        self.running = False
    
    async def start(self) -> None:
        """Start the consumer service.
        
        Initializes and starts the AIOKafkaConsumer with configuration
        from ConsumerConfig. Sets up JSON deserialization for event values.
        
        Raises:
            KafkaError: If consumer fails to start or connect to Kafka.
        """
        try:
            logger.info(
                f"Starting Kafka consumer for topic: {self.config.topic}, "
                f"group: {self.config.group_id}"
            )
            
            # Create consumer with JSON deserialization
            self.consumer = AIOKafkaConsumer(
                self.config.topic,
                bootstrap_servers=self.config.bootstrap_servers,
                group_id=self.config.group_id,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset=self.config.auto_offset_reset,
                enable_auto_commit=self.config.enable_auto_commit,
                max_poll_records=self.config.max_poll_records,
                session_timeout_ms=self.config.session_timeout_ms,
                heartbeat_interval_ms=self.config.heartbeat_interval_ms,
            )
            
            await self.consumer.start()
            
            # Start result producer
            await self.result_producer.start()
            
            # Start dead letter queue producer
            await self.dlq.start()
            
            self.running = True
            
            logger.info(
                f"Kafka consumer started successfully for topic: {self.config.topic}"
            )
        
        except KafkaError as e:
            logger.error(f"Failed to start Kafka consumer: {e}", exc_info=True)
            self.running = False
            raise
        except Exception as e:
            logger.error(f"Unexpected error starting consumer: {e}", exc_info=True)
            self.running = False
            raise
    
    async def stop(self) -> None:
        """Stop the consumer service gracefully.
        
        Stops the consumer, result producer, and dead letter queue producer,
        and leaves the consumer group. Ensures proper cleanup of resources
        and offset commits.
        """
        import sys
        import time
        
        def print_status(msg: str):
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            print(f"[{timestamp}] STOP: {msg}", file=sys.stderr, flush=True)
        
        print_status("Starting consumer stop sequence")
        self.running = False
        
        # Stop dead letter queue producer
        print_status("Stopping dead letter queue producer...")
        try:
            await self.dlq.stop()
            print_status("Dead letter queue producer stopped")
        except Exception as e:
            print_status(f"ERROR stopping dead letter queue: {e}")
            logger.warning(f"Error stopping dead letter queue: {e}", exc_info=True)
        
        # Stop result producer
        print_status("Stopping result producer...")
        try:
            await self.result_producer.stop()
            print_status("Result producer stopped")
        except Exception as e:
            print_status(f"ERROR stopping result producer: {e}")
            logger.warning(f"Error stopping result producer: {e}", exc_info=True)
        
        # Stop consumer with timeout to prevent infinite hangs
        if self.consumer:
            print_status("Stopping Kafka consumer...")
            try:
                logger.info("Stopping Kafka consumer...")
                # Add timeout to prevent infinite hangs on offset commit
                await asyncio.wait_for(self.consumer.stop(), timeout=5.0)
                print_status("Kafka consumer stopped successfully")
                logger.info("Kafka consumer stopped successfully")
            except asyncio.TimeoutError:
                print_status("WARNING: Consumer stop timed out after 5s, forcing close")
                logger.warning("Consumer stop timed out, forcing close")
                try:
                    # Force close the consumer
                    if hasattr(self.consumer, '_coordinator'):
                        print_status("Closing coordinator...")
                    await asyncio.wait_for(self.consumer.close(), timeout=2.0)
                    print_status("Consumer force-closed")
                except Exception as e2:
                    print_status(f"ERROR force-closing consumer: {e2}")
                    logger.warning(f"Error force-closing consumer: {e2}", exc_info=True)
            except Exception as e:
                print_status(f"ERROR stopping consumer: {e}")
                logger.warning(f"Error stopping consumer: {e}", exc_info=True)
                # Don't re-raise - we want to ensure cleanup continues
        
        print_status("Consumer stop sequence complete")
    
    async def consume_and_process(self) -> None:
        """Main consumption loop - processes events asynchronously.
        
        Continuously consumes messages from Kafka and processes them
        asynchronously. Each WORKFLOW_TRIGGERED event spawns an async task
        for workflow execution, allowing concurrent processing.
        
        Uses timeout-based polling to allow cancellation checks between
        message fetches, preventing indefinite blocking.
        
        Raises:
            RuntimeError: If consumer not started.
            KafkaError: If Kafka connection errors occur.
        """
        import sys
        import time
        
        def print_status(msg: str):
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            print(f"[{timestamp}] CONSUMER: {msg}", file=sys.stderr, flush=True)
        
        if not self.consumer:
            print_status("ERROR: Consumer not started")
            raise RuntimeError("Consumer not started. Call start() first.")
        
        if not self.running:
            print_status("WARNING: Consumer not running, cannot consume messages")
            logger.warning("Consumer not running, cannot consume messages")
            return
        
        print_status("Starting message consumption loop...")
        logger.info("Starting message consumption loop...")
        
        # Poll timeout - allows checking self.running between fetches
        poll_timeout_ms = 1000  # 1 second
        iteration = 0
        
        try:
            while self.running:
                iteration += 1
                print_status(f"Loop iteration {iteration}, running={self.running}")
                
                try:
                    print_status(f"Calling getmany(timeout_ms={poll_timeout_ms}, max_records=10)")
                    # Use getmany with timeout to allow cancellation checks
                    # This prevents indefinite blocking
                    messages = await asyncio.wait_for(
                        self.consumer.getmany(timeout_ms=poll_timeout_ms, max_records=10),
                        timeout=1.5  # Slightly longer than poll_timeout_ms
                    )
                    print_status(f"getmany returned: {len(messages)} topic partitions")
                    
                    if not messages:
                        print_status("No messages in this batch, continuing...")
                        continue
                    
                    # Process all messages in this batch
                    total_messages = sum(len(msgs) for msgs in messages.values())
                    print_status(f"Processing {total_messages} messages from {len(messages)} partitions")
                    
                    for topic_partition, partition_messages in messages.items():
                        print_status(f"Processing partition {topic_partition}: {len(partition_messages)} messages")
                        for message in partition_messages:
                            # Check if we should stop before processing
                            if not self.running:
                                print_status("Consumer stopped flag detected, exiting")
                                logger.info("Consumer stopped, exiting consumption loop")
                                return
                            
                            print_status(f"Processing message: topic={message.topic}, partition={message.partition}, offset={message.offset}")
                            
                            try:
                                # Deserialize event data (already deserialized by value_deserializer)
                                event_data = message.value
                                print_status(f"Deserialized event data: {type(event_data)}")
                                
                                # Validate and create WorkflowEvent
                                event = WorkflowEvent(**event_data)
                                print_status(f"Created WorkflowEvent: id={event.event_id}, type={event.event_type}")
                                
                                # Only process WORKFLOW_TRIGGERED events
                                if event.event_type == EventType.WORKFLOW_TRIGGERED:
                                    print_status(f"Processing WORKFLOW_TRIGGERED event: {event.event_id}")
                                    logger.debug(
                                        f"Received WORKFLOW_TRIGGERED event: {event.event_id}"
                                    )
                                    # Process event asynchronously (non-blocking)
                                    asyncio.create_task(
                                        self._process_event_with_error_handling(event)
                                    )
                                    print_status(f"Created async task for event: {event.event_id}")
                                else:
                                    print_status(f"Ignoring event type: {event.event_type}")
                                    logger.debug(
                                        f"Ignoring event type: {event.event_type} "
                                        f"for event: {event.event_id}"
                                    )
                            
                            except Exception as e:
                                # Log error but continue processing other messages
                                print_status(f"ERROR processing message: {e}")
                                logger.error(
                                    f"Error processing message from topic {message.topic}, "
                                    f"partition {message.partition}, offset {message.offset}: {e}",
                                    exc_info=True,
                                )
                                # Continue processing - don't stop consumer on single message error
                
                except asyncio.TimeoutError:
                    # Timeout is expected - continue loop to check self.running
                    print_status(f"Timeout waiting for messages (iteration {iteration}), continuing...")
                    continue
                except KafkaError as e:
                    print_status(f"Kafka error: {e}")
                    logger.error(f"Kafka error in consumption loop: {e}", exc_info=True)
                    raise
        
        except asyncio.CancelledError:
            print_status("Consumption loop cancelled")
            logger.info("Consumption loop cancelled")
            raise
        except KafkaError as e:
            print_status(f"Kafka error (outer): {e}")
            logger.error(f"Kafka error in consumption loop: {e}", exc_info=True)
            raise
        except Exception as e:
            print_status(f"Unexpected error: {e}")
            logger.error(
                f"Unexpected error in consumption loop: {e}", exc_info=True
            )
            raise
        finally:
            print_status("Exiting consumption loop")
    
    async def _process_event_with_error_handling(
        self, event: WorkflowEvent
    ) -> None:
        """Process event with retry and error handling.
        
        Wraps workflow processing in retry logic with exponential backoff.
        On failure after retries, publishes to dead letter queue and publishes
        error result. Ensures that failures in individual workflow executions
        don't crash the consumer.
        
        Args:
            event: WorkflowEvent to process.
        """
        try:
            # Retry with exponential backoff
            result = await retry_async(
                self.processor.process_workflow_event,
                event,
                config=self.retry_config
            )
            return result
        
        except Exception as e:
            logger.error(
                f"Failed to process workflow event {event.event_id} "
                f"after {self.retry_config.max_retries} retries: {e}",
                exc_info=True,
            )
            
            # Publish to dead letter queue
            try:
                await self.dlq.publish_failed_event(
                    original_event=event.model_dump(mode="json"),
                    error=e,
                    retry_count=self.retry_config.max_retries,
                    context={
                        "workflow_id": event.workflow_id,
                        "workflow_run_id": event.workflow_run_id,
                    }
                )
            except Exception as dlq_error:
                logger.critical(
                    f"Failed to publish to dead letter queue for event "
                    f"{event.event_id}: {dlq_error}",
                    exc_info=True,
                )
            
            # Publish error result to result topic
            try:
                await self.result_producer.publish_result(
                    correlation_id=event.event_id,
                    workflow_id=event.workflow_id,
                    workflow_run_id=event.workflow_run_id,
                    result={},
                    status="error",
                    error=f"Processing failed after {self.retry_config.max_retries} retries: {str(e)}"
                )
            except Exception as result_error:
                logger.error(
                    f"Failed to publish error result for event {event.event_id}: {result_error}",
                    exc_info=True,
                )
            
            # Don't re-raise - allow consumer to continue processing other events

