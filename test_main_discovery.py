#!/usr/bin/env python3
"""
Test script for main.py auto-discovery functionality
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from runtime.core.plugin import PluginManager
from common.config import get_settings

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_main_discovery():
    """Test the main.py discovery functionality."""
    logger.info("🧪 Testing main.py auto-discovery...")
    
    # Create plugin manager
    plugin_manager = PluginManager()
    
    # Load settings (like main.py does)
    settings = get_settings()
    logger.info(f"📋 Loaded settings: {list(settings.keys())}")
    
    # Discover plugins (like main.py does)
    logger.info("🔄 Discovering plugins...")
    await plugin_manager.discover_plugins(config=settings.get('plugins', {}))
    
    # Check what plugins were loaded
    loaded_plugins = plugin_manager.get_loaded_plugins()
    logger.info(f"📦 Loaded plugins: {loaded_plugins}")
    
    # Start plugins (like main.py does)
    logger.info("🔄 Starting plugin manager...")
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
    logger.info("✅ Main.py auto-discovery test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_main_discovery()) 