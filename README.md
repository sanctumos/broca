

# Sanctum: Broca 3 (v3.0.0)

A CLI-first, plugin-based message processing system for agent communication.

## 📄 License

This project uses dual licensing:
- **Source Code**: [GNU Affero General Public License v3.0](LICENSE) (AGPLv3)
- **Documentation & Data**: [Creative Commons Attribution-ShareAlike 4.0 International](LICENSE-DOCS) (CC-BY-SA 4.0)

For complete license details, see the respective LICENSE files or read our comprehensive [Licensing Guide](LICENSING.md).

## 🚀 Overview

Sanctum: Broca 3 is the production release of Broca, focusing on:
- CLI-first architecture for better control and automation
- Plugin-based system for extensible message handling
- Clean separation between core and platform-specific code
- Improved maintainability and testing capabilities

## Broca: The Middleware Bridge

Sanctum: Broca 3 serves as middleware designed to bridge the Letta Agentic Framework with various communication endpoints. Just as Broca's area in the human brain is responsible for language production and speech, Sanctum: Broca 3 acts as the "speech center" for AI systems—translating agent intentions into actionable messages across different platforms.

In the AI brain, Sanctum: Broca 3 plays a crucial role by:
- **Translating Agent Intentions:** Converting high-level agent decisions into platform-specific messages.
- **Unifying Communication:** Providing a standardized interface for different endpoints (Telegram, CLI, APIs, etc.).
- **Enabling Extensibility:** Allowing new endpoints to be integrated seamlessly through the plugin system.

This middleware approach ensures that the Letta Agentic Framework can focus on decision-making and intelligence, while Sanctum: Broca 3 handles the complexities of communication and integration.

## 🏗️ Architecture

```
broca2/
├── main.py              # Core runtime entry point
├── runtime/             # Core system components
│   ├── core/           # Core functionality
│   │   ├── agent.py    # Agent API interaction
│   │   ├── queue.py    # Message queue processing
│   │   ├── plugin.py   # Plugin management
│   │   └── message.py  # Message handling
├── cli/                 # CLI tools
│   ├── queue.py        # Queue management
│   ├── users.py        # User management
│   ├── conversations.py # Conversation tools
│   └── settings.py     # Settings management
├── plugins/            # Platform plugins
│   ├── telegram/      # Telegram plugin
│   └── cli/           # CLI plugin
└── common/            # Shared utilities
    ├── config.py      # Configuration
    └── logging.py     # Logging setup
```

## 🔧 Core Components

### Runtime
- **Application**: Main coordinator
- **QueueProcessor**: Message queue handling
- **AgentClient**: Agent API interaction
- **PluginManager**: Plugin lifecycle management

### CLI Tools
- **Queue Management**: List, flush, delete messages
- **User Management**: List and manage users
- **Conversation Tools**: View and manage conversations
- **Settings**: Configure system behavior

### Plugins
- **Telegram Plugin**: Telegram message handling
- **CLI Plugin**: Diagnostic/testing interface

## 🎯 Features

### Message Processing
- Multiple processing modes:
  - Echo: Direct message return
  - Listen: Store without processing
  - Live: Process through agent
- Core block management
- Error handling and recovery

### Plugin System
- Standardized plugin interface
- Platform-specific message handling
- Event routing
- Settings management per plugin

### CLI Interface
- Comprehensive admin tools
- Diagnostic capabilities
- Settings management
- Queue operations

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sanctumos/broca.git
   cd broca
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## 🚦 Usage

### Running the Server
```bash
python main.py
```

### CLI Tools
```bash
# Queue management
python -m cli.btool queue list
python -m cli.btool queue flush

# User management
python -m cli.btool users list

# Settings
broca-admin settings set message_mode live
```

### Plugins
- Telegram plugin runs as part of the server
- CLI plugin is a standalone diagnostic tool

## 📝 Configuration

### Settings
- Message processing mode
- Queue refresh interval
- Debug mode
- Plugin-specific settings

### Environment Variables
- Agent API credentials
- Database configuration
- Plugin-specific settings

## 🔌 Plugin Development

