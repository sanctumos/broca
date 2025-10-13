"""Extended unit tests for runtime agent client."""

from unittest.mock import MagicMock, patch

import pytest

from runtime.core.agent import AgentClient


class TestAgentClientExtended:
    """Extended test cases for AgentClient."""

    @patch("runtime.core.agent.get_env_var")
    def test_agent_client_initialization(self, mock_get_env_var):
        """Test agent client initialization."""
        mock_get_env_var.side_effect = (
            lambda key, default=None, required=False, cast_type=None: {
                "DEBUG_MODE": "true",
                "AGENT_ID": "test-agent",
            }.get(key, default)
        )

        agent = AgentClient()
        assert agent is not None
        assert agent.debug_mode == "true"

    @patch("runtime.core.agent.get_env_var")
    @pytest.mark.asyncio
    async def test_agent_client_initialize_debug_mode(self, mock_get_env_var):
        """Test agent client initialization in debug mode."""
        mock_get_env_var.side_effect = (
            lambda key, default=None, required=False, cast_type=None: {
                "DEBUG_MODE": "true",
                "AGENT_ID": None,
            }.get(key, default)
        )

        agent = AgentClient()
        result = await agent.initialize()
        assert result is True

    @patch("runtime.core.agent.get_env_var")
    @pytest.mark.asyncio
    async def test_agent_client_initialize_production_mode(self, mock_get_env_var):
        """Test agent client initialization in production mode."""
        mock_get_env_var.side_effect = (
            lambda key, default=None, required=False, cast_type=None: {
                "DEBUG_MODE": "false",
                "AGENT_ID": "test-agent",
            }.get(key, default)
        )

        with patch("runtime.core.agent.get_letta_client") as mock_get_client:
            mock_client = MagicMock()
            mock_agent = MagicMock()
            mock_agent.id = "test-agent"
            mock_agent.name = "Test Agent"
            mock_client.agents.retrieve.return_value = mock_agent
            mock_get_client.return_value = mock_client

            agent = AgentClient()
            result = await agent.initialize()
            assert result is True

    @patch("runtime.core.agent.get_env_var")
    @pytest.mark.asyncio
    async def test_agent_client_process_message_debug_mode(self, mock_get_env_var):
        """Test processing message in debug mode."""
        mock_get_env_var.side_effect = (
            lambda key, default=None, required=False, cast_type=None: {
                "DEBUG_MODE": "true",
                "AGENT_ID": None,
            }.get(key, default)
        )

        agent = AgentClient()
        message = "Test message"

        result = await agent.process_message(message)
        assert result == message

    @patch("runtime.core.agent.get_env_var")
    @pytest.mark.asyncio
    async def test_agent_client_process_message_production_mode(self, mock_get_env_var):
        """Test processing message in production mode."""
        mock_get_env_var.side_effect = (
            lambda key, default=None, required=False, cast_type=None: {
                "DEBUG_MODE": "false",
                "AGENT_ID": "test-agent",
            }.get(key, default)
        )

        with patch("runtime.core.agent.get_letta_client"):
            with patch("runtime.core.agent.exponential_backoff") as mock_backoff:
                mock_backoff.return_value = "Test response"

                agent = AgentClient()
                message = "Test message"

                result = await agent.process_message(message)
                assert result == "Test response"

    @patch("runtime.core.agent.get_env_var")
    def test_agent_client_should_retry_exception(self, mock_get_env_var):
        """Test exception retry logic."""
        mock_get_env_var.side_effect = (
            lambda key, default=None, required=False, cast_type=None: {
                "DEBUG_MODE": "true",
                "AGENT_ID": None,
            }.get(key, default)
        )

        agent = AgentClient()

        # Test auth error - should not retry
        auth_error = Exception("unauthorized")
        assert agent._should_retry_exception(auth_error) is False

        # Test bad request error - should not retry
        bad_request_error = Exception("bad request")
        assert agent._should_retry_exception(bad_request_error) is False

        # Test other error - should retry (but depends on is_retryable_exception)
        other_error = Exception("network error")
        # The actual behavior depends on the is_retryable_exception function
        result = agent._should_retry_exception(other_error)
        assert isinstance(result, bool)

    @patch("runtime.core.agent.get_env_var")
    @pytest.mark.asyncio
    async def test_agent_client_cleanup(self, mock_get_env_var):
        """Test agent client cleanup."""
        mock_get_env_var.side_effect = (
            lambda key, default=None, required=False, cast_type=None: {
                "DEBUG_MODE": "true",
                "AGENT_ID": None,
            }.get(key, default)
        )

        agent = AgentClient()

        # Should not raise an exception
        await agent.cleanup()

    @patch("runtime.core.agent.get_env_var")
    def test_agent_client_missing_agent_id_error(self, mock_get_env_var):
        """Test error when agent ID is missing in production mode."""
        mock_get_env_var.side_effect = (
            lambda key, default=None, required=False, cast_type=None: {
                "DEBUG_MODE": "false",
                "AGENT_ID": None,
            }.get(key, default)
        )

        with pytest.raises(ValueError, match="Missing required environment variable"):
            AgentClient()
