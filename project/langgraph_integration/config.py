"""Configuration management for LangGraph Kafka consumer.

This module provides configuration management for the async Kafka consumer service,
loading settings from environment variables with sensible defaults.
"""

import os
from typing import Optional


class ConsumerConfig:
    """Configuration for LangGraph Kafka consumer service.
    
    Loads configuration from environment variables with defaults.
    All settings can be overridden via environment variables.
    
    Attributes:
        bootstrap_servers: Kafka broker addresses (comma-separated)
        topic: Kafka topic to consume from
        group_id: Consumer group ID for offset management
        auto_offset_reset: Offset reset policy ('earliest' or 'latest')
        enable_auto_commit: Whether to auto-commit offsets
        max_poll_records: Maximum number of records per poll
        session_timeout_ms: Session timeout in milliseconds
        heartbeat_interval_ms: Heartbeat interval in milliseconds
    """
    
    def __init__(
        self,
        bootstrap_servers: Optional[str] = None,
        topic: Optional[str] = None,
        group_id: Optional[str] = None,
        auto_offset_reset: Optional[str] = None,
        enable_auto_commit: Optional[bool] = None,
        max_poll_records: Optional[int] = None,
        session_timeout_ms: Optional[int] = None,
        heartbeat_interval_ms: Optional[int] = None,
    ):
        """Initialize configuration with environment variable overrides.
        
        Args:
            bootstrap_servers: Kafka broker addresses (default: KAFKA_BOOTSTRAP_SERVERS or 'localhost:9092')
            topic: Kafka topic name (default: KAFKA_WORKFLOW_EVENTS_TOPIC or 'workflow-events')
            group_id: Consumer group ID (default: KAFKA_CONSUMER_GROUP_ID or 'langgraph-consumer-group')
            auto_offset_reset: Offset reset policy (default: 'latest')
            enable_auto_commit: Auto-commit setting (default: True)
            max_poll_records: Max records per poll (default: 500)
            session_timeout_ms: Session timeout (default: 30000)
            heartbeat_interval_ms: Heartbeat interval (default: 3000)
        """
        self.bootstrap_servers = (
            bootstrap_servers
            or os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        )
        self.topic = (
            topic
            or os.getenv("KAFKA_WORKFLOW_EVENTS_TOPIC", "workflow-events")
        )
        self.group_id = (
            group_id
            or os.getenv("KAFKA_CONSUMER_GROUP_ID", "langgraph-consumer-group")
        )
        self.auto_offset_reset = auto_offset_reset or "latest"
        self.enable_auto_commit = (
            enable_auto_commit
            if enable_auto_commit is not None
            else os.getenv("KAFKA_ENABLE_AUTO_COMMIT", "true").lower() == "true"
        )
        self.max_poll_records = max_poll_records or 500
        self.session_timeout_ms = session_timeout_ms or 30000
        self.heartbeat_interval_ms = heartbeat_interval_ms or 3000
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary for consumer initialization.
        
        Returns:
            Dictionary with consumer configuration parameters.
        """
        return {
            "bootstrap_servers": self.bootstrap_servers,
            "group_id": self.group_id,
            "auto_offset_reset": self.auto_offset_reset,
            "enable_auto_commit": self.enable_auto_commit,
            "max_poll_records": self.max_poll_records,
            "session_timeout_ms": self.session_timeout_ms,
            "heartbeat_interval_ms": self.heartbeat_interval_ms,
        }

