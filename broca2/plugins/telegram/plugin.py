"""Telegram plugin entry point."""
from plugins.telegram.telegram_plugin import TelegramPlugin
from plugins import Plugin

class TelegramPluginWrapper(Plugin):
    """Wrapper for TelegramPlugin to make it compatible with auto-discovery."""
    
    def __init__(self):
        """Initialize the wrapper."""
        self._plugin = TelegramPlugin()
    
    def get_name(self) -> str:
        """Get the plugin name."""
        return self._plugin.get_name()
    
    def get_platform(self) -> str:
        """Get the platform name."""
        return self._plugin.get_platform()
    
    def get_message_handler(self):
        """Get the message handler."""
        return self._plugin.get_message_handler()
    
    def get_settings(self):
        """Get plugin settings."""
        return self._plugin.get_settings()
    
    def apply_settings(self, settings):
        """Apply settings to the plugin."""
        if hasattr(self._plugin, 'apply_settings'):
            self._plugin.apply_settings(settings)
        else:
            # Fallback for backward compatibility
            if hasattr(self._plugin, 'validate_settings'):
                self._plugin.validate_settings(settings)
    
    def validate_settings(self, settings):
        """Validate plugin settings."""
        if hasattr(self._plugin, 'validate_settings'):
            return self._plugin.validate_settings(settings)
        return True
    
    async def start(self):
        """Start the plugin."""
        await self._plugin.start()
    
    async def stop(self):
        """Stop the plugin."""
        await self._plugin.stop()
    
    def register_event_handler(self, event_type, handler):
        """Register an event handler."""
        if hasattr(self._plugin, 'register_event_handler'):
            self._plugin.register_event_handler(event_type, handler)
    
    def emit_event(self, event):
        """Emit an event."""
        if hasattr(self._plugin, 'emit_event'):
            self._plugin.emit_event(event)
    
    def add_message_handler(self, callback, event):
        """Add a message handler."""
        if hasattr(self._plugin, 'add_message_handler'):
            self._plugin.add_message_handler(callback, event)

# Export the wrapper class
__all__ = ['TelegramPluginWrapper']
