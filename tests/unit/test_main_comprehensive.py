"""Comprehensive tests for main.py application."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from main import Application, create_default_settings, main


class TestMainApplicationComprehensive:
    """Comprehensive tests for main.py application."""

    def test_create_default_settings_file_exists(self):
        """Test create_default_settings when file already exists."""
        with patch("pathlib.Path.exists", return_value=True):
            create_default_settings()
            # Should not create file if it exists

    def test_create_default_settings_file_not_exists(self):
        """Test create_default_settings when file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False), patch(
            "builtins.open", create=True
        ) as mock_open, patch("json.dump") as mock_json_dump:
            create_default_settings()
            mock_open.assert_called_once()
            mock_json_dump.assert_called_once()

    def test_application_init(self):
        """Test Application initialization."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()
            assert app.plugin_manager is not None
            assert app.agent is not None
            assert app.queue_processor is not None
            assert app._settings_file == "settings.json"
            assert app._settings_mtime == 0

    def test_application_setup_signal_handlers(self):
        """Test signal handler setup."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch(
            "main.signal.signal"
        ) as mock_signal:
            Application()
            assert mock_signal.call_count == 2  # SIGTERM and SIGINT

    @pytest.mark.asyncio
    async def test_check_settings_no_change(self):
        """Test _check_settings when file hasn't changed."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()
            app._settings_mtime = 1000

            with patch("os.path.getmtime", return_value=1000):
                await app._check_settings()
                # Should not reload settings

    @pytest.mark.asyncio
    async def test_check_settings_file_changed(self):
        """Test _check_settings when file has changed."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()
            app._settings_mtime = 1000

            with patch("os.path.getmtime", return_value=2000), patch(
                "main.get_settings", return_value={"message_mode": "live"}
            ), patch("main.validate_settings"), patch.object(
                app.queue_processor, "set_message_mode"
            ), patch.object(
                app.plugin_manager, "update_message_mode", new_callable=AsyncMock
            ):
                await app._check_settings()
                assert app._settings_mtime == 2000

    @pytest.mark.asyncio
    async def test_check_settings_with_debug_mode(self):
        """Test _check_settings with debug mode change."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()
            app._settings_mtime = 1000

            with patch("os.path.getmtime", return_value=2000), patch(
                "main.get_settings", return_value={"debug_mode": True}
            ), patch("main.validate_settings"):
                await app._check_settings()
                assert app.agent.debug_mode is True

    @pytest.mark.asyncio
    async def test_check_settings_with_queue_refresh(self):
        """Test _check_settings with queue refresh change."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()
            app._settings_mtime = 1000

            with patch("os.path.getmtime", return_value=2000), patch(
                "main.get_settings", return_value={"queue_refresh": 10}
            ), patch("main.validate_settings"):
                await app._check_settings()
                assert app.queue_processor.refresh_interval == 10

    @pytest.mark.asyncio
    async def test_check_settings_with_max_retries(self):
        """Test _check_settings with max retries change."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()
            app._settings_mtime = 1000

            with patch("os.path.getmtime", return_value=2000), patch(
                "main.get_settings", return_value={"max_retries": 5}
            ), patch("main.validate_settings"):
                await app._check_settings()
                assert app.queue_processor.max_retries == 5

    @pytest.mark.asyncio
    async def test_check_settings_exception(self):
        """Test _check_settings with exception."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()

            with patch("os.path.getmtime", side_effect=OSError("File not found")):
                await app._check_settings()
                # Should not raise exception

    @pytest.mark.asyncio
    async def test_process_message(self):
        """Test _process_message."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()

            with patch.object(
                app.agent, "process_message", new_callable=AsyncMock
            ) as mock_process:
                mock_process.return_value = "Test response"
                result = await app._process_message("Test message")
                assert result == "Test response"
                mock_process.assert_called_once_with("Test message")

    @pytest.mark.asyncio
    async def test_on_message_processed(self):
        """Test _on_message_processed."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()

            await app._on_message_processed(123, "Test response")
            # Should not raise exception

    @pytest.mark.asyncio
    async def test_start_success(self):
        """Test successful application start."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()

            with patch("main.initialize_database", new_callable=AsyncMock), patch(
                "main.check_and_migrate_db", new_callable=AsyncMock
            ), patch.object(
                app.agent, "initialize", new_callable=AsyncMock, return_value=True
            ), patch(
                "main.get_settings",
                return_value={"plugins": {}, "message_mode": "live"},
            ), patch.object(
                app.plugin_manager, "discover_plugins", new_callable=AsyncMock
            ), patch.object(
                app.plugin_manager, "start", new_callable=AsyncMock
            ), patch.object(
                app.queue_processor, "set_message_mode"
            ), patch(
                "asyncio.create_task"
            ), patch.object(
                app._shutdown_event, "wait", new_callable=AsyncMock
            ), patch.object(
                app, "stop", new_callable=AsyncMock
            ):
                await app.start()

    @pytest.mark.asyncio
    async def test_start_agent_initialization_failed(self):
        """Test start when agent initialization fails."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()

            with patch("main.initialize_database", new_callable=AsyncMock), patch(
                "main.check_and_migrate_db", new_callable=AsyncMock
            ), patch.object(
                app.agent, "initialize", new_callable=AsyncMock, return_value=False
            ), patch.object(
                app, "stop", new_callable=AsyncMock
            ):
                await app.start()

    @pytest.mark.asyncio
    async def test_start_exception(self):
        """Test start with exception."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()

            with patch(
                "main.initialize_database", side_effect=Exception("Database error")
            ), patch.object(app, "stop", new_callable=AsyncMock):
                with pytest.raises(Exception, match="Database error"):
                    await app.start()

    @pytest.mark.asyncio
    async def test_monitor_settings_success(self):
        """Test _monitor_settings success."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()

            with patch.object(app, "_check_settings", new_callable=AsyncMock), patch(
                "asyncio.sleep", side_effect=asyncio.CancelledError
            ):
                with pytest.raises(asyncio.CancelledError):
                    await app._monitor_settings()

    @pytest.mark.asyncio
    async def test_monitor_settings_exception(self):
        """Test _monitor_settings with exception."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()

            with patch.object(
                app,
                "_check_settings",
                new_callable=AsyncMock,
                side_effect=Exception("Check error"),
            ), patch("asyncio.sleep", side_effect=asyncio.CancelledError):
                with pytest.raises(asyncio.CancelledError):
                    await app._monitor_settings()

    @pytest.mark.asyncio
    async def test_stop_success(self):
        """Test successful application stop."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()
            app._tasks = {MagicMock()}

            with patch.object(
                app.queue_processor, "stop", new_callable=AsyncMock
            ), patch.object(app.agent, "cleanup", new_callable=AsyncMock), patch.object(
                app.plugin_manager, "stop", new_callable=AsyncMock
            ), patch(
                "asyncio.gather", new_callable=AsyncMock
            ), patch(
                "os.remove"
            ):
                await app.stop()

    @pytest.mark.asyncio
    async def test_stop_exception(self):
        """Test stop with exception."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()

            with patch.object(
                app.queue_processor,
                "stop",
                new_callable=AsyncMock,
                side_effect=Exception("Stop error"),
            ), patch("os.remove"):
                await app.stop()
                # Should not raise exception

    @pytest.mark.asyncio
    async def test_stop_pid_file_removal_error(self):
        """Test stop with PID file removal error."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()

            with patch.object(
                app.queue_processor, "stop", new_callable=AsyncMock
            ), patch.object(app.agent, "cleanup", new_callable=AsyncMock), patch.object(
                app.plugin_manager, "stop", new_callable=AsyncMock
            ), patch(
                "os.remove", side_effect=OSError("File not found")
            ):
                await app.stop()
                # Should not raise exception

    def test_update_settings_message_mode(self):
        """Test update_settings with message mode."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()

            with patch.object(app.queue_processor, "set_message_mode") as mock_set_mode:
                app.update_settings({"message_mode": "echo"})
                mock_set_mode.assert_called_once_with("echo")

    def test_update_settings_debug_mode(self):
        """Test update_settings with debug mode."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()

            app.update_settings({"debug_mode": True})
            assert app.agent.debug_mode is True

    def test_update_settings_multiple(self):
        """Test update_settings with multiple settings."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()

            with patch.object(app.queue_processor, "set_message_mode") as mock_set_mode:
                app.update_settings({"message_mode": "live", "debug_mode": False})
                mock_set_mode.assert_called_once_with("live")
                assert app.agent.debug_mode is False

    def test_main_success(self):
        """Test main function success."""
        with patch("main.Application") as mock_app_class, patch(
            "asyncio.run"
        ) as mock_run:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app
            mock_run.return_value = None

            main()

            mock_app_class.assert_called_once()
            mock_run.assert_called_once_with(mock_app.start())

    def test_main_keyboard_interrupt(self):
        """Test main function with KeyboardInterrupt."""
        with patch("main.Application") as mock_app_class, patch(
            "asyncio.run", side_effect=KeyboardInterrupt
        ):
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app

            main()

    def test_main_exception(self):
        """Test main function with exception."""
        with patch("main.Application") as mock_app_class, patch(
            "asyncio.run", side_effect=Exception("Test error")
        ), patch("sys.exit") as mock_exit:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app

            main()

            mock_exit.assert_called_once_with(1)

    def test_main_final_cleanup(self):
        """Test main function final cleanup."""
        with patch("main.Application") as mock_app_class, patch(
            "asyncio.run"
        ) as mock_run:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app
            mock_run.side_effect = [None, None]  # start() and stop()

            main()

            assert mock_run.call_count == 2

    def test_main_final_cleanup_exception(self):
        """Test main function final cleanup with exception."""
        with patch("main.Application") as mock_app_class, patch(
            "asyncio.run"
        ) as mock_run, patch("sys.exit"):
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app
            mock_run.side_effect = [None, Exception("Cleanup error")]

            main()

            assert mock_run.call_count == 2

    @pytest.mark.asyncio
    async def test_application_lifecycle(self):
        """Test complete application lifecycle."""
        with patch("main.create_default_settings"), patch(
            "builtins.open", create=True
        ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
            app = Application()

            # Test start
            with patch("main.initialize_database", new_callable=AsyncMock), patch(
                "main.check_and_migrate_db", new_callable=AsyncMock
            ), patch.object(
                app.agent, "initialize", new_callable=AsyncMock, return_value=True
            ), patch(
                "main.get_settings",
                return_value={"plugins": {}, "message_mode": "live"},
            ), patch.object(
                app.plugin_manager, "discover_plugins", new_callable=AsyncMock
            ), patch.object(
                app.plugin_manager, "start", new_callable=AsyncMock
            ), patch.object(
                app.queue_processor, "set_message_mode"
            ), patch(
                "asyncio.create_task"
            ), patch.object(
                app._shutdown_event, "wait", new_callable=AsyncMock
            ), patch.object(
                app, "stop", new_callable=AsyncMock
            ):
                await app.start()

            # Test stop
            with patch.object(
                app.queue_processor, "stop", new_callable=AsyncMock
            ), patch.object(app.agent, "cleanup", new_callable=AsyncMock), patch.object(
                app.plugin_manager, "stop", new_callable=AsyncMock
            ), patch(
                "os.remove"
            ):
                await app.stop()

    def test_application_with_different_settings(self):
        """Test application with different settings configurations."""
        settings_configs = [
            {"message_mode": "echo", "debug_mode": False},
            {"message_mode": "live", "debug_mode": True},
            {"message_mode": "dry_run", "debug_mode": False, "queue_refresh": 10},
            {"max_retries": 5, "debug_mode": True},
        ]

        for settings in settings_configs:
            with patch("main.create_default_settings"), patch(
                "builtins.open", create=True
            ), patch("os.getpid", return_value=12345), patch("main.signal.signal"):
                app = Application()
                app.update_settings(settings)

                if "message_mode" in settings:
                    assert app.queue_processor.message_mode == settings["message_mode"]
                if "debug_mode" in settings:
                    assert app.agent.debug_mode == settings["debug_mode"]
