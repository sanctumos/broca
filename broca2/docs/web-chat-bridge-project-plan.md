# Broca2 Web Chat Bridge - Project Plan

## Project Overview

**Objective:** Create a secure, pull-based web chat integration for Broca2 agents that eliminates security risks by keeping the Sanctum server isolated from public internet exposure.

**Architecture:** API-first design with two separate components:
1. **PHP Web Chat Bridge** - API-first design that handles web chat sessions and message routing
2. **Broca2 Web Chat Plugin** - Plugin that polls the PHP API and integrates with Broca2

---

## 🎯 Project Goals

### Primary Goals
1. **Zero New Attack Surface:** No new inbound ports or public exposure on Sanctum server
2. **Frictionless User Experience:** Web chat widget accessible without Telegram or SaaS requirements
3. **API-First Design:** Clean, well-defined API that the plugin can easily consume
4. **Easy Maintenance:** Simple PHP API that's easy to audit, rate-limit, and replace

### Success Criteria
- [ ] PHP API is well-designed and documented
- [ ] Web chat widget functions seamlessly for end users
- [ ] Broca2 plugin polls PHP API successfully
- [ ] Message routing works correctly between web chat and agents
- [ ] No new inbound ports on Sanctum server
- [ ] Session management handles multiple concurrent users
- [ ] Rate limiting prevents abuse
- [ ] Error handling is robust and graceful

---

## 🏗️ System Architecture

### Component Overview

```
┌─────────────────┐    HTTP Polling    ┌─────────────────┐
│   Broca2 Plugin │ ◄───────────────── │   PHP Web Chat  │
│   (web_chat)    │                    │   Bridge        │
│                 │    HTTP POST       │                 │
│                 │ ──────────────────► │                 │
└─────────────────┘                    └─────────────────┘
         │                                      │
         │                                      │
         ▼                                      ▼
┌─────────────────┐                    ┌─────────────────┐
│   Broca2 Core   │                    │   Web Chat      │
│   (Queue/Agent) │                    │   Widget        │
└─────────────────┘                    └─────────────────┘
```

### Data Flow
1. **User Input:** Web chat widget sends message to PHP Bridge
2. **Message Storage:** PHP Bridge stores message in local database
3. **Plugin Polling:** Broca2 plugin polls PHP Bridge for new messages
4. **Agent Processing:** Broca2 processes message through existing queue system
5. **Response Delivery:** Plugin POSTs response back to PHP Bridge
6. **User Display:** Web chat widget displays response to user

---

## 📋 Implementation Plan

## Part 1: PHP Web Chat Bridge (API-First Design)

### 1.1 API Design Philosophy

**API-First Principles:**
- Design the API contract first, before any implementation
- Clear, RESTful endpoints with consistent response formats
- Comprehensive error handling and status codes
- Authentication and rate limiting built into the design
- Documentation-driven development

### 1.2 API Contract Definition

**Note:** The actual API implementation has been completed and documented. The following is the final API specification that the Broca2 plugin will consume.

#### **Final API Documentation**

The complete API documentation is available at: `broca2/docs/web-chat-bridge-api-documentation.md`

**Key API Details:**
- **Base URL:** `http://localhost:8000/api/v1/index.php`
- **Authentication:** Bearer token (API key for plugin, admin password for admin endpoints)
- **Response Format:** Consistent JSON with `success`, `message`, `timestamp`, and `data` fields

#### **Plugin-Relevant Endpoints**

**GET /api/inbox** (Plugin polls for messages)
```json
{
  "endpoint": "/api/inbox",
  "method": "GET",
  "description": "Retrieve unprocessed messages for Broca2 plugin",
  "headers": {
    "Authorization": "Bearer {api_key}",
    "Content-Type": "application/json"
  },
  "query_params": {
    "limit": "integer (default: 50)",
    "offset": "integer (default: 0)",
    "since": "timestamp (optional)"
  },
  "response": {
    "success": true,
    "messages": [
      {
        "id": "integer",
        "session_id": "string",
        "message": "string",
        "timestamp": "ISO 8601 timestamp",
        "metadata": "object (optional)"
      }
    ],
    "pagination": {
      "total": "integer",
      "limit": "integer",
      "offset": "integer",
      "has_more": "boolean"
    }
  },
  "error_response": {
    "success": false,
    "error": "string",
    "code": "integer"
  }
}
```

