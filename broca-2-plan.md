1) [x] create a broca2/ folder
2) [ ] copy all async loop functionality from broca 1 to broca 2
   a) [x] Core Components to Migrate:
      - [x] Application class (main.py) - Core coordinator
      - [x] QueueProcessor (core/queue.py) - Message queue handling
      - [x] AgentClient (core/agent.py) - Agent API interaction
      - [x] MessageFormatter (core/message.py) - Message formatting
      - [x] LettaClient (core/letta_client.py) - Letta API client
   
   b) [x] Database Dependencies:
      - [x] Message operations (get_message_text, update_message_with_response)
      - [x] User operations (get_user_details, get_platform_profile_id, get_letta_user_block_id)
      - [x] Queue operations (update_queue_status, get_pending_queue_item)
   
   c) [ ] Configuration and Logging:
      - [x] Common config setup (common/config.py)
      - [x] Logging setup with emoji support (common/logging.py)
   
   d) [x] Message Processing Modes:
      - [x] Echo mode (direct message return)
      - [x] Listen mode (store without processing)
      - [x] Live mode (process through agent)
   
   e) [x] Core Block Management:
      - [x] Attach/detach core blocks for users
      - [x] Handle core block errors and cleanup
   
   f) [x] Error Handling:
      - [x] Graceful shutdown on KeyboardInterrupt
      - [x] Error recovery in queue processing
      - [x] Core block cleanup on errors
   
   g) [x] Testing Requirements:
      - [x] Test all message modes
      - [x] Test core block attachment/detachment
      - [x] Test error recovery
      - [x] Test queue processing
      - [x] Test agent communication
3) [x] make sure it's working as standalone
4) [x] recreate everything that was previously controlled by the "settings" page in the dash to a CLI.
5) [x] recreate the queue tools as CLI (list queue, flush message, delete message, flush all, delete all)
6) [x] recreate the users tools as CLI (perviously was just list users. we'll add more features later)
7) [x] recreate the conversations tools as CLI (previously was just list conversations. we'll add more features later)

Plugins:
1) [x] create plugins/ folder
2) [ ] Plugin: create simple cli tool for adding messages to the queue
3) [x] Plugin: bring broca/telegram/ into the plugins folder, refactor to new setup

Plugin Refactoring Plan:

A. Core Plugin Interface (Required for both Telegram and CLI)
   1) [x] Create abstract Plugin base class in plugins/__init__.py:
      - Required methods: start(), stop(), get_name()
      - Optional methods: get_settings(), validate_settings()
      - Event handling interface for message processing
      - DO NOT:
        - Add plugin-specific methods to base class
        - Implement complex event routing logic
        - Create plugin dependency management
   
   2) [x] Create MessageHandler base class in runtime/core/message.py:
      - Abstract methods for message processing
      - Common message formatting and sanitization
      - Platform-agnostic message buffer functionality
      - DO NOT:
        - Add platform-specific formatting
        - Implement complex message threading
        - Create message persistence logic
   
   3) [x] Create PluginManager in runtime/core/plugin.py:
      - Plugin registration and lifecycle management
      - Event routing between plugins and core
      - Settings management per plugin
      - DO NOT:
        - Add plugin dependency resolution
        - Implement complex event filtering
        - Create plugin version management

