"""Message handling and formatting functionality."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Message:
    """Base message class for platform-agnostic message handling."""

    content: str
    user_id: str | None = None
    username: str | None = None
    platform: str | None = None
    timestamp: datetime | None = None
    metadata: dict[str, Any] | None = None


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
        sanitized = "".join(
            c if (ord(c) <= 0xFFFF and c not in {"\n", "\r"}) else " " for c in text
        )
        # Collapse multiple spaces into one and trim
        return " ".join(sanitized.split())

    @staticmethod
    def format_message(
        message: str,
        platform_user_id: int | None = None,
        username: str | None = None,
        platform: str | None = None,
        include_timestamp: bool = False,
        timestamp: datetime | None = None,
    ) -> str:
        """Format a message with metadata.

        Args:
            message: The message text to format
            platform_user_id: Optional platform-specific user ID
            username: Optional username
            platform: Optional platform name for ID labeling
            include_timestamp: Whether to include timestamp in format
            timestamp: Optional timestamp for the message

        Returns:
            Formatted message with metadata
        """
        # Format: [Username: @username, Platform ID: id] message
        parts = []

        # Add user info if provided
        user_parts = []
        if username:
            user_parts.append(f"Username: @{username}")
        if platform_user_id:
            # Use platform-specific label or fallback to "Platform ID"
            id_label = f"{platform.title()} ID" if platform else "Platform ID"
            user_parts.append(f"{id_label}: {platform_user_id}")
        if user_parts:
            # Ensure exact format: [Username: @username, Platform ID: id]
            parts.append(f"[{', '.join(user_parts)}]")

        # Add the message
        parts.append(message)

        # Join all parts with spaces
        return " ".join(parts)

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
        parts = formatted_message.split("] ")
        if len(parts) > 1:
            return parts[-1]

        # If no metadata found, return the original message
        return formatted_message


class MessageHandler(ABC):
    """Base class for platform-specific message handlers.

    This class defines the interface for handling messages in a platform-agnostic way.
    Platform-specific handlers should inherit from this class and implement the required methods.
    """

    @abstractmethod
    async def handle_message(self, message: Message) -> None:
        """Handle an incoming message.

        Args:
            message: The message to handle
        """
        pass

    @abstractmethod
    async def send_message(self, message: Message) -> None:
        """Send a message.

        Args:
            message: The message to send
        """
        pass

    def format_message(self, message: Message) -> str:
        """Format a message for display.

        This is an optional method that handlers can override to provide
        platform-specific formatting. The base implementation uses the
        MessageFormatter.

        Args:
            message: The message to format

        Returns:
            str: The formatted message
        """
        return MessageFormatter.format_message(
            message.content,
            message.user_id,
            message.username,
            message.timestamp is not None,
            message.timestamp,
        )

    def sanitize_message(self, message: Message) -> Message:
        """Sanitize a message's content.

        This is an optional method that handlers can override to provide
        platform-specific sanitization. The base implementation uses the
        MessageFormatter.

        Args:
            message: The message to sanitize

        Returns:
            Message: The sanitized message
        """
        sanitized_content = MessageFormatter.sanitize_text(message.content)
        return Message(
            content=sanitized_content,
            user_id=message.user_id,
            username=message.username,
            platform=message.platform,
            timestamp=message.timestamp,
            metadata=message.metadata,
        )
