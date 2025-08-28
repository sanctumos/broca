"""
Web Chat Plugin for Broca2

This plugin polls a PHP-based web chat API and processes messages through the Broca2 agent system.
It follows the pull-based architecture where the plugin polls for new messages and posts responses back.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from plugins import Plugin, Event, EventType
import logging


from plugins.web_chat.settings import WebChatSettings
from plugins.web_chat.api_client import WebChatAPIClient
from plugins.web_chat.message_handler import WebChatMessageHandler


class WebChatPlugin(Plugin):
    """Web Chat Plugin for Broca2."""
    
    def __init__(self, settings: Optional[WebChatSettings] = None):
        self.settings = settings  # Initialize lazily
        self.api_client: Optional[WebChatAPIClient] = None
        self.message_handler: Optional[WebChatMessageHandler] = None
        self.polling_task: Optional[asyncio.Task] = None
        self.is_running = False
        self.logger = logging.getLogger(__name__)
        
        # Track processed messages to avoid duplicates
        self.processed_messages = set()
        
        # Track session responses for correlation
        self.session_responses = {}
    
    def get_name(self) -> str:
        """Get the plugin name."""
        if self.settings is None:
            return "web_chat"
        return self.settings.plugin_name
    
    def get_platform(self) -> str:
        """Get the platform name."""
        if self.settings is None:
            return "web_chat"
        return self.settings.platform_name
    
    def get_message_handler(self):
        """Get the message handler for this plugin."""
        return self._handle_response
    
    async def start(self):
        """Start the plugin."""
        if self.is_running:
            self.logger.warning("Plugin is already running")
            return
        
        try:
            # Initialize API client
            self.api_client = WebChatAPIClient(self.settings)
            
            # Initialize message handler
            self.message_handler = WebChatMessageHandler(self.settings.platform_name)
            
            # Test connection
            if not await self.api_client.test_connection():
                self.logger.error("Failed to connect to web chat API")
                return
            
            self.logger.info("Web Chat Plugin started successfully")
            self.is_running = True
            
            # Start polling task
            self.polling_task = asyncio.create_task(self._poll_messages())
            
        except Exception as e:
            self.logger.error(f"Error starting Web Chat Plugin: {e}")
            raise
    
    async def stop(self):
        """Stop the plugin."""
        if not self.is_running:
            return
        
        self.logger.info("Stopping Web Chat Plugin...")
        self.is_running = False
        
        # Cancel polling task
        if self.polling_task:
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
        
        # Close API client
        if self.api_client and self.api_client.session:
            await self.api_client.session.close()
        
        self.logger.info("Web Chat Plugin stopped")
    
    def get_settings(self) -> Dict[str, Any]:
        """Get plugin settings."""
        if self.settings is None:
            try:
                self.settings = WebChatSettings.from_env()
            except Exception as e:
                self.logger.warning(f"Could not load Web Chat settings: {e}")
                # Return a minimal settings object
                return {}
        return self.settings.to_dict()
    
    def validate_settings(self) -> bool:
        """Validate plugin settings."""
        return self.settings.validate_settings()
    
    def apply_settings(self, settings: Dict[str, Any]) -> None:
        """Apply settings to the plugin."""
        if settings:
            self.settings = WebChatSettings.from_dict(settings)
            self.logger.info(f"Applied settings to plugin: {self.get_name()}")
    
    async def _poll_messages(self):
        """Poll for new messages from the web chat API."""
        self.logger.info(f"Starting message polling with {self.settings.poll_interval}s interval")
        
        while self.is_running:
            try:
                # Get messages from API
                messages = await self.api_client.get_messages(limit=50)
                
                if messages:
                    self.logger.info(f"Processing {len(messages)} messages")
                    
                    for message_data in messages:
                        if not self.is_running:
                            break
                        
                        await self._process_message(message_data)
                
                # Wait before next poll
                await asyncio.sleep(self.settings.poll_interval)
                
            except asyncio.CancelledError:
                self.logger.info("Message polling cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in message polling: {e}")
                await asyncio.sleep(self.settings.retry_delay)
    
    async def _process_message(self, message_data: Dict[str, Any]):
        """Process a single message from the API."""
        try:
            # Create unique identifier for this message
            message_id = f"{message_data.get('session_id')}_{message_data.get('id')}_{message_data.get('timestamp')}"
            
            # Skip if already processed
            if message_id in self.processed_messages:
                return
            
            # Process the message
            message = await self.message_handler.process_incoming_message(message_data)
            
            if message:
                # Mark as processed
                self.processed_messages.add(message_id)
                
                # Message is already queued for processing by the message handler
                self.logger.info(f"Message queued for processing from session {message_data.get('session_id')}")
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    async def send_response(self, session_id: str, response_text: str, 
                          original_message=None) -> bool:
        """
        Send a response back to the web chat.
        
        Args:
            session_id: The session ID to send the response to
            response_text: The response text to send
            original_message: The original message being responded to (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.api_client:
            self.logger.error("API client not initialized")
            return False
        
        try:
            # Process outgoing message in database
            if original_message:
                await self.message_handler.process_outgoing_message(
                    session_id, response_text, original_message
                )
            
            # Send response via API
            success = await self.api_client.post_response(session_id, response_text)
            
            if success:
                self.logger.info(f"Successfully sent response to session {session_id}")
            else:
                self.logger.error(f"Failed to send response to session {session_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending response: {e}")
            return False
    
    async def _handle_response(self, response: str, profile, message_id: int) -> None:
        """Handle sending a response to a web chat user.
        
        Args:
            response: The response text to send
            profile: The platform profile of the user
            message_id: The ID of the message being responded to
        """
        try:
            # Extract session_id from profile metadata
            metadata = profile.metadata
            if isinstance(metadata, str):
                import json
                metadata = json.loads(metadata)
            
            session_id = metadata.get('session_id')
            if not session_id:
                self.logger.error(f"No session_id found in profile metadata for message {message_id}")
                return
            
            # Send response via API
            success = await self.send_response(session_id, response)
            
            if success:
                self.logger.info(f"Successfully sent response to session {session_id}")
            else:
                self.logger.error(f"Failed to send response to session {session_id}")
                
        except Exception as e:
            self.logger.error(f"Error handling response for message {message_id}: {e}")
    
    async def handle_agent_response(self, agent_response: str, session_id: str, 
                                  original_message=None) -> bool:
        """
        Handle a response from the Broca2 agent.
        
        Args:
            agent_response: The response from the agent
            session_id: The session ID to send the response to
            original_message: The original message being responded to (optional)
            
        Returns:
            True if successful, False otherwise
        """
        return await self.send_response(session_id, agent_response, original_message)
    
    def cleanup_processed_messages(self, max_age_hours: int = 24):
        """Clean up old processed message IDs to prevent memory bloat."""
        # This is a simple implementation - in production, you might want
        # to use a more sophisticated approach with timestamps
        if len(self.processed_messages) > 1000:  # Arbitrary limit
            # Clear half of the processed messages
            self.processed_messages.clear()
            self.logger.info("Cleaned up processed message cache") 