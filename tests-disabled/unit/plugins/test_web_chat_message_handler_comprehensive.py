"""
Comprehensive tests for Web Chat Message Handler.

This module tests the WebChatMessageHandler class which handles
processing of incoming and outgoing web chat messages.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from plugins.web_chat.message_handler import WebChatMessageHandler


class TestWebChatMessageHandler:
    """Test cases for WebChatMessageHandler class."""

    def test_initialization_default(self):
        """Test WebChatMessageHandler initialization with default platform."""
        handler = WebChatMessageHandler()
        assert handler.platform_name == "web_chat"
        assert handler.logger is not None

    def test_initialization_custom_platform(self):
        """Test WebChatMessageHandler initialization with custom platform."""
        handler = WebChatMessageHandler(platform_name="custom_platform")
        assert handler.platform_name == "custom_platform"
        assert handler.logger is not None

    @pytest.mark.asyncio
    async def test_process_incoming_message_success(self):
        """Test successful processing of incoming message."""
        handler = WebChatMessageHandler()

        message_data = {
            "session_id": "test_session_123",
            "message": "Hello, world!",
            "timestamp": "2024-01-01T12:00:00Z",
            "uid": "test_uid_456",
        }

        mock_letta_user = Mock()
        mock_letta_user.id = 1

        mock_platform_profile = Mock()
        mock_platform_profile.id = 2

        with patch(
            "plugins.web_chat.message_handler.get_or_create_letta_user",
            new_callable=AsyncMock,
        ) as mock_get_user, patch(
            "plugins.web_chat.message_handler.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch(
            "plugins.web_chat.message_handler.insert_message", new_callable=AsyncMock
        ) as mock_insert, patch(
            "plugins.web_chat.message_handler.add_to_queue", new_callable=AsyncMock
        ) as mock_add_queue:
            mock_get_user.return_value = mock_letta_user
            mock_get_profile.return_value = (mock_platform_profile, mock_letta_user)
            mock_insert.return_value = 123

            result = await handler.process_incoming_message(message_data)

            assert result == 123
            mock_get_user.assert_called_once()
            mock_get_profile.assert_called_once()
            mock_insert.assert_called_once()
            mock_add_queue.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_incoming_message_missing_session_id(self):
        """Test processing message with missing session_id."""
        handler = WebChatMessageHandler()

        message_data = {
            "message": "Hello, world!",
            "timestamp": "2024-01-01T12:00:00Z",
            "uid": "test_uid_456",
        }

        result = await handler.process_incoming_message(message_data)
        assert result is None

    @pytest.mark.asyncio
    async def test_process_incoming_message_missing_message_text(self):
        """Test processing message with missing message text."""
        handler = WebChatMessageHandler()

        message_data = {
            "session_id": "test_session_123",
            "timestamp": "2024-01-01T12:00:00Z",
            "uid": "test_uid_456",
        }

        result = await handler.process_incoming_message(message_data)
        assert result is None

    @pytest.mark.asyncio
    async def test_process_incoming_message_empty_message_text(self):
        """Test processing message with empty message text."""
        handler = WebChatMessageHandler()

        message_data = {
            "session_id": "test_session_123",
            "message": "",
            "timestamp": "2024-01-01T12:00:00Z",
            "uid": "test_uid_456",
        }

        result = await handler.process_incoming_message(message_data)
        assert result is None

    @pytest.mark.asyncio
    async def test_process_incoming_message_no_timestamp(self):
        """Test processing message without timestamp."""
        handler = WebChatMessageHandler()

        message_data = {
            "session_id": "test_session_123",
            "message": "Hello, world!",
            "uid": "test_uid_456",
        }

        mock_letta_user = Mock()
        mock_letta_user.id = 1

        mock_platform_profile = Mock()
        mock_platform_profile.id = 2

        with patch(
            "plugins.web_chat.message_handler.get_or_create_letta_user",
            new_callable=AsyncMock,
        ) as mock_get_user, patch(
            "plugins.web_chat.message_handler.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch(
            "plugins.web_chat.message_handler.insert_message", new_callable=AsyncMock
        ) as mock_insert, patch(
            "plugins.web_chat.message_handler.add_to_queue", new_callable=AsyncMock
        ):
            mock_get_user.return_value = mock_letta_user
            mock_get_profile.return_value = (mock_platform_profile, mock_letta_user)
            mock_insert.return_value = 123

            result = await handler.process_incoming_message(message_data)

            assert result == 123

    @pytest.mark.asyncio
    async def test_process_incoming_message_no_uid(self):
        """Test processing message without UID."""
        handler = WebChatMessageHandler()

        message_data = {
            "session_id": "test_session_123",
            "message": "Hello, world!",
            "timestamp": "2024-01-01T12:00:00Z",
        }

        mock_letta_user = Mock()
        mock_letta_user.id = 1

        mock_platform_profile = Mock()
        mock_platform_profile.id = 2

        with patch(
            "plugins.web_chat.message_handler.get_or_create_letta_user",
            new_callable=AsyncMock,
        ) as mock_get_user, patch(
            "plugins.web_chat.message_handler.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch(
            "plugins.web_chat.message_handler.insert_message", new_callable=AsyncMock
        ) as mock_insert, patch(
            "plugins.web_chat.message_handler.add_to_queue", new_callable=AsyncMock
        ):
            mock_get_user.return_value = mock_letta_user
            mock_get_profile.return_value = (mock_platform_profile, mock_letta_user)
            mock_insert.return_value = 123

            result = await handler.process_incoming_message(message_data)

            assert result == 123

    @pytest.mark.asyncio
    async def test_process_incoming_message_custom_platform(self):
        """Test processing message with custom platform."""
        handler = WebChatMessageHandler(platform_name="custom_platform")

        message_data = {
            "session_id": "test_session_123",
            "message": "Hello, world!",
            "timestamp": "2024-01-01T12:00:00Z",
            "uid": "test_uid_456",
        }

        mock_letta_user = Mock()
        mock_letta_user.id = 1

        mock_platform_profile = Mock()
        mock_platform_profile.id = 2

        with patch(
            "plugins.web_chat.message_handler.get_or_create_letta_user",
            new_callable=AsyncMock,
        ) as mock_get_user, patch(
            "plugins.web_chat.message_handler.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch(
            "plugins.web_chat.message_handler.insert_message", new_callable=AsyncMock
        ) as mock_insert, patch(
            "plugins.web_chat.message_handler.add_to_queue", new_callable=AsyncMock
        ):
            mock_get_user.return_value = mock_letta_user
            mock_get_profile.return_value = (mock_platform_profile, mock_letta_user)
            mock_insert.return_value = 123

            result = await handler.process_incoming_message(message_data)

            assert result == 123

    @pytest.mark.asyncio
    async def test_process_incoming_message_exception(self):
        """Test processing message with exception."""
        handler = WebChatMessageHandler()

        message_data = {
            "session_id": "test_session_123",
            "message": "Hello, world!",
            "timestamp": "2024-01-01T12:00:00Z",
            "uid": "test_uid_456",
        }

        with patch(
            "plugins.web_chat.message_handler.get_or_create_letta_user",
            new_callable=AsyncMock,
        ) as mock_get_user:
            mock_get_user.side_effect = Exception("Database error")

            result = await handler.process_incoming_message(message_data)
            assert result is None

    @pytest.mark.asyncio
    async def test_process_outgoing_message_success(self):
        """Test successful processing of outgoing message."""
        handler = WebChatMessageHandler()

        session_id = "test_session_123"
        response_text = "Hello back!"

        original_message = Mock()
        original_message.letta_user_id = 1
        original_message.platform_profile_id = 2
        original_message.id = 123

        with patch(
            "plugins.web_chat.message_handler.insert_message", new_callable=AsyncMock
        ) as mock_insert:
            result = await handler.process_outgoing_message(
                session_id, response_text, original_message
            )

            assert result is True
            mock_insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_outgoing_message_no_original_message(self):
        """Test processing outgoing message without original message."""
        handler = WebChatMessageHandler()

        session_id = "test_session_123"
        response_text = "Hello back!"

        result = await handler.process_outgoing_message(session_id, response_text, None)
        assert result is False

    @pytest.mark.asyncio
    async def test_process_outgoing_message_exception(self):
        """Test processing outgoing message with exception."""
        handler = WebChatMessageHandler()

        session_id = "test_session_123"
        response_text = "Hello back!"

        original_message = Mock()
        original_message.letta_user_id = 1
        original_message.platform_profile_id = 2
        original_message.id = 123

        with patch(
            "plugins.web_chat.message_handler.insert_message", new_callable=AsyncMock
        ) as mock_insert:
            mock_insert.side_effect = Exception("Database error")

            result = await handler.process_outgoing_message(
                session_id, response_text, original_message
            )
            assert result is False

    def test_sanitize_message_normal(self):
        """Test sanitizing normal message."""
        handler = WebChatMessageHandler()

        message = "Hello, world! This is a normal message."
        result = handler.sanitize_message(message)
        assert result == message

    def test_sanitize_message_empty(self):
        """Test sanitizing empty message."""
        handler = WebChatMessageHandler()

        result = handler.sanitize_message("")
        assert result == ""

    def test_sanitize_message_none(self):
        """Test sanitizing None message."""
        handler = WebChatMessageHandler()

        result = handler.sanitize_message(None)
        assert result == ""

    def test_sanitize_message_with_null_bytes(self):
        """Test sanitizing message with null bytes."""
        handler = WebChatMessageHandler()

        message = "Hello\x00world\x00!"
        result = handler.sanitize_message(message)
        assert result == "Helloworld!"

    def test_sanitize_message_with_whitespace(self):
        """Test sanitizing message with excessive whitespace."""
        handler = WebChatMessageHandler()

        message = "   Hello, world!   "
        result = handler.sanitize_message(message)
        assert result == "Hello, world!"

    def test_sanitize_message_too_long(self):
        """Test sanitizing message that's too long."""
        handler = WebChatMessageHandler()

        message = "A" * 5000  # Longer than 4000 character limit
        result = handler.sanitize_message(message)
        assert len(result) == 4003  # 4000 + "..."
        assert result.endswith("...")

    def test_sanitize_message_exactly_limit(self):
        """Test sanitizing message exactly at limit."""
        handler = WebChatMessageHandler()

        message = "A" * 4000  # Exactly at limit
        result = handler.sanitize_message(message)
        assert result == message
        assert len(result) == 4000

    def test_sanitize_message_just_over_limit(self):
        """Test sanitizing message just over limit."""
        handler = WebChatMessageHandler()

        message = "A" * 4001  # Just over limit
        result = handler.sanitize_message(message)
        assert len(result) == 4003  # 4000 + "..."
        assert result.endswith("...")

    def test_sanitize_message_with_special_characters(self):
        """Test sanitizing message with special characters."""
        handler = WebChatMessageHandler()

        message = "Hello! @#$%^&*()_+-=[]{}|;':\",./<>?"
        result = handler.sanitize_message(message)
        assert result == message

    def test_sanitize_message_with_newlines(self):
        """Test sanitizing message with newlines."""
        handler = WebChatMessageHandler()

        message = "Hello,\nworld!\n\nHow are you?"
        result = handler.sanitize_message(message)
        assert result == message

    def test_sanitize_message_with_tabs(self):
        """Test sanitizing message with tabs."""
        handler = WebChatMessageHandler()

        message = "Hello,\tworld!\t\tHow are you?"
        result = handler.sanitize_message(message)
        assert result == message

    def test_sanitize_message_mixed_issues(self):
        """Test sanitizing message with multiple issues."""
        handler = WebChatMessageHandler()

        message = "   Hello\x00world!\n\n   "
        result = handler.sanitize_message(message)
        assert result == "Helloworld!"

    def test_sanitize_message_unicode(self):
        """Test sanitizing message with unicode characters."""
        handler = WebChatMessageHandler()

        message = "Hello, 世界! 🌍"
        result = handler.sanitize_message(message)
        assert result == message

    def test_sanitize_message_very_long_unicode(self):
        """Test sanitizing very long unicode message."""
        handler = WebChatMessageHandler()

        message = "🌍" * 3000  # 3000 unicode characters
        result = handler.sanitize_message(message)
        assert len(result) == 3000
        assert result == message

    def test_sanitize_message_very_long_unicode_over_limit(self):
        """Test sanitizing very long unicode message over limit."""
        handler = WebChatMessageHandler()

        message = "🌍" * 3000 + "A" * 2000  # Over limit
        result = handler.sanitize_message(message)
        assert len(result) == 4003  # 4000 + "..."
        assert result.endswith("...")

    @pytest.mark.asyncio
    async def test_process_incoming_message_with_sanitization(self):
        """Test that incoming messages are sanitized."""
        handler = WebChatMessageHandler()

        message_data = {
            "session_id": "test_session_123",
            "message": "   Hello\x00world!   ",
            "timestamp": "2024-01-01T12:00:00Z",
            "uid": "test_uid_456",
        }

        mock_letta_user = Mock()
        mock_letta_user.id = 1

        mock_platform_profile = Mock()
        mock_platform_profile.id = 2

        with patch(
            "plugins.web_chat.message_handler.get_or_create_letta_user",
            new_callable=AsyncMock,
        ) as mock_get_user, patch(
            "plugins.web_chat.message_handler.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch(
            "plugins.web_chat.message_handler.insert_message", new_callable=AsyncMock
        ) as mock_insert, patch(
            "plugins.web_chat.message_handler.add_to_queue", new_callable=AsyncMock
        ):
            mock_get_user.return_value = mock_letta_user
            mock_get_profile.return_value = (mock_platform_profile, mock_letta_user)
            mock_insert.return_value = 123

            result = await handler.process_incoming_message(message_data)

            assert result == 123
            # Verify that insert_message was called with sanitized content
            call_args = mock_insert.call_args
            assert call_args[1]["message"] == "Helloworld!"

    @pytest.mark.asyncio
    async def test_process_incoming_message_timestamp_parsing(self):
        """Test timestamp parsing in incoming message."""
        handler = WebChatMessageHandler()

        message_data = {
            "session_id": "test_session_123",
            "message": "Hello, world!",
            "timestamp": "2024-01-01T12:00:00Z",
            "uid": "test_uid_456",
        }

        mock_letta_user = Mock()
        mock_letta_user.id = 1

        mock_platform_profile = Mock()
        mock_platform_profile.id = 2

        with patch(
            "plugins.web_chat.message_handler.get_or_create_letta_user",
            new_callable=AsyncMock,
        ) as mock_get_user, patch(
            "plugins.web_chat.message_handler.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch(
            "plugins.web_chat.message_handler.insert_message", new_callable=AsyncMock
        ) as mock_insert, patch(
            "plugins.web_chat.message_handler.add_to_queue", new_callable=AsyncMock
        ):
            mock_get_user.return_value = mock_letta_user
            mock_get_profile.return_value = (mock_platform_profile, mock_letta_user)
            mock_insert.return_value = 123

            result = await handler.process_incoming_message(message_data)

            assert result == 123
            # Verify that insert_message was called with correct timestamp
            call_args = mock_insert.call_args
            assert call_args[1]["timestamp"] == "2024-01-01T12:00:00Z"

    @pytest.mark.asyncio
    async def test_process_incoming_message_metadata_creation(self):
        """Test metadata creation in incoming message."""
        handler = WebChatMessageHandler()

        message_data = {
            "session_id": "test_session_123",
            "message": "Hello, world!",
            "timestamp": "2024-01-01T12:00:00Z",
            "uid": "test_uid_456",
        }

        mock_letta_user = Mock()
        mock_letta_user.id = 1

        mock_platform_profile = Mock()
        mock_platform_profile.id = 2

        with patch(
            "plugins.web_chat.message_handler.get_or_create_letta_user",
            new_callable=AsyncMock,
        ) as mock_get_user, patch(
            "plugins.web_chat.message_handler.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch(
            "plugins.web_chat.message_handler.insert_message", new_callable=AsyncMock
        ) as mock_insert, patch(
            "plugins.web_chat.message_handler.add_to_queue", new_callable=AsyncMock
        ):
            mock_get_user.return_value = mock_letta_user
            mock_get_profile.return_value = (mock_platform_profile, mock_letta_user)
            mock_insert.return_value = 123

            result = await handler.process_incoming_message(message_data)

            assert result == 123
            # Verify that get_or_create_platform_profile was called with correct metadata
            call_args = mock_get_profile.call_args
            metadata = call_args[1]["metadata"]
            assert metadata["session_id"] == "test_session_123"
            assert metadata["uid"] == "test_uid_456"
            assert metadata["source"] == "web_chat"

    @pytest.mark.asyncio
    async def test_process_outgoing_message_metadata_creation(self):
        """Test metadata creation in outgoing message."""
        handler = WebChatMessageHandler()

        session_id = "test_session_123"
        response_text = "Hello back!"

        original_message = Mock()
        original_message.letta_user_id = 1
        original_message.platform_profile_id = 2
        original_message.id = 123

        with patch(
            "plugins.web_chat.message_handler.insert_message", new_callable=AsyncMock
        ) as mock_insert:
            result = await handler.process_outgoing_message(
                session_id, response_text, original_message
            )

            assert result is True
            # Verify that insert_message was called with correct metadata
            call_args = mock_insert.call_args
            message_obj = call_args[0][0]
            assert message_obj.metadata["session_id"] == session_id
            assert message_obj.metadata["platform"] == "web_chat"
            assert message_obj.metadata["source"] == "broca2_agent"
            assert message_obj.metadata["in_response_to"] == 123
