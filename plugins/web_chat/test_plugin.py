"""
Simple test script for the Web Chat Plugin

This script tests basic plugin functionality without requiring a running API.
"""

import asyncio
import os
import sys

# Add the broca2 directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from plugins.web_chat.plugin import WebChatPlugin
from plugins.web_chat.settings import WebChatSettings


async def test_plugin_initialization():
    """Test that the plugin can be initialized correctly."""
    print("Testing Web Chat Plugin initialization...")
    
    try:
        # Create settings with test values
        settings = WebChatSettings(
            api_url="http://localhost:8000",
            api_key="test_api_key",
            poll_interval=5,
            max_retries=3,
            retry_delay=10
        )
        
        # Create plugin
        plugin = WebChatPlugin(settings)
        
        # Test basic methods
        print(f"Plugin name: {plugin.get_name()}")
        print(f"Platform: {plugin.get_platform()}")
        print(f"Settings valid: {plugin.validate_settings()}")
        
        # Test message handler
        handler = plugin.get_message_handler()
        print(f"Message handler created: {handler is not None}")
        
        print("✅ Plugin initialization test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Plugin initialization test failed: {e}")
        return False


async def test_settings():
    """Test settings functionality."""
    print("\nTesting settings...")
    
    try:
        # Test from_env
        settings = WebChatSettings.from_env()
        print(f"Settings from env: {settings.api_url}")
        
        # Test to_dict and from_dict
        settings_dict = settings.to_dict()
        new_settings = WebChatSettings.from_dict(settings_dict)
        print(f"Settings round-trip test: {new_settings.api_url == settings.api_url}")
        
        print("✅ Settings test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Settings test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("Web Chat Plugin Test Suite")
    print("=" * 40)
    
    results = []
    
    # Test plugin initialization
    results.append(await test_plugin_initialization())
    
    # Test settings
    results.append(await test_settings())
    
    # Summary
    print("\n" + "=" * 40)
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed!")
    
    return all(results)


if __name__ == "__main__":
    asyncio.run(main()) 