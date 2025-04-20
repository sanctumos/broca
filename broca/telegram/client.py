"""Telegram client setup and configuration."""
import os
import json
from typing import Optional
from telethon import TelegramClient, events
from common.config import get_env_var
from common.logging import setup_logging

# Setup logging
setup_logging()

class TelegramBot:
    """Wrapper for Telegram client functionality."""
    
    def __init__(self):
        """Initialize the Telegram bot with configuration."""
        # Get credentials from environment
        self.api_id = get_env_var("TELEGRAM_API_ID", required=True, cast_type=int)
        self.api_hash = get_env_var("TELEGRAM_API_HASH", required=True)
        self.phone = get_env_var("TELEGRAM_PHONE", required=True)
        
        print(f"Telegram config - API ID: {self.api_id}, "
              f"API Hash: {self.api_hash[:4]}..., "
              f"Phone: {self.phone}")
        
        # Create session filename based on phone number
        self.session_file = f"telegram_session_{self.phone.replace('+', '')}"
        self.session_info_file = f"{self.session_file}.json"
        
        # Check if credentials have changed
        should_clear_session = self._should_clear_session()
        if should_clear_session:
            print("Credentials changed, clearing session cache...")
            self._clear_session_files()
        else:
            print("Using cached session (credentials unchanged)")
        
        # Save current credentials
        self._save_session_info()
        
        # Initialize the client
        print(f"Initializing Telegram client with session: {self.session_file}")
        self.client = TelegramClient(self.session_file, self.api_id, self.api_hash)
        
        # Track connection state
        self._is_connected = False
        
        # Register connection state monitoring
        @self.client.on(events.NewMessage)
        async def _handle_new_message(event):
            """Handle new messages and log them."""
            sender = await event.get_sender()
            print(f"📨 New message from {sender.first_name} (@{sender.username}): {event.text[:50]}...")
    
    def _should_clear_session(self) -> bool:
        """Check if the session should be cleared based on credential changes."""
        try:
            if not os.path.exists(self.session_info_file):
                return True
            
            with open(self.session_info_file, 'r') as f:
                saved_info = json.load(f)
            
            return (
                saved_info.get('api_id') != self.api_id or
                saved_info.get('api_hash') != self.api_hash or
                saved_info.get('phone') != self.phone
            )
        except Exception as e:
            print(f"Error checking session info: {e}")
            return True
    
    def _save_session_info(self) -> None:
        """Save current session information."""
        try:
            session_info = {
                'api_id': self.api_id,
                'api_hash': self.api_hash,
                'phone': self.phone
            }
            with open(self.session_info_file, 'w') as f:
                json.dump(session_info, f)
        except Exception as e:
            print(f"Warning: Could not save session info: {e}")
    
    def _clear_session_files(self) -> None:
        """Clear session files if they exist."""
        try:
            if os.path.exists(f"{self.session_file}.session"):
                os.remove(f"{self.session_file}.session")
            if os.path.exists(self.session_info_file):
                os.remove(self.session_info_file)
        except Exception as e:
            print(f"Warning: Could not remove session files: {e}")
    
    async def start(self) -> None:
        """Start the Telegram client."""
        print(f"Starting Telegram client for {self.phone}...")
        await self.client.start(phone=self.phone)
        print("Telegram client started, checking connection...")
        
        # Check connection status immediately
        if self.client.is_connected():
            self._is_connected = True
            me = await self.client.get_me()
            print(f"✅ Connected successfully as: {me.first_name} (@{me.username})")
            print(f"📱 Ready to receive messages on {self.phone}")
        else:
            print("❌ Failed to connect to Telegram")
            raise ConnectionError("Could not establish connection to Telegram")
    
    async def stop(self) -> None:
        """Stop the Telegram client."""
        print("Stopping Telegram client...")
        if self._is_connected:
            await self.client.disconnect()
            self._is_connected = False
            print("Telegram client stopped successfully.")
        else:
            print("Telegram client was not connected.")
    
    async def send_message(self, user_id: int, message: str) -> None:
        """Send a message to a user.
        
        Args:
            user_id: The Telegram user ID to send to
            message: The message to send
        """
        if not self._is_connected:
            print("❌ Cannot send message: Client not connected")
            return
            
        print(f"📤 Sending message to user {user_id}")
        async with self.client.action(user_id, action='typing'):
            await self.client.send_message(user_id, message)
            print(f"✅ Message sent to user {user_id}")
    
    def add_event_handler(self, callback, event):
        """Add an event handler to the client.
        
        Args:
            callback: The callback function to handle the event
            event: The event to handle
        """
        print(f"📝 Adding event handler for {event.__class__.__name__}")
        self.client.add_event_handler(callback, event)
    
    def run(self) -> None:
        """Run the client until disconnected."""
        print("🔄 Running Telegram client...")
        self.client.run_until_disconnected() 