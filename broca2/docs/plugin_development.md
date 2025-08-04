# Sanctum: Broca 2 Plugin Development Guide

## Overview
Sanctum: Broca 2 is designed with a plugin-first architecture. **Plugins are the primary way to integrate new endpoints, services, and communication channels**—not just Telegram or CLI, but any system (APIs, bots, webhooks, etc.) that needs to send or receive messages through Sanctum: Broca.

Plugins can:
- Connect Sanctum: Broca to external platforms (e.g., Telegram, Slack, REST APIs, custom bots)
- Add diagnostic or testing surfaces (CLI, admin tools)
- Extend Sanctum: Broca for automation, monitoring, or custom workflows

**CLI tools and plugins are built to be MCP'able:**
- All CLI interfaces are designed so that agents (not just humans) can operate them programmatically.
- This enables Sanctum: Broca to be managed, tested, and extended by other AI agents or automation systems.
- MCP (Machine Control Protocol) compatibility is a core design goal for all admin and plugin interfaces.

---

## Agent/MCP Integration
- Plugins and CLI tools are designed for both human and agent (AI/automation) operation.
- All commands and endpoints are scriptable, with JSON output and machine-friendly error handling.
- This allows Sanctum: Broca to be embedded in larger agent networks, automated test harnesses, or orchestration systems.
- When building a plugin or CLI, always consider how an agent would interact with it (not just a human).

---

## Plugin Architecture
- All plugins inherit from the `Plugin` base class (`plugins/__init__.py`).
- Plugins are managed by the `PluginManager` (`runtime/core/plugin.py`).
- Plugins are loaded, started, and stopped independently.
- Each plugin must implement a standardized interface.

---

## Required Methods
Every plugin **must** implement:
- `get_name(self) -> str`: Unique plugin identifier.
- `get_platform(self) -> str`: Platform name (e.g., 'telegram', 'cli').
- `get_message_handler(self) -> Callable`: Returns the message handler function/coroutine.
- `start(self) -> Awaitable`: Async initialization logic.
- `stop(self) -> Awaitable`: Async cleanup logic.
- `apply_settings(self, settings: Dict[str, Any]) -> None`: Apply dynamic settings (NEW).

### Example Skeleton
```python
from plugins import Plugin

class MyPlugin(Plugin):
    def get_name(self):
        return "my_plugin"
    def get_platform(self):
        return "my_platform"
    def get_message_handler(self):
        return self._handle_response  # Must return a callable function
    async def start(self):
        # Startup logic
        pass
    async def stop(self):
        # Cleanup logic
        pass
    def apply_settings(self, settings: Dict[str, Any]) -> None:
        """Apply dynamic settings to the plugin."""
        if settings:
            # Apply settings logic here
            pass
```

---

## Optional Methods
- `get_settings(self) -> dict | None`: Return plugin-specific settings.
- `validate_settings(self, settings: dict) -> bool`: Validate settings.
- `register_event_handler(self, event_type, handler)`: Register for core/plugin events.
- `emit_event(self, event)`: Emit custom events.

## Critical Implementation Details

### Message Handler Requirements
- **Must return a callable function**: `get_message_handler()` must return a function that can be called by the queue processor.
- **Function signature**: The handler should accept `(response: str, profile, message_id: int)` parameters.
- **Example implementation**:
```python
def get_message_handler(self):
    return self._handle_response

async def _handle_response(self, response: str, profile, message_id: int) -> None:
    """Handle sending a response to the platform."""
    # Extract platform-specific data from profile
    # Send response via platform API
    pass
```

### Lazy Import Pattern
- **Self-contained plugins**: All external dependencies should be imported lazily (inside methods, not at module level).
- **Core dependencies**: Only `letta_client` should be imported at the top level as it's core infrastructure.
- **Example**:
```python
# ❌ BAD - Module-level import
from aiogram import Bot
from telethon import TelegramClient

# ✅ GOOD - Lazy import
async def start(self):
    from aiogram import Bot
    from telethon import TelegramClient
    # Use imports here
```

