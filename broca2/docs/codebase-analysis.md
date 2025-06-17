# Broca Codebase Analysis

## Core Components Overview

### 1. Application Structure (`broca2/main.py`)
- **Purpose**: Main application entry point and component coordination
- **Components**:
  - `Application` class managing all system components
  - Plugin management system
  - Settings management with hot-reload capability
  - Database initialization and migration
- **Key Features**:
  - Dynamic settings management via `settings.json`
  - Plugin-based architecture
  - Graceful startup and shutdown
  - PID tracking for process management

### 2. Queue System (`runtime/core/queue.py`)
- **Purpose**: Handles asynchronous processing of messages
- **Components**:
  - `QueueProcessor` class for message processing
  - Core block management for user context
  - Multiple processing modes (echo, listen, live)
- **Key Features**:
  - Concurrent message processing
  - Error handling and retry mechanism
  - Core block management for processing
  - Status tracking (pending, processing, completed, failed)
  - Platform-specific response routing

### 3. Database Operations (`database/operations/`)
- **Structure**:
  - Clean separation into focused modules
  - `messages.py`: Message CRUD operations
  - `queue.py`: Queue management
  - `users.py`: User/profile management
  - `shared.py`: Common database utilities
- **Key Tables**:
  - `messages`: Stores message content and metadata
  - `queue`: Tracks processing status and attempts
  - `platform_profiles`: Links platform users to internal IDs
  - `letta_users`: Core user management

### 4. Plugin System (`runtime/core/plugin.py`)
- **Purpose**: Extensible platform integration
- **Components**:
  - `PluginManager` for plugin lifecycle
  - Platform-specific plugins (e.g., Telegram)
  - Message handler registration
- **Key Features**:
  - Dynamic plugin loading
  - Platform-specific message handling
  - Event routing system

## Key Workflows

### Message Processing Flow
1. **Message Reception**:
   - Platform-specific handler receives message
   - Message sanitized and formatted
   - Added to processing queue

2. **Queue Processing**:
   - QueueProcessor picks up pending messages
   - Attaches user's core block for context
   - Processes based on current mode
   - Routes response through platform handler
   - Updates message and queue status

### Settings Management
1. **Configuration**:
   - Settings stored in `settings.json`
   - Hot-reload capability
   - Default settings generation
2. **Key Settings**:
   - Message processing mode
   - Debug mode
   - Queue refresh interval
   - Maximum retry attempts

## Project Structure
```
broca2/
├── main.py                 # Application entry point
├── runtime/
│   └── core/
│       ├── queue.py       # Queue processing
│       ├── plugin.py      # Plugin management
│       └── agent.py       # Agent client
├── database/
│   ├── operations/
│   │   ├── messages.py    # Message operations
│   │   ├── queue.py       # Queue operations
│   │   ├── users.py       # User operations
│   │   └── shared.py      # Common utilities
│   └── models.py          # Database models
├── plugins/
│   └── telegram/          # Telegram integration
├── common/
│   ├── config.py          # Configuration management
│   └── logging.py         # Logging setup
└── cli/                   # Command-line tools
```

## Key Considerations
- Maintain async/await patterns throughout
- Keep error handling and retry logic
- Preserve transaction safety
- Support multiple processing modes
- Extensible plugin architecture
- Configuration hot-reload capability

```sql
-- Queue Table
CREATE TABLE queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    letta_user_id INTEGER,
    message_id INTEGER,
    status TEXT,
    attempts INTEGER DEFAULT 0,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (letta_user_id) REFERENCES letta_users(id),
    FOREIGN KEY (message_id) REFERENCES messages(id)
)
```

## Recommendations for Extraction

### 1. Core Components to Extract
- Message Buffer System
- Queue Processor
- Database Operations

### 2. Suggested File Structure
```
src/
├── queue/
│   ├── processor.py
│   └── queue_ops.py
└── db/
    ├── models.py
    └── operations.py
```

### 3. Key Considerations
- Maintain async/await patterns
- Keep error handling and retry logic
- Preserve transaction safety
- Consider making buffer delay configurable
- Extract core processing modes into separate handlers 