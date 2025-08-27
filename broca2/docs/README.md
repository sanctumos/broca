# ⚠️ REPOSITORY MOVED ⚠️

**This repository has moved to: [http://github.com/sanctumos/broca](http://github.com/sanctumos/broca)**

Please update your git remotes and use the new repository location for all future development and contributions.

---

# Broca 2 Documentation

A message processing system with flexible modes and comprehensive status tracking, now part of the Sanctum constellation with multi-agent support.

## 🏗️ Architecture Overview

Broca 2 is now part of the larger Sanctum constellation, supporting multiple agent instances with a shared base installation:

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

## 🚀 Features

### Message Processing Modes

The system supports three distinct message processing modes:

1. **Live Mode**
   - Full message processing through the agent
   - Core block attachment for context management
   - Complete response handling and delivery

2. **Echo Mode**
   - Simple message echo without agent processing
   - Maintains message history without agent interaction
   - Useful for testing and debugging

3. **Listen Mode**
   - Stores messages without processing
   - No agent interaction or responses
   - Useful for collecting training data

### Multi-Agent Support

- **Instance Isolation**: Each agent runs in its own instance with separate configuration
- **Shared Resources**: Base installation and virtual environment shared across instances
- **Independent Databases**: Each agent maintains its own message history and user data
- **Flexible Configuration**: Per-agent environment variables and settings

### Status System

Messages and queue items follow a comprehensive status system:

1. **Core States**
   - RECEIVED: Initial message state
   - QUEUED: Added to processing queue
   - PROCESSING: Currently being handled
   - COMPLETED/FAILED: Final processing states
   - STORED/ECHOED: Mode-specific completion states
   - ARCHIVED: Terminal state for completed items

2. **Status Categories**
   - ACTIVE: Items currently in the system
   - COMPLETED: Successfully processed items
   - PROBLEMATIC: Failed or cancelled items
   - INACTIVE: Archived items

## 🔧 Environment Variables

### Base Installation Variables
Required variables for the base installation:
- `TELEGRAM_API_ID`: Your Telegram API ID
- `TELEGRAM_API_HASH`: Your Telegram API hash
- `TELEGRAM_PHONE`: Phone number for the Telegram client

### Agent-Specific Variables
Each agent instance requires its own `.env` file with:
- `LETTA_API_ENDPOINT`: Endpoint URL for the specific Letta agent
- `LETTA_API_KEY`: API key for the specific Letta agent
- `AGENT_ID`: Unique identifier for the agent instance
- `DEBUG_MODE`: Enable/disable debug mode (default: false)

### Optional Variables
- `QUEUE_REFRESH`: Queue refresh interval in seconds (default: 5)
- `MAX_RETRIES`: Maximum retry attempts for failed messages (default: 3)
- `MESSAGE_MODE`: Processing mode (live/echo/listen, default: live)

## 🛠️ Development Setup

### Multi-Agent Setup

1. **Create Sanctum directory structure:**
   ```bash
   mkdir ~/sanctum
   cd ~/sanctum
   ```

2. **Clone base Broca 2 installation:**
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
   mkdir agent-721679f6-c8af-4e01-8677-dc042dc80368
   cd agent-721679f6-c8af-4e01-8677-dc042dc80368
   
   # Copy base configuration
   cp ../.env.example .env
   cp ../settings.json .
   
   # Edit agent-specific configuration
   nano .env
   # Set AGENT_ENDPOINT, AGENT_API_KEY, and other agent-specific settings
   ```

4. **Run agent-specific instances:**
   ```bash
   # From the agent folder
   cd agent-721679f6-c8af-4e01-8677-dc042dc80368
   python ../main.py
   ```

### Single Instance Setup (Legacy)

For single-instance development:
1. Clone the repository
2. Copy `.env.example` to `.env` and fill in required values
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `python main.py`

## 📁 Project Structure

### Base Installation
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
│   ├── btool.py        # Main CLI interface
│   ├── ctool.py        # Configuration tools
│   ├── qtool.py        # Queue management
│   ├── utool.py        # User management
│   └── settings.py     # Settings management
├── plugins/            # Platform plugins
│   ├── telegram/      # Telegram plugin
│   ├── telegram_bot/  # Telegram bot plugin
│   └── cli_test/      # CLI testing plugin
├── common/            # Shared utilities
│   ├── config.py      # Configuration
│   ├── exceptions.py  # Custom exceptions
│   └── logging.py     # Logging setup
└── database/          # Database models and operations
    ├── models.py      # Database models
    └── operations/    # Database operations
```

### Agent Instance Structure
```
agent-{uuid}/
├── .env                # Agent-specific environment
├── settings.json       # Agent-specific settings
├── sanctum.db         # Agent-specific database
└── logs/              # Agent-specific logs
```

## 🔌 Plugin System

Broca 2 supports a plugin-based architecture for extensible message handling:

- **Telegram Plugin**: Full Telegram message handling with markdown support
- **Telegram Bot Plugin**: Standalone Telegram bot implementation
- **CLI Test Plugin**: Diagnostic and testing interface
- **Custom Plugins**: Easy to create new platform integrations

## 📊 Monitoring & Management

### CLI Tools
- **Queue Management**: List, flush, delete messages
- **User Management**: List and manage users
- **Configuration**: Manage agent-specific settings
- **Diagnostics**: System health and performance monitoring

### Logging
- **Per-Agent Logs**: Each agent maintains its own log files
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Log Rotation**: Automatic log management and cleanup

## 🔮 Recent Improvements

1. **Multi-Agent Architecture**
   - Support for multiple agent instances
   - Shared base installation with instance isolation
   - Per-agent configuration and database management

2. **Core Block Management**
   - Proper attachment/detachment cycle
   - Reliable block ID storage
   - Error handling and cleanup

3. **Message Formatting**
   - Standardized format across components
   - Emoji-based logging system
   - Improved metadata handling
   - Telegram markdown support

4. **Client Architecture**
   - Singleton Letta client implementation
   - Standardized environment variables
   - Improved configuration management

5. **Status Tracking**
   - Comprehensive status system
   - Mode-specific status workflows
   - Status history and monitoring

## 📚 Additional Documentation

### User Documentation
- [Plugin Development Guide](plugin_development.md)
- [CLI Tools Reference](cli_reference.md)
- [Configuration Guide](configuration.md)
- [Telegram Plugin](telegram-plugin-spec.md)
- [Telegram Bot Plugin](telegram-bot-plugin.md)
- [CLI-Test Plugin](cli-test-plugin.md)
- [Telegram Markdown Guide](telegram-markdown-guide.md)
- [Multi-Agent Architecture Guide](multi-agent-architecture.md)
- [Web Chat Bridge API](web-chat-bridge-api-documentation.md)
- [Web Chat Bridge Project Plan](web-chat-bridge-project-plan.md)

### Developer Documentation
For internal development documentation, technical analysis, and project planning, see the [dev-docs/](dev-docs/) folder.

## 🤖 Agent/MCP-Ready Design

Broca 2 is built so that all CLI tools and plugin interfaces are **MCP'able** (machine-controllable by agents):
- Every CLI and admin tool is scriptable and can be operated by other AI agents or automation systems
- All commands support machine-friendly output (e.g., JSON) and error handling
- This enables Broca 2 to be embedded in agent networks, automated test harnesses, or orchestration systems

## 🚧 TODO List

1. **Multi-Agent Management**
   - [x] Implement multi-agent folder structure
   - [x] Add per-agent configuration isolation
   - [x] Support shared virtual environment
   - [ ] Add centralized agent management CLI
   - [ ] Implement agent health monitoring
   - [ ] Add agent deployment automation

2. **Queue Management**
   - [x] Implement basic status system
   - [x] Add status transition validation
   - [x] Implement basic status history tracking
   - [ ] Add comprehensive queue item archival system
   - [ ] Improve status transition logging
   - [ ] Add queue cleanup automation

3. **Dashboard Enhancements**
   - [x] Add basic message search functionality
   - [ ] Implement advanced conversation filtering (user/date)
   - [ ] Add conversation export functionality
   - [x] Add basic status-based queue filtering
   - [x] Implement basic status transition visualization
   - [ ] Add advanced analytics dashboard

4. **Monitoring & Logging**
   - [x] Add emoji-based logging system
   - [ ] Add performance monitoring
   - [ ] Create alert system for queue backlogs
   - [x] Add basic status transition monitoring
   - [ ] Implement comprehensive monitoring dashboard
   - [ ] Add system health metrics

5. **Security**
   - [ ] Add authentication for dashboard access
   - [ ] Implement role-based access control
   - [x] Basic API key management
   - [ ] Add session management
   - [ ] Implement audit logging
   - [ ] Add security headers and CSRF protection

6. **Deployment**
   - [ ] Create backup/restore procedures
   - [x] Add basic health check endpoints
   - [ ] Add comprehensive status monitoring endpoints
   - [ ] Create deployment documentation
   - [ ] Add container support
   - [ ] Create automated deployment scripts 