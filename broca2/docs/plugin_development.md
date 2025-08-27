# ⚠️ REPOSITORY MOVED ⚠️

**This repository has moved to: [http://github.com/sanctumos/broca](http://github.com/sanctumos/broca)**

Please update your git remotes and use the new repository location for all future development and contributions.

---

# Sanctum: Broca 2 Plugin Development Guide

## Overview
Sanctum: Broca 2 is designed with a plugin-first architecture. **Plugins are the primary way to integrate new endpoints, services, and communication channels**—not just Telegram or CLI, but any system (APIs, bots, webhooks, etc.) that needs to send or receive messages through Sanctum: Broca.

With the new multi-agent architecture, plugins can:
- Connect Sanctum: Broca to external platforms (e.g., Telegram, Slack, REST APIs, custom bots)
- Add diagnostic or testing surfaces (CLI, admin tools)
- Extend Sanctum: Broca for automation, monitoring, or custom workflows
- **Work with multiple agent instances** through shared base installation

**CLI tools and plugins are built to be MCP'able:**
- All CLI interfaces are designed so that agents (not just humans) can operate them programmatically.
- This enables Sanctum: Broca to be managed, tested, and extended by other AI agents or automation systems.
- MCP (Machine Control Protocol) compatibility is a core design goal for all admin and plugin interfaces.

---

## Multi-Agent Plugin Architecture

### Plugin Location and Sharing
- **Base Installation**: Plugins are installed in `broca2/plugins/` and shared across all agent instances
- **Agent Instances**: Each agent instance can have its own plugin configuration and settings
- **Shared Resources**: Plugin code and dependencies are shared, but configuration is per-agent

### Plugin Configuration Hierarchy
1. **Agent-specific settings** (`agent-{uuid}/settings.json`) - Highest priority
2. **Agent-specific environment** (`agent-{uuid}/.env`) - Second priority
3. **Base plugin settings** (`broca2/settings.json`) - Third priority
4. **Base environment** (`broca2/.env`) - Fourth priority
5. **Default values** (hardcoded in plugin) - Lowest priority

### Example: Plugin Configuration
```json
// broca2/settings.json (base)
{
  "plugins": {
    "telegram": {
      "enabled": true,
      "parse_mode": "MarkdownV2",
      "session_timeout": 3600
    }
  }
}

// broca2/agent-{uuid}/settings.json (agent-specific)
{
  "plugins": {
    "telegram": {
      "enabled": true,
      "parse_mode": "MarkdownV2",
      "custom_setting": "agent_specific_value"
    }
  }
}
```

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
- **Plugins can access agent-specific configuration** through the plugin manager.

---

## Required Methods
Every plugin **must** implement:
- `get_name(self) -> str`: Unique plugin identifier.
- `get_platform(self) -> str`: Platform name (e.g., 'telegram', 'cli').
- `get_message_handler(self) -> Callable`: Returns the message handler function/coroutine.
- `start(self) -> Awaitable`: Async initialization logic.
- `stop(self) -> Awaitable`: Async cleanup logic.
- `apply_settings(self, settings: Dict[str, Any]) -> None`: Apply dynamic settings (NEW).

### Example Skeleton with Multi-Agent Support
```python
from plugins import Plugin
from typing import Dict, Any, Optional

class MyPlugin(Plugin):
    def __init__(self, settings=None, agent_id=None):
        self.settings = settings
        self.agent_id = agent_id  # Track which agent this plugin instance serves
        super().__init__()
    
    def get_name(self):
        return "my_plugin"
    
    def get_platform(self):
        return "my_platform"
    
    def get_message_handler(self):
        return self._handle_response  # Must return a callable function
    
    async def start(self):
        # Startup logic - can use agent_id for agent-specific initialization
        if self.agent_id:
            self.logger.info(f"Starting plugin for agent: {self.agent_id}")
        pass
    
    async def stop(self):
        # Cleanup logic
        pass
    
    def apply_settings(self, settings: Dict[str, Any]) -> None:
        """Apply dynamic settings to the plugin."""
        if settings:
            # Apply settings logic here
            # Can merge agent-specific settings with base settings
            pass
    
    def get_agent_specific_setting(self, key: str, default=None):
        """Get agent-specific setting with fallback to base setting."""
        if self.agent_id and hasattr(self, 'agent_settings'):
            return self.agent_settings.get(key, default)
        return self.settings.get(key, default) if self.settings else default
```

---

## Optional Methods
- `get_settings(self) -> dict | None`: Return plugin-specific settings.
- `validate_settings(self, settings: dict) -> bool`: Validate settings.
- `register_event_handler(self, event_type, handler)`: Register for core/plugin events.
- `emit_event(self, event)`: Emit custom events.
- `get_agent_specific_setting(self, key: str, default=None)`: Get agent-specific configuration.

## Critical Implementation Details

### Message Handler Requirements
- **Must return a callable function**: `get_message_handler()` must return a function that can be called by the queue processor.
- **Function signature**: The handler should accept `(response: str, profile, message_id: int)` parameters.
- **Agent awareness**: The handler can access agent-specific configuration through `self.agent_id`.

### Example implementation with multi-agent support:
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
        
        # Use agent-specific settings if available
        api_key = self.get_agent_specific_setting('API_KEY', 'default_key')
        endpoint = self.get_agent_specific_setting('API_ENDPOINT', 'default_endpoint')
        
        # Send response via platform API
        success = await self.send_response(metadata.get('session_id'), response, api_key, endpoint)
        
        if success:
            self.logger.info(f"Successfully sent response for agent {self.agent_id}")
        else:
            self.logger.error(f"Failed to send response for agent {self.agent_id}")
            
    except Exception as e:
        self.logger.error(f"Error handling response for agent {self.agent_id}: {e}")
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

### Settings Management with Multi-Agent Support
- **Lazy initialization**: Initialize settings in `__init__()` but load them lazily in `get_settings()`.
- **Fallback values**: Provide sensible defaults when settings are `None`.
- **Agent-specific overrides**: Support both base and agent-specific configuration.

```python
def __init__(self, settings=None, agent_id=None):
    self.settings = settings  # Don't load immediately
    self.agent_id = agent_id
    self.agent_settings = None

def get_settings(self):
    if self.settings is None:
        self.settings = self.load_settings_from_env()
    
    # Load agent-specific settings if available
    if self.agent_id:
        self.agent_settings = self.load_agent_specific_settings(self.agent_id)
    
    return self.settings.to_dict()

def get_agent_specific_setting(self, key: str, default=None):
    """Get setting with agent-specific override."""
    # Check agent-specific settings first
    if self.agent_settings and key in self.agent_settings:
        return self.agent_settings[key]
    
    # Fall back to base settings
    if self.settings and key in self.settings:
        return self.settings[key]
    
    # Finally, use default
    return default
```

---

## Plugin Lifecycle in Multi-Agent Environment
- **Initialization:** Instantiated by PluginManager with agent context.
- **Start:** `await plugin.start()` is called when the agent instance starts.
- **Stop:** `await plugin.stop()` is called on agent shutdown or reload.
- **Settings:** Loaded from both base config and agent-specific config.
- **Agent Context:** Plugin maintains awareness of which agent instance it serves.

---

## Message Handler Integration
- Each plugin must provide a message handler (function or coroutine).
- The handler is registered with the PluginManager for its platform.
- **Critical**: The handler must be callable and accept the correct parameters.
- **Multi-Agent**: Handler can access agent-specific configuration and context.

### Response Handler Pattern with Multi-Agent Support
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
        
        # Use agent-specific configuration
        api_key = self.get_agent_specific_setting('API_KEY')
        endpoint = self.get_agent_specific_setting('API_ENDPOINT')
        
        # Send response via platform API
        success = await self.send_response(metadata.get('session_id'), response)
        
        if success:
            self.logger.info(f"Successfully sent response for agent {self.agent_id}")
        else:
            self.logger.error(f"Failed to send response for agent {self.agent_id}")
            
    except Exception as e:
        self.logger.error(f"Error handling response for agent {self.agent_id}: {e}")
```

### Incoming Message Processing with Multi-Agent Support
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
            self.logger.info(f"Message queued for processing by agent {self.agent_id}")
            
    except Exception as e:
        self.logger.error(f"Error processing message for agent {self.agent_id}: {e}")
```

---

## Event and Error Handling
- Plugins can register for core events (message, status, error).
- Use `register_event_handler` and `emit_event` for custom workflows.
- Handle errors gracefully and log using the core logger.
- **Multi-Agent**: Include agent context in logging and error handling.

---

## Settings and Configuration with Multi-Agent Support
- Plugin settings are defined in the plugin and/or loaded from config files.
- Use `get_settings` and `validate_settings` for custom options.
- **Agent-specific overrides**: Support both base and agent-specific configuration.
- **Configuration inheritance**: Implement proper fallback from agent-specific to base settings.

### Example: Plugin Settings with Multi-Agent Support
```python
class MyPlugin(Plugin):
    def __init__(self, settings=None, agent_id=None):
        self.settings = settings
        self.agent_id = agent_id
        self.agent_settings = None
    
    def get_settings(self):
        """Get merged settings (agent-specific + base)."""
        base_settings = self.settings or {}
        
        if self.agent_id:
            # Load agent-specific settings
            agent_config_path = f"agent-{self.agent_id}/settings.json"
            if os.path.exists(agent_config_path):
                try:
                    with open(agent_config_path, 'r') as f:
                        self.agent_settings = json.load(f)
                except Exception as e:
                    self.logger.warning(f"Failed to load agent settings: {e}")
        
        # Merge settings (agent-specific overrides base)
        merged_settings = base_settings.copy()
        if self.agent_settings and 'plugins' in self.agent_settings:
            plugin_settings = self.agent_settings['plugins'].get(self.get_name(), {})
            merged_settings.update(plugin_settings)
        
        return merged_settings
    
    def validate_settings(self, settings: dict) -> bool:
        """Validate both base and agent-specific settings."""
        # Validate base settings
        if not super().validate_settings(settings):
            return False
        
        # Validate agent-specific settings if present
        if self.agent_settings:
            agent_plugin_settings = self.agent_settings.get('plugins', {}).get(self.get_name(), {})
            if not self._validate_agent_settings(agent_plugin_settings):
                return False
        
        return True
```

---

## Plugin Development Best Practices for Multi-Agent

### 1. **Agent Context Awareness**
- Always consider which agent instance the plugin is serving
- Use agent-specific configuration when available
- Log with agent context for easier debugging

### 2. **Configuration Management**
- Implement proper fallback from agent-specific to base settings
- Validate both base and agent-specific configurations
- Support dynamic configuration updates

### 3. **Resource Isolation**
- Ensure plugin resources are properly isolated between agents
- Use agent-specific paths for files, databases, and logs
- Avoid sharing mutable state between agent instances

### 4. **Error Handling**
- Include agent context in all error messages and logs
- Implement proper cleanup for agent-specific resources
- Handle configuration errors gracefully

### 5. **Testing**
- Test plugins with multiple agent instances
- Verify configuration inheritance and overrides
- Test agent isolation and resource separation

---

## Example: Complete Multi-Agent Plugin

```python
#!/usr/bin/env python3
"""Example plugin with full multi-agent support."""

import os
import json
import logging
from typing import Dict, Any, Optional
from plugins import Plugin

class ExamplePlugin(Plugin):
    def __init__(self, settings=None, agent_id=None):
        self.settings = settings
        self.agent_id = agent_id
        self.agent_settings = None
        self.logger = logging.getLogger(f"ExamplePlugin.{agent_id or 'base'}")
        
        # Initialize plugin-specific attributes
        self.api_client = None
        self.polling_task = None
    
    def get_name(self):
        return "example_plugin"
    
    def get_platform(self):
        return "example_platform"
    
    def get_message_handler(self):
        return self._handle_response
    
    async def start(self):
        """Initialize the plugin for the specific agent."""
        try:
            # Load settings
            settings = self.get_settings()
            
            # Initialize API client with agent-specific configuration
            api_key = self.get_agent_specific_setting('API_KEY')
            endpoint = self.get_agent_specific_setting('API_ENDPOINT')
            
            self.api_client = await self._create_api_client(api_key, endpoint)
            
            # Start polling for incoming messages
            self.polling_task = asyncio.create_task(self._poll_messages())
            
            self.logger.info(f"Plugin started for agent {self.agent_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to start plugin for agent {self.agent_id}: {e}")
            raise
    
    async def stop(self):
        """Clean up plugin resources."""
        try:
            if self.polling_task:
                self.polling_task.cancel()
                try:
                    await self.polling_task
                except asyncio.CancelledError:
                    pass
            
            if self.api_client:
                await self.api_client.close()
            
            self.logger.info(f"Plugin stopped for agent {self.agent_id}")
            
        except Exception as e:
            self.logger.error(f"Error stopping plugin for agent {self.agent_id}: {e}")
    
    def apply_settings(self, settings: Dict[str, Any]) -> None:
        """Apply dynamic settings updates."""
        if settings:
            # Update plugin settings
            self.settings.update(settings)
            
            # Reconfigure if needed
            if self.api_client:
                asyncio.create_task(self._reconfigure())
    
    def get_settings(self):
        """Get merged settings (agent-specific + base)."""
        base_settings = self.settings or {}
        
        if self.agent_id:
            # Load agent-specific settings
            agent_config_path = f"agent-{self.agent_id}/settings.json"
            if os.path.exists(agent_config_path):
                try:
                    with open(agent_config_path, 'r') as f:
                        self.agent_settings = json.load(f)
                except Exception as e:
                    self.logger.warning(f"Failed to load agent settings: {e}")
        
        # Merge settings (agent-specific overrides base)
        merged_settings = base_settings.copy()
        if self.agent_settings and 'plugins' in self.agent_settings:
            plugin_settings = self.agent_settings['plugins'].get(self.get_name(), {})
            merged_settings.update(plugin_settings)
        
        return merged_settings
    
    def get_agent_specific_setting(self, key: str, default=None):
        """Get agent-specific setting with fallback to base setting."""
        # Check agent-specific settings first
        if self.agent_settings and 'plugins' in self.agent_settings:
            plugin_settings = self.agent_settings['plugins'].get(self.get_name(), {})
            if key in plugin_settings:
                return plugin_settings[key]
        
        # Fall back to base settings
        if self.settings and key in self.settings:
            return self.settings[key]
        
        # Finally, use default
        return default
    
    async def _handle_response(self, response: str, profile, message_id: int) -> None:
        """Handle sending a response to the platform."""
        try:
            # Extract platform-specific data from profile
            metadata = profile.metadata
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
            
            # Send response via platform API
            success = await self._send_response(metadata.get('session_id'), response)
            
            if success:
                self.logger.info(f"Successfully sent response for agent {self.agent_id}")
            else:
                self.logger.error(f"Failed to send response for agent {self.agent_id}")
                
        except Exception as e:
            self.logger.error(f"Error handling response for agent {self.agent_id}: {e}")
    
    async def _poll_messages(self):
        """Poll for incoming messages from the platform."""
        while True:
            try:
                # Poll for messages using agent-specific configuration
                messages = await self._fetch_messages()
                
                for message in messages:
                    await self._process_message(message)
                
                # Wait before next poll
                await asyncio.sleep(self.get_agent_specific_setting('POLL_INTERVAL', 5))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error polling messages for agent {self.agent_id}: {e}")
                await asyncio.sleep(5)  # Wait before retry
    
    async def _process_message(self, message_data: Dict[str, Any]):
        """Process a single message from the platform."""
        try:
            # Create/update user and profile
            # Insert message into database
            # Add to processing queue
            message_id = await self.message_handler.process_incoming_message(message_data)
            
            if message_id:
                self.logger.info(f"Message queued for processing by agent {self.agent_id}")
                
        except Exception as e:
            self.logger.error(f"Error processing message for agent {self.agent_id}: {e}")
    
    async def _create_api_client(self, api_key: str, endpoint: str):
        """Create API client with agent-specific configuration."""
        # Implementation depends on the specific platform
        pass
    
    async def _send_response(self, session_id: str, response: str) -> bool:
        """Send response via platform API."""
        # Implementation depends on the specific platform
        pass
    
    async def _fetch_messages(self) -> list:
        """Fetch messages from the platform."""
        # Implementation depends on the specific platform
        pass
    
    async def _reconfigure(self):
        """Reconfigure plugin with new settings."""
        # Implementation for dynamic reconfiguration
        pass
```

---

## Cross-References
- See `plugins/` directory for existing plugin implementations
- See `broca2/docs/multi-agent-architecture.md` for multi-agent setup
- See `broca2/docs/configuration.md` for configuration details
- See `broca2/docs/cli_reference.md` for CLI tool usage

---

For more details, see the main README or contact the maintainers. 