**POST /api/outbox**
```json
{
  "endpoint": "/api/outbox",
  "method": "POST",
  "description": "Send agent response back to web chat",
  "headers": {
    "Authorization": "Bearer {api_key}",
    "Content-Type": "application/json"
  },
  "body": {
    "session_id": "string (required)",
    "response": "string (required)",
    "message_id": "integer (optional)",
    "timestamp": "ISO 8601 timestamp (optional)"
  },
  "response": {
    "success": true,
    "message": "Response sent successfully",
    "session_id": "string"
  },
  "error_response": {
    "success": false,
    "error": "string",
    "code": "integer"
  }
}
```

**POST /api/messages**
```json
{
  "endpoint": "/api/messages",
  "method": "POST",
  "description": "Receive message from web chat widget",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "session_id": "string (required)",
    "message": "string (required)",
    "timestamp": "ISO 8601 timestamp (optional)"
  },
  "response": {
    "success": true,
    "message": "Message received",
    "message_id": "integer"
  },
  "error_response": {
    "success": false,
    "error": "string",
    "code": "integer"
  }
}
```

**GET /api/responses/{session_id}**
```json
{
  "endpoint": "/api/responses/{session_id}",
  "method": "GET",
  "description": "Get responses for a specific session",
  "query_params": {
    "since": "timestamp (optional)"
  },
  "response": {
    "success": true,
    "responses": [
      {
        "id": "integer",
        "response": "string",
        "timestamp": "ISO 8601 timestamp"
      }
    ]
  }
}
```

**GET /api/sessions**
```json
{
  "endpoint": "/api/sessions",
  "method": "GET",
  "description": "List active sessions (admin only)",
  "headers": {
    "Authorization": "Bearer {admin_key}"
  },
  "query_params": {
    "limit": "integer (default: 50)",
    "offset": "integer (default: 0)",
    "active": "boolean (optional)"
  },
  "response": {
    "success": true,
    "sessions": [
      {
        "id": "string",
        "created_at": "ISO 8601 timestamp",
        "last_active": "ISO 8601 timestamp",
        "message_count": "integer",
        "metadata": "object"
      }
    ],
    "pagination": {
      "total": "integer",
      "limit": "integer",
      "offset": "integer",
      "has_more": "boolean"
    }
  }
}
```

### 1.3 Application Structure
**Location:** `~/sanctum/broca2/web-chat-bridge/`

**Files to Create:**
```
web-chat-bridge/
├── api/
│   ├── inbox.php      # GET - Broca2 plugin polls for new messages
│   ├── outbox.php     # POST - Broca2 plugin sends agent responses
│   ├── messages.php   # POST - Web widget sends messages
│   ├── responses.php  # GET - Web widget gets responses
│   └── sessions.php   # GET - Admin session management
├── config/
│   ├── database.php   # Database configuration
│   └── settings.php   # API settings and rate limits
├── includes/
│   ├── database.php   # Database operations
│   ├── auth.php       # Authentication and rate limiting
│   ├── api_response.php # Standardized API responses
│   └── utils.php      # Utility functions
├── web/
│   ├── chat.php       # Web chat widget interface
│   ├── admin.php      # Admin interface for monitoring
│   └── assets/
│       ├── chat.js    # Frontend JavaScript
│       └── style.css  # Chat widget styling
├── docs/
│   ├── api.md         # API documentation
│   └── examples.md    # API usage examples
└── database/
    └── schema.sql     # Database schema
```

### 1.4 Database Schema

