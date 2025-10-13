"""Extended unit tests for main.py."""

import asyncio
import json
import os
import signal
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from main import Application, create_default_settings


class TestMainExtended:
    """Extended test cases for main.py."""

    def test_create_default_settings(self):
        """Test creating default settings file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Settings file should not exist initially
                assert not Path("settings.json").exists()

                # Create default settings
                create_default_settings()

                # Settings file should now exist
                assert Path("settings.json").exists()

                # Verify content
                with open("settings.json") as f:
                    settings = json.load(f)

                expected_settings = {
                    "debug_mode": False,
                    "queue_refresh": 5,
                    "max_retries": 3,
                    "message_mode": "live",
                }
                assert settings == expected_settings

            finally:
                os.chdir(original_cwd)

    def test_create_default_settings_file_exists(self):
        """Test creating default settings when file already exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Create existing settings file
                existing_settings = {"custom": "value"}
                with open("settings.json", "w") as f:
                    json.dump(existing_settings, f)

                # Create default settings
                create_default_settings()

                # Original settings should be preserved
                with open("settings.json") as f:
                    settings = json.load(f)
                assert settings == existing_settings

            finally:
                os.chdir(original_cwd)

    @patch("main.PluginManager")
    @patch("main.AgentClient")
    @patch("main.QueueProcessor")
    @patch("main.create_default_settings")
    @patch("main.setup_logging")
    def test_application_initialization(
        self,
        mock_setup_logging,
        mock_create_settings,
        mock_queue_processor,
        mock_agent_client,
        mock_plugin_manager,
    ):
        """Test application initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Mock the components
                mock_plugin_manager.return_value = MagicMock()
                mock_agent_client.return_value = MagicMock()
                mock_queue_processor.return_value = MagicMock()

                # Create application
                app = Application()

                # Verify components were initialized
                mock_plugin_manager.assert_called_once()
                mock_agent_client.assert_called_once()
                mock_queue_processor.assert_called_once()
                mock_create_settings.assert_called_once()
                mock_setup_logging.assert_called_once()

                # Verify attributes
                assert app.plugin_manager is not None
                assert app.agent is not None
                assert app.queue_processor is not None
                assert app._settings_file == "settings.json"
                assert app._settings_mtime == 0
                assert not app._shutdown_event.is_set()
                assert len(app._tasks) == 0

                # Verify PID file was created
                assert Path("broca2.pid").exists()

            finally:
                os.chdir(original_cwd)

    @patch("main.PluginManager")
    @patch("main.AgentClient")
    @patch("main.QueueProcessor")
    @patch("main.create_default_settings")
    @patch("main.setup_logging")
    def test_application_signal_handlers(
        self,
        mock_setup_logging,
        mock_create_settings,
        mock_queue_processor,
        mock_agent_client,
        mock_plugin_manager,
    ):
        """Test signal handler setup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Mock the components
                mock_plugin_manager.return_value = MagicMock()
                mock_agent_client.return_value = MagicMock()
                mock_queue_processor.return_value = MagicMock()

                # Create application
                Application()

                # Verify signal handlers were set up
                assert signal.signal(signal.SIGTERM, signal.SIG_DFL) is not None
                assert signal.signal(signal.SIGINT, signal.SIG_DFL) is not None

            finally:
                os.chdir(original_cwd)

    @patch("main.PluginManager")
    @patch("main.AgentClient")
    @patch("main.QueueProcessor")
    @patch("main.create_default_settings")
    @patch("main.setup_logging")
    @patch("main.get_settings")
    @patch("main.validate_settings")
    @pytest.mark.asyncio
    async def test_check_settings_no_change(
        self,
        mock_validate_settings,
        mock_get_settings,
        mock_setup_logging,
        mock_create_settings,
        mock_queue_processor,
        mock_agent_client,
        mock_plugin_manager,
    ):
        """Test settings check when no changes detected."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Create settings file
                settings = {"message_mode": "live", "debug_mode": False}
                with open("settings.json", "w") as f:
                    json.dump(settings, f)

                # Mock the components
                mock_plugin_manager.return_value = MagicMock()
                mock_agent_client.return_value = MagicMock()
                mock_queue_processor.return_value = MagicMock()

                # Create application
                app = Application()

                # Set initial mtime
                app._settings_mtime = os.path.getmtime("settings.json")

                # Mock get_settings to return same settings
                mock_get_settings.return_value = settings

                # Check settings (should not trigger reload)
                await app._check_settings()

                # Verify validate_settings was not called
                mock_validate_settings.assert_not_called()

            finally:
                os.chdir(original_cwd)

    @patch("main.PluginManager")
    @patch("main.AgentClient")
    @patch("main.QueueProcessor")
    @patch("main.create_default_settings")
    @patch("main.setup_logging")
    @patch("main.get_settings")
    @patch("main.validate_settings")
    @pytest.mark.asyncio
    async def test_check_settings_with_changes(
        self,
        mock_validate_settings,
        mock_get_settings,
        mock_setup_logging,
        mock_create_settings,
        mock_queue_processor,
        mock_agent_client,
        mock_plugin_manager,
    ):
        """Test settings check when changes are detected."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Create initial settings file
                initial_settings = {"message_mode": "live", "debug_mode": False}
                with open("settings.json", "w") as f:
                    json.dump(initial_settings, f)

                # Mock the components
                mock_plugin_manager.return_value = MagicMock()
                mock_agent_client.return_value = MagicMock()
                mock_queue_processor.return_value = MagicMock()

                # Create application
                app = Application()

                # Set initial mtime to 0 to force reload
                app._settings_mtime = 0

                # Mock get_settings to return updated settings
                updated_settings = {
                    "message_mode": "echo",
                    "debug_mode": True,
                    "queue_refresh": 10,
                }
                mock_get_settings.return_value = updated_settings

                # Check settings (should trigger reload)
                await app._check_settings()

                # Verify validate_settings was called
                mock_validate_settings.assert_called_once_with(updated_settings)

                # Verify queue processor was updated
                app.queue_processor.set_message_mode.assert_called_once_with("echo")

                # Verify plugin manager was updated
                app.plugin_manager.update_message_mode.assert_called_once_with("echo")

            finally:
                os.chdir(original_cwd)

    @patch("main.PluginManager")
    @patch("main.AgentClient")
    @patch("main.QueueProcessor")
    @patch("main.create_default_settings")
    @patch("main.setup_logging")
    @pytest.mark.asyncio
    async def test_process_message(
        self,
        mock_setup_logging,
        mock_create_settings,
        mock_queue_processor,
        mock_agent_client,
        mock_plugin_manager,
    ):
        """Test message processing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Mock the components
                mock_agent = MagicMock()
                mock_agent.process_message = AsyncMock(
                    return_value="Processed response"
                )
                mock_agent_client.return_value = mock_agent

                mock_plugin_manager.return_value = MagicMock()
                mock_queue_processor.return_value = MagicMock()

                # Create application
                app = Application()

                # Process a message
                result = await app._process_message("Test message")

                # Verify agent processed the message
                mock_agent.process_message.assert_called_once_with("Test message")
                assert result == "Processed response"

            finally:
                os.chdir(original_cwd)

    @patch("main.PluginManager")
    @patch("main.AgentClient")
    @patch("main.QueueProcessor")
    @patch("main.create_default_settings")
    @patch("main.setup_logging")
    @patch("main.initialize_database")
    @patch("main.check_and_migrate_db")
    @pytest.mark.asyncio
    async def test_initialize_components(
        self,
        mock_migrate_db,
        mock_init_db,
        mock_setup_logging,
        mock_create_settings,
        mock_queue_processor,
        mock_agent_client,
        mock_plugin_manager,
    ):
        """Test component initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Mock the components
                mock_plugin_manager.return_value = MagicMock()
                mock_agent_client.return_value = MagicMock()
                mock_queue_processor.return_value = MagicMock()

                # Create application
                app = Application()

                # Initialize components
                await app._initialize_components()

                # Verify database operations were called
                mock_migrate_db.assert_called_once()
                mock_init_db.assert_called_once()

                # Verify agent was initialized
                app.agent.initialize.assert_called_once()

                # Verify plugins were discovered and started
                app.plugin_manager.discover_plugins.assert_called_once()
                app.plugin_manager.start.assert_called_once()

            finally:
                os.chdir(original_cwd)

    @patch("main.PluginManager")
    @patch("main.AgentClient")
    @patch("main.QueueProcessor")
    @patch("main.create_default_settings")
    @patch("main.setup_logging")
    @pytest.mark.asyncio
    async def test_cleanup_components(
        self,
        mock_setup_logging,
        mock_create_settings,
        mock_queue_processor,
        mock_agent_client,
        mock_plugin_manager,
    ):
        """Test component cleanup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Mock the components
                mock_plugin_manager.return_value = MagicMock()
                mock_agent_client.return_value = MagicMock()
                mock_queue_processor.return_value = MagicMock()

                # Create application
                app = Application()

                # Cleanup components
                await app._cleanup_components()

                # Verify components were cleaned up
                app.queue_processor.stop.assert_called_once()
                app.plugin_manager.stop.assert_called_once()
                app.agent.cleanup.assert_called_once()

            finally:
                os.chdir(original_cwd)

    @patch("main.PluginManager")
    @patch("main.AgentClient")
    @patch("main.QueueProcessor")
    @patch("main.create_default_settings")
    @patch("main.setup_logging")
    @pytest.mark.asyncio
    async def test_run_application(
        self,
        mock_setup_logging,
        mock_create_settings,
        mock_queue_processor,
        mock_agent_client,
        mock_plugin_manager,
    ):
        """Test running the application."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Mock the components
                mock_plugin_manager.return_value = MagicMock()
                mock_agent_client.return_value = MagicMock()
                mock_queue_processor.return_value = MagicMock()

                # Create application
                app = Application()

                # Mock the initialization and cleanup methods
                app._initialize_components = AsyncMock()
                app._cleanup_components = AsyncMock()

                # Create a task that will set the shutdown event after a short delay
                async def shutdown_after_delay():
                    await asyncio.sleep(0.1)
                    app._shutdown_event.set()

                # Start the shutdown task
                shutdown_task = asyncio.create_task(shutdown_after_delay())

                # Run the application (should exit quickly due to shutdown event)
                await app.run()

                # Verify initialization and cleanup were called
                app._initialize_components.assert_called_once()
                app._cleanup_components.assert_called_once()

                # Clean up the shutdown task
                shutdown_task.cancel()

            finally:
                os.chdir(original_cwd)

    @patch("main.PluginManager")
    @patch("main.AgentClient")
    @patch("main.QueueProcessor")
    @patch("main.create_default_settings")
    @patch("main.setup_logging")
    def test_application_pid_file(
        self,
        mock_setup_logging,
        mock_create_settings,
        mock_queue_processor,
        mock_agent_client,
        mock_plugin_manager,
    ):
        """Test PID file creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Mock the components
                mock_plugin_manager.return_value = MagicMock()
                mock_agent_client.return_value = MagicMock()
                mock_queue_processor.return_value = MagicMock()

                # Create application
                Application()

                # Verify PID file was created
                assert Path("broca2.pid").exists()

                # Verify PID content
                with open("broca2.pid") as f:
                    pid_content = f.read().strip()
                assert pid_content == str(os.getpid())

            finally:
                os.chdir(original_cwd)
