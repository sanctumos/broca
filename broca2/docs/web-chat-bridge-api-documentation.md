# Web Chat Bridge API Documentation

## Overview

The Web Chat Bridge API provides a secure, RESTful interface for managing web chat sessions, messages, and responses. This API is designed to be consumed by the Broca2 web chat plugin and provides endpoints for both plugin communication and admin management.

**Base URL:** `http://localhost:8000/api/v1/`

**Authentication:** Bearer token authentication using API keys or admin passwords

---

## Authentication

### API Key Authentication
Used by the Broca2 plugin for accessing message endpoints.

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/v1/?action=inbox
```

### Admin Password Authentication
Used for admin endpoints and configuration management.

```bash
curl -H "Authorization: Bearer YOUR_ADMIN_PASSWORD" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/v1/?action=sessions
```

---

## Response Format

All API responses follow a consistent JSON format:

### Success Response
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        // Response data here
    }
}
```

### Error Response
```json
{
    "success": false,
    "error": "Error description",
    "timestamp": "2025-08-04T03:17:33+00:00"
}
```

---

## Plugin Endpoints

### 1. Get Unprocessed Messages (Inbox)

**Endpoint:** `GET /api/v1/?action=inbox`

**Description:** Retrieve unprocessed messages for Broca2 plugin processing.

**Authentication:** API Key required

**Query Parameters:**
- `limit` (optional): Number of messages to retrieve (default: 50, max: 100)
- `offset` (optional): Number of messages to skip (default: 0)
- `since` (optional): ISO timestamp to get messages since specific time

**cURL Example:**
```bash
curl -X GET \
     -H "Authorization: Bearer api_h8hcbfg4uiqfz6sjy1h6ri" \
     -H "Content-Type: application/json" \
     "http://localhost:8000/api/v1/?action=inbox&limit=10&offset=0"
```

**Response:**
```json
{
    "success": true,
    "message": "Messages retrieved successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "messages": [
            {
                "id": 1,
                "session_id": "session_abc123",
                "message": "Hello, how can you help me?",
                "timestamp": "2025-08-04T03:08:55.484Z",
                "uid": "2632f72d266e529c"
            }
        ],
        "pagination": {
            "total": 1,
            "limit": 10,
            "offset": 0,
            "has_more": false
        }
    }
}
```

### 2. Submit Response

**Endpoint:** `POST /api/v1/?action=outbox`

**Description:** Submit a response from Broca2 agent back to the web chat.

**Authentication:** API Key required

**Request Body:**
```json
{
    "session_id": "session_abc123",
    "response": "Hello! I'm here to help you. What can I assist you with today?"
}
```

**cURL Example:**
```bash
curl -X POST \
     -H "Authorization: Bearer api_h8hcbfg4uiqfz6sjy1h6ri" \
     -H "Content-Type: application/json" \
     -d '{
         "session_id": "session_abc123",
         "response": "Hello! I am here to help you. What can I assist you with today?"
     }' \
     "http://localhost:8000/api/v1/?action=outbox"
```

**Response:**
```json
{
    "success": true,
    "message": "Response sent successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "response_id": 1,
        "session_id": "session_abc123",
        "timestamp": "2025-08-04T03:17:33+00:00"
    }
}
```

### 3. Get Session Responses

**Endpoint:** `GET /api/v1/?action=responses`

**Description:** Retrieve responses for a specific session (used by web chat widget).

**Authentication:** None required (public endpoint)

**Query Parameters:**
- `session_id` (required): Session ID to get responses for

**cURL Example:**
```bash
curl -X GET \
     -H "Content-Type: application/json" \
     "http://localhost:8000/api/v1/?action=responses&session_id=session_abc123"
```

**Response:**
```json
{
    "success": true,
    "message": "Responses retrieved successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "responses": [
            {
                "id": 1,
                "session_id": "session_abc123",
                "response": "Hello! I am here to help you. What can I assist you with today?",
                "timestamp": "2025-08-04T03:17:33+00:00"
            }
        ]
    }
}
```

### 4. Submit Message

**Endpoint:** `POST /api/v1/?action=messages`

**Description:** Submit a new message from web chat widget.

**Authentication:** None required (public endpoint)

**Request Body:**
```json
{
    "session_id": "session_abc123",
    "message": "Can you help me with my project?"
}
```

**cURL Example:**
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{
         "session_id": "session_abc123",
         "message": "Can you help me with my project?"
     }' \
     "http://localhost:8000/api/v1/?action=messages"
