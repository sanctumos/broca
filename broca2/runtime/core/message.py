"""Message handling and formatting functionality."""
from datetime import datetime
from typing import Optional, Dict, Any, List

class MessageFormatter:
    """Handles message formatting and processing."""
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Remove problematic characters and normalize whitespace.
        
        Args:
            text: The text to sanitize
            
        Returns:
            Sanitized text with normalized whitespace
        """
        # Replace any newline or carriage return with a space
        sanitized = ''.join(
            c if (ord(c) <= 0xFFFF and c not in {'\n', '\r'}) else ' ' 
            for c in text
        )
        # Collapse multiple spaces into one and trim
        return ' '.join(sanitized.split())
    
    @staticmethod
    def format_message(
        message: str,
        platform_user_id: Optional[int] = None,
        username: Optional[str] = None,
        include_timestamp: bool = False,
        timestamp: Optional[datetime] = None
    ) -> str:
        """Format a message with metadata.
        
        Args:
            message: The message text to format
            platform_user_id: Optional platform-specific user ID (Telegram ID)
            username: Optional username
            include_timestamp: Whether to include timestamp in format
            timestamp: Optional timestamp for the message
            
        Returns:
            Formatted message with metadata
        """
        # Format: [Username: @username, Telegram ID: id] message
        parts = []
        
        # Add user info if provided
        user_parts = []
        if username:
            user_parts.append(f"Username: @{username}")
        if platform_user_id:
            user_parts.append(f"Telegram ID: {platform_user_id}")
        if user_parts:
            # Ensure exact format: [Username: @username, Telegram ID: id]
            parts.append(f"[{', '.join(user_parts)}]")
        
        # Add the message
        parts.append(message)
        
        # Join all parts with spaces
        return ' '.join(parts)
    
    @staticmethod
    def extract_message_content(formatted_message: str) -> str:
        """Extract the actual message content from a formatted message.
        
        Args:
            formatted_message: The formatted message to extract from
            
        Returns:
            The actual message content without metadata
        """
        # Our format is: [Telegram ID: X, Username: @Y] [TIMESTAMP] MESSAGE
        # We want to extract just the MESSAGE part
        
        # Split on the last '] ' to get the message content
        parts = formatted_message.split('] ')
        if len(parts) > 1:
            return parts[-1]
        
        # If no metadata found, return the original message
        return formatted_message 