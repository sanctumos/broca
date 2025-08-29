





---

# Broca 2 Installation Guide

## Overview
Broca 2 now uses a simple `requirements.txt` approach instead of package installation. This allows for multiple isolated instances without global conflicts.

## Installation Methods

### Method 1: Single Instance (Development)
```bash
# Clone the repository
git clone https://github.com/sanctumos/broca.git
cd broca/broca2

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Method 2: Multi-Agent Setup (Production)
```bash
# Create your sanctum directory
mkdir ~/sanctum
cd ~/sanctum

# Clone the base installation
git clone https://github.com/sanctumos/broca.git broca2
cd broca2

# Create shared virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create agent-specific instances
mkdir ~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368
cd ~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368

# Copy configuration files
cp ~/sanctum/broca2/.env.example .env
cp ~/sanctum/broca2/settings.json .

# Edit agent-specific configuration
nano .env
# Set AGENT_ID, TELEGRAM_API_ID, etc.

# Run the agent instance
python ../main.py
```

## Benefits of This Approach

1. **No Global Conflicts**: Each agent instance is completely isolated
2. **Simple Dependencies**: Just `pip install -r requirements.txt`
3. **Easy Updates**: Update the base installation once, affects all agents
4. **Flexible Configuration**: Each agent has its own `.env` and `settings.json`
5. **Independent Databases**: Each agent has its own `sanctum.db`

## CLI Tools

Instead of global commands, use module-based execution:

```bash
# Queue management
python -m cli.btool queue list
python -m cli.btool queue flush

# User management  
python -m cli.btool users list

# Settings
python -m cli.btool settings show
```

## Virtual Environment (Recommended)

For production deployments, the virtual environment is created at the top level:

```bash
# Virtual environment is shared across all agents
~/sanctum/broca2/venv/

# Activate the shared environment
source ~/sanctum/broca2/venv/bin/activate  # On Windows: venv\Scripts\activate

# Run application from agent directory
cd ~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368
python ../main.py
```

## Troubleshooting

### Import Errors
If you get import errors, ensure you're running from the correct directory:
```bash
cd ~/sanctum/broca2/agent-721679f6-c8af-4e01-8677-dc042dc80368
python ../main.py
```

### Missing Dependencies
If dependencies are missing:
```bash
cd ~/sanctum/broca2
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration Issues
Ensure each agent instance has its own:
- `.env` file with agent-specific settings
- `settings.json` with runtime configuration
- `sanctum.db` database file 