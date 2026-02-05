# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.11.0] - 2025-01-05

### Added
- **Letta identity threading**: `sender_id` is now passed from plugins through the queue and agent so the Letta API receives the correct `identity_id` per sender
- **Database**: `get_letta_identity_id(platform_user_id, platform)` in `database/operations/users.py` for resolving Letta identity IDs from platform user IDs

### Changed
- **Agent**: `process_message`, `create`, `stream`, and `create_async` accept optional `sender_id` and forward it to the Letta client
- **Queue**: Processor retrieves identity_id from the database and invokes the agent with `sender_id`
- **Main**: `_process_message` accepts and passes `sender_id` from queue payload to the agent
- **Telegram Bot plugin**: Passes Telegram user ID as `sender_id` when enqueueing and when calling the processor

### Known limitations / TODO
- **Image handling**: Previous progress on image/attachment handling was lost; basic text flow is restored. Image support is planned for a future release.

---

## [0.10.0] - 2025-01-04

### Added
- **Plugin Auto-Discovery System**: Dynamic plugin discovery and loading from `plugins/` directory
  - Automatic plugin detection and instantiation
  - Dynamic settings injection via `apply_settings()` method
  - Platform-specific message handler registration
- **Web Chat Plugin**: Complete polling-based web chat integration
  - PHP API bridge architecture for secure web chat
  - Pull-based message retrieval from external API
  - Session management with unique user identification
  - Full end-to-end message processing pipeline
- **Enhanced Plugin Interface**: New `apply_settings()` method for dynamic configuration
- **Platform-Agnostic Message Formatting**: Updated MessageFormatter to use platform-specific ID labels
- **Database Integration Patterns**: Standardized user and profile creation patterns
- **Comprehensive Plugin Development Guide**: Updated documentation with real-world examples and troubleshooting

### Changed
- **Plugin Architecture**: Transitioned from hardcoded plugin loading to dynamic auto-discovery
- **Message Handler Requirements**: Standardized response handler pattern with `(response, profile, message_id)` signature
- **Settings Management**: Implemented lazy initialization and fallback patterns for plugin settings
- **Import Patterns**: Established lazy import patterns for self-contained plugins
- **Documentation**:
  - Updated plugin development guide with critical implementation details
  - Added troubleshooting section with common issues and solutions
  - Enhanced examples with complete plugin implementations
  - Added database integration patterns and error handling strategies

### Fixed
- **Plugin Loading Errors**: Resolved module import and dependency issues
- **Message Routing**: Fixed response handler callable requirements
- **User Details Lookup**: Corrected database integration for user and profile creation
- **Settings Validation**: Improved error handling for missing or invalid settings
- **Platform-Specific Labels**: Fixed hardcoded "Telegram ID" labels to use platform-specific naming

### Technical Details
- **Auto-Discovery**: Plugins automatically discovered and loaded from `plugins/` directory
- **Lazy Loading**: External dependencies imported only when needed
- **Database Integration**: Standardized patterns for user creation, message insertion, and queue processing
- **Error Handling**: Comprehensive error handling with graceful degradation
- **Resource Management**: Proper cleanup of connections and tasks in plugin lifecycle

---

## [0.9.1] - 2024-12-28

### Added
- **Multi-Agent Installation Support**: New requirements.txt-based installation approach for multiple agent instances
- **Agent-Specific Directory Structure**: Support for isolated agent instances under `~/sanctum/broca2/<AGENTID>/`
- **Shared Virtual Environment**: Single venv at `~/sanctum/broca2/venv/` shared across all agents
- **Installation Documentation**: New `INSTALL.md` with comprehensive multi-agent setup instructions

### Changed
- **Installation Method**: Switched from egg-info package installation to simple requirements.txt approach
- **CLI Execution**: Updated CLI tools to use module-based execution (`python -m cli.btool`) instead of global commands
- **Documentation Updates**:
  - Updated README with new multi-agent folder structure
  - Revised installation instructions for agent-specific directories
  - Updated CLI usage examples to reflect new execution method
- **Project Structure**: Removed setup.py and egg-info in favor of requirements.txt approach

### Fixed
- **Global Installation Conflicts**: Eliminated conflicts when running multiple Broca instances
- **Agent Isolation**: Each agent now has completely isolated configuration, database, and logs
- **Resource Efficiency**: Shared base installation with agent-specific data directories

### Removed
- **setup.py**: Removed package installation configuration
- **broca2.egg-info/**: Removed package metadata directory
- **Global Console Scripts**: Removed `broca2` and `broca-admin` global commands

### Technical Details
- **Dependencies**: Maintained same dependency list in requirements.txt
- **Execution**: Agents run with `python ../main.py` from agent-specific directories
- **Configuration**: Each agent has its own `.env`, `settings.json`, and `sanctum.db`

---

## [0.9.0] - 2024-12-28

### Added
- **CLI-first Architecture**: Complete redesign focusing on command-line interface for better control and automation
- **Plugin System**: Extensible plugin-based message handling system
  - Telegram plugin for Telegram bot integration
  - CLI plugin for diagnostic and testing capabilities
  - Standardized plugin interface with lifecycle management
- **Prismatic Telegram Bot Plugin**: New plugin implementing 1:1 owner-only messaging with aiogram integration
- **Queue Management System**: Comprehensive message queue processing with multiple modes (Echo, Listen, Live)
- **Agent API Integration**: Enhanced Letta Agentic Framework integration through `AgentClient`
- **Database Operations**: New database models and operations for users, messages, and queue management
- **CLI Tools**: Comprehensive admin tools including:
  - Queue management (`broca-admin queue`)
  - User management (`broca-admin users`)
  - Settings management (`broca-admin settings`)
  - Conversation tools for viewing and managing conversations
- **MCP-Ready Design**: All CLI tools and plugin interfaces designed for machine-controllability by agents

### Changed
- **Project Rebranding**: Renamed from "Broca 2" to "Sanctum: Broca 2" across all documentation and references
- **Architecture Restructure**: Clean separation between core and platform-specific code
- **Database Schema**: Refactored LettaUser model, removed redundant `conversation_history_limit` field
- **Documentation Updates**:
  - Enhanced README with middleware role explanation and multi-agent architecture plans
  - Updated project analysis and documentation formatting
  - Revised project plans for Telegram bot implementation
  - Added comprehensive plugin development guide

### Fixed
- **Telegram Bot Stability**: Addressed minor bugs in Prismatic Telegram BOT plugin implementation
- **Database Migration**: Enhanced migration scripts with proper error handling and logging
- **Message Handling**: Improved Telegram message handling with bot ignore functionality
- **Documentation**: Corrected formatting in Database Layer section for improved readability

### Removed
- **Legacy Documentation**: Removed outdated `broca-2-plan.md` and `codebase-analysis.md` files as part of project restructuring
- **Database Backup**: Removed database backup from git tracking and updated `.gitignore`

### Technical Details
- **Dependencies**: Updated to include telethon, python-dotenv, sqlalchemy, aiohttp, emoji, rich, typer, and pydantic
- **Entry Points**: Added console scripts for `broca2` and `broca-admin`
- **Version**: Bumped to 0.9.0 reflecting major architectural changes

### Planned Features
- **Multi-Agent Architecture**: Support for multiple Letta agents with shared virtual environments
- **Broca MCP Server**: Management Control Panel for instance management, monitoring, and centralized configuration

---

## How to Read This Changelog

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes

---

*For more details on any changes, please refer to the git commit history or project documentation.*
