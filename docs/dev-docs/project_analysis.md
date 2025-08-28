# ⚠️ REPOSITORY MOVED ⚠️

**This repository has moved to: [http://github.com/sanctumos/broca](http://github.com/sanctumos/broca)**

Please update your git remotes and use the new repository location for all future development and contributions.

---

# Project Analysis Document

## Project Overview
This document provides a comprehensive analysis of the Sanctum: Broca 2 project structure, components, and their current status. Broca 2 is a CLI-first, plugin-based message processing system for agent communication, now supporting multiple agent instances through a shared base installation architecture.

## Project Structure

### Multi-Agent Architecture
The project now follows a multi-agent architecture where:
- **Base Installation**: `broca2/` contains shared components, plugins, and runtime
- **Agent Instances**: `agent-{uuid}/` directories contain agent-specific configurations and data
- **Shared Resources**: Virtual environment, plugins, and core code are shared across all agents

### Core Components
- `runtime/core/` - Contains the fundamental business logic and core functionality
  - `agent.py` - Main agent implementation handling message processing and state management
  - `queue.py` - Queue management system for handling message processing
  - `plugin.py` - Plugin management and lifecycle
  - `message.py` - Message data structures and handling
  - `letta_client.py` - Client implementation for external service integration

### Plugin System
- `plugins/` - Extensible plugin architecture for different platforms
  - `telegram/` - Telegram message handling with markdown support
  - `telegram_bot/` - Standalone Telegram bot implementation
  - `cli_test/` - CLI testing and diagnostic interface

### CLI Tools
- `cli/` - Command-line interface tools for administration and management
  - `btool.py` - Main CLI interface for queue management, users, and system operations
  - `ctool.py` - Configuration and settings management
  - `qtool.py` - Queue-specific operations and monitoring
  - `utool.py` - User management and operations
  - `settings.py` - Settings management utilities

### Database Layer
- `database/` - Database operations and models
  - `operations/` - Database CRUD operations and queries
  - `models.py` - Database models and schemas
  - `session.py` - Database session management

### Configuration and Environment
- **Base Configuration**: `.env` and `settings.json` for shared settings
- **Agent Configuration**: `agent-{uuid}/.env` and `agent-{uuid}/settings.json` for agent-specific settings
- **Shared Resources**: `broca2/requirements.txt` for Python dependencies

## Detailed Component Analysis

### Core Components

#### Agent System (`runtime/core/agent.py`)
**Architecture:**
- Implements the `AgentClient` class for interacting with the agent API
- Supports multiple agent instances through configuration
- Uses environment variables for configuration (AGENT_ID, DEBUG_MODE)
- Implements singleton pattern for Letta client access

**Key Methods:**
1. `initialize()`: 
   - Verifies agent existence
   - Establishes connection with Letta service
   - Returns boolean success status

2. `process_message()`:
   - Handles message processing through agent API
   - Supports debug mode for testing
   - Processes different message types (reasoning_message, content)
   - Implements fallback to reasoning if no content found

3. `cleanup()`:
   - Handles resource cleanup
   - Currently minimal implementation

**Integration Points:**
- Connects with Letta service via `letta_client`
- Uses environment variables for configuration
- Implements logging with custom formatter
- Supports agent-specific configuration through multi-agent architecture

#### Queue Management (`runtime/core/queue.py`)
**Architecture:**
- Implements `QueueProcessor` class for message queue handling
- Uses custom `EmojiFormatter` for logging
- Supports three modes: echo, listen, and live
- **Multi-Agent**: Each agent instance maintains its own queue and database

**Key Components:**
1. `QueueProcessor`:
   - Manages message processing queue
   - Handles message prioritization
   - Implements retry mechanisms
   - Supports typing indicators for Telegram

2. Message Processing Flow:
   - Retrieves pending messages from queue
   - Processes based on current mode
   - Updates message and queue status
   - Handles core block attachment/detachment

**Mode-Specific Behavior:**
1. Echo Mode:
   - Returns formatted message without processing
   - Updates message and queue status
   - Sends response via callback

2. Listen Mode:
   - Stores messages without processing
   - Marks queue items as completed
   - No response generation

3. Live Mode:
   - Processes messages through agent
   - Manages core block attachment
   - Handles typing indicators

#### Plugin Management (`runtime/core/plugin.py`)
**Architecture:**
- Manages plugin lifecycle and configuration
- Supports multi-agent plugin instances
- Handles plugin discovery and loading
- Manages agent-specific plugin configuration

**Key Features:**
1. **Plugin Discovery**: Automatically discovers plugins in `plugins/` directory
2. **Multi-Agent Support**: Creates plugin instances for each agent
3. **Configuration Management**: Merges base and agent-specific settings
4. **Lifecycle Management**: Handles plugin start/stop for each agent

### Plugin System

#### Telegram Plugin (`plugins/telegram/`)
**Architecture:**
- Full Telegram message handling with markdown support
- Implements `MessageFormatter` with markdown preservation
- Supports Telegram MarkdownV2 format with fallback to plain text
- **Multi-Agent**: Each agent can have different Telegram configurations

**Key Features:**
1. **Markdown Support**: Preserves markdown formatting from Letta/Broca responses
2. **Telegram Compatibility**: Escapes special characters for MarkdownV2
3. **Error Handling**: Falls back to plain text if markdown parsing fails
4. **Agent Isolation**: Each agent maintains separate Telegram sessions

#### CLI Test Plugin (`plugins/cli_test/`)
**Architecture:**
- Diagnostic and testing interface
- Provides CLI commands for system testing
- Supports both human and machine (MCP) operation
- **Multi-Agent**: Can test specific agent instances or all agents

### CLI Tools

#### Main CLI Interface (`cli/btool.py`)
**Architecture:**
- Primary CLI tool for system administration
- Supports multi-agent operations
- Provides JSON output for automation
- Implements MCP-compatible interface

**Key Commands:**
1. **Queue Management**: `queue list`, `queue flush`, `queue delete`
2. **User Management**: `users list`, `users get`, `users conversations`
3. **System Status**: `status`, `agent info`, `plugins list`
4. **Multi-Agent**: `agents list`, `agents status`, `agents backup`

#### Configuration Tools (`cli/ctool.py`)
**Architecture:**
- Manages system and plugin configuration
- Supports both base and agent-specific settings
- Implements configuration validation
- Provides dynamic configuration updates

### Database Layer

#### Database Operations (`database/operations/`)
**Architecture:**
- Implements CRUD operations for all database entities
- Supports multi-agent database isolation
- Provides transaction management
- Implements connection pooling

**Key Components:**
1. **Message Operations**: Insert, update, and query messages
2. **User Operations**: User creation and management
3. **Queue Operations**: Queue item management and status updates
4. **Profile Operations**: Platform-specific user profile management

#### Database Models (`database/models.py`)
**Architecture:**
- Defines database schema and relationships
- Supports multi-agent data isolation
- Implements proper indexing and constraints
- Provides migration support

## Multi-Agent Architecture Benefits

### 1. **Instance Isolation**
- Each agent runs independently with separate configuration
- Independent databases prevent data cross-contamination
- Separate log files for easy debugging and monitoring

### 2. **Shared Resources**
- Base installation and virtual environment shared across all instances
- Common plugins and runtime components
- Reduced disk usage and maintenance overhead

### 3. **Scalability**
- Easy to add new agents without affecting existing ones
- Clear 1:1 mapping between agent IDs and instance folders
- Standardized folder structure for easy automation

### 4. **Maintenance**
- Update base installation once, affects all agents
- Git-based updates preserve agent-specific configurations
- Centralized dependency management

## Current Status and Capabilities

### ✅ **Implemented Features**
1. **Multi-Agent Architecture**: Complete implementation with shared base installation
2. **Plugin System**: Extensible plugin architecture with multi-agent support
3. **CLI Tools**: Comprehensive command-line interface for administration
4. **Telegram Integration**: Full message handling with markdown support
5. **Database Layer**: Robust database operations with multi-agent isolation
6. **Configuration Management**: Hierarchical configuration with agent-specific overrides

### 🔄 **In Progress**
1. **Plugin Development**: Additional platform integrations
2. **CLI Enhancements**: Advanced monitoring and management commands
3. **Documentation**: Comprehensive guides for multi-agent setup and management

### 📋 **Planned Features**
1. **Centralized Management**: MCP server for managing multiple Broca instances
2. **Advanced Monitoring**: Comprehensive health monitoring and alerting
3. **Automated Deployment**: Scripts for agent deployment and configuration
4. **Container Support**: Docker and container orchestration support

## Technical Architecture

### **Configuration Hierarchy**
1. **Agent-specific settings** (`agent-{uuid}/settings.json`) - Highest priority
2. **Agent-specific environment** (`agent-{uuid}/.env`) - Second priority
3. **Base plugin settings** (`settings.json`) - Third priority
4. **Base environment** (`.env`) - Fourth priority
5. **Default values** (hardcoded in plugin) - Lowest priority

### **Plugin Architecture**
- **Base Installation**: Plugins installed in `plugins/` and shared across all agents
- **Agent Instances**: Each agent can have its own plugin configuration and settings
- **Shared Resources**: Plugin code and dependencies shared, but configuration per-agent

### **Database Architecture**
- **Agent Isolation**: Each agent maintains separate database file (`sanctum.db`)
- **Shared Schema**: All agents use the same database schema and models
- **Data Separation**: Complete data isolation between agent instances

## Integration Points

### **External Services**
1. **Letta API**: Agent communication and message processing
2. **Telegram API**: Message delivery and user interaction
3. **Database**: SQLite database for message and user storage

### **Internal Components**
1. **Plugin Manager**: Manages plugin lifecycle and configuration
2. **Queue Processor**: Handles message processing and routing
3. **CLI Tools**: Provides administrative and diagnostic interfaces
4. **Configuration System**: Manages hierarchical configuration

## Security Considerations

### **Multi-Agent Security**
- Each agent runs with its own database and configuration
- No shared credentials between agents
- Separate log files prevent information leakage
- Proper file permissions for agent directories

### **Configuration Security**
- Environment variables for sensitive data
- Agent-specific API keys and endpoints
- Secure backup and restore procedures
- Access control for shared resources

## Performance Characteristics

### **Resource Usage**
- **Memory**: Minimal per-agent overhead due to shared base installation
- **Disk**: Efficient storage with shared code and dependencies
- **CPU**: Scalable processing with per-agent queue management
- **Network**: Optimized API calls with connection pooling

### **Scalability**
- **Horizontal**: Easy to add new agents on the same machine
- **Vertical**: Can scale individual agent resources as needed
- **Geographic**: Support for distributed agent deployments

## Conclusion

Sanctum: Broca 2 represents a significant evolution from the original Broca system, introducing a robust multi-agent architecture that maintains the core message processing capabilities while adding substantial scalability and management features. The plugin-based architecture and CLI-first design make it highly extensible and suitable for both development and production environments.

The multi-agent architecture provides excellent isolation and scalability while maintaining resource efficiency through shared components. The comprehensive CLI tools and plugin system make it easy to manage multiple agent instances and extend functionality for new platforms and use cases.

## Cross-References
- [Multi-Agent Architecture Guide](multi-agent-architecture.md) - Complete guide to multi-agent setup
- [Plugin Development Guide](plugin_development.md) - Creating plugins for Broca 2
- [CLI Reference](cli_reference.md) - Command-line tool documentation
- [Configuration Guide](configuration.md) - Configuration management details 