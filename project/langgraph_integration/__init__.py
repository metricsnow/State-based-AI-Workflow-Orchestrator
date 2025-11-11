"""LangGraph Integration Module

This module provides async Kafka consumer integration for LangGraph workflows.
It enables event-driven workflow execution by consuming workflow events from Kafka
and triggering LangGraph workflows asynchronously.

Example:
    ```python
    from langgraph_integration.service import main
    import asyncio
    
    # Run the consumer service
    asyncio.run(main())
    ```
"""

from langgraph_integration.consumer import LangGraphKafkaConsumer
from langgraph_integration.processor import WorkflowProcessor
from langgraph_integration.config import ConsumerConfig

__all__ = [
    "LangGraphKafkaConsumer",
    "WorkflowProcessor",
    "ConsumerConfig",
]

