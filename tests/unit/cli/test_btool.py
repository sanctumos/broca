"""
Tests for CLI bot management tool (btool.py).
"""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

from cli.btool import (
    add_bot,
    get_ignore_list_path,
    list_bots,
    load_ignore_list,
    main,
    remove_bot,
    save_ignore_list,
)


class TestBtoolFunctions:
    """Test btool.py functions."""

    def test_get_ignore_list_path(self):
        """Test getting ignore list path."""
        path = get_ignore_list_path()
        assert isinstance(path, Path)
        assert path.name == "telegram_ignore_list.json"

    def test_load_ignore_list_file_exists(self):
        """Test loading ignore list when file exists."""
        mock_data = {
            "bot1": {"id": "123", "username": "testbot1"},
            "bot2": {"id": "456", "username": "testbot2"},
        }

        with patch("cli.btool.get_ignore_list_path") as mock_path, patch(
            "builtins.open", mock_open(read_data=json.dumps(mock_data))
        ), patch("pathlib.Path.exists", return_value=True):
            mock_path.return_value = Path("test.json")
            result = load_ignore_list()

            assert result == mock_data

    def test_load_ignore_list_file_not_exists(self):
        """Test loading ignore list when file doesn't exist."""
        with patch("cli.btool.get_ignore_list_path") as mock_path, patch(
            "pathlib.Path.exists", return_value=False
        ):
            mock_path.return_value = Path("test.json")
            result = load_ignore_list()

            assert result == {}

    def test_load_ignore_list_json_decode_error(self):
        """Test loading ignore list with JSON decode error."""
        with patch("cli.btool.get_ignore_list_path") as mock_path, patch(
            "builtins.open", mock_open(read_data="invalid json")
        ), patch("pathlib.Path.exists", return_value=True), patch(
            "cli.btool.logger"
        ) as mock_logger:
            mock_path.return_value = Path("test.json")
            result = load_ignore_list()

            assert result == {}
            mock_logger.error.assert_called_once_with(
                "Failed to parse ignore list file"
            )

    def test_save_ignore_list(self):
        """Test saving ignore list."""
        mock_data = {
            "bot1": {"id": "123", "username": "testbot1"},
            "bot2": {"id": "456", "username": "testbot2"},
        }

        with patch("cli.btool.get_ignore_list_path") as mock_path, patch(
            "builtins.open", mock_open()
        ) as mock_file:
            mock_path.return_value = Path("test.json")
            save_ignore_list(mock_data)

            mock_file.assert_called_once_with(Path("test.json"), "w")
            mock_file.return_value.write.assert_called_once_with(
                json.dumps(mock_data, indent=2)
            )

    def test_add_bot_new_bot(self):
        """Test adding new bot to ignore list."""
        existing_data = {"bot1": {"id": "123", "username": "testbot1"}}

        with patch("cli.btool.load_ignore_list", return_value=existing_data), patch(
            "cli.btool.save_ignore_list"
        ) as mock_save:
            add_bot("testbot2", "456")

            expected_data = {
                "bot1": {"id": "123", "username": "testbot1"},
                "testbot2": {"id": "456", "username": "testbot2"},
            }
            mock_save.assert_called_once_with(expected_data)

    def test_add_bot_existing_bot(self):
        """Test adding existing bot to ignore list."""
        existing_data = {"bot1": {"id": "123", "username": "testbot1"}}

        with patch("cli.btool.load_ignore_list", return_value=existing_data), patch(
            "cli.btool.save_ignore_list"
        ) as mock_save:
            add_bot("bot1", "456")

            expected_data = {"bot1": {"id": "456", "username": "bot1"}}
            mock_save.assert_called_once_with(expected_data)

    def test_remove_bot_existing_bot(self):
        """Test removing existing bot from ignore list."""
        existing_data = {
            "bot1": {"id": "123", "username": "testbot1"},
            "bot2": {"id": "456", "username": "testbot2"},
        }

        with patch("cli.btool.load_ignore_list", return_value=existing_data), patch(
            "cli.btool.save_ignore_list"
        ) as mock_save:
            remove_bot("bot1")

            expected_data = {"bot2": {"id": "456", "username": "testbot2"}}
            mock_save.assert_called_once_with(expected_data)

    def test_remove_bot_nonexistent_bot(self):
        """Test removing non-existent bot from ignore list."""
        existing_data = {"bot1": {"id": "123", "username": "testbot1"}}

        with patch("cli.btool.load_ignore_list", return_value=existing_data), patch(
            "cli.btool.save_ignore_list"
        ) as mock_save:
            remove_bot("bot2")

            # Should save the same data since bot2 doesn't exist
            mock_save.assert_called_once_with(existing_data)

    def test_list_bots_with_data(self):
        """Test listing bots with data."""
        mock_data = {
            "bot1": {"id": "123", "username": "testbot1"},
            "bot2": {"id": "456", "username": "testbot2"},
        }

        with patch("cli.btool.load_ignore_list", return_value=mock_data), patch(
            "builtins.print"
        ) as mock_print:
            list_bots()

            # Should print each bot
            assert mock_print.call_count >= 2

    def test_list_bots_empty(self):
        """Test listing bots when list is empty."""
        with patch("cli.btool.load_ignore_list", return_value={}), patch(
            "builtins.print"
        ) as mock_print:
            list_bots()

            # Should print "No ignored bots"
            mock_print.assert_called_once()

    def test_main_add_command(self):
        """Test main function with add command."""
        with patch("cli.btool.add_bot") as mock_add, patch(
            "sys.argv", ["btool.py", "add", "testbot", "123"]
        ):
            main()
            mock_add.assert_called_once_with("testbot", "123")

    def test_main_remove_command(self):
        """Test main function with remove command."""
        with patch("cli.btool.remove_bot") as mock_remove, patch(
            "sys.argv", ["btool.py", "remove", "testbot"]
        ):
            main()
            mock_remove.assert_called_once_with("testbot")

    def test_main_list_command(self):
        """Test main function with list command."""
        with patch("cli.btool.list_bots") as mock_list, patch(
            "sys.argv", ["btool.py", "list"]
        ):
            main()
            mock_list.assert_called_once()

    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        with patch("sys.argv", ["btool.py", "invalid"]), patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)

    def test_main_insufficient_args(self):
        """Test main function with insufficient arguments."""
        with patch("sys.argv", ["btool.py"]), patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)