### Settings Management
- **Lazy initialization**: Initialize settings in `__init__()` but load them lazily in `get_settings()`.
- **Fallback values**: Provide sensible defaults when settings are `None`.
- **Example**:
```python
def __init__(self, settings=None):
    self.settings = settings  # Don't load immediately

def get_settings(self):
    if self.settings is None:
        self.settings = self.load_settings_from_env()
    return self.settings.to_dict()

def get_name(self):
    if self.settings is None:
        return "my_plugin"  # Fallback
    return self.settings.plugin_name
```

---

## Plugin Lifecycle
- **Initialization:** Instantiated by PluginManager.
- **Start:** `await plugin.start()` is called when the system starts.
- **Stop:** `await plugin.stop()` is called on shutdown or reload.
- **Settings:** Loaded from config and passed to the plugin if needed.

---

## Message Handler Integration
- Each plugin must provide a message handler (function or coroutine).
- The handler is registered with the PluginManager for its platform.
- **Critical**: The handler must be callable and accept the correct parameters.

### Response Handler Pattern
The queue processor calls your handler with: `(response: str, profile, message_id: int)`

```python
def get_message_handler(self):
    return self._handle_response

async def _handle_response(self, response: str, profile, message_id: int) -> None:
    """Handle sending a response to the platform."""
    try:
        # Extract platform-specific data from profile
        metadata = profile.metadata
        if isinstance(metadata, str):
            import json
            metadata = json.loads(metadata)
        
        # Send response via platform API
        success = await self.send_response(metadata.get('session_id'), response)
        
        if success:
            self.logger.info(f"Successfully sent response")
        else:
            self.logger.error(f"Failed to send response")
            
    except Exception as e:
        self.logger.error(f"Error handling response: {e}")
```

### Incoming Message Processing
For plugins that poll for messages (like web chat), process incoming messages in your polling loop:

```python
async def _process_message(self, message_data: Dict[str, Any]):
    """Process a single message from the platform."""
    try:
        # Create/update user and profile
        # Insert message into database
        # Add to processing queue
        message_id = await self.message_handler.process_incoming_message(message_data)
        
        if message_id:
            self.logger.info(f"Message queued for processing")
            
    except Exception as e:
        self.logger.error(f"Error processing message: {e}")
```

---

## Event and Error Handling
- Plugins can register for core events (message, status, error).
- Use `register_event_handler` and `emit_event` for custom workflows.
- Handle errors gracefully and log using the core logger.

---

## Settings and Configuration
- Plugin settings are defined in the plugin and/or loaded from config files.
- Use `get_settings` and `validate_settings` for custom options.
- **Dynamic settings**: Use `apply_settings()` for runtime configuration changes.

### Settings Pattern
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class MyPluginSettings:
    api_key: Optional[str] = None
    api_url: str = "https://api.example.com"
    poll_interval: int = 5
    debug: bool = False
    
    @classmethod
    def from_env(cls):
        """Load settings from environment variables."""
        return cls(
            api_key=os.getenv("MY_PLUGIN_API_KEY"),
            api_url=os.getenv("MY_PLUGIN_API_URL", "https://api.example.com"),
            poll_interval=int(os.getenv("MY_PLUGIN_POLL_INTERVAL", "5")),
            debug=os.getenv("MY_PLUGIN_DEBUG", "false").lower() == "true"
        )
    
    def to_dict(self):
        return {
            "api_key": self.api_key,
            "api_url": self.api_url,
            "poll_interval": self.poll_interval,
            "debug": self.debug
        }

class MyPlugin(Plugin):
    def __init__(self, settings=None):
        self.settings = settings  # Lazy initialization
    
    def get_settings(self):
        if self.settings is None:
            self.settings = MyPluginSettings.from_env()
        return self.settings.to_dict()
    
    def apply_settings(self, settings: Dict[str, Any]) -> None:
        """Apply dynamic settings."""
        if settings:
            self.settings = MyPluginSettings(**settings)
