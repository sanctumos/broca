"""Integration tests for runtime components."""

import pytest

from runtime.core.agent import AgentClient
from runtime.core.plugin import PluginManager
from runtime.core.queue import QueueProcessor


@pytest.mark.integration
@pytest.mark.asyncio
async def test_runtime_components_initialization(temp_db, mock_env_vars):
    """Test all runtime components can be initialized together."""
    # Initialize components
    agent = AgentClient()
    plugin_manager = PluginManager()
    
    async def mock_processor(message: str):
        return f"Processed: {message}"
    
    queue_processor = QueueProcessor(
        message_processor=mock_processor,
        plugin_manager=plugin_manager
    )
    
    # Verify all components initialized
    assert agent is not None
    assert plugin_manager is not None
    assert queue_processor is not None
    
    # Cleanup
    await queue_processor.stop()
    await agent.cleanup()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_runtime_components_lifecycle(temp_db, mock_env_vars):
    """Test complete lifecycle of runtime components."""
    # Initialize
    agent = AgentClient()
    plugin_manager = PluginManager()
    
    async def mock_processor(message: str):
        return "Response"
    
    queue_processor = QueueProcessor(
        message_processor=mock_processor,
        plugin_manager=plugin_manager
    )
    
    # Start components
    await agent.initialize()
    await plugin_manager.discover_plugins(config={})
    await plugin_manager.start()
    
    # Stop components
    await queue_processor.stop()
    await agent.cleanup()
    await plugin_manager.stop()
    
    # Verify cleanup completed
    assert not queue_processor.is_running


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_flow_integration(temp_db, mock_env_vars, mock_letta_client):
    """Test complete message flow through runtime components."""
    from database.operations.messages import insert_message
    from database.operations.queue import add_to_queue
    from database.operations.users import get_or_create_platform_profile
    
    # Setup components
    agent = AgentClient()
    plugin_manager = PluginManager()
    
    async def message_processor(message: str):
        return await agent.process_message(message)
    
    queue_processor = QueueProcessor(
        message_processor=message_processor,
        plugin_manager=plugin_manager,
        message_mode="echo"
    )
    
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
        message="Integration test"
    )
    
    await add_to_queue(user.id, message_id)
    
    # Initialize components
    await agent.initialize()
    await plugin_manager.discover_plugins(config={})
    await plugin_manager.start()
    
    # Verify integration
    assert queue_processor.plugin_manager == plugin_manager
    
    # Cleanup
    await queue_processor.stop()
    await agent.cleanup()
    await plugin_manager.stop()
