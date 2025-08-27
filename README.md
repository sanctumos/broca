

# Sanctum: Broca 2 (v0.10.0)

A CLI-first, plugin-based message processing system for agent communication.

## 🚀 Overview

Sanctum: Broca 2 is a refactored version of Broca, focusing on:
- CLI-first architecture for better control and automation
- Plugin-based system for extensible message handling
- Clean separation between core and platform-specific code
- Improved maintainability and testing capabilities

## Broca: The Middleware Bridge

Sanctum: Broca 2 serves as middleware designed to bridge the Letta Agentic Framework with various communication endpoints. Just as Broca's area in the human brain is responsible for language production and speech, Sanctum: Broca 2 acts as the "speech center" for AI systems—translating agent intentions into actionable messages across different platforms.

In the AI brain, Sanctum: Broca 2 plays a crucial role by:
- **Translating Agent Intentions:** Converting high-level agent decisions into platform-specific messages.
- **Unifying Communication:** Providing a standardized interface for different endpoints (Telegram, CLI, APIs, etc.).
- **Enabling Extensibility:** Allowing new endpoints to be integrated seamlessly through the plugin system.

This middleware approach ensures that the Letta Agentic Framework can focus on decision-making and intelligence, while Sanctum: Broca 2 handles the complexities of communication and integration.

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
- [Multi-Agent Architecture Guide](broca2/docs/multi-agent-architecture.md) - Complete guide to running multiple agent instances
- [Plugin Development Guide](broca2/docs/plugin_development.md)
- [CLI Tools Reference](broca2/docs/cli_reference.md)
- [Configuration Guide](broca2/docs/configuration.md)
- [Telegram Plugin](broca2/docs/telegram-plugin-spec.md)
- [Telegram Bot Plugin](broca2/docs/telegram-bot-plugin.md)
- [CLI-Test Plugin](broca2/docs/cli-test-plugin.md)
- [Web Chat Bridge API](broca2/docs/web-chat-bridge-api-documentation.md)
- [Web Chat Bridge Project Plan](broca2/docs/web-chat-bridge-project-plan.md)

### Developer Documentation
For internal development documentation, technical analysis, and project planning, see the [broca2/docs/dev-docs/](broca2/docs/dev-docs/) folder.

## 🤖 Agent/MCP-Ready Design

Sanctum: Broca 2 is built so that all CLI tools and plugin interfaces are **MCP'able** (machine-controllable by agents):
- Every CLI and admin tool is scriptable and can be operated by other AI agents or automation systems.
- All commands support machine-friendly output (e.g., JSON) and error handling.
- This enables Sanctum: Broca 2 to be embedded in agent networks, automated test harnesses, or orchestration systems.
- When extending Sanctum: Broca 2, always consider both human and agent/automation use cases.

## 🔮 Planned Updates

### Multi-Agent Architecture
Sanctum: Broca 2 will support multiple Letta agents through a simple, efficient architecture:
- Each agent will run in its own Broca instance
- Instances will share a common virtual environment to minimize resource usage
- Simple git-based update system that preserves agent-specific configurations
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
~/sanctum/broca2/             # Base Broca 2 installation
├── venv/                     # Shared virtual environment
├── main.py
├── runtime/
├── plugins/
├── requirements.txt
├── agent-721679f6-c8af-4e01-8677-dc042dc80368/  # Agent-specific instance
│   ├── .env                   # Agent-specific environment
│   ├── settings.json          # Agent-specific settings
│   ├── sanctum.db            # Agent-specific database
│   └── logs/                 # Agent-specific logs
├── agent-9a2b3c4d-5e6f-7890-abcd-ef1234567890/  # Another agent
│   ├── .env
│   ├── settings.json
│   ├── sanctum.db
│   └── logs/
└── shared/                   # Shared resources (optional)
    ├── templates/
    └── configs/
```

### Setup Instructions

1. **Choose your master folder:**
   ```bash
   # Typically your home directory or a dedicated user folder
   mkdir ~/sanctum
   cd ~/sanctum
   ```

2. **Clone the base Broca 2 installation:**
   ```bash
   git clone https://github.com/sanctumos/broca.git broca2
   cd broca2
   
   # Create shared virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create agent-specific instances:**
   ```bash
   # For each Letta agent, create a folder named after the agent ID
   mkdir ~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368
   cd ~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368
   
   # Copy base configuration
   cp ~/sanctum/broca2/.env.example .env
   cp ~/sanctum/broca2/settings.json .
   
   # Edit agent-specific configuration
   nano .env
   # Set AGENT_ENDPOINT, AGENT_API_KEY, and other agent-specific settings
   ```

4. **Run agent-specific instances:**
   ```bash
   # From the agent folder
   cd ~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368
   python ../main.py
   
   # Or use the CLI tools
   python -m cli.btool queue list
   ```

### Master Sanctum Provisioning Suite Integration

If you're using the Master Sanctum Provisioning Suite:

1. **Configure the Sanctum home folder** in your provisioning suite's `.env` file
2. **The suite will automatically:**
   - Git-clone Broca 2 into the proper folder structure
   - Create agent-specific folders based on your agent configurations
   - Set up the correct relative paths for all components

### Managing Multiple Instances

#### Starting Instances
```bash
# Start a specific agent's Broca instance
cd ~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368
python ../main.py

# Or use a process manager like PM2
pm2 start "broca-agent-1" --interpreter python -- ../main.py
pm2 start "broca-agent-2" --interpreter python -- ../main.py
```

#### Configuration Management
```bash
# Each agent has its own configuration
~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368/.env
~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368/settings.json

# Shared configurations can be symlinked or copied
ln -s ~/sanctum/broca2/shared/templates/telegram_config.json ~/sanctum/broca2/agent-*/telegram_config.json
```

#### Database Management
```bash
# Each agent has its own database
~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368/sanctum.db

# Backup agent-specific databases
cp ~/sanctum/broca2/agent-*/sanctum.db ~/sanctum/broca2/backups/
```

#### Logging
```bash
# Each agent has its own logs
~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368/logs/

# Centralized logging (optional)
ln -s ~/sanctum/broca2/logs/ ~/sanctum/broca2/agent-*/logs
```

### Benefits of This Structure

- **Isolation**: Each agent runs independently with its own configuration and database
- **Scalability**: Easy to add new agents without affecting existing ones
- **Maintenance**: Update the base Broca 2 installation once, affects all agents
- **Backup**: Simple to backup individual agent configurations and data
- **Resource Efficiency**: Shared base installation reduces disk usage
- **Flexibility**: Each agent can have different plugins, settings, and configurations

## 🤖 Acknowledgments

- Original Broca project (It was me).
- Contributors and maintainers (Also me).
- Community support  (the AI agents I made to help me).