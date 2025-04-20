# Broca Codebase Analysis

## Core Components Overview

### 1. Message Buffer System (`telegram/handlers.py`)
- **Purpose**: Buffers messages for batch processing
- **Key Components**:
  - `MessageBuffer` class with configurable delay (default 5s)
  - In-memory buffer using Dict[int, Dict[str, Any]]
  - Async flush mechanism with cancellable tasks
- **Flow**:
  1. Messages added to buffer with user/platform IDs
  2. Flush scheduled after delay
  3. Messages combined and inserted into database
  4. Added to processing queue

### 2. Queue System (`core/queue.py`, `database/operations/queue.py`)
- **Purpose**: Handles asynchronous processing of messages
- **Components**:
  - `QueueProcessor` class for message processing
  - Database-backed queue storage
  - Multiple processing modes (echo, listen, live)
- **Key Features**:
  - Concurrent message processing
  - Error handling and retry mechanism
  - Core block management for processing
  - Status tracking (pending, processing, completed, failed)

### 3. Database Operations
- **Structure**:
  - Clean separation into focused modules
  - `messages.py`: Message CRUD operations
  - `queue.py`: Queue management
  - `users.py`: User/profile management
- **Key Tables**:
  - `messages`: Stores message content and metadata
  - `queue`: Tracks processing status and attempts
  - `platform_profiles`: Links platform users to internal IDs

### 4. Main Processing Loop (`main.py`)
- **Core Components**:
  - Application class coordinating all parts
  - Telegram event handlers
  - Queue processor task
  - Message mode management (echo/listen/live)

## Key Workflows

### Message Processing Flow
1. **Message Reception**:
   - Telegram handler receives message
   - Message sanitized and formatted
   - Added to MessageBuffer

2. **Buffer Processing**:
   - Messages accumulated for configured delay
   - Combined messages flushed to database
   - Queue entry created for processing

3. **Queue Processing**:
   - QueueProcessor picks up pending messages
   - Processes based on current mode
   - Updates message and queue status
   - Handles responses/callbacks

### Database Schema (Key Tables)

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
├── buffer/
│   ├── message_buffer.py
│   └── buffer_utils.py
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