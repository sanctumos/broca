"""
Tests for CLI settings management tool (settings.py).
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from cli.settings import (
    get_settings,
    load_settings,
    main,
    print_output,
    reload_settings,
    save_settings,
    set_debug_mode,
    set_max_retries,
    set_message_mode,
    set_queue_refresh,
)


class TestSettingsFunctions:
    """Test settings.py functions."""

    def test_load_settings_file_exists(self):
        """Test loading settings when file exists."""
        mock_settings = {
            "debug_mode": True,
            "queue_refresh": 10,
            "max_retries": 5,
            "message_mode": "test",
        }

        with patch("cli.settings.SETTINGS_PATH") as mock_path, patch(
            "pathlib.Path.exists", return_value=True
        ), patch("builtins.open", mock_open(read_data=json.dumps(mock_settings))):
            mock_path.return_value = Path("test.json")
            result = load_settings()

            assert result == mock_settings

    def test_load_settings_file_not_exists(self):
        """Test loading settings when file doesn't exist."""
        default_settings = {
            "debug_mode": False,
            "queue_refresh": 5,
            "max_retries": 3,
            "message_mode": "live",
        }

        with patch("cli.settings.SETTINGS_PATH") as mock_path, patch(
            "pathlib.Path.exists", return_value=False
        ):
            mock_path.return_value = Path("test.json")
            result = load_settings()

            assert result == default_settings

    def test_save_settings(self):
        """Test saving settings."""
        mock_settings = {
            "debug_mode": True,
            "queue_refresh": 10,
            "max_retries": 5,
            "message_mode": "test",
        }

        with patch("cli.settings.SETTINGS_PATH") as mock_path, patch(
            "builtins.open", mock_open()
        ) as mock_file:
            mock_path.return_value = Path("test.json")
            save_settings(mock_settings)

            mock_file.assert_called_once_with(Path("test.json"), "w")
            mock_file.return_value.write.assert_called_once_with(
                json.dumps(mock_settings, indent=4)
            )

    def test_print_output_json(self):
        """Test printing output in JSON format."""
        mock_data = {"key": "value"}

        with patch("builtins.print") as mock_print:
            print_output(mock_data, json_output=True)
            mock_print.assert_called_once_with(json.dumps(mock_data, indent=2))

    def test_print_output_human_readable(self):
        """Test printing output in human-readable format."""
        mock_data = {"key": "value"}

        with patch("builtins.print") as mock_print:
            print_output(mock_data, json_output=False)
            mock_print.assert_called_once()

    def test_get_settings(self):
        """Test getting all settings."""
        mock_settings = {
            "debug_mode": True,
            "queue_refresh": 10,
            "max_retries": 5,
            "message_mode": "test",
        }

        args = MagicMock()
        args.json = False

        with patch("cli.settings.load_settings", return_value=mock_settings), patch(
            "cli.settings.print_output"
        ) as mock_print:
            get_settings(args)

            mock_print.assert_called_once_with(mock_settings, False)

    def test_set_message_mode(self):
        """Test setting message mode."""
        mock_settings = {
            "debug_mode": False,
            "queue_refresh": 5,
            "max_retries": 3,
            "message_mode": "live",
        }

        args = MagicMock()
        args.mode = "test"
        args.json = False

        with patch("cli.settings.load_settings", return_value=mock_settings), patch(
            "cli.settings.save_settings"
        ) as mock_save, patch("cli.settings.print_output") as mock_print:
            set_message_mode(args)

            expected_settings = {
                "debug_mode": False,
                "queue_refresh": 5,
                "max_retries": 3,
                "message_mode": "test",
            }
            mock_save.assert_called_once_with(expected_settings)
            mock_print.assert_called_once_with("test", False)

    def test_set_debug_mode_true(self):
        """Test setting debug mode to true."""
        mock_settings = {
            "debug_mode": False,
            "queue_refresh": 5,
            "max_retries": 3,
            "message_mode": "live",
        }

        args = MagicMock()
        args.enabled = True
        args.json = False

        with patch("cli.settings.load_settings", return_value=mock_settings), patch(
            "cli.settings.save_settings"
        ) as mock_save, patch("cli.settings.print_output") as mock_print:
            set_debug_mode(args)

            expected_settings = {
                "debug_mode": True,
                "queue_refresh": 5,
                "max_retries": 3,
                "message_mode": "live",
            }
            mock_save.assert_called_once_with(expected_settings)
            mock_print.assert_called_once_with(True, False)

    def test_set_debug_mode_false(self):
        """Test setting debug mode to false."""
        mock_settings = {
            "debug_mode": True,
            "queue_refresh": 5,
            "max_retries": 3,
            "message_mode": "live",
        }

        args = MagicMock()
        args.enabled = False
        args.json = False

        with patch("cli.settings.load_settings", return_value=mock_settings), patch(
            "cli.settings.save_settings"
        ) as mock_save, patch("cli.settings.print_output") as mock_print:
            set_debug_mode(args)

            expected_settings = {
                "debug_mode": False,
                "queue_refresh": 5,
                "max_retries": 3,
                "message_mode": "live",
            }
            mock_save.assert_called_once_with(expected_settings)
            mock_print.assert_called_once_with(False, False)

    def test_set_queue_refresh(self):
        """Test setting queue refresh interval."""
        mock_settings = {
            "debug_mode": False,
            "queue_refresh": 5,
            "max_retries": 3,
            "message_mode": "live",
        }

        args = MagicMock()
        args.seconds = 10
        args.json = False

        with patch("cli.settings.load_settings", return_value=mock_settings), patch(
            "cli.settings.save_settings"
        ) as mock_save, patch("cli.settings.print_output") as mock_print:
            set_queue_refresh(args)

            expected_settings = {
                "debug_mode": False,
                "queue_refresh": 10,
                "max_retries": 3,
                "message_mode": "live",
            }
            mock_save.assert_called_once_with(expected_settings)
            mock_print.assert_called_once_with(10, False)

    def test_set_max_retries(self):
        """Test setting max retries."""
        mock_settings = {
            "debug_mode": False,
            "queue_refresh": 5,
            "max_retries": 3,
            "message_mode": "live",
        }

        args = MagicMock()
        args.count = 5
        args.json = False

        with patch("cli.settings.load_settings", return_value=mock_settings), patch(
            "cli.settings.save_settings"
        ) as mock_save, patch("cli.settings.print_output") as mock_print:
            set_max_retries(args)

            expected_settings = {
                "debug_mode": False,
                "queue_refresh": 5,
                "max_retries": 5,
                "message_mode": "live",
            }
            mock_save.assert_called_once_with(expected_settings)
            mock_print.assert_called_once_with(5, False)

    def test_reload_settings(self):
        """Test reloading settings."""
        args = MagicMock()
        args.json = False

        with patch("cli.settings.load_settings") as mock_load, patch(
            "cli.settings.print_output"
        ) as mock_print:
            mock_load.return_value = {"test": "value"}
            reload_settings(args)

            mock_print.assert_called_once_with({"test": "value"}, False)

    def test_main_get_command(self):
        """Test main function with get command."""
        with patch("cli.settings.get_settings") as mock_get, patch(
            "sys.argv", ["settings.py", "get"]
        ):
            main()
            mock_get.assert_called_once()

    def test_main_set_message_mode_command(self):
        """Test main function with set message-mode command."""
        with patch("cli.settings.set_message_mode") as mock_set, patch(
            "sys.argv", ["settings.py", "set", "message-mode", "test"]
        ):
            main()
            mock_set.assert_called_once()

    def test_main_set_debug_mode_command(self):
        """Test main function with set debug-mode command."""
        with patch("cli.settings.set_debug_mode") as mock_set, patch(
            "sys.argv", ["settings.py", "set", "debug-mode", "true"]
        ):
            main()
            mock_set.assert_called_once()

    def test_main_set_queue_refresh_command(self):
        """Test main function with set queue-refresh command."""
        with patch("cli.settings.set_queue_refresh") as mock_set, patch(
            "sys.argv", ["settings.py", "set", "queue-refresh", "10"]
        ):
            main()
            mock_set.assert_called_once()

    def test_main_set_max_retries_command(self):
        """Test main function with set max-retries command."""
        with patch("cli.settings.set_max_retries") as mock_set, patch(
            "sys.argv", ["settings.py", "set", "max-retries", "5"]
        ):
            main()
            mock_set.assert_called_once()

    def test_main_reload_command(self):
        """Test main function with reload command."""
        with patch("cli.settings.reload_settings") as mock_reload, patch(
            "sys.argv", ["settings.py", "reload"]
        ):
            main()
            mock_reload.assert_called_once()

    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        with patch("sys.argv", ["settings.py", "invalid"]), patch(
            "sys.exit"
        ) as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)

    def test_main_insufficient_args(self):
        """Test main function with insufficient arguments."""
        with patch("sys.argv", ["settings.py"]), patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)
