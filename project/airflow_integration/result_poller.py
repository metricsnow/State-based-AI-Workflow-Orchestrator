"""Result poller for retrieving workflow results from Kafka.

This module provides a synchronous Kafka consumer for polling workflow results
from the workflow-results topic. Used by Airflow tasks to retrieve results
from LangGraph workflows via correlation ID matching.
"""

import json
import logging
import time
from typing import Any, Dict, Optional
from uuid import UUID

from kafka import KafkaConsumer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class WorkflowResultPoller:
    """Poller for retrieving workflow results from Kafka.
    
    Provides a synchronous polling mechanism for Airflow tasks to retrieve
    workflow results from the workflow-results Kafka topic. Uses correlation
    IDs to match results with original trigger events.
    
    Attributes:
        bootstrap_servers: Kafka broker addresses (comma-separated)
        topic: Kafka topic name for results (default: 'workflow-results')
        timeout: Timeout in seconds for result retrieval (default: 300)
        poll_interval: Interval in seconds between poll attempts (default: 1.0)
    """
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "workflow-results",
        timeout: int = 300,
        poll_interval: float = 1.0,
    ):
        """Initialize result poller.
        
        Args:
            bootstrap_servers: Kafka broker addresses (default: 'localhost:9092')
            topic: Kafka topic name for results (default: 'workflow-results')
            timeout: Timeout in seconds for result retrieval (default: 300)
            poll_interval: Interval in seconds between poll attempts (default: 1.0)
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.timeout = timeout
        self.poll_interval = poll_interval
    
    def poll_for_result(
        self,
        correlation_id: UUID,
        workflow_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Poll for workflow result with correlation ID.
        
        Creates a Kafka consumer and polls for a result message matching the
        correlation ID. Optionally matches workflow_id if provided. Returns
        None if timeout is reached or no matching result is found.
        
        Args:
            correlation_id: Event ID from the original trigger event
            workflow_id: Optional workflow ID to match (for additional validation)
        
        Returns:
            Dictionary containing result data if found, None if timeout or not found
        
        Raises:
            KafkaError: If Kafka connection or consumer errors occur
        """
        consumer = None
        
        try:
            logger.info(
                f"Polling for result with correlation_id: {correlation_id}, "
                f"timeout: {self.timeout}s"
            )
            
            # Create consumer with JSON deserialization
            consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=[self.bootstrap_servers],
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="latest",
                consumer_timeout_ms=self.timeout * 1000,
                enable_auto_commit=False,  # Don't commit offsets for polling
            )
            
            start_time = time.time()
            correlation_id_str = str(correlation_id)
            
            # Poll for messages until timeout or result found
            for message in consumer:
                # Check timeout
                elapsed_time = time.time() - start_time
                if elapsed_time > self.timeout:
                    logger.warning(
                        f"Timeout waiting for result: correlation_id={correlation_id}, "
                        f"elapsed={elapsed_time:.2f}s"
                    )
                    return None
                
                try:
                    result_data = message.value
                    
                    # Match correlation ID
                    result_correlation_id = result_data.get("correlation_id")
                    if result_correlation_id != correlation_id_str:
                        # Not our message, continue polling
                        continue
                    
                    # Optional: match workflow_id if provided
                    if workflow_id:
                        result_workflow_id = result_data.get("workflow_id")
                        if result_workflow_id != workflow_id:
                            logger.debug(
                                f"Workflow ID mismatch: expected={workflow_id}, "
                                f"got={result_workflow_id}, continuing..."
                            )
                            continue
                    
                    # Found matching result
                    logger.info(
                        f"Result found for correlation_id: {correlation_id}, "
                        f"status: {result_data.get('status')}, "
                        f"elapsed: {elapsed_time:.2f}s"
                    )
                    return result_data
                
                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(
                        f"Error parsing result message: {e}, continuing..."
                    )
                    continue
                except Exception as e:
                    logger.error(
                        f"Unexpected error processing message: {e}", exc_info=True
                    )
                    continue
            
            # Consumer timeout reached (no more messages)
            logger.warning(
                f"Result not found for correlation_id: {correlation_id}, "
                f"timeout: {self.timeout}s"
            )
            return None
        
        except KafkaError as e:
            logger.error(
                f"Kafka error polling for result: correlation_id={correlation_id}, "
                f"error={e}",
                exc_info=True,
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error polling for result: correlation_id={correlation_id}, "
                f"error={e}",
                exc_info=True,
            )
            raise
        finally:
            if consumer:
                try:
                    consumer.close()
                except Exception as e:
                    logger.warning(f"Error closing consumer: {e}")

