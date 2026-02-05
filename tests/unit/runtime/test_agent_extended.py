"""Extended unit tests for runtime agent client."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

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
                "DEBUG_MODE": False,
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
                "DEBUG_MODE": False,  # Return boolean False directly
                "AGENT_ID": "test-agent",
            }.get(key, default)
        )

        with patch("runtime.core.agent.get_letta_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            mock_response = MagicMock()
            mock_message = MagicMock()
            mock_message.message_type = "assistant_message"
            mock_message.content = "Test response"
            mock_response.messages = [mock_message]
            mock_client.agents.messages.create.return_value = mock_response

            agent = AgentClient()
            message = "Test message"

            result = await agent.process_message(message)
            assert result == "Test response"
            # SDK 1.x: create(agent_id, *, input=...)
            mock_client.agents.messages.create.assert_called_once_with(
                "test-agent",
                input="Test message",
            )

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
                "DEBUG_MODE": False,  # Return boolean False directly
                "AGENT_ID": None,
            }.get(key, default)
        )

        with pytest.raises(ValueError, match="Missing required environment variable"):
            AgentClient()

    @patch("runtime.core.agent.get_env_var")
    @pytest.mark.asyncio
    async def test_agent_client_process_message_async_debug_mode(
        self, mock_get_env_var
    ):
        """Test process_message_async in debug mode."""
        mock_get_env_var.side_effect = (
            lambda key, default=None, required=False, cast_type=None: {
                "DEBUG_MODE": "true",
                "AGENT_ID": None,
            }.get(key, default)
        )

        agent = AgentClient()
        message = "Test message"

        result = await agent.process_message_async(message)
        assert result == message

    @patch("runtime.core.agent.get_env_var")
    @pytest.mark.asyncio
    async def test_agent_client_process_message_async_streaming_success(
        self, mock_get_env_var
    ):
        """Test process_message_async with successful streaming."""
        mock_get_env_var.side_effect = (
            lambda key, default=None, required=False, cast_type=None: {
                "DEBUG_MODE": False,
                "AGENT_ID": "test-agent",
                "LONG_TASK_MAX_WAIT": "600",
            }.get(key, default)
        )

        with patch("runtime.core.agent.get_letta_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            # Create async generator for stream
            async def mock_stream_generator():
                mock_event = MagicMock()
                mock_event.conversation_id = "conv-123"
                mock_event.conversation = None
                mock_event.run = None
                mock_event.data = None
                mock_event.messages = None
                yield mock_event

            # Mock stream object
            mock_stream = mock_stream_generator()

            # Mock messages.create to return stream
            mock_client.agents.messages.create.return_value = mock_stream

            # Mock conversations.messages.list to return final message
            mock_messages_response = MagicMock()
            mock_assistant_msg = MagicMock()
            mock_assistant_msg.message_type = "assistant_message"
            mock_assistant_msg.content = "Final response"
            mock_messages_response.data = [mock_assistant_msg]
            mock_client.conversations.messages.list.return_value = (
                mock_messages_response
            )

            agent = AgentClient()
            result = await agent.process_message_async("Test message")

            assert result == "Final response"
            # SDK 1.x: create(agent_id, *, input=..., streaming=..., ...)
            mock_client.agents.messages.create.assert_called_once_with(
                "test-agent",
                input="Test message",
                streaming=True,
                background=True,
                include_pings=True,
            )
            # SDK 1.x: list(conversation_id, *, order=..., limit=...)
            mock_client.conversations.messages.list.assert_called_once_with(
                "conv-123", order="desc", limit=10
            )

    @patch("runtime.core.agent.get_env_var")
    @pytest.mark.asyncio
    async def test_agent_client_process_message_async_no_conversation_id(
        self, mock_get_env_var
    ):
        """Test process_message_async when conversation_id is not found in stream."""
        mock_get_env_var.side_effect = (
            lambda key, default=None, required=False, cast_type=None: {
                "DEBUG_MODE": False,
                "AGENT_ID": "test-agent",
                "LONG_TASK_MAX_WAIT": "600",
            }.get(key, default)
        )

        with patch("runtime.core.agent.get_letta_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            # Create async generator for stream with no conversation_id
            async def mock_stream_generator():
                mock_event = MagicMock()
                mock_event.conversation_id = None
                mock_event.conversation = None
                mock_event.run = None
                mock_event.data = None
                mock_event.messages = None
                yield mock_event

            mock_stream = mock_stream_generator()
            mock_client.agents.messages.create.return_value = mock_stream

            agent = AgentClient()
            result = await agent.process_message_async("Test message")

            assert result is None

    @patch("runtime.core.agent.get_env_var")
    @pytest.mark.asyncio
    async def test_agent_client_process_message_async_timeout(self, mock_get_env_var):
        """Test process_message_async with timeout."""
        mock_get_env_var.side_effect = (
            lambda key, default=None, required=False, cast_type=None: {
                "DEBUG_MODE": False,
                "AGENT_ID": "test-agent",
                "LONG_TASK_MAX_WAIT": "1",  # 1 second timeout
            }.get(key, default)
        )

        with patch("runtime.core.agent.get_letta_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            # Mock stream that never closes (simulating timeout)
            async def slow_stream():
                while True:
                    await asyncio.sleep(2)  # Sleep longer than timeout
                    yield MagicMock()

            mock_stream = slow_stream()
            mock_client.agents.messages.create.return_value = mock_stream

            # Mock fallback method
            with patch.object(
                AgentClient, "_fallback_to_async", new_callable=AsyncMock
            ) as mock_fallback:
                mock_fallback.return_value = "Fallback response"
                agent = AgentClient()
                result = await agent.process_message_async("Test message")

                assert result == "Fallback response"

    @patch("runtime.core.agent.get_env_var")
    @pytest.mark.asyncio
    async def test_agent_client_fallback_to_async(self, mock_get_env_var):
        """Test _fallback_to_async method."""
        mock_get_env_var.side_effect = (
            lambda key, default=None, required=False, cast_type=None: {
                "DEBUG_MODE": False,
                "AGENT_ID": "test-agent",
            }.get(key, default)
        )

        with patch("runtime.core.agent.get_letta_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            # Mock create_async to return run with conversation_id
            mock_run = MagicMock()
            mock_run.conversation_id = "conv-456"
            mock_client.agents.messages.create_async.return_value = mock_run

            # Mock conversations.messages.list to eventually return message
            mock_messages_response = MagicMock()
            mock_assistant_msg = MagicMock()
            mock_assistant_msg.message_type = "assistant_message"
            mock_assistant_msg.content = "Polled response"
            mock_messages_response.data = [mock_assistant_msg]
            mock_client.conversations.messages.list.return_value = (
                mock_messages_response
            )

            agent = AgentClient()
            result = await agent._fallback_to_async("Test message")

            assert result == "Polled response"
            # SDK 1.x: create_async(agent_id, *, input=...)
            mock_client.agents.messages.create_async.assert_called_once_with(
                "test-agent", input="Test message"
            )

    @patch("runtime.core.agent.get_env_var")
    @pytest.mark.asyncio
    async def test_agent_client_process_message_async_conversation_id_from_run(
        self, mock_get_env_var
    ):
        """Test process_message_async extracting conversation_id from event.run."""
        mock_get_env_var.side_effect = (
            lambda key, default=None, required=False, cast_type=None: {
                "DEBUG_MODE": False,
                "AGENT_ID": "test-agent",
                "LONG_TASK_MAX_WAIT": "600",
            }.get(key, default)
        )

        with patch("runtime.core.agent.get_letta_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            # Create async generator with conversation_id in event.run
            async def mock_stream_generator():
                mock_event = MagicMock()
                mock_event.conversation_id = None
                mock_run = MagicMock()
                mock_run.conversation_id = "conv-from-run"
                mock_event.run = mock_run
                mock_event.conversation = None
                mock_event.data = None
                mock_event.messages = None
                yield mock_event

            mock_stream = mock_stream_generator()
            mock_client.agents.messages.create.return_value = mock_stream

            # Mock conversations.messages.list
            mock_messages_response = MagicMock()
            mock_assistant_msg = MagicMock()
            mock_assistant_msg.message_type = "assistant"
            mock_assistant_msg.text = "Response from run"
            mock_messages_response.data = [mock_assistant_msg]
            mock_client.conversations.messages.list.return_value = (
                mock_messages_response
            )

            agent = AgentClient()
            result = await agent.process_message_async("Test message")

            assert result == "Response from run"
            # SDK 1.x: list(conversation_id, *, order=..., limit=...)
            mock_client.conversations.messages.list.assert_called_once_with(
                "conv-from-run", order="desc", limit=10
            )

    @patch("runtime.core.agent.get_env_var")
    @pytest.mark.asyncio
    async def test_agent_client_process_message_async_stream_error_with_conversation_id(
        self, mock_get_env_var
    ):
        """Test process_message_async when stream errors but conversation_id was captured."""
        mock_get_env_var.side_effect = (
            lambda key, default=None, required=False, cast_type=None: {
                "DEBUG_MODE": False,
                "AGENT_ID": "test-agent",
                "LONG_TASK_MAX_WAIT": "600",
            }.get(key, default)
        )

        with patch("runtime.core.agent.get_letta_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            # Create async generator that raises error after first event
            async def mock_stream_generator():
                mock_event = MagicMock()
                mock_event.conversation_id = "conv-error"
                mock_event.conversation = None
                mock_event.run = None
                mock_event.data = None
                mock_event.messages = None
                yield mock_event
                raise Exception("Stream error")

            mock_stream = mock_stream_generator()
            mock_client.agents.messages.create.return_value = mock_stream

            # Mock conversations.messages.list
            mock_messages_response = MagicMock()
            mock_assistant_msg = MagicMock()
            mock_assistant_msg.message_type = "assistant_message"
            mock_assistant_msg.content = "Recovered response"
            mock_messages_response.data = [mock_assistant_msg]
            mock_client.conversations.messages.list.return_value = (
                mock_messages_response
            )

            agent = AgentClient()
            result = await agent.process_message_async("Test message")

            assert result == "Recovered response"
