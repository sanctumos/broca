"""
Message Handler for Web Chat Plugin

This module handles processing of incoming web chat messages and
integration with Broca2's database and queue systems.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from database.operations.users import get_or_create_letta_user, get_or_create_platform_profile
from database.operations.messages import insert_message
from database.operations.queue import add_to_queue
from runtime.core.message import Message
import logging


class WebChatMessageHandler:
    """Handles processing of web chat messages and integration with Broca2."""
    
    def __init__(self, platform_name: str = "web_chat"):
        self.platform_name = platform_name
        self.logger = logging.getLogger(__name__)
    
    async def process_incoming_message(self, message_data: Dict[str, Any]) -> Optional[Message]:
        """
        Process an incoming message from the web chat API.
        
        Args:
            message_data: Dictionary containing message data from API
            
        Returns:
            Message object if successfully processed, None otherwise
        """
        try:
            # Extract message data
            session_id = message_data.get('session_id')
            message_text = message_data.get('message', '')
            timestamp = message_data.get('timestamp')
            uid = message_data.get('uid')  # PHP-generated unique identifier
            
            if not session_id or not message_text:
                self.logger.warning(f"Invalid message data: {message_data}")
                return None
            
            # Use UID as platform_user_id for Broca2 integration
            platform_user_id = uid if uid else session_id
            
            # Create or get user and platform profile
            if self.platform_name == "web_chat":
                # For web chat, we'll create a generic user if needed
                letta_user = await get_or_create_letta_user(
                    username=f"web_user_{platform_user_id}",
                    display_name=f"Web Chat User ({platform_user_id[:8]})",
                    platform_user_id=platform_user_id
                )
                
                platform_profile, letta_user = await get_or_create_platform_profile(
                    platform=self.platform_name,
                    platform_user_id=platform_user_id,
                    username=f"web_user_{platform_user_id}",
                    display_name=f"Web User ({platform_user_id[:8]})",
                    metadata={
                        'session_id': session_id,
                        'uid': uid,
                        'source': 'web_chat'
                    }
                )
            else:
                # Fallback for other platforms
                letta_user = await get_or_create_letta_user(
                    username=f"{self.platform_name}_user_{platform_user_id}",
                    display_name=f"{self.platform_name.title()} User",
                    platform_user_id=platform_user_id
                )
                
                platform_profile, letta_user = await get_or_create_platform_profile(
                    platform=self.platform_name,
                    platform_user_id=platform_user_id,
                    username=f"{self.platform_name}_user_{platform_user_id}",
                    display_name=f"{self.platform_name.title()} User",
                    metadata={'session_id': session_id}
                )
            
            # Create message object
            message = Message(
                content=message_text,
                user_id=platform_user_id,
                username=f"web_user_{platform_user_id}",
                platform=self.platform_name,
                timestamp=datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if timestamp else datetime.utcnow(),
                metadata={
                    'session_id': session_id,
                    'uid': uid,
                    'platform': self.platform_name,
                    'source': 'web_chat_api',
                    'letta_user_id': letta_user.id,
                    'platform_profile_id': platform_profile.id
                }
            )
            
            # Insert message into database
            message_id = await insert_message(
                letta_user_id=letta_user.id,
                platform_profile_id=platform_profile.id,
                role="user",
                message=message_text,
                timestamp=timestamp
            )
            
            # Add to processing queue
            await add_to_queue(
                letta_user_id=letta_user.id,
                message_id=message_id
            )
            
            self.logger.info(f"Processed incoming message from session {session_id} (UID: {uid})")
            return message_id
            
        except Exception as e:
            self.logger.error(f"Error processing incoming message: {e}")
            return None
    
    async def process_outgoing_message(self, session_id: str, response_text: str, 
                                     original_message: Optional[Message] = None) -> bool:
        """
        Process an outgoing message to be sent back to the web chat.
        
        Args:
            session_id: The session ID to send the response to
            response_text: The response text to send
            original_message: The original message being responded to (optional)
            
        Returns:
            True if successfully processed, False otherwise
        """
        try:
            if not original_message:
                self.logger.warning(f"No original message provided for response to session {session_id}")
                return False
            
            # Create outgoing message object
            outgoing_message = Message(
                id=None,  # Will be set by database
                letta_user_id=original_message.letta_user_id,
                platform_profile_id=original_message.platform_profile_id,
                content=response_text,
                message_type="outgoing",
                timestamp=datetime.utcnow(),
                metadata={
                    'session_id': session_id,
                    'platform': self.platform_name,
                    'source': 'broca2_agent',
                    'in_response_to': original_message.id
                }
            )
            
            # Insert outgoing message into database
            await insert_message(outgoing_message)
            
            self.logger.info(f"Processed outgoing message for session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing outgoing message: {e}")
            return False
    
    def sanitize_message(self, message_text: str) -> str:
        """
        Sanitize message text for safe processing.
        
        Args:
            message_text: Raw message text
            
        Returns:
            Sanitized message text
        """
        if not message_text:
            return ""
        
        # Basic sanitization - remove null bytes and excessive whitespace
        sanitized = message_text.replace('\x00', '').strip()
        
        # Limit message length
        if len(sanitized) > 4000:  # Reasonable limit for chat messages
            sanitized = sanitized[:4000] + "..."
        
        return sanitized 