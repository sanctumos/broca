"""Extended unit tests for CLI tools - btool.py."""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from cli.btool import (
    add_bot,
    get_ignore_list_path,
    list_bots,
    load_ignore_list,
    main,
    remove_bot,
    save_ignore_list,
)


class TestBtoolExtended:
    """Extended test cases for btool.py."""

    def test_get_ignore_list_path_default(self):
        """Test getting default ignore list path."""
        path = get_ignore_list_path()
        assert path == Path("telegram_ignore_list.json")

    def test_get_ignore_list_path_custom(self):
        """Test getting custom ignore list path."""
        # The function doesn't support custom paths, it always returns the same path
        path = get_ignore_list_path()
        assert path == Path("telegram_ignore_list.json")

    def test_load_ignore_list_file_exists(self):
        """Test loading ignore list when file exists."""
        test_data = {"bots": ["bot1", "bot2"]}

        with patch("cli.btool.get_ignore_list_path") as mock_path:
            mock_path.return_value.exists.return_value = True
            with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
                result = load_ignore_list()
                assert result == test_data

    def test_load_ignore_list_file_not_exists(self):
        """Test loading ignore list when file doesn't exist."""
        with patch("cli.btool.get_ignore_list_path") as mock_path:
            mock_path.return_value.exists.return_value = False
            result = load_ignore_list()
            assert result == {}

    def test_load_ignore_list_invalid_json(self):
        """Test loading ignore list with invalid JSON."""
        with patch("cli.btool.get_ignore_list_path") as mock_path:
            mock_path.return_value.exists.return_value = True
            with patch("builtins.open", mock_open(read_data="invalid json")):
                result = load_ignore_list()
                assert result == {}

    def test_save_ignore_list(self):
        """Test saving ignore list."""
        test_data = {"bots": ["bot1", "bot2"]}

        with patch("cli.btool.get_ignore_list_path", return_value="/test/path.json"):
            with patch("builtins.open", mock_open()) as mock_file:
                save_ignore_list(test_data)
                mock_file.assert_called_once_with("/test/path.json", "w")
                # json.dump() calls write multiple times, so we check that write was called
                assert mock_file().write.called

    def test_add_bot_new_bot(self):
        """Test adding a new bot."""
        test_data = {"123": {"username": "bot1"}}
        new_bot = "bot2"

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("cli.btool.save_ignore_list") as mock_save:
                add_bot(new_bot)

                expected_data = {
                    "123": {"username": "bot1"},
                    "bot2": {"username": "bot2"},
                }
                mock_save.assert_called_once_with(expected_data)

    def test_add_bot_existing_bot(self):
        """Test adding an existing bot."""
        test_data = {"123": {"username": "bot1"}, "456": {"username": "bot2"}}
        existing_bot = "bot1"

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("cli.btool.save_ignore_list") as mock_save:
                add_bot(existing_bot)

                # Should not save since bot already exists
                mock_save.assert_not_called()

    def test_remove_bot_existing_bot(self):
        """Test removing an existing bot."""
        test_data = {"123": {"username": "bot1"}, "456": {"username": "bot2"}}
        bot_to_remove = "123"

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("cli.btool.save_ignore_list") as mock_save:
                remove_bot(bot_to_remove)

                expected_data = {"456": {"username": "bot2"}}
                mock_save.assert_called_once_with(expected_data)

    def test_remove_bot_nonexistent_bot(self):
        """Test removing a non-existent bot."""
        test_data = {"123": {"username": "bot1"}, "456": {"username": "bot2"}}
        bot_to_remove = "789"

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("cli.btool.save_ignore_list") as mock_save:
                remove_bot(bot_to_remove)

                # Should not save since bot doesn't exist
                mock_save.assert_not_called()

    def test_list_bots_with_bots(self):
        """Test listing bots when bots exist."""
        test_data = {"123": {"username": "bot1"}, "456": {"username": "bot2"}}

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("builtins.print") as mock_print:
                list_bots()

                # Should print information about the bots
                assert mock_print.called

    def test_list_bots_empty(self):
        """Test listing bots when no bots exist."""
        test_data = {}

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("builtins.print") as mock_print:
                list_bots()

                # Should print "No bots in ignore list"
                mock_print.assert_called_once_with("No bots in ignore list")

    def test_main_add_command(self):
        """Test main function with add command."""
        with patch("cli.btool.add_bot") as mock_add:
            with patch("sys.argv", ["btool.py", "add", "testbot"]):
                main()
                mock_add.assert_called_once_with("testbot", None)

    def test_main_remove_command(self):
        """Test main function with remove command."""
        with patch("cli.btool.remove_bot") as mock_remove:
            with patch("sys.argv", ["btool.py", "remove", "testbot"]):
                main()
                mock_remove.assert_called_once_with("testbot")

    def test_main_list_command(self):
        """Test main function with list command."""
        with patch("cli.btool.list_bots") as mock_list:
            with patch("sys.argv", ["btool.py", "list"]):
                main()
                mock_list.assert_called_once()

    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        with patch("sys.argv", ["btool.py", "invalid"]):
            with patch("sys.exit") as mock_exit:
                main()
                mock_exit.assert_called_with(2)

    def test_main_no_args(self):
        """Test main function with no arguments."""
        with patch("sys.argv", ["btool.py"]):
            # When no command is provided, argparse just prints help and doesn't call print()
            # The help is printed to stdout by argparse, not by our code
            main()
            # No specific assertion needed - the function should complete without error

    def test_add_bot_with_empty_list(self):
        """Test adding bot to empty list."""
        test_data = {}
        new_bot = "bot1"

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("cli.btool.save_ignore_list") as mock_save:
                add_bot(new_bot)

                expected_data = {"bot1": {"username": "bot1"}}
                mock_save.assert_called_once_with(expected_data)

    def test_remove_bot_from_empty_list(self):
        """Test removing bot from empty list."""
        test_data = {}
        bot_to_remove = "bot1"

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("cli.btool.save_ignore_list") as mock_save:
                remove_bot(bot_to_remove)

                # Should not save since bot doesn't exist
                mock_save.assert_not_called()

    def test_load_ignore_list_file_error(self):
        """Test loading ignore list with file error."""
        with patch("cli.btool.get_ignore_list_path") as mock_path:
            mock_path.return_value.exists.return_value = True
            with patch("builtins.open", side_effect=OSError("File error")):
                # Should raise the OSError since it's not handled
                with pytest.raises(OSError):
                    load_ignore_list()

    def test_save_ignore_list_file_error(self):
        """Test saving ignore list with file error."""
        test_data = {"123": {"username": "bot1"}}

        with patch("cli.btool.get_ignore_list_path", return_value="/test/path.json"):
            with patch("builtins.open", side_effect=OSError("File error")):
                # Should raise OSError
                with pytest.raises(OSError, match="File error"):
                    save_ignore_list(test_data)

    def test_add_bot_with_special_characters(self):
        """Test adding bot with special characters."""
        test_data = {}
        special_bot = "bot@#$%"

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("cli.btool.save_ignore_list") as mock_save:
                add_bot(special_bot)

                expected_data = {"bot@#$%": {"username": "bot@#$%"}}
                mock_save.assert_called_once_with(expected_data)

    def test_list_bots_with_special_characters(self):
        """Test listing bots with special characters."""
        test_data = {"123": {"username": "bot@#$%"}, "456": {"username": "bot!@#"}}

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("builtins.print") as mock_print:
                list_bots()

                # Should print information about the bots
                assert mock_print.called
