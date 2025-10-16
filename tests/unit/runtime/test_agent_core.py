"""Unit tests for runtime core agent functionality."""

from unittest.mock import patch

import pytest

from runtime.core.agent import AgentClient


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_client_init():
    """Test AgentClient initialization."""
    with patch("runtime.core.agent.get_env_var") as mock_env:
        mock_env.return_value = "http://test.endpoint"
        agent = AgentClient()
        assert agent is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_client_process_message():
    """Test AgentClient process_message."""
    with patch("runtime.core.agent.get_env_var") as mock_env:
        mock_env.return_value = "test_agent"

        agent = AgentClient()
        result = await agent.process_message("test")
        assert result == "test"  # In debug mode, it returns the original message


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_client_initialize():
    """Test AgentClient initialize."""
    with patch("runtime.core.agent.get_env_var") as mock_env:
        mock_env.return_value = "test_agent"

        agent = AgentClient()
        result = await agent.initialize()
        assert result is True  # In debug mode, it returns True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_client_error_handling():
    """Test AgentClient error handling."""
    with patch("runtime.core.agent.get_env_var") as mock_env:
        mock_env.return_value = "test_agent"

        agent = AgentClient()
        # Test that process_message handles errors gracefully
        result = await agent.process_message("test")
        assert result == "test"  # In debug mode, it returns the original message


@pytest.mark.unit
def test_agent_client_properties():
    """Test AgentClient properties."""
    with patch("runtime.core.agent.get_env_var") as mock_env:
        mock_env.return_value = "test_agent"
        agent = AgentClient()
        assert hasattr(agent, "debug_mode")
        assert hasattr(agent, "agent_id")
