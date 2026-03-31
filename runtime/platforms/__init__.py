"""Platform-specific helpers (delivery, etc.) shared by runtime and CLI tools."""

from runtime.platforms.telegram_delivery import deliver_telegram_markdown

__all__ = ["deliver_telegram_markdown"]