```sql
-- Web chat sessions (separate from Broca2, for temporary session management)
CREATE TABLE web_chat_sessions (
    id VARCHAR(64) PRIMARY KEY,
    uid VARCHAR(16) UNIQUE,  -- Unique identifier for web chat users
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_active TEXT DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),   -- IP address for potential user matching
    metadata TEXT
);

-- Web chat messages (temporary storage before processing by Broca2)
CREATE TABLE web_chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(64),
    message TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    processed INTEGER DEFAULT 0,
    broca_message_id INTEGER NULL,  -- Links to Broca2 messages table when processed
    FOREIGN KEY (session_id) REFERENCES web_chat_sessions(id)
);

-- Web chat responses (agent responses sent back to web widget)
CREATE TABLE web_chat_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(64),
    response TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    message_id INTEGER NULL,  -- Links to original message
    FOREIGN KEY (session_id) REFERENCES web_chat_sessions(id),
    FOREIGN KEY (message_id) REFERENCES web_chat_messages(id)
);

-- Rate limiting table
CREATE TABLE rate_limits (
    ip_address VARCHAR(45),
    endpoint VARCHAR(50),
    count INTEGER DEFAULT 1,
    window_start TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ip_address, endpoint)
);
```

### 1.5 Security Features

#### Authentication
- **API Key Authentication:** Required for plugin communication
- **Admin Key Authentication:** Separate key for admin endpoints
- **Session-based Authentication:** For web widget users

#### Rate Limiting
- **Per-IP Limits:** Prevent abuse from individual IPs
- **Per-Endpoint Limits:** Different limits for different endpoints
- **Sliding Window:** Rolling time window for rate limiting

#### Input Validation
- **Message Sanitization:** Clean all user input
- **Session Validation:** Validate session IDs
- **Content Length Limits:** Prevent oversized messages

#### CORS Configuration
```php
// Proper CORS headers for web widget
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
```

### 1.6 User Identification System

#### **Problem Statement**
Web chat visitors don't have persistent identifiers like Telegram users. We need a system to:
1. **Generate unique IDs** for new web visitors
2. **Track returning users** across sessions
3. **Maintain conversation continuity** for the same user

#### **Solution: PHP-Generated UID System**

**PHP Bridge UID Generation:**
```php
// includes/utils.php
function generate_web_chat_uid(): string {
    // Generate a 16-character hex UID
    return bin2hex(random_bytes(8));
}

function get_or_create_web_chat_user($session_id, $ip_address = null): array {
    // Check if session already has a UID
    $stmt = $pdo->prepare("SELECT uid FROM web_chat_sessions WHERE id = ?");
    $stmt->execute([$session_id]);
    $session = $stmt->fetch();
    
    if ($session && $session['uid']) {
        return ['uid' => $session['uid'], 'is_new' => false];
    }
    
    // Generate new UID for this session
    $uid = generate_web_chat_uid();
    
    // Update session with UID
    $stmt = $pdo->prepare("UPDATE web_chat_sessions SET uid = ? WHERE id = ?");
    $stmt->execute([$uid, $session_id]);
    
    return ['uid' => $uid, 'is_new' => true];
}
```

**Updated Database Schema:**
```sql
-- Add UID field to web_chat_sessions
ALTER TABLE web_chat_sessions ADD COLUMN uid VARCHAR(16) UNIQUE;

-- Add index for efficient UID lookups
CREATE INDEX idx_web_chat_sessions_uid ON web_chat_sessions(uid);

-- Add IP tracking for potential future user matching
ALTER TABLE web_chat_sessions ADD COLUMN ip_address VARCHAR(45);
```

**Updated API Contract:**
```json
{
  "endpoint": "/api/messages",
  "method": "POST", 
  "description": "Receive message from web chat widget",
  "body": {
    "session_id": "string (required)",
    "message": "string (required)",
    "timestamp": "ISO 8601 timestamp (optional)"
  },
  "response": {
    "success": true,
    "message": "Message received",
    "message_id": "integer",
    "uid": "string (16-char hex UID)",
    "is_new_user": "boolean"
  }
}
```