```

---

## Registering and Enabling Plugins
- Plugins are discovered and loaded by the PluginManager.
- To enable/disable a plugin, update the config and restart Sanctum: Broca 2.
- Plugins should clean up all resources on stop.

---

## Best Practices
- Keep plugins isolated: no cross-plugin dependencies.
- Use async/await for all I/O.
- Log all significant actions and errors.
- Validate all external input.
- Document your plugin's settings and usage.

### Database Integration
- **User creation**: Use `get_or_create_letta_user()` and `get_or_create_platform_profile()` for consistent user management.
- **Message handling**: Use `insert_message()` and `add_to_queue()` for message processing.
- **Profile metadata**: Store platform-specific data (like session IDs) in profile metadata.

```python
# Create user and profile
letta_user = await get_or_create_letta_user(
    username=f"web_user_{platform_user_id}",
    display_name=f"Web User ({platform_user_id[:8]})",
    platform_user_id=platform_user_id
)

platform_profile, _ = await get_or_create_platform_profile(
    platform=self.platform_name,
    platform_user_id=platform_user_id,
    username=f"web_user_{platform_user_id}",
    display_name=f"Web User ({platform_user_id[:8]})",
    metadata={
        'session_id': session_id,
        'uid': uid,
        'source': 'web_chat'
    }
)

# Insert message
message_id = await insert_message(
    letta_user_id=letta_user.id,
    platform_profile_id=platform_profile.id,
    role="user",
    message=message_text,
    timestamp=timestamp
)

# Add to queue
await add_to_queue(
    letta_user_id=letta_user.id,
    message_id=message_id
)
```

### Error Handling
- **Graceful degradation**: Handle missing settings, network errors, and invalid data.
- **Logging**: Use structured logging with appropriate levels.
- **Resource cleanup**: Always clean up connections and resources in `stop()`.

### Platform-Specific Considerations
- **Polling plugins**: Implement proper backoff and retry logic.
- **API plugins**: Handle rate limits and authentication errors.
- **Real-time plugins**: Manage connection state and reconnection logic.

---

## Troubleshooting

### Common Issues
- **"Object is not callable"**: Ensure `get_message_handler()` returns a function, not an object.
- **"Module not found"**: Use lazy imports for external dependencies.
- **"User details not found"**: Check that users and profiles are created correctly.
- **"Settings validation failed"**: Provide fallback values for missing settings.

### Debugging Checklist
- [ ] Plugin loads without errors during discovery
- [ ] Plugin starts successfully
- [ ] Message handler is callable
- [ ] Database operations succeed
- [ ] Queue processing works
- [ ] Response routing functions

### Logging Strategy
```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debugging info")
logger.info("General information")
logger.warning("Warning messages")
logger.error("Error conditions")
```

### Testing Your Plugin
1. **Isolation testing**: Test plugin methods in isolation
2. **Integration testing**: Test with the full system
3. **Error testing**: Test with invalid data and network failures
4. **Performance testing**: Test with high message volumes

---

## Example: Complete Plugin
```python
from plugins import Plugin
from typing import Dict, Any, Optional
import asyncio
import logging
from dataclasses import dataclass
import os

@dataclass
class MyPluginSettings:
    api_key: Optional[str] = None
    api_url: str = "https://api.example.com"
    poll_interval: int = 5
    
    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv("MY_PLUGIN_API_KEY"),
            api_url=os.getenv("MY_PLUGIN_API_URL", "https://api.example.com"),
            poll_interval=int(os.getenv("MY_PLUGIN_POLL_INTERVAL", "5"))
        )
    
    def to_dict(self):
        return {
            "api_key": self.api_key,
            "api_url": self.api_url,
            "poll_interval": self.poll_interval
        }

