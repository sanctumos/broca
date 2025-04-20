# Schema Migration Documentation

## Current Schema (v1)

### Users Table
Currently tied directly to Telegram users:
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,  -- Telegram user ID
    username TEXT,                -- Telegram username
    first_name TEXT,             -- Telegram first name
    last_active TEXT,            -- Last activity timestamp
    message_count INTEGER DEFAULT 0
)
```

### Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,             -- References Telegram user_id
    role TEXT,                   -- Message role (user/assistant)
    message TEXT,                -- Message content
    timestamp TEXT,              -- Message timestamp
    processed INTEGER DEFAULT 0,  -- Processing flag
    agent_response TEXT          -- Agent's response
)
```

### Queue Table
```sql
CREATE TABLE queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,             -- References Telegram user_id
    message_id INTEGER,          -- References messages.id
    status TEXT,                 -- pending/processing/done/failed
    attempts INTEGER DEFAULT 0,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
)
```

## Planned Schema (v2)

### Master Users Table (NEW)
```sql
CREATE TABLE letta_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_active TEXT,
    -- Letta-agent specific metadata
    agent_preferences TEXT,       -- JSON field for agent preferences
    conversation_history_limit INTEGER DEFAULT 10,
    custom_instructions TEXT,
    is_active BOOLEAN DEFAULT true
)
```

### Platform Profiles Table (NEW)
```sql
CREATE TABLE platform_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    letta_user_id INTEGER,       -- References letta_users.id
    platform TEXT,               -- 'telegram', 'discord', 'email', etc.
    platform_user_id TEXT,       -- Platform-specific user ID
    username TEXT,               -- Platform username
    display_name TEXT,           -- Platform display/first name
    metadata TEXT,               -- JSON field for platform-specific data
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_active TEXT,
    UNIQUE(platform, platform_user_id)
)
```

### Updated Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    letta_user_id INTEGER,       -- Now references letta_users.id
    platform_profile_id INTEGER, -- References platform_profiles.id
    role TEXT,                   -- Message role (user/assistant)
    message TEXT,                -- Message content
    timestamp TEXT,              -- Message timestamp
    processed INTEGER DEFAULT 0,  -- Processing flag
    agent_response TEXT          -- Agent's response
)
```

### Updated Queue Table
```sql
CREATE TABLE queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    letta_user_id INTEGER,       -- Now references letta_users.id
    message_id INTEGER,          -- References messages.id
    status TEXT,                 -- pending/processing/done/failed
    attempt_count INTEGER DEFAULT 0,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
)
```

## Migration Plan

1. Drop existing tables (since we're not preserving data):
   ```sql
   DROP TABLE IF EXISTS users;
   DROP TABLE IF EXISTS messages;
   DROP TABLE IF EXISTS queue;
   ```

2. Create new schema:
   - Create `letta_users` table
   - Create `platform_profiles` table
   - Create updated `messages` table
   - Create updated `queue` table

3. Update application code:
   - Modify Telegram handler to create/update master user records
   - Update database operations to work with new schema
   - Update dashboard queries to join across new tables
   - Update queue processor to use new user references

## Benefits of New Schema

1. **Platform Agnostic**: Master user records are independent of communication platforms

2. **Extensible**: 
   - Easy to add new platforms via platform_profiles
   - Flexible metadata storage for both users and platforms
   - Agent preferences stored at user level

3. **Better Data Organization**:
   - Clear separation between user identity and platform presence
   - Platform-specific data isolated to profiles
   - Easier to manage cross-platform user experience

4. **Future Ready**:
   - Prepared for Letta-agent specific features
   - Ready for multi-platform support
   - Supports user preference management 