"""Telegram bot plugin settings."""
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class MessageMode(Enum):
    """Message handling modes."""
    ECHO = 'echo'
    LISTEN = 'listen'
    LIVE = 'live'

@dataclass
class TelegramBotSettings:
    """Telegram bot plugin settings."""
    # Bot credentials
    bot_token: str
    
    # Owner identification (exactly one must be set)
    owner_id: Optional[str] = None
    owner_username: Optional[str] = None
    
    # Message handling
    message_mode: MessageMode = MessageMode.ECHO
    buffer_delay: int = 5  # seconds
    
    @classmethod
    def from_env(cls) -> 'TelegramBotSettings':
        """Create settings from environment variables.
        
        Returns:
            TelegramBotSettings: Settings loaded from environment
        """
        from common.config import get_env_var
        
        # Get bot token (required)
        bot_token = get_env_var("TELEGRAM_BOT_TOKEN", required=True)
        
        # Get owner identifier (exactly one must be set)
        owner_id = get_env_var("TELEGRAM_OWNER_ID", required=False)
        owner_username = get_env_var("TELEGRAM_OWNER_USERNAME", required=False)
        
        if not owner_id and not owner_username:
            raise ValueError("Either TELEGRAM_OWNER_ID or TELEGRAM_OWNER_USERNAME must be set")
        if owner_id and owner_username:
            raise ValueError("Only one of TELEGRAM_OWNER_ID or TELEGRAM_OWNER_USERNAME should be set")
        
        return cls(
            bot_token=bot_token,
            owner_id=owner_id,
            owner_username=owner_username,
            message_mode=MessageMode(get_env_var("TELEGRAM_MESSAGE_MODE", default="echo")),
            buffer_delay=int(get_env_var("TELEGRAM_BUFFER_DELAY", default="5"))
        )
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary.
        
        Returns:
            dict: Settings as dictionary
        """
        return {
            "bot_token": self.bot_token,
            "owner_id": self.owner_id,
            "owner_username": self.owner_username,
            "message_mode": self.message_mode.value,
            "buffer_delay": self.buffer_delay
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TelegramBotSettings':
        """Create settings from dictionary.
        
        Args:
            data: Dictionary containing settings
            
        Returns:
            TelegramBotSettings: Settings loaded from dictionary
        """
        return cls(
            bot_token=data["bot_token"],
            owner_id=data.get("owner_id"),
            owner_username=data.get("owner_username"),
            message_mode=MessageMode(data.get("message_mode", "echo")),
            buffer_delay=data.get("buffer_delay", 5)
        ) 