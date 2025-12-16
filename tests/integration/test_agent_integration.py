"""Integration tests for agent client."""

import pytest

from runtime.core.agent import AgentClient
from runtime.core.queue import QueueProcessor


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_client_initialization(mock_env_vars):
    """Test agent client initialization."""
    client = AgentClient()
    
    assert client is not None
    assert hasattr(client, "agent_id")
    assert hasattr(client, "debug_mode")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_client_initialize_debug_mode(mock_env_vars):
    """Test agent client initialization in debug mode."""
    import os
    from unittest.mock import patch
    with patch.dict(os.environ, {"DEBUG_MODE": "true"}):
        client = AgentClient()
        
        result = await client.initialize()
        
        assert result is True  # Should succeed in debug mode


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_client_process_message_debug_mode(mock_env_vars):
    """Test processing message in debug mode."""
    import os
    from unittest.mock import patch
    with patch.dict(os.environ, {"DEBUG_MODE": "true"}):
        client = AgentClient()
        
        response = await client.process_message("Test message")
        
        # In debug mode, should return message as-is
        assert response == "Test message"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_queue_processor_integration(temp_db, mock_env_vars, mock_letta_client):
    """Test agent client integration with queue processor."""
    from unittest.mock import patch
    
    client = AgentClient()
    
    async def mock_processor(message: str):
        return await client.process_message(message)
    
    processor = QueueProcessor(
        message_processor=mock_processor,
        message_mode="echo"
    )
    
    assert processor.message_processor is not None
    
    # Test integration
    if client.debug_mode:
        response = await mock_processor("Test")
        assert response == "Test"
    
    await processor.stop()
    await client.cleanup()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_cleanup(mock_env_vars):
    """Test agent client cleanup."""
    client = AgentClient()
    
    # Cleanup should not raise
    await client.cleanup()
    
    # Should be able to call multiple times
    await client.cleanup()
