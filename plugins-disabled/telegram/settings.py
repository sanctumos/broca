"""Telegram plugin settings."""

from dataclasses import dataclass
from enum import Enum


class MessageMode(Enum):
    """Message handling modes."""

    ECHO = "echo"
    LISTEN = "listen"
    LIVE = "live"


@dataclass
class TelegramSettings:
    """Telegram plugin settings."""

    # API credentials
    api_id: str
    api_hash: str
    session_string: str | None = None

    # Message handling
    message_mode: MessageMode = MessageMode.ECHO
    buffer_delay: int = 5  # seconds

    # Session management
    auto_save_session: bool = True

    @classmethod
    def from_env(cls) -> "TelegramSettings":
        """Create settings from environment variables.

        Returns:
            TelegramSettings: Settings loaded from environment
        """
        from common.config import get_env_var

        return cls(
            api_id=get_env_var("TELEGRAM_API_ID", required=True),
            api_hash=get_env_var("TELEGRAM_API_HASH", required=True),
            session_string=get_env_var("TELEGRAM_SESSION_STRING", default=""),
            message_mode=MessageMode(
                get_env_var("TELEGRAM_MESSAGE_MODE", default="echo")
            ),
            buffer_delay=int(get_env_var("TELEGRAM_BUFFER_DELAY", default="5")),
            auto_save_session=get_env_var(
                "TELEGRAM_AUTO_SAVE_SESSION", default="true"
            ).lower()
            == "true",
        )

    def to_dict(self) -> dict:
        """Convert settings to dictionary.

        Returns:
            dict: Settings as dictionary
        """
        return {
            "api_id": self.api_id,
            "api_hash": self.api_hash,
            "session_string": self.session_string,
            "message_mode": self.message_mode.value,
            "buffer_delay": self.buffer_delay,
            "auto_save_session": self.auto_save_session,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TelegramSettings":
        """Create settings from dictionary.

        Args:
            data: Dictionary containing settings

        Returns:
            TelegramSettings: Settings loaded from dictionary
        """
        return cls(
            api_id=data["api_id"],
            api_hash=data["api_hash"],
            session_string=data.get("session_string"),
            message_mode=MessageMode(data.get("message_mode", "echo")),
            buffer_delay=data.get("buffer_delay", 5),
            auto_save_session=data.get("auto_save_session", True),
        )
