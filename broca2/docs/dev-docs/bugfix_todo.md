# ⚠️ REPOSITORY MOVED ⚠️

**This repository has moved to: [http://github.com/sanctumos/broca](http://github.com/sanctumos/broca)**

Please update your git remotes and use the new repository location for all future development and contributions.

---

# Letta Integration Bugfix TODO

## Message Formatting Issues ✅

1. **Timestamp Pollution** ✅
   - Location: `telegram/handlers.py` in `MessageBuffer._flush_buffer`
   - Issue: Adding unnecessary timestamps to messages
   - Fix: Removed timestamp from message formatting
   - Status: Completed
   - Changes:
     - Removed timestamp formatting from message buffer
     - Standardized on clean message format without timestamps

2. **Inconsistent Message Formatting** ✅
   - Location: Multiple files
   - Issue: Different formatting between test script and application
   - Fix: Standardized message formatting across all components
   - Status: Completed
   - Changes:
     - Implemented `MessageFormatter` class in `core.message`
     - Standardized format: `[User: @username] message`
     - Removed redundant formatting layers
     - Added proper user metadata handling

3. **Logging Enhancement** ✅
   - Location: `core/queue.py`
   - Issue: Logs lacked visual distinction and context
   - Fix: Added emoji-based log formatting
   - Status: Completed
   - Changes:
     - Implemented `EmojiFormatter` class
     - Added visual indicators for different log levels:
       - 🔵 INFO
       - ⚠️ WARNING
       - ❌ ERROR
       - 🔍 DEBUG
       - 🚨 CRITICAL
     - Enhanced log messages with more context
     - Improved error and status reporting

## Response Handling Issues ✅

1. **Incorrect Response Field Access** ✅
   - Location: `core/agent.py` in `process_message`
   - Issue: Trying to access non-existent fields in Letta response
   - Current: `response.messages[0].message`
   - Actual Format:
     ```json
     {
       "messages": [
         {
           "id": "id",
           "date": "2024-01-15T09:30:00Z",
           "name": "name",
           "otid": "otid",
           "message_type": "system_message",
           "content": "content"
         }
       ],
       "usage": {...}
     }
     ```
   - Fix: Update to access correct fields in response structure
   - Status: Completed
   - Changes:
     - Updated to use `response.messages[0].content`
     - Added proper error handling for missing attributes
     - Added detailed logging for debugging
     - Improved type hints and documentation

2. **Response Processing** ✅
   - Location: `core/agent.py`
   - Issue: Not properly handling the Letta response format
   - Current: Attempting to access incorrect fields
   - Fix: Update to match actual response structure
   - Status: Completed
   - Changes:
     - Added robust response validation
     - Improved error handling and logging
     - Added debug logging for response details
     - Implemented proper attribute checking

## Client Initialization Issues ✅

1. **Duplicate Letta Client** ✅
   - Location: `database/operations.py`
   - Issue: Global Letta client initialization might conflict with agent client
   - Current: 
     ```python
     client = Letta(
         base_url=os.getenv('LETTA_SERVER_URL'),
         token=os.getenv('LETTA_SERVER_PASSWORD')
     )
     ```
   - Fix: Remove duplicate client or ensure proper separation of concerns
   - Status: Completed
   - Changes:
     - Created singleton Letta client in `core/letta_client.py`
     - Standardized environment variables
     - Updated all files to use singleton client
     - Added `.env.example` documentation

2. **Environment Variable Standardization** ✅
   - Location: All files using Letta client
   - Issue: Inconsistent environment variable names across the codebase
   - Fix: Standardize on `LETTA_API_ENDPOINT` and `LETTA_API_KEY`
   - Status: Completed
   - Changes:
     - Updated all references to use standardized variable names
     - Updated documentation and .env.example
     - Added validation for required variables

3. **Client Configuration Management** ✅
   - Issue: No centralized configuration management for Letta client
   - Fix: Implement singleton pattern with proper error handling
   - Status: Completed
   - Changes:
     - Created configuration class for Letta client settings
     - Implemented proper error handling for missing/invalid config
     - Added configuration validation

## Message Flow Issues

1. **Multiple Formatting Layers** ✅
   - Location: `telegram/handlers.py` and `core/queue.py`
   - Issue: Messages being formatted multiple times
   - Fix: Implemented single source of formatting
   - Status: Completed
   - Changes:
     - Centralized formatting in `MessageFormatter` class
     - Removed redundant formatting in buffer and queue
     - Standardized format across all components

2. **Response Processing** ✅
   - Location: `core/agent.py`
   - Issue: Not properly handling the Letta response format
   - Current: Attempting to access incorrect fields
   - Fix: Update to match actual response structure
   - Status: Completed
   - Changes:
     - Added robust response validation
     - Improved error handling and logging
     - Added debug logging for response details
     - Implemented proper attribute checking

## Next Steps
1. ~~Remove timestamp formatting from message buffer~~ ✅
2. ~~Standardize message formatting across components~~ ✅
3. ~~Fix response handling in agent client~~ ✅
4. ~~Resolve duplicate client initialization~~ ✅
5. ~~Implement single source of message formatting~~ ✅
6. ~~Update response processing to match Letta format~~ ✅
7. Implement comprehensive error recovery system
8. Add automated testing suite
9. Optimize database operations
10. Complete API documentation

# Bugfix Todo List

## Priority Order (Most Foundational to Least)

1. **Client Initialization & Configuration** ✅ (Critical Infrastructure)
   - Duplicate Letta Client ✅
   - Environment Variable Standardization ✅
   - Client Configuration Management ✅

2. **Response Handling** ✅ (Core Functionality)
   - Incorrect Response Field Access ✅
   - Response Processing ✅

3. **Message Formatting** (Data Flow)
   - Multiple Formatting Layers
   - Inconsistent Message Formatting
   - Timestamp Pollution

4. **Message Flow & Queue Processing** (System Behavior)
   - Queue Processing Logic
   - Message Buffer Management
   - Error Handling

5. **Database Operations** (Data Management)
   - Message Storage
   - Queue Management

6. **Testing & Validation** (Quality Assurance)
   - Test Coverage
   - Validation

7. **Core Block Management**
   - Core block attachment/detachment

8. **Redundant Context Management**
   - Remove redundant conversation history implementation

9. **Queue Status Display Issues** 🔄

## Detailed Fixes by Priority

### Priority 1: Client Initialization & Configuration ✅

#### 1. Duplicate Letta Client ✅
- **Location**: `database/operations.py` and `core/agent.py`
- **Issue**: Two separate Letta clients being initialized with different environment variables
- **Impact**: 
  - Creates duplicate connections to Letta server
  - Uses inconsistent environment variables
  - Could lead to connection issues if variables point to different servers
- **Fix**: 
  - Standardize environment variables:
    - `LETTA_API_KEY` (replace `AGENT_API_KEY` and `LETTA_SERVER_PASSWORD`)
    - `LETTA_API_ENDPOINT` (replace `AGENT_ENDPOINT` and `LETTA_SERVER_URL`)
  - Create singleton Letta client
  - Use dependency injection for client sharing
  - Remove duplicate initialization in `database/operations.py`
- **Status**: Completed
- **Changes**: Implemented singleton pattern with standardized configuration

#### 2. Environment Variable Standardization ✅
- **Location**: All files using Letta client
- **Issue**: Inconsistent environment variable names across the codebase
- **Fix**:
  - Update all references to use standardized variable names
  - Update documentation and .env.example
  - Add validation for required variables
- **Status**: Completed
- **Changes**: Standardized on `LETTA_API_ENDPOINT` and `LETTA_API_KEY`

#### 3. Client Configuration Management ✅
- **Issue**: No centralized configuration management for Letta client
- **Fix**:
  - Create configuration class for Letta client settings
  - Implement proper error handling for missing/invalid config
  - Add configuration validation
- **Status**: Completed
- **Changes**: Implemented singleton pattern with proper error handling

### Priority 2: Response Handling ✅

#### 1. Incorrect Response Field Access ✅
- **Location**: `core/agent.py` in `process_message` method
- **Issue**: Trying to access `message` attribute on `ReasoningMessage` object
- **Fix**: Update to use correct field access based on Letta response format
- **Status**: Completed
- **Changes**:
  - Updated to use `response.messages[0].content`
  - Added proper error handling for missing attributes
  - Added detailed logging for debugging
  - Improved type hints and documentation

#### 2. Response Processing ✅
- **Location**: `core/agent.py`
- **Issue**: Response format not being handled correctly
- **Fix**: Update response processing to match Letta format with `messages` array
- **Status**: Completed
- **Changes**:
  - Added robust response validation
  - Improved error handling and logging
  - Added debug logging for response details
  - Implemented proper attribute checking

#### 3. Message content extraction
- **Location**: `core/agent.py`
- **Issue**: Incorrect handling of reasoning vs content messages
- **Fix**: Added proper message type detection and fallback to reasoning when content missing
- **Status**: Completed
- **Changes**:
  - Added fallback to reasoning when content missing
  - Added proper message type detection

### Priority 3: Message Formatting ✅

#### 1. Message Standardization ✅
- **Location**: All message-handling components
- **Issue**: Inconsistent message formatting across system
- **Fix**:
  - Implemented centralized `MessageFormatter` class
  - Standardized format across all components
  - Removed redundant formatting layers
  - Added proper metadata handling
- **Status**: Completed
- **Changes**: 
  - Created unified message format
  - Removed timestamp pollution
  - Improved user metadata handling
  - Enhanced logging with emoji formatting

#### 2. Logging Enhancement ✅
- **Location**: `core/queue.py`
- **Issue**: Logs lacked visual distinction and context
- **Fix**:
  - Implemented emoji-based log formatting
  - Enhanced log messages with more context
  - Added clear visual indicators for different log levels
- **Status**: Completed
- **Changes**:
  - Added `EmojiFormatter` class
  - Improved log readability with emojis
  - Enhanced error and status reporting
  - Added more descriptive context to log messages

### Priority 4: Message Flow & Queue Processing

#### 1. Queue Processing Logic
- **Location**: `core/queue.py`
- **Issue**: Mode handling logic could be clearer
- **Fix**: Refactor mode handling into separate methods

#### 2. Message Buffer Management
- **Location**: `telegram/handlers.py`
- **Issue**: Buffer cleanup not properly handled
- **Fix**: Implement proper buffer cleanup on shutdown

#### 3. Error Handling
- **Location**: Multiple files
- **Issue**: Inconsistent error handling across the codebase
- **Fix**: Implement standardized error handling and logging

### Priority 5: Database Operations

#### 1. Message Storage
- **Location**: `database/operations.py`
- **Issue**: Message storage could be optimized
- **Fix**: Review and optimize message storage schema

#### 2. Queue Management
- **Location**: `database/operations.py`
- **Issue**: Queue status updates could be more robust
- **Fix**: Implement transaction-based queue updates

#### 3. User ID handling
- **Location**: `database/operations.py`
- **Issue**: Confusion between platform_user_id and database ID
- **Fix**: Added proper type conversion for Telegram IDs
- **Status**: Completed
- **Changes**:
  - Fixed platform_user_id vs database ID confusion
  - Added proper type conversion for Telegram IDs
  - Improved error handling for missing profiles

### Priority 6: Testing & Validation

#### 1. Test Coverage
- **Issue**: Limited test coverage for message flow
- **Fix**: Add comprehensive tests for message processing

#### 2. Validation
- **Issue**: Input validation could be improved
- **Fix**: Add input validation at key points in the message flow

#### 3. Debug tools
- **Location**: Added test_agent.py for message processing testing
- **Issue**: Limited debugging tools
- **Fix**: Added test_agent.py for message processing testing
- **Status**: Completed
- **Changes**:
  - Added test_agent.py for message processing testing
  - Added detailed logging
  - Added response structure inspection

### Priority 7: Core Block Management ✅
- [x] Core block attachment/detachment
  - Location: `core/queue.py` in message processing
  - Issue: Core block not properly attached/detached for each message
  - Impact: 
    - Potential memory leaks
    - Inconsistent message processing
    - Possible state corruption between messages
  - Fix: ✅
    - Ensure core block is attached before processing each message
    - Verify core block is properly detached after processing
    - Add logging for core block state changes
    - Implement proper error handling for attachment failures
  - Priority: High (affects message processing reliability)
  - Status: Completed
  - Implementation Details:
    - Proper block lifecycle management in QueueProcessor
    - Robust error handling with nested try/catch blocks
    - Block detachment guaranteed in finally blocks
    - Detailed logging for block operations
    - Block IDs stored and retrieved reliably from database
    - No reliance on unreliable client.blocks.list()
    - Each message processing has independent block cycle
    - Multiple safeguards against state corruption

### Priority 8: Redundant Context Management
- [x] Remove redundant conversation history implementation
  - Location: `database/models.py`, `database/operations.py`
  - Issue: Middleware implements its own conversation history limit which is redundant with Letta's context management
  - Impact:
    - Unnecessary database field and code complexity
    - Potential confusion about where context is actually managed
    - No actual effect on conversation context (managed by Letta)
  - Fix:
    - Removed `conversation_history_limit` field from database schema
    - Removed related code from operations
    - Updated documentation to clarify that Letta manages context through core blocks
    - Ensured core block attachment/detachment is properly implemented
  - Priority: Medium (cleanup task)
  - Dependencies:
    - Core Block Management fix
    - Database schema migration

### Priority 9: Queue Status Display Issues 🔄

**Problem Description:**
1. Conversational List Status Issues:
   - All messages are showing as "Pending" in the conversations list
   - Root cause: In `get_message_history()`, the status fallback logic is incorrect:
     ```python
     'status': row[8] if row[8] else ('Processed' if bool(row[4]) else 'Pending')
     ```
   - The LEFT JOIN with queue table means most messages don't have a queue status (row[8] is NULL)
   - The fallback logic then incorrectly defaults to 'Pending' for processed messages

2. Queue Page Display Issues:
   - The Queue page is not showing any items, including actual pending items
   - Root cause: Multiple potential issues:
     - `get_all_queue_items()` may be filtering too aggressively with:
       ```sql
       WHERE q.status IN ('pending', 'processing')
       ```
     - Possible disconnect between queue status updates and message processing status
     - Queue items might be getting cleared without proper status tracking

**Impact:**
- Users cannot accurately track message processing status
- System appears non-functional even when working correctly
- Difficult to debug processing issues without accurate status display
- Poor user experience due to misleading status information

**Required Fixes:**
1. Conversational List:
   - Revise status determination logic in `get_message_history()`
   - Consider using message's processed flag as primary status indicator
   - Add proper status mapping between queue and message states

2. Queue Page:
   - Review and possibly expand status filter in `get_all_queue_items()`
   - Implement proper status tracking throughout message lifecycle
   - Add status transition logging for debugging
   - Consider adding queue item retention policy

**Dependencies:**
- Database schema for messages and queue tables
- Message processing workflow in QueueProcessor
- Status update operations in database layer

**Notes:**
- Status synchronization between messages and queue items needs careful handling
- Consider adding a cleanup routine for orphaned queue items
- May need to add migration for fixing incorrect status values

**Proposed Status System Design:**

1. **Core Status States:**
   ```python
   MESSAGE_STATES = {
       'RECEIVED':    'Message received, not yet queued',
       'QUEUED':      'Added to processing queue',
       'PROCESSING':  'Currently being processed',
       'COMPLETED':   'Successfully processed',
       'FAILED':      'Processing failed',
       'STORED':      'Stored without processing (Listen mode)',
       'ECHOED':      'Echoed back without processing (Echo mode)',
       'RETRYING':    'Scheduled for retry',
       'CANCELLED':   'Processing cancelled',
       'ARCHIVED':    'Moved to archive'
   }
   ```

2. **Valid State Transitions:**
   ```python
   STATE_TRANSITIONS = {
       'RECEIVED':   ['QUEUED', 'CANCELLED'],
       'QUEUED':     ['PROCESSING', 'CANCELLED'],
       'PROCESSING': ['COMPLETED', 'FAILED', 'STORED', 'ECHOED'],
       'FAILED':     ['RETRYING', 'ARCHIVED', 'CANCELLED'],
       'RETRYING':   ['QUEUED'],
       'COMPLETED':  ['ARCHIVED'],
       'STORED':     ['ARCHIVED'],
       'ECHOED':     ['ARCHIVED'],
       'CANCELLED':  ['ARCHIVED'],
       'ARCHIVED':   []  # Terminal state
   }
   ```

3. **Mode-Specific Workflows:**
   - **Live Mode Path:**
     ```
     RECEIVED -> QUEUED -> PROCESSING -> [COMPLETED|FAILED] -> ARCHIVED
     ```
   - **Echo Mode Path:**
     ```
     RECEIVED -> QUEUED -> PROCESSING -> ECHOED -> ARCHIVED
     ```
   - **Listen Mode Path:**
     ```
     RECEIVED -> QUEUED -> PROCESSING -> STORED -> ARCHIVED
     ```

4. **Status Display Categories:**
   ```python
   DISPLAY_CATEGORIES = {
       'ACTIVE': [
           'QUEUED',
           'PROCESSING',
           'RETRYING'
       ],
       'COMPLETED': [
           'COMPLETED',
           'STORED',
           'ECHOED'
       ],
       'PROBLEMATIC': [
           'FAILED',
           'CANCELLED'
       ],
       'INACTIVE': [
           'ARCHIVED'
       ]
   }
   ```

5. **Status Properties:**
   ```python
   STATUS_PROPERTIES = {
       'RECEIVED':   {'color': 'gray',    'icon': '📥', 'priority': 1},
       'QUEUED':     {'color': 'blue',    'icon': '📋', 'priority': 2},
       'PROCESSING': {'color': 'yellow',  'icon': '⚙️', 'priority': 3},
       'COMPLETED':  {'color': 'green',   'icon': '✅', 'priority': 4},
       'FAILED':     {'color': 'red',     'icon': '❌', 'priority': 5},
       'STORED':     {'color': 'purple',  'icon': '💾', 'priority': 4},
       'ECHOED':     {'color': 'cyan',    'icon': '🔄', 'priority': 4},
       'RETRYING':   {'color': 'orange',  'icon': '🔁', 'priority': 2},
       'CANCELLED':  {'color': 'gray',    'icon': '⏹️', 'priority': 5},
       'ARCHIVED':   {'color': 'gray',    'icon': '📦', 'priority': 6}
   }
   ```

6. **Implementation Requirements:**

   a. **Database Changes:**
   ```sql
   ALTER TABLE queue ADD COLUMN display_status TEXT;
   ALTER TABLE queue ADD COLUMN last_transition TIMESTAMP;
   ALTER TABLE queue ADD COLUMN transition_count INTEGER DEFAULT 0;
   ```

   b. **Status Management Class:**
   ```python
   class StatusManager:
       async def transition_status(self, item_id: int, new_status: str) -> bool:
           """
           Handles status transitions with validation and logging.
           Returns success/failure of transition.
           """
           pass

       async def get_item_history(self, item_id: int) -> List[Dict]:
           """
           Returns status transition history for an item.
           """
           pass

       async def cleanup_stuck_items(self) -> None:
           """
           Identifies and resolves items stuck in intermediate states.
           """
           pass
   ```

   c. **Display Components:**
   ```python
   class StatusDisplay:
       def get_status_badge(self, status: str) -> Dict:
           """
           Returns HTML/CSS properties for status display.
           """
           pass

       def get_category_counts(self) -> Dict[str, int]:
           """
           Returns count of items in each display category.
           """
           pass
   ```

7. **Migration Strategy:**
   - Phase 1: Add new status columns without enforcing constraints
   - Phase 2: Migrate existing statuses to new system
   - Phase 3: Enable status transition validation
   - Phase 4: Update UI components
   - Phase 5: Clean up legacy status handling

8. **Monitoring and Maintenance:**
   - Log all status transitions for audit
   - Monitor items stuck in intermediate states
   - Regular cleanup of archived items
   - Dashboard for status distribution
   - Alerts for unusual transition patterns

This system provides:
- Clear state definitions and transitions
- Mode-specific workflows
- Consistent display properties
- Status history tracking
- Cleanup mechanisms
- Migration path from current system

## 1. Client Initialization & Configuration ✅
- [x] Duplicate Letta Client
  - Multiple initializations across files
  - Potential conflicts in configuration
  - Solution: Created singleton Letta client in core/letta_client.py
  - Updated all components to use the singleton client
  - Added proper environment variable handling
  - Added .env.example file for documentation

## 2. Response Handling ✅
- [x] Incorrect response field access
  - Fixed response.messages[0].content access
  - Added proper error handling
  - Added logging for debugging
- [x] Response processing
  - Improved error handling
  - Added type hints
  - Added detailed logging
- [x] Message content extraction
  - Fixed handling of reasoning vs content messages
  - Added proper message type detection
  - Added fallback to reasoning when content missing

## 3. Message Formatting ✅
- [x] Timestamp pollution
  - Removed redundant timestamps from message formatting
  - Made timestamps optional in MessageFormatter
  - Standardized timestamp format when used
- [x] Buffer formatting
  - Standardized message format across components
  - Improved message content extraction
  - Added consistent metadata formatting
- [x] Inconsistent message formatting
  - Centralized formatting in MessageFormatter
  - Unified format: [Telegram ID: X, Username: @Y] message
  - Improved message sanitization

## 4. Database Operations
- [ ] Connection management
  - Connection pooling
  - Connection timeouts
  - Error recovery
- [ ] Query optimization
  - Index missing
  - Slow queries
  - Query caching
- [x] User ID handling
  - Fixed platform_user_id vs database ID confusion
  - Added proper type conversion for Telegram IDs
  - Improved error handling for missing profiles

## 5. Error Handling
- [x] Unhandled exceptions
  - Added try-catch blocks in critical paths
  - Improved error messages
  - Added detailed logging
- [ ] Error recovery
  - Automatic retries
  - State recovery
  - Error notifications
- [ ] Queue processing errors
  - Handle failed message processing
  - Implement retry mechanism
  - Add dead letter queue

## 6. Testing
- [ ] Test coverage
  - Missing test cases
  - Edge cases
  - Integration tests
- [ ] Test data
  - Test data management
  - Data cleanup
  - Mock data
- [x] Debug tools
  - Added test_agent.py for message processing testing
  - Added detailed logging
  - Added response structure inspection

## 7. Documentation
- [ ] API documentation
  - Endpoint documentation
  - Request/response examples
  - Error codes
- [ ] Code documentation
  - Function documentation
  - Class documentation
  - Module documentation

## 8. Core Block Management ✅
- [x] Core block attachment/detachment
  - Location: `core/queue.py` in message processing
  - Issue: Core block not properly attached/detached for each message
  - Impact: 
    - Potential memory leaks
    - Inconsistent message processing
    - Possible state corruption between messages
  - Fix: ✅
    - Ensure core block is attached before processing each message
    - Verify core block is properly detached after processing
    - Add logging for core block state changes
    - Implement proper error handling for attachment failures
  - Priority: High (affects message processing reliability)
  - Status: Completed
  - Implementation Details:
    - Proper block lifecycle management in QueueProcessor
    - Robust error handling with nested try/catch blocks
    - Block detachment guaranteed in finally blocks
    - Detailed logging for block operations
    - Block IDs stored and retrieved reliably from database
    - No reliance on unreliable client.blocks.list()
    - Each message processing has independent block cycle
    - Multiple safeguards against state corruption

## 9. Redundant Context Management
- [x] Remove redundant conversation history implementation
  - Location: `database/models.py`, `database/operations.py`
  - Issue: Middleware implements its own conversation history limit which is redundant with Letta's context management
  - Impact:
    - Unnecessary database field and code complexity
    - Potential confusion about where context is actually managed
    - No actual effect on conversation context (managed by Letta)
  - Fix:
    - Removed `conversation_history_limit` field from database schema
    - Removed related code from operations
    - Updated documentation to clarify that Letta manages context through core blocks
    - Ensured core block attachment/detachment is properly implemented
  - Priority: Medium (cleanup task)
  - Dependencies:
    - Core Block Management fix
    - Database schema migration 