### 1.7 Web Chat Widget (Updated)

```javascript
class WebChatWidget {
    constructor(config) {
        this.apiUrl = config.apiUrl;
        this.sessionId = this.generateSessionId();
        this.userUid = null;  // Will be set by PHP
        this.messageQueue = [];
        this.isConnected = false;
        
        this.init();
    }
    
    async init() {
        await this.createSession();
        this.startPolling();
        this.bindEvents();
    }
    
    async sendMessage(text) {
        const message = {
            session_id: this.sessionId,
            message: text,
            timestamp: new Date().toISOString()
        };
        
        try {
            const response = await fetch(`${this.apiUrl}/api/messages`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(message)
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Store UID if this is a new user
                if (data.uid && !this.userUid) {
                    this.userUid = data.uid;
                    console.log(`New user UID: ${this.userUid}`);
                }
                
                this.addMessageToUI('user', text);
            }
        } catch (error) {
            console.error('Failed to send message:', error);
        }
    }
    
    generateSessionId() {
        // Generate a session ID for this browser session
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }
    
    startPolling() {
        setInterval(async () => {
            await this.checkForResponses();
        }, 2000);
    }
    
    async checkForResponses() {
        try {
            const response = await fetch(`${this.apiUrl}/api/responses/${this.sessionId}`);
            const data = await response.json();
            
            if (data.success && data.responses) {
                for (const response of data.responses) {
                    this.addMessageToUI('agent', response.response);
                }
            }
        } catch (error) {
            console.error('Failed to check responses:', error);
        }
    }
}
```

---

## Part 2: Broca2 Web Chat Plugin

### 2.1 Plugin Structure
**Location:** `broca2/plugins/web_chat/`

**Files to Create:**
```
plugins/web_chat/
├── __init__.py
├── plugin.py          # Main plugin class (follows Plugin interface)
├── settings.py        # Plugin settings
├── api_client.py      # HTTP client for PHP Bridge
├── message_handler.py # Message handling logic
└── tests/
    ├── __init__.py
    ├── test_plugin.py
    ├── test_api_client.py
    └── test_message_handler.py
```

### 2.2 Plugin Implementation (Following plugin_development.md)

