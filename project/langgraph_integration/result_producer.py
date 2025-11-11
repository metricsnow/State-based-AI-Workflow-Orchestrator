"""Async result producer for publishing workflow results to Kafka.

This module provides an async Kafka producer for publishing workflow results
to the workflow-results topic. Results include correlation IDs for matching
with original trigger events.
"""

import json
import logging
import os
from typing import Any, Dict, Optional
from uuid import UUID

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError, KafkaTimeoutError

from workflow_events import WorkflowResultEvent

logger = logging.getLogger(__name__)


class ResultProducer:
    """Async producer for workflow results.
    
    Publishes workflow execution results to the workflow-results Kafka topic.
    Results include correlation IDs (from original trigger events) for matching
    requests to responses in Airflow tasks.
    
    Attributes:
        bootstrap_servers: Kafka broker addresses (comma-separated)
        topic: Kafka topic name for results (default: 'workflow-results')
        producer: AIOKafkaProducer instance (created on start)
    """
    
    def __init__(
        self,
        bootstrap_servers: Optional[str] = None,
        topic: Optional[str] = None,
    ):
        """Initialize async result producer.
        
        Args:
            bootstrap_servers: Kafka broker addresses. If None, reads from
                KAFKA_BOOTSTRAP_SERVERS environment variable or defaults to
                'localhost:9092'
            topic: Kafka topic name for results. If None, reads from
                KAFKA_WORKFLOW_RESULTS_TOPIC environment variable or defaults
                to 'workflow-results'
        """
        self.bootstrap_servers = (
            bootstrap_servers
            or os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        )
        self.topic = (
            topic
            or os.getenv("KAFKA_WORKFLOW_RESULTS_TOPIC", "workflow-results")
        )
        self.producer: Optional[AIOKafkaProducer] = None
    
    async def start(self) -> None:
        """Start the producer.
        
        Initializes and starts the AIOKafkaProducer with JSON serialization
        for result event values.
        
        Raises:
            KafkaError: If producer fails to start or connect to Kafka.
        """
        try:
            logger.info(
                f"Starting result producer for topic: {self.topic}, "
                f"bootstrap_servers: {self.bootstrap_servers}"
            )
            
            # Create producer with JSON serialization
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            
            await self.producer.start()
            
            logger.info(
                f"Result producer started successfully for topic: {self.topic}"
            )
        
        except KafkaError as e:
            logger.error(f"Failed to start result producer: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error starting result producer: {e}", exc_info=True
            )
            raise
    
    async def stop(self) -> None:
        """Stop the producer gracefully.
        
        Stops the producer and ensures all pending messages are sent.
        """
        if self.producer:
            try:
                logger.info("Stopping result producer...")
                await self.producer.stop()
                logger.info("Result producer stopped successfully")
            except Exception as e:
                logger.warning(f"Error stopping result producer: {e}", exc_info=True)
                # Don't re-raise - we want to ensure cleanup continues
            finally:
                self.producer = None
    
    async def publish_result(
        self,
        correlation_id: UUID,
        workflow_id: str,
        workflow_run_id: str,
        result: Dict[str, Any],
        status: str = "success",
        error: Optional[str] = None,
    ) -> None:
        """Publish workflow result to result topic.
        
        Creates a WorkflowResultEvent and publishes it to the workflow-results
        topic. The correlation_id matches the original trigger event's event_id,
        allowing Airflow tasks to match requests to responses.
        
        Args:
            correlation_id: Event ID from the original trigger event
            workflow_id: Identifier of the workflow
            workflow_run_id: Identifier of the specific workflow run
            result: Workflow result data dictionary
            status: Result status ('success', 'failure', 'error')
            error: Optional error message if status is 'error'
        
        Raises:
            RuntimeError: If producer not started
            KafkaError: If publish operation fails
            KafkaTimeoutError: If publish operation times out
        """
        if not self.producer:
            error_msg = "Producer not started. Call start() first."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        try:
            # Create result event
            result_event = WorkflowResultEvent(
                correlation_id=correlation_id,
                workflow_id=workflow_id,
                workflow_run_id=workflow_run_id,
                result=result,
                status=status,
                error=error,
            )
            
            # Serialize event to dict for JSON encoding
            event_dict = result_event.model_dump(mode="json")
            
            # Publish to Kafka
            logger.debug(
                f"Publishing result for correlation_id: {correlation_id}, "
                f"status: {status}"
            )
            
            # Use send_and_wait for reliable delivery
            record_metadata = await self.producer.send_and_wait(
                self.topic, event_dict
            )
            
            logger.info(
                f"Result published: topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}, "
                f"correlation_id={correlation_id}"
            )
        
        except KafkaTimeoutError as e:
            logger.error(
                f"Kafka timeout publishing result for correlation_id "
                f"{correlation_id}: {e}",
                exc_info=True,
            )
            raise
        except KafkaError as e:
            logger.error(
                f"Kafka error publishing result for correlation_id "
                f"{correlation_id}: {e}",
                exc_info=True,
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error publishing result for correlation_id "
                f"{correlation_id}: {e}",
                exc_info=True,
            )
            raise