### Plugin Structure
```python
from plugins import Plugin

class MyPlugin(Plugin):
    def get_name(self) -> str:
        return "my_plugin"

    def get_platform(self) -> str:
        return "my_platform"

    def get_message_handler(self) -> Callable:
        return self._handle_message

    async def start(self) -> None:
        # Initialize plugin

    async def stop(self) -> None:
        # Cleanup plugin
```

### Required Methods
- `get_name()`: Plugin identifier
- `get_platform()`: Platform name
- `get_message_handler()`: Message handler
- `start()`: Plugin initialization
- `stop()`: Plugin cleanup

## 🧪 Testing

### Core Functionality
- Message processing modes
- Queue operations
- Core block management
- Error handling

### Plugin Integration
- Plugin lifecycle
- Message routing
- Event handling
- Settings propagation

## 📚 Documentation

### User Documentation
- [Multi-Agent Architecture Guide](https://github.com/sanctumos/broca/blob/main/docs/multi-agent-architecture.md) - Complete guide to running multiple agent instances
- [Plugin Development Guide](https://github.com/sanctumos/broca/blob/main/docs/plugin_development.md)
- [CLI Tools Reference](https://github.com/sanctumos/broca/blob/main/docs/cli_reference.md)
- [Configuration Guide](https://github.com/sanctumos/broca/blob/main/docs/configuration.md)
- [Telegram Plugin](https://github.com/sanctumos/broca/blob/main/docs/telegram-plugin-spec.md)
- [Telegram Bot Plugin](https://github.com/sanctumos/broca/blob/main/docs/telegram-bot-plugin.md)
- [CLI-Test Plugin](https://github.com/sanctumos/broca/blob/main/docs/cli-test-plugin.md)
- [Web Chat Bridge API](https://github.com/sanctumos/broca/blob/main/docs/web-chat-bridge-api-documentation.md)

## 🤖 Agent/MCP-Ready Design

Sanctum: Broca 3 is built so that all CLI tools and plugin interfaces are **MCP'able** (machine-controllable by agents):
- Every CLI and admin tool is scriptable and can be operated by other AI agents or automation systems.
- All commands support machine-friendly output (e.g., JSON) and error handling.
- This enables Sanctum: Broca 3 to be embedded in agent networks, automated test harnesses, or orchestration systems.
- When extending Sanctum: Broca 3, always consider both human and agent/automation use cases.

## 🔮 Planned Updates

### Multi-Agent Architecture
Sanctum: Broca 3 will support multiple Letta agents through a simple, efficient architecture:
- Each agent will run in its own completely isolated Broca instance
- Instances share only the Sanctum-wide virtual environment (not Broca-specific)
- Each agent has its own configuration, database, and plugin instances
- Clear 1:1 mapping between Broca instances and Letta agents

### Broca MCP Server
A new Management Control Panel server will be added to manage multiple Broca instances:
- Instance Management: Deploy, monitor, and update Broca instances
- Agent Configuration: Manage Letta agent credentials and settings
- Monitoring & Logging: Centralized logging and performance metrics
- Resource Management: Monitor shared resources and system health
- Security: Centralized credential management and access control

## 🏠 Multi-Agent Setup

### Folder Structure
For managing multiple Broca instances on the same machine, use the following structure:

```
~/sanctum/                    # Sanctum home directory
├── venv/                     # Sanctum-wide virtual environment (shared by all tools)
├── agent-721679f6-c8af-4e01-8677-dc042dc80368/  # Agent-specific instance
│   ├── broca/                # Complete Broca repository clone for this agent
│   │   ├── main.py
│   │   ├── runtime/
│   │   ├── plugins/
│   │   ├── requirements.txt
│   │   └── ...
│   ├── .env                   # Agent-specific environment
│   ├── settings.json          # Agent-specific settings
│   ├── sanctum.db            # Agent-specific database
│   └── logs/                 # Agent-specific logs
├── agent-9a2b3c4d-5e6f-7890-abcd-ef1234567890/  # Another agent
│   ├── broca/                # Complete Broca repository clone for this agent
│   │   ├── main.py
│   │   ├── runtime/
│   │   ├── plugins/
│   │   ├── requirements.txt
│   │   └── ...
│   ├── .env
│   ├── settings.json
│   ├── sanctum.db
│   └── logs/
└── other-sanctum-tools/      # Other Sanctum tools (shared venv)
    ├── tool1/
    └── tool2/
```

### Setup Instructions

1. **Choose your master folder:**
   ```bash
   # Typically your home directory or a dedicated user folder
   mkdir ~/sanctum
   cd ~/sanctum
   ```

2. **Create agent-specific instances:**
   ```bash
   # For each Letta agent, create a folder named after the agent ID
   mkdir ~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368
   cd ~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368

   # Clone a complete Broca repository for this agent
   git clone https://github.com/sanctumos/broca.git broca

   # Note: Virtual environment is managed at the Sanctum level, not per Broca instance
   # The venv in ~/sanctum/venv/ is shared by all Sanctum tools
   ```

3. **Configure agent-specific instances:**
   ```bash
   # Copy base configuration from the cloned repository
   cp ~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368/broca/.env.example ~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368/.env
   cp ~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368/broca/settings.json ~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368/

   # Edit agent-specific configuration
   nano ~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368/.env
   # Set AGENT_ENDPOINT, AGENT_API_KEY, and other agent-specific settings
   ```

4. **Run agent-specific instances:**
   ```bash
   # From the agent folder
   cd ~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368

   # Activate the Sanctum-wide virtual environment
   source ~/sanctum/venv/bin/activate  # On Windows: ~/sanctum/venv/Scripts/activate

   # Run the instance from the agent's Broca clone
   python broca/main.py

   # Or use the CLI tools
   python -m broca.cli.btool queue list
   ```

### Master Sanctum Provisioning Suite Integration

If you're using the Master Sanctum Provisioning Suite:

1. **Configure the Sanctum home folder** in your provisioning suite's `.env` file
2. **The suite will automatically:**
   - Git-clone Broca 3 into the proper folder structure
   - Create agent-specific folders based on your agent configurations
   - Set up the correct relative paths for all components

### Managing Multiple Instances

#### Starting Instances
```bash
# Start a specific agent's Broca instance
cd ~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368

# Activate the Sanctum-wide virtual environment
source ~/sanctum/venv/bin/activate  # On Windows: ~/sanctum/venv/Scripts/activate

# Run the instance from the agent's Broca clone
python broca/main.py

# Or use a process manager like PM2
pm2 start "broca-agent-1" --interpreter ~/sanctum/venv/bin/python -- ~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368/broca/main.py
pm2 start "broca-agent-2" --interpreter ~/sanctum/venv/bin/python -- ~/sanctum/agent-9a2b3c4d-5e6f-7890-abcd-ef1234567890/broca/main.py
```

#### Configuration Management
```bash
# Each agent has its own configuration
~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368/.env
~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368/settings.json

# Note: No shared configurations - each agent is completely isolated
# If you need similar configs, copy and modify them manually
```

#### Database Management
```bash
# Each agent has its own database
~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368/sanctum.db

# Backup agent-specific databases
cp ~/sanctum/agent-*/sanctum.db ~/sanctum/backups/
```

#### Logging
```bash
# Each agent has its own logs
~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368/logs/

# Note: No centralized logging - each agent maintains its own log files
# For centralized monitoring, use external log aggregation tools
```

### Benefits of This Structure

- **Complete Isolation**: Each agent runs independently with its own complete Broca repository, configuration, database, and plugin instances
- **Scalability**: Easy to add new agents without affecting existing ones
- **Maintenance**: Each agent can be updated independently by pulling from their own Broca repository
- **Backup**: Simple to backup individual agent configurations and data
- **Resource Efficiency**: Only the virtual environment is shared (Sanctum-wide, not Broca-specific)
- **Flexibility**: Each agent can have different plugins, settings, and configurations
- **Security**: No cross-agent data leakage or configuration conflicts
- **Version Control**: Each agent can run different versions of Broca if needed

## 🤖 Acknowledgments

- Original Broca project (It was me).
- Contributors and maintainers (Also me).
- Community support  (the AI agents I made to help me).
