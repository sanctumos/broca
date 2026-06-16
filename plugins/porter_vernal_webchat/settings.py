"""
Settings for the Porter Vernal Web Chat Plugin
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class PorterWebChatSettings:
    api_url: str = field(default="http://localhost:8000/partner-bridge")
    api_key: str = field(default="")
    poll_interval: int = field(default=5)
    max_retries: int = field(default=3)
    retry_delay: int = field(default=10)
    plugin_name: str = field(default="porter_vernal_webchat")
    platform_name: str = field(default="porter_vernal_webchat")
    enable_user_creation: bool = field(default=True)
    enable_message_logging: bool = field(default=True)

    def __post_init__(self):
        if not self.api_url:
            raise ValueError("API URL is required")
        if self.poll_interval < 1:
            raise ValueError("Poll interval must be at least 1 second")

    @classmethod
    def from_env(cls) -> "PorterWebChatSettings":
        return cls(
            api_url=os.getenv(
                "PARTNER_BRIDGE_API_URL",
                os.getenv("WEB_CHAT_API_URL", "http://localhost:8000/partner-bridge"),
            ),
            api_key=os.getenv("PARTNER_BRIDGE_POLL_API_KEY", os.getenv("WEB_CHAT_API_KEY", "")),
            poll_interval=int(os.getenv("WEB_CHAT_POLL_INTERVAL", "5")),
            max_retries=int(os.getenv("WEB_CHAT_MAX_RETRIES", "3")),
            retry_delay=int(os.getenv("WEB_CHAT_RETRY_DELAY", "10")),
            plugin_name=os.getenv("WEB_CHAT_PLUGIN_NAME", "porter_vernal_webchat"),
            platform_name=os.getenv("WEB_CHAT_PLATFORM_NAME", "porter_vernal_webchat"),
            enable_user_creation=os.getenv("WEB_CHAT_ENABLE_USER_CREATION", "true").lower() == "true",
            enable_message_logging=os.getenv("WEB_CHAT_ENABLE_MESSAGE_LOGGING", "true").lower() == "true",
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "api_url": self.api_url,
            "api_key": self.api_key,
            "poll_interval": self.poll_interval,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "plugin_name": self.plugin_name,
            "platform_name": self.platform_name,
            "enable_user_creation": self.enable_user_creation,
            "enable_message_logging": self.enable_message_logging,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PorterWebChatSettings":
        return cls(**data)

    def validate_settings(self) -> bool:
        try:
            self.__post_init__()
            return True
        except ValueError:
            return False
