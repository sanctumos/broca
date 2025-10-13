"""Unit tests for runtime core agent functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from runtime.core.agent import AgentClient


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_client_initialization():
    """Test AgentClient initialization."""
    with patch("runtime.core.agent.get_env_var") as mock_env:
        mock_env.return_value = "http://test.endpoint"

        agent = AgentClient()
        assert agent is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_client_send_message():
    """Test AgentClient send_message method."""
    with patch("runtime.core.agent.get_env_var") as mock_env, patch(
        "runtime.core.agent.httpx.AsyncClient"
    ) as mock_client_class:
        mock_env.return_value = "http://test.endpoint"
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "test response"}
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        agent = AgentClient()
        result = await agent.send_message("test message")

        assert result == {"response": "test response"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_client_send_message_error():
    """Test AgentClient send_message with error response."""
    with patch("runtime.core.agent.get_env_var") as mock_env, patch(
        "runtime.core.agent.httpx.AsyncClient"
    ) as mock_client_class:
        mock_env.return_value = "http://test.endpoint"
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        agent = AgentClient()

        with pytest.raises(Exception):
            await agent.send_message("test message")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_client_get_status():
    """Test AgentClient get_status method."""
    with patch("runtime.core.agent.get_env_var") as mock_env, patch(
        "runtime.core.agent.httpx.AsyncClient"
    ) as mock_client_class:
        mock_env.return_value = "http://test.endpoint"
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "active"}
        mock_response.status_code = 200
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        agent = AgentClient()
        result = await agent.get_status()

        assert result == {"status": "active"}
