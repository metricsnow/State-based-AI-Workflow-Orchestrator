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
        self.processor = WorkflowProcessor()
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
        
        Stops the consumer and leaves the consumer group. Ensures proper
        cleanup of resources and offset commits.
        """
        self.running = False
        
        if self.consumer:
            try:
                logger.info("Stopping Kafka consumer...")
                await self.consumer.stop()
                logger.info("Kafka consumer stopped successfully")
            except Exception as e:
                logger.warning(f"Error stopping consumer: {e}", exc_info=True)
                # Don't re-raise - we want to ensure cleanup continues
    
    async def consume_and_process(self) -> None:
        """Main consumption loop - processes events asynchronously.
        
        Continuously consumes messages from Kafka and processes them
        asynchronously. Each WORKFLOW_TRIGGERED event spawns an async task
        for workflow execution, allowing concurrent processing.
        
        Raises:
            RuntimeError: If consumer not started.
            KafkaError: If Kafka connection errors occur.
        """
        if not self.consumer:
            raise RuntimeError("Consumer not started. Call start() first.")
        
        if not self.running:
            logger.warning("Consumer not running, cannot consume messages")
            return
        
        logger.info("Starting message consumption loop...")
        
        try:
            async for message in self.consumer:
                # Check if we should stop
                if not self.running:
                    logger.info("Consumer stopped, exiting consumption loop")
                    break
                
                try:
                    # Deserialize event data (already deserialized by value_deserializer)
                    event_data = message.value
                    
                    # Validate and create WorkflowEvent
                    event = WorkflowEvent(**event_data)
                    
                    # Only process WORKFLOW_TRIGGERED events
                    if event.event_type == EventType.WORKFLOW_TRIGGERED:
                        logger.debug(
                            f"Received WORKFLOW_TRIGGERED event: {event.event_id}"
                        )
                        # Process event asynchronously (non-blocking)
                        asyncio.create_task(
                            self._process_event_with_error_handling(event)
                        )
                    else:
                        logger.debug(
                            f"Ignoring event type: {event.event_type} "
                            f"for event: {event.event_id}"
                        )
                
                except Exception as e:
                    # Log error but continue processing other messages
                    logger.error(
                        f"Error processing message from topic {message.topic}, "
                        f"partition {message.partition}, offset {message.offset}: {e}",
                        exc_info=True,
                    )
                    # Continue processing - don't stop consumer on single message error
        
        except KafkaError as e:
            logger.error(f"Kafka error in consumption loop: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in consumption loop: {e}", exc_info=True
            )
            raise
    
    async def _process_event_with_error_handling(
        self, event: WorkflowEvent
    ) -> None:
        """Process event with error handling to prevent task failures from stopping consumer.
        
        Wraps workflow processing in error handling to ensure that failures
        in individual workflow executions don't crash the consumer.
        
        Args:
            event: WorkflowEvent to process.
        """
        try:
            await self.processor.process_workflow_event(event)
        except Exception as e:
            # Error already logged in processor, just log here for context
            logger.error(
                f"Failed to process workflow event {event.event_id}: {e}",
                exc_info=True,
            )
            # Don't re-raise - allow consumer to continue processing other events
            # TODO: Consider dead letter queue for failed events (future enhancement)

