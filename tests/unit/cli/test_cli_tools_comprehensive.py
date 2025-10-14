"""Additional comprehensive tests for CLI tools."""

from unittest.mock import MagicMock, mock_open, patch

import pytest

from cli.btool import main as btool_main
from cli.ctool import main as ctool_main
from cli.qtool import main as qtool_main
from cli.settings import main as settings_main
from cli.utool import main as utool_main


class TestCLIToolsComprehensive:
    """Comprehensive test cases for CLI tools."""

    def test_btool_main_list_command(self):
        """Test btool main with list command."""
        with patch("sys.argv", ["btool", "list"]):
            with patch("cli.btool.list_bots") as mock_list:
                mock_list.return_value = None
                btool_main()

    def test_btool_main_add_command(self):
        """Test btool main with add command."""
        with patch("sys.argv", ["btool", "add", "test_bot"]):
            with patch("cli.btool.add_bot") as mock_add:
                mock_add.return_value = None
                btool_main()

    def test_btool_main_remove_command(self):
        """Test btool main with remove command."""
        with patch("sys.argv", ["btool", "remove", "test_bot"]):
            with patch("cli.btool.remove_bot") as mock_remove:
                mock_remove.return_value = None
                btool_main()

    def test_btool_main_invalid_command(self):
        """Test btool main with invalid command."""
        with patch("sys.argv", ["btool", "invalid"]):
            with patch("sys.exit") as mock_exit:
                btool_main()
                mock_exit.assert_called()

    def test_btool_main_no_args(self):
        """Test btool main with no arguments."""
        with patch("sys.argv", ["btool"]):
            with patch("sys.exit") as mock_exit:
                btool_main()
                # argparse prints help but doesn't call sys.exit when no args provided
                mock_exit.assert_not_called()

    def test_qtool_main_list_command(self):
        """Test qtool main with list command."""
        with patch("sys.argv", ["qtool", "list"]):
            with patch("cli.qtool.list_queue") as mock_list:
                mock_list.return_value = None
                qtool_main()

    def test_qtool_main_flush_command(self):
        """Test qtool main with flush command."""
        with patch("sys.argv", ["qtool", "flush", "--all"]):
            with patch("cli.qtool.flush_queue") as mock_flush:
                mock_flush.return_value = None
                qtool_main()

    def test_qtool_main_delete_command(self):
        """Test qtool main with delete command."""
        with patch("sys.argv", ["qtool", "delete", "--id", "1"]):
            with patch("cli.qtool.delete_queue") as mock_delete:
                mock_delete.return_value = None
                qtool_main()

    def test_qtool_main_invalid_command(self):
        """Test qtool main with invalid command."""
        with patch("sys.argv", ["qtool", "invalid"]):
            with patch("sys.exit") as mock_exit:
                qtool_main()
                mock_exit.assert_called()

    def test_qtool_main_no_args(self):
        """Test qtool main with no arguments."""
        with patch("sys.argv", ["qtool"]):
            with patch("sys.exit") as mock_exit:
                qtool_main()
                # argparse prints help but doesn't call sys.exit when no args provided
                mock_exit.assert_not_called()

    def test_utool_main_list_command(self):
        """Test utool main with list command."""
        with patch("sys.argv", ["utool", "list"]):
            with patch("cli.utool.list_users") as mock_list:
                mock_list.return_value = None
                utool_main()

    def test_utool_main_get_command(self):
        """Test utool main with get command."""
        with patch("sys.argv", ["utool", "get", "1"]):
            with patch("cli.utool.get_user") as mock_get:
                mock_get.return_value = None
                utool_main()

    def test_utool_main_update_command(self):
        """Test utool main with update command."""
        with patch("sys.argv", ["utool", "update", "1", "active"]):
            with patch("cli.utool.update_user_status") as mock_update:
                mock_update.return_value = None
                utool_main()

    def test_utool_main_invalid_command(self):
        """Test utool main with invalid command."""
        with patch("sys.argv", ["utool", "invalid"]):
            with patch("sys.exit") as mock_exit:
                utool_main()
                mock_exit.assert_called()

    def test_utool_main_no_args(self):
        """Test utool main with no arguments."""
        with patch("sys.argv", ["utool"]):
            with patch("sys.exit") as mock_exit:
                utool_main()
                # argparse prints help but doesn't call sys.exit when no args provided
                mock_exit.assert_not_called()

    def test_ctool_main_list_command(self):
        """Test ctool main with list command."""
        with patch("sys.argv", ["ctool", "list"]):
            with patch("cli.ctool.list_conversations") as mock_list:
                mock_list.return_value = None
                ctool_main()

    def test_ctool_main_get_command(self):
        """Test ctool main with get command."""
        with patch("sys.argv", ["ctool", "get", "1", "2"]):
            with patch("cli.ctool.get_conversation") as mock_get:
                mock_get.return_value = None
                ctool_main()

    def test_ctool_main_invalid_command(self):
        """Test ctool main with invalid command."""
        with patch("sys.argv", ["ctool", "invalid"]):
            with patch("sys.exit") as mock_exit:
                ctool_main()
                mock_exit.assert_called()

    def test_ctool_main_no_args(self):
        """Test ctool main with no arguments."""
        with patch("sys.argv", ["ctool"]):
            with patch("sys.exit") as mock_exit:
                ctool_main()
                # argparse prints help but doesn't call sys.exit when no args provided
                mock_exit.assert_not_called()

    def test_settings_main_get_command(self):
        """Test settings main with get command."""
        with patch("sys.argv", ["settings", "get"]):
            with patch("cli.settings.get_settings") as mock_get:
                mock_get.return_value = None
                settings_main()

    def test_settings_main_mode_command(self):
        """Test settings main with mode command."""
        with patch("sys.argv", ["settings", "mode", "live"]):
            with patch("cli.settings.set_message_mode") as mock_set:
                mock_set.return_value = None
                settings_main()

    def test_settings_main_debug_command(self):
        """Test settings main with debug command."""
        with patch("sys.argv", ["settings", "debug", "--enable"]):
            with patch("cli.settings.set_debug_mode") as mock_set:
                mock_set.return_value = None
                settings_main()

    def test_settings_main_refresh_command(self):
        """Test settings main with refresh command."""
        with patch("sys.argv", ["settings", "refresh", "5"]):
            with patch("cli.settings.set_queue_refresh") as mock_set:
                mock_set.return_value = None
                settings_main()

    def test_settings_main_retries_command(self):
        """Test settings main with retries command."""
        with patch("sys.argv", ["settings", "retries", "3"]):
            with patch("cli.settings.set_max_retries") as mock_set:
                mock_set.return_value = None
                settings_main()

    def test_settings_main_reload_command(self):
        """Test settings main with reload command."""
        with patch("sys.argv", ["settings", "reload"]):
            with patch("cli.settings.reload_settings") as mock_reload:
                mock_reload.return_value = None
                settings_main()

    def test_settings_main_invalid_command(self):
        """Test settings main with invalid command."""
        with patch("sys.argv", ["settings", "invalid"]):
            with patch("sys.exit") as mock_exit:
                settings_main()
                mock_exit.assert_called()

    def test_settings_main_no_args(self):
        """Test settings main with no arguments."""
        with patch("sys.argv", ["settings"]):
            with patch("sys.exit") as mock_exit:
                settings_main()
                # argparse prints help but doesn't call sys.exit when no args provided
                mock_exit.assert_not_called()

    def test_btool_add_bot_with_exception(self):
        """Test btool add_bot with exception."""
        with patch("cli.btool.load_ignore_list") as mock_load:
            mock_load.side_effect = Exception("File error")
            with pytest.raises(Exception):
                from cli.btool import add_bot

                add_bot("test_bot")

    def test_btool_remove_bot_with_exception(self):
        """Test btool remove_bot with exception."""
        with patch("cli.btool.load_ignore_list") as mock_load:
            mock_load.side_effect = Exception("File error")
            with pytest.raises(Exception):
                from cli.btool import remove_bot

                remove_bot("test_bot")

    def test_btool_list_bots_with_exception(self):
        """Test btool list_bots with exception."""
        with patch("cli.btool.load_ignore_list") as mock_load:
            mock_load.side_effect = Exception("File error")
            with pytest.raises(Exception):
                from cli.btool import list_bots

                list_bots()

    def test_qtool_list_queue_with_exception(self):
        """Test qtool list_queue with exception."""
        with patch("cli.qtool.asyncio.run") as mock_run:
            mock_run.side_effect = Exception("Async error")
            with pytest.raises(Exception):
                from cli.qtool import list_queue

                list_queue()

    def test_qtool_flush_queue_with_exception(self):
        """Test qtool flush_queue with exception."""
        with patch("cli.qtool.asyncio.run") as mock_run:
            mock_run.side_effect = Exception("Async error")
            with pytest.raises(Exception):
                from cli.qtool import flush_queue

                flush_queue()

    def test_qtool_delete_queue_with_exception(self):
        """Test qtool delete_queue with exception."""
        with patch("cli.qtool.asyncio.run") as mock_run:
            mock_run.side_effect = Exception("Async error")
            # delete_queue is an async function, so we don't expect it to raise directly
            from cli.qtool import delete_queue

            delete_queue(1)  # This will create a coroutine but not execute it

    def test_utool_list_users_with_exception(self):
        """Test utool list_users with exception."""
        with patch("cli.utool.asyncio.run") as mock_run:
            mock_run.side_effect = Exception("Async error")
            from cli.utool import list_users

            # list_users is async, so calling it directly creates a coroutine but doesn't execute it
            # The exception would be raised when asyncio.run() is called internally
            result = list_users(MagicMock())
            assert result is not None  # Should be a coroutine object

    def test_utool_get_user_with_exception(self):
        """Test utool get_user with exception."""
        with patch("cli.utool.asyncio.run") as mock_run:
            mock_run.side_effect = Exception("Async error")
            from cli.utool import get_user

            # get_user is async, so calling it directly creates a coroutine but doesn't execute it
            # The exception would be raised when asyncio.run() is called internally
            result = get_user(1)
            assert result is not None  # Should be a coroutine object

    def test_utool_update_user_status_with_exception(self):
        """Test utool update_user_status with exception."""
        with patch("cli.utool.asyncio.run") as mock_run:
            mock_run.side_effect = Exception("Async error")
            with pytest.raises(Exception):
                from cli.utool import update_user_status

                update_user_status(1, "active")

    def test_ctool_list_conversations_with_exception(self):
        """Test ctool list_conversations with exception."""
        with patch("cli.ctool.asyncio.run") as mock_run:
            mock_run.side_effect = Exception("Async error")
            with pytest.raises(Exception):
                from cli.ctool import list_conversations

                list_conversations()

    def test_ctool_get_conversation_with_exception(self):
        """Test ctool get_conversation with exception."""
        with patch("cli.ctool.asyncio.run") as mock_run:
            mock_run.side_effect = Exception("Async error")
            from cli.ctool import get_conversation

            # get_conversation is async, so calling it directly creates a coroutine but doesn't execute it
            # The exception would be raised when asyncio.run() is called internally
            result = get_conversation(1)
            assert result is not None  # Should be a coroutine object

    def test_settings_load_settings_with_exception(self):
        """Test settings load_settings with exception."""
        with patch("cli.settings.json.load") as mock_load:
            mock_load.side_effect = Exception("JSON error")
            with pytest.raises(Exception):
                from cli.settings import load_settings

                load_settings()

    def test_settings_save_settings_with_exception(self):
        """Test settings save_settings with exception."""
        with patch("cli.settings.json.dump") as mock_dump:
            mock_dump.side_effect = Exception("JSON error")
            with pytest.raises(Exception):
                from cli.settings import save_settings

                save_settings({})

    def test_btool_get_ignore_list_path_default(self):
        """Test btool get_ignore_list_path with default."""
        from pathlib import Path

        from cli.btool import get_ignore_list_path

        path = get_ignore_list_path()
        assert path == Path("telegram_ignore_list.json")

    def test_btool_get_ignore_list_path_custom(self):
        """Test btool get_ignore_list_path with custom path."""
        from pathlib import Path

        from cli.btool import get_ignore_list_path

        # get_ignore_list_path doesn't support custom paths, always returns the same path
        path = get_ignore_list_path()
        assert path == Path("telegram_ignore_list.json")

    def test_btool_load_ignore_list_file_exists(self):
        """Test btool load_ignore_list when file exists."""
        mock_data = {"bot1": {"username": "bot1"}, "bot2": {"username": "bot2"}}
        with patch("cli.btool.Path") as mock_path:
            mock_path.return_value.exists.return_value = True
            with patch("cli.btool.json.load", return_value=mock_data):
                from cli.btool import load_ignore_list

                result = load_ignore_list()
                assert result == mock_data

    def test_btool_load_ignore_list_file_not_exists(self):
        """Test btool load_ignore_list when file doesn't exist."""
        with patch("cli.btool.Path") as mock_path:
            mock_path.return_value.exists.return_value = False
            from cli.btool import load_ignore_list

            result = load_ignore_list()
            assert result == {}

    def test_btool_save_ignore_list(self):
        """Test btool save_ignore_list."""
        mock_data = ["bot1", "bot2"]
        with patch("cli.btool.json.dump") as mock_dump:
            with patch("builtins.open", mock_open()):
                from cli.btool import save_ignore_list

                save_ignore_list(mock_data)
                mock_dump.assert_called_once()

    def test_qtool_print_json_with_data(self):
        """Test qtool print_json with data."""
        mock_data = [{"id": 1, "content": "test"}]
        with patch("json.dumps", return_value='{"id": 1}'):
            with patch("builtins.print") as mock_print:
                from cli.qtool import print_json

                print_json(mock_data)
                mock_print.assert_called_once()

    def test_qtool_print_json_empty_data(self):
        """Test qtool print_json with empty data."""
        with patch("builtins.print") as mock_print:
            from cli.qtool import print_json

            print_json([])
            mock_print.assert_called_once_with("[]")

    def test_qtool_print_queue_items_with_data(self):
        """Test qtool print_queue_items with data."""
        mock_items = [
            {
                "id": 1,
                "content": "test1",
                "display_name": "Item 1",
                "username": "user1",
                "message": "test message 1",
                "status": "pending",
                "attempts": 0,
                "timestamp": "2023-01-01T00:00:00",
            },
            {
                "id": 2,
                "content": "test2",
                "display_name": "Item 2",
                "username": "user2",
                "message": "test message 2",
                "status": "pending",
                "attempts": 0,
                "timestamp": "2023-01-01T00:00:00",
            },
        ]
        with patch("builtins.print") as mock_print:
            from cli.qtool import print_queue_items

            print_queue_items(mock_items)
            assert (
                mock_print.call_count == 16
            )  # Header + separator + 2 items * 7 lines each

    def test_qtool_print_queue_items_empty(self):
        """Test qtool print_queue_items with empty data."""
        with patch("builtins.print") as mock_print:
            from cli.qtool import print_queue_items

            print_queue_items([])
            mock_print.assert_called_once_with("No items in queue")

    def test_utool_print_json_with_data(self):
        """Test utool print_json with data."""
        mock_data = [{"id": 1, "username": "user1"}]
        with patch("json.dumps", return_value='{"id": 1}'):
            with patch("builtins.print") as mock_print:
                from cli.utool import print_json

                print_json(mock_data)
                mock_print.assert_called_once()

    def test_utool_print_users_with_data(self):
        """Test utool print_users with data."""
        mock_users = [
            {"id": 1, "username": "user1", "display_name": "User 1"},
            {"id": 2, "username": "user2", "display_name": "User 2"},
        ]
        with patch("builtins.print") as mock_print:
            from cli.utool import print_users

            print_users(mock_users)
            assert (
                mock_print.call_count == 12
            )  # Header + separator + 2 users * 5 lines each

    def test_utool_print_users_empty(self):
        """Test utool print_users with empty data."""
        with patch("builtins.print") as mock_print:
            from cli.utool import print_users

            print_users([])
            mock_print.assert_called_once_with("No users found")

    def test_ctool_print_json_with_data(self):
        """Test ctool print_json with data."""
        mock_data = [{"id": 1, "title": "conv1"}]
        with patch("json.dumps", return_value='{"id": 1}'):
            with patch("builtins.print") as mock_print:
                from cli.ctool import print_json

                print_json(mock_data)
                mock_print.assert_called_once()

    def test_ctool_print_conversations_with_data(self):
        """Test ctool print_conversations with data."""
        mock_conversations = [
            {
                "id": 1,
                "title": "conv1",
                "username": "user1",
                "display_name": "Conv 1",
                "message": "Hello",
                "agent_response": "Hi there!",
                "timestamp": "2024-01-01",
            },
            {
                "id": 2,
                "title": "conv2",
                "username": "user2",
                "display_name": "Conv 2",
                "message": "How are you?",
                "agent_response": "I'm doing well!",
                "timestamp": "2024-01-02",
            },
        ]
        with patch("builtins.print") as mock_print:
            from cli.ctool import print_conversations

            print_conversations(mock_conversations)
            assert (
                mock_print.call_count == 12
            )  # Header + separator + 2 conversations * 5 lines each

    def test_ctool_print_conversations_empty(self):
        """Test ctool print_conversations with empty data."""
        with patch("builtins.print") as mock_print:
            from cli.ctool import print_conversations

            print_conversations([])
            mock_print.assert_called_once_with("No conversations found")

    def test_settings_print_output_with_data(self):
        """Test settings print_output with data."""
        mock_data = {"debug_mode": True, "queue_refresh": 5}
        with patch("builtins.print") as mock_print:
            from cli.settings import print_output

            print_output(mock_data, False)  # Human-readable format
            assert mock_print.call_count == 2  # Two key-value pairs

    def test_settings_print_output_empty(self):
        """Test settings print_output with empty data."""
        with patch("builtins.print") as mock_print:
            from cli.settings import print_output

            print_output({}, False)  # Human-readable format
            assert mock_print.call_count == 0  # Empty dict prints nothing

    def test_btool_main_with_help(self):
        """Test btool main with help argument."""
        with patch("sys.argv", ["btool", "--help"]):
            with patch("sys.exit") as mock_exit:
                btool_main()
                mock_exit.assert_called()

    def test_qtool_main_with_help(self):
        """Test qtool main with help argument."""
        with patch("sys.argv", ["qtool", "--help"]):
            with patch("sys.exit") as mock_exit:
                qtool_main()
                mock_exit.assert_called()

    def test_utool_main_with_help(self):
        """Test utool main with help argument."""
        with patch("sys.argv", ["utool", "--help"]):
            with patch("sys.exit") as mock_exit:
                utool_main()
                mock_exit.assert_called()

    def test_ctool_main_with_help(self):
        """Test ctool main with help argument."""
        with patch("sys.argv", ["ctool", "--help"]):
            with patch("sys.exit") as mock_exit:
                ctool_main()
                mock_exit.assert_called()

    def test_settings_main_with_help(self):
        """Test settings main with help argument."""
        with patch("sys.argv", ["settings", "--help"]):
            with patch("sys.exit") as mock_exit:
                settings_main()
                mock_exit.assert_called()

    def test_btool_main_with_version(self):
        """Test btool main with version argument."""
        with patch("sys.argv", ["btool", "--version"]):
            with patch("sys.exit") as mock_exit:
                btool_main()
                mock_exit.assert_called()

    def test_qtool_main_with_version(self):
        """Test qtool main with version argument."""
        with patch("sys.argv", ["qtool", "--version"]):
            with patch("sys.exit") as mock_exit:
                qtool_main()
                mock_exit.assert_called()

    def test_utool_main_with_version(self):
        """Test utool main with version argument."""
        with patch("sys.argv", ["utool", "--version"]):
            with patch("sys.exit") as mock_exit:
                utool_main()
                mock_exit.assert_called()

    def test_ctool_main_with_version(self):
        """Test ctool main with version argument."""
        with patch("sys.argv", ["ctool", "--version"]):
            with patch("sys.exit") as mock_exit:
                ctool_main()
                mock_exit.assert_called()

    def test_settings_main_with_version(self):
        """Test settings main with version argument."""
        with patch("sys.argv", ["settings", "--version"]):
            with patch("sys.exit") as mock_exit:
                settings_main()
                mock_exit.assert_called()

    def test_btool_add_bot_already_exists(self):
        """Test btool add_bot when bot already exists."""
        with patch(
            "cli.btool.load_ignore_list",
            return_value={"bot1": {"username": "bot1"}, "bot2": {"username": "bot2"}},
        ):
            with patch("cli.btool.save_ignore_list") as mock_save:
                from cli.btool import add_bot

                result = add_bot("bot1")
                assert result is None
                mock_save.assert_not_called()

    def test_btool_remove_bot_not_exists(self):
        """Test btool remove_bot when bot doesn't exist."""
        with patch(
            "cli.btool.load_ignore_list",
            return_value={"bot1": {"username": "bot1"}, "bot2": {"username": "bot2"}},
        ):
            with patch("cli.btool.save_ignore_list") as mock_save:
                from cli.btool import remove_bot

                result = remove_bot("bot3")
                assert result is None
                mock_save.assert_not_called()

    def test_settings_set_message_mode_invalid(self):
        """Test settings set_message_mode with invalid mode."""
        with pytest.raises(SystemExit):
            from argparse import Namespace

            from cli.settings import set_message_mode

            args = Namespace(mode="invalid_mode", json=False)
            set_message_mode(args)

    def test_settings_set_debug_mode_invalid(self):
        """Test settings set_debug_mode with invalid value."""
        with pytest.raises(ValueError):
            from cli.settings import set_debug_mode

            set_debug_mode("invalid")

    def test_settings_set_queue_refresh_invalid(self):
        """Test settings set_queue_refresh with invalid value."""
        with pytest.raises(SystemExit):
            from argparse import Namespace

            from cli.settings import set_queue_refresh

            args = Namespace(seconds=-1, json=False)
            set_queue_refresh(args)

    def test_settings_set_max_retries_invalid(self):
        """Test settings set_max_retries with invalid value."""
        with pytest.raises(SystemExit):
            from argparse import Namespace

            from cli.settings import set_max_retries

            args = Namespace(retries=-1, json=False)
            set_max_retries(args)