B. Telegram Plugin Refactoring
   - DO NOT:
     - move CORE functionality into the plugin.
   1) [x] Update TelegramBot to inherit from Plugin base class:
      - Move Telegram-specific settings to plugin config
      - Implement required Plugin interface methods
      - Remove direct environment variable access
      - DO NOT:
        - Add new Telegram features
        - Change existing message handling logic
        - Modify core block functionality
    
   2) [x] Refactor MessageHandler to use base class:
      - Move Telegram-specific formatting to plugin
      - Use common message buffer implementation
      - Implement platform-specific user handling
      - DO NOT:
        - Change message processing flow
        - Add new message types
        - Modify existing error handling
    
   3) [x] Create Telegram-specific settings:
      - Move API credentials to plugin config
      - Add session management settings
      - Define message handling modes
      - DO NOT:
        - Add complex configuration validation
        - Create new setting types
        - Modify core settings structure

   4) [ ] Implement Message Routing Using Existing Schema:
      a) Platform Handler Registration:
         - Add platform handler registry to PluginManager:
           ```python
           class PluginManager:
               def __init__(self):
                   self._platform_handlers: Dict[str, Callable] = {}  # platform -> handler
           
               def register_platform_handler(self, platform: str, handler: Callable) -> None:
                   """Register a handler for a specific platform."""
                   self._platform_handlers[platform] = handler
           ```
         - Update Plugin base class to register platform handlers:
           ```python
           class Plugin(ABC):
               def get_platform(self) -> str:
                   """Get the platform name this plugin handles."""
                   pass
           
               def get_message_handler(self) -> Callable:
                   """Get the message handler for this platform."""
                   pass
           ```
      
      b) Response Routing:
         - Add response routing to QueueProcessor:
           ```python
           async def _process_with_core_block(self, message_id: int) -> None:
               # Process message with agent...
               response = await self.message_processor(message)
               
               # Route response back to platform
               profile = await get_message_platform_profile(message_id)
               if profile and profile.platform in self.plugin_manager._platform_handlers:
                   handler = self.plugin_manager._platform_handlers[profile.platform]
                   await handler(response, profile)
           ```
         - Update message status tracking:
           ```python
           async def update_message_status(
               self,
               message_id: int,
               status: str,
               response: Optional[str] = None
           ) -> None:
               """Update message status and store response."""
               await update_message(
                   message_id=message_id,
                   processed=1,
                   agent_response=response
               )
           ```
      
      c) Platform-Specific Response Handling:
         - Implement platform-specific response formatting in plugins:
           ```python
           class TelegramPlugin(Plugin):
               def get_platform(self) -> str:
                   return "telegram"
           
               def get_message_handler(self) -> Callable:
                   return self._handle_response
           
               async def _handle_response(self, response: str, profile: PlatformProfile) -> None:
                   # Format response for Telegram
                   formatted = self.format_response(response)
                   await self.client.send_message(
                       profile.platform_user_id,
                       formatted
                   )
           ```
      
      d) Error Handling:
         - Add error routing to platform handlers:
           ```python
           async def _handle_response(self, response: str, profile: PlatformProfile) -> None:
               try:
                   formatted = self.format_response(response)
                   await self.client.send_message(
                       profile.platform_user_id,
                       formatted
                   )
               except Exception as e:
                   logger.error(f"Failed to send response to {profile.platform_user_id}: {e}")
                   # Update message status to failed
                   await update_message_status(
                       message_id=message_id,
                       status="failed",
                       response=str(e)
                   )
           ```
      
      DO NOT:
      - Add new database tables or columns
      - Implement complex message threading
      - Create plugin-to-plugin communication
      - Modify existing database schema

C. CLI Conversation Plugin
   1) [ ] Create CLI plugin structure:
      - Implement Plugin base class
      - Add command-line interface for conversation
      - Support message modes (echo, listen, live)
      - DO NOT:
        - Add complex CLI features
        - Implement advanced terminal UI
        - Create new message types
   
   2) [ ] Implement CLI message handling:
      - Use common MessageHandler base
      - Add CLI-specific formatting
      - Support interactive conversation
      - DO NOT:
        - Add complex input validation
        - Implement command aliases
        - Create new message formats
   
   3) [ ] Add CLI-specific features:
      - Command history
      - Message threading
      - User switching
      - DO NOT:
        - Add complex command parsing
        - Implement advanced history features
        - Create new user management features

D. Common Infrastructure
   1) [ ] Update core to support multiple plugins:
      - Modify main.py to use PluginManager
      - Add plugin configuration loading
      - Support concurrent plugin operation
      - DO NOT:
        - Add plugin dependency management
        - Implement complex startup sequences
        - Create new core features
   
   2) [ ] Create plugin settings schema:
      - Define required vs optional settings
      - Add validation rules
      - Support plugin-specific settings
      - DO NOT:
        - Add complex validation logic
        - Create new setting types
        - Modify core settings structure
   
   3) [ ] Implement plugin event system:
      - Define core events (message, status, error)
      - Add plugin event registration
      - Support event filtering
      - DO NOT:
        - Add complex event routing
        - Implement event persistence
        - Create new event types

Implementation Order:
1. Core Plugin Interface (A.1-3)
2. Telegram Plugin Refactoring (B.1-3)
3. Common Infrastructure (D.1-3)
4. CLI Conversation Plugin (C.1-3)

This refactoring will:
- Create a clean separation between core and plugins
- Enable easy addition of new plugins
- Provide consistent behavior across plugins
- Make the system more maintainable and testable

Scope Boundaries:
1. DO NOT modify:
   - Core block functionality
   - Database operations
   - Message processing logic
   - Queue management
   - Agent communication
   - Error handling patterns

2. DO NOT add:
   - New message types
   - Complex UI features
   - Advanced configuration
   - Plugin dependencies
   - New core features
   - Complex event routing

3. DO NOT change:
   - Existing message flow
   - Core settings structure
   - Error handling patterns
   - Database schema
   - Queue processing
   - Agent interaction

Focus Areas:
1. Plugin interface standardization
2. Message handling abstraction
3. Settings management
4. Event system basics
5. CLI conversation basics
6. Telegram plugin cleanup

---

**LET'S GOOOO 🚀**

Here's your `broca2/` skeleton—clean, CLI-first, plugin-ready, runtime-modular.

---

## 🧱 Directory Structure

