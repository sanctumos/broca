





---

# Sanctum: Broca 2 Configuration Guide

## Overview
Sanctum: Broca 2 uses a combination of JSON and environment variable configuration for maximum flexibility. With the new multi-agent architecture, configuration is split between base installation settings and agent-specific configurations. This guide covers all configuration options, files, and best practices.

---

## Multi-Agent Configuration Structure

### Base Installation Configuration
Located in the root directory, these settings are shared across all agent instances:
- `settings.json`: Base runtime settings and plugin configurations
- `.env`: Base environment variables for shared services (Telegram API, etc.)

### Agent-Specific Configuration
Each agent instance has its own configuration in `agent-{uuid}/` directories:
- `agent-{uuid}/.env`: Agent-specific environment variables
- `agent-{uuid}/settings.json`: Agent-specific runtime settings
- `agent-{uuid}/sanctum.db`: Agent-specific database

---

## Configuration Files

### Base Installation Files
- `settings.json`: Main runtime settings (log level, max workers, timeout, etc.)
- `.env`: Base environment variables for shared services
- `requirements.txt`: Python dependencies for all agents

### Agent Instance Files
- `agent-{uuid}/.env`: Agent-specific environment variables
- `agent-{uuid}/settings.json`: Agent-specific runtime settings
- `agent-{uuid}/sanctum.db`: Agent-specific database
- `agent-{uuid}/logs/`: Agent-specific log directory

---

## Environment Variables

### Base Installation Variables (.env in broca2 root)
| Variable                         | Description                                                        | Example Value                |
|----------------------------------|--------------------------------------------------------------------|------------------------------|
| `TELEGRAM_API_ID`                | Telegram API ID                                                    | `123456`                     |
| `TELEGRAM_API_HASH`              | Telegram API hash                                                  | `abcdef123456`               |
| `TELEGRAM_PHONE`                 | Telegram phone number                                              | `+1234567890`                |
| `DEBUG_MODE`                     | Enable/disable debug mode                                          | `false`                      |
| `LOG_LEVEL`                      | Logging level                                                      | `INFO`                       |
| `ENABLE_IMAGE_HANDLING`          | Enable multimodal image handling (photos accepted, optional addendum) | `false`                      |
| `ENABLE_TMPFILES_IMAGE_ADDENDUM` | When image handling is on, upload images to tmpfiles.org and append `[Image Attachment: url]` to message text | `false`                      |

### Agent Instance Variables (.env in agent-{uuid}/)
| Variable                | Description                        | Example Value                |
|-------------------------|------------------------------------|------------------------------|
| `AGENT_ID`              | Unique agent identifier            | `721679f6-c8af-4e01-8677-dc042dc80368` |
| `LETTA_API_KEY`         | Letta agent API key                | `abc123`                     |
| `LETTA_API_ENDPOINT`    | Letta agent API endpoint URL        | `https://api.letta.ai`       |
| `MESSAGE_MODE`          | Message processing mode            | `live`/`echo`/`listen`       |
| `QUEUE_REFRESH`         | Queue refresh interval (seconds)   | `5`                          |
| `MAX_RETRIES`           | Max retry attempts for failures     | `3`                          |
| `DEBUG_MODE`            | Agent-specific debug mode          | `false`                      |

---

## Settings Structure

### Base Settings (`settings.json`)
```json
{
  "system": {
    "log_level": "INFO",
    "max_workers": 4,
    "timeout": 30
  },
  "plugins": {
    "telegram": {
      "enabled": true,
      "parse_mode": "MarkdownV2"
    }
  }
}
```

### Agent Settings (`broca2/agent-{uuid}/settings.json`)
```json
{
  "agent": {
    "id": "721679f6-c8af-4e01-8677-dc042dc80368",
    "name": "My Agent",
    "description": "Agent for specific tasks"
  },
  "message_processing": {
    "mode": "live",
    "queue_refresh": 5,
    "max_retries": 3
  },
  "plugins": {
    "telegram": {
      "enabled": true,
      "parse_mode": "MarkdownV2"
    }
  }
}
```

---

## Configuration Management

### Creating New Agent Instances
```bash
# Copy base configuration templates
cp ~/sanctum/broca2/.env.example ~/sanctum/broca2/agent-{uuid}/.env
cp ~/sanctum/broca2/settings.json ~/sanctum/broca2/agent-{uuid}/settings.json

# Edit agent-specific configuration
nano ~/sanctum/broca2/agent-{uuid}/.env
nano ~/sanctum/broca2/agent-{uuid}/settings.json
```

