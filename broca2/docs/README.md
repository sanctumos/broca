# Broca

A message processing system with flexible modes and comprehensive status tracking.

## Features

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

### Environment Variables

Required variables:
- `TELEGRAM_API_ID`: Your Telegram API ID
- `TELEGRAM_API_HASH`: Your Telegram API hash
- `TELEGRAM_PHONE`: Phone number for the Telegram client
- `LETTA_API_ENDPOINT`: Endpoint URL for the Letta service
- `LETTA_API_KEY`: API key for the Letta service
- `DEBUG_MODE`: Enable/disable debug mode (default: false)

Optional variables:
- `QUEUE_REFRESH`: Queue refresh interval in seconds (default: 5)
- `MAX_RETRIES`: Maximum retry attempts for failed messages (default: 3)
- `MESSAGE_MODE`: Processing mode (live/echo/listen, default: live)

### Recent Improvements

1. **Core Block Management**
   - Proper attachment/detachment cycle
   - Reliable block ID storage
   - Error handling and cleanup

2. **Message Formatting**
   - Standardized format across components
   - Emoji-based logging system
   - Improved metadata handling

3. **Client Architecture**
   - Singleton Letta client implementation
   - Standardized environment variables
   - Improved configuration management

4. **Status Tracking**
   - Comprehensive status system
   - Mode-specific status workflows
   - Status history and monitoring

## Development Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in required values:
   ```
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   TELEGRAM_PHONE=your_phone_number
   DEBUG_MODE=true  # for testing
   ```
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `python main.py`

## Project Structure

```
broca/
├── core/
│   ├── agent.py       # Agent client implementation
│   └── queue.py       # Queue processing logic
├── database/
│   ├── models.py      # Database models and schema
│   └── operations/
│       ├── shared.py  # Shared database operations
│       ├── users.py   # User-related operations
│       ├── messages.py # Message-related operations
│       └── queue.py   # Queue-related operations
├── telegram/
│   ├── client.py      # Telegram client setup
│   └── handlers.py    # Message handling logic
├── web/
│   └── app.py         # Flask dashboard application
├── templates/         # Dashboard HTML templates
├── static/           # Static assets for dashboard
└── main.py           # Application entry point
```

## TODO List

1. **Queue Management**
   - [x] Implement basic status system
   - [x] Add status transition validation
   - [x] Implement basic status history tracking
   - [ ] Add comprehensive queue item archival system
   - [ ] Improve status transition logging
   - [ ] Add queue cleanup automation

2. **Dashboard Enhancements**
   - [x] Add basic message search functionality
   - [ ] Implement advanced conversation filtering (user/date)
   - [ ] Add conversation export functionality
   - [x] Add basic status-based queue filtering
   - [x] Implement basic status transition visualization
   - [ ] Add advanced analytics dashboard

3. **Monitoring & Logging**
   - [x] Add emoji-based logging system
   - [ ] Add performance monitoring
   - [ ] Create alert system for queue backlogs
   - [x] Add basic status transition monitoring
   - [ ] Implement comprehensive monitoring dashboard
   - [ ] Add system health metrics

4. **Security**
   - [ ] Add authentication for dashboard access
   - [ ] Implement role-based access control
   - [x] Basic API key management
   - [ ] Add session management
   - [ ] Implement audit logging
   - [ ] Add security headers and CSRF protection

5. **Deployment**
   - [ ] Create backup/restore procedures
   - [x] Add basic health check endpoints
   - [ ] Add comprehensive status monitoring endpoints
   - [ ] Create deployment documentation
   - [ ] Add container support
   - [ ] Create automated deployment scripts 