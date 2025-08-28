"""
Simple test for Web Chat Plugin without database dependencies

This script tests the basic plugin structure and settings without requiring
the full Broca2 database and runtime dependencies.
"""

import asyncio
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class SimpleWebChatSettings:
    """Simplified settings for testing."""
    
    api_url: str = field(default="http://localhost:8000")
    api_key: str = field(default="")
    poll_interval: int = field(default=5)
    max_retries: int = field(default=3)
    retry_delay: int = field(default=10)
    plugin_name: str = field(default="web_chat")
    platform_name: str = field(default="web_chat")
    
    def __post_init__(self):
        """Validate settings after initialization."""
        if not self.api_url:
            raise ValueError("API URL is required")
        
        if not self.api_key:
            raise ValueError("API key is required")
    
    @classmethod
    def from_env(cls) -> 'SimpleWebChatSettings':
        """Create settings from environment variables."""
        return cls(
            api_url=os.getenv('WEB_CHAT_API_URL', 'http://localhost:8000'),
            api_key=os.getenv('WEB_CHAT_API_KEY', 'test_key'),
            poll_interval=int(os.getenv('WEB_CHAT_POLL_INTERVAL', '5')),
            max_retries=int(os.getenv('WEB_CHAT_MAX_RETRIES', '3')),
            retry_delay=int(os.getenv('WEB_CHAT_RETRY_DELAY', '10')),
            plugin_name=os.getenv('WEB_CHAT_PLUGIN_NAME', 'web_chat'),
            platform_name=os.getenv('WEB_CHAT_PLATFORM_NAME', 'web_chat'),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            'api_url': self.api_url,
            'api_key': self.api_key,
            'poll_interval': self.poll_interval,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'plugin_name': self.plugin_name,
            'platform_name': self.platform_name,
        }
    
    def validate_settings(self) -> bool:
        """Validate all settings."""
        try:
            self.__post_init__()
            return True
        except ValueError:
            return False


class SimpleWebChatPlugin:
    """Simplified Web Chat Plugin for testing."""
    
    def __init__(self, settings: Optional[SimpleWebChatSettings] = None):
        self.settings = settings or SimpleWebChatSettings.from_env()
        self.is_running = False
        self.logger = None  # Would be logging.getLogger(__name__)
    
    def get_name(self) -> str:
        """Get the plugin name."""
        return self.settings.plugin_name
    
    def get_platform(self) -> str:
        """Get the platform name."""
        return self.settings.platform_name
    
    def get_settings(self) -> Dict[str, Any]:
        """Get plugin settings."""
        return self.settings.to_dict()
    
    def validate_settings(self) -> bool:
        """Validate plugin settings."""
        return self.settings.validate_settings()


async def test_basic_functionality():
    """Test basic plugin functionality."""
    print("Testing basic Web Chat Plugin functionality...")
    
    try:
        # Test settings creation
        settings = SimpleWebChatSettings(
            api_url="http://localhost:8000",
            api_key="test_api_key",
            poll_interval=5
        )
        print(f"✅ Settings created: {settings.api_url}")
        
        # Test settings validation
        assert settings.validate_settings()
        print("✅ Settings validation passed")
        
        # Test plugin creation
        plugin = SimpleWebChatPlugin(settings)
        print(f"✅ Plugin created: {plugin.get_name()}")
        
        # Test plugin methods
        assert plugin.get_name() == "web_chat"
        assert plugin.get_platform() == "web_chat"
        assert plugin.validate_settings()
        print("✅ Plugin methods working correctly")
        
        # Test settings round-trip
        settings_dict = settings.to_dict()
        new_settings = SimpleWebChatSettings(**settings_dict)
        assert new_settings.api_url == settings.api_url
        print("✅ Settings round-trip test passed")
        
        print("🎉 All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


async def test_environment_loading():
    """Test environment variable loading."""
    print("\nTesting environment variable loading...")
    
    try:
        # Set test environment variables
        os.environ['WEB_CHAT_API_URL'] = 'http://test.example.com'
        os.environ['WEB_CHAT_API_KEY'] = 'test_env_key'
        
        # Test from_env
        settings = SimpleWebChatSettings.from_env()
        assert settings.api_url == 'http://test.example.com'
        assert settings.api_key == 'test_env_key'
        print("✅ Environment variable loading passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment loading test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("Web Chat Plugin Simple Test Suite")
    print("=" * 40)
    
    results = []
    
    # Test basic functionality
    results.append(await test_basic_functionality())
    
    # Test environment loading
    results.append(await test_environment_loading())
    
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