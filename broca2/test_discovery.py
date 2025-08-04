#!/usr/bin/env python3
"""
Test script for plugin discovery functionality
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the broca2 directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from runtime.core.plugin import PluginManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_discovery():
    """Test the plugin discovery functionality."""
    logger.info("🧪 Testing plugin discovery...")
    
    # Create plugin manager
    plugin_manager = PluginManager()
    
    # Test configuration
    config = {
        "fake_plugin": {
            "enabled": True,
            "message": "Hello from test config!",
            "debug": True
        }
    }
    
    # Discover plugins
    await plugin_manager.discover_plugins(config=config)
    
    # Check what plugins were loaded
    loaded_plugins = plugin_manager.get_loaded_plugins()
    logger.info(f"📦 Loaded plugins: {loaded_plugins}")
    
    # Start plugins
    await plugin_manager.start()
    
    # Check if plugins are running
    for plugin_name in loaded_plugins:
        plugin = plugin_manager.get_plugin(plugin_name)
        if plugin:
            logger.info(f"✅ Plugin {plugin_name} is loaded and running")
        else:
            logger.error(f"❌ Plugin {plugin_name} not found")
    
    # Stop plugins
    await plugin_manager.stop()
    logger.info("🛑 All plugins stopped")

if __name__ == "__main__":
    asyncio.run(test_discovery()) 