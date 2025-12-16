"""Settings for the Telegram bot plugin."""

from dataclasses import dataclass
from enum import Enum


class MessageMode(Enum):
    """Message handling modes."""

    ECHO = "echo"
    LISTEN = "listen"
    LIVE = "live"


@dataclass
class TelegramBotSettings:
    """Settings for the Telegram bot plugin."""

    bot_token: str
    owner_id: int | None = None
    owner_username: str | None = None
    message_mode: MessageMode = MessageMode.ECHO
    buffer_delay: int = 5
    require_owner: bool = True

    def __post_init__(self):
        """Validate settings after initialization."""
        if not self.bot_token:
            raise ValueError("Bot token is required")

        # Owner validation only required if require_owner is True
        if self.require_owner:
            if not self.owner_id and not self.owner_username:
                raise ValueError("Either owner_id or owner_username must be set")

            if self.owner_id and self.owner_username:
                raise ValueError("Only one of owner_id or owner_username should be set")

        if not isinstance(self.message_mode, MessageMode):
            self.message_mode = MessageMode(self.message_mode)

        if not isinstance(self.buffer_delay, int):
            self.buffer_delay = int(self.buffer_delay)

        if not isinstance(self.require_owner, bool):
            # Convert string to bool if needed
            if isinstance(self.require_owner, str):
                self.require_owner = self.require_owner.lower() in ("true", "1", "yes")
            else:
                self.require_owner = bool(self.require_owner)

    @classmethod
    def from_env(cls) -> "TelegramBotSettings":
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

        # Convert owner_id to int if present
        if owner_id:
            owner_id = int(owner_id)

        # Get message mode (optional)
        message_mode = get_env_var("TELEGRAM_MESSAGE_MODE", default="echo")

        # Get buffer delay (optional)
        buffer_delay = get_env_var("TELEGRAM_BUFFER_DELAY", default="5")

        # Get require_owner setting (optional, defaults to True)
        require_owner_str = get_env_var("TELEGRAM_REQUIRE_OWNER", default="true")
        require_owner = require_owner_str.lower() in ("true", "1", "yes")

        return cls(
            bot_token=bot_token,
            owner_id=owner_id,
            owner_username=owner_username,
            message_mode=message_mode,
            buffer_delay=buffer_delay,
            require_owner=require_owner,
        )

    def to_dict(self) -> dict:
        """Convert settings to dictionary.

        Returns:
            dict: Dictionary representation of settings
        """
        return {
            "bot_token": self.bot_token,
            "owner_id": self.owner_id,
            "owner_username": self.owner_username,
            "message_mode": self.message_mode.value,
            "buffer_delay": self.buffer_delay,
            "require_owner": self.require_owner,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TelegramBotSettings":
        """Create settings from dictionary.

        Args:
            data: Dictionary containing settings

        Returns:
            TelegramBotSettings: Settings loaded from dictionary
        """
        if "bot_token" not in data:
            raise ValueError("Bot token is required")

        return cls(
            bot_token=data["bot_token"],
            owner_id=data.get("owner_id"),
            owner_username=data.get("owner_username"),
            message_mode=data.get("message_mode", "echo"),
            buffer_delay=data.get("buffer_delay", 5),
            require_owner=data.get("require_owner", True),
        )
