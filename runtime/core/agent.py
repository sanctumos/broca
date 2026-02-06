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
import re
import uuid

from common.config import get_env_var
from common.logging import setup_logging
from common.retry import (
    CircuitBreaker,
    RetryConfig,
    exponential_backoff,
    is_retryable_exception,
)

from .letta_client import get_letta_client


def _user_message_list(text: str, sender_id: str | None = None) -> list[dict]:
    """Single user message as Letta messages payload (SDK format: content is a string).
    sender_id scopes the conversation per identity. otid forces a new thread so Letta
    does not reuse a conversation with corrupt tool/tool_calls ordering."""
    msg: dict = {"role": "user", "content": text, "otid": str(uuid.uuid4())}
    if sender_id:
        msg["sender_id"] = sender_id
    return [msg]


_IMAGE_ADDENDUM_PATTERN = re.compile(
    r"^\s*\[Image Attachment:\s*\S+\]\s*$", re.IGNORECASE | re.MULTILINE
)


def _strip_image_addendum(text: str) -> str:
    """Remove [Image Attachment: ...] lines from a message."""
    return _IMAGE_ADDENDUM_PATTERN.sub("", text).strip()


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

            # Verify agent exists (sync SDK call run in thread to avoid blocking)
            logger.debug(f"Attempting to retrieve agent {self.agent_id}")
            try:
                agent = await asyncio.to_thread(client.agents.retrieve, self.agent_id)
                logger.info(f"✅ Connected to agent {agent.id}: {agent.name}")
                return True
            except Exception as e:
                logger.error(f"❌ Agent {self.agent_id} not found: {str(e)}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to initialize Letta client: {str(e)}")
            return False

    async def process_message(
        self, message: str, sender_id: str | None = None
    ) -> str | None:
        """Process a message through the agent API with retry logic.
        sender_id: optional Letta identity ID to scope conversation per user."""
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
            response = await asyncio.to_thread(
                client.agents.messages.create,
                self.agent_id,
                messages=_user_message_list(message, sender_id),
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

    async def process_message_async(
        self, message: str, sender_id: str | None = None
    ) -> str | None:
        """Process message using background streaming.
        sender_id: optional Letta identity ID to scope conversation per user.

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

        async def _consume_stream(stream):
            if hasattr(stream, "__aiter__"):
                async for event in stream:
                    yield event
                return

            # Fallback for sync iterables: consume in executor to avoid blocking.
            loop = asyncio.get_running_loop()
            iterator = iter(stream)
            while True:
                try:
                    event = await loop.run_in_executor(None, next, iterator)
                except StopIteration:
                    break
                except (RuntimeError, Exception) as e:
                    # PEP 479 / executor: StopIteration can become RuntimeError in thread
                    if "StopIteration" in str(e):
                        break
                    raise
                yield event

        async def _process_with_streaming():
            client = get_letta_client()

            logger.debug(
                "Sending message to agent %s with streaming (sender_id=%s)",
                self.agent_id,
                f"{sender_id[:8]}..." if sender_id else "None",
            )

            # Sync SDK call: explicit messages=, sender_id, and otid (fresh thread per request).
            try:
                stream = await asyncio.to_thread(
                    lambda: client.agents.messages.create(
                        self.agent_id,
                        messages=_user_message_list(message, sender_id),
                        streaming=True,
                        background=True,
                        include_pings=True,
                    )
                )
            except (AttributeError, TypeError):
                # SDK has create_stream instead of create(streaming=True)
                stream = await asyncio.to_thread(
                    lambda: client.agents.messages.create_stream(
                        self.agent_id,
                        messages=_user_message_list(message, sender_id),
                        include_pings=True,
                    )
                )

            conversation_id = None
            message_id = None
            event_count = 0
            stream_response_content = None  # assistant content from stream (some SDKs/backends don't send conversation_id)

            try:
                async for event in _consume_stream(stream):
                    event_count += 1

                    # Prefer assistant content from stream so we don't depend on conversation_id
                    mt = getattr(event, "message_type", None)
                    if mt in ("assistant_message", "assistant"):
                        content = _extract_content(event)
                        if content:
                            stream_response_content = content
                            logger.debug(
                                "Captured assistant content from stream event #%s",
                                event_count,
                            )
                        # Capture message id for fallback (docs: AssistantMessage has id: str)
                        if not message_id and hasattr(event, "id") and event.id:
                            message_id = event.id
                            logger.debug(
                                "Captured message_id from stream event #%s: %s",
                                event_count,
                                message_id,
                            )

                    if not conversation_id:
                        if hasattr(event, "conversation_id") and event.conversation_id:
                            conversation_id = event.conversation_id
                            logger.debug(
                                "Captured conversation_id from stream event "
                                f"#{event_count}: {conversation_id}"
                            )
                        elif hasattr(event, "conversation") and hasattr(
                            event.conversation, "id"
                        ):
                            conversation_id = event.conversation.id
                            logger.debug(
                                "Captured conversation_id from stream event "
                                f"#{event_count}: {conversation_id}"
                            )
                        elif hasattr(event, "run") and hasattr(
                            event.run, "conversation_id"
                        ):
                            conversation_id = event.run.conversation_id
                            logger.debug(
                                "Captured conversation_id from stream event "
                                f"#{event_count}: {conversation_id}"
                            )
                        elif hasattr(event, "data"):
                            data = event.data
                            if (
                                hasattr(data, "conversation_id")
                                and data.conversation_id
                            ):
                                conversation_id = data.conversation_id
                                logger.debug(
                                    "Captured conversation_id from stream event data "
                                    f"#{event_count}: {conversation_id}"
                                )

                    if not message_id:
                        if hasattr(event, "message_id") and event.message_id:
                            message_id = event.message_id
                        elif hasattr(event, "messages") and event.messages:
                            for msg in event.messages:
                                if hasattr(msg, "id"):
                                    message_id = msg.id
                                    break

                    if event_count % 100 == 0:
                        logger.debug(
                            "Stream active: processed %s events, conversation_id=%s",
                            event_count,
                            "captured" if conversation_id else "not yet",
                        )

                logger.debug(
                    "Stream closed after %s events - processing complete", event_count
                )

            except Exception as stream_error:
                logger.error(
                    "Error consuming stream after %s events: %s",
                    event_count,
                    str(stream_error),
                )
                if not conversation_id and not stream_response_content:
                    logger.warning(
                        "No conversation_id captured from stream, cannot fetch message"
                    )
                    raise
                if stream_response_content:
                    return stream_response_content

            # If we got assistant content from the stream, use it (SDK/backend may not send conversation_id)
            if stream_response_content:
                return stream_response_content

            if conversation_id:
                logger.debug(
                    "Fetching final message from conversation %s", conversation_id
                )
                messages_response = await asyncio.to_thread(
                    client.conversations.messages.list,
                    conversation_id,
                    order="desc",
                    limit=10,
                )
                if hasattr(messages_response, "data") and messages_response.data:
                    for msg in messages_response.data:
                        if getattr(msg, "message_type", None) in (
                            "assistant_message",
                            "assistant",
                        ):
                            response_content = _extract_content(msg)
                            if response_content:
                                logger.debug(
                                    "Found assistant message in conversation %s",
                                    conversation_id,
                                )
                                return response_content
                logger.warning(
                    "No assistant message found in conversation %s", conversation_id
                )
                return None

            if message_id:
                logger.debug(
                    "Fetching message by message_id (messages.retrieve): %s", message_id
                )
                # Per API docs: messages.retrieve(message_id) -> get /v1/messages/{message_id}
                try:
                    msg = await asyncio.to_thread(
                        client.messages.retrieve,
                        message_id,
                    )
                    if msg:
                        # API docs say retrieve returns List[Message]; take first
                        if isinstance(msg, list | tuple) and msg:
                            msg = msg[0]
                        content = _extract_content(msg)
                        if content:
                            return content
                except AttributeError:
                    # SDK has no top-level messages.retrieve; try agents.messages.list
                    pass
                except Exception as retrieve_err:
                    logger.debug(
                        "messages.retrieve(%s) failed: %s", message_id, retrieve_err
                    )
                # Fallback: list agent messages and find by id
                messages_response = await asyncio.to_thread(
                    client.agents.messages.list,
                    self.agent_id,
                    limit=10,
                )
                if hasattr(messages_response, "data") and messages_response.data:
                    for msg in messages_response.data:
                        if getattr(msg, "id", None) == message_id:
                            response_content = _extract_content(msg)
                            if response_content:
                                return response_content

            logger.error("Could not extract conversation_id or message_id from stream")
            return None

        max_wait = int(get_env_var("LONG_TASK_MAX_WAIT", default="600"))
        try:
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
            logger.error("Stream processing timed out after %s seconds", max_wait)
            logger.info("Attempting fallback to create_async method")
            try:
                return await self._fallback_to_async(message, sender_id)
            except Exception as fallback_error:
                logger.error("Fallback method also failed: %s", str(fallback_error))
                return None
        except Exception as e:
            logger.error("Error processing message with streaming: %s", str(e))
            err_lower = str(e).lower()
            if "[image attachment:" in message.lower() and (
                "thought_signature" in err_lower
                or "image-analyzer" in err_lower
                or "invalid_argument" in err_lower
            ):
                logger.warning(
                    "Image tool call failed (thought_signature). Retrying without image addendum."
                )
                stripped = _strip_image_addendum(message)
                if stripped and stripped != message:
                    try:
                        return await self._fallback_to_async(stripped, sender_id)
                    except Exception as fallback_error:
                        logger.error(
                            "Fallback without image addendum also failed: %s",
                            str(fallback_error),
                        )
            logger.info("Attempting fallback to create_async method")
            try:
                return await self._fallback_to_async(message, sender_id)
            except Exception as fallback_error:
                logger.error("Fallback method also failed: %s", str(fallback_error))
                return None

    async def _fallback_to_async(
        self, message: str, sender_id: str | None = None
    ) -> str | None:
        """Fallback method using create_async if streaming fails.

        Args:
            message: The message to process
            sender_id: optional Letta identity ID to scope conversation per user

        Returns:
            The agent's response or None if processing failed
        """
        client = get_letta_client()

        logger.debug(
            f"Using create_async fallback for message to agent {self.agent_id}"
        )

        try:
            # Use create_async which returns a Run object immediately (sync SDK in thread)
            run = await asyncio.to_thread(
                client.agents.messages.create_async,
                self.agent_id,
                messages=_user_message_list(message, sender_id),
            )

            # Extract conversation_id from run object (may be None in initial response)
            conversation_id = None
            if hasattr(run, "conversation_id") and run.conversation_id:
                conversation_id = run.conversation_id
            elif hasattr(run, "conversation") and hasattr(run.conversation, "id"):
                conversation_id = run.conversation.id

            # If create_async response didn't include conversation_id, poll run until it appears
            if not conversation_id and hasattr(run, "id") and run.id:
                for wait_sec in (0.5, 1.0, 2.0):
                    await asyncio.sleep(wait_sec)
                    try:
                        updated = await asyncio.to_thread(
                            client.runs.retrieve,
                            run.id,
                        )
                        if getattr(updated, "conversation_id", None):
                            conversation_id = updated.conversation_id
                            logger.debug(
                                "Got conversation_id from runs.retrieve after %.1fs",
                                wait_sec,
                            )
                            break
                    except Exception as e:
                        logger.debug("runs.retrieve(%s) failed: %s", run.id, e)
                        continue

            if not conversation_id:
                logger.error(
                    "Could not extract conversation_id from run object (run_id=%s). "
                    "Run may have failed before creating a conversation.",
                    getattr(run, "id", None),
                )
                return None

            logger.debug(f"Got conversation_id from run: {conversation_id}")

            # Poll conversation messages until we get a response
            # This is a fallback, so we'll poll with reasonable intervals
            max_polls = 200  # Poll up to 200 times
            poll_interval = 3  # 3 seconds between polls

            for poll_count in range(max_polls):
                await asyncio.sleep(poll_interval)

                try:
                    messages_response = await asyncio.to_thread(
                        client.conversations.messages.list,
                        conversation_id,
                        order="desc",
                        limit=10,
                    )

                    if hasattr(messages_response, "data") and messages_response.data:
                        for msg in messages_response.data:
                            if hasattr(msg, "message_type"):
                                if (
                                    msg.message_type == "assistant_message"
                                    or msg.message_type == "assistant"
                                ):
                                    if hasattr(msg, "content") and msg.content:
                                        logger.debug(
                                            f"Found assistant message after {poll_count} polls"
                                        )
                                        return msg.content
                                    elif hasattr(msg, "text") and msg.text:
                                        return msg.text
                except Exception as poll_error:
                    logger.warning(
                        f"Error polling conversation (attempt {poll_count}): {str(poll_error)}"
                    )
                    continue

            logger.error(
                f"No assistant message found after {max_polls} polling attempts"
            )
            return None

        except Exception as e:
            logger.error(f"Error in fallback async method: {str(e)}")
            raise

    async def cleanup(self) -> None:
        """Clean up any resources used by the agent client."""
        pass
