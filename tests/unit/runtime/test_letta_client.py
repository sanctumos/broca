"""Unit tests for runtime core letta_client functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from runtime.core.letta_client import LettaClient, get_letta_client


@pytest.mark.unit
@pytest.mark.asyncio
async def test_letta_client_initialization():
    """Test LettaClient initialization."""
    with patch("runtime.core.letta_client.LettaClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        client = LettaClient()
        assert client is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_letta_client_singleton():
    """Test get_letta_client returns singleton instance."""
    with patch("runtime.core.letta_client.LettaClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        client1 = get_letta_client()
        client2 = get_letta_client()

        # Should return the same instance (singleton)
        assert client1 is client2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_letta_client_add_to_queue():
    """Test LettaClient add_to_queue method."""
    with patch("runtime.core.letta_client.LettaClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.add_to_queue = AsyncMock(return_value={"id": "test-id"})
        mock_client_class.return_value = mock_client

        client = get_letta_client()
        result = await client.add_to_queue("test message", 123)

        assert result == {"id": "test-id"}
        mock_client.add_to_queue.assert_called_once_with("test message", 123)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_letta_client_send_message():
    """Test LettaClient send_message method."""
    with patch("runtime.core.letta_client.LettaClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.send_message = AsyncMock(return_value={"response": "test response"})
        mock_client_class.return_value = mock_client

        client = get_letta_client()
        result = await client.send_message("test message", 123)

        assert result == {"response": "test response"}
        mock_client.send_message.assert_called_once_with("test message", 123)
