"""Tests for LangGraph integration configuration management.

Tests configuration loading from environment variables and defaults.
"""

import os
import pytest

from langgraph_integration.config import ConsumerConfig


class TestConsumerConfig:
    """Test ConsumerConfig initialization and defaults."""

    def test_config_defaults(self) -> None:
        """Test configuration uses sensible defaults."""
        config = ConsumerConfig()
        
        assert config.bootstrap_servers == "localhost:9092"
        assert config.topic == "workflow-events"
        assert config.group_id == "langgraph-consumer-group"
        assert config.auto_offset_reset == "latest"
        assert config.enable_auto_commit is True
        assert config.max_poll_records == 500
        assert config.session_timeout_ms == 30000
        assert config.heartbeat_interval_ms == 3000

    def test_config_from_environment(self, monkeypatch) -> None:
        """Test configuration loads from environment variables."""
        monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        monkeypatch.setenv("KAFKA_WORKFLOW_EVENTS_TOPIC", "custom-topic")
        monkeypatch.setenv("KAFKA_CONSUMER_GROUP_ID", "custom-group")
        monkeypatch.setenv("KAFKA_ENABLE_AUTO_COMMIT", "false")
        
        config = ConsumerConfig()
        
        assert config.bootstrap_servers == "kafka:9092"
        assert config.topic == "custom-topic"
        assert config.group_id == "custom-group"
        assert config.enable_auto_commit is False

    def test_config_explicit_override(self) -> None:
        """Test explicit configuration parameters override defaults."""
        config = ConsumerConfig(
            bootstrap_servers="custom:9092",
            topic="custom-topic",
            group_id="custom-group",
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )
        
        assert config.bootstrap_servers == "custom:9092"
        assert config.topic == "custom-topic"
        assert config.group_id == "custom-group"
        assert config.auto_offset_reset == "earliest"
        assert config.enable_auto_commit is False

    def test_config_to_dict(self) -> None:
        """Test configuration conversion to dictionary."""
        config = ConsumerConfig()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "bootstrap_servers" in config_dict
        assert "group_id" in config_dict
        assert "auto_offset_reset" in config_dict
        assert "enable_auto_commit" in config_dict
        assert config_dict["bootstrap_servers"] == "localhost:9092"

