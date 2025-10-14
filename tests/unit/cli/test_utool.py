"""
Tests for CLI user management tool (utool.py).
"""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cli.utool import (
    get_user,
    list_users,
    main,
    print_json,
    print_users,
    update_user_status,
)


class TestUtoolFunctions:
    """Test utool.py functions."""

    @pytest.mark.asyncio
    async def test_list_users_json_output(self):
        """Test listing users with JSON output."""
        mock_users = [
            {"id": "1", "display_name": "User1", "username": "user1"},
            {"id": "2", "display_name": "User2", "username": "user2"},
        ]

        args = MagicMock()
        args.json = True

        with patch(
            "cli.utool.get_all_users", new_callable=AsyncMock
        ) as mock_get, patch("cli.utool.print_json") as mock_print_json:
            mock_get.return_value = mock_users
            await list_users(args)

            mock_print_json.assert_called_once_with(mock_users)

    @pytest.mark.asyncio
    async def test_list_users_table_output(self):
        """Test listing users with table output."""
        mock_users = [
            {"id": "1", "display_name": "User1", "username": "user1"},
            {"id": "2", "display_name": "User2", "username": "user2"},
        ]

        args = MagicMock()
        args.json = False

        with patch(
            "cli.utool.get_all_users", new_callable=AsyncMock
        ) as mock_get, patch("cli.utool.print_users") as mock_print_table:
            mock_get.return_value = mock_users
            await list_users(args)

            mock_print_table.assert_called_once_with(mock_users)

    @pytest.mark.asyncio
    async def test_get_user_found(self):
        """Test getting user by ID when user exists."""
        mock_user_details = ("User1", "user1")

        args = MagicMock()
        args.id = "123"
        args.json = False

        with patch(
            "cli.utool.get_user_details", new_callable=AsyncMock
        ) as mock_get, patch("cli.utool.print_users") as mock_print_users:
            mock_get.return_value = mock_user_details
            await get_user(args)

            mock_get.assert_called_once_with("123")
            expected_user = {"id": "123", "display_name": "User1", "username": "user1"}
            mock_print_users.assert_called_once_with([expected_user])

    @pytest.mark.asyncio
    async def test_get_user_not_found(self):
        """Test getting user by ID when user doesn't exist."""
        args = MagicMock()
        args.id = "123"

        with patch(
            "cli.utool.get_user_details", new_callable=AsyncMock
        ) as mock_get, patch("builtins.print") as mock_print, patch(
            "sys.exit"
        ) as mock_exit:
            mock_get.return_value = None
            await get_user(args)

            mock_get.assert_called_once_with("123")
            mock_print.assert_called_once_with(
                "User with ID 123 not found", file=sys.stderr
            )
            mock_exit.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_user_json_output(self):
        """Test getting user by ID with JSON output."""
        mock_user_details = ("User1", "user1")

        args = MagicMock()
        args.id = "123"
        args.json = True

        with patch(
            "cli.utool.get_user_details", new_callable=AsyncMock
        ) as mock_get, patch("cli.utool.print_json") as mock_print_json:
            mock_get.return_value = mock_user_details
            await get_user(args)

            expected_user = {"id": "123", "display_name": "User1", "username": "user1"}
            mock_print_json.assert_called_once_with([expected_user])

    @pytest.mark.asyncio
    async def test_update_user_status_active(self):
        """Test updating user status to active."""
        mock_user = {"id": "123", "is_active": True}

        args = MagicMock()
        args.id = "123"
        args.status = "active"

        with patch(
            "cli.utool.update_letta_user", new_callable=AsyncMock
        ) as mock_update, patch("builtins.print") as mock_print:
            mock_update.return_value = mock_user
            await update_user_status(args)

            mock_update.assert_called_once_with("123", {"is_active": True})
            mock_print.assert_called_once_with("User 123 status updated to active")

    @pytest.mark.asyncio
    async def test_update_user_status_inactive(self):
        """Test updating user status to inactive."""
        mock_user = {"id": "123", "is_active": False}

        args = MagicMock()
        args.id = "123"
        args.status = "inactive"

        with patch(
            "cli.utool.update_letta_user", new_callable=AsyncMock
        ) as mock_update, patch("builtins.print") as mock_print:
            mock_update.return_value = mock_user
            await update_user_status(args)

            mock_update.assert_called_once_with("123", {"is_active": False})
            mock_print.assert_called_once_with("User 123 status updated to inactive")

    @pytest.mark.asyncio
    async def test_update_user_status_not_found(self):
        """Test updating user status when user doesn't exist."""
        args = MagicMock()
        args.id = "123"
        args.status = "active"

        with patch(
            "cli.utool.update_letta_user", new_callable=AsyncMock
        ) as mock_update, patch("builtins.print") as mock_print, patch(
            "sys.exit"
        ) as mock_exit:
            mock_update.return_value = None
            await update_user_status(args)

            mock_update.assert_called_once_with("123", {"is_active": True})
            mock_print.assert_called_once_with(
                "User with ID 123 not found", file=sys.stderr
            )
            mock_exit.assert_called_once_with(1)

    def test_print_json(self):
        """Test printing JSON output."""
        mock_users = [
            {"id": "1", "display_name": "User1", "username": "user1"},
            {"id": "2", "display_name": "User2", "username": "user2"},
        ]

        with patch("builtins.print") as mock_print:
            print_json(mock_users)
            mock_print.assert_called_once()

    def test_print_users(self):
        """Test printing users in table format."""
        mock_users = [
            {"id": "1", "display_name": "User1", "username": "user1"},
            {"id": "2", "display_name": "User2", "username": "user2"},
        ]

        with patch("builtins.print") as mock_print:
            print_users(mock_users)
            # Should print header and users
            assert mock_print.call_count >= 2

    def test_print_users_empty(self):
        """Test printing empty users list."""
        with patch("builtins.print") as mock_print:
            print_users([])
            mock_print.assert_called_once_with("No users found")

    def test_main_list_command(self):
        """Test main function with list command."""
        with patch("sys.argv", ["utool", "list"]), patch(
            "cli.utool.list_users", new_callable=AsyncMock
        ), patch("asyncio.run") as mock_run:
            main()
            mock_run.assert_called_once()

    def test_main_get_command(self):
        """Test main function with get command."""
        with patch("sys.argv", ["utool", "get", "123"]), patch(
            "cli.utool.get_user", new_callable=AsyncMock
        ), patch("asyncio.run") as mock_run:
            main()
            mock_run.assert_called_once()

    def test_main_update_command(self):
        """Test main function with update command."""
        with patch("sys.argv", ["utool", "update", "123", "active"]), patch(
            "cli.utool.update_user_status", new_callable=AsyncMock
        ), patch("asyncio.run") as mock_run:
            main()
            mock_run.assert_called_once()

    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        with patch("sys.argv", ["utool.py", "invalid"]), patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_with(
                2
            )  # argparse calls sys.exit(2) for invalid arguments
