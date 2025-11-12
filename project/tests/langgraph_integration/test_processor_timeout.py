"""Unit tests for processor timeout handling."""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from workflow_events import (
    WorkflowEvent,
    EventType,
    EventSource,
    WorkflowEventPayload,
    WorkflowEventMetadata,
)
from langgraph_integration.processor import WorkflowProcessor
from langgraph_integration.result_producer import ResultProducer


class TestProcessorTimeout:
    """Tests for processor timeout handling."""
    
    @pytest.mark.asyncio
    async def test_workflow_timeout_raises_timeout_error(self):
        """Test that workflow timeout raises TimeoutError."""
        # Create a mock result producer
        result_producer = AsyncMock(spec=ResultProducer)
        result_producer.publish_result = AsyncMock()
        
        # Create processor with short timeout
        processor = WorkflowProcessor(
            result_producer=result_producer,
            workflow_timeout=0.1  # 100ms timeout
        )
        
        # Create test event
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test-workflow",
            workflow_run_id="test-run-123",
            payload=WorkflowEventPayload(data={"task": "test"}),
            metadata=WorkflowEventMetadata(environment="dev", version="1.0")
        )
        
        # Mock workflow to hang indefinitely
        with patch('langgraph_integration.processor.multi_agent_graph') as mock_graph:
            # Create a mock that hangs
            def hanging_invoke(state, config):
                import time
                # Sleep longer than timeout (but not too long for tests)
                time.sleep(1.0)  # 1s is enough to exceed 0.1s timeout
                return {"completed": True}
            
            mock_graph.invoke = hanging_invoke
            
            # Should raise TimeoutError
            with pytest.raises(TimeoutError) as exc_info:
                await processor.process_workflow_event(event)
            
            assert "timed out" in str(exc_info.value).lower()
            assert "0.1" in str(exc_info.value) or "100" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_workflow_timeout_publishes_error_result(self):
        """Test that timeout publishes error result."""
        # Create a mock result producer
        result_producer = AsyncMock(spec=ResultProducer)
        result_producer.publish_result = AsyncMock()
        
        # Create processor with short timeout
        processor = WorkflowProcessor(
            result_producer=result_producer,
            workflow_timeout=0.1  # 100ms timeout
        )
        
        # Create test event
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test-workflow",
            workflow_run_id="test-run-123",
            payload=WorkflowEventPayload(data={"task": "test"}),
            metadata=WorkflowEventMetadata(environment="dev", version="1.0")
        )
        
        # Mock workflow to hang
        with patch('langgraph_integration.processor.multi_agent_graph') as mock_graph:
            def hanging_invoke(state, config):
                import time
                # Sleep longer than timeout (but not too long for tests)
                time.sleep(1.0)  # 1s is enough to exceed 0.1s timeout
                return {"completed": True}
            
            mock_graph.invoke = hanging_invoke
            
            # Should raise TimeoutError
            with pytest.raises(TimeoutError):
                await processor.process_workflow_event(event)
            
            # Verify error result was published
            result_producer.publish_result.assert_called_once()
            call_args = result_producer.publish_result.call_args
            assert call_args[1]["status"] == "error"
            error_msg = call_args[1]["error"].lower()
            assert "timeout" in error_msg or "timed out" in error_msg
    
    @pytest.mark.asyncio
    async def test_default_timeout_from_environment(self):
        """Test that default timeout is read from environment variable."""
        import os
        
        with patch.dict(os.environ, {"WORKFLOW_EXECUTION_TIMEOUT": "600"}):
            processor = WorkflowProcessor()
            assert processor.workflow_timeout == 600
    
    @pytest.mark.asyncio
    async def test_custom_timeout_override(self):
        """Test that custom timeout overrides environment variable."""
        import os
        
        with patch.dict(os.environ, {"WORKFLOW_EXECUTION_TIMEOUT": "600"}):
            processor = WorkflowProcessor(workflow_timeout=120)
            assert processor.workflow_timeout == 120
    
    @pytest.mark.asyncio
    async def test_successful_workflow_within_timeout(self):
        """Test that successful workflow completes within timeout."""
        # Create a mock result producer
        result_producer = AsyncMock(spec=ResultProducer)
        result_producer.publish_result = AsyncMock()
        
        # Create processor with timeout
        processor = WorkflowProcessor(
            result_producer=result_producer,
            workflow_timeout=5.0
        )
        
        # Create test event
        event = WorkflowEvent(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source=EventSource.AIRFLOW,
            workflow_id="test-workflow",
            workflow_run_id="test-run-123",
            payload=WorkflowEventPayload(data={"task": "test"}),
            metadata=WorkflowEventMetadata(environment="dev", version="1.0")
        )
        
        # Mock workflow to complete quickly
        with patch('langgraph_integration.processor.multi_agent_graph') as mock_graph:
            mock_graph.invoke = MagicMock(return_value={
                "completed": True,
                "agent_results": {},
                "task": "test",
                "metadata": {}
            })
            
            # Should complete successfully
            result = await processor.process_workflow_event(event)
            
            assert result is not None
            assert result.get("completed") is True
            
            # Verify success result was published
            result_producer.publish_result.assert_called_once()
            call_args = result_producer.publish_result.call_args
            assert call_args[1]["status"] == "success"

