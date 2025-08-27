# ⚠️ REPOSITORY MOVED ⚠️

**This repository has moved to: [http://github.com/sanctumos/broca](http://github.com/sanctumos/broca)**

Please update your git remotes and use the new repository location for all future development and contributions.

---

# 504 Gateway Timeout Issue - Long Message Processing

## Issue Overview

We've identified a critical issue with **504 Gateway Timeout errors** occurring during long message processing or extensive tool-chain usage on the Letta server. This appears to be a recoverable error condition that requires systematic handling.

### Error Symptoms

```
[2025-06-24 21:22:27] [INFO] 🔵 Processing message with attached core block block-94...
[2025-06-24 21:23:27] [INFO] HTTP Request: POST https://your-letta-server.com:8283/v1/agents/agent-{uuid}/messages "HTTP/1.1 504 Gateway Time-out"
[2025-06-24 21:23:27] [ERROR] Error processing message: status_code: 504, body: <html>
<head><title>504 Gateway Time-out</title></head>
<body>
<center><h1>504 Gateway Time-out</h1></center>
<hr><center>nginx/1.24.0 (Ubuntu)</center>
</body>
</html>

[2025-06-24 21:23:27] [INFO] 🔵 Detaching core block block-94... from agent
[2025-06-24 21:23:28] [INFO] HTTP Request: PATCH https://your-letta-server.com:8283/v1/agents/agent-{uuid}/core-memory/blocks/detach/block-{uuid} "HTTP/1.1 200 OK"
[2025-06-24 21:23:28] [WARNING] ⚠️ No response received from agent - Message processing failed
[2025-06-24 21:23:28] [WARNING] ⚠️ No response received from agent - Message processing failed
```

### What is a 504 Gateway Timeout?

A **504 Gateway Timeout** occurs when:
- Nginx (acting as a reverse proxy/gateway) doesn't receive a timely response from the upstream server (Letta API)
- The upstream server is taking longer than the configured timeout period to process the request
- In our case, the Letta server is taking more than ~60 seconds to process complex messages with tool chains

## Root Cause Analysis

### Technical Details

1. **Request Flow:**
   ```
   Broca-2 Client → Nginx Reverse Proxy → Letta Server
   ```

2. **Timeout Sequence:**
   - Message processing starts with core block attachment
   - Long-running operation (tool chains, complex reasoning) begins
   - Nginx timeout threshold (~60 seconds) is exceeded
   - Nginx returns 504 error while Letta server continues processing
   - Core block is detached, but response is lost

3. **Current Error Handling:**
   - Located in `broca2/runtime/core/queue.py:_process_with_core_block()`
   - Generic exception handling catches 504 but doesn't implement recovery
   - Core block is properly detached (cleanup works)
   - Message is marked as 'failed' in queue

### Factors Contributing to Long Processing Times

1. **Tool Chain Execution:** Complex tool sequences can take several minutes
2. **Large Context Processing:** Large message contexts require more processing time
3. **Core Block Operations:** Attach/detach operations add overhead
4. **Agent Reasoning:** Complex reasoning cycles can extend processing time

## Recovery Strategy Research

### Available Recovery Mechanisms

Based on Letta API documentation, we have several recovery options:

#### 1. Conversations Endpoint Recovery
```python
# Get conversation history to retrieve the response
client.agents.messages.list(
    agent_id="agent_id",
    limit=1,  # Get the most recent message
    after="last_known_message_id"
)
```

#### 2. Agent State Polling
```python
# Check if agent has new messages after timeout
response = client.agents.retrieve(agent_id="agent_id")
# Check response.message_ids for new entries
```

#### 3. Async Message Handling
```python
# Use async message creation (if available)
client.agents.messages.create_async(
    agent_id="agent_id",
    messages=[MessageCreate(role="user", content="message")]
)
```

## Proposed Solutions

### Immediate Solutions (High Priority)

#### 1. Enhanced Error Detection
Add specific 504 timeout detection in `queue.py`:

```python
# In _process_with_core_block method
except Exception as e:
    error_str = str(e)
    if "504" in error_str or "Gateway Time-out" in error_str:
        logger.warning(f"⚠️ 504 timeout detected - attempting recovery for user {letta_user_id}")
        # Implement recovery logic here
        response = await self._attempt_timeout_recovery(letta_user_id, message)
        if response:
            return response, 'completed'
    
    logger.error(f"Error during message processing: {str(e)}")
    # ... existing cleanup code
```

#### 2. Response Recovery Implementation
```python
async def _attempt_timeout_recovery(self, letta_user_id: int, original_message: str) -> Optional[str]:
    """Attempt to recover response after 504 timeout."""
    try:
        # Wait a brief moment for processing to complete
        await asyncio.sleep(5)
        
        # Query conversations endpoint for the response
        messages = self.letta_client.agents.messages.list(
            agent_id=self.agent_id,
            limit=5,  # Get recent messages
            use_assistant_message=True
        )
        
        # Look for assistant messages that might be our response
        for msg in messages:
            if msg.message_type == 'assistant_message' and msg.content:
                # Validate this is likely our response
                if self._validate_response_match(msg, original_message):
                    logger.info(f"✅ Successfully recovered response from timeout")
                    return msg.content
        
        return None
    except Exception as e:
        logger.error(f"Recovery attempt failed: {str(e)}")
        return None
```

#### 3. Configurable Retry Mechanism
Extend the existing `max_retries` setting to handle 504 timeouts:

```python
# In settings.json
{
    "debug_mode": false,
    "queue_refresh": 5,
    "max_retries": 3,
    "message_mode": "live",
    "timeout_recovery_enabled": true,
    "timeout_recovery_delay": 10,
    "timeout_recovery_attempts": 2
}
```

### Medium-Term Solutions

#### 1. Timeout Prevention
- Implement message size/complexity analysis
- Pre-calculate estimated processing time
- Split large messages into smaller chunks if needed

#### 2. Async Processing Pattern
- Implement async message submission
- Poll for completion rather than waiting synchronously
- Provide progress updates to users during long operations

#### 3. Enhanced Monitoring
- Add metrics for message processing times
- Monitor 504 error frequency and patterns
- Alert on excessive timeout rates

### Long-Term Solutions

#### 1. Infrastructure Optimization
- Work with server admin to increase Nginx timeout values
- Implement connection keep-alive optimization
- Consider load balancing for high-traffic scenarios

#### 2. Processing Architecture
- Implement background job processing for long operations
- Add message processing queue with priority levels
- Create dedicated processing threads for complex operations

## Implementation Priority

### Phase 1: Critical (Immediate)
1. ✅ Document the issue (this document)
2. 🔄 Implement 504 error detection
3. 🔄 Add basic response recovery mechanism
4. 🔄 Add timeout-specific logging

### Phase 2: Important (Next Sprint)
1. Implement configurable retry mechanism
2. Add recovery attempt metrics
3. Enhance error reporting to users
4. Test recovery mechanism thoroughly

### Phase 3: Optimization (Future)
1. Implement async processing patterns
2. Add message complexity analysis
3. Optimize server-side timeout handling
4. Implement progress indicators for long operations

## Configuration Changes Needed

### Current Configuration
```json
{
    "max_retries": 3,
    "queue_refresh": 5,
    "message_mode": "live"
}
```

### Proposed Enhanced Configuration
```json
{
    "max_retries": 3,
    "queue_refresh": 5,
    "message_mode": "live",
    "timeout_handling": {
        "enabled": true,
        "recovery_attempts": 2,
        "recovery_delay_seconds": 10,
        "max_recovery_wait_seconds": 300,
        "log_recovery_attempts": true
    }
}
```

## Testing Strategy

### Test Scenarios
1. **Deliberate Timeout:** Create artificially long-running operations
2. **Network Simulation:** Test with simulated network delays
3. **Recovery Validation:** Verify responses are correctly recovered
4. **Concurrent Processing:** Test recovery under load
5. **Edge Cases:** Test partial responses, malformed recovery data

### Success Metrics
- 504 errors are detected and logged appropriately
- Recovery success rate > 80% for legitimate timeouts
- No message loss during recovery attempts
- Core block cleanup remains reliable
- User experience degradation is minimized

## Code Locations for Implementation

### Primary Files to Modify
1. `broca2/runtime/core/queue.py` - Main recovery logic
2. `broca2/runtime/core/agent.py` - Enhanced error handling
3. `broca2/common/config.py` - Configuration schema updates
4. `broca2/settings.json` - Default configuration values

### New Files to Create
1. `broca2/runtime/core/recovery.py` - Dedicated recovery mechanisms
2. `broca2/runtime/core/timeout_handler.py` - Timeout-specific handling
3. `broca2/database/operations/recovery.py` - Recovery state tracking

## Related Issues and Dependencies

### Existing Code Dependencies
- Letta client configuration and connectivity
- Database operations for message state tracking
- Queue processing and status updates
- Core block management system

### Potential Conflicts
- Existing retry mechanisms in queue processing
- Message status tracking and updates
- Concurrent processing safeguards
- Error reporting and logging systems

## Monitoring and Alerting

### Metrics to Track
- 504 error frequency and patterns
- Recovery attempt success/failure rates
- Message processing time distributions
- Core block operation timing
- Queue processing efficiency

### Alert Conditions
- 504 error rate exceeds 5% of total messages
- Recovery failure rate exceeds 20%
- Average message processing time increases significantly
- Core block operations failing after recovery

## Documentation Updates Required

### User-Facing Documentation
- Update error handling documentation
- Add troubleshooting guide for timeout issues
- Document new configuration options
- Update API behavior documentation

### Developer Documentation
- Update architecture diagrams
- Document recovery mechanisms
- Add debugging guides for timeout issues
- Update contribution guidelines for timeout handling

---

**Last Updated:** 2025-01-24  
**Status:** In Progress  
**Priority:** High  
**Assignee:** Development Team  
**Related:** Message Processing, Error Handling, Letta Integration 