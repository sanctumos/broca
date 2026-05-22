# Web Chat Plugin for Broca2

This plugin enables Broca2 to integrate with a PHP-based web chat bridge, allowing agents to respond to web chat messages through a pull-based architecture.

## Overview

The Web Chat Plugin polls a PHP API for new messages, processes them through the Broca2 agent system, and posts responses back to the web chat. This follows a pull-based architecture where the plugin actively polls for messages rather than exposing new ports on the Broca2 server.

## Features

- **Pull-based Architecture**: Plugin polls the PHP API for new messages
- **User Management**: Automatically creates Broca2 users and platform profiles for web chat visitors
- **Message Processing**: Integrates with Broca2's database and queue systems
- **Session Management**: Tracks web chat sessions and maintains conversation context
- **Error Handling**: Robust error handling with retry logic and exponential backoff
- **Configuration**: Environment-based configuration with validation

## Installation

1. Ensure the plugin is in the `broca2/plugins/web_chat/` directory
2. Set up environment variables (see Configuration section)
3. The plugin will be automatically loaded by Broca2's plugin system

## Configuration

### Environment Variables

Set the following environment variables for the plugin:

```bash
# Required
WEB_CHAT_API_URL=http://localhost:8000
WEB_CHAT_API_KEY=your_api_key_here

# Optional (with defaults)
WEB_CHAT_POLL_INTERVAL=5
WEB_CHAT_MAX_RETRIES=3
WEB_CHAT_RETRY_DELAY=10
WEB_CHAT_PLUGIN_NAME=web_chat
WEB_CHAT_PLATFORM_NAME=web_chat
WEB_CHAT_ENABLE_USER_CREATION=true
WEB_CHAT_ENABLE_MESSAGE_LOGGING=true
```

### Example .env Configuration

```env
# Web Chat Plugin Configuration
WEB_CHAT_API_URL=http://localhost:8000
WEB_CHAT_API_KEY=api_h8hcbfg4uiqfz6sjy1h6ri
WEB_CHAT_POLL_INTERVAL=5
WEB_CHAT_MAX_RETRIES=3
WEB_CHAT_RETRY_DELAY=10
```

## API Integration

The plugin communicates with a PHP-based web chat bridge API that provides the following endpoints:

- `GET /api/v1/?action=inbox` - Retrieve unprocessed messages
- `POST /api/v1/?action=outbox` - Submit agent responses

### Message Format

Incoming messages from the API:
```json
{
    "id": 1,
    "session_id": "session_abc123",
    "message": "Hello, how can you help me?",
    "timestamp": "2025-08-04T03:08:55.484Z",
    "uid": "2632f72d266e529c"
}
```

Outgoing responses to the API:
```json
{
    "session_id": "session_abc123",
    "response": "Hello! I'm here to help you. What can I assist you with today?"
}
```

## User Management

The plugin automatically creates Broca2 users and platform profiles for web chat visitors:

- **User Creation**: Creates `LettaUser` entries for web chat visitors
- **Platform Profiles**: Creates `PlatformProfile` entries with the PHP-generated UID
- **Session Tracking**: Maintains session context through the `session_id`
- **Metadata**: Stores additional context in message and profile metadata

## Database Integration

The plugin integrates with Broca2's existing database schema:

- **Messages**: Incoming and outgoing messages are stored in the `messages` table
- **Queue**: Messages are added to the processing queue for agent handling
- **Users**: Web chat visitors are created as `LettaUser` entries
- **Platform Profiles**: User profiles are created in the `platform_profiles` table

## Testing

Run the test script to verify plugin functionality:

```bash
cd broca2/plugins/web_chat
python test_plugin.py
```

## Usage

The plugin is designed to work automatically once configured:

1. **Startup**: Plugin automatically starts when Broca2 loads
2. **Polling**: Continuously polls the PHP API for new messages
3. **Processing**: Messages are processed through Broca2's agent system
4. **Responses**: Agent responses are posted back to the web chat

## Error Handling

The plugin includes robust error handling:

- **Connection Failures**: Retries with exponential backoff
- **API Errors**: Logs errors and continues polling
- **Message Processing**: Gracefully handles malformed messages
- **Duplicate Prevention**: Tracks processed messages to avoid duplicates

## Logging

The plugin uses Broca2's logging system:

- **Info**: Connection status, message processing, successful operations
- **Warning**: Invalid messages, configuration issues
- **Error**: API failures, processing errors, connection problems

## Security Considerations

- **API Key Authentication**: All API requests use Bearer token authentication
- **Input Validation**: Messages are sanitized before processing
- **Rate Limiting**: Respects API rate limits and implements backoff
- **No Core Changes**: Plugin doesn't modify Broca2's core infrastructure

## Troubleshooting

### Common Issues

1. **Connection Failed**: Check API URL and network connectivity
2. **Authentication Error**: Verify API key is correct
3. **No Messages**: Ensure PHP API is running and has messages
4. **Plugin Not Loading**: Check environment variables and plugin directory

### Debug Mode

Enable debug logging by setting the log level in Broca2's configuration.

## Development

The plugin follows Broca2's plugin development guidelines:

- **Plugin Interface**: Implements the required `Plugin` interface
- **Settings Management**: Uses dataclass-based settings with validation
- **Message Handler**: Separate message processing logic
- **Async Operations**: All I/O operations are asynchronous
- **Error Handling**: Comprehensive error handling and logging

## License

This plugin is part of the Broca2 project and follows the same licensing terms. 