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

import asyncio
import logging

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

        def _extract_content(msg) -> str | None:
            if hasattr(msg, "content"):
                content = msg.content
                if isinstance(content, str):
                    return content
                if isinstance(content, list):
                    parts = []
                    for part in content:
                        if hasattr(part, "text"):
                            parts.append(part.text)
                        elif isinstance(part, dict) and "text" in part:
                            parts.append(part["text"])
                    if parts:
                        return "\n".join(parts)
            if hasattr(msg, "text"):
                return msg.text
            return None

        async def _process_with_letta():
            client = get_letta_client()

            logger.debug(f"Sending message to agent {self.agent_id}: {message}")
            response = client.agents.messages.create(
                agent_id=self.agent_id,
                input=message,
            )

            messages = getattr(response, "messages", None)
            if not messages:
                logger.warning("No messages returned for response")
                return None

            response_content = None
            for msg in messages:
                if getattr(msg, "message_type", None) == "reasoning_message":
                    continue
                response_content = _extract_content(msg)
                if response_content:
                    break

            if response_content is None:
                logger.error("No response content found in run messages")

            return response_content

        try:
            return await _process_with_letta()
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
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

    async def process_message_async(self, message: str) -> str | None:
        """Process message using background streaming.
        
        Strategy:
        1. Send message with streaming=True, background=True, include_pings=True
        2. Extract conversation_id (or message_id) from stream events
        3. Consume/discard stream until it closes (indicates processing complete)
        4. Once stream closes, fetch final message using conversation_id via non-streaming API
        5. Return the message content
        """
        if self.debug_mode:
            logger.debug(f"Debug mode: returning message without processing: {message}")
            return message

        # Streaming responses are not async-iterable in the sync client.
        # Fall back to run-based polling to avoid blocking.
        return await self.process_message(message)

    async def _fallback_to_async(self, message: str) -> str | None:
        """Fallback method using create_async if streaming fails.
        
        Args:
            message: The message to process
            
        Returns:
            The agent's response or None if processing failed
        """
        client = get_letta_client()
        
        logger.debug(f"Using create_async fallback for message to agent {self.agent_id}")
        
        try:
            # Use create_async which returns a Run object immediately
            run = client.agents.messages.create_async(
                agent_id=self.agent_id,
                input=message,
            )
            
            # Extract conversation_id from run object
            conversation_id = None
            if hasattr(run, 'conversation_id') and run.conversation_id:
                conversation_id = run.conversation_id
            elif hasattr(run, 'conversation') and hasattr(run.conversation, 'id'):
                conversation_id = run.conversation.id
            
            if not conversation_id:
                logger.error("Could not extract conversation_id from run object")
                return None
            
            logger.debug(f"Got conversation_id from run: {conversation_id}")
            
            # Poll conversation messages until we get a response
            # This is a fallback, so we'll poll with reasonable intervals
            max_polls = 200  # Poll up to 200 times
            poll_interval = 3  # 3 seconds between polls
            
            for poll_count in range(max_polls):
                await asyncio.sleep(poll_interval)
                
                try:
                    messages_response = client.conversations.messages.list(
                        conversation_id=conversation_id,
                        order='desc',
                        limit=10
                    )
                    
                    if hasattr(messages_response, 'data') and messages_response.data:
                        for msg in messages_response.data:
                            if hasattr(msg, 'message_type'):
                                if msg.message_type == 'assistant_message' or msg.message_type == 'assistant':
                                    if hasattr(msg, 'content') and msg.content:
                                        logger.debug(f"Found assistant message after {poll_count} polls")
                                        return msg.content
                                    elif hasattr(msg, 'text') and msg.text:
                                        return msg.text
                except Exception as poll_error:
                    logger.warning(f"Error polling conversation (attempt {poll_count}): {str(poll_error)}")
                    continue
            
            logger.error(f"No assistant message found after {max_polls} polling attempts")
            return None
            
        except Exception as e:
            logger.error(f"Error in fallback async method: {str(e)}")
            raise

    async def cleanup(self) -> None:
        """Clean up any resources used by the agent client."""
        pass
