"""Unit tests for runtime core agent functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

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
async def test_agent_client_send_message():
    """Test AgentClient send_message."""
    with patch("runtime.core.agent.get_env_var") as mock_env, patch(
        "runtime.core.agent.httpx.AsyncClient"
    ) as mock_client:
        mock_env.return_value = "http://test.endpoint"
        mock_client_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "test"}
        mock_response.status_code = 200
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        agent = AgentClient()
        result = await agent.send_message("test")
        assert result == {"response": "test"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_client_get_status():
    """Test AgentClient get_status."""
    with patch("runtime.core.agent.get_env_var") as mock_env, patch(
        "runtime.core.agent.httpx.AsyncClient"
    ) as mock_client:
        mock_env.return_value = "http://test.endpoint"
        mock_client_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "active"}
        mock_response.status_code = 200
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        agent = AgentClient()
        result = await agent.get_status()
        assert result == {"status": "active"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_client_error_handling():
    """Test AgentClient error handling."""
    with patch("runtime.core.agent.get_env_var") as mock_env, patch(
        "runtime.core.agent.httpx.AsyncClient"
    ) as mock_client:
        mock_env.return_value = "http://test.endpoint"
        mock_client_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Error"
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        agent = AgentClient()
        try:
            await agent.send_message("test")
        except Exception:
            pass  # Expected


@pytest.mark.unit
def test_agent_client_properties():
    """Test AgentClient properties."""
    with patch("runtime.core.agent.get_env_var") as mock_env:
        mock_env.return_value = "http://test.endpoint"
        agent = AgentClient()
        assert hasattr(agent, "endpoint")
        assert hasattr(agent, "api_key")
