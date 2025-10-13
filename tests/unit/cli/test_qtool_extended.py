"""Extended unit tests for CLI tools - qtool.py."""

import json
from unittest.mock import patch

from cli.qtool import (
    delete_queue,
    flush_queue,
    list_queue,
    main,
    print_json,
    print_queue_items,
)


class TestQtoolExtended:
    """Extended test cases for qtool.py."""

    @patch("cli.qtool.get_queue_items")
    def test_list_queue_with_items(self, mock_get_queue):
        """Test listing queue with items."""
        mock_items = [
            {"id": 1, "message": "test1", "display_name": "User1"},
            {"id": 2, "message": "test2", "display_name": "User2"},
        ]
        mock_get_queue.return_value = mock_items

        with patch("cli.qtool.print_queue_items") as mock_print:
            list_queue()
            mock_print.assert_called_once_with(mock_items)

    @patch("cli.qtool.get_queue_items")
    def test_list_queue_empty(self, mock_get_queue):
        """Test listing empty queue."""
        mock_get_queue.return_value = []

        with patch("cli.qtool.print_queue_items") as mock_print:
            list_queue()
            mock_print.assert_called_once_with([])

    @patch("cli.qtool.flush_queue_items")
    def test_flush_queue_success(self, mock_flush):
        """Test flushing queue successfully."""
        mock_flush.return_value = 5

        with patch("builtins.print") as mock_print:
            flush_queue()
            mock_print.assert_called_once_with("Flushed 5 items from queue")

    @patch("cli.qtool.flush_queue_items")
    def test_flush_queue_empty(self, mock_flush):
        """Test flushing empty queue."""
        mock_flush.return_value = 0

        with patch("builtins.print") as mock_print:
            flush_queue()
            mock_print.assert_called_once_with("No items to flush")

    @patch("cli.qtool.delete_queue_item")
    def test_delete_queue_success(self, mock_delete):
        """Test deleting queue item successfully."""
        mock_delete.return_value = True

        with patch("builtins.print") as mock_print:
            delete_queue(123)
            mock_print.assert_called_once_with("Deleted queue item 123")

    @patch("cli.qtool.delete_queue_item")
    def test_delete_queue_not_found(self, mock_delete):
        """Test deleting non-existent queue item."""
        mock_delete.return_value = False

        with patch("builtins.print") as mock_print:
            delete_queue(999)
            mock_print.assert_called_once_with("Queue item 999 not found")

    def test_print_json_with_data(self):
        """Test printing JSON data."""
        test_data = {"key": "value", "number": 123}

        with patch("builtins.print") as mock_print:
            print_json(test_data)
            mock_print.assert_called_once_with(json.dumps(test_data, indent=2))

    def test_print_json_empty(self):
        """Test printing empty JSON data."""
        test_data = {}

        with patch("builtins.print") as mock_print:
            print_json(test_data)
            mock_print.assert_called_once_with(json.dumps(test_data, indent=2))

    def test_print_queue_items_with_items(self):
        """Test printing queue items."""
        test_items = [
            {"id": 1, "message": "test1", "display_name": "User1"},
            {"id": 2, "message": "test2", "display_name": "User2"},
        ]

        with patch("builtins.print") as mock_print:
            print_queue_items(test_items)

            # Should print header and each item
            assert mock_print.call_count == 4
            mock_print.assert_any_call("Queue Items:")
            mock_print.assert_any_call("ID: 1, Message: test1, User: User1")
            mock_print.assert_any_call("ID: 2, Message: test2, User: User2")

    def test_print_queue_items_empty(self):
        """Test printing empty queue items."""
        with patch("builtins.print") as mock_print:
            print_queue_items([])
            mock_print.assert_called_once_with("No items in queue")

    def test_print_queue_items_none(self):
        """Test printing None queue items."""
        with patch("builtins.print") as mock_print:
            print_queue_items(None)
            mock_print.assert_called_once_with("No items in queue")

    def test_main_list_command(self):
        """Test main function with list command."""
        with patch("cli.qtool.list_queue") as mock_list:
            with patch("cli.qtool.sys.argv", ["qtool.py", "list"]):
                main()
                mock_list.assert_called_once()

    def test_main_flush_command(self):
        """Test main function with flush command."""
        with patch("cli.qtool.flush_queue") as mock_flush:
            with patch("cli.qtool.sys.argv", ["qtool.py", "flush"]):
                main()
                mock_flush.assert_called_once()

    def test_main_delete_command(self):
        """Test main function with delete command."""
        with patch("cli.qtool.delete_queue") as mock_delete:
            with patch("cli.qtool.sys.argv", ["qtool.py", "delete", "123"]):
                main()
                mock_delete.assert_called_once_with(123)

    def test_main_delete_command_invalid_id(self):
        """Test main function with delete command and invalid ID."""
        with patch("cli.qtool.sys.argv", ["qtool.py", "delete", "invalid"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        with patch("cli.qtool.sys.argv", ["qtool.py", "invalid"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_main_no_args(self):
        """Test main function with no arguments."""
        with patch("cli.qtool.sys.argv", ["qtool.py"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_print_queue_items_with_missing_fields(self):
        """Test printing queue items with missing fields."""
        test_items = [
            {"id": 1, "message": "test1"},  # Missing display_name
            {"id": 2, "display_name": "User2"},  # Missing message
        ]

        with patch("builtins.print") as mock_print:
            print_queue_items(test_items)

            # Should handle missing fields gracefully
            assert mock_print.call_count == 3
            mock_print.assert_any_call("Queue Items:")

    def test_print_queue_items_with_special_characters(self):
        """Test printing queue items with special characters."""
        test_items = [{"id": 1, "message": "test@#$%", "display_name": "User@#$%"}]

        with patch("builtins.print") as mock_print:
            print_queue_items(test_items)

            # Should print special characters correctly
            assert mock_print.call_count == 2
            mock_print.assert_any_call("Queue Items:")
            mock_print.assert_any_call("ID: 1, Message: test@#$%, User: User@#$%")

    def test_print_json_with_special_characters(self):
        """Test printing JSON with special characters."""
        test_data = {"key": "value@#$%", "special": "chars!@#"}

        with patch("builtins.print") as mock_print:
            print_json(test_data)
            mock_print.assert_called_once_with(json.dumps(test_data, indent=2))

    def test_flush_queue_with_exception(self):
        """Test flushing queue with exception."""
        with patch(
            "cli.qtool.flush_queue_items", side_effect=Exception("Database error")
        ):
            with patch("builtins.print") as mock_print:
                flush_queue()
                mock_print.assert_called()

    def test_delete_queue_with_exception(self):
        """Test deleting queue item with exception."""
        with patch(
            "cli.qtool.delete_queue_item", side_effect=Exception("Database error")
        ):
            with patch("builtins.print") as mock_print:
                delete_queue(123)
                mock_print.assert_called()

    def test_list_queue_with_exception(self):
        """Test listing queue with exception."""
        with patch(
            "cli.qtool.get_queue_items", side_effect=Exception("Database error")
        ):
            with patch("builtins.print") as mock_print:
                list_queue()
                mock_print.assert_called()

    def test_main_delete_command_no_id(self):
        """Test main function with delete command but no ID."""
        with patch("cli.qtool.sys.argv", ["qtool.py", "delete"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_print_queue_items_with_none_values(self):
        """Test printing queue items with None values."""
        test_items = [
            {"id": None, "message": "test1", "display_name": "User1"},
            {"id": 2, "message": None, "display_name": "User2"},
            {"id": 3, "message": "test3", "display_name": None},
        ]

        with patch("builtins.print") as mock_print:
            print_queue_items(test_items)

            # Should handle None values gracefully
            assert mock_print.call_count == 4
            mock_print.assert_any_call("Queue Items:")
