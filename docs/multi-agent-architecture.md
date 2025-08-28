# ⚠️ REPOSITORY MOVED ⚠️

**This repository has moved to: [http://github.com/sanctumos/broca](http://github.com/sanctumos/broca)**

Please update your git remotes and use the new repository location for all future development and contributions.

---

# Multi-Agent Architecture Guide

## Overview

Broca 2 now supports running multiple Letta agent instances from a single base installation. This architecture provides isolation between agents while sharing common resources, making it efficient to manage multiple AI agents on the same system.

## 🏗️ Architecture Principles

### 1. **Instance Isolation**
- Each agent runs in its own directory with separate configuration
- Independent databases prevent data cross-contamination
- Separate log files for easy debugging and monitoring

### 2. **Shared Resources**
- Base Broca 2 installation shared across all instances
- Common virtual environment reduces disk usage and maintenance
- Shared plugins and runtime components

### 3. **Simple Management**
- Clear 1:1 mapping between agent IDs and instance folders
- Standardized folder structure for easy automation
- Git-based updates that preserve agent-specific configurations

## 📁 Directory Structure

```
~/sanctum/broca2/             # Base Broca 2 installation
├── venv/                     # Shared virtual environment
├── main.py                   # Core runtime entry point
├── runtime/                  # Core system components
├── plugins/                  # Available plugins
├── cli/                      # CLI tools
├── common/                   # Shared utilities
├── database/                 # Database models
├── requirements.txt          # Python dependencies
├── .env.example             # Base configuration template
├── settings.json            # Base settings template
├── agent-{uuid}/            # Agent-specific instance
│   ├── .env                 # Agent-specific environment
│   ├── settings.json        # Agent-specific settings
│   ├── sanctum.db          # Agent-specific database
│   └── logs/               # Agent-specific logs
├── agent-{uuid}/            # Another agent instance
│   ├── .env
│   ├── settings.json
│   ├── sanctum.db
│   └── logs/
└── shared/                  # Shared resources (optional)
    ├── templates/           # Common templates
    ├── configs/            # Shared configurations
    └── backups/            # Backup storage
```

## 🚀 Setup Instructions

### Step 1: Create Sanctum Directory Structure

```bash
# Create the main sanctum directory
mkdir ~/sanctum
cd ~/sanctum

# Clone the base Broca 2 installation
git clone https://github.com/sanctumos/broca.git broca2
cd broca2

# Create shared virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure Base Installation

```bash
# Copy and configure base environment
cp .env.example .env
nano .env

# Set base configuration (shared across all agents)
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
TELEGRAM_PHONE=your_phone_number
DEBUG_MODE=false
```

### Step 3: Create Agent Instances

```bash
# For each Letta agent, create a folder named after the agent ID
mkdir agent-721679f6-c8af-4e01-8677-dc042dc80368
cd agent-721679f6-c8af-4e01-8677-dc042dc80368

# Copy base configuration templates
cp ../.env.example .env
cp ../settings.json .

# Edit agent-specific configuration
nano .env

# Set agent-specific variables
AGENT_ID=721679f6-c8af-4e01-8677-dc042dc80368
LETTA_API_ENDPOINT=https://your-letta-instance.com/api/v1
LETTA_API_KEY=your_agent_specific_api_key
DEBUG_MODE=false
MESSAGE_MODE=live
```

### Step 4: Run Agent Instances

```bash
# From the agent folder
cd ~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368

# Run the agent instance
python ../main.py

# Or use CLI tools
python -m cli.btool queue list
python -m cli.btool users list
```

## 🔧 Configuration Management

### Environment Variables

#### Base Installation (.env in broca2 root)
```bash
# Telegram API configuration (shared)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number

# System configuration
DEBUG_MODE=false
LOG_LEVEL=INFO
```

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

#### Base Settings (settings.json in broca2 root)
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
cd ~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368
python ../main.py

# Terminal 2: Start second agent
cd ~/sanctum/broca2/agent-9a2b3c4d-5e6f-7890-abcd-ef1234567890
python ../main.py
```

### Process Manager (PM2)

```bash
# Install PM2 if not already installed
npm install -g pm2

# Start agents with PM2
cd ~/sanctum/broca2

pm2 start "broca-agent-1" --interpreter python -- agent-721679f6-c8af-4e01-8677-dc042dc80368/main.py
pm2 start "broca-agent-2" --interpreter python -- agent-9a2b3c4d-5e6f-7890-abcd-ef1234567890/main.py

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
WorkingDirectory=/home/your_username/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368
ExecStart=/home/your_username/sanctum/broca2/venv/bin/python ../main.py
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
cd ~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368
python -m cli.btool queue list
python -m cli.btool queue flush

# User management
python -m cli.btool users list

# Settings management
python -m cli.ctool settings show
python -m cli.ctool settings set message_mode live
```

### Log Management

```bash
# View agent-specific logs
cd ~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368
tail -f logs/broca.log

# Centralized log viewing (if symlinked)
tail -f ~/sanctum/broca2/logs/agent-721679f6-c8af-4e01-8677-dc042dc80368.log

# Log rotation and cleanup
find ~/sanctum/broca2/agent-*/logs -name "*.log" -mtime +7 -delete
```

### Database Management

```bash
# Backup agent-specific databases
cd ~/sanctum/broca2
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
# Update base Broca 2 installation
cd ~/sanctum/broca2
git pull origin main

# Update shared virtual environment
source venv/bin/activate
pip install -r requirements.txt

# Restart all agent instances
pm2 restart all
# or
sudo systemctl restart broca-agent-*
```

### Agent-Specific Updates

```bash
# Update agent configuration
cd ~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368

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
# Update plugins in base installation
cd ~/sanctum/broca2
git pull origin main

# Restart agents to pick up plugin changes
pm2 restart all
```

## 🛡️ Security Considerations

### Isolation

- Each agent runs with its own database and configuration
- No shared credentials between agents
- Separate log files prevent information leakage

### Access Control

```bash
# Set proper permissions for agent directories
chmod 700 ~/sanctum/broca2/agent-*/
chmod 600 ~/sanctum/broca2/agent-*/.env
chmod 600 ~/sanctum/broca2/agent-*/settings.json

# Restrict access to shared resources
chmod 755 ~/sanctum/broca2/shared/
chmod 644 ~/sanctum/broca2/shared/*
```

### Backup Security

```bash
# Encrypt backups
tar -czf - ~/sanctum/broca2/agent-*/sanctum.db | \
gpg --encrypt --recipient your-email@example.com > \
~/sanctum/broca2/backups/$(date +%Y%m%d)_encrypted.tar.gz.gpg
```

## 🔍 Troubleshooting

### Common Issues

#### 1. **Agent Can't Start**
```bash
# Check environment variables
cd ~/sanctum/broca2/agent-{uuid}
cat .env

# Verify virtual environment activation
source ../venv/bin/activate
python -c "import telethon; print('Telethon OK')"

# Check logs
tail -f logs/broca.log
```

#### 2. **Database Connection Issues**
```bash
# Verify database file exists
ls -la ~/sanctum/broca2/agent-{uuid}/sanctum.db

# Check database permissions
chmod 644 ~/sanctum/broca2/agent-{uuid}/sanctum.db

# Test database connection
cd ~/sanctum/broca2/agent-{uuid}
python -m cli.btool queue list
```

#### 3. **Plugin Loading Issues**
```bash
# Check plugin configuration
cat ~/sanctum/broca2/agent-{uuid}/settings.json

# Verify plugin files exist
ls -la ~/sanctum/broca2/plugins/

# Check plugin logs
tail -f ~/sanctum/broca2/agent-{uuid}/logs/broca.log
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
cd ~/sanctum/broca2/agent-{uuid}
python -m cli.btool queue stats
```

## 🚀 Advanced Features

### Shared Resources

```bash
# Create shared templates
mkdir -p ~/sanctum/broca2/shared/templates
cp ~/sanctum/broca2/plugins/telegram/templates/* ~/sanctum/broca2/shared/templates/

# Symlink shared resources to agent instances
cd ~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368
ln -s ../shared/templates templates
ln -s ../shared/configs configs
```

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

cd ~/sanctum/broca2

# Create agent directory
mkdir -p "agent-${AGENT_ID}"
cd "agent-${AGENT_ID}"

# Copy configuration templates
cp ../.env.example .env
cp ../settings.json .

# Configure agent-specific settings
sed -i "s/AGENT_ID=.*/AGENT_ID=${AGENT_ID}/" .env
sed -i "s|LETTA_API_ENDPOINT=.*|LETTA_API_ENDPOINT=${AGENT_ENDPOINT}|" .env
sed -i "s/LETTA_API_KEY=.*/LETTA_API_KEY=${AGENT_API_KEY}/" .env

# Create logs directory
mkdir -p logs

echo "Agent ${AGENT_ID} deployed successfully!"
echo "Start with: cd agent-${AGENT_ID} && python ../main.py"
```

### Health Monitoring

```bash
#!/bin/bash
# health-check.sh - Monitor all agent instances

cd ~/sanctum/broca2

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

1. **Maintain Isolation**: Ensure changes don't break agent isolation
2. **Shared Resources**: Consider impact on shared components
3. **Configuration**: Support both base and agent-specific settings
4. **Testing**: Test with multiple agent instances
5. **Documentation**: Update this guide for any architectural changes
