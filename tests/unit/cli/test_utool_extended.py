"""Extended unit tests for CLI tools - utool.py."""

import json
from unittest.mock import patch

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
    def test_list_users_with_users(self, mock_get_users):
        """Test listing users when users exist."""
        mock_users = [
            {"id": 1, "username": "user1", "status": "active"},
            {"id": 2, "username": "user2", "status": "inactive"},
        ]
        mock_get_users.return_value = mock_users

        with patch("cli.utool.print_users") as mock_print:
            list_users()
            mock_print.assert_called_once_with(mock_users)

    @patch("cli.utool.get_all_users")
    def test_list_users_empty(self, mock_get_users):
        """Test listing users when no users exist."""
        mock_get_users.return_value = []

        with patch("cli.utool.print_users") as mock_print:
            list_users()
            mock_print.assert_called_once_with([])

    @patch("cli.utool.get_user_by_id")
    def test_get_user_success(self, mock_get_user):
        """Test getting user successfully."""
        mock_user = {"id": 1, "username": "user1", "status": "active"}
        mock_get_user.return_value = mock_user

        with patch("cli.utool.print_json") as mock_print:
            get_user(1)
            mock_print.assert_called_once_with(mock_user)

    @patch("cli.utool.get_user_by_id")
    def test_get_user_not_found(self, mock_get_user):
        """Test getting non-existent user."""
        mock_get_user.return_value = None

        with patch("builtins.print") as mock_print:
            get_user(999)
            mock_print.assert_called_once_with("User 999 not found")

    @patch("cli.utool.update_user_status_by_id")
    def test_update_user_status_success(self, mock_update):
        """Test updating user status successfully."""
        mock_update.return_value = True

        with patch("builtins.print") as mock_print:
            update_user_status(1, "inactive")
            mock_print.assert_called_once_with("Updated user 1 status to inactive")

    @patch("cli.utool.update_user_status_by_id")
    def test_update_user_status_not_found(self, mock_update):
        """Test updating status of non-existent user."""
        mock_update.return_value = False

        with patch("builtins.print") as mock_print:
            update_user_status(999, "active")
            mock_print.assert_called_once_with("User 999 not found")

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
            {"id": 1, "username": "user1", "status": "active"},
            {"id": 2, "username": "user2", "status": "inactive"},
        ]

        with patch("builtins.print") as mock_print:
            print_users(test_users)

            # Should print header and each user
            assert mock_print.call_count == 3
            mock_print.assert_any_call("Users:")
            mock_print.assert_any_call("ID: 1, Username: user1, Status: active")
            mock_print.assert_any_call("ID: 2, Username: user2, Status: inactive")

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
                mock_get.assert_called_once_with(1)

    def test_main_get_command_invalid_id(self):
        """Test main function with get command and invalid ID."""
        with patch("cli.utool.sys.argv", ["utool.py", "get", "invalid"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_main_update_command(self):
        """Test main function with update command."""
        with patch("cli.utool.update_user_status") as mock_update:
            with patch("cli.utool.sys.argv", ["utool.py", "update", "1", "inactive"]):
                main()
                mock_update.assert_called_once_with(1, "inactive")

    def test_main_update_command_invalid_id(self):
        """Test main function with update command and invalid ID."""
        with patch("cli.utool.sys.argv", ["utool.py", "update", "invalid", "active"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_main_update_command_no_status(self):
        """Test main function with update command but no status."""
        with patch("cli.utool.sys.argv", ["utool.py", "update", "1"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        with patch("cli.utool.sys.argv", ["utool.py", "invalid"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_main_no_args(self):
        """Test main function with no arguments."""
        with patch("cli.utool.sys.argv", ["utool.py"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_print_users_with_missing_fields(self):
        """Test printing users with missing fields."""
        test_users = [
            {"id": 1, "username": "user1"},  # Missing status
            {"id": 2, "status": "active"},  # Missing username
        ]

        with patch("builtins.print") as mock_print:
            print_users(test_users)

            # Should handle missing fields gracefully
            assert mock_print.call_count == 3
            mock_print.assert_any_call("Users:")

    def test_print_users_with_special_characters(self):
        """Test printing users with special characters."""
        test_users = [{"id": 1, "username": "user@#$%", "status": "active@#$%"}]

        with patch("builtins.print") as mock_print:
            print_users(test_users)

            # Should print special characters correctly
            assert mock_print.call_count == 2
            mock_print.assert_any_call("Users:")
            mock_print.assert_any_call("ID: 1, Username: user@#$%, Status: active@#$%")

    def test_print_json_with_special_characters(self):
        """Test printing JSON with special characters."""
        test_data = {"username": "user@#$%", "status": "active!@#"}

        with patch("builtins.print") as mock_print:
            print_json(test_data)
            mock_print.assert_called_once_with(json.dumps(test_data, indent=2))

    def test_update_user_status_with_exception(self):
        """Test updating user status with exception."""
        with patch(
            "cli.utool.update_user_status_by_id",
            side_effect=Exception("Database error"),
        ):
            with patch("builtins.print") as mock_print:
                update_user_status(1, "active")
                mock_print.assert_called()

    def test_get_user_with_exception(self):
        """Test getting user with exception."""
        with patch("cli.utool.get_user_by_id", side_effect=Exception("Database error")):
            with patch("builtins.print") as mock_print:
                get_user(1)
                mock_print.assert_called()

    def test_list_users_with_exception(self):
        """Test listing users with exception."""
        with patch("cli.utool.get_all_users", side_effect=Exception("Database error")):
            with patch("builtins.print") as mock_print:
                list_users()
                mock_print.assert_called()

    def test_print_users_with_none_values(self):
        """Test printing users with None values."""
        test_users = [
            {"id": None, "username": "user1", "status": "active"},
            {"id": 2, "username": None, "status": "inactive"},
            {"id": 3, "username": "user3", "status": None},
        ]

        with patch("builtins.print") as mock_print:
            print_users(test_users)

            # Should handle None values gracefully
            assert mock_print.call_count == 4
            mock_print.assert_any_call("Users:")

    def test_update_user_status_with_invalid_status(self):
        """Test updating user status with invalid status."""
        with patch("cli.utool.update_user_status_by_id", return_value=False):
            with patch("builtins.print") as mock_print:
                update_user_status(1, "invalid_status")
                mock_print.assert_called_once_with("User 1 not found")

    def test_get_user_with_string_id(self):
        """Test getting user with string ID."""
        with patch("cli.utool.sys.argv", ["utool.py", "get", "abc"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_update_user_status_with_string_id(self):
        """Test updating user status with string ID."""
        with patch("cli.utool.sys.argv", ["utool.py", "update", "abc", "active"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called()

    def test_print_users_with_empty_strings(self):
        """Test printing users with empty strings."""
        test_users = [
            {"id": 1, "username": "", "status": "active"},
            {"id": 2, "username": "user2", "status": ""},
        ]

        with patch("builtins.print") as mock_print:
            print_users(test_users)

            # Should handle empty strings gracefully
            assert mock_print.call_count == 3
            mock_print.assert_any_call("Users:")
            mock_print.assert_any_call("ID: 1, Username: , Status: active")
            mock_print.assert_any_call("ID: 2, Username: user2, Status: ")
