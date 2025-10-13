"""Extended unit tests for CLI tools - btool.py."""

import json
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


class TestBtoolExtended:
    """Extended test cases for btool.py."""

    def test_get_ignore_list_path_default(self):
        """Test getting default ignore list path."""
        with patch("cli.btool.os.path.expanduser", return_value="/home/user"):
            path = get_ignore_list_path()
            assert path == "/home/user/telegram_ignore_list.json"

    def test_get_ignore_list_path_custom(self):
        """Test getting custom ignore list path."""
        custom_path = "/custom/path/ignore.json"
        with patch("cli.btool.os.path.expanduser", return_value="/custom/path"):
            with patch("cli.btool.os.getenv", return_value=custom_path):
                path = get_ignore_list_path()
                assert path == custom_path

    def test_load_ignore_list_file_exists(self):
        """Test loading ignore list when file exists."""
        test_data = {"bots": ["bot1", "bot2"]}

        with patch("cli.btool.get_ignore_list_path", return_value="/test/path.json"):
            with patch("cli.btool.os.path.exists", return_value=True):
                with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
                    result = load_ignore_list()
                    assert result == test_data

    def test_load_ignore_list_file_not_exists(self):
        """Test loading ignore list when file doesn't exist."""
        with patch("cli.btool.get_ignore_list_path", return_value="/test/path.json"):
            with patch("cli.btool.os.path.exists", return_value=False):
                result = load_ignore_list()
                assert result == {"bots": []}

    def test_load_ignore_list_invalid_json(self):
        """Test loading ignore list with invalid JSON."""
        with patch("cli.btool.get_ignore_list_path", return_value="/test/path.json"):
            with patch("cli.btool.os.path.exists", return_value=True):
                with patch("builtins.open", mock_open(read_data="invalid json")):
                    result = load_ignore_list()
                    assert result == {"bots": []}

    def test_save_ignore_list(self):
        """Test saving ignore list."""
        test_data = {"bots": ["bot1", "bot2"]}

        with patch("cli.btool.get_ignore_list_path", return_value="/test/path.json"):
            with patch("builtins.open", mock_open()) as mock_file:
                save_ignore_list(test_data)
                mock_file.assert_called_once_with("/test/path.json", "w")
                mock_file().write.assert_called_once_with(
                    json.dumps(test_data, indent=2)
                )

    def test_add_bot_new_bot(self):
        """Test adding a new bot."""
        test_data = {"bots": ["bot1"]}
        new_bot = "bot2"

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("cli.btool.save_ignore_list") as mock_save:
                add_bot(new_bot)

                expected_data = {"bots": ["bot1", "bot2"]}
                mock_save.assert_called_once_with(expected_data)

    def test_add_bot_existing_bot(self):
        """Test adding an existing bot."""
        test_data = {"bots": ["bot1", "bot2"]}
        existing_bot = "bot1"

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("cli.btool.save_ignore_list") as mock_save:
                add_bot(existing_bot)

                # Should not save since bot already exists
                mock_save.assert_not_called()

    def test_remove_bot_existing_bot(self):
        """Test removing an existing bot."""
        test_data = {"bots": ["bot1", "bot2"]}
        bot_to_remove = "bot1"

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("cli.btool.save_ignore_list") as mock_save:
                remove_bot(bot_to_remove)

                expected_data = {"bots": ["bot2"]}
                mock_save.assert_called_once_with(expected_data)

    def test_remove_bot_nonexistent_bot(self):
        """Test removing a non-existent bot."""
        test_data = {"bots": ["bot1", "bot2"]}
        bot_to_remove = "bot3"

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("cli.btool.save_ignore_list") as mock_save:
                remove_bot(bot_to_remove)

                # Should not save since bot doesn't exist
                mock_save.assert_not_called()

    def test_list_bots_with_bots(self):
        """Test listing bots when bots exist."""
        test_data = {"bots": ["bot1", "bot2"]}

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("builtins.print") as mock_print:
                list_bots()

                # Should print each bot
                assert mock_print.call_count == 2
                mock_print.assert_any_call("bot1")
                mock_print.assert_any_call("bot2")

    def test_list_bots_empty(self):
        """Test listing bots when no bots exist."""
        test_data = {"bots": []}

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("builtins.print") as mock_print:
                list_bots()

                # Should print "No bots in ignore list"
                mock_print.assert_called_once_with("No bots in ignore list")

    def test_main_add_command(self):
        """Test main function with add command."""
        with patch("cli.btool.add_bot") as mock_add:
            with patch("cli.btool.sys.argv", ["btool.py", "add", "testbot"]):
                main()
                mock_add.assert_called_once_with("testbot")

    def test_main_remove_command(self):
        """Test main function with remove command."""
        with patch("cli.btool.remove_bot") as mock_remove:
            with patch("cli.btool.sys.argv", ["btool.py", "remove", "testbot"]):
                main()
                mock_remove.assert_called_once_with("testbot")

    def test_main_list_command(self):
        """Test main function with list command."""
        with patch("cli.btool.list_bots") as mock_list:
            with patch("cli.btool.sys.argv", ["btool.py", "list"]):
                main()
                mock_list.assert_called_once()

    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        with patch("cli.btool.sys.argv", ["btool.py", "invalid"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_main_no_args(self):
        """Test main function with no arguments."""
        with patch("cli.btool.sys.argv", ["btool.py"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_add_bot_with_empty_list(self):
        """Test adding bot to empty list."""
        test_data = {"bots": []}
        new_bot = "bot1"

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("cli.btool.save_ignore_list") as mock_save:
                add_bot(new_bot)

                expected_data = {"bots": ["bot1"]}
                mock_save.assert_called_once_with(expected_data)

    def test_remove_bot_from_empty_list(self):
        """Test removing bot from empty list."""
        test_data = {"bots": []}
        bot_to_remove = "bot1"

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("cli.btool.save_ignore_list") as mock_save:
                remove_bot(bot_to_remove)

                # Should not save since list is empty
                mock_save.assert_not_called()

    def test_load_ignore_list_file_error(self):
        """Test loading ignore list with file error."""
        with patch("cli.btool.get_ignore_list_path", return_value="/test/path.json"):
            with patch("cli.btool.os.path.exists", return_value=True):
                with patch("builtins.open", side_effect=OSError("File error")):
                    result = load_ignore_list()
                    assert result == {"bots": []}

    def test_save_ignore_list_file_error(self):
        """Test saving ignore list with file error."""
        test_data = {"bots": ["bot1"]}

        with patch("cli.btool.get_ignore_list_path", return_value="/test/path.json"):
            with patch("builtins.open", side_effect=OSError("File error")):
                # Should not raise exception
                save_ignore_list(test_data)

    def test_add_bot_with_special_characters(self):
        """Test adding bot with special characters."""
        test_data = {"bots": []}
        special_bot = "bot@#$%"

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("cli.btool.save_ignore_list") as mock_save:
                add_bot(special_bot)

                expected_data = {"bots": ["bot@#$%"]}
                mock_save.assert_called_once_with(expected_data)

    def test_list_bots_with_special_characters(self):
        """Test listing bots with special characters."""
        test_data = {"bots": ["bot@#$%", "bot!@#"]}

        with patch("cli.btool.load_ignore_list", return_value=test_data):
            with patch("builtins.print") as mock_print:
                list_bots()

                # Should print each bot including special characters
                assert mock_print.call_count == 2
                mock_print.assert_any_call("bot@#$%")
                mock_print.assert_any_call("bot!@#")
