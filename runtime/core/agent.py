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

        async def _process_with_letta():
            client = get_letta_client()

            logger.debug(f"Sending message to agent {self.agent_id}: {message}")
            response = client.agents.messages.create(
                agent_id=self.agent_id,
                input=message,  # v1.0+ API: use input parameter instead of messages
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

        async def _process_with_streaming():
            client = get_letta_client()

            logger.debug(f"Sending message to agent {self.agent_id} with streaming: {message}")
            
            # Start streaming with background mode
            stream = client.agents.messages.create(
                agent_id=self.agent_id,
                input=message,
                streaming=True,
                background=True,
                include_pings=True,  # Prevent connection timeouts
            )

            conversation_id = None
            message_id = None
            event_count = 0

            # Consume stream - only extract conversation_id/message_id, discard everything else
            try:
                async for event in stream:
                    event_count += 1
                    
                    # Capture conversation_id from early events (ONLY thing we need from stream)
                    if not conversation_id:
                        # Check various possible attributes for conversation_id
                        if hasattr(event, 'conversation_id') and event.conversation_id:
                            conversation_id = event.conversation_id
                            logger.debug(f"Captured conversation_id from stream event #{event_count}: {conversation_id}")
                        elif hasattr(event, 'conversation') and hasattr(event.conversation, 'id'):
                            conversation_id = event.conversation.id
                            logger.debug(f"Captured conversation_id from stream event #{event_count}: {conversation_id}")
                        elif hasattr(event, 'run') and hasattr(event.run, 'conversation_id'):
                            conversation_id = event.run.conversation_id
                            logger.debug(f"Captured conversation_id from stream event #{event_count}: {conversation_id}")
                        # Also check if event itself has a data attribute with conversation info
                        elif hasattr(event, 'data'):
                            data = event.data
                            if hasattr(data, 'conversation_id') and data.conversation_id:
                                conversation_id = data.conversation_id
                                logger.debug(f"Captured conversation_id from stream event data #{event_count}: {conversation_id}")
                    
                    # Also try to capture message_id if available
                    if not message_id:
                        if hasattr(event, 'message_id') and event.message_id:
                            message_id = event.message_id
                        elif hasattr(event, 'messages') and event.messages:
                            # Get message_id from first message if available
                            for msg in event.messages:
                                if hasattr(msg, 'id'):
                                    message_id = msg.id
                                    break
                    
                    # Discard all other stream content - we don't need it
                    # Log periodically to show stream is active
                    if event_count % 100 == 0:
                        logger.debug(f"Stream active: processed {event_count} events, conversation_id={'captured' if conversation_id else 'not yet'}")
                
                logger.debug(f"Stream closed after {event_count} events - processing complete")
                
            except Exception as stream_error:
                logger.error(f"Error consuming stream after {event_count} events: {str(stream_error)}")
                # If we got conversation_id before error, we can still try to fetch message
                if not conversation_id:
                    logger.warning("No conversation_id captured from stream, cannot fetch message")
                    raise

            # Stream closed = processing complete
            # Now fetch the actual message using non-streaming API
            if conversation_id:
                logger.debug(f"Fetching final message from conversation {conversation_id}")
                try:
                    messages_response = client.conversations.messages.list(
                        conversation_id=conversation_id,
                        order='desc',
                        limit=10
                    )
                    
                    # Extract assistant message from the list
                    if hasattr(messages_response, 'data') and messages_response.data:
                        for msg in messages_response.data:
                            # Look for assistant message
                            if hasattr(msg, 'message_type'):
                                if msg.message_type == 'assistant_message' or msg.message_type == 'assistant':
                                    if hasattr(msg, 'content') and msg.content:
                                        logger.debug("Found assistant message in conversation")
                                        return msg.content
                                    elif hasattr(msg, 'text') and msg.text:
                                        return msg.text
                    
                    logger.warning(f"No assistant message found in conversation {conversation_id}")
                    return None
                    
                except Exception as fetch_error:
                    logger.error(f"Error fetching message from conversation: {str(fetch_error)}")
                    raise
            
            # Fallback: try to get message by message_id if we have it
            if message_id:
                logger.debug(f"Attempting to fetch message by message_id: {message_id}")
                try:
                    # Try to get message from agent messages list
                    messages_response = client.agents.messages.list(
                        agent_id=self.agent_id,
                        limit=10
                    )
                    if hasattr(messages_response, 'data') and messages_response.data:
                        for msg in messages_response.data:
                            if hasattr(msg, 'id') and msg.id == message_id:
                                if hasattr(msg, 'content') and msg.content:
                                    return msg.content
                except Exception as fetch_error:
                    logger.error(f"Error fetching message by message_id: {str(fetch_error)}")
            
            logger.error("Could not extract conversation_id or message_id from stream")
            return None

        # Get max wait time from config (default 10 minutes)
        max_wait = int(get_env_var("LONG_TASK_MAX_WAIT", default="600"))
        
        try:
            # Wrap with timeout to prevent indefinite waiting
            return await asyncio.wait_for(
                exponential_backoff(
                    _process_with_streaming,
                    config=LETTA_RETRY_CONFIG,
                    circuit_breaker=LETTA_CIRCUIT_BREAKER,
                    retry_on_exception=self._should_retry_exception,
                ),
                timeout=max_wait,
            )
        except asyncio.TimeoutError:
            logger.error(f"Stream processing timed out after {max_wait} seconds")
            # Fallback to async method if streaming times out
            logger.info("Attempting fallback to create_async method")
            try:
                return await self._fallback_to_async(message)
            except Exception as fallback_error:
                logger.error(f"Fallback method also failed: {str(fallback_error)}")
                return None
        except Exception as e:
            logger.error(f"Error processing message with streaming after retries: {str(e)}")
            # Try fallback to async method
            logger.info("Attempting fallback to create_async method")
            try:
                return await self._fallback_to_async(message)
            except Exception as fallback_error:
                logger.error(f"Fallback method also failed: {str(fallback_error)}")
                return None

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
