"""Service entry point for LangGraph Kafka consumer.

This module provides the main service entry point for running the async
Kafka consumer as a standalone service. It handles signal handling for
graceful shutdown and service lifecycle management.
"""

import asyncio
import logging
import os
import signal
import sys
from typing import Optional

from langgraph_integration.consumer import LangGraphKafkaConsumer
from langgraph_integration.config import ConsumerConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Global consumer instance for signal handling
consumer: Optional[LangGraphKafkaConsumer] = None


def signal_handler(sig: int, frame) -> None:
    """Handle shutdown signals (SIGINT, SIGTERM).
    
    Sets up graceful shutdown by stopping the consumer when receiving
    termination signals. This allows proper cleanup and offset commits.
    
    Args:
        sig: Signal number.
        frame: Current stack frame.
    """
    logger.info(f"Received signal {sig}, initiating graceful shutdown...")
    if consumer:
        # Create task to stop consumer (if event loop is running)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(consumer.stop())
            else:
                loop.run_until_complete(consumer.stop())
        except RuntimeError:
            # Event loop not available, just log
            logger.warning("Event loop not available for graceful shutdown")
    else:
        logger.warning("Consumer not initialized, exiting immediately")
        sys.exit(0)


async def main() -> None:
    """Main service entry point.
    
    Initializes and runs the async Kafka consumer service. Handles
    configuration, signal registration, and service lifecycle.
    """
    global consumer
    
    logger.info("Starting LangGraph Kafka Consumer Service...")
    
    # Load configuration from environment
    config = ConsumerConfig()
    logger.info(
        f"Configuration: topic={config.topic}, "
        f"bootstrap_servers={config.bootstrap_servers}, "
        f"group_id={config.group_id}"
    )
    
    # Create consumer instance
    consumer = LangGraphKafkaConsumer(config=config)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start consumer
        await consumer.start()
        
        # Start consumption loop
        await consumer.consume_and_process()
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    except Exception as e:
        logger.error(f"Service error: {e}", exc_info=True)
        raise
    finally:
        # Ensure consumer is stopped
        if consumer:
            await consumer.stop()
        logger.info("Service stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

