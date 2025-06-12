# Sanctum: Broca 2 CLI Tools Reference

## Overview
Sanctum: Broca 2 provides a suite of CLI tools for administration, diagnostics, and development. All tools are designed for automation and scripting as well as interactive use.

---

## CLI Tools List
- `broca-admin queue`: Manage the message queue (list, flush, delete)
- `broca-admin users`: List and manage users
- `broca-admin conversations`: View and manage conversations
- `broca-admin settings`: Configure system behavior
- (Other tools may be added in `cli/`)

---

## Usage Examples
### Queue Management
```sh
broca-admin queue list
broca-admin queue flush
broca-admin queue delete <id>
```

### User Management
```sh
broca-admin users list
broca-admin users add <username>
broca-admin users remove <id>
```

### Conversations
```sh
broca-admin conversations list
broca-admin conversations get <user_id> <platform_id> --limit 10
```

### Settings
```sh
broca-admin settings get
broca-admin settings set message_mode live
broca-admin settings mode echo
broca-admin settings debug --enable
broca-admin settings refresh 10
```

---

## Command-Line Arguments & Options
- All tools support `--json` for machine-readable output.
- Most commands support subcommands and arguments (see `--help`).
- Example:
```sh
broca-admin queue list --json
broca-admin users list --json
```

---

## Output Formats
- **Plain text:** Human-readable, default.
- **JSON:** Use `--json` for structured output (for scripting, automation).

---

## Extending CLI Tools
- Add new scripts in `cli/` (e.g., `cli/btool.py` for bot ignore list management).
- Use `argparse` for argument parsing.
- Register new commands in `broca-admin` dispatcher if needed.
- Follow the pattern in existing tools for consistency.

---

## Troubleshooting
- Use `--help` for command usage.
- Check logs for errors if a command fails.
- Ensure you have the correct permissions for DB operations.
- For JSON output, pipe to `jq` or similar tools for processing.

---

## Example: Adding a New CLI Command
1. Create a new script in `cli/` (e.g., `cli/btool.py`).
2. Implement argument parsing and main logic.
3. Register the command in the main CLI dispatcher if needed.
4. Test with both plain and JSON output.

---

## Cross-References
- See `cli/` directory for all CLI tool implementations.
- See `broca2/docs/plugin_development.md` for plugin CLI integration.
- See `broca2/docs/configuration.md` for settings details.

---

For more advanced usage or automation, see the main README or contact the maintainers. 