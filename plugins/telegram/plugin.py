"""Telegram plugin entry point."""

from plugins import Plugin
from plugins.base import BasePluginWrapper
from plugins.telegram.telegram_plugin import TelegramPlugin


class TelegramPluginWrapper(BasePluginWrapper):
    """Wrapper for TelegramPlugin to make it compatible with auto-discovery."""

    def __init__(self):
        """Initialize the wrapper."""
        super().__init__(TelegramPlugin())

    def add_message_handler(self, callback, event):
        """Add a message handler.
        
        This is specific to TelegramPlugin and not part of the base wrapper.
        
        Args:
            callback: Callback function
            event: Event to handle
        """
        if hasattr(self._plugin, "add_message_handler"):
            self._plugin.add_message_handler(callback, event)


# Export the wrapper class
__all__ = ["TelegramPluginWrapper"]
