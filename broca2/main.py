"""Main application entry point."""
import asyncio
import sys
import logging
from typing import Optional
from telethon import events
from dotenv import load_dotenv

from runtime.core.agent import AgentClient
from runtime.core.queue import QueueProcessor
from plugins.telegram.plugin import TelegramBot
from plugins.telegram.handlers import MessageHandler
from database.operations.shared import initialize_database, check_and_migrate_db
from common.config import get_env_var
from common.logging import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class Application:
    """Main application class that coordinates all components."""
    
    def __init__(self):
        """Initialize the application components."""
        self.agent = AgentClient()
        self.telegram = TelegramBot()
        self.message_handler = MessageHandler()
        self.queue_processor: Optional[QueueProcessor] = None
    
    async def _handle_message(self, event: events.NewMessage.Event) -> None:
        """Handle incoming Telegram messages.
        
        Args:
            event: The Telegram message event
        """
        await self.message_handler.handle_private_message(event)
    
    async def _process_message(self, message: str) -> Optional[str]:
        """Process a message through the agent.
        
        Args:
            message: The message to process
            
        Returns:
            The agent's response or None if processing failed
        """
        return await self.agent.process_message(message)
    
    async def _on_message_processed(self, user_id: int, response: str) -> None:
        """Handle processed messages.
        
        Args:
            user_id: The Telegram user ID
            response: The processed response message
        """
        if self.telegram.client:
            await self.telegram.client.send_message(user_id, response)
    
    async def start(self) -> None:
        """Start all application components."""
        try:
            # Initialize and migrate the database safely
            await initialize_database()
            await check_and_migrate_db()
            
            # Initialize the agent
            logger.info("🔄 Initializing agent API connection...")
            if not await self.agent.initialize():
                logger.error("❌ Failed to initialize agent. Exiting...")
                return
            
            # Initialize queue processor
            logger.info("📋 Initializing message queue processor...")
            self.queue_processor = QueueProcessor(
                message_processor=self._process_message,
                message_mode='echo',  # Default mode
                on_message_processed=self._on_message_processed,
                telegram_client=self.telegram.client
            )
            
            # Set initial message mode
            self.message_handler.set_message_mode('echo')
            self.queue_processor.set_message_mode('echo')
            
            # Start queue processor
            queue_task = asyncio.create_task(self.queue_processor.start())
            
            # Set up Telegram handlers
            logger.info("📱 Setting up Telegram handlers...")
            self.telegram.add_event_handler(
                self._handle_message,
                events.NewMessage(incoming=True)
            )
            
            # Start Telegram client
            logger.info("🤖 Starting Telegram client...")
            await self.telegram.start()
            logger.info("✅ Application started successfully!")
            
            # Wait for the Telegram client to disconnect
            await self.telegram.client.run_until_disconnected()
            
        except KeyboardInterrupt:
            logger.warning("⚠️ Shutdown requested by user")
            # Cancel the queue processor task
            if self.queue_processor:
                queue_task.cancel()
                try:
                    await queue_task
                except asyncio.CancelledError:
                    pass
            # Clean up agent
            await self.agent.cleanup()
            # Disconnect Telegram client
            await self.telegram.client.disconnect()
            raise
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            # Clean up agent
            await self.agent.cleanup()
            # Disconnect Telegram client
            await self.telegram.client.disconnect()
            raise
    
    async def stop(self) -> None:
        """Stop all application components."""
        # Stop queue processor
        if self.queue_processor:
            self.queue_processor.stop()
        
        # Stop Telegram client
        await self.telegram.stop()
        
        # Clean up agent
        await self.agent.cleanup()

    def update_settings(self, settings: dict) -> None:
        """Update application settings.
        
        Args:
            settings: Dictionary containing the new settings
        """
        if 'message_mode' in settings:
            new_mode = settings['message_mode']
            logger.info(f"Updating message mode to: {new_mode}")
            self.message_handler.set_message_mode(new_mode)
            if self.queue_processor:
                self.queue_processor.set_message_mode(new_mode)
        if 'debug_mode' in settings:
            self.agent.debug_mode = settings['debug_mode']

def main() -> None:
    """Application entry point."""
    try:
        logger.info("🚀 Starting application...")
        app = Application()
        asyncio.run(app.start())
    except KeyboardInterrupt:
        logger.warning("⚠️ Shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 