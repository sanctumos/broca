"""Base classes and utilities for plugins to reduce code duplication.

This module provides common base classes and mixins that plugins can use
to avoid duplicating common functionality.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from plugins import Event, EventType, Plugin


class BasePluginWrapper(Plugin):
    """Base class for plugin wrappers that delegate to underlying plugin implementations.
    
    This class eliminates duplication in wrapper classes like TelegramPluginWrapper
    and TelegramBotPluginWrapper by providing a common implementation.
    
    Usage:
        class MyPluginWrapper(BasePluginWrapper):
            def __init__(self):
                super().__init__(MyPlugin())
    """

    def __init__(self, plugin_instance: Any):
        """Initialize wrapper with plugin instance.
        
        Args:
            plugin_instance: The underlying plugin implementation
        """
        self._plugin = plugin_instance

    def get_name(self) -> str:
        """Get the plugin name."""
        return self._plugin.get_name()

    def get_platform(self) -> str:
        """Get the platform name."""
        return self._plugin.get_platform()

    def get_message_handler(self) -> Callable:
        """Get the message handler."""
        return self._plugin.get_message_handler()

    def get_settings(self) -> dict[str, Any] | None:
        """Get plugin settings."""
        return self._plugin.get_settings()

    def apply_settings(self, settings: dict[str, Any]) -> None:
        """Apply settings to the plugin.
        
        Args:
            settings: Settings dictionary to apply
            
        Raises:
            ValueError: If settings are invalid (propagated from plugin)
        """
        if hasattr(self._plugin, "apply_settings") and callable(
            getattr(self._plugin, "apply_settings", None)
        ):
            self._plugin.apply_settings(settings)
        else:
            # Fallback for backward compatibility
            if hasattr(self._plugin, "validate_settings") and callable(
                getattr(self._plugin, "validate_settings", None)
            ):
                if not self._plugin.validate_settings(settings):
                    raise ValueError("Invalid settings provided")

    def validate_settings(self, settings: dict[str, Any]) -> bool:
        """Validate plugin settings.
        
        Args:
            settings: Settings dictionary to validate
            
        Returns:
            True if settings are valid, False otherwise
        """
        if hasattr(self._plugin, "validate_settings"):
            return self._plugin.validate_settings(settings)
        return True

    async def start(self) -> None:
        """Start the plugin."""
        await self._plugin.start()

    async def stop(self) -> None:
        """Stop the plugin."""
        await self._plugin.stop()

    def register_event_handler(
        self, event_type: EventType, handler: Callable[[Event], None]
    ) -> None:
        """Register an event handler.
        
        Args:
            event_type: Type of event to handle
            handler: Function to call when event occurs
        """
        if hasattr(self._plugin, "register_event_handler"):
            self._plugin.register_event_handler(event_type, handler)

    def emit_event(self, event: Event) -> None:
        """Emit an event.
        
        Args:
            event: Event to emit
        """
        if hasattr(self._plugin, "emit_event"):
            self._plugin.emit_event(event)


class SettingsMixin:
    """Mixin for plugins that handle settings.
    
    Provides common settings handling functionality that can be mixed into
    plugin classes to reduce duplication.
    """

    def get_settings_dict(self) -> dict[str, Any] | None:
        """Get settings as a dictionary.
        
        Returns:
            Settings dictionary or None if no settings
        """
        if hasattr(self, "settings") and self.settings:
            if hasattr(self.settings, "to_dict"):
                return self.settings.to_dict()
            elif isinstance(self.settings, dict):
                return self.settings
        return None

    def apply_settings_safe(self, settings: dict[str, Any]) -> None:
        """Apply settings with error handling.
        
        Args:
            settings: Settings dictionary to apply
            
        Raises:
            ValueError: If settings are invalid
        """
        if hasattr(self, "apply_settings"):
            self.apply_settings(settings)
        elif hasattr(self, "validate_settings"):
            if not self.validate_settings(settings):
                raise ValueError("Invalid settings provided")
        # If neither method exists, silently ignore (for plugins without settings)
