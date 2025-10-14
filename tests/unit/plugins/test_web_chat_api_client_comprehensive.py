"""Comprehensive tests for plugins/web_chat/api_client.py."""

from unittest.mock import AsyncMock, patch

import pytest

from plugins.web_chat.api_client import WebChatAPIClient
from plugins.web_chat.settings import WebChatSettings


class TestWebChatAPIClient:
    """Test cases for WebChatAPIClient class."""

    def test_initialization(self):
        """Test WebChatAPIClient initialization."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        assert client.settings == settings
        assert client.session is None
        assert client.logger is not None

    @pytest.mark.asyncio
    async def test_context_manager_entry(self):
        """Test async context manager entry."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session

            async with client as context_client:
                assert context_client == client
                assert client.session == mock_session
                mock_session_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_exit(self):
        """Test async context manager exit."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        mock_session = AsyncMock()
        client.session = mock_session

        await client.__aexit__(None, None, None)
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_exit_no_session(self):
        """Test async context manager exit with no session."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        # No session set
        await client.__aexit__(None, None, None)
        # Should not raise any errors

    def test_get_headers(self):
        """Test _get_headers method."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        with patch("plugins.web_chat.api_client.log_safe_value") as mock_log_safe:
            mock_log_safe.return_value = "test_key***"

            headers = client._get_headers()

            expected_headers = {
                "Authorization": "Bearer test_key",
                "Content-Type": "application/json",
                "User-Agent": "Broca2-WebChat-Plugin/1.0",
            }
            assert headers == expected_headers
            mock_log_safe.assert_called_once_with("test_key", 10)

    @pytest.mark.asyncio
    async def test_get_messages_success(self):
        """Test successful get_messages call."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        mock_messages = [
            {"id": 1, "message": "Hello", "session_id": "session1"},
            {"id": 2, "message": "World", "session_id": "session2"},
        ]

        mock_response_data = {"success": True, "data": {"messages": mock_messages}}

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await client.get_messages(limit=50, offset=0)

            assert result == mock_messages
            mock_session.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_messages_with_since(self):
        """Test get_messages with since parameter."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        mock_messages = [{"id": 1, "message": "Hello"}]
        mock_response_data = {"success": True, "data": {"messages": mock_messages}}

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await client.get_messages(
                limit=50, offset=0, since="2023-01-01T00:00:00Z"
            )

            assert result == mock_messages

            # Check that since parameter was included
            call_args = mock_session.get.call_args
            params = call_args[1]["params"]
            assert params["since"] == "2023-01-01T00:00:00Z"

    @pytest.mark.asyncio
    async def test_get_messages_limit_capped(self):
        """Test get_messages with limit capped at 100."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        mock_messages = []
        mock_response_data = {"success": True, "data": {"messages": mock_messages}}

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch("aiohttp.ClientSession", return_value=mock_session):
            await client.get_messages(limit=150, offset=0)

            # Check that limit was capped at 100
            call_args = mock_session.get.call_args
            params = call_args[1]["params"]
            assert params["limit"] == 100

    @pytest.mark.asyncio
    async def test_get_messages_api_error(self):
        """Test get_messages with API error response."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        mock_response_data = {"success": False, "message": "API Error"}

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await client.get_messages()

            assert result == []

    @pytest.mark.asyncio
    async def test_get_messages_http_error(self):
        """Test get_messages with HTTP error status."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        mock_response = AsyncMock()
        mock_response.status = 500

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await client.get_messages()

            assert result == []

    @pytest.mark.asyncio
    async def test_get_messages_exception(self):
        """Test get_messages with exception."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        mock_session = AsyncMock()
        mock_session.get.side_effect = Exception("Network error")

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await client.get_messages()

            assert result == []

    @pytest.mark.asyncio
    async def test_get_messages_existing_session(self):
        """Test get_messages with existing session."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        mock_messages = [{"id": 1, "message": "Hello"}]
        mock_response_data = {"success": True, "data": {"messages": mock_messages}}

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        client.session = mock_session

        result = await client.get_messages()

        assert result == mock_messages
        # Should not create new session
        assert client.session == mock_session

    @pytest.mark.asyncio
    async def test_post_response_success(self):
        """Test successful post_response call."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        mock_response_data = {"success": True, "message": "Response posted"}

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await client.post_response("session123", "Hello response")

            assert result is True
            mock_session.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_response_api_error(self):
        """Test post_response with API error response."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        mock_response_data = {"success": False, "message": "Post failed"}

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await client.post_response("session123", "Hello response")

            assert result is False

    @pytest.mark.asyncio
    async def test_post_response_http_error(self):
        """Test post_response with HTTP error status."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        mock_response = AsyncMock()
        mock_response.status = 500

        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await client.post_response("session123", "Hello response")

            assert result is False

    @pytest.mark.asyncio
    async def test_post_response_exception(self):
        """Test post_response with exception."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        mock_session = AsyncMock()
        mock_session.post.side_effect = Exception("Network error")

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await client.post_response("session123", "Hello response")

            assert result is False

    @pytest.mark.asyncio
    async def test_post_response_existing_session(self):
        """Test post_response with existing session."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        mock_response_data = {"success": True, "message": "Response posted"}

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        client.session = mock_session

        result = await client.post_response("session123", "Hello response")

        assert result is True
        # Should not create new session
        assert client.session == mock_session

    @pytest.mark.asyncio
    async def test_test_connection_success(self):
        """Test successful test_connection call."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        with patch.object(
            client, "get_messages", new_callable=AsyncMock
        ) as mock_get_messages:
            mock_get_messages.return_value = [{"id": 1, "message": "test"}]

            result = await client.test_connection()

            assert result is True
            mock_get_messages.assert_called_once_with(limit=1)

    @pytest.mark.asyncio
    async def test_test_connection_failure(self):
        """Test test_connection with failure."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        with patch.object(
            client, "get_messages", new_callable=AsyncMock
        ) as mock_get_messages:
            mock_get_messages.side_effect = Exception("Connection failed")

            result = await client.test_connection()

            assert result is False
            mock_get_messages.assert_called_once_with(limit=1)

    @pytest.mark.asyncio
    async def test_get_messages_params_structure(self):
        """Test that get_messages constructs correct parameters."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        mock_response_data = {"success": True, "data": {"messages": []}}

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch("aiohttp.ClientSession", return_value=mock_session):
            await client.get_messages(limit=25, offset=10, since="2023-01-01T00:00:00Z")

            call_args = mock_session.get.call_args
            params = call_args[1]["params"]

            expected_params = {
                "action": "inbox",
                "limit": 25,
                "offset": 10,
                "since": "2023-01-01T00:00:00Z",
            }
            assert params == expected_params

    @pytest.mark.asyncio
    async def test_post_response_data_structure(self):
        """Test that post_response constructs correct data structure."""
        settings = WebChatSettings(
            api_url="https://api.example.com",
            api_key="test_key",
            poll_interval=5,
            max_messages=100,
        )
        client = WebChatAPIClient(settings)

        mock_response_data = {"success": True, "message": "Response posted"}

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response

        with patch("aiohttp.ClientSession", return_value=mock_session):
            await client.post_response("session123", "Hello response")

            call_args = mock_session.post.call_args
            json_data = call_args[1]["json"]
            params = call_args[1]["params"]

            expected_data = {"session_id": "session123", "response": "Hello response"}
            expected_params = {"action": "outbox"}

            assert json_data == expected_data
            assert params == expected_params