```python
"""Web chat plugin for Broca2."""
import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from plugins import Plugin, Event, EventType
from database.models import PlatformProfile
from database.operations.messages import update_message_status
from .settings import WebChatSettings
from .api_client import WebChatAPIClient
from .message_handler import WebChatMessageHandler

logger = logging.getLogger(__name__)

class WebChatPlugin(Plugin):
    """Web chat plugin that polls PHP Bridge for messages."""
    
    def __init__(self):
        """Initialize the web chat plugin."""
        self.settings = WebChatSettings.from_env()
        self.api_client = WebChatAPIClient(self.settings)
        self.message_handler = WebChatMessageHandler()
        self.polling_interval = self.settings.polling_interval
        self._polling_task = None
        self._running = False
    
    def get_name(self) -> str:
        """Get the plugin name.
        
        Returns:
            str: Plugin name
        """
        return "web_chat"
    
    def get_platform(self) -> str:
        """Get the platform name this plugin handles.
        
        Returns:
            str: Platform name
        """
        return "web_chat"
    
    def get_message_handler(self) -> WebChatMessageHandler:
        """Get the message handler for this platform.
        
        Returns:
            WebChatMessageHandler: The message handler instance
        """
        return self.message_handler
    
    def get_settings(self) -> Optional[Dict[str, Any]]:
        """Get the plugin's settings.
        
        Returns:
            Optional[Dict[str, Any]]: Plugin settings
        """
        return self.settings.to_dict()
    
    def validate_settings(self, settings: WebChatSettings) -> bool:
        """Validate plugin settings.
        
        Args:
            settings: Settings to validate
            
        Returns:
            bool: True if settings are valid, False otherwise
        """
        try:
            if not settings.api_url:
                return False
            if not settings.api_key:
                return False
            return True
        except Exception as e:
            logger.error(f"Invalid settings: {e}")
            return False
    
    async def start(self) -> None:
        """Start the plugin.
        
        This method should:
        - Initialize any required resources
        - Set up event handlers
        - Start any background tasks
        """
        try:
            logger.info("🔄 Starting Web Chat plugin...")
            
            # Initialize API client
            await self.api_client.initialize()
            
            # Start polling task
            self._polling_task = asyncio.create_task(self._poll_messages())
            self._running = True
            
            logger.info("✅ Web Chat plugin started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Web Chat plugin: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the plugin.
        
        This method should:
        - Clean up resources
        - Stop background tasks
        - Close any connections
        """
        try:
            logger.info("🛑 Stopping Web Chat plugin...")
            
            self._running = False
            
            if self._polling_task:
                self._polling_task.cancel()
                try:
                    await self._polling_task
                except asyncio.CancelledError:
                    pass
            
            # Clean up API client
            await self.api_client.close()
            
            logger.info("✅ Web Chat plugin stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Error stopping Web Chat plugin: {e}")
            raise
    
    async def _poll_messages(self) -> None:
        """Poll PHP Bridge for new messages."""
        while self._running:
            try:
                messages = await self.api_client.get_new_messages()
                
                for message in messages:
                    await self._process_message(message)
                    
            except Exception as e:
                logger.error(f"❌ Error polling web chat messages: {e}")
            
            await asyncio.sleep(self.polling_interval)
    
    async def _process_message(self, message: Dict[str, Any]) -> None:
        """Process a web chat message through Broca2 queue."""
        try:
            # Use the message handler to process the message
            result = await self.message_handler.process_incoming_message(message)
            logger.info(f"📥 Queued web chat message {result['message_id']} for processing")
            
        except Exception as e:
            logger.error(f"❌ Failed to process web chat message: {e}")
            raise
    
    async def _handle_response(self, response: str, profile: PlatformProfile) -> None:
        """Handle agent response for web chat messages.
        
        This method is called by the PluginManager when an agent response
        needs to be sent back to the web chat platform.
        """
        try:
            # Find the web chat session for this platform profile
            session_id = profile.platform_user_id  # In web_chat platform, this is the session_id
            
            # Process outgoing message through message handler
            await self.message_handler.process_outgoing_message(session_id, response)
            
            # Send response back to PHP Bridge
            success = await self.api_client.send_response(session_id, response)
            
            if success:
                logger.info(f"📤 Sent response to web chat session {session_id}")
            else:
                logger.error(f"❌ Failed to send response to web chat session {session_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send response to web chat: {e}")
            raise
```

### 2.3 Message Handler Implementation

