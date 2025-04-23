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