class MyPlugin(Plugin):
    def __init__(self, settings: Optional[MyPluginSettings] = None):
        self.settings = settings
        self.is_running = False
        self.polling_task = None
        self.logger = logging.getLogger(__name__)
    
    def get_name(self) -> str:
        if self.settings is None:
            return "my_plugin"
        return "my_plugin"
    
    def get_platform(self) -> str:
        if self.settings is None:
            return "my_platform"
        return "my_platform"
    
    def get_message_handler(self):
        return self._handle_response
    
    def get_settings(self) -> Dict[str, Any]:
        if self.settings is None:
            self.settings = MyPluginSettings.from_env()
        return self.settings.to_dict()
    
    def apply_settings(self, settings: Dict[str, Any]) -> None:
        if settings:
            self.settings = MyPluginSettings(**settings)
            self.logger.info(f"Applied settings to plugin: {self.get_name()}")
    
    async def start(self):
        if self.is_running:
            self.logger.warning("Plugin is already running")
            return
        
        try:
            # Initialize API client (lazy import)
            from my_plugin.api_client import APIClient
            self.api_client = APIClient(self.settings)
            
            # Test connection
            if not await self.api_client.test_connection():
                self.logger.error("Failed to connect to API")
                return
            
            self.logger.info("My Plugin started successfully")
            self.is_running = True
            
            # Start polling task
            self.polling_task = asyncio.create_task(self._poll_messages())
            
        except Exception as e:
            self.logger.error(f"Error starting My Plugin: {e}")
            raise
    
    async def stop(self):
        if not self.is_running:
            return
        
        self.logger.info("Stopping My Plugin...")
        self.is_running = False
        
        # Cancel polling task
        if self.polling_task:
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
        
        # Close API client
        if hasattr(self, 'api_client') and self.api_client:
            await self.api_client.close()
        
        self.logger.info("My Plugin stopped")
    
    async def _poll_messages(self):
        """Poll for new messages from the API."""
        while self.is_running:
            try:
                # Get messages from API
                messages = await self.api_client.get_messages()
                
                for message_data in messages:
                    if not self.is_running:
                        break
                    await self._process_message(message_data)
                
                await asyncio.sleep(self.settings.poll_interval)
                
            except asyncio.CancelledError:
                self.logger.info("Message polling cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in message polling: {e}")
                await asyncio.sleep(self.settings.retry_delay)
    
    async def _process_message(self, message_data: Dict[str, Any]):
        """Process a single message from the API."""
        try:
            # Process message with message handler
            message_id = await self.message_handler.process_incoming_message(message_data)
            
            if message_id:
                self.logger.info(f"Message queued for processing")
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    async def _handle_response(self, response: str, profile, message_id: int) -> None:
        """Handle sending a response to the platform."""
        try:
            # Extract platform-specific data from profile
            metadata = profile.metadata
            if isinstance(metadata, str):
                import json
                metadata = json.loads(metadata)
            
            # Send response via API
            success = await self.api_client.send_response(
                metadata.get('session_id'), 
                response
            )
            
            if success:
                self.logger.info(f"Successfully sent response")
            else:
                self.logger.error(f"Failed to send response")
                
        except Exception as e:
            self.logger.error(f"Error handling response: {e}")
```

---

## Cross-References
- See `plugins/__init__.py` for the Plugin base class.
- See `runtime/core/plugin.py` for PluginManager logic.
- See `plugins/telegram/` for a real-world plugin example.
- See `plugins/web_chat/` for a complete polling plugin example.
- See `broca2/docs/cli_reference.md` for CLI plugin details.
- See `broca2/docs/configuration.md` for settings integration.

## Key Learnings from Web Chat Plugin Development

### Auto-Discovery System
- **Plugin discovery**: Plugins are automatically discovered from the `plugins/` directory.
- **Dynamic loading**: Plugins are loaded, configured, and started automatically.
- **Settings injection**: Plugin settings are injected via `apply_settings()` method.

### Message Flow Architecture
1. **Incoming messages**: Polled from external APIs or received via webhooks
2. **User creation**: Users and profiles are created/updated in the database
3. **Message insertion**: Messages are stored in the database
4. **Queue processing**: Messages are queued for agent processing
5. **Agent response**: Agent processes messages and generates responses
6. **Response routing**: Responses are routed back to the original platform

### Database Integration Patterns
- **User management**: Use `get_or_create_letta_user()` for consistent user creation
- **Profile management**: Use `get_or_create_platform_profile()` for platform-specific data
- **Message handling**: Use `insert_message()` and `add_to_queue()` for message processing
- **Metadata storage**: Store platform-specific data (session IDs, etc.) in profile metadata

### Error Handling Patterns
- **Graceful degradation**: Handle missing settings and network failures
- **Resource cleanup**: Always clean up connections and tasks in `stop()`
- **Logging**: Use structured logging with appropriate levels
- **Retry logic**: Implement exponential backoff for polling operations

---

## Extending Sanctum: Broca 2
- Add new plugins in `plugins/`.
- Register them in your config or via PluginManager.
- Follow the interface and lifecycle requirements above.

---

For questions or advanced use cases, see the main README or contact the maintainers. 