```python
"""Message handler for the web chat plugin."""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from runtime.core.message import MessageFormatter
from database.operations.users import get_or_create_platform_profile
from database.operations.messages import insert_message, update_message_status
from database.operations.queue import add_to_queue

logger = logging.getLogger(__name__)

class WebChatMessageHandler:
    """Handles incoming and outgoing messages for the web chat plugin."""

    def __init__(self):
        """Initialize the message handler."""
        self.formatter = MessageFormatter()
        logger.info("Initialized WebChatMessageHandler")
    
    async def process_incoming_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming message from the PHP Bridge.
        
        Args:
            message_data: The incoming message data
            
        Returns:
            dict: Message processing result
        """
        try:
            # Extract message data
            session_id = message_data['session_id']
            message_text = message_data['message']
            timestamp = message_data.get('timestamp', datetime.now().isoformat())
            
            # Extract UID if available (PHP Bridge provides this)
            uid = message_data.get('uid')
            if not uid:
                # Fallback: use session_id as UID (for backward compatibility)
                uid = session_id

            # Sanitize inputs
            sanitized_message = self.formatter.sanitize_text(message_text)
            sanitized_uid = self.formatter.sanitize_text(uid)
            
            # Get or create user profile using UID as platform_user_id
            # This ensures the same web visitor gets the same Broca2 user profile
            profile, letta_user = await get_or_create_platform_profile(
                platform="web_chat",
                platform_user_id=sanitized_uid,  # Use UID instead of session_id
                username=f"web_chat_{sanitized_uid[:8]}",
                display_name=f"Web Chat User {sanitized_uid[:8]}"
            )
            
            # Insert message
            message_id = await insert_message(
                letta_user_id=letta_user.id,
                platform_profile_id=profile.id,
                role="user",
                message=sanitized_message,
                timestamp=timestamp
            )
            
            # Add to queue
            await add_to_queue(letta_user.id, message_id)
            
            return {
                "message_id": message_id,
                "letta_user_id": letta_user.id,
                "platform_profile_id": profile.id,
                "session_id": session_id,
                "uid": uid,
                "timestamp": timestamp
            }
        except Exception as e:
            logger.error(f"Error processing incoming message: {e}")
            raise
    
    async def process_outgoing_message(self, session_id: str, response: str) -> None:
        """Process an outgoing message to the PHP Bridge.
        
        Args:
            session_id: The web chat session ID
            response: The response to send
        """
        try:
            # This will be handled by the API client
            # The message handler just logs the action
            logger.info(f"Processing outgoing message for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error processing outgoing message: {e}")
            raise

    async def update_message_status(self, message_id: int, status: str) -> None:
        """Update the status of a message.
        
        Args:
            message_id: The message ID to update
            status: The new status
        """
        try:
            await update_message_status(message_id, status)
            logger.info(f"Updated message {message_id} status to {status}")
        except Exception as e:
            logger.error(f"Error updating message status: {e}")
            raise

    def format_message(self, message: str) -> str:
        """Format a message for web chat.
        
        Args:
            message: The message to format
            
        Returns:
            str: The formatted message
        """
        return self.formatter.format_message(message)
```

### 2.4 API Client Implementation

```python
"""HTTP client for PHP Bridge API."""
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from .settings import WebChatSettings

logger = logging.getLogger(__name__)

class WebChatAPIClient:
    """HTTP client for communicating with PHP Bridge API."""
    
    def __init__(self, settings: WebChatSettings):
        """Initialize the API client."""
        self.settings = settings
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self) -> None:
        """Initialize the HTTP session."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.settings.timeout)
        )
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
    
    async def get_new_messages(self) -> List[Dict[str, Any]]:
        """Get new messages from PHP Bridge.
        
        Returns:
            List[Dict[str, Any]]: List of new messages with UIDs
        """
        headers = {
            'Authorization': f'Bearer {self.settings.api_key}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'limit': 50,
            'offset': 0
        }
        
                        async with self.session.get(
                    f"{self.settings.api_url}/api/v1/?action=inbox",
                    headers=headers,
                    params=params
                ) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('success'):
                    messages = data.get('data', {}).get('messages', [])
                    
                    # Ensure each message has a UID
                    for message in messages:
                        if 'uid' not in message:
                            # Fallback: use session_id as UID
                            message['uid'] = message.get('session_id', 'unknown')
                    
                    return messages
                else:
                    logger.error(f"API error: {data.get('error')}")
                    return []
            else:
                logger.error(f"Failed to get messages: {response.status}")
                return []
    
    async def send_response(self, session_id: str, response: str) -> bool:
        """Send agent response to PHP Bridge.
        
        Args:
            session_id: Web chat session ID
            response: Agent response message
            
        Returns:
            bool: True if successful, False otherwise
        """
        headers = {
            'Authorization': f'Bearer {self.settings.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'session_id': session_id,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        
                        async with self.session.post(
                    f"{self.settings.api_url}/api/v1/?action=outbox",
                    headers=headers,
                    json=data
                ) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data.get('success', False)
            else:
                logger.error(f"Failed to send response: {response.status}")
                return False
```

