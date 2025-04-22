"""Plugin management and event routing."""
from typing import Dict, List, Optional, Set, Callable
import asyncio
import logging
from broca2.plugins import Plugin, Event, EventType

logger = logging.getLogger(__name__)

class PluginManager:
    """Manages plugin lifecycle and event routing.
    
    This class is responsible for:
    - Loading and unloading plugins
    - Managing plugin lifecycle (start/stop)
    - Routing events between plugins
    - Managing plugin settings
    """
    
    def __init__(self):
        """Initialize the plugin manager."""
        self._plugins: Dict[str, Plugin] = {}
        self._event_handlers: Dict[EventType, Set[Callable]] = {
            event_type: set() for event_type in EventType
        }
        self._running = False
    
    async def load_plugin(self, plugin: Plugin) -> None:
        """Load a plugin.
        
        Args:
            plugin: The plugin to load
            
        Raises:
            ValueError: If a plugin with the same name is already loaded
        """
        name = plugin.get_name()
        if name in self._plugins:
            raise ValueError(f"Plugin {name} is already loaded")
        
        self._plugins[name] = plugin
        logger.info(f"Loaded plugin: {name}")
    
    async def unload_plugin(self, name: str) -> None:
        """Unload a plugin.
        
        Args:
            name: Name of the plugin to unload
            
        Raises:
            KeyError: If the plugin is not loaded
        """
        if name not in self._plugins:
            raise KeyError(f"Plugin {name} is not loaded")
        
        plugin = self._plugins[name]
        if self._running:
            await plugin.stop()
        
        del self._plugins[name]
        logger.info(f"Unloaded plugin: {name}")
    
    async def start_all(self) -> None:
        """Start all loaded plugins."""
        if self._running:
            return
        
        self._running = True
        for name, plugin in self._plugins.items():
            try:
                await plugin.start()
                logger.info(f"Started plugin: {name}")
            except Exception as e:
                logger.error(f"Failed to start plugin {name}: {e}")
                # Don't re-raise, continue with other plugins
    
    async def stop_all(self) -> None:
        """Stop all loaded plugins."""
        if not self._running:
            return
        
        self._running = False
        for name, plugin in self._plugins.items():
            try:
                await plugin.stop()
                logger.info(f"Stopped plugin: {name}")
            except Exception as e:
                logger.error(f"Failed to stop plugin {name}: {e}")
                # Don't re-raise, continue with other plugins
    
    def register_event_handler(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Register an event handler.
        
        Args:
            event_type: Type of event to handle
            handler: Function to call when event occurs
        """
        self._event_handlers[event_type].add(handler)
    
    def unregister_event_handler(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Unregister an event handler.
        
        Args:
            event_type: Type of event to unregister from
            handler: Handler to unregister
        """
        if handler in self._event_handlers[event_type]:
            self._event_handlers[event_type].remove(handler)
    
    def emit_event(self, event: Event) -> None:
        """Emit an event to all registered handlers.
        
        Args:
            event: Event to emit
        """
        handlers = self._event_handlers[event.type]
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event.type}: {e}")
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a loaded plugin by name.
        
        Args:
            name: Name of the plugin to get
            
        Returns:
            The plugin if found, None otherwise
        """
        return self._plugins.get(name)
    
    def get_all_plugins(self) -> List[Plugin]:
        """Get all loaded plugins.
        
        Returns:
            List of all loaded plugins
        """
        return list(self._plugins.values())
    
    def is_running(self) -> bool:
        """Check if plugins are running.
        
        Returns:
            True if plugins are running, False otherwise
        """
        return self._running 