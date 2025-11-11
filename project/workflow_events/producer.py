"""
Kafka Producer for Workflow Events

This module provides a Kafka producer wrapper for publishing workflow events to Kafka topics.
Implements best practices for reliability, error handling, and connection management.
"""

import json
import logging
from typing import Optional

from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError

from .schema import WorkflowEvent

logger = logging.getLogger(__name__)


class WorkflowEventProducer:
    """Kafka producer for workflow events.

    Provides a wrapper around kafka-python's KafkaProducer with:
    - Event serialization using Pydantic models
    - Error handling and retries
    - Connection management
    - Proper logging

    Attributes:
        bootstrap_servers: Kafka broker address (e.g., 'localhost:9092')
        producer: KafkaProducer instance
    """

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        acks: str = "all",
        retries: int = 3,
        max_in_flight_requests_per_connection: int = 1,
        request_timeout_ms: int = 30000,
        delivery_timeout_ms: int = 120000,
    ):
        """Initialize Kafka producer.

        Args:
            bootstrap_servers: Kafka broker address (default: 'localhost:9092')
            acks: Number of acknowledgments required (default: 'all' for reliability)
            retries: Number of retry attempts (default: 3)
            max_in_flight_requests_per_connection: Max in-flight requests (default: 1)
            request_timeout_ms: Request timeout in milliseconds (default: 30000)
            delivery_timeout_ms: Delivery timeout in milliseconds (default: 120000)

        Raises:
            KafkaError: If connection to Kafka fails
        """
        self.bootstrap_servers = bootstrap_servers
        self.producer: Optional[KafkaProducer] = None
        self._acks = acks
        self._retries = retries
        self._max_in_flight = max_in_flight_requests_per_connection
        self._request_timeout_ms = request_timeout_ms
        self._delivery_timeout_ms = delivery_timeout_ms
        self._connect()

    def _connect(self) -> None:
        """Create Kafka producer connection.

        Raises:
            KafkaError: If connection to Kafka fails
        """
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[self.bootstrap_servers],
                value_serializer=self._serialize_event,
                acks=self._acks,
                retries=self._retries,
                max_in_flight_requests_per_connection=self._max_in_flight,
                request_timeout_ms=self._request_timeout_ms,
                delivery_timeout_ms=self._delivery_timeout_ms,
            )
            logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise KafkaError(f"Failed to connect to Kafka: {e}") from e

    @staticmethod
    def _serialize_event(event_dict: dict) -> bytes:
        """Serialize event dictionary to JSON bytes.

        Args:
            event_dict: Event dictionary from Pydantic model

        Returns:
            JSON-encoded bytes

        Raises:
            ValueError: If serialization fails
        """
        try:
            return json.dumps(event_dict, default=str).encode("utf-8")
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize event: {e}")
            raise ValueError(f"Failed to serialize event: {e}") from e

    def publish_event(
        self, event: WorkflowEvent, topic: str = "workflow-events", timeout: int = 10
    ) -> bool:
        """Publish workflow event to Kafka topic.

        Args:
            event: WorkflowEvent instance to publish
            topic: Kafka topic name (default: 'workflow-events')
            timeout: Timeout in seconds for send confirmation (default: 10)

        Returns:
            True if event was published successfully, False otherwise

        Raises:
            KafkaError: If producer is not connected
            KafkaTimeoutError: If publish operation times out
        """
        if not self.producer:
            error_msg = "Producer not connected"
            logger.error(error_msg)
            raise KafkaError(error_msg)

        try:
            # Serialize event to dict using Pydantic's model_dump
            event_dict = event.model_dump()

            # Publish to Kafka
            future = self.producer.send(topic, value=event_dict)

            # Wait for confirmation
            record_metadata = future.get(timeout=timeout)

            logger.info(
                f"Event published: topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}, "
                f"event_id={event.event_id}"
            )
            return True

        except KafkaTimeoutError as e:
            logger.error(f"Kafka timeout publishing event {event.event_id}: {e}")
            return False
        except KafkaError as e:
            logger.error(f"Kafka error publishing event {event.event_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error publishing event {event.event_id}: {e}")
            return False

    def flush(self, timeout: Optional[float] = None) -> None:
        """Flush all pending messages.

        Args:
            timeout: Timeout in seconds (default: None, waits indefinitely)

        Raises:
            KafkaTimeoutError: If flush operation times out
        """
        if self.producer:
            try:
                self.producer.flush(timeout=timeout)
                logger.debug("Producer flushed successfully")
            except KafkaTimeoutError as e:
                logger.error(f"Flush timeout: {e}")
                raise
            except Exception as e:
                logger.error(f"Error during flush: {e}")
                raise

    def close(self) -> None:
        """Close producer connection.

        Flushes all pending messages before closing.
        """
        if self.producer:
            producer_to_close = self.producer
            self.producer = None  # Set to None first to prevent reuse
            
            try:
                # Flush before closing to ensure all messages are sent
                producer_to_close.flush()
            except Exception as e:
                logger.warning(f"Error during flush before close: {e}")
                # Continue to close even if flush fails
            
            try:
                producer_to_close.close()
                logger.info("Kafka producer closed")
            except Exception as e:
                logger.error(f"Error closing producer: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures producer is closed."""
        self.close()

