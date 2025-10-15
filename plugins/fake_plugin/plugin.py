"""
Fake Plugin for testing plugin discovery

This plugin implements the minimal Plugin interface to test
if Broca2 can discover and load plugins automatically.
"""

import logging
from typing import Any

from plugins import Plugin


class FakePlugin(Plugin):
    """A fake plugin for testing plugin discovery."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.name = "FakePlugin"
        self.platform = "fake"

    def get_name(self) -> str:
        """Get the plugin name."""
        return "fake_plugin"

    def get_platform(self) -> str:
        """Get the platform name."""
        return "fake_platform"

    def get_message_handler(self):
        """Get the message handler for this plugin."""
        return self  # Return self as a mock handler

    async def start(self):
        """Start the plugin."""
        if self.is_running:
            self.logger.warning("Fake plugin is already running")
            return

        self.logger.info("🎭 Fake plugin started successfully")
        self.is_running = True

    async def stop(self):
        """Stop the plugin."""
        if not self.is_running:
            return

        self.logger.info("🎭 Fake plugin stopped")
        self.is_running = False

    def get_settings(self) -> dict[str, Any]:
        """Get plugin settings."""
        return {"enabled": True, "message": "Hello from fake plugin!", "debug": False}

    def apply_settings(self, settings: dict[str, Any]) -> None:
        """Apply settings to the plugin."""
        self.enabled = settings.get("enabled", True)
        self.message = settings.get("message", "Hello from fake plugin!")
        self.debug = settings.get("debug", False)
        self.logger.info(
            f"Applied settings: enabled={self.enabled}, message='{self.message}', debug={self.debug}"
        )

    def validate_settings(self, settings: dict[str, Any]) -> bool:
        """Validate plugin settings."""
        return True  # Always valid for fake plugin

    def register_event_handler(self, event_type, handler):
        """Register an event handler."""
        pass  # No-op for fake plugin

    def emit_event(self, event):
        """Emit an event."""
        pass  # No-op for fake plugin
