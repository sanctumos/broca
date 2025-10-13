"""
Tests for CLI conversation management tool (ctool.py).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cli.ctool import (
    get_conversation,
    list_conversations,
    main,
    print_conversations,
    print_json,
)


class TestCtoolFunctions:
    """Test ctool.py functions."""

    @pytest.mark.asyncio
    async def test_list_conversations_json_output(self):
        """Test listing conversations with JSON output."""
        mock_conversations = [
            {
                "letta_user_id": "1",
                "platform_profile_id": "telegram_123",
                "message": "Hello",
                "timestamp": "2024-01-01T00:00:00",
            },
            {
                "letta_user_id": "2",
                "platform_profile_id": "telegram_456",
                "message": "Hi there",
                "timestamp": "2024-01-01T01:00:00",
            },
        ]

        args = MagicMock()
        args.json = True

        with patch(
            "cli.ctool.get_message_history", new_callable=AsyncMock
        ) as mock_get, patch("cli.ctool.print_json") as mock_print_json:
            mock_get.return_value = mock_conversations
            await list_conversations(args)

            mock_print_json.assert_called_once_with(mock_conversations)

    @pytest.mark.asyncio
    async def test_list_conversations_table_output(self):
        """Test listing conversations with table output."""
        mock_conversations = [
            {
                "letta_user_id": "1",
                "platform_profile_id": "telegram_123",
                "message": "Hello",
                "timestamp": "2024-01-01T00:00:00",
            }
        ]

        args = MagicMock()
        args.json = False

        with patch(
            "cli.ctool.get_message_history", new_callable=AsyncMock
        ) as mock_get, patch("cli.ctool.print_conversations") as mock_print_table:
            mock_get.return_value = mock_conversations
            await list_conversations(args)

            mock_print_table.assert_called_once_with(mock_conversations)

    @pytest.mark.asyncio
    async def test_get_conversation_with_matches(self):
        """Test getting conversation for specific user with matches."""
        mock_conversations = [
            {
                "letta_user_id": "1",
                "platform_profile_id": "telegram_123",
                "message": "Hello",
                "timestamp": "2024-01-01T00:00:00",
            },
            {
                "letta_user_id": "2",
                "platform_profile_id": "telegram_456",
                "message": "Hi there",
                "timestamp": "2024-01-01T01:00:00",
            },
            {
                "letta_user_id": "1",
                "platform_profile_id": "telegram_123",
                "message": "How are you?",
                "timestamp": "2024-01-01T02:00:00",
            },
        ]

        args = MagicMock()
        args.user_id = "1"
        args.platform_id = "telegram_123"
        args.limit = 10
        args.json = False

        with patch(
            "cli.ctool.get_message_history", new_callable=AsyncMock
        ) as mock_get, patch("cli.ctool.print_conversations") as mock_print_table:
            mock_get.return_value = mock_conversations
            await get_conversation(args)

            expected_conversations = [
                {
                    "letta_user_id": "1",
                    "platform_profile_id": "telegram_123",
                    "message": "Hello",
                    "timestamp": "2024-01-01T00:00:00",
                },
                {
                    "letta_user_id": "1",
                    "platform_profile_id": "telegram_123",
                    "message": "How are you?",
                    "timestamp": "2024-01-01T02:00:00",
                },
            ]
            mock_print_table.assert_called_once_with(expected_conversations)

    @pytest.mark.asyncio
    async def test_get_conversation_with_limit(self):
        """Test getting conversation with limit applied."""
        mock_conversations = [
            {
                "letta_user_id": "1",
                "platform_profile_id": "telegram_123",
                "message": "Message 1",
                "timestamp": "2024-01-01T00:00:00",
            },
            {
                "letta_user_id": "1",
                "platform_profile_id": "telegram_123",
                "message": "Message 2",
                "timestamp": "2024-01-01T01:00:00",
            },
            {
                "letta_user_id": "1",
                "platform_profile_id": "telegram_123",
                "message": "Message 3",
                "timestamp": "2024-01-01T02:00:00",
            },
        ]

        args = MagicMock()
        args.user_id = "1"
        args.platform_id = "telegram_123"
        args.limit = 2
        args.json = False

        with patch(
            "cli.ctool.get_message_history", new_callable=AsyncMock
        ) as mock_get, patch("cli.ctool.print_conversations") as mock_print_table:
            mock_get.return_value = mock_conversations
            await get_conversation(args)

            # Should only get first 2 messages
            expected_conversations = mock_conversations[:2]
            mock_print_table.assert_called_once_with(expected_conversations)

    @pytest.mark.asyncio
    async def test_get_conversation_no_matches(self):
        """Test getting conversation for user with no matches."""
        mock_conversations = [
            {
                "letta_user_id": "2",
                "platform_profile_id": "telegram_456",
                "message": "Hi there",
                "timestamp": "2024-01-01T01:00:00",
            }
        ]

        args = MagicMock()
        args.user_id = "1"
        args.platform_id = "telegram_123"
        args.limit = 10
        args.json = False

        with patch(
            "cli.ctool.get_message_history", new_callable=AsyncMock
        ) as mock_get, patch("cli.ctool.print_conversations") as mock_print_table:
            mock_get.return_value = mock_conversations
            await get_conversation(args)

            mock_print_table.assert_called_once_with([])

    @pytest.mark.asyncio
    async def test_get_conversation_json_output(self):
        """Test getting conversation with JSON output."""
        mock_conversations = [
            {
                "letta_user_id": "1",
                "platform_profile_id": "telegram_123",
                "message": "Hello",
                "timestamp": "2024-01-01T00:00:00",
            }
        ]

        args = MagicMock()
        args.user_id = "1"
        args.platform_id = "telegram_123"
        args.limit = 10
        args.json = True

        with patch(
            "cli.ctool.get_message_history", new_callable=AsyncMock
        ) as mock_get, patch("cli.ctool.print_json") as mock_print_json:
            mock_get.return_value = mock_conversations
            await get_conversation(args)

            mock_print_json.assert_called_once_with(mock_conversations)

    def test_print_json(self):
        """Test printing JSON output."""
        mock_conversations = [
            {
                "letta_user_id": "1",
                "platform_profile_id": "telegram_123",
                "message": "Hello",
                "timestamp": "2024-01-01T00:00:00",
            }
        ]

        with patch("builtins.print") as mock_print:
            print_json(mock_conversations)
            mock_print.assert_called_once()

    def test_print_conversations_with_data(self):
        """Test printing conversations with data."""
        mock_conversations = [
            {
                "letta_user_id": "1",
                "platform_profile_id": "telegram_123",
                "message": "Hello",
                "timestamp": "2024-01-01T00:00:00",
            }
        ]

        with patch("builtins.print") as mock_print:
            print_conversations(mock_conversations)
            # Should print header and conversation
            assert mock_print.call_count >= 2

    def test_print_conversations_empty(self):
        """Test printing empty conversations list."""
        with patch("builtins.print") as mock_print:
            print_conversations([])
            mock_print.assert_called_once_with("No conversations found")

    def test_main_list_command(self):
        """Test main function with list command."""
        args = MagicMock()
        args.command = "list"
        args.json = False

        with patch("cli.ctool.list_conversations", new_callable=AsyncMock), patch(
            "asyncio.run"
        ) as mock_run:
            main()
            mock_run.assert_called_once()

    def test_main_get_command(self):
        """Test main function with get command."""
        args = MagicMock()
        args.command = "get"
        args.user_id = "1"
        args.platform_id = "telegram_123"
        args.limit = 10
        args.json = False

        with patch("cli.ctool.get_conversation", new_callable=AsyncMock), patch(
            "asyncio.run"
        ) as mock_run:
            main()
            mock_run.assert_called_once()

    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        with patch("sys.argv", ["ctool.py", "invalid"]), patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)
