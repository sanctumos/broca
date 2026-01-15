"""Unit tests for runtime core letta_client functionality."""

from unittest.mock import MagicMock, patch

import pytest

from runtime.core.letta_client import LettaClient, get_letta_client


@pytest.mark.unit
def test_letta_client_initialization():
    """Test LettaClient initialization with v1.0+ API (api_key parameter)."""
    with patch("runtime.core.letta_client.get_env_var") as mock_env, patch(
        "runtime.core.letta_client.Letta"
    ) as mock_letta_class:
        mock_env.side_effect = lambda key, **kwargs: {
            "AGENT_ENDPOINT": "http://test.endpoint",
            "AGENT_API_KEY": "test-api-key",
        }.get(key)
        mock_letta_instance = MagicMock()
        mock_letta_class.return_value = mock_letta_instance

        client = LettaClient()

        assert client is not None
        # Verify Letta was called with api_key (v1.0+ API) not token
        mock_letta_class.assert_called_once_with(
            base_url="http://test.endpoint",
            api_key="test-api-key"
        )


@pytest.mark.unit
def test_get_letta_client_singleton():
    """Test get_letta_client returns singleton instance."""
    with patch("runtime.core.letta_client.LettaClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Clear singleton
        import runtime.core.letta_client
        runtime.core.letta_client._letta_client = None

        client1 = get_letta_client()
        client2 = get_letta_client()

        # Should return the same instance (singleton)
        assert client1 is client2


@pytest.mark.unit
def test_letta_client_properties():
    """Test LettaClient property accessors."""
    with patch("runtime.core.letta_client.get_env_var") as mock_env, patch(
        "runtime.core.letta_client.Letta"
    ) as mock_letta_class:
        mock_env.side_effect = lambda key, **kwargs: {
            "AGENT_ENDPOINT": "http://test.endpoint",
            "AGENT_API_KEY": "test-api-key",
        }.get(key)
        
        mock_letta_instance = MagicMock()
        mock_agents = MagicMock()
        mock_blocks = MagicMock()
        mock_identities = MagicMock()
        mock_conversations = MagicMock()
        
        mock_letta_instance.agents = mock_agents
        mock_letta_instance.blocks = mock_blocks
        mock_letta_instance.identities = mock_identities
        mock_letta_instance.conversations = mock_conversations
        mock_letta_class.return_value = mock_letta_instance

        client = LettaClient()

        # Test property accessors
        assert client.agents == mock_agents
        assert client.blocks == mock_blocks
        assert client.identities == mock_identities
        assert client.conversations == mock_conversations
        assert client.client == mock_letta_instance


@pytest.mark.unit
def test_letta_client_close():
    """Test LettaClient close method."""
    with patch("runtime.core.letta_client.get_env_var") as mock_env, patch(
        "runtime.core.letta_client.Letta"
    ):
        mock_env.side_effect = lambda key, **kwargs: {
            "AGENT_ENDPOINT": "http://test.endpoint",
            "AGENT_API_KEY": "test-api-key",
        }.get(key)

        client = LettaClient()
        # Should not raise an exception
        client.close()