### 2.4 Configuration and Environment Variables

#### **Environment Variables Required**

The web chat plugin follows the same configuration pattern as existing Broca2 plugins. Add these variables to your Broca2 instance's `.env` file:

```bash
# Web Chat Plugin Configuration
WEB_CHAT_API_URL=http://localhost:8000
WEB_CHAT_API_KEY=api_h8hcbfg4uiqfz6sjy1h6ri

# Optional settings (with defaults)
WEB_CHAT_POLLING_INTERVAL=5
WEB_CHAT_MAX_RETRIES=3
WEB_CHAT_TIMEOUT=30
```

#### **Configuration Variables**

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `WEB_CHAT_API_URL` | ✅ Yes | - | PHP Bridge API endpoint |
| `WEB_CHAT_API_KEY` | ✅ Yes | - | Authentication key for PHP Bridge |
| `WEB_CHAT_POLLING_INTERVAL` | ❌ No | `5` | Seconds between API polls |
| `WEB_CHAT_MAX_RETRIES` | ❌ No | `3` | HTTP request retry attempts |
| `WEB_CHAT_TIMEOUT` | ❌ No | `30` | HTTP request timeout (seconds) |

#### **PHP Bridge Configuration**

The PHP Bridge also requires its own configuration:

```bash
# PHP Bridge Configuration (.env file in web-chat-bridge directory)
DB_PATH=/path/to/web_chat.db
API_KEY=your-secure-api-key-here
ADMIN_KEY=your-admin-key-here
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### 2.5 Settings Implementation (Following Established Pattern)

```python
"""Settings for web chat plugin."""
from dataclasses import dataclass
from typing import Optional
from common.config import get_env_var

