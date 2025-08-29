





---

# Multi-Agent Architecture Guide

## Overview

Broca 2 supports running multiple Letta agent instances through a complete isolation approach. Each agent runs in its own completely isolated Broca instance with its own repository clone, configuration, database, and plugin instances. This architecture provides maximum isolation between agents while sharing only the Sanctum-wide virtual environment.

## 🏗️ Architecture Principles

### 1. **Complete Instance Isolation**
- Each agent runs in its own directory with a complete Broca repository clone
- Independent databases prevent any data cross-contamination
- Separate configuration files and plugin instances
- Independent log files for easy debugging and monitoring

### 2. **Shared Resources (Minimal)**
- Only the Sanctum-wide virtual environment is shared (not Broca-specific)
- No shared Broca code, plugins, or runtime components between agents
- Each agent maintains its own complete Broca installation

### 3. **Simple Management**
- Clear 1:1 mapping between agent IDs and instance folders
- Standardized folder structure for easy automation
- Each agent can be updated independently by pulling from their own Broca repository

## 📁 Directory Structure

```
~/sanctum/                    # Sanctum home directory
├── venv/                     # Sanctum-wide virtual environment (shared by all tools)
├── agent-{uuid}/            # Agent-specific instance
│   ├── broca/               # Complete Broca repository clone for this agent
│   │   ├── main.py          # Core runtime entry point
│   │   ├── runtime/         # Core system components
│   │   ├── plugins/         # Available plugins
│   │   ├── cli/             # CLI tools
│   │   ├── common/          # Shared utilities
│   │   ├── database/        # Database models
│   │   ├── requirements.txt # Python dependencies
│   │   ├── .env.example     # Base configuration template
│   │   └── settings.json    # Base settings template
│   ├── .env                 # Agent-specific environment
│   ├── settings.json        # Agent-specific settings
│   ├── sanctum.db          # Agent-specific database
│   └── logs/               # Agent-specific logs
├── agent-{uuid}/            # Another agent instance
│   ├── broca/               # Complete Broca repository clone for this agent
│   │   ├── main.py
│   │   ├── runtime/
│   │   ├── plugins/
│   │   └── ...
│   ├── .env
│   ├── settings.json
│   ├── sanctum.db
│   └── logs/
└── other-sanctum-tools/     # Other Sanctum tools (shared venv)
    ├── tool1/
    └── tool2/
```

## 🚀 Setup Instructions

### Step 1: Create Sanctum Directory Structure

```bash
# Create the main sanctum directory
mkdir ~/sanctum
cd ~/sanctum

# Create shared virtual environment (Sanctum-wide, not Broca-specific)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Create Agent Instances

```bash
# For each Letta agent, create a folder named after the agent ID
mkdir agent-721679f6-c8af-4e01-8677-dc042dc80368
cd agent-721679f6-c8af-4e01-8677-dc042dc80368

# Clone a complete Broca repository for this agent
git clone https://github.com/sanctumos/broca.git broca

# Note: Virtual environment is managed at the Sanctum level, not per Broca instance
# The venv in ~/sanctum/venv/ is shared by all Sanctum tools
```

### Step 3: Configure Agent Instances

```bash
# Copy base configuration from the cloned repository
cp broca/.env.example .env
cp broca/settings.json .

# Edit agent-specific configuration
nano .env

# Set agent-specific variables
AGENT_ID=721679f6-c8af-4e01-8677-dc042dc80368
LETTA_API_ENDPOINT=https://your-letta-instance.com/api/v1
LETTA_API_KEY=your_agent_specific_api_key
DEBUG_MODE=false
MESSAGE_MODE=live
```

### Step 4: Install Dependencies and Run Agent Instances

```bash
# Activate the Sanctum-wide virtual environment
cd ~/sanctum
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Broca dependencies
cd agent-721679f6-c8af-4e01-8677-dc042dc80368/broca
pip install -r requirements.txt

# Run the agent instance
python main.py

# Or use CLI tools
python -m cli.btool queue list
python -m cli.btool users list
```

## 🔧 Configuration Management

### Environment Variables

#### Agent Instance (.env in agent-{uuid}/)
```bash
# Agent identification
AGENT_ID=721679f6-c8af-4e01-8677-dc042dc80368

# Letta API configuration (agent-specific)
LETTA_API_ENDPOINT=https://your-letta-instance.com/api/v1
LETTA_API_KEY=your_agent_specific_api_key

# Agent-specific settings
MESSAGE_MODE=live
QUEUE_REFRESH=5
MAX_RETRIES=3
DEBUG_MODE=false
```

### Settings Files

#### Agent Settings (settings.json in agent-{uuid}/)
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

## 🚦 Running Multiple Instances

### Manual Startup

```bash
# Terminal 1: Start first agent
cd ~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368

# Activate the Sanctum-wide virtual environment
source ~/sanctum/venv/bin/activate

# Run the instance from the agent's Broca clone
python broca/main.py

