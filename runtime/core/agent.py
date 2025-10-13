"""
Agent API client and operations.

Copyright (C) 2024 Sanctum OS

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging

from letta_client import MessageCreate

from common.config import get_env_var
from common.logging import setup_logging
from common.retry import (
    CircuitBreaker,
    RetryConfig,
    exponential_backoff,
    is_retryable_exception,
)

from .letta_client import get_letta_client

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Retry configuration for Letta API calls
LETTA_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    base_delay=1.0,
    max_delay=60.0,
    jitter=True,
)

# Circuit breaker for Letta API
LETTA_CIRCUIT_BREAKER = CircuitBreaker(
    failure_threshold=5,
    timeout=300.0,  # 5 minutes
)


class AgentClient:
    """Client for interacting with the agent API."""

    def __init__(self):
        """Initialize the agent client with configuration."""
        self.debug_mode = get_env_var(
            "DEBUG_MODE", default="false", cast_type=lambda x: x.lower() == "true"
        )
        self.agent_id = get_env_var("AGENT_ID", required=not self.debug_mode)

        logger.debug(f"Initializing AgentClient with ID: {self.agent_id}")
        logger.debug(f"Debug mode: {self.debug_mode}")

        if not self.debug_mode and not self.agent_id:
            raise ValueError(
                "Missing required environment variable. Please ensure AGENT_ID "
                "is set in your .env file, or set DEBUG_MODE=true to run in "
                "debug mode without an agent API."
            )

    async def initialize(self) -> bool:
        """Initialize the agent connection."""
        if self.debug_mode:
            logger.info("🔧 Running in debug mode - agent API disabled")
            return True

        try:
            # Get the singleton Letta client
            client = get_letta_client()
            logger.debug("Retrieved Letta client instance")

            # Verify agent exists
            logger.debug(f"Attempting to retrieve agent {self.agent_id}")
            try:
                agent = client.agents.retrieve(self.agent_id)
                logger.info(f"✅ Connected to agent {agent.id}: {agent.name}")
                return True
            except Exception as e:
                logger.error(f"❌ Agent {self.agent_id} not found: {str(e)}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to initialize Letta client: {str(e)}")
            return False

    async def process_message(self, message: str) -> str | None:
        """Process a message through the agent API with retry logic."""
        if self.debug_mode:
            logger.debug(f"Debug mode: returning message without processing: {message}")
            return message

        async def _process_with_letta():
            client = get_letta_client()

            logger.debug(f"Sending message to agent {self.agent_id}: {message}")
            response = client.agents.messages.create(
                agent_id=self.agent_id,
                messages=[MessageCreate(role="user", content=message)],
            )

            logger.debug(f"Received response: {response}")

            if not hasattr(response, "messages"):
                logger.error("Response does not have 'messages' attribute")
                return None

            if not response.messages:
                logger.warning("No messages in response")
                return None

            response_content = None
            for msg in response.messages:
                logger.debug(
                    f"Processing message: id={msg.id}, type={msg.message_type}"
                )

                if msg.message_type == "reasoning_message":
                    logger.debug(f"Found reasoning: {msg.reasoning}")
                    continue

                if hasattr(msg, "content"):
                    response_content = msg.content
                    break

            if response_content is None:
                logger.error("No response content found in any message")
                for msg in response.messages:
                    if msg.message_type == "reasoning_message" and hasattr(
                        msg, "reasoning"
                    ):
                        response_content = msg.reasoning
                        break

            return response_content

        try:
            return await exponential_backoff(
                _process_with_letta,
                config=LETTA_RETRY_CONFIG,
                circuit_breaker=LETTA_CIRCUIT_BREAKER,
                retry_on_exception=self._should_retry_exception,
            )
        except Exception as e:
            logger.error(f"Error processing message after retries: {str(e)}")
            return None

    def _should_retry_exception(self, exception: Exception) -> bool:
        """Determine if an exception should be retried for Letta API calls.

        Args:
            exception: Exception to check

        Returns:
            True if exception should be retried
        """
        # Don't retry on authentication errors
        if "auth" in str(exception).lower() or "unauthorized" in str(exception).lower():
            return False

        # Don't retry on invalid request errors
        if (
            "bad request" in str(exception).lower()
            or "invalid" in str(exception).lower()
        ):
            return False

        # Use default retry logic for other exceptions
        return is_retryable_exception(exception)

    async def cleanup(self) -> None:
        """Clean up any resources used by the agent client."""
        pass
