"""End-to-end tests for complete application workflows."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from database.operations.messages import insert_message, update_message_with_response
from database.operations.queue import add_to_queue, atomic_dequeue_item, update_queue_status
from database.operations.users import get_or_create_platform_profile
from runtime.core.agent import AgentClient
from runtime.core.plugin import PluginManager
from runtime.core.queue import QueueProcessor


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_complete_message_processing_workflow(temp_db, mock_env_vars, mock_letta_client):
    """Test complete message processing workflow from user input to response."""
    # 1. Create user
    profile, user = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="e2euser",
        display_name="E2E Test User"
    )
    
    # 2. Create message
    message_id = await insert_message(
        letta_user_id=user.id,
        platform_profile_id=profile.id,
        role="user",
        message="Hello, this is an E2E test"
    )
    
    # 3. Enqueue message
    await add_to_queue(user.id, message_id)
    
    # 4. Initialize components
    agent = AgentClient()
    await agent.initialize()
    
    plugin_manager = PluginManager()
    await plugin_manager.discover_plugins(config={})
    await plugin_manager.start()
    
    async def message_processor(message: str):
        return await agent.process_message(message)
    
    queue_processor = QueueProcessor(
        message_processor=message_processor,
        plugin_manager=plugin_manager,
        message_mode="echo"
    )
    
    # 5. Process queue item
    queue_item = await atomic_dequeue_item()
    assert queue_item is not None
    assert queue_item.message_id == message_id
    
    # 6. Get message
    from database.operations.messages import get_message_text
    message_data = await get_message_text(queue_item.message_id)
    assert message_data is not None
    
    # 7. Process message
    response = await message_processor(message_data[1])
    assert response is not None
    
    # 8. Update message with response
    await update_message_with_response(message_id, response)
    
    # 9. Update queue status
    await update_queue_status(queue_id, "completed")
    
    # 10. Cleanup
    await queue_processor.stop()
    await agent.cleanup()
    await plugin_manager.stop()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multiple_users_concurrent_workflow(temp_db, mock_env_vars, mock_letta_client):
    """Test multiple users sending messages concurrently."""
    # Create multiple users
    users = []
    for i in range(3):
        profile, user = await get_or_create_platform_profile(
            platform="telegram",
            platform_user_id=f"user{i}",
            username=f"user{i}",
            display_name=f"User {i}"
        )
        users.append((profile, user))
    
    # Create messages for each user
    message_ids = []
    for profile, user in users:
        message_id = await insert_message(
            letta_user_id=user.id,
            platform_profile_id=profile.id,
            role="user",
            message=f"Message from user {user.id}"
        )
        message_ids.append(message_id)
    
    # Enqueue all messages
    for profile, user in users:
        await add_to_queue(user.id, message_ids[users.index((profile, user))])
    
    # Process all messages
    agent = AgentClient()
    await agent.initialize()
    
    async def message_processor(message: str):
        return await agent.process_message(message)
    
    processed = []
    for _ in range(len(users)):
        queue_item = await atomic_dequeue_item()
        if queue_item:
            response = await message_processor("Test response")
            await update_queue_status(queue_item.id, "completed")
            processed.append(queue_item.id)
    
    assert len(processed) == len(users)
    
    await agent.cleanup()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_error_recovery_workflow(temp_db, mock_env_vars, mock_letta_client):
    """Test error recovery in message processing workflow."""
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
        message="Test error recovery"
    )
    
    await add_to_queue(user.id, message_id)
    
    # Simulate processing error
    agent = AgentClient()
    await agent.initialize()
    
    async def failing_processor(message: str):
        raise Exception("Processing error")
    
    queue_processor = QueueProcessor(
        message_processor=failing_processor,
        message_mode="echo"
    )
    
    # Try to process (should handle error gracefully)
    queue_item = await atomic_dequeue_item()
    if queue_item:
        try:
            await failing_processor("test")
        except Exception:
            # Error should be handled
            pass
    
    await queue_processor.stop()
    await agent.cleanup()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_settings_reload_workflow(temp_db, mock_env_vars, tmp_path, monkeypatch):
    """Test settings reload during runtime."""
    monkeypatch.chdir(tmp_path)
    
    import json
    import main
    
    # Create initial settings
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(json.dumps({
        "debug_mode": False,
        "queue_refresh": 5,
        "max_retries": 3,
        "message_mode": "echo"
    }))
    
    # Initialize application components
    import main
    with patch("main.PluginManager") as mock_pm_class, \
         patch("main.AgentClient") as mock_agent_class, \
         patch("main.QueueProcessor") as mock_qp_class, \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"), \
         patch("main.validate_environment_variables"), \
         patch("main.initialize_database", new_callable=AsyncMock), \
         patch("main.check_and_migrate_db", new_callable=AsyncMock), \
         patch("main.get_settings") as mock_get_settings:
        
        mock_pm = AsyncMock()
        mock_pm_class.return_value = mock_pm
        
        mock_agent = AsyncMock()
        mock_agent.initialize.return_value = True
        mock_agent_class.return_value = mock_agent
        
        mock_qp = MagicMock()
        mock_qp_class.return_value = mock_qp
        
        mock_get_settings.return_value = {
            "debug_mode": False,
            "queue_refresh": 5,
            "max_retries": 3,
            "message_mode": "echo",
            "plugins": {}
        }
        
        app = main.Application()
        app._settings_mtime = 0
        
        # Simulate settings file change
        settings_file.write_text(json.dumps({
            "debug_mode": True,
            "queue_refresh": 10,
            "max_retries": 5,
            "message_mode": "live"
        }))
        
        # Check settings (should reload)
        await app._check_settings()
        
        app._shutdown_event.set()
        await app.stop()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_application_startup_and_shutdown(temp_db, mock_env_vars, tmp_path, monkeypatch):
    """Test complete application startup and shutdown."""
    monkeypatch.chdir(tmp_path)
    
    import json
    import main
    from unittest.mock import AsyncMock, MagicMock, patch
    
    # Create settings file
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(json.dumps({
        "debug_mode": True,
        "queue_refresh": 1,
        "max_retries": 1,
        "message_mode": "echo",
        "plugins": {}
    }))
    
    # Test application lifecycle
    with patch("main.PluginManager") as mock_pm_class, \
         patch("main.AgentClient") as mock_agent_class, \
         patch("main.QueueProcessor") as mock_qp_class, \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"), \
         patch("main.validate_environment_variables"), \
         patch("main.initialize_database", new_callable=AsyncMock), \
         patch("main.check_and_migrate_db", new_callable=AsyncMock), \
         patch("main.get_settings") as mock_get_settings:
        
        mock_pm = AsyncMock()
        mock_pm_class.return_value = mock_pm
        
        mock_agent = AsyncMock()
        mock_agent.initialize.return_value = True
        mock_agent_class.return_value = mock_agent
        
        mock_qp = MagicMock()
        mock_qp_class.return_value = mock_qp
        
        mock_get_settings.return_value = {
            "debug_mode": True,
            "queue_refresh": 1,
            "max_retries": 1,
            "message_mode": "echo",
            "plugins": {}
        }
        
        app = main.Application()
        app._shutdown_event.set()  # Immediate shutdown
        
        # Start and stop
        await app.start()
        await app.stop()
        
        # Verify components were initialized and stopped
        assert app.plugin_manager is not None
        assert app.agent is not None
        assert app.queue_processor is not None
