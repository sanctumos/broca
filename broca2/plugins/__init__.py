"""Plugins package for broca2."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum, auto

class EventType(Enum):
    """Core event types that plugins can handle."""
    MESSAGE = auto()  # New message received
    STATUS = auto()   # Status update
    ERROR = auto()    # Error occurred

@dataclass
class Event:
    """Base event class for plugin communication."""
    type: EventType
    data: Dict[str, Any]
    source: str  # Plugin that generated the event

class Plugin(ABC):
    """Base class for all plugins.
    
    This class defines the required interface that all plugins must implement.
    Plugins should inherit from this class and implement the required methods.
    """
    
    @abstractmethod
    async def start(self) -> None:
        """Start the plugin.
        
        This method should:
        - Initialize any required resources
        - Set up event handlers
        - Start any background tasks
        """
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the plugin.
        
        This method should:
        - Clean up resources
        - Stop background tasks
        - Close any connections
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the plugin's name.
        
        Returns:
            str: The plugin's name, used for identification and logging.
        """
        pass
    
    def get_settings(self) -> Optional[Dict[str, Any]]:
        """Get the plugin's settings.
        
        This is an optional method that plugins can override to provide
        their specific settings. The base implementation returns None.
        
        Returns:
            Optional[Dict[str, Any]]: Plugin settings or None if no settings.
        """
        return None
    
    def validate_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate plugin settings.
        
        This is an optional method that plugins can override to validate
        their settings. The base implementation always returns True.
        
        Args:
            settings: Settings to validate
            
        Returns:
            bool: True if settings are valid, False otherwise
        """
        return True
    
    def register_event_handler(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Register an event handler.
        
        This is an optional method that plugins can override to handle
        specific event types. The base implementation does nothing.
        
        Args:
            event_type: Type of event to handle
            handler: Function to call when event occurs
        """
        pass
    
    def emit_event(self, event: Event) -> None:
        """Emit an event.
        
        This is an optional method that plugins can override to emit
        events. The base implementation does nothing.
        
        Args:
            event: Event to emit
        """
        pass
