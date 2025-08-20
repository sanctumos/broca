# Sanctum: Broca 2 CLI Tools Reference

## Overview
Sanctum: Broca 2 provides a suite of CLI tools for administration, diagnostics, and development. All tools are designed for automation and scripting as well as interactive use. With the new multi-agent architecture, CLI tools can operate on specific agent instances or across all agents.

---

## CLI Tools List

### Core CLI Tools
- `btool.py`: Main CLI interface for queue management, users, and system operations
- `ctool.py`: Configuration and settings management
- `qtool.py`: Queue-specific operations and monitoring
- `utool.py`: User management and operations
- `settings.py`: Settings management utilities

### Usage Pattern
```bash
# From the base installation directory
python -m cli.btool <command> [options]

# From an agent instance directory
cd ~/sanctum/broca2/agent-{uuid}
python -m cli.btool <command> [options]
```

---

## Usage Examples

### Queue Management
```bash
# List all messages in queue
python -m cli.btool queue list

# Flush all messages from queue
python -m cli.btool queue flush

# Delete specific message by ID
python -m cli.btool queue delete <id>

# Get queue statistics
python -m cli.btool queue stats
```

### User Management
```bash
# List all users
python -m cli.btool users list

# Get user details
python -m cli.btool users get <user_id>

# List user conversations
python -m cli.btool users conversations <user_id>
```

### Configuration Management
```bash
# Show current settings
python -m cli.ctool settings show

# Set specific setting
python -m cli.ctool settings set message_mode live

# Get setting value
python -m cli.ctool settings get message_mode
```

### System Operations
```bash
# Show system status
python -m cli.btool status

# Show agent information
python -m cli.btool agent info

# Show plugin status
python -m cli.btool plugins list
```

---

## Multi-Agent CLI Operations

### Agent-Specific Operations
```bash
# Work with specific agent instance
cd ~/sanctum/broca2/agent-{uuid}

# List queue for this agent
python -m cli.btool queue list

# Show agent-specific settings
python -m cli.ctool settings show

# Check agent status
python -m cli.btool status
```

### Cross-Agent Operations
```bash
# From base installation directory
cd ~/sanctum/broca2

# List all agent instances
python -m cli.btool agents list

# Show status of all agents
python -m cli.btool agents status

# Backup all agent databases
python -m cli.btool agents backup
```

---

## Command-Line Arguments & Options

### Common Options
- `--json`: Output in JSON format for machine-readable output
- `--verbose` or `-v`: Enable verbose logging
- `--debug`: Enable debug mode
- `--help` or `-h`: Show command help

### Examples
```bash
# JSON output for automation
python -m cli.btool queue list --json

# Verbose output for debugging
python -m cli.btool users list --verbose

# Debug mode for troubleshooting
python -m cli.btool status --debug
```

---

## Output Formats

### Plain Text (Default)
Human-readable output suitable for interactive use and logging.

### JSON Output
Structured output for scripting and automation:
```bash
# Get JSON output
python -m cli.btool queue list --json

# Pipe to jq for processing
python -m cli.btool users list --json | jq '.[] | .username'

# Save to file
python -m cli.btool status --json > status.json
```

---

## Multi-Agent CLI Patterns

### Working with Specific Agents
```bash
# Navigate to agent directory
cd ~/sanctum/broca2/agent-{uuid}

# All CLI operations now work on this agent's data
python -m cli.btool queue list
python -m cli.btool users list
python -m cli.ctool settings show
```

### Working from Base Directory
```bash
# From base installation
cd ~/sanctum/broca2

# Use --agent-id flag for specific agent operations
python -m cli.btool queue list --agent-id {uuid}
python -m cli.btool users list --agent-id {uuid}
python -m cli.ctool settings show --agent-id {uuid}
```

### Batch Operations
```bash
# Backup all agent databases
python -m cli.btool agents backup

# Show status of all agents
python -m cli.btool agents status

# Update all agent configurations
python -m cli.ctool agents update-config
```

---

## Extending CLI Tools

### Adding New Commands
1. Create new script in `cli/` directory
2. Follow existing patterns for argument parsing
3. Implement proper error handling and output formatting
4. Add support for `--json` output
5. Consider multi-agent usage patterns

### Example: New Command Structure
```python
#!/usr/bin/env python3
"""New CLI command for custom functionality."""

import argparse
import json
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Custom command")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--agent-id", help="Specific agent ID")
    
    args = parser.parse_args()
    
    try:
        # Command logic here
        result = {"status": "success", "data": "example"}
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Status: {result['status']}")
            print(f"Data: {result['data']}")
            
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## Troubleshooting

### Common Issues
- **Permission Denied**: Ensure proper access to agent directories
- **Agent Not Found**: Verify agent ID and directory structure
- **Database Errors**: Check agent-specific database files
- **Configuration Issues**: Verify both base and agent-specific configs

### Debug Commands
```bash
# Enable debug mode
python -m cli.btool --debug status

# Check agent directory structure
ls -la ~/sanctum/broca2/agent-*/

# Verify virtual environment
source ~/sanctum/broca2/venv/bin/activate
python -c "import cli.btool; print('CLI tools OK')"
```

### Log Analysis
```bash
# Check agent-specific logs
tail -f ~/sanctum/broca2/agent-{uuid}/logs/broca.log

# Check base installation logs
tail -f ~/sanctum/broca2/logs/broca.log
```

---

## Automation Examples

### Scripting with CLI Tools
```bash
#!/bin/bash
# Monitor all agents and report status

cd ~/sanctum/broca2

echo "Agent Status Report - $(date)"
echo "================================"

for agent_dir in agent-*/; do
    agent_id=$(basename "$agent_dir")
    echo -n "Agent ${agent_id}: "
    
    # Get status in JSON format
    status=$(python -m cli.btool status --agent-id "$agent_id" --json 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo "$status" | jq -r '.status'
    else
        echo "ERROR"
    fi
done
```

### Cron Jobs
```bash
# Add to crontab for regular monitoring
# */5 * * * * cd ~/sanctum/broca2 && python -m cli.btool agents health-check > /tmp/broca-health.log 2>&1
```

---

## Cross-References
- See `cli/` directory for all CLI tool implementations
- See `broca2/docs/multi-agent-architecture.md` for multi-agent setup
- See `broca2/docs/plugin_development.md` for plugin CLI integration
- See `broca2/docs/configuration.md` for settings details

---

For more advanced usage or automation, see the main README or contact the maintainers. 