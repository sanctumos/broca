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
   1) [ ] Create abstract Plugin base class in plugins/__init__.py:
      - Required methods: start(), stop(), get_name()
      - Optional methods: get_settings(), validate_settings()
      - Event handling interface for message processing
   
   2) [ ] Create MessageHandler base class in runtime/core/message.py:
      - Abstract methods for message processing
      - Common message formatting and sanitization
      - Platform-agnostic message buffer functionality
   
   3) [ ] Create PluginManager in runtime/core/plugin.py:
      - Plugin registration and lifecycle management
      - Event routing between plugins and core
      - Settings management per plugin

B. Telegram Plugin Refactoring
   1) [ ] Update TelegramBot to inherit from Plugin base class:
      - Move Telegram-specific settings to plugin config
      - Implement required Plugin interface methods
      - Remove direct environment variable access
   
   2) [ ] Refactor MessageHandler to use base class:
      - Move Telegram-specific formatting to plugin
      - Use common message buffer implementation
      - Implement platform-specific user handling
   
   3) [ ] Create Telegram-specific settings:
      - Move API credentials to plugin config
      - Add session management settings
      - Define message handling modes

C. CLI Conversation Plugin
   1) [ ] Create CLI plugin structure:
      - Implement Plugin base class
      - Add command-line interface for conversation
      - Support message modes (echo, listen, live)
   
   2) [ ] Implement CLI message handling:
      - Use common MessageHandler base
      - Add CLI-specific formatting
      - Support interactive conversation
   
   3) [ ] Add CLI-specific features:
      - Command history
      - Message threading
      - User switching

D. Common Infrastructure
   1) [ ] Update core to support multiple plugins:
      - Modify main.py to use PluginManager
      - Add plugin configuration loading
      - Support concurrent plugin operation
   
   2) [ ] Create plugin settings schema:
      - Define required vs optional settings
      - Add validation rules
      - Support plugin-specific settings
   
   3) [ ] Implement plugin event system:
      - Define core events (message, status, error)
      - Add plugin event registration
      - Support event filtering

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