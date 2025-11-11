"""
Kafka Consumer for Workflow Events

This module provides a Kafka consumer wrapper for consuming workflow events from Kafka topics.
Implements best practices for reliability, error handling, offset management, and event deserialization.
"""

import json
import logging
from typing import Callable, Optional, List

from kafka import KafkaConsumer
from kafka.errors import KafkaError, KafkaTimeoutError
from kafka.structs import TopicPartition

from .schema import WorkflowEvent

logger = logging.getLogger(__name__)


class WorkflowEventConsumer:
    """Kafka consumer for workflow events.

    Provides a wrapper around kafka-python's KafkaConsumer with:
    - Event deserialization using Pydantic models
    - Error handling and graceful degradation
    - Consumer group support
    - Offset management
    - Proper logging

    Attributes:
        bootstrap_servers: Kafka broker address (e.g., 'localhost:9092')
        group_id: Consumer group ID (optional)
        auto_offset_reset: Offset reset policy ('earliest', 'latest', 'none')
        enable_auto_commit: Whether to auto-commit offsets
        consumer: KafkaConsumer instance
    """

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        group_id: Optional[str] = None,
        auto_offset_reset: str = "earliest",
        enable_auto_commit: bool = True,
        consumer_timeout_ms: int = 1000,
        max_poll_records: Optional[int] = None,
    ):
        """Initialize Kafka consumer.

        Args:
            bootstrap_servers: Kafka broker address (default: 'localhost:9092')
            group_id: Consumer group ID (optional, enables consumer groups)
            auto_offset_reset: Offset reset policy (default: 'earliest')
            enable_auto_commit: Whether to auto-commit offsets (default: True)
            consumer_timeout_ms: Consumer timeout in milliseconds (default: 1000)
            max_poll_records: Maximum number of records per poll (optional)

        Raises:
            KafkaError: If connection to Kafka fails
        """
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset
        self.enable_auto_commit = enable_auto_commit
        self.consumer_timeout_ms = consumer_timeout_ms
        self.max_poll_records = max_poll_records
        self.consumer: Optional[KafkaConsumer] = None
        self._connect()

    def _connect(self) -> None:
        """Create Kafka consumer connection.

        Raises:
            KafkaError: If connection to Kafka fails
        """
        try:
            config = {
                "bootstrap_servers": [self.bootstrap_servers],
                "value_deserializer": self._deserialize_event,
                "auto_offset_reset": self.auto_offset_reset,
                "enable_auto_commit": self.enable_auto_commit,
                "consumer_timeout_ms": self.consumer_timeout_ms,
            }

            if self.group_id:
                config["group_id"] = self.group_id

            if self.max_poll_records:
                config["max_poll_records"] = self.max_poll_records

            self.consumer = KafkaConsumer(**config)
            logger.info(
                f"Connected to Kafka at {self.bootstrap_servers}"
                + (f" (group_id: {self.group_id})" if self.group_id else "")
            )
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise KafkaError(f"Failed to connect to Kafka: {e}") from e

    @staticmethod
    def _deserialize_event(message_bytes: bytes) -> dict:
        """Deserialize JSON bytes to event dictionary.

        Args:
            message_bytes: JSON-encoded bytes from Kafka

        Returns:
            Event dictionary

        Raises:
            ValueError: If deserialization fails
        """
        try:
            return json.loads(message_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Failed to deserialize event: {e}")
            raise ValueError(f"Failed to deserialize event: {e}") from e

    def subscribe(self, topics: List[str]) -> None:
        """Subscribe to Kafka topics.

        Args:
            topics: List of topic names to subscribe to

        Raises:
            KafkaError: If consumer is not connected
        """
        if not self.consumer:
            error_msg = "Consumer not connected"
            logger.error(error_msg)
            raise KafkaError(error_msg)

        try:
            self.consumer.subscribe(topics)
            logger.info(f"Subscribed to topics: {topics}")
        except Exception as e:
            logger.error(f"Failed to subscribe to topics {topics}: {e}")
            raise KafkaError(f"Failed to subscribe to topics: {e}") from e

    def consume_events(
        self,
        callback: Callable[[WorkflowEvent], None],
        topics: List[str],
        timeout_ms: Optional[int] = None,
    ) -> None:
        """Consume events and call callback for each event.

        Args:
            callback: Function to call for each consumed event
            topics: List of topic names to consume from
            timeout_ms: Optional timeout in milliseconds (overrides consumer_timeout_ms)

        Raises:
            KafkaError: If consumer is not connected or subscription fails
            ValueError: If event deserialization fails
        """
        if not self.consumer:
            error_msg = "Consumer not connected"
            logger.error(error_msg)
            raise KafkaError(error_msg)

        self.subscribe(topics)

        # Use provided timeout or default
        timeout = timeout_ms if timeout_ms is not None else self.consumer_timeout_ms

        try:
            for message in self.consumer:
                try:
                    # Deserialize event dictionary
                    event_dict = message.value

                    # Validate and create WorkflowEvent from dict
                    event = WorkflowEvent.model_validate(event_dict)

                    # Process event via callback
                    callback(event)

                    logger.debug(
                        f"Processed event: {event.event_id} "
                        f"(topic={message.topic}, partition={message.partition}, offset={message.offset})"
                    )

                except ValueError as e:
                    # Deserialization/validation error - log and continue
                    logger.error(
                        f"Error deserializing/validating event: {e} "
                        f"(topic={message.topic}, partition={message.partition}, offset={message.offset})"
                    )
                    # Continue processing other events
                    continue
                except Exception as e:
                    # Callback error - log and continue
                    logger.error(
                        f"Error processing event in callback: {e} "
                        f"(topic={message.topic}, partition={message.partition}, offset={message.offset})"
                    )
                    # Continue processing other events
                    continue

        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        except StopIteration:
            # Consumer timeout - this is expected behavior
            logger.debug("Consumer timeout reached")
        except Exception as e:
            logger.error(f"Consumer error: {e}")
            raise KafkaError(f"Consumer error: {e}") from e

    def poll(self, timeout_ms: int = 1000) -> dict:
        """Poll for new messages.

        Args:
            timeout_ms: Timeout in milliseconds (default: 1000)

        Returns:
            Dictionary mapping TopicPartition to list of ConsumerRecords

        Raises:
            KafkaError: If consumer is not connected
        """
        if not self.consumer:
            error_msg = "Consumer not connected"
            logger.error(error_msg)
            raise KafkaError(error_msg)

        try:
            return self.consumer.poll(timeout_ms=timeout_ms)
        except Exception as e:
            logger.error(f"Error polling for messages: {e}")
            raise KafkaError(f"Error polling for messages: {e}") from e

    def commit(self, offsets: Optional[dict] = None) -> None:
        """Commit offsets.

        Args:
            offsets: Optional dictionary of TopicPartition to OffsetAndMetadata
                     If None, commits current position

        Raises:
            KafkaError: If consumer is not connected or commit fails
        """
        if not self.consumer:
            error_msg = "Consumer not connected"
            logger.error(error_msg)
            raise KafkaError(error_msg)

        try:
            if offsets:
                self.consumer.commit(offsets=offsets)
                logger.debug(f"Committed offsets: {offsets}")
            else:
                self.consumer.commit()
                logger.debug("Committed current position")
        except Exception as e:
            logger.error(f"Error committing offsets: {e}")
            raise KafkaError(f"Error committing offsets: {e}") from e

    def seek(self, partition: TopicPartition, offset: int) -> None:
        """Seek to a specific offset in a partition.

        Args:
            partition: TopicPartition to seek in
            offset: Offset to seek to

        Raises:
            KafkaError: If consumer is not connected
        """
        if not self.consumer:
            error_msg = "Consumer not connected"
            logger.error(error_msg)
            raise KafkaError(error_msg)

        try:
            self.consumer.seek(partition, offset)
            logger.info(f"Seeked to offset {offset} in partition {partition}")
        except Exception as e:
            logger.error(f"Error seeking to offset: {e}")
            raise KafkaError(f"Error seeking to offset: {e}") from e

    def position(self, partition: TopicPartition) -> int:
        """Get current position (offset) for a partition.

        Args:
            partition: TopicPartition to get position for

        Returns:
            Current offset

        Raises:
            KafkaError: If consumer is not connected
        """
        if not self.consumer:
            error_msg = "Consumer not connected"
            logger.error(error_msg)
            raise KafkaError(error_msg)

        try:
            return self.consumer.position(partition)
        except Exception as e:
            logger.error(f"Error getting position: {e}")
            raise KafkaError(f"Error getting position: {e}") from e

    def close(self, timeout_ms: Optional[int] = None) -> None:
        """Close consumer connection.

        Args:
            timeout_ms: Optional timeout in milliseconds for closing
        """
        if self.consumer:
            consumer_to_close = self.consumer
            self.consumer = None  # Set to None first to prevent reuse

            try:
                consumer_to_close.close(timeout_ms=timeout_ms)
                logger.info("Kafka consumer closed")
            except Exception as e:
                logger.error(f"Error closing consumer: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures consumer is closed."""
        self.close()

