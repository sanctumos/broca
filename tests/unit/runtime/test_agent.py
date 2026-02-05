"""Unit tests for runtime core agent functionality."""

import os
from unittest.mock import MagicMock, patch

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
    """Test AgentClient process_message method."""
    with patch.dict(
        os.environ, {"DEBUG_MODE": "false", "AGENT_ID": "test-agent-123"}
    ), patch("runtime.core.agent.get_letta_client") as mock_get_client:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.messages = [
            MagicMock(content="test response", message_type="assistant")
        ]
        mock_client.agents.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        agent = AgentClient()
        result = await agent.process_message("test message")

        assert result == "test response"
        # Explicit messages= (single user message) to avoid input/tool ambiguity
        call = mock_client.agents.messages.create.call_args
        assert call[0][0] == "test-agent-123"
        msgs = call[1]["messages"]
        assert len(msgs) == 1
        m = msgs[0]
        assert (m.get("role") or getattr(m, "role", None)) == "user"
        content = (
            m.get("content") if isinstance(m, dict) else getattr(m, "content", None)
        )
        assert content == "test message"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_client_send_message_error():
    """Test AgentClient process_message with error response."""
    with patch.dict(
        os.environ, {"DEBUG_MODE": "false", "AGENT_ID": "test-agent-123"}
    ), patch("runtime.core.agent.get_letta_client") as mock_get_client, patch(
        "runtime.core.agent.is_retryable_exception"
    ) as mock_retryable:
        mock_client = MagicMock()
        mock_client.agents.messages.create.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client
        # Make the exception non-retryable so it gets raised immediately
        mock_retryable.return_value = False

        agent = AgentClient()
        result = await agent.process_message("test message")

        # The method catches exceptions and returns None
        assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_client_get_status():
    """Test AgentClient initialize method."""
    with patch.dict(
        os.environ, {"DEBUG_MODE": "false", "AGENT_ID": "test-agent-123"}
    ), patch("runtime.core.agent.get_letta_client") as mock_get_client:
        mock_client = MagicMock()
        mock_agent = MagicMock()
        mock_agent.id = "test-agent-123"
        mock_agent.name = "Test Agent"
        mock_client.agents.retrieve.return_value = mock_agent
        mock_get_client.return_value = mock_client

        agent = AgentClient()
        result = await agent.initialize()

        assert result is True
