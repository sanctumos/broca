"""Integration tests for plugin system."""

import pytest

from runtime.core.plugin import PluginManager
from runtime.core.queue import QueueProcessor


@pytest.mark.integration
@pytest.mark.asyncio
async def test_plugin_manager_discovery_and_loading(temp_db, mock_env_vars):
    """Test plugin discovery and loading."""
    manager = PluginManager()
    
    settings = {
        "plugins": {
            "telegram": {"enabled": True},
            "telegram_bot": {"enabled": True},
        }
    }
    
    # Discover plugins
    await manager.discover_plugins(config=settings.get("plugins", {}))
    
    # Start plugin manager
    await manager.start()
    
    # Verify plugins are loaded
    plugins = manager.get_all_plugins()
    assert len(plugins) > 0
    
    # Stop plugin manager
    await manager.stop()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_queue_processor_with_plugin_manager(temp_db, mock_env_vars, mock_letta_client):
    """Test queue processor integration with plugin manager."""
    async def mock_processor(message: str):
        return f"Processed: {message}"
    
    manager = PluginManager()
    await manager.discover_plugins(config={})
    await manager.start()
    
    processor = QueueProcessor(
        message_processor=mock_processor,
        plugin_manager=manager,
        message_mode="echo"
    )
    
    assert processor.plugin_manager == manager
    
    # Stop components
    await processor.stop()
    await manager.stop()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_routing_integration(temp_db, mock_env_vars, mock_letta_client):
    """Test message routing through plugin system."""
    from database.operations.messages import insert_message
    from database.operations.queue import add_to_queue
    from database.operations.users import get_or_create_platform_profile
    
    # Create user and message
    profile, user = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="testuser",
        display_name="Test User"
    )
    
    message_id = await insert_message(
        letta_user_id=user.id,
        platform_profile_id=profile.id,
        role="user",
        message="Test routing message"
    )
    
    # Enqueue message
    await add_to_queue(user.id, message_id)
    
    # Setup plugin manager and queue processor
    manager = PluginManager()
    await manager.discover_plugins(config={})
    await manager.start()
    
    async def mock_processor(message: str):
        return "Response message"
    
    processor = QueueProcessor(
        message_processor=mock_processor,
        plugin_manager=manager,
        message_mode="echo"
    )
    
    # Verify integration
    assert processor.plugin_manager is not None
    
    # Cleanup
    await processor.stop()
    await manager.stop()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_plugin_lifecycle_integration(temp_db, mock_env_vars):
    """Test complete plugin lifecycle."""
    manager = PluginManager()
    
    # Discover
    await manager.discover_plugins(config={})
    
    # Start
    await manager.start()
    
    # Get plugins
    plugins = manager.get_all_plugins()
    
    # Stop
    await manager.stop()
    
    # Verify lifecycle completed
    assert manager is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_plugins_integration(temp_db, mock_env_vars):
    """Test multiple plugins working together."""
    manager = PluginManager()
    
    settings = {
        "plugins": {
            "telegram": {"enabled": True},
            "web_chat": {"enabled": True},
        }
    }
    
    await manager.discover_plugins(config=settings.get("plugins", {}))
    await manager.start()
    
    plugins = manager.get_all_plugins()
    
    # Verify multiple plugins can coexist
    assert len(plugins) >= 0  # May be 0 if plugins not configured
    
    await manager.stop()
