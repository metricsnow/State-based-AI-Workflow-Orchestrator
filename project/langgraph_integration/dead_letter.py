"""Dead letter queue for failed workflow events.

This module provides a dead letter queue (DLQ) producer for publishing
failed workflow events that could not be processed after retries.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

logger = logging.getLogger(__name__)


class DeadLetterQueue:
    """Dead letter queue for failed events.
    
    Publishes failed workflow events to a dedicated Kafka topic for manual
    investigation and potential reprocessing. Each DLQ event includes the
    original event, error details, retry count, and context information.
    
    Attributes:
        bootstrap_servers: Kafka broker addresses (comma-separated)
        topic: Kafka topic name for dead letter queue
        producer: AIOKafkaProducer instance (created on start)
    """
    
    def __init__(
        self,
        bootstrap_servers: Optional[str] = None,
        topic: Optional[str] = None,
    ):
        """Initialize dead letter queue.
        
        Args:
            bootstrap_servers: Kafka broker addresses. If None, reads from
                KAFKA_BOOTSTRAP_SERVERS environment variable or defaults to
                'localhost:9092'
            topic: Kafka topic name for DLQ. If None, reads from
                KAFKA_DLQ_TOPIC environment variable or defaults to
                'workflow-events-dlq'
        """
        self.bootstrap_servers = (
            bootstrap_servers
            or os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        )
        self.topic = (
            topic
            or os.getenv("KAFKA_DLQ_TOPIC", "workflow-events-dlq")
        )
        self.producer: Optional[AIOKafkaProducer] = None
    
    async def start(self) -> None:
        """Start the dead letter queue producer.
        
        Initializes and starts the AIOKafkaProducer with JSON serialization
        for DLQ event values.
        
        Raises:
            KafkaError: If producer fails to start or connect to Kafka.
        """
        try:
            logger.info(
                f"Starting dead letter queue producer for topic: {self.topic}, "
                f"bootstrap_servers: {self.bootstrap_servers}"
            )
            
            # Create producer with JSON serialization
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            
            await self.producer.start()
            
            logger.info(
                f"Dead letter queue producer started successfully for topic: {self.topic}"
            )
        
        except KafkaError as e:
            logger.error(
                f"Failed to start dead letter queue producer: {e}",
                exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error starting dead letter queue producer: {e}",
                exc_info=True
            )
            raise
    
    async def stop(self) -> None:
        """Stop the dead letter queue producer gracefully.
        
        Stops the producer and ensures all pending messages are sent.
        """
        if self.producer:
            try:
                logger.info("Stopping dead letter queue producer...")
                await self.producer.stop()
                logger.info("Dead letter queue producer stopped successfully")
            except Exception as e:
                logger.warning(
                    f"Error stopping dead letter queue producer: {e}",
                    exc_info=True
                )
                # Don't re-raise - we want to ensure cleanup continues
            finally:
                self.producer = None
    
    async def publish_failed_event(
        self,
        original_event: Dict[str, Any],
        error: Exception,
        retry_count: int,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish failed event to dead letter queue.
        
        Creates a DLQ event containing the original event, error details,
        retry count, and context information, then publishes it to the DLQ topic.
        
        Args:
            original_event: Original workflow event that failed (as dictionary)
            error: Exception that caused the failure
            retry_count: Number of retry attempts made before failure
            context: Optional additional context information (e.g., workflow_id)
        
        Raises:
            RuntimeError: If producer not started
            KafkaError: If publish operation fails
        """
        if not self.producer:
            error_msg = "Dead letter queue producer not started. Call start() first."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Create DLQ event structure
        dlq_event = {
            "dlq_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "original_event": original_event,
            "error": {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": None  # Optionally include traceback for debugging
            },
            "retry_count": retry_count,
            "context": context or {}
        }
        
        try:
            # Publish to DLQ topic
            logger.debug(
                f"Publishing failed event to DLQ: {dlq_event['dlq_id']} "
                f"(original event_id: {original_event.get('event_id')})"
            )
            
            record_metadata = await self.producer.send_and_wait(
                self.topic, dlq_event
            )
            
            logger.error(
                f"Published failed event to DLQ: topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}, "
                f"dlq_id={dlq_event['dlq_id']}, "
                f"original event_id={original_event.get('event_id')}"
            )
        
        except KafkaError as e:
            logger.critical(
                f"Failed to publish to DLQ: {e}. "
                f"Original event_id: {original_event.get('event_id')}",
                exc_info=True
            )
            # Last resort: log to file or external system
            # For now, we just log the critical error
            raise
        except Exception as e:
            logger.critical(
                f"Unexpected error publishing to DLQ: {e}. "
                f"Original event_id: {original_event.get('event_id')}",
                exc_info=True
            )
            raise