```
broca2/
├── main.py - used to call core loop
├── runtime/
│   └── all the core files here.
├── cli/
│   ├── __init__.py
│   ├── queue.py
│   ├── users.py
│   ├── conversations.py
│   └── settings.py
├── plugins/
│   ├── __init__.py
│   ├── cli_test/
│   │   └── plugin.py
│   └── telegram/
│       └── plugin.py  # placeholder for refactor
└── common/
    ├── config.py
    ├── logging.py
    └── __init__.py
```

---

## 🧠 Core Concepts

- `main.py` = boot entrypoint for the runtime loop
- `runtime/loop.py` = async system manager (polls queue, dispatches)
- `cli/broca_admin.py` = argparse dispatcher
- `cli/*.py` = command groups (flush queue, list users, etc)
- `plugins/` = isolated input surfaces
- `common/` = shared config + logging

---

## ✨ Sample Files

### `main.py`
```python
import asyncio
from runtime.loop import run_runtime

if __name__ == "__main__":
    asyncio.run(run_runtime())
```

---

### `runtime/loop.py`
```python
import asyncio

async def run_runtime():
    print("🔁 Broca 2 Runtime Starting...")
    # TODO: Load plugins, start polling loop, initialize queue processor
    await asyncio.sleep(1)
```

---

### `cli/broca_admin.py`
```python
import argparse
from cli import queue, users, conversations, settings

def main():
    parser = argparse.ArgumentParser(description="Broca Admin CLI")
    subparsers = parser.add_subparsers(dest="command")

    queue.register(subparsers)
    users.register(subparsers)
    conversations.register(subparsers)
    settings.register(subparsers)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

---

### `cli/queue.py` (starter)
```python
def register(subparsers):
    q = subparsers.add_parser("flush-queue", help="Flush the entire message queue")
    q.set_defaults(func=flush_queue)

def flush_queue(args):
    print("🧹 Flushing the message queue...")
    # TODO: Connect to DB and delete all queue entries
```

---

### `plugins/cli_test/plugin.py`
```python
import asyncio

async def send_test_message(user_id, message):
    print(f"📥 [CLI Plugin] Queuing message for user {user_id}: {message}")
    # TODO: Insert message into DB and add to queue
```

## 📋 Project Context

### Why We're Refactoring
- Moving from web-based to CLI-first architecture
- Improving plugin system for better extensibility
- Reducing complexity in core components
- Making the system more maintainable

### Current Pain Points
1. Web interface tightly coupled with core functionality
2. Plugin system lacks standardization
3. Settings management scattered across components
4. Message handling varies by platform
5. Core functionality mixed with platform-specific code

### Technical Context
- Python 3.8+ required
- AsyncIO-based event loop
- SQLite database with existing schema
- Current async loop handles:
  - Queue polling
  - Message processing
  - Agent communication
  - Core block management

## 🧪 Testing Strategy

### Verification Steps
1. Core Functionality:
   - [ ] Async loop maintains existing behavior
   - [ ] Queue processing works as before
   - [ ] Message modes (echo, listen, live) function correctly
   - [ ] Core block management unchanged

2. Plugin System:
   - [ ] Telegram plugin works with new interface
   - [ ] CLI plugin handles messages correctly
   - [ ] Settings propagate to plugins
   - [ ] Events route properly

3. Database Operations:
   - [ ] All existing queries work
   - [ ] Data integrity maintained
   - [ ] Transaction handling unchanged

### Regression Testing
1. Automated Tests:
   - [ ] Unit tests for new plugin interface
   - [ ] Integration tests for message flow
   - [ ] End-to-end tests for core scenarios

2. Manual Verification:
   - [ ] Telegram message processing
   - [ ] CLI conversation handling
   - [ ] Settings management
   - [ ] Error recovery

## 🚦 Migration Path

### Phase 1: Preparation
1. [ ] Backup current database
2. [ ] Document current behavior
3. [ ] Create test scenarios
4. [ ] Set up monitoring

### Phase 2: Implementation
1. [ ] Implement core plugin interface
2. [ ] Refactor Telegram plugin
3. [ ] Add CLI plugin
4. [ ] Update settings management

### Phase 3: Verification
1. [ ] Run test suite
2. [ ] Verify core functionality
3. [ ] Test plugin integration
4. [ ] Validate settings

### Phase 4: Deployment
1. [ ] Deploy to staging
2. [ ] Monitor for issues
3. [ ] Roll out to production
4. [ ] Verify data integrity

### Rollback Plan
1. [ ] Keep old code in separate branch
2. [ ] Document rollback steps
3. [ ] Prepare database restore
4. [ ] Test rollback procedure

## 🚨 Risk Mitigation

### High-Risk Areas
1. Database Operations:
   - Keep existing queries unchanged
   - Verify all operations work
   - Test transaction handling

2. Message Processing:
   - Maintain existing flow
   - Verify all modes work
   - Test error handling

3. Plugin Integration:
   - Test each plugin independently
   - Verify event handling
   - Check settings propagation

### Monitoring
1. [ ] Set up logging for new components
2. [ ] Add performance metrics
3. [ ] Monitor error rates
4. [ ] Track plugin health