"""
Plugin management system for broca2.

Copyright (C) 2024 Sanctum OS

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""Plugin management system for broca2."""
import asyncio
import logging
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import importlib.util
import sys
from common.config import validate_settings
from common.exceptions import PluginError
from plugins import Plugin, Event, EventType

logger = logging.getLogger(__name__)

class PluginManager:
    """Manages plugin lifecycles and event routing."""
    
    def __init__(self):
        """Initialize the plugin manager."""
        self._plugins: Dict[str, Plugin] = {}
        self._event_handlers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._platform_handlers: Dict[str, Callable] = {}
        self._running = False
    
    async def load_plugin(self, plugin_path: str) -> None:
        """Load a plugin from the given path.
        
        Args:
            plugin_path: Path to the plugin module
            
        Raises:
            PluginError: If plugin loading fails
        """
        try:
            # Convert path to module name
            module_name = Path(plugin_path).stem
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if spec is None:
                raise PluginError(f"Could not load plugin from {plugin_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find and instantiate the plugin class
            for name, obj in module.__dict__.items():
                if isinstance(obj, type) and issubclass(obj, Plugin) and obj != Plugin:
                    plugin = obj()
                    plugin_name = plugin.get_name()
                    
                    if plugin_name in self._plugins:
                        raise PluginError(f"Plugin {plugin_name} already loaded")
                    
                    # Register platform handler if plugin provides one
                    platform = plugin.get_platform()
                    if platform:
                        handler = plugin.get_message_handler()
                        if handler:
                            self._platform_handlers[platform] = handler
                            logger.info(f"Registered message handler for platform: {platform}")
                    
                    self._plugins[plugin_name] = plugin
                    logger.info(f"Loaded plugin: {plugin_name}")
                    return
            
            raise PluginError(f"No plugin class found in {plugin_path}")
            
        except Exception as e:
            raise PluginError(f"Failed to load plugin from {plugin_path}: {str(e)}")
    
    async def unload_plugin(self, plugin_name: str) -> None:
        """Unload a plugin.
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Raises:
            PluginError: If plugin unloading fails
        """
        if plugin_name not in self._plugins:
            raise PluginError(f"Plugin {plugin_name} not loaded")
        
        plugin = self._plugins[plugin_name]
        
        # Unregister platform handler if this plugin provided one
        platform = plugin.get_platform()
        if platform and platform in self._platform_handlers:
            del self._platform_handlers[platform]
            logger.info(f"Unregistered message handler for platform: {platform}")
        
        try:
            await plugin.stop()
            del self._plugins[plugin_name]
            logger.info(f"Unloaded plugin: {plugin_name}")
        except Exception as e:
            raise PluginError(f"Failed to unload plugin {plugin_name}: {str(e)}")
    
    async def start_plugin(self, plugin_name: str) -> None:
        """Start a plugin.
        
        Args:
            plugin_name: Name of the plugin to start
            
        Raises:
            PluginError: If plugin start fails
        """
        if plugin_name not in self._plugins:
            raise PluginError(f"Plugin {plugin_name} not loaded")
        
        plugin = self._plugins[plugin_name]
        try:
            await plugin.start()
            logger.info(f"Started plugin: {plugin_name}")
        except Exception as e:
            raise PluginError(f"Failed to start plugin {plugin_name}: {str(e)}")
    
    async def stop_plugin(self, plugin_name: str) -> None:
        """Stop a plugin.
        
        Args:
            plugin_name: Name of the plugin to stop
            
        Raises:
            PluginError: If plugin stop fails
        """
        if plugin_name not in self._plugins:
            raise PluginError(f"Plugin {plugin_name} not loaded")
        
        plugin = self._plugins[plugin_name]
        try:
            await plugin.stop()
            logger.info(f"Stopped plugin: {plugin_name}")
        except Exception as e:
            raise PluginError(f"Failed to stop plugin {plugin_name}: {str(e)}")
    
    def register_event_handler(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Register an event handler.
        
        Args:
            event_type: Type of event to handle
            handler: Function to call when event occurs
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    def unregister_event_handler(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Unregister an event handler.
        
        Args:
            event_type: Type of event to unregister
            handler: Handler to remove
        """
        if event_type in self._event_handlers:
            self._event_handlers[event_type].remove(handler)
    
    def emit_event(self, event: Event) -> None:
        """Emit an event to all registered handlers.
        
        Args:
            event: Event to emit
        """
        if event.type in self._event_handlers:
            for handler in self._event_handlers[event.type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {str(e)}")
    
    def get_platform_handler(self, platform: str) -> Optional[Callable]:
        """Get the message handler for a platform.
        
        Args:
            platform: Platform name to get handler for
            
        Returns:
            Optional[Callable]: Message handler if registered, None otherwise
        """
        return self._platform_handlers.get(platform)
    
    async def discover_plugins(self, plugins_dir: str = "plugins", config: dict = None) -> None:
        """Discover and load all plugins in the plugins directory with dynamic settings.
        
        Args:
            plugins_dir: Path to plugins directory (relative to current directory)
            config: Optional configuration dict for plugin settings
        """
        plugins_path = Path(plugins_dir)
        if not plugins_path.exists():
            logger.warning(f"Plugins directory {plugins_dir} does not exist")
            return
        
        for plugin_dir in plugins_path.iterdir():
            if not plugin_dir.is_dir() or plugin_dir.name.startswith('_'):
                continue
            
            plugin_file = plugin_dir / "plugin.py"
            if plugin_file.exists():
                try:
                    # Load the plugin
                    await self.load_plugin(str(plugin_file))
                    
                    # Get the loaded plugin instance
                    plugin_name = plugin_dir.name
                    plugin = self._plugins.get(plugin_name)
                    
                    if plugin is None:
                        logger.error(f"Failed to load plugin {plugin_name} - plugin not found after loading")
                        continue
                    
                    # Get plugin settings schema
                    settings_schema = plugin.get_settings() if hasattr(plugin, 'get_settings') else {}
                    
                    # Load plugin-specific config if available
                    plugin_config = {}
                    if config and plugin_name in config:
                        plugin_config = config[plugin_name]
                    
                    # Apply settings to plugin
                    if hasattr(plugin, 'apply_settings'):
                        plugin.apply_settings(plugin_config)
                        logger.info(f"Applied settings to plugin: {plugin_name}")
                    elif hasattr(plugin, 'validate_settings') and plugin.validate_settings(plugin_config):
                        # Fallback for backward compatibility
                        logger.warning(f"Plugin {plugin_name} should implement apply_settings()")
                    else:
                        logger.info(f"Plugin {plugin_name} loaded without settings")
                    
                    logger.info(f"Loaded plugin: {plugin_name}")
                    
                except PluginError as e:
                    logger.error(f"Failed to load plugin {plugin_dir.name}: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error loading plugin {plugin_dir.name}: {e}")
    
    async def start(self) -> None:
        """Start all loaded plugins."""
        if self._running:
            return
        
        self._running = True
        for plugin_name in list(self._plugins.keys()):
            try:
                await self.start_plugin(plugin_name)
            except PluginError as e:
                logger.error(f"Failed to start plugin {plugin_name}: {str(e)}")
    
    async def stop(self) -> None:
        """Stop all loaded plugins."""
        if not self._running:
            return
        
        self._running = False
        for plugin_name in list(self._plugins.keys()):
            try:
                await self.stop_plugin(plugin_name)
            except PluginError as e:
                logger.error(f"Failed to stop plugin {plugin_name}: {str(e)}")
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a loaded plugin by name.
        
        Args:
            plugin_name: Name of the plugin to get
            
        Returns:
            Optional[Plugin]: The plugin if loaded, None otherwise
        """
        return self._plugins.get(plugin_name)
    
    def get_loaded_plugins(self) -> List[str]:
        """Get names of all loaded plugins.
        
        Returns:
            List[str]: List of loaded plugin names
        """
        return list(self._plugins.keys())
    
    def is_running(self) -> bool:
        """Check if the plugin manager is running.
        
        Returns:
            bool: True if running, False otherwise
        """
        return self._running 