"""Extended unit tests for CLI tools - ctool.py."""

import json
from unittest.mock import patch

from cli.ctool import (
    get_conversation,
    list_conversations,
    main,
    print_conversations,
    print_json,
)


class TestCtoolExtended:
    """Extended test cases for ctool.py."""

    @patch("cli.ctool.get_all_conversations")
    def test_list_conversations_with_conversations(self, mock_get_conversations):
        """Test listing conversations when conversations exist."""
        mock_conversations = [
            {"id": 1, "title": "conv1", "display_name": "User1"},
            {"id": 2, "title": "conv2", "display_name": "User2"},
        ]
        mock_get_conversations.return_value = mock_conversations

        with patch("cli.ctool.print_conversations") as mock_print:
            list_conversations()
            mock_print.assert_called_once_with(mock_conversations)

    @patch("cli.ctool.get_all_conversations")
    def test_list_conversations_empty(self, mock_get_conversations):
        """Test listing conversations when no conversations exist."""
        mock_get_conversations.return_value = []

        with patch("cli.ctool.print_conversations") as mock_print:
            list_conversations()
            mock_print.assert_called_once_with([])

    @patch("cli.ctool.get_conversation_by_id")
    def test_get_conversation_success(self, mock_get_conversation):
        """Test getting conversation successfully."""
        mock_conversation = {"id": 1, "title": "conv1", "display_name": "User1"}
        mock_get_conversation.return_value = mock_conversation

        with patch("cli.ctool.print_json") as mock_print:
            get_conversation(1)
            mock_print.assert_called_once_with(mock_conversation)

    @patch("cli.ctool.get_conversation_by_id")
    def test_get_conversation_not_found(self, mock_get_conversation):
        """Test getting non-existent conversation."""
        mock_get_conversation.return_value = None

        with patch("builtins.print") as mock_print:
            get_conversation(999)
            mock_print.assert_called_once_with("Conversation 999 not found")

    def test_print_json_with_data(self):
        """Test printing JSON data."""
        test_data = {"id": 1, "title": "conv1", "display_name": "User1"}

        with patch("builtins.print") as mock_print:
            print_json(test_data)
            mock_print.assert_called_once_with(json.dumps(test_data, indent=2))

    def test_print_json_empty(self):
        """Test printing empty JSON data."""
        test_data = {}

        with patch("builtins.print") as mock_print:
            print_json(test_data)
            mock_print.assert_called_once_with(json.dumps(test_data, indent=2))

    def test_print_conversations_with_conversations(self):
        """Test printing conversations."""
        test_conversations = [
            {"id": 1, "title": "conv1", "display_name": "User1"},
            {"id": 2, "title": "conv2", "display_name": "User2"},
        ]

        with patch("builtins.print") as mock_print:
            print_conversations(test_conversations)

            # Should print header and each conversation
            assert mock_print.call_count == 3
            mock_print.assert_any_call("Conversations:")
            mock_print.assert_any_call("ID: 1, Title: conv1, User: User1")
            mock_print.assert_any_call("ID: 2, Title: conv2, User: User2")

    def test_print_conversations_empty(self):
        """Test printing empty conversations list."""
        with patch("builtins.print") as mock_print:
            print_conversations([])
            mock_print.assert_called_once_with("No conversations found")

    def test_print_conversations_none(self):
        """Test printing None conversations."""
        with patch("builtins.print") as mock_print:
            print_conversations(None)
            mock_print.assert_called_once_with("No conversations found")

    def test_main_list_command(self):
        """Test main function with list command."""
        with patch("cli.ctool.list_conversations") as mock_list:
            with patch("cli.ctool.sys.argv", ["ctool.py", "list"]):
                main()
                mock_list.assert_called_once()

    def test_main_get_command(self):
        """Test main function with get command."""
        with patch("cli.ctool.get_conversation") as mock_get:
            with patch("cli.ctool.sys.argv", ["ctool.py", "get", "1"]):
                main()
                mock_get.assert_called_once_with(1)

    def test_main_get_command_invalid_id(self):
        """Test main function with get command and invalid ID."""
        with patch("cli.ctool.sys.argv", ["ctool.py", "get", "invalid"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        with patch("cli.ctool.sys.argv", ["ctool.py", "invalid"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_main_no_args(self):
        """Test main function with no arguments."""
        with patch("cli.ctool.sys.argv", ["ctool.py"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_print_conversations_with_missing_fields(self):
        """Test printing conversations with missing fields."""
        test_conversations = [
            {"id": 1, "title": "conv1"},  # Missing display_name
            {"id": 2, "display_name": "User2"},  # Missing title
        ]

        with patch("builtins.print") as mock_print:
            print_conversations(test_conversations)

            # Should handle missing fields gracefully
            assert mock_print.call_count == 3
            mock_print.assert_any_call("Conversations:")

    def test_print_conversations_with_special_characters(self):
        """Test printing conversations with special characters."""
        test_conversations = [
            {"id": 1, "title": "conv@#$%", "display_name": "User@#$%"}
        ]

        with patch("builtins.print") as mock_print:
            print_conversations(test_conversations)

            # Should print special characters correctly
            assert mock_print.call_count == 2
            mock_print.assert_any_call("Conversations:")
            mock_print.assert_any_call("ID: 1, Title: conv@#$%, User: User@#$%")

    def test_print_json_with_special_characters(self):
        """Test printing JSON with special characters."""
        test_data = {"title": "conv@#$%", "display_name": "User!@#"}

        with patch("builtins.print") as mock_print:
            print_json(test_data)
            mock_print.assert_called_once_with(json.dumps(test_data, indent=2))

    def test_get_conversation_with_exception(self):
        """Test getting conversation with exception."""
        with patch(
            "cli.ctool.get_conversation_by_id", side_effect=Exception("Database error")
        ):
            with patch("builtins.print") as mock_print:
                get_conversation(1)
                mock_print.assert_called()

    def test_list_conversations_with_exception(self):
        """Test listing conversations with exception."""
        with patch(
            "cli.ctool.get_all_conversations", side_effect=Exception("Database error")
        ):
            with patch("builtins.print") as mock_print:
                list_conversations()
                mock_print.assert_called()

    def test_print_conversations_with_none_values(self):
        """Test printing conversations with None values."""
        test_conversations = [
            {"id": None, "title": "conv1", "display_name": "User1"},
            {"id": 2, "title": None, "display_name": "User2"},
            {"id": 3, "title": "conv3", "display_name": None},
        ]

        with patch("builtins.print") as mock_print:
            print_conversations(test_conversations)

            # Should handle None values gracefully
            assert mock_print.call_count == 4
            mock_print.assert_any_call("Conversations:")

    def test_get_conversation_with_string_id(self):
        """Test getting conversation with string ID."""
        with patch("cli.ctool.sys.argv", ["ctool.py", "get", "abc"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_print_conversations_with_empty_strings(self):
        """Test printing conversations with empty strings."""
        test_conversations = [
            {"id": 1, "title": "", "display_name": "User1"},
            {"id": 2, "title": "conv2", "display_name": ""},
        ]

        with patch("builtins.print") as mock_print:
            print_conversations(test_conversations)

            # Should handle empty strings gracefully
            assert mock_print.call_count == 3
            mock_print.assert_any_call("Conversations:")
            mock_print.assert_any_call("ID: 1, Title: , User: User1")
            mock_print.assert_any_call("ID: 2, Title: conv2, User: ")

    def test_main_get_command_no_id(self):
        """Test main function with get command but no ID."""
        with patch("cli.ctool.sys.argv", ["ctool.py", "get"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_print_conversations_with_long_titles(self):
        """Test printing conversations with long titles."""
        test_conversations = [{"id": 1, "title": "a" * 100, "display_name": "User1"}]

        with patch("builtins.print") as mock_print:
            print_conversations(test_conversations)

            # Should handle long titles
            assert mock_print.call_count == 2
            mock_print.assert_any_call("Conversations:")
            mock_print.assert_any_call(f"ID: 1, Title: {'a' * 100}, User: User1")

    def test_print_json_with_nested_data(self):
        """Test printing JSON with nested data."""
        test_data = {
            "id": 1,
            "title": "conv1",
            "metadata": {"created": "2024-01-01", "updated": "2024-01-02"},
        }

        with patch("builtins.print") as mock_print:
            print_json(test_data)
            mock_print.assert_called_once_with(json.dumps(test_data, indent=2))

    def test_print_conversations_with_unicode(self):
        """Test printing conversations with unicode characters."""
        test_conversations = [{"id": 1, "title": "café", "display_name": "José"}]

        with patch("builtins.print") as mock_print:
            print_conversations(test_conversations)

            # Should handle unicode characters
            assert mock_print.call_count == 2
            mock_print.assert_any_call("Conversations:")
            mock_print.assert_any_call("ID: 1, Title: café, User: José")