# Terminal 2: Start second agent
cd ~/sanctum/agent-9a2b3c4d-5e6f-7890-abcd-ef1234567890

# Activate the Sanctum-wide virtual environment
source ~/sanctum/venv/bin/activate

# Run the instance from the agent's Broca clone
python broca/main.py
```

### Process Manager (PM2)

```bash
# Install PM2 if not already installed
npm install -g pm2

# Start agents with PM2
cd ~/sanctum

pm2 start "broca-agent-1" --interpreter venv/bin/python -- agent-721679f6-c8af-4e01-8677-dc042dc80368/broca/main.py
pm2 start "broca-agent-2" --interpreter venv/bin/python -- agent-9a2b3c4d-5e6f-7890-abcd-ef1234567890/broca/main.py

# Monitor processes
pm2 list
pm2 logs

# Stop agents
pm2 stop broca-agent-1
pm2 stop broca-agent-2
```

### Systemd Services

```bash
# Create systemd service file for each agent
sudo nano /etc/systemd/system/broca-agent-1.service

[Unit]
Description=Broca Agent 1
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368
ExecStart=/home/your_username/sanctum/venv/bin/python broca/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Enable and start services
sudo systemctl enable broca-agent-1
sudo systemctl start broca-agent-1
sudo systemctl status broca-agent-1
```

## 📊 Monitoring and Management

### CLI Tools

```bash
# Queue management for specific agent
cd ~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368

# Activate the Sanctum-wide virtual environment
source ~/sanctum/venv/bin/activate

# Use CLI tools from the agent's Broca clone
python -m broca.cli.btool queue list
python -m broca.cli.btool queue flush

# User management
python -m broca.cli.btool users list

# Settings management
python -m broca.cli.ctool settings show
python -m broca.cli.ctool settings set message_mode live
```

### Log Management

```bash
# View agent-specific logs
cd ~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368
tail -f logs/broca.log

# Note: No centralized logging - each agent maintains its own log files
# For centralized monitoring, use external log aggregation tools
```

### Database Management

```bash
# Backup agent-specific databases
cd ~/sanctum
mkdir -p backups/$(date +%Y%m%d)

# Backup all agent databases
for agent_dir in agent-*/; do
    agent_id=$(basename "$agent_dir")
    cp "$agent_dir/sanctum.db" "backups/$(date +%Y%m%d)/${agent_id}_sanctum.db"
done

# Restore specific agent database
cp backups/20241201/agent-721679f6-c8af-4e01-8677-dc042dc80368_sanctum.db \
   agent-721679f6-c8af-4e01-8677-dc042dc80368/sanctum.db
```

## 🔄 Updates and Maintenance

### Base Installation Updates

```bash
# Each agent can be updated independently
cd ~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368/broca
git pull origin main

# Update dependencies in the shared virtual environment
cd ~/sanctum
source venv/bin/activate
cd agent-721679f6-c8af-4e01-8677-dc042dc80368/broca
pip install -r requirements.txt

# Restart specific agent instance
pm2 restart broca-agent-1
# or
sudo systemctl restart broca-agent-1
```

### Agent-Specific Updates

```bash
# Update agent configuration
cd ~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368

# Edit configuration
nano .env
nano settings.json

# Restart specific agent
pm2 restart broca-agent-1
# or
sudo systemctl restart broca-agent-1
```

### Plugin Updates

```bash
# Update plugins in each agent's Broca instance
cd ~/sanctum/agent-721679f6-c8af-4e01-8677-dc042dc80368/broca
git pull origin main

# Restart agent to pick up plugin changes
pm2 restart broca-agent-1
```

## 🛡️ Security Considerations

### Isolation

- Each agent runs with its own complete Broca repository, database, and configuration
- No shared credentials or data between agents
- Separate log files prevent information leakage

### Access Control

```bash
# Set proper permissions for agent directories
chmod 700 ~/sanctum/agent-*/
chmod 600 ~/sanctum/agent-*/.env
chmod 600 ~/sanctum/agent-*/settings.json

# Restrict access to shared virtual environment
chmod 755 ~/sanctum/venv/
```

### Backup Security

```bash
# Encrypt backups
tar -czf - ~/sanctum/agent-*/sanctum.db | \
gpg --encrypt --recipient your-email@example.com > \
~/sanctum/backups/$(date +%Y%m%d)_encrypted.tar.gz.gpg
```

## 🔍 Troubleshooting

### Common Issues

#### 1. **Agent Can't Start**
```bash
# Check environment variables
cd ~/sanctum/agent-{uuid}
cat .env

# Verify virtual environment activation
source ~/sanctum/venv/bin/activate
cd broca
python -c "import telethon; print('Telethon OK')"

# Check logs
tail -f logs/broca.log
```

#### 2. **Database Connection Issues**
```bash
# Verify database file exists
ls -la ~/sanctum/agent-{uuid}/sanctum.db

# Check database permissions
chmod 644 ~/sanctum/agent-{uuid}/sanctum.db

