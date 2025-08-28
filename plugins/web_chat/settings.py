"""
Settings for the Web Chat Plugin

This module defines the configuration settings for the web chat plugin,
including API endpoints, authentication, and polling intervals.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class WebChatSettings:
    """Settings for the Web Chat Plugin."""
    
    # API Configuration
    api_url: str = field(default="http://localhost:8000")
    api_key: str = field(default="")
    
    # Polling Configuration
    poll_interval: int = field(default=5)  # seconds
    max_retries: int = field(default=3)
    retry_delay: int = field(default=10)  # seconds
    
    # Plugin Configuration
    plugin_name: str = field(default="web_chat")
    platform_name: str = field(default="web_chat")
    
    # Database Configuration (for Broca2 integration)
    enable_user_creation: bool = field(default=True)
    enable_message_logging: bool = field(default=True)
    
    def __post_init__(self):
        """Validate settings after initialization."""
        if not self.api_url:
            raise ValueError("API URL is required")
        
        # Make API key optional for development/testing
        # if not self.api_key:
        #     raise ValueError("API key is required")
        
        if self.poll_interval < 1:
            raise ValueError("Poll interval must be at least 1 second")
        
        if self.max_retries < 0:
            raise ValueError("Max retries must be non-negative")
    
    @classmethod
    def from_env(cls) -> 'WebChatSettings':
        """Create settings from environment variables."""
        try:
            return cls(
                api_url=os.getenv('WEB_CHAT_API_URL', 'http://localhost:8000'),
                api_key=os.getenv('WEB_CHAT_API_KEY', ''),
                poll_interval=int(os.getenv('WEB_CHAT_POLL_INTERVAL', '5')),
                max_retries=int(os.getenv('WEB_CHAT_MAX_RETRIES', '3')),
                retry_delay=int(os.getenv('WEB_CHAT_RETRY_DELAY', '10')),
                plugin_name=os.getenv('WEB_CHAT_PLUGIN_NAME', 'web_chat'),
                platform_name=os.getenv('WEB_CHAT_PLATFORM_NAME', 'web_chat'),
                enable_user_creation=os.getenv('WEB_CHAT_ENABLE_USER_CREATION', 'true').lower() == 'true',
                enable_message_logging=os.getenv('WEB_CHAT_ENABLE_MESSAGE_LOGGING', 'true').lower() == 'true',
            )
        except (ValueError, TypeError) as e:
            # Return a minimal settings object if environment variables are invalid
            return cls(
                api_url='http://localhost:8000',
                api_key='',
                poll_interval=5,
                max_retries=3,
                retry_delay=10,
                plugin_name='web_chat',
                platform_name='web_chat',
                enable_user_creation=True,
                enable_message_logging=True,
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            'api_url': self.api_url,
            'api_key': self.api_key,
            'poll_interval': self.poll_interval,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'plugin_name': self.plugin_name,
            'platform_name': self.platform_name,
            'enable_user_creation': self.enable_user_creation,
            'enable_message_logging': self.enable_message_logging,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebChatSettings':
        """Create settings from dictionary."""
        return cls(**data)
    
    def validate_settings(self) -> bool:
        """Validate all settings."""
        try:
            self.__post_init__()
            return True
        except ValueError:
            return False 