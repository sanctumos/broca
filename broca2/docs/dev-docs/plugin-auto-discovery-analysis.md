# ⚠️ REPOSITORY MOVED ⚠️

**This repository has moved to: [http://github.com/sanctumos/broca](http://github.com/sanctumos/broca)**

Please update your git remotes and use the new repository location for all future development and contributions.

---

# Plugin Auto-Discovery Analysis

## Executive Summary

After extensive analysis of the Broca2 codebase, I've identified that **plugin auto-discovery is completely missing**. The application currently only manually loads the Telegram plugin and has no mechanism to discover or load other plugins automatically.

## Current State Analysis

### ✅ What Exists
1. **PluginManager class** (`broca2/runtime/core/plugin.py`)
   - Has `load_plugin(plugin_path: str)` method
   - Has `start()` and `stop()` methods for all loaded plugins
   - Has proper plugin lifecycle management
   - Has platform handler registration

2. **Plugin Interface** (`broca2/plugins/__init__.py`)
   - Well-defined `Plugin` abstract base class
   - Required methods: `start()`, `stop()`, `get_name()`, `get_platform()`, `get_message_handler()`
   - Optional methods: `get_settings()`, `validate_settings()`

3. **Plugin Structure**
   - Plugins are organized in `broca2/plugins/` directory
   - Each plugin has its own subdirectory (e.g., `telegram/`, `fake_plugin/`)
   - Plugins follow consistent structure with `__init__.py` and `plugin.py`

### ❌ What's Missing
1. **No Auto-Discovery Mechanism**
   - No directory scanning
   - No plugin enumeration
   - No automatic loading

2. **Hardcoded Plugin Loading**
   - Only Telegram plugin is manually loaded in `main.py`
   - No dynamic plugin discovery

## Detailed Analysis

### 1. Plugin Loading in main.py

**Current Implementation (Lines 62-68):**
```python
# Load the telegram plugin
self.plugin_manager._plugins[self.telegram.get_name()] = self.telegram
platform = self.telegram.get_platform()
if platform:
    handler = self.telegram.get_message_handler()
    if handler:
        self.plugin_manager._platform_handlers[platform] = handler
        logger.info(f"Registered message handler for platform: {platform}")
```

**Problems:**
- Only loads Telegram plugin explicitly
- No scanning of plugins directory
- No use of `PluginManager.load_plugin()` method
- No error handling for missing plugins

### 2. PluginManager Capabilities

**Available Methods:**
- `load_plugin(plugin_path: str)` - Loads plugin from file path
- `start()` - Starts all loaded plugins
- `stop()` - Stops all loaded plugins
- `get_loaded_plugins()` - Returns list of loaded plugin names

**Missing Methods:**
- No `discover_plugins()` method
- No `scan_plugins_directory()` method
- No automatic plugin enumeration

### 3. Plugin Directory Structure

**Current Structure:**
```
broca2/plugins/
├── __init__.py              # Plugin interface definitions
├── telegram/                # Telegram plugin
│   ├── __init__.py
│   ├── telegram_plugin.py
│   └── handlers.py
├── fake_plugin/             # Test plugin
│   ├── __init__.py
│   ├── plugin.py
│   └── README.md
├── telegram_bot/            # Alternative Telegram plugin
├── cli_test/               # CLI test plugin
└── __pycache__/
```

**Discovery Requirements:**
- Scan `broca2/plugins/` directory
- Find subdirectories (excluding `__pycache__`)
- Look for `plugin.py` files in each subdirectory
- Load plugins that implement the `Plugin` interface

## Required Changes

### 1. Enhanced Plugin Discovery with Settings Management

**File:** `broca2/runtime/core/plugin.py`

**Add new method:**
```python
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
                plugin = await self.load_plugin(str(plugin_file))
                
                # Get plugin settings schema
                settings_schema = plugin.get_settings() if hasattr(plugin, 'get_settings') else {}
                
                # Load plugin-specific config if available
                plugin_config = {}
                if config and plugin.get_name() in config:
                    plugin_config = config[plugin.get_name()]
                
                # Apply settings to plugin
                if hasattr(plugin, 'apply_settings'):
                    plugin.apply_settings(plugin_config)
                elif hasattr(plugin, 'validate_settings') and plugin.validate_settings(plugin_config):
                    # Fallback for backward compatibility
                    logger.warning(f"Plugin {plugin.get_name()} should implement apply_settings()")
                
                logger.info(f"Loaded plugin: {plugin.get_name()}")
                
            except PluginError as e:
                logger.error(f"Failed to load plugin {plugin_dir.name}: {e}")
```

### 2. Comprehensive Telegram Hardcoding Analysis

After extensive search through the codebase, I found **multiple layers of Telegram hardcoding** that need to be addressed:

#### **A. Import Statements (Lines 15-16)**
```python
from plugins.telegram.telegram_plugin import TelegramPlugin
from plugins.telegram.handlers import MessageHandler
```
**Action:** Remove these imports

#### **B. Application Initialization (Lines 52-53)**
```python
self.telegram = TelegramPlugin()
self.message_handler = MessageHandler(telegram_plugin=self.telegram)
```
**Action:** Remove these lines

#### **C. Manual Plugin Registration (Lines 62-68)**
```python
# Load the telegram plugin
self.plugin_manager._plugins[self.telegram.get_name()] = self.telegram
platform = self.telegram.get_platform()
if platform:
    handler = self.telegram.get_message_handler()
    if handler:
        self.plugin_manager._platform_handlers[platform] = handler
        logger.info(f"Registered message handler for platform: {platform}")
```
**Action:** Remove this entire block

#### **D. Message Processing (Lines 154-155)**
```python
if self.telegram.client:
    await self.telegram.client.send_message(user_id, response)
```
**Action:** Replace with generic plugin message handling

#### **E. Plugin Startup (Line 176)**
```python
await self.telegram.start()
```
**Action:** Remove this line

#### **F. Message Handler Registration (Lines 194-196)**
```python
self.telegram.add_message_handler(
    self._handle_message,
    events.NewMessage(incoming=True)
)
```
**Action:** Remove this block

#### **G. Application Main Loop (Line 205)**
```python
await self.telegram.client.run_until_disconnected()
```
**Action:** Replace with generic application main loop

#### **H. Error Handling (Lines 219, 226)**
```python
await self.telegram.client.disconnect()
```
**Action:** Remove these lines

#### **I. Application Shutdown (Lines 243-245)**
```python
if self.telegram:
    logger.info("🛑 Stopping Telegram client...")
    await self.telegram.stop()
```
**Action:** Remove this block

### 3. Replace Telegram-Specific Message Handling

**Current (Lines 128-132):**
```python
async def _handle_message(self, event: events.NewMessage.Event) -> None:
    """Handle incoming Telegram messages.
    
    Args:
        event: The Telegram message event
    """
    await self.message_handler.handle_private_message(event)
```

**Replace with generic message handling:**
```python
async def _handle_message(self, event) -> None:
    """Handle incoming messages from any platform.
    
    Args:
        event: The message event from any platform
    """
    # Let the plugin manager route to appropriate handler
    platform = getattr(event, 'platform', 'unknown')
    handler = self.plugin_manager.get_platform_handler(platform)
    if handler:
        await handler(event)
    else:
        logger.warning(f"No handler found for platform: {platform}")
```

### 4. Replace Telegram-Specific Main Loop

**Current (Line 205):**
```python
await self.telegram.client.run_until_disconnected()
```

**Replace with generic application loop:**
```python
# Keep application running until interrupted
try:
    while True:
        await asyncio.sleep(1)
except KeyboardInterrupt:
    logger.info("Shutdown requested")
```

### 5. Update Queue Processor Integration

**Current (Lines 46-63 in runtime/core/queue.py):**
```python
def __init__(self, message_processor: Callable, plugin_manager: PluginManager,
             telegram_client: Optional[Any] = None,
             # ... other parameters
             ):
    # ...
    self.telegram_client = telegram_client
```

**Action:** Remove `telegram_client` parameter and related logic

### 6. Update Message Formatting

**Current (Lines 49-86 in runtime/core/message.py):**
```python
# Format: [Username: @username, Telegram ID: id] message
# Our format is: [Telegram ID: X, Username: @Y] [TIMESTAMP] MESSAGE
```

**Action:** Make message formatting platform-agnostic

**SIMPLE FIX:** The core `MessageFormatter` class in `runtime/core/message.py` has **hardcoded "Telegram ID" labels**, but the logic is already platform-agnostic:

- **Line 49**: Comment: "platform-specific user ID (Telegram ID)"
- **Line 57**: Comment: "Format: [Username: @username, Telegram ID: id] message"  
- **Line 65**: Code: `user_parts.append(f"Telegram ID: {platform_user_id}")` ← **This is the only actual code change needed**
- **Line 67**: Comment: "Ensure exact format: [Username: @username, Telegram ID: id]"
- **Line 86**: Comment: "Our format is: [Telegram ID: X, Username: @Y] [TIMESTAMP] MESSAGE"

**The logic is already platform-agnostic** - it just has a hardcoded label. This requires:

1. **Change "Telegram ID" to "Platform ID" or "User ID"** in the actual code (Line 65)
2. **Update comments** to be platform-agnostic
3. **No major refactoring needed** - the system already works generically

### 7. Remove Telegram-Specific Dependencies

**Files to update:**
- `broca2/runtime/core/queue.py` - Remove telegram_client parameter
- `broca2/runtime/core/message.py` - Make formatting platform-agnostic
- `broca2/plugins/telegram/handlers.py` - Keep as plugin-specific code

### 8. Update Application Flow

**New Application Flow:**
1. Initialize core components (agent, plugin manager, queue processor)
2. Load application configuration
3. Discover and load all plugins with their settings
4. Start plugin manager (which starts all plugins)
5. Run generic application loop
6. Handle shutdown through plugin manager

**Benefits:**
- Platform-agnostic message handling
- Centralized plugin lifecycle management
- Dynamic settings injection
- Easy addition of new platforms
- Consistent error handling across all plugins
- Configuration-driven plugin management

### 9. Integration with Existing Systems

**Current Systems We Can Leverage:**

#### **A. Settings Hot-Reloading (Already Implemented)**
```python
# main.py already has _check_settings() method
async def _check_settings(self):
    # Monitors settings.json for changes
    # Updates message_mode, debug_mode, queue_refresh, max_retries
    # We can extend this for plugin settings
```

#### **B. Configuration Management (Already Implemented)**
```python
# common/config.py provides:
- get_settings(settings_file: str = "settings.json") -> dict
- save_settings(settings: dict, settings_file: str = "settings.json") -> None
- validate_settings(settings: dict) -> None
```

#### **C. Platform Handler Routing (Already Implemented)**
```python
# runtime/core/queue.py already uses:
handler = self.plugin_manager.get_platform_handler(profile.platform)
```

**Integration Strategy:**
1. **Extend existing `settings.json`** to include plugin configurations
2. **Extend `_check_settings()`** to reload plugin settings
3. **Leverage existing `get_platform_handler()`** for message routing
4. **Use existing configuration functions** for plugin settings management

### 9. Plugin Settings Management

**Current State:**
- `get_settings()` and `validate_settings()` are optional in the interface
- Settings handling is ambiguous and inconsistent
- Plugins may rely on constructor arguments for config

**Required Changes:**

#### **A. Standardize Settings Interface**
```python
# Make these strongly recommended (if not mandatory)
def get_settings(self) -> Dict[str, Any]:
    """Return plugin settings schema and defaults."""
    return {
        "api_key": "required",
        "debug": False,
        "polling_interval": 30
    }

def apply_settings(self, settings: Dict[str, Any]) -> None:
    """Apply settings to plugin instance."""
    self.api_key = settings.get("api_key")
    self.debug = settings.get("debug", False)
    self.polling_interval = settings.get("polling_interval", 30)
```

#### **B. Plugin Discovery Process**
1. **Instantiate plugin** (no constructor arguments for config)
2. **Get settings schema** via `get_settings()`
3. **Load plugin config** from central configuration
4. **Apply settings** via `apply_settings()`
5. **Start plugin** via `start()`

#### **C. Configuration Structure**
```json
{
  "debug_mode": false,
  "queue_refresh": 5,
  "max_retries": 3,
  "message_mode": "live",
  "plugins": {
    "telegram": {
      "api_key": "your_telegram_token",
      "debug": false,
      "polling_interval": 30
    },
    "web_chat": {
      "api_url": "https://your-api.com",
      "api_key": "your_api_key",
      "poll_interval": 5
    },
    "fake_plugin": {
      "enabled": true,
      "message": "Hello from fake plugin!"
    }
  }
}
```

#### **D. Backward Compatibility**
- Existing plugins without `apply_settings()` will work with warnings
- Fallback to `validate_settings()` for legacy plugins
- Gradual migration path for existing plugins

## Implementation Strategy

### Phase 1: Enhanced Plugin Discovery
1. Add `discover_plugins()` method to `PluginManager` with settings support
2. Create configuration loading system
3. Test with fake plugin to verify discovery and settings work

### Phase 2: Update main.py
1. Remove hardcoded Telegram plugin loading
2. Add auto-discovery call with config
3. Remove manual plugin instantiation
4. Add configuration loading

### Phase 3: Plugin Settings Standardization
1. Update existing plugins to use `apply_settings()` pattern
2. Create configuration templates for each plugin
3. Add settings validation and error handling

### Phase 4: Test and Refine
1. Test with existing plugins
2. Add error handling for plugin loading failures
3. Add logging for discovery process
4. Test configuration hot-reloading (optional)

## Expected Behavior After Changes

### Startup Logs:
```
[INFO] 🚀 Starting application...
[INFO] 📋 Loading configuration...
[INFO] 🔄 Discovering plugins...
[INFO] Loaded plugin: telegram (with settings)
[INFO] Loaded plugin: fake_plugin (with settings)
[INFO] 🔄 Starting plugin manager...
[INFO] Started plugin: telegram
[INFO] 🎭 Fake plugin started successfully
[INFO] ✅ Application started successfully!
```

### Plugin Discovery Process:
1. Load application configuration
2. Scan `broca2/plugins/` directory
3. Find subdirectories (excluding `__pycache__`)
4. Look for `plugin.py` files
5. Load each plugin using `PluginManager.load_plugin()`
6. Get plugin settings schema via `get_settings()`
7. Apply plugin-specific configuration via `apply_settings()`
8. Start all loaded plugins using `PluginManager.start()`

### Configuration-Driven Plugin Management:
- Plugins are enabled/disabled via configuration
- Settings are injected dynamically
- No code changes required to add new plugins
- Centralized configuration management

## Benefits of Auto-Discovery with Dynamic Settings

1. **Simplified Plugin Development**: Just drop a plugin in the directory
2. **No Code Changes**: Adding new plugins doesn't require main.py changes
3. **Configuration-Driven**: Enable/disable plugins via config files
4. **Dynamic Settings**: Inject settings at runtime without code changes
5. **Consistent Loading**: All plugins use the same loading mechanism
6. **Better Error Handling**: Centralized plugin loading with proper error handling
7. **Future-Proof**: Easy to add plugin configuration/enable-disable later
8. **Hot-Reloading**: Optional support for runtime configuration changes

## Risk Assessment

### Low Risk:
- PluginManager already has proper error handling
- Plugin interface is well-defined
- Existing plugins follow the interface

### Medium Risk:
- Removing hardcoded Telegram loading might break existing functionality
- Need to ensure all plugins implement the interface correctly

### Mitigation:
- Test thoroughly with existing plugins
- Add comprehensive error handling
- Maintain backward compatibility during transition

## Conclusion

The auto-discovery mechanism is straightforward to implement. The main changes are:

1. **Add `discover_plugins()` method** to PluginManager
2. **Remove hardcoded plugin loading** from main.py
3. **Add auto-discovery call** during startup

This will enable Broca2 to automatically discover and load any plugin that follows the established interface, making the system much more flexible and maintainable. 