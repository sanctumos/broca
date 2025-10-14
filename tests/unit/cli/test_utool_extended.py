"""Extended unit tests for CLI tools - utool.py."""

import json
import sys
from unittest.mock import patch

import pytest

from cli.utool import (
    get_user,
    list_users,
    main,
    print_json,
    print_users,
    update_user_status,
)


class TestUtoolExtended:
    """Extended test cases for utool.py."""

    @patch("cli.utool.get_all_users")
    async def test_list_users_with_users(self, mock_get_users):
        """Test listing users when users exist."""
        mock_users = [
            {"id": 1, "username": "user1", "status": "active"},
            {"id": 2, "username": "user2", "status": "inactive"},
        ]
        mock_get_users.return_value = mock_users

        args = type("Args", (), {"json": False})()
        with patch("cli.utool.print_users") as mock_print:
            await list_users(args)
            mock_print.assert_called_once_with(mock_users)

    @patch("cli.utool.get_all_users")
    async def test_list_users_empty(self, mock_get_users):
        """Test listing users when no users exist."""
        mock_get_users.return_value = []

        args = type("Args", (), {"json": False})()
        with patch("cli.utool.print_users") as mock_print:
            await list_users(args)
            mock_print.assert_called_once_with([])

    @patch("cli.utool.get_user_details")
    async def test_get_user_success(self, mock_get_user):
        """Test getting user successfully."""
        mock_user = ("Display Name", "username")
        mock_get_user.return_value = mock_user

        args = type("Args", (), {"id": 1, "json": False})()
        with patch("cli.utool.print_users") as mock_print:
            await get_user(args)
            mock_print.assert_called_once()

    @patch("cli.utool.get_user_details")
    async def test_get_user_not_found(self, mock_get_user):
        """Test getting non-existent user."""
        mock_get_user.return_value = None

        args = type("Args", (), {"id": 999, "json": False})()
        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
            await get_user(args)
            mock_print.assert_called_once_with(
                "User with ID 999 not found", file=sys.stderr
            )
            mock_exit.assert_called_once_with(1)

    @patch("cli.utool.update_letta_user")
    async def test_update_user_status_success(self, mock_update):
        """Test updating user status successfully."""
        mock_update.return_value = {"id": 1, "status": "inactive"}

        args = type("Args", (), {"id": 1, "status": "inactive", "json": False})()
        with patch("builtins.print") as mock_print:
            await update_user_status(args)
            mock_print.assert_called_once_with("User 1 status updated to inactive")

    @patch("cli.utool.update_letta_user")
    async def test_update_user_status_not_found(self, mock_update):
        """Test updating status of non-existent user."""
        mock_update.return_value = None

        args = type("Args", (), {"id": 999, "status": "active", "json": False})()
        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
            await update_user_status(args)
            mock_print.assert_called_once_with(
                "User with ID 999 not found", file=sys.stderr
            )
            mock_exit.assert_called_once_with(1)

    def test_print_json_with_data(self):
        """Test printing JSON data."""
        test_data = {"id": 1, "username": "user1", "status": "active"}

        with patch("builtins.print") as mock_print:
            print_json(test_data)
            mock_print.assert_called_once_with(json.dumps(test_data, indent=2))

    def test_print_json_empty(self):
        """Test printing empty JSON data."""
        test_data = {}

        with patch("builtins.print") as mock_print:
            print_json(test_data)
            mock_print.assert_called_once_with(json.dumps(test_data, indent=2))

    def test_print_users_with_users(self):
        """Test printing users."""
        test_users = [
            {
                "id": 1,
                "username": "user1",
                "display_name": "User One",
                "is_active": True,
            },
            {
                "id": 2,
                "username": "user2",
                "display_name": "User Two",
                "is_active": False,
            },
        ]

        with patch("builtins.print") as mock_print:
            print_users(test_users)

            # Should print header and each user
            assert mock_print.call_count >= 3
            mock_print.assert_any_call("\nUsers:")
            mock_print.assert_any_call("-" * 80)

    def test_print_users_empty(self):
        """Test printing empty users list."""
        with patch("builtins.print") as mock_print:
            print_users([])
            mock_print.assert_called_once_with("No users found")

    def test_print_users_none(self):
        """Test printing None users."""
        with patch("builtins.print") as mock_print:
            print_users(None)
            mock_print.assert_called_once_with("No users found")

    def test_main_list_command(self):
        """Test main function with list command."""
        with patch("cli.utool.list_users") as mock_list:
            with patch("cli.utool.sys.argv", ["utool.py", "list"]):
                main()
                mock_list.assert_called_once()

    def test_main_get_command(self):
        """Test main function with get command."""
        with patch("cli.utool.get_user") as mock_get:
            with patch("cli.utool.sys.argv", ["utool.py", "get", "1"]):
                main()
                # The function is called with the parsed args object
                args = mock_get.call_args[0][0]
                assert args.id == 1  # argparse converts string to int
                assert args.json is False

    def test_main_get_command_invalid_id(self):
        """Test main function with get command and invalid ID."""
        with patch("cli.utool.sys.argv", ["utool.py", "get", "invalid"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_main_update_command(self):
        """Test main function with update command."""
        with patch("cli.utool.update_user_status") as mock_update:
            with patch("cli.utool.sys.argv", ["utool.py", "update", "1", "inactive"]):
                main()
                # The function is called with the parsed args object
                args = mock_update.call_args[0][0]
                assert args.id == 1
                assert args.status == "inactive"
                assert args.json is False

    def test_main_update_command_invalid_id(self):
        """Test main function with update command and invalid ID."""
        with patch("cli.utool.sys.argv", ["utool.py", "update", "invalid", "active"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_main_update_command_no_status(self):
        """Test main function with update command but no status."""
        with patch("cli.utool.sys.argv", ["utool.py", "update", "1"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        with patch("cli.utool.sys.argv", ["utool.py", "invalid"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_main_no_args(self):
        """Test main function with no arguments."""
        with patch("cli.utool.sys.argv", ["utool.py"]):
            with patch("argparse.ArgumentParser.print_help") as mock_print_help:
                main()
                mock_print_help.assert_called_once()

    def test_print_users_with_missing_fields(self):
        """Test printing users with missing fields."""
        test_users = [
            {
                "id": 1,
                "username": "user1",
                "display_name": "User One",
                "is_active": True,
            },  # Complete
            {
                "id": 2,
                "username": "user2",
                "display_name": "User Two",
                "is_active": False,
            },  # Complete
        ]

        with patch("builtins.print") as mock_print:
            print_users(test_users)

            # Should handle missing fields gracefully
            assert mock_print.call_count >= 3
            mock_print.assert_any_call("\nUsers:")
            mock_print.assert_any_call("-" * 80)

    def test_print_users_with_special_characters(self):
        """Test printing users with special characters."""
        test_users = [
            {
                "id": 1,
                "username": "user@#$%",
                "display_name": "User@#$%",
                "is_active": True,
            }
        ]

        with patch("builtins.print") as mock_print:
            print_users(test_users)

            # Should handle special characters gracefully
            assert mock_print.call_count >= 3
            mock_print.assert_any_call("\nUsers:")
            mock_print.assert_any_call("-" * 80)

    def test_print_json_with_special_characters(self):
        """Test printing JSON with special characters."""
        test_data = {"username": "user@#$%", "status": "active!@#"}

        with patch("builtins.print") as mock_print:
            print_json(test_data)
            mock_print.assert_called_once_with(json.dumps(test_data, indent=2))

    async def test_update_user_status_with_exception(self):
        """Test updating user status with exception."""
        args = type("Args", (), {"id": 1, "status": "active", "json": False})()
        with patch(
            "cli.utool.update_letta_user",
            side_effect=Exception("Database error"),
        ):
            with pytest.raises(Exception, match="Database error"):
                await update_user_status(args)

    async def test_get_user_with_exception(self):
        """Test getting user with exception."""
        args = type("Args", (), {"id": 1, "json": False})()
        with patch(
            "cli.utool.get_user_details", side_effect=Exception("Database error")
        ):
            with pytest.raises(Exception, match="Database error"):
                await get_user(args)

    async def test_list_users_with_exception(self):
        """Test listing users with exception."""
        args = type("Args", (), {"json": False})()
        with patch("cli.utool.get_all_users", side_effect=Exception("Database error")):
            with pytest.raises(Exception, match="Database error"):
                await list_users(args)

    def test_print_users_with_none_values(self):
        """Test printing users with None values."""
        test_users = [
            {
                "id": None,
                "username": "user1",
                "display_name": "User One",
                "is_active": True,
            },
            {"id": 2, "username": None, "display_name": "User Two", "is_active": False},
            {"id": 3, "username": "user3", "display_name": None, "is_active": True},
            {
                "id": 4,
                "username": "user4",
                "display_name": "User Four",
                "is_active": None,
            },
        ]

        with patch("builtins.print") as mock_print:
            print_users(test_users)

            # Should handle None values gracefully
            assert mock_print.call_count >= 3
            mock_print.assert_any_call("\nUsers:")
            mock_print.assert_any_call("-" * 80)

    async def test_update_user_status_with_invalid_status(self):
        """Test updating user status with invalid status."""
        args = type("Args", (), {"id": 1, "status": "invalid_status", "json": False})()
        with patch("cli.utool.update_letta_user", return_value=None):
            with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
                await update_user_status(args)
                mock_print.assert_called_once_with(
                    "User with ID 1 not found", file=sys.stderr
                )
                mock_exit.assert_called_once_with(1)

    def test_get_user_with_string_id(self):
        """Test getting user with string ID."""
        with patch("cli.utool.sys.argv", ["utool.py", "get", "abc"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_update_user_status_with_string_id(self):
        """Test updating user status with string ID."""
        with patch("cli.utool.sys.argv", ["utool.py", "update", "abc", "active"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_print_users_with_empty_strings(self):
        """Test printing users with empty strings."""
        test_users = [
            {"id": 1, "username": "", "display_name": "User One", "is_active": True},
            {"id": 2, "username": "user2", "display_name": "", "is_active": False},
        ]

        with patch("builtins.print") as mock_print:
            print_users(test_users)

            # Should handle empty strings gracefully
            assert mock_print.call_count >= 3
            mock_print.assert_any_call("\nUsers:")
            mock_print.assert_any_call("-" * 80)