# Test database connection
cd ~/sanctum/agent-{uuid}
source ~/sanctum/venv/bin/activate
python -m broca.cli.btool queue list
```

#### 3. **Plugin Loading Issues**
```bash
# Check plugin configuration
cat ~/sanctum/agent-{uuid}/settings.json

# Verify plugin files exist
ls -la ~/sanctum/agent-{uuid}/broca/plugins/

# Check plugin logs
tail -f ~/sanctum/agent-{uuid}/logs/broca.log
```

### Performance Monitoring

```bash
# Monitor resource usage
htop
iotop
df -h

# Check agent-specific resource usage
ps aux | grep "agent-"
lsof | grep "agent-"

# Monitor database performance
cd ~/sanctum/agent-{uuid}
source ~/sanctum/venv/bin/activate
python -m broca.cli.btool queue stats
```

## 🚀 Advanced Features

### Automated Deployment

```bash
#!/bin/bash
# deploy-agent.sh - Automated agent deployment script

AGENT_ID=$1
AGENT_ENDPOINT=$2
AGENT_API_KEY=$3

if [ -z "$AGENT_ID" ] || [ -z "$AGENT_ENDPOINT" ] || [ -z "$AGENT_API_KEY" ]; then
    echo "Usage: $0 <agent_id> <endpoint> <api_key>"
    exit 1
fi

cd ~/sanctum

# Create agent directory
mkdir -p "agent-${AGENT_ID}"
cd "agent-${AGENT_ID}"

# Clone Broca repository for this agent
git clone https://github.com/sanctumos/broca.git broca

# Copy configuration templates
cp broca/.env.example .env
cp broca/settings.json .

# Configure agent-specific settings
sed -i "s/AGENT_ID=.*/AGENT_ID=${AGENT_ID}/" .env
sed -i "s|LETTA_API_ENDPOINT=.*|LETTA_API_ENDPOINT=${AGENT_ENDPOINT}|" .env
sed -i "s/LETTA_API_KEY=.*/LETTA_API_KEY=${AGENT_API_KEY}/" .env

# Create logs directory
mkdir -p logs

echo "Agent ${AGENT_ID} deployed successfully!"
echo "Start with: cd agent-${AGENT_ID} && source ~/sanctum/venv/bin/activate && python broca/main.py"
```

### Health Monitoring

```bash
#!/bin/bash
# health-check.sh - Monitor all agent instances

cd ~/sanctum

echo "Broca 2 Agent Health Check"
echo "=========================="

for agent_dir in agent-*/; do
    agent_id=$(basename "$agent_dir")
    echo -n "Agent ${agent_id}: "
    
    if [ -f "${agent_dir}/sanctum.db" ]; then
        echo -n "DB ✓ "
    else
        echo -n "DB ✗ "
    fi
    
    if [ -f "${agent_dir}/.env" ]; then
        echo -n "ENV ✓ "
    else
        echo -n "ENV ✗ "
    fi
    
    if [ -d "${agent_dir}/logs" ]; then
        echo -n "LOGS ✓ "
    else
        echo -n "LOGS ✗ "
    fi
    
    if [ -d "${agent_dir}/broca" ]; then
        echo -n "BROCA ✓ "
    else
        echo -n "BROCA ✗ "
    fi
    
    echo ""
done

echo ""
echo "Virtual Environment:"
if [ -d "venv" ]; then
    echo "✓ Virtual environment exists"
    source venv/bin/activate
    python --version
else
    echo "✗ Virtual environment missing"
fi
```

## 📚 Additional Resources

- [Main README](../README.md) - Complete project overview
- [CLI Reference](cli_reference.md) - Command-line tool documentation
- [Configuration Guide](configuration.md) - Detailed configuration options
- [Plugin Development](plugin_development.md) - Creating custom plugins
- [Telegram Plugin](telegram-plugin-spec.md) - Telegram integration details

## 🤝 Contributing

When contributing to the multi-agent architecture:

1. **Maintain Complete Isolation**: Ensure changes don't break agent isolation
2. **Repository Independence**: Each agent should maintain its own complete Broca installation
3. **Configuration**: Support agent-specific settings without shared configurations
4. **Testing**: Test with multiple agent instances
5. **Documentation**: Update this guide for any architectural changes

## 🎯 Benefits of This Architecture

- **Complete Isolation**: Each agent runs independently with its own complete Broca repository, configuration, database, and plugin instances
- **Scalability**: Easy to add new agents without affecting existing ones
- **Maintenance**: Each agent can be updated independently by pulling from their own Broca repository
- **Backup**: Simple to backup individual agent configurations and data
- **Resource Efficiency**: Only the virtual environment is shared (Sanctum-wide, not Broca-specific)
- **Flexibility**: Each agent can have different plugins, settings, and configurations
- **Security**: No cross-agent data leakage or configuration conflicts
- **Version Control**: Each agent can run different versions of Broca if needed