### Updating Base Configuration
```bash
# Update base settings (affects all agents)
cd ~/sanctum/broca2
nano settings.json
nano .env

# Restart all agent instances to pick up changes
pm2 restart all
# or
sudo systemctl restart broca-agent-*
```

### Updating Agent-Specific Configuration
```bash
# Update specific agent configuration
cd ~/sanctum/broca2/agent-{uuid}
nano .env
nano settings.json

# Restart specific agent
pm2 restart broca-agent-{uuid}
# or
sudo systemctl restart broca-agent-{uuid}
```

---

## Plugin-Specific Configuration

### Base Plugin Configuration
Plugins can define base settings in `settings.json`:
```json
{
  "plugins": {
    "telegram": {
      "enabled": true,
      "parse_mode": "MarkdownV2",
      "session_timeout": 3600
    }
  }
}
```

### Agent-Specific Plugin Configuration
Each agent can override or extend plugin settings:
```json
{
  "plugins": {
    "telegram": {
      "enabled": true,
      "parse_mode": "MarkdownV2",
      "custom_setting": "agent_specific_value"
    }
  }
}
```

---

## Configuration Inheritance and Overrides

### Priority Order (Highest to Lowest)
1. **Agent-specific settings** (`agent-{uuid}/settings.json`)
2. **Agent-specific environment** (`agent-{uuid}/.env`)
3. **Base settings** (`settings.json`)
4. **Base environment** (`.env`)
5. **Default values** (hardcoded in code)

### Example: Message Mode Configuration
```bash
# Base installation (.env)
MESSAGE_MODE=live

# Agent instance (.env)
MESSAGE_MODE=echo

# Result: Agent uses 'echo' mode (agent setting overrides base)
```

---

## Adding/Changing Configuration Options

### For Base Installation
1. Add the new option to `settings.json` or `.env`
2. Update the code to read the new option (see `common/config.py`)
3. Validate the option in `validate_settings()`
4. Document the new option in this guide
5. Test with multiple agent instances

### For Agent Instances
1. Add the new option to `broca2/agent-{uuid}/settings.json` or `broca2/agent-{uuid}/.env`
2. Update the code to read agent-specific options
3. Ensure proper fallback to base configuration
4. Document the new option in this guide
5. Test with the specific agent instance

---

## Security & Best Practices

### Multi-Agent Security
- Never commit secrets or API keys to version control
- Use `.env` for sensitive data in both base and agent directories
- Set proper permissions: `chmod 700 agent-*/` and `chmod 600 agent-*/.env`
- Each agent maintains separate credentials and databases
- Validate all config values before use

### Configuration Validation
- Use default values and type checks
- Implement configuration validation for both base and agent settings
- Ensure agent isolation is maintained
- Document all config options for users and developers

---

## Troubleshooting

### Configuration Issues
- If the app fails to start, check for missing or invalid config values
- Verify both base and agent-specific configurations
- Use `--debug` or set `DEBUG_MODE=true` for more verbose logs
- Check for typos in `.env` and `settings.json` files
- Use the CLI tools to view and set config options

### Multi-Agent Issues
- Ensure agent directories exist and have proper permissions
- Verify virtual environment is accessible from agent directories
- Check that agent-specific databases are properly initialized
- Monitor logs in `agent-{uuid}/logs/` directories

---

## Example: Adding a New Config Option

### 1. Add to Base Settings
```json
// settings.json
{
  "system": {
    "log_level": "INFO",
    "max_workers": 4,
    "timeout": 30,
    "new_feature": true
  }
}
```

### 2. Add to Agent Settings
```json
// broca2/agent-{uuid}/settings.json
{
  "agent": {
    "id": "721679f6-c8af-4e01-8677-dc042dc80368",
    "name": "My Agent",
    "new_feature": false  // Override base setting
  }
}
```

### 3. Update Configuration Code
```python
# common/config.py
def get_config_value(key: str, agent_id: str = None) -> Any:
    # Check agent-specific setting first
    if agent_id:
        agent_value = get_agent_setting(key, agent_id)
        if agent_value is not None:
            return agent_value

    # Fall back to base setting
    return get_base_setting(key)
```

---

## Cross-References
- See `common/config.py` for config loading and validation
- See `docs/multi-agent-architecture.md` for multi-agent setup
- See `docs/plugin_development.md` for plugin config integration
- See `docs/cli_reference.md` for CLI config commands

---

For more details, see the main README or contact the maintainers.