@dataclass
class WebChatSettings:
    """Settings for web chat plugin."""
    api_url: str
    api_key: str
    polling_interval: int = 5
    max_retries: int = 3
    timeout: int = 30

    def __post_init__(self):
        """Validate settings after initialization."""
        if not self.api_url:
            raise ValueError("API URL is required")
        
        if not self.api_key:
            raise ValueError("API key is required")
        
        if not isinstance(self.polling_interval, int):
            self.polling_interval = int(self.polling_interval)
        
        if not isinstance(self.max_retries, int):
            self.max_retries = int(self.max_retries)
        
        if not isinstance(self.timeout, int):
            self.timeout = int(self.timeout)

    @classmethod
    def from_env(cls) -> 'WebChatSettings':
        """Create settings from environment variables.

        Returns:
            WebChatSettings: Settings loaded from environment
        """
        # Get API URL (required)
        api_url = get_env_var("WEB_CHAT_API_URL", required=True)

        # Get API key (required)
        api_key = get_env_var("WEB_CHAT_API_KEY", required=True)

        # Get polling interval (optional)
        polling_interval = get_env_var("WEB_CHAT_POLLING_INTERVAL", default="5")

        # Get max retries (optional)
        max_retries = get_env_var("WEB_CHAT_MAX_RETRIES", default="3")

        # Get timeout (optional)
        timeout = get_env_var("WEB_CHAT_TIMEOUT", default="30")

        return cls(
            api_url=api_url,
            api_key=api_key,
            polling_interval=int(polling_interval),
            max_retries=int(max_retries),
            timeout=int(timeout)
        )

    def to_dict(self) -> dict:
        """Convert settings to dictionary.

        Returns:
            dict: Dictionary representation of settings
        """
        return {
            "api_url": self.api_url,
            "api_key": self.api_key,
            "polling_interval": self.polling_interval,
            "max_retries": self.max_retries,
            "timeout": self.timeout
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WebChatSettings':
        """Create settings from dictionary.

        Args:
            data: Dictionary containing settings

        Returns:
            WebChatSettings: Settings loaded from dictionary
        """
        if "api_url" not in data:
            raise ValueError("API URL is required")
        
        if "api_key" not in data:
            raise ValueError("API key is required")

        return cls(
            api_url=data["api_url"],
            api_key=data["api_key"],
            polling_interval=data.get("polling_interval", 5),
            max_retries=data.get("max_retries", 3),
            timeout=data.get("timeout", 30)
        )
```

---

## 🔧 Development Tasks

### Week 0: Setup and Configuration
- [ ] Set up PHP Bridge environment and dependencies
- [ ] Configure Broca2 environment variables for web chat plugin
- [ ] Set up separate databases (Broca2 and PHP Bridge)
- [ ] Generate secure API keys for authentication
- [ ] Test basic connectivity between components

### Week 1: PHP API Design and Implementation
- [ ] Design API contract and endpoints
- [ ] Create database schema
- [ ] Implement core API endpoints
- [ ] Add authentication and rate limiting
- [ ] Create standardized API responses
- [ ] Write API documentation

### Week 2: PHP Web Chat Widget and Admin
- [ ] Create web chat widget interface
- [ ] Implement real-time message updates
- [ ] Add admin monitoring interface
- [ ] Create styling and animations
- [ ] Add session management

### Week 3: Broca2 Plugin Development
- [ ] Create plugin structure following plugin_development.md
- [ ] Implement Plugin interface methods
- [ ] Create API client to match PHP API
- [ ] Add message processing logic
- [ ] Implement response handling
- [ ] Add comprehensive error handling

### Week 4: Integration and Testing
- [ ] Integrate plugin with Broca2
- [ ] Test end-to-end message flow
- [ ] Add comprehensive logging
- [ ] Performance optimization
- [ ] Security audit

---

## 🛡️ Security Considerations

### PHP Bridge Security
- **Rate Limiting:** Per-IP and per-endpoint limits
- **Authentication:** API key validation for plugin communication
- **Input Validation:** Sanitize all inputs
- **CORS:** Proper CORS configuration for web widget
- **HTTPS:** Enforce HTTPS for all communications

### Plugin Security
- **API Key Management:** Secure storage and rotation of API keys
- **Input Validation:** Validate all messages from PHP Bridge
- **Error Handling:** Graceful handling of API failures
- **Logging:** Comprehensive logging for security events

---

## 📊 Monitoring and Maintenance

### PHP Bridge Metrics
- **API Performance:** Response times and throughput
- **Error Rates:** Failed requests and error types
- **User Activity:** Active sessions and message volume
- **System Resources:** CPU, memory, and database usage

### Plugin Metrics
- **Polling Success Rate:** Track successful API calls
- **Message Processing:** Monitor message queue processing
- **Error Rates:** Track plugin errors and failures
- **Response Times:** Monitor API response times

---

## 🎯 Success Metrics

### Technical Metrics
- **Uptime:** 99.9% API availability
- **Response Time:** < 2 seconds for message processing
- **Error Rate:** < 1% error rate for API requests
- **Throughput:** Support 100+ concurrent users

### User Experience Metrics
- **Message Delivery:** 100% message delivery success rate
- **Response Time:** < 5 seconds for agent responses
- **User Satisfaction:** Positive user feedback
- **Adoption Rate:** Growing number of active users

---

## 🎉 Conclusion

This API-first approach provides a clear separation between the two components:

1. **PHP Web Chat Bridge** - Well-designed API that handles web chat sessions and provides a clean interface
2. **Broca2 Web Chat Plugin** - Plugin that consumes the API and integrates seamlessly with Broca2

The key success factors are:
1. **API-First Design:** Clean, well-documented API contract
2. **Security First:** Zero new attack surface on Sanctum
3. **Proven Patterns:** Following established plugin architecture
4. **User Experience:** Frictionless web chat access
5. **Maintainability:** Simple, auditable PHP API

By following this plan, we can create a robust, secure, and user-friendly web chat integration that enhances the Broca2 ecosystem without compromising security. 