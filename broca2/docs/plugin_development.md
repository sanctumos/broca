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

### Example Skeleton
```python
from plugins import Plugin

class MyPlugin(Plugin):
    def get_name(self):
        return "my_plugin"
    def get_platform(self):
        return "my_platform"
    def get_message_handler(self):
        return self._handle_message
    async def start(self):
        # Startup logic
        pass
    async def stop(self):
        # Cleanup logic
        pass
```

---

## Optional Methods
- `get_settings(self) -> dict | None`: Return plugin-specific settings.
- `validate_settings(self, settings: dict) -> bool`: Validate settings.
- `register_event_handler(self, event_type, handler)`: Register for core/plugin events.
- `emit_event(self, event)`: Emit custom events.

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
- Example:
```python
def get_message_handler(self):
    return self._handle_message

async def _handle_message(self, message, *args, **kwargs):
    # Process message
    pass
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
- Example:
```python
def get_settings(self):
    return {"api_key": "...", "debug": False}
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

---

## Troubleshooting
- Check logs for plugin load/start/stop errors.
- Use the CLI plugin for diagnostics.
- Ensure your plugin does not block the event loop.
- Validate settings before use.

---

## Example: Minimal Plugin
```python
from plugins import Plugin

class EchoPlugin(Plugin):
    def get_name(self):
        return "echo"
    def get_platform(self):
        return "cli"
    def get_message_handler(self):
        return self._echo
    async def start(self):
        print("EchoPlugin started!")
    async def stop(self):
        print("EchoPlugin stopped!")
    async def _echo(self, message, *args, **kwargs):
        print(f"Echo: {message}")
```

---

## Cross-References
- See `plugins/__init__.py` for the Plugin base class.
- See `runtime/core/plugin.py` for PluginManager logic.
- See `plugins/telegram/` for a real-world plugin example.
- See `broca2/docs/cli_reference.md` for CLI plugin details.
- See `broca2/docs/configuration.md` for settings integration.

---

## Extending Sanctum: Broca 2
- Add new plugins in `plugins/`.
- Register them in your config or via PluginManager.
- Follow the interface and lifecycle requirements above.

---

For questions or advanced use cases, see the main README or contact the maintainers. 