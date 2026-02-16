"""Queue processing and message handling."""

import asyncio
import logging
from collections.abc import Callable
from typing import Any

from common.config import get_env_var
from database.operations.messages import (
    get_message_platform_profile,
    get_message_text,
    update_message_with_response,
)
from database.operations.queue import (
    atomic_dequeue_item,
    requeue_failed_item,
    requeue_stale_processing_items,
    update_queue_status,
)
from database.operations.users import (
    get_letta_identity_id,
    get_letta_user_block_id,
    get_platform_profile_id,
    get_user_details,
)
from runtime.core.letta_client import get_letta_client

from .message import MessageFormatter

logger = logging.getLogger(__name__)


class QueueProcessor:
    """Handles processing of queued messages."""

    def __init__(
        self,
        message_processor: Callable[[str], str],
        message_mode: str = "echo",
        plugin_manager: Any | None = None,
        telegram_client: Any | None = None,
        on_message_processed: Callable[[int, str], None] | None = None,
        max_concurrent: int | None = None,
    ):
        """Initialize the queue processor.

        Args:
            message_processor: Function to process messages
            message_mode: The message mode ('echo', 'listen', or 'live')
            plugin_manager: The plugin manager instance for routing responses
            telegram_client: The Telegram client instance for typing indicator
            on_message_processed: Optional callback for when a message is processed
            max_concurrent: Maximum number of concurrent messages to process (default: 3, or from config)
        """
        self.message_processor = message_processor
        self.message_mode = message_mode
        self.formatter = MessageFormatter()
        self.is_running = False
        self.plugin_manager = plugin_manager
        self.telegram_client = telegram_client
        self.on_message_processed = on_message_processed
        self.processing_messages = set()  # Track messages being processed
        self._stop_event = asyncio.Event()
        self.letta_client = get_letta_client()
        self.agent_id = get_env_var("AGENT_ID", required=True)

        # Hard constraint: single-flight processing only
        self.max_concurrent = 1
        self._concurrency_semaphore = asyncio.Semaphore(self.max_concurrent)
        self._processing_tasks: set[asyncio.Task] = set()

    async def _process_with_core_block(
        self, message: str, letta_user_id: int
    ) -> tuple[str | None, str]:
        """Process a message with proper core block management."""
        # Get the user's core block ID
        block_id = await get_letta_user_block_id(letta_user_id)
        if not block_id:
            logger.error(
                f"Core block not found for user {letta_user_id} - Cannot process message"
            )
            return None, "failed"

        try:
            # Attach core block (sync SDK call run in thread to avoid blocking event loop)
            logger.info(f"Attaching user core block {block_id[:8]}... to agent")
            try:
                await asyncio.to_thread(
                    self.letta_client.agents.blocks.attach,
                    block_id,
                    agent_id=self.agent_id,
                )
            except Exception as attach_error:
                err_msg = str(attach_error).lower()
                if (
                    "unique constraint" in err_msg
                    or "already exists" in err_msg
                    or "duplicate key" in err_msg
                    or "409" in err_msg
                    or "unique_agent_block" in err_msg
                ):
                    logger.info(
                        f"Core block {block_id[:8]} already attached; continuing"
                    )
                else:
                    raise

            # Process the message (pass sender_id so Letta scopes conversation per user)
            logger.info(
                f"Processing message with attached core block {block_id[:8]}..."
            )
            identity_id = await get_letta_identity_id(letta_user_id)
            if not identity_id:
                logger.warning(
                    "letta_user_id=%s has no letta_identity_id; sending without sender_id (conversation may be shared)",
                    letta_user_id,
                )
            response = await self.message_processor(message, sender_id=identity_id)

            # Detach core block (sync SDK call run in thread)
            logger.info(f"Detaching core block {block_id[:8]}... from agent")
            await asyncio.to_thread(
                self.letta_client.agents.blocks.detach,
                block_id,
                agent_id=self.agent_id,
            )

            if not response:
                logger.warning(
                    "No response received from agent - Message processing failed"
                )
                return None, "failed"

            return response, "completed"

        except Exception as e:
            logger.error(f"Error during message processing: {str(e)}")
            # Try to detach core block even if there was an error
            try:
                logger.info(
                    f"Cleaning up: Detaching core block {block_id[:8]}... from agent"
                )
                await asyncio.to_thread(
                    self.letta_client.agents.blocks.detach,
                    block_id,
                    agent_id=self.agent_id,
                )
                logger.info("Core block successfully detached")
            except Exception as detach_error:
                logger.error(
                    f"Failed to detach core block after error: {str(detach_error)}"
                )
            return None, "failed"

    async def _process_single_message(self, queue_item: Any) -> None:
        """Process a single message from the queue.

        Args:
            queue_item: The queue item to process
        """
        try:
            # Get message details
            message_data = await get_message_text(queue_item.message_id)
            if not message_data:
                logger.warning(f"Message {queue_item.message_id} not found in database")
                # Try to requeue, if max attempts exceeded it will be marked as failed
                await requeue_failed_item(queue_item.id)
                return

            (
                _,
                message_text,
            ) = message_data  # Get the message text (second element) instead of role

            # Get user details
            user_data = await get_user_details(queue_item.letta_user_id)
            if not user_data:
                logger.warning(
                    f"User details not found for Letta user {queue_item.letta_user_id} "
                    "(orphaned queue item); marking as failed"
                )
                await update_queue_status(queue_item.id, "failed")
                return

            display_name, username = user_data

            # Format message with consistent metadata
            platform_profile = await get_platform_profile_id(queue_item.letta_user_id)
            if not platform_profile:
                logger.warning(
                    f"Platform profile not found for Letta user {queue_item.letta_user_id} "
                    "(orphaned queue item); marking as failed"
                )
                await update_queue_status(queue_item.id, "failed")
                return

            platform_profile_id, platform_user_id = platform_profile

            # Get platform name from profile
            from database.operations.users import get_platform_profile

            profile = await get_platform_profile(platform_profile_id)
            platform_name = profile.platform if profile else None

            formatted_message = self.formatter.format_message(
                message=message_text,
                platform_user_id=platform_user_id,
                username=username,
                platform=platform_name,
            )

            # Process message according to mode
            if self.message_mode == "echo":
                # Echo mode: Return the formatted message
                logger.info("ECHO MODE: Returning formatted message")
                response = formatted_message  # Use formatted message with metadata
                status = "completed"
            else:
                # Process with agent (guarded by timeout)
                logger.info(f"Processing message in {self.message_mode.upper()} mode")
                timeout_seconds = max(
                    300, int(get_env_var("MESSAGE_PROCESS_TIMEOUT", default="300"))
                )
                try:
                    response, status = await asyncio.wait_for(
                        self._process_with_core_block(
                            message=formatted_message,
                            letta_user_id=queue_item.letta_user_id,
                        ),
                        timeout=timeout_seconds,
                    )
                except asyncio.TimeoutError:
                    logger.error(
                        f"Message processing timed out after {timeout_seconds}s"
                    )
                    response, status = None, "failed"

            if response:
                # Update message and queue status
                await update_message_with_response(queue_item.message_id, response)
                await update_queue_status(queue_item.id, status)

                # Route response through platform handler
                if not await self._route_response(queue_item.message_id, response):
                    logger.warning("Failed to route response through platform handler")
            else:
                # Backoff before requeue to avoid spam retries
                attempts = getattr(queue_item, "attempts", 0) or 0
                delay = min(5 * (2**attempts), 300)
                if delay > 0:
                    logger.warning(
                        f"Backing off for {delay:.0f}s before requeue "
                        f"(attempt {attempts + 1})"
                    )
                    await asyncio.sleep(delay)

                # Try to requeue if no response, if max attempts exceeded it will be marked as failed
                await requeue_failed_item(queue_item.id)
                logger.warning(
                    "No response received from agent - Message processing failed"
                )

        except Exception as e:
            logger.error(f"Error processing queue item {queue_item.id}: {str(e)}")
            attempts = getattr(queue_item, "attempts", 0) or 0
            delay = min(5 * (2**attempts), 300)
            if delay > 0:
                logger.warning(
                    f"Backing off for {delay:.0f}s before requeue "
                    f"(attempt {attempts + 1})"
                )
                await asyncio.sleep(delay)
            # Try to requeue on error, if max attempts exceeded it will be marked as failed
            await requeue_failed_item(queue_item.id)

    async def _process_single_message_with_tracking(self, queue_item: Any) -> None:
        """Wrapper to track message processing and manage semaphore.

        Args:
            queue_item: The queue item to process
        """
        try:
            self.processing_messages.add(queue_item.id)
            logger.info(f"Atomically dequeued message (Queue ID: {queue_item.id})")
            await self._process_single_message(queue_item)
        finally:
            self.processing_messages.discard(queue_item.id)
            self._concurrency_semaphore.release()

    async def _route_response(self, message_id: int, response: str) -> bool:
        """Route a response through the appropriate platform handler.

        Args:
            message_id: ID of the message being responded to
            response: The response to route

        Returns:
            bool: True if routing succeeded, False otherwise
        """
        if not self.plugin_manager:
            logger.warning("No plugin manager available for response routing")
            return False

        # Get the platform profile for the message
        profile = await get_message_platform_profile(message_id)
        if not profile:
            logger.error(f"Could not find platform profile for message {message_id}")
            return False

        # Get the handler for this platform
        handler = self.plugin_manager.get_platform_handler(profile.platform)
        if not handler:
            logger.error(f"No handler registered for platform {profile.platform}")
            return False

        try:
            # Debug logging
            logger.info(
                f"🔵 Routing response through {profile.platform} handler: response={response[:50]}..., profile={profile}, message_id={message_id}"
            )

            # Route the response through the platform handler
            await handler(response, profile, message_id)
            return True
        except Exception as e:
            logger.error(
                f"Error routing response through {profile.platform} handler: {str(e)}"
            )
            return False

    async def start(self) -> None:
        """Start processing the queue with concurrent message processing."""
        if self.is_running:
            logger.warning("Queue processor is already running")
            return

        self.is_running = True
        self._stop_event.clear()
        logger.info(
            f"Queue processor started in {self.message_mode.upper()} mode "
            f"(max concurrent: {self.max_concurrent})"
        )

        try:
            # Requeue any stuck processing items from previous crashes
            await requeue_stale_processing_items()

            while self.is_running and not self._stop_event.is_set():
                try:
                    # Wait for available concurrency slot
                    await self._concurrency_semaphore.acquire()

                    # Atomically dequeue next message from queue
                    queue_item = await atomic_dequeue_item()
                    if not queue_item:
                        self._concurrency_semaphore.release()
                        await asyncio.sleep(1)  # Wait before checking again
                        continue

                    # Create task for concurrent processing
                    task = asyncio.create_task(
                        self._process_single_message_with_tracking(queue_item)
                    )
                    self._processing_tasks.add(task)
                    task.add_done_callback(self._processing_tasks.discard)

                except asyncio.CancelledError:
                    logger.info("Queue processor received cancellation signal")
                    break
                except Exception as e:
                    logger.error(f"Queue processor error: {str(e)}")
                    # Release semaphore if we got an error before creating task
                    try:
                        self._concurrency_semaphore.release()
                    except Exception:
                        pass
                    await asyncio.sleep(1)  # Wait before retrying

        finally:
            self.is_running = False
            # Wait for all processing tasks to complete
            if self._processing_tasks:
                logger.info(
                    f"Waiting for {len(self._processing_tasks)} processing tasks to complete..."
                )
                await asyncio.gather(*self._processing_tasks, return_exceptions=True)
            logger.info("Queue processor stopped")

    async def stop(self) -> None:
        """Stop processing the queue."""
        if not self.is_running:
            return

        logger.info("Stopping queue processor...")
        self._stop_event.set()
        self.is_running = False

        # Wait for any in-progress messages to complete
        timeout = 10.0  # Maximum wait time in seconds
        start_time = asyncio.get_event_loop().time()
        while self.processing_messages or self._processing_tasks:
            if asyncio.get_event_loop().time() - start_time > timeout:
                logger.warning(
                    f"Timeout waiting for messages to complete. "
                    f"Remaining: {len(self.processing_messages)} messages, "
                    f"{len(self._processing_tasks)} tasks"
                )
                break
            await asyncio.sleep(0.1)

        # Cancel any remaining tasks
        for task in self._processing_tasks:
            if not task.done():
                task.cancel()

        if self._processing_tasks:
            await asyncio.gather(*self._processing_tasks, return_exceptions=True)

        logger.info("Queue processor stopped")

    def set_message_mode(self, mode: str) -> None:
        """Update the message processing mode."""
        self.message_mode = mode
        logger.info(f"Message processing mode changed to: {mode.upper()}")