```

**Response:**
```json
{
    "success": true,
    "message": "Message submitted successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "message_id": 2,
        "session_id": "session_abc123",
        "message": "Can you help me with my project?",
        "timestamp": "2025-08-04T03:17:33+00:00",
        "uid": "2632f72d266e529c",
        "is_new_user": false
    }
}
```

---

## Admin Endpoints

### 1. Get Active Sessions

**Endpoint:** `GET /api/v1/?action=sessions`

**Description:** Retrieve active sessions for admin monitoring.

**Authentication:** Admin password required

**Query Parameters:**
- `limit` (optional): Number of sessions to retrieve (default: 50, max: 100)
- `offset` (optional): Number of sessions to skip (default: 0)
- `active` (optional): Filter for active sessions only (default: true)

**cURL Example:**
```bash
curl -X GET \
     -H "Authorization: Bearer free0ps" \
     -H "Content-Type: application/json" \
     "http://localhost:8000/api/v1/?action=sessions&limit=10&active=true"
```

**Response:**
```json
{
    "success": true,
    "message": "Sessions retrieved successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "sessions": [
            {
                "id": "session_mdwj6vj5_okiiczierw",
                "uid": "2632f72d266e529c",
                "created_at": "2025-08-04 03:08:53",
                "last_active": "2025-08-04 03:17:13",
                "ip_address": "::1",
                "metadata": [],
                "message_count": 2,
                "response_count": 0
            }
        ],
        "pagination": {
            "total": 1,
            "limit": 10,
            "offset": 0,
            "has_more": false
        }
    }
}
```

### 2. Get Session Messages

**Endpoint:** `GET /api/v1/?action=session_messages`

**Description:** Retrieve all messages and responses for a specific session.

**Authentication:** Admin password required

**Query Parameters:**
- `session_id` (required): Session ID to get messages for

**cURL Example:**
```bash
curl -X GET \
     -H "Authorization: Bearer free0ps" \
     -H "Content-Type: application/json" \
     "http://localhost:8000/api/v1/?action=session_messages&session_id=session_mdwj6vj5_okiiczierw"
```

**Response:**
```json
{
    "success": true,
    "message": "Session messages retrieved",
    "timestamp": "2025-08-04T03:17:40+00:00",
    "data": {
        "session": {
            "id": "session_mdwj6vj5_okiiczierw",
            "uid": "2632f72d266e529c",
            "created_at": "2025-08-04 03:08:53",
            "last_active": "2025-08-04 03:17:13",
            "ip_address": "::1",
            "metadata": "[]"
        },
        "messages": [
            {
                "id": 9,
                "session_id": "session_mdwj6vj5_okiiczierw",
                "message": "whadduo",
                "timestamp": "2025-08-04T03:08:55.484Z"
            },
            {
                "id": 10,
                "session_id": "session_mdwj6vj5_okiiczierw",
                "message": "biatchs! lol",
                "timestamp": "2025-08-04T03:09:00.214Z"
            }
        ],
        "responses": []
    }
}
```

### 3. Get Configuration

**Endpoint:** `GET /api/v1/?action=config`

**Description:** Retrieve current system configuration.

**Authentication:** Admin password required

**cURL Example:**
```bash
curl -X GET \
     -H "Authorization: Bearer free0ps" \
     -H "Content-Type: application/json" \
     "http://localhost:8000/api/v1/?action=config"
```

**Response:**
```json
{
    "success": true,
    "message": "Configuration retrieved successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "api_key": "api_abc123def456",
        "admin_key": "free0ps",
        "session_timeout": 1800
    }
}
```

### 4. Update Configuration

**Endpoint:** `POST /api/v1/?action=config`

**Description:** Update system configuration (API key, admin password, session timeout).

**Authentication:** Admin password required

**Request Body:**
```json
{
    "api_key": "api_new_key_123",
    "admin_key": "new_admin_password",
    "session_timeout": 1800
}
```

**cURL Example:**
```bash
curl -X POST \
     -H "Authorization: Bearer free0ps" \
     -H "Content-Type: application/json" \
     -d '{
         "api_key": "api_new_key_123",
         "admin_key": "new_admin_password",
         "session_timeout": 1800
     }' \
     "http://localhost:8000/api/v1/?action=config"
```

**Response:**
```json
{
    "success": true,
    "message": "Configuration updated successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "api_key": "api_new_key_123",
        "admin_key": "new_admin_password",
        "session_timeout": 1800
    }
}
```

### 5. Manual Cleanup

**Endpoint:** `POST /api/v1/?action=cleanup`

**Description:** Manually trigger cleanup of inactive sessions.

**Authentication:** Admin password required

**cURL Example:**
```bash
curl -X POST \
     -H "Authorization: Bearer free0ps" \
     -H "Content-Type: application/json" \
     "http://localhost:8000/api/v1/?action=cleanup"
```

**Response:**
```json
{
    "success": true,
    "message": "Cleanup completed successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "cleaned_count": 5
    }
}
```

### 6. Clear All Data

**Endpoint:** `POST /api/v1/?action=clear_data`

**Description:** Clear all sessions, messages, and responses (DESTRUCTIVE).

**Authentication:** Admin password required

**cURL Example:**
```bash
curl -X POST \
     -H "Authorization: Bearer free0ps" \
     -H "Content-Type: application/json" \
     "http://localhost:8000/api/v1/?action=clear_data"
