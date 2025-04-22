"""Queue processing functionality."""
import asyncio
import logging
from typing import Optional, Callable, Tuple, Any
from database.operations.messages import get_message_text, update_message_with_response
from database.operations.users import get_user_details, get_platform_profile_id, get_letta_user_block_id
from database.operations.queue import update_queue_status, get_pending_queue_item
from runtime.core.message import MessageFormatter
from runtime.core.letta_client import get_letta_client
from common.config import get_env_var
from common.logging import setup_logging

# Setup logging with emojis
setup_logging()
logger = logging.getLogger(__name__)

# Add emoji mapping to log records
def add_emoji(record):
    """Add emoji to log record based on level."""
    emojis = {
        logging.INFO: "🔵",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.DEBUG: "🔍",
        logging.CRITICAL: "🚨"
    }
    record.msg = f"{emojis.get(record.levelno, '')} {record.msg}"
    return True

# Add emoji filter to logger
logger.addFilter(add_emoji)

class QueueProcessor:
    """Handles processing of queued messages."""
    
    def __init__(
        self,
        message_processor: Callable[[str], str],
        message_mode: str = 'echo',
        on_message_processed: Optional[Callable[[int, str], None]] = None,
        telegram_client: Optional[Any] = None
    ):
        """Initialize the queue processor.
        
        Args:
            message_processor: Function to process messages
            message_mode: The message mode ('echo', 'listen', or 'live')
            on_message_processed: Callback function when a message is processed
            telegram_client: The Telegram client instance for typing indicator
        """
        self.message_processor = message_processor
        self.message_mode = message_mode
        self.formatter = MessageFormatter()
        self.is_running = False
        self.on_message_processed = on_message_processed
        self.letta_client = get_letta_client()
        self.telegram_client = telegram_client
        self.processing_messages = set()  # Track messages being processed
        self._stop_event = asyncio.Event()
    
    async def _process_with_core_block(
        self,
        message: str,
        letta_user_id: int,
        agent_id: str
    ) -> Tuple[Optional[str], str]:
        """Process a message with proper core block management."""
        # Get the user's core block ID
        block_id = await get_letta_user_block_id(letta_user_id)
        if not block_id:
            logger.error(f"Core block not found for user {letta_user_id} - Cannot process message")
            return None, 'failed'
            
        try:
            # Attach core block
            logger.info(f"Attaching user core block {block_id[:8]}... to agent")
            self.letta_client.agents.blocks.attach(
                agent_id=agent_id,
                block_id=block_id
            )
            
            # Process the message
            logger.info(f"Processing message with attached core block {block_id[:8]}...")
            response = await self.message_processor(message)
            
            # Detach core block
            logger.info(f"Detaching core block {block_id[:8]}... from agent")
            self.letta_client.agents.blocks.detach(
                agent_id=agent_id,
                block_id=block_id
            )
            
            if not response:
                logger.warning("No response received from agent - Message processing failed")
                return None, 'failed'
                
            return response, 'completed'
            
        except Exception as e:
            logger.error(f"Error during message processing: {str(e)}")
            # Try to detach core block even if there was an error
            try:
                logger.info(f"Cleaning up: Detaching core block {block_id[:8]}... from agent")
                self.letta_client.agents.blocks.detach(
                    agent_id=agent_id,
                    block_id=block_id
                )
                logger.info("Core block successfully detached")
            except Exception as detach_error:
                logger.error(f"Failed to detach core block after error: {str(detach_error)}")
            return None, 'failed'
    
    async def start(self) -> None:
        """Start processing the queue."""
        if self.is_running:
            logger.warning("Queue processor is already running")
            return
            
        self.is_running = True
        self._stop_event.clear()
        logger.info(f"Queue processor started in {self.message_mode.upper()} mode")
        
        try:
            while self.is_running and not self._stop_event.is_set():
                try:
                    # Get next message from queue
                    queue_item = await get_pending_queue_item()
                    if not queue_item:
                        await asyncio.sleep(1)  # Wait before checking again
                        continue
                    
                    # Skip if already processing this message
                    if queue_item.id in self.processing_messages:
                        await asyncio.sleep(1)
                        continue
                    
                    self.processing_messages.add(queue_item.id)
                    logger.info(f"Found pending message (Queue ID: {queue_item.id})")
                    
                    try:
                        # Get message details
                        message_data = await get_message_text(queue_item.message_id)
                        if not message_data:
                            logger.warning(f"Message {queue_item.message_id} not found in database")
                            await update_queue_status(queue_item.id, 'failed')
                            self.processing_messages.remove(queue_item.id)
                            continue
                        
                        _, message_text = message_data  # Get the message text (second element) instead of role
                        
                        # Get user details
                        user_data = await get_user_details(queue_item.letta_user_id)
                        if not user_data:
                            logger.warning(f"User details not found for Letta user {queue_item.letta_user_id}")
                            await update_queue_status(queue_item.id, 'failed')
                            self.processing_messages.remove(queue_item.id)
                            continue
                            
                        display_name, username = user_data
                        
                        # Format message with consistent metadata
                        platform_profile = await get_platform_profile_id(queue_item.letta_user_id)
                        if not platform_profile:
                            logger.warning(f"Platform profile not found for Letta user {queue_item.letta_user_id}")
                            await update_queue_status(queue_item.id, 'failed')
                            self.processing_messages.remove(queue_item.id)
                            continue
                            
                        platform_profile_id, platform_user_id = platform_profile
                        formatted_message = self.formatter.format_message(
                            message=message_text,
                            platform_user_id=platform_user_id,
                            username=username
                        )
                        
                        # Process message according to mode
                        if self.message_mode == 'echo':
                            # Echo mode: Return the formatted message
                            logger.info("ECHO MODE: Returning formatted message")
                            response = formatted_message  # Use formatted message with metadata
                            status = 'completed'
                            
                            # Update message and queue status
                            await update_message_with_response(queue_item.message_id, response)
                            await update_queue_status(queue_item.id, status)
                            
                            # Send response if callback is set
                            if self.on_message_processed:
                                platform_profile = await get_platform_profile_id(queue_item.letta_user_id)
                                if platform_profile:
                                    _, telegram_user_id = platform_profile
                                    try:
                                        # Convert platform_user_id to integer for Telegram
                                        telegram_user_id_int = int(telegram_user_id)
                                        await self.on_message_processed(telegram_user_id_int, response)
                                    except ValueError:
                                        logger.error(f"Invalid Telegram user ID format: {telegram_user_id}")
                                        await update_queue_status(queue_item.id, 'failed')
                        elif self.message_mode == 'listen':
                            # Listen mode: Store message without processing
                            logger.info("LISTEN MODE: Storing message without processing")
                            # Mark as completed without processing
                            await update_queue_status(queue_item.id, 'completed')
                            logger.info(f"Message stored (Queue ID: {queue_item.id})")
                            
                        elif self.message_mode == 'live':
                            # Live mode: Process through agent with core block
                            logger.info("LIVE MODE: Processing message through agent with core block")
                            
                            # Get agent ID from environment
                            agent_id = get_env_var("AGENT_ID", required=True)
                            
                            # Process with core block using formatted message
                            response, status = await self._process_with_core_block(
                                message=formatted_message,  # Use formatted message with metadata
                                letta_user_id=queue_item.letta_user_id,
                                agent_id=agent_id
                            )
                            
                            if response:
                                # Update message and queue status
                                await update_message_with_response(queue_item.message_id, response)
                                await update_queue_status(queue_item.id, status)
                                
                                # Send response if callback is set
                                if self.on_message_processed:
                                    platform_profile = await get_platform_profile_id(queue_item.letta_user_id)
                                    if platform_profile:
                                        _, telegram_user_id = platform_profile
                                        try:
                                            # Convert platform_user_id to integer for Telegram
                                            telegram_user_id_int = int(telegram_user_id)
                                            await self.on_message_processed(telegram_user_id_int, response)
                                        except ValueError:
                                            logger.error(f"Invalid Telegram user ID format: {telegram_user_id}")
                                            await update_queue_status(queue_item.id, 'failed')
                            else:
                                # Mark as failed if no response
                                await update_queue_status(queue_item.id, 'failed')
                                logger.warning("No response received from agent - Message processing failed")
                        
                    except Exception as e:
                        logger.error(f"Error processing queue item {queue_item.id}: {str(e)}")
                        await update_queue_status(queue_item.id, 'failed')
                        
                    finally:
                        # Always remove from processing set
                        self.processing_messages.remove(queue_item.id)
                        
                except asyncio.CancelledError:
                    logger.info("Queue processor received cancellation signal")
                    break
                except Exception as e:
                    logger.error(f"Queue processor error: {str(e)}")
                    await asyncio.sleep(1)  # Wait before retrying
                    
        finally:
            self.is_running = False
            logger.info("Queue processor stopped")
    
    async def stop(self) -> None:
        """Stop processing the queue."""
        if not self.is_running:
            return
            
        logger.info("Stopping queue processor...")
        self._stop_event.set()
        self.is_running = False
        
        # Wait for any in-progress messages to complete
        while self.processing_messages:
            await asyncio.sleep(0.1)
        
        logger.info("Queue processor stopped")
    
    def set_message_mode(self, mode: str) -> None:
        """Update the message processing mode."""
        self.message_mode = mode
        logger.info(f"Message processing mode changed to: {mode.upper()}") 