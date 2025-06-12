# Sanctum: Broca 2 Configuration Guide

## Overview
Sanctum: Broca 2 uses a combination of JSON and environment variable configuration for maximum flexibility. This guide covers all configuration options, files, and best practices.

---

## Configuration Files
- `settings.json`: Main runtime settings (message mode, queue refresh, debug, etc.)
- `.env`: Environment variables for sensitive data (API keys, DB paths, etc.)
- Plugin configs: Plugins may have their own config files or sections in `settings.json`.

---

## Environment Variables
| Variable                | Description                        | Example Value                |
|-------------------------|------------------------------------|------------------------------|
| `LETTA_API_KEY`         | Letta agent API key                | `abc123`                     |
| `LETTA_API_ENDPOINT`    | Letta agent API endpoint URL        | `https://api.letta.ai`       |
| `TELEGRAM_API_ID`       | Telegram API ID                    | `123456`                     |
| `TELEGRAM_API_HASH`     | Telegram API hash                  | `abcdef123456`               |
| `TELEGRAM_PHONE`        | Telegram phone number              | `+1234567890`                |
| `DEBUG_MODE`            | Enable/disable debug mode          | `true`                       |
| `QUEUE_REFRESH`         | Queue refresh interval (seconds)   | `5`                          |
| `MAX_RETRIES`           | Max retry attempts for failures     | `3`                          |
| `MESSAGE_MODE`          | Message processing mode            | `live`/`echo`/`listen`       |

---

## Settings Structure (`settings.json`)
```json
{
  "debug_mode": false,
  "queue_refresh": 5,
  "max_retries": 3,
  "message_mode": "live"
}
```
- `debug_mode`: Enables verbose logging and diagnostics.
- `queue_refresh`: How often the queue is polled (in seconds).
- `max_retries`: Maximum number of retries for failed messages.
- `message_mode`: Processing mode (`live`, `echo`, `listen`).

---

## Plugin-Specific Configuration
- Plugins may define their own settings in `settings.json` or separate files.
- Example (in `settings.json`):
```json
{
  "telegram": {
    "api_id": "...",
    "api_hash": "...",
    "session_string": "..."
  }
}
```
- Always document plugin config options in the plugin's README or in `plugin_development.md`.

---

## Adding/Changing Configuration Options
1. Add the new option to `settings.json` or `.env`.
2. Update the code to read the new option (see `common/config.py`).
3. Validate the option in `validate_settings()`.
4. Document the new option in this guide.

---

## Security & Best Practices
- Never commit secrets or API keys to version control.
- Use `.env` for sensitive data.
- Validate all config values before use.
- Use default values and type checks.
- Document all config options for users and developers.

---

## Troubleshooting
- If the app fails to start, check for missing or invalid config values.
- Use `--debug` or set `DEBUG_MODE=true` for more verbose logs.
- Check for typos in `.env` and `settings.json`.
- Use the CLI tools to view and set config options.

---

## Example: Adding a New Config Option
1. Add the option to `settings.json`:
```json
{
  "my_new_option": "value"
}
```
2. Update `common/config.py` to read and validate the option.
3. Document the option in this file.
4. Test with different values and edge cases.

---

## Cross-References
- See `common/config.py` for config loading and validation.
- See `broca2/docs/plugin_development.md` for plugin config integration.
- See `broca2/docs/cli_reference.md` for CLI config commands.

---

For more details, see the main README or contact the maintainers. 