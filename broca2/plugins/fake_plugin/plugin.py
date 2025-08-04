"""
Fake Plugin for testing plugin discovery

This plugin implements the minimal Plugin interface to test
if Broca2 can discover and load plugins automatically.
"""

import logging
from typing import Dict, Any, Optional
from broca2.plugins import Plugin


class FakePlugin(Plugin):
    """A fake plugin for testing plugin discovery."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_running = False
    
    def get_name(self) -> str:
        """Get the plugin name."""
        return "fake_plugin"
    
    def get_platform(self) -> str:
        """Get the platform name."""
        return "fake_platform"
    
    def get_message_handler(self):
        """Get the message handler for this plugin."""
        return None  # No message handler for fake plugin
    
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
    
    def get_settings(self) -> Dict[str, Any]:
        """Get plugin settings."""
        return {
            'name': 'fake_plugin',
            'platform': 'fake_platform',
            'status': 'running' if self.is_running else 'stopped'
        }
    
    def validate_settings(self) -> bool:
        """Validate plugin settings."""
        return True  # Always valid for fake plugin 