```

**Response:**
```json
{
    "success": true,
    "message": "All data cleared successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "cleared_sessions": 10,
        "cleared_messages": 25,
        "cleared_responses": 15
    }
}
```

---

## Error Handling

### HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid authentication
- `404 Not Found` - Resource not found
- `405 Method Not Allowed` - Invalid HTTP method
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Common Error Responses

**Authentication Error:**
```json
{
    "success": false,
    "error": "Authentication required",
    "timestamp": "2025-08-04T03:17:33+00:00"
}
```

**Rate Limit Error:**
```json
{
    "success": false,
    "error": "Rate limit exceeded. Please try again later.",
    "timestamp": "2025-08-04T03:17:33+00:00"
}
```

**Validation Error:**
```json
{
    "success": false,
    "error": "Invalid session ID format",
    "timestamp": "2025-08-04T03:17:33+00:00"
}
```

**Not Found Error:**
```json
{
    "success": false,
    "error": "Session not found",
    "timestamp": "2025-08-04T03:17:33+00:00"
}
```

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Public Endpoints:** 100 requests per minute per IP
- **Admin Endpoints:** 50 requests per minute per IP
- **Plugin Endpoints:** 200 requests per minute per API key

When rate limited, the API returns a `429 Too Many Requests` status with an error message.

---

## Session Management

### Session Lifecycle

1. **Creation:** Sessions are automatically created when a message is submitted
2. **Activity:** Sessions are marked as active when messages or responses are sent
3. **Timeout:** Sessions become inactive after 30 minutes of no activity
4. **Cleanup:** Inactive sessions are automatically cleaned up

### Session ID Format

Session IDs follow the format: `session_{timestamp}_{random_string}`

Example: `session_mdwj6vj5_okiiczierw`

### UID System

Each user gets a unique, persistent UID that remains consistent across sessions:

- **Format:** 16-character hexadecimal string
- **Example:** `2632f72d266e529c`
- **Storage:** Stored in database and returned with messages
- **Purpose:** Track users across multiple sessions

---

## Plugin Integration Guide

### For Broca2 Plugin Development

1. **Polling Strategy:**
   - Poll the `/inbox` endpoint every 5-10 seconds
   - Process messages in order by timestamp
   - Submit responses using the `/responses` endpoint

2. **Error Handling:**
   - Implement exponential backoff for failed requests
   - Log all API errors for debugging
   - Handle rate limiting gracefully

3. **Message Processing:**
   - Always check the `success` field in responses
   - Handle empty message arrays gracefully
   - Use the `uid` field to track users

### Example Plugin Workflow

```bash
# 1. Get unprocessed messages
curl -H "Authorization: Bearer YOUR_API_KEY" \
     "http://localhost:8000/api/v1/?action=inbox"

# 2. Process each message with Broca2
# (Your plugin logic here)

# 3. Submit response
curl -X POST \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"session_id": "session_123", "response": "Agent response"}' \
     "http://localhost:8000/api/v1/?action=outbox"
```

---

## Security Considerations

### API Key Security
- Store API keys securely in your plugin configuration
- Rotate keys regularly using the admin interface
- Never expose API keys in client-side code

### Admin Password Security
- Use strong, unique admin passwords
- Change default admin password immediately
- Store admin password securely for plugin configuration

### Input Validation
- All inputs are validated and sanitized
- Session IDs must match expected format
- Messages are limited to reasonable length

### CORS Configuration
- API supports cross-origin requests for web chat widget
- Admin endpoints are restricted to same-origin requests

---

## Testing Examples

### Test API Key Authentication
```bash
curl -H "Authorization: Bearer api_test_key" \
     "http://localhost:8000/api/v1/?action=inbox"
```

### Test Message Submission
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"session_id": "test_session_123", "message": "Test message"}' \
     "http://localhost:8000/api/v1/?action=messages"
```

### Test Response Submission
```bash
curl -X POST \
     -H "Authorization: Bearer api_h8hcbfg4uiqfz6sjy1h6ri" \
     -H "Content-Type: application/json" \
     -d '{"session_id": "test_session_123", "response": "Test response"}' \
     "http://localhost:8000/api/v1/?action=outbox"
```

### Test Admin Access
```bash
curl -H "Authorization: Bearer free0ps" \
     "http://localhost:8000/api/v1/?action=sessions"
```

---

## Configuration

### Default Settings

- **Session Timeout:** 30 minutes (1800 seconds)
- **Rate Limiting:** 100 requests/minute for public endpoints
- **Database:** SQLite with automatic cleanup
- **CORS:** Enabled for web chat widget

### Environment Variables

The API uses the following configuration files:
- `config/settings.php` - API settings and keys
- `config/database.php` - Database configuration
- `includes/auth.php` - Authentication logic

---

## Support

For API support or questions:
1. Check the error responses for specific issues
2. Verify authentication credentials
3. Ensure proper request format
4. Check rate limiting status
5. Review session timeout settings

The API is designed to be self-documenting with clear error messages and consistent response formats. 