"""CLI Test Plugin for testing plugin discovery."""

import logging
from typing import Dict, Any
from plugins import Plugin

logger = logging.getLogger(__name__)

class CLITestPlugin(Plugin):
    """A simple CLI test plugin."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_running = False
    
    def get_name(self) -> str:
        """Get the plugin name."""
        return "cli_test"
    
    def get_platform(self) -> str:
        """Get the platform name."""
        return "cli"
    
    def get_message_handler(self):
        """Get the message handler for this plugin."""
        return None  # No message handler for CLI test plugin
    
    async def start(self):
        """Start the plugin."""
        if self.is_running:
            self.logger.warning("CLI test plugin is already running")
            return
        
        self.logger.info("🔧 CLI test plugin started successfully")
        self.is_running = True
    
    async def stop(self):
        """Stop the plugin."""
        if not self.is_running:
            return
        
        self.logger.info("🔧 CLI test plugin stopped")
        self.is_running = False
    
    def get_settings(self) -> Dict[str, Any]:
        """Get plugin settings."""
        return {
            'enabled': True,
            'debug': False
        }
    
    def apply_settings(self, settings: Dict[str, Any]) -> None:
        """Apply settings to the plugin."""
        self.enabled = settings.get('enabled', True)
        self.debug = settings.get('debug', False)
        self.logger.info(f"Applied settings: enabled={self.enabled}, debug={self.debug}")
    
    def validate_settings(self) -> bool:
        """Validate plugin settings."""
        return True  # Always valid for CLI test plugin
