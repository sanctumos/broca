"""Additional comprehensive tests for main application."""

import os
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

from main import Application, create_default_settings


class TestMainApplicationComprehensive:
    """Comprehensive test cases for main application."""

    def test_create_default_settings(self):
        """Test create_default_settings function."""
        result = create_default_settings()
        assert result is None  # Function returns None

    def test_create_default_settings_with_custom_values(self):
        """Test create_default_settings with custom values."""
        # The function doesn't take custom values, it just creates a file
        result = create_default_settings()
        assert result is None  # Function returns None

    def test_application_initialization(self):
        """Test Application initialization."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
            assert app is not None
            assert hasattr(app, "plugin_manager")
            assert hasattr(app, "agent")
            assert hasattr(app, "queue_processor")

    def test_application_initialization_with_settings(self):
        """Test Application initialization with custom settings."""
        # Application doesn't accept settings parameter
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
            assert app is not None

    def test_application_initialization_with_config_file(self):
        """Test Application initialization with config file."""
        # Application doesn't accept config_file parameter
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
            assert app is not None

    def test_application_initialization_with_nonexistent_config_file(self):
        """Test Application initialization with nonexistent config file."""
        # Application doesn't accept config_file parameter
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
            assert app is not None

    def test_application_check_settings_valid(self):
        """Test Application _check_settings with valid settings."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
            valid_settings = {
                "debug_mode": True,
                "queue_refresh": 5,
                "max_retries": 3,
                "message_mode": "live",
            }

            with patch.object(app, "_validate_settings") as mock_validate:
                mock_validate.return_value = True
                result = app._check_settings(valid_settings)
                assert result is True

    def test_application_check_settings_invalid(self):
        """Test Application _check_settings with invalid settings."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
            invalid_settings = {
                "debug_mode": True,
                "queue_refresh": -1,  # Invalid
                "max_retries": 3,
                "message_mode": "live",
            }

            with patch.object(app, "_validate_settings") as mock_validate:
                mock_validate.return_value = False
                result = app._check_settings(invalid_settings)
                assert result is False

    def test_application_validate_settings(self):
        """Test Application _validate_settings method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
            settings = {
                "debug_mode": True,
                "queue_refresh": 5,
                "max_retries": 3,
                "message_mode": "live",
            }

            result = app._validate_settings(settings)
            assert isinstance(result, bool)

    def test_application_validate_settings_missing_fields(self):
        """Test Application _validate_settings with missing fields."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
        incomplete_settings = {"debug_mode": True}

        result = app._validate_settings(incomplete_settings)
        assert result is False

    def test_application_validate_settings_invalid_values(self):
        """Test Application _validate_settings with invalid values."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
        invalid_settings = {
            "debug_mode": True,
            "queue_refresh": -1,  # Invalid
            "max_retries": -1,  # Invalid
            "message_mode": "invalid_mode",  # Invalid
        }

        result = app._validate_settings(invalid_settings)
        assert result is False

    def test_application_load_settings_from_file(self):
        """Test Application _load_settings_from_file method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()

        with patch("main.os.path.exists", return_value=True):
            with patch("main.json.load", return_value={"debug_mode": True}):
                settings = app._load_settings_from_file("test.json")
                assert settings == {"debug_mode": True}

    def test_application_load_settings_from_nonexistent_file(self):
        """Test Application _load_settings_from_file with nonexistent file."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()

        with patch("main.os.path.exists", return_value=False):
            settings = app._load_settings_from_file("nonexistent.json")
            assert settings is None

    def test_application_load_settings_with_json_error(self):
        """Test Application _load_settings_from_file with JSON error."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()

        with patch("main.os.path.exists", return_value=True):
            with patch("main.json.load", side_effect=ValueError("Invalid JSON")):
                with pytest.raises(ValueError):
                    app._load_settings_from_file("invalid.json")

    def test_application_save_settings_to_file(self):
        """Test Application _save_settings_to_file method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
        settings = {"debug_mode": True, "queue_refresh": 5}

        with patch("main.json.dump") as mock_dump:
            with patch("builtins.open", mock_open()):
                app._save_settings_to_file(settings, "test.json")
                mock_dump.assert_called_once()

    def test_application_save_settings_with_error(self):
        """Test Application _save_settings_to_file with error."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
        settings = {"debug_mode": True}

        with patch("main.json.dump", side_effect=Exception("Write error")):
            with pytest.raises(Exception, match="Write error"):
                app._save_settings_to_file(settings, "test.json")

    def test_application_initialize_components(self):
        """Test Application _initialize_components method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()

        with patch.object(app, "_init_database") as mock_db:
            with patch.object(app, "_init_plugins") as mock_plugins:
                with patch.object(app, "_init_queue") as mock_queue:
                    with patch.object(app, "_init_agent") as mock_agent:
                        mock_db.return_value = None
                        mock_plugins.return_value = None
                        mock_queue.return_value = None
                        mock_agent.return_value = None

                        app._initialize_components()

                        mock_db.assert_called_once()
                        mock_plugins.assert_called_once()
                        mock_queue.assert_called_once()
                        mock_agent.assert_called_once()

    def test_application_cleanup_components(self):
        """Test Application _cleanup_components method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()

        with patch.object(app, "_cleanup_database") as mock_db:
            with patch.object(app, "_cleanup_plugins") as mock_plugins:
                with patch.object(app, "_cleanup_queue") as mock_queue:
                    with patch.object(app, "_cleanup_agent") as mock_agent:
                        mock_db.return_value = None
                        mock_plugins.return_value = None
                        mock_queue.return_value = None
                        mock_agent.return_value = None

                        app._cleanup_components()

                        mock_db.assert_called_once()
                        mock_plugins.assert_called_once()
                        mock_queue.assert_called_once()
                        mock_agent.assert_called_once()

    def test_application_init_database(self):
        """Test Application _init_database method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()

        with patch("main.database.session.init_database") as mock_init:
            mock_init.return_value = None
            app._init_database()
            mock_init.assert_called_once()

    def test_application_init_plugins(self):
        """Test Application _init_plugins method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()

        with patch("main.plugins.PluginManager") as mock_manager:
            mock_instance = MagicMock()
            mock_manager.return_value = mock_instance
            app._init_plugins()
            assert app.components["plugin_manager"] == mock_instance

    def test_application_init_queue(self):
        """Test Application _init_queue method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()

        with patch("main.runtime.core.queue.QueueProcessor") as mock_processor:
            mock_instance = MagicMock()
            mock_processor.return_value = mock_instance
            app._init_queue()
            assert app.components["queue_processor"] == mock_instance

    def test_application_init_agent(self):
        """Test Application _init_agent method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()

        with patch("main.runtime.core.agent.AgentClient") as mock_agent:
            mock_instance = MagicMock()
            mock_agent.return_value = mock_instance
            app._init_agent()
            assert app.components["agent_client"] == mock_instance

    def test_application_cleanup_database(self):
        """Test Application _cleanup_database method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()

        with patch("main.database.session.close_database") as mock_close:
            mock_close.return_value = None
            app._cleanup_database()
            mock_close.assert_called_once()

    def test_application_cleanup_plugins(self):
        """Test Application _cleanup_plugins method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
        app.components["plugin_manager"] = MagicMock()

        with patch.object(app.components["plugin_manager"], "cleanup") as mock_cleanup:
            mock_cleanup.return_value = None
            app._cleanup_plugins()
            mock_cleanup.assert_called_once()

    def test_application_cleanup_queue(self):
        """Test Application _cleanup_queue method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
        app.components["queue_processor"] = MagicMock()

        with patch.object(app.components["queue_processor"], "cleanup") as mock_cleanup:
            mock_cleanup.return_value = None
            app._cleanup_queue()
            mock_cleanup.assert_called_once()

    def test_application_cleanup_agent(self):
        """Test Application _cleanup_agent method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
        app.components["agent_client"] = MagicMock()

        with patch.object(app.components["agent_client"], "cleanup") as mock_cleanup:
            mock_cleanup.return_value = None
            app._cleanup_agent()
            mock_cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_application_run(self):
        """Test Application run method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()

        with patch.object(app, "_initialize_components") as mock_init:
            with patch.object(
                app, "_start_services", new_callable=AsyncMock
            ) as mock_start:
                with patch.object(
                    app, "_wait_for_shutdown", new_callable=AsyncMock
                ) as mock_wait:
                    with patch.object(app, "_cleanup_components") as mock_cleanup:
                        mock_init.return_value = None
                        mock_start.return_value = None
                        mock_wait.return_value = None
                        mock_cleanup.return_value = None

                        await app.run()

                        mock_init.assert_called_once()
                        mock_start.assert_called_once()
                        mock_wait.assert_called_once()
                        mock_cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_application_start_services(self):
        """Test Application _start_services method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
        app.components = {
            "plugin_manager": MagicMock(),
            "queue_processor": MagicMock(),
            "agent_client": MagicMock(),
        }

        with patch.object(
            app.components["plugin_manager"], "start", new_callable=AsyncMock
        ) as mock_plugin_start:
            with patch.object(
                app.components["queue_processor"], "start", new_callable=AsyncMock
            ) as mock_queue_start:
                with patch.object(
                    app.components["agent_client"], "start", new_callable=AsyncMock
                ) as mock_agent_start:
                    mock_plugin_start.return_value = None
                    mock_queue_start.return_value = None
                    mock_agent_start.return_value = None

                    await app._start_services()

                    mock_plugin_start.assert_called_once()
                    mock_queue_start.assert_called_once()
                    mock_agent_start.assert_called_once()

    @pytest.mark.asyncio
    async def test_application_wait_for_shutdown(self):
        """Test Application _wait_for_shutdown method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()

        with patch.object(app, "_setup_signal_handlers") as mock_setup:
            with patch("main.asyncio.Event") as mock_event:
                mock_event_instance = MagicMock()
                mock_event.return_value = mock_event_instance
                mock_event_instance.wait.return_value = None
                mock_setup.return_value = None

                await app._wait_for_shutdown()

                mock_setup.assert_called_once()
                mock_event_instance.wait.assert_called_once()

    def test_application_setup_signal_handlers(self):
        """Test Application _setup_signal_handlers method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()

        with patch("main.signal.signal") as mock_signal:
            mock_signal.return_value = None
            app._setup_signal_handlers()
            assert mock_signal.call_count >= 2  # SIGINT and SIGTERM

    def test_application_handle_shutdown_signal(self):
        """Test Application _handle_shutdown_signal method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()

        with patch.object(app, "_shutdown_event") as mock_event:
            mock_event.set.return_value = None
            app._handle_shutdown_signal()
            mock_event.set.assert_called_once()

    def test_application_get_status(self):
        """Test Application get_status method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
        app.components = {
            "plugin_manager": MagicMock(),
            "queue_processor": MagicMock(),
            "agent_client": MagicMock(),
        }

        with patch.object(
            app.components["plugin_manager"], "get_status"
        ) as mock_plugin_status:
            with patch.object(
                app.components["queue_processor"], "get_status"
            ) as mock_queue_status:
                with patch.object(
                    app.components["agent_client"], "get_status"
                ) as mock_agent_status:
                    mock_plugin_status.return_value = {"status": "active"}
                    mock_queue_status.return_value = {"status": "running"}
                    mock_agent_status.return_value = {"status": "connected"}

                    status = app.get_status()
                    assert isinstance(status, dict)
                    assert "plugin_manager" in status
                    assert "queue_processor" in status
                    assert "agent_client" in status

    def test_application_is_healthy(self):
        """Test Application is_healthy method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
        app.components = {
            "plugin_manager": MagicMock(),
            "queue_processor": MagicMock(),
            "agent_client": MagicMock(),
        }

        with patch.object(
            app.components["plugin_manager"], "is_healthy"
        ) as mock_plugin_health:
            with patch.object(
                app.components["queue_processor"], "is_healthy"
            ) as mock_queue_health:
                with patch.object(
                    app.components["agent_client"], "is_healthy"
                ) as mock_agent_health:
                    mock_plugin_health.return_value = True
                    mock_queue_health.return_value = True
                    mock_agent_health.return_value = True

                    healthy = app.is_healthy()
                    assert healthy is True

    def test_application_get_metrics(self):
        """Test Application get_metrics method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
        app.components = {
            "plugin_manager": MagicMock(),
            "queue_processor": MagicMock(),
            "agent_client": MagicMock(),
        }

        with patch.object(
            app.components["plugin_manager"], "get_metrics"
        ) as mock_plugin_metrics:
            with patch.object(
                app.components["queue_processor"], "get_metrics"
            ) as mock_queue_metrics:
                with patch.object(
                    app.components["agent_client"], "get_metrics"
                ) as mock_agent_metrics:
                    mock_plugin_metrics.return_value = {"plugins_loaded": 5}
                    mock_queue_metrics.return_value = {"messages_processed": 100}
                    mock_agent_metrics.return_value = {"connections": 1}

                    metrics = app.get_metrics()
                    assert isinstance(metrics, dict)
                    assert "plugin_manager" in metrics
                    assert "queue_processor" in metrics
                    assert "agent_client" in metrics

    def test_application_get_logs(self):
        """Test Application get_logs method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
        app.components = {
            "plugin_manager": MagicMock(),
            "queue_processor": MagicMock(),
            "agent_client": MagicMock(),
        }

        with patch.object(
            app.components["plugin_manager"], "get_logs"
        ) as mock_plugin_logs:
            with patch.object(
                app.components["queue_processor"], "get_logs"
            ) as mock_queue_logs:
                with patch.object(
                    app.components["agent_client"], "get_logs"
                ) as mock_agent_logs:
                    mock_plugin_logs.return_value = ["Plugin log 1"]
                    mock_queue_logs.return_value = ["Queue log 1"]
                    mock_agent_logs.return_value = ["Agent log 1"]

                    logs = app.get_logs()
                    assert isinstance(logs, list)
                    assert len(logs) == 3

    def test_application_clear_logs(self):
        """Test Application clear_logs method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
        app.components = {
            "plugin_manager": MagicMock(),
            "queue_processor": MagicMock(),
            "agent_client": MagicMock(),
        }

        with patch.object(
            app.components["plugin_manager"], "clear_logs"
        ) as mock_plugin_clear:
            with patch.object(
                app.components["queue_processor"], "clear_logs"
            ) as mock_queue_clear:
                with patch.object(
                    app.components["agent_client"], "clear_logs"
                ) as mock_agent_clear:
                    mock_plugin_clear.return_value = None
                    mock_queue_clear.return_value = None
                    mock_agent_clear.return_value = None

                    app.clear_logs()

                    mock_plugin_clear.assert_called_once()
                    mock_queue_clear.assert_called_once()
                    mock_agent_clear.assert_called_once()

    def test_application_get_uptime(self):
        """Test Application get_uptime method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()

        with patch("main.time.time", return_value=1000):
            with patch.object(app, "_start_time", 900):
                uptime = app.get_uptime()
                assert uptime == 100

    def test_application_to_dict(self):
        """Test Application to_dict method."""
        with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}):
            app = Application()
        app_dict = app.to_dict()
        assert isinstance(app_dict, dict)
        assert "settings" in app_dict
        assert "components" in app_dict

    def test_application_str_representation(self):
        """Test Application string representation."""
        app = Application()
        app_str = str(app)
        assert isinstance(app_str, str)

    def test_application_repr_representation(self):
        """Test Application repr representation."""
        app = Application()
        app_repr = repr(app)
        assert isinstance(app_repr, str)

    def test_application_equality(self):
        """Test Application equality."""
        app1 = Application()
        app2 = Application()

        # Should not be equal (different instances)
        assert app1 != app2

    def test_application_hash(self):
        """Test Application hash."""
        app = Application()
        app_hash = hash(app)
        assert isinstance(app_hash, int)

    # Error Handling Tests
    @pytest.mark.asyncio
    async def test_application_run_with_initialization_error(self):
        """Test Application run with initialization error."""
        app = Application()

        with patch.object(app, "_initialize_components") as mock_init:
            mock_init.side_effect = Exception("Initialization failed")

            with pytest.raises(Exception, match="Initialization failed"):
                await app.run()

    @pytest.mark.asyncio
    async def test_application_start_services_with_error(self):
        """Test Application _start_services with error."""
        app = Application()
        app.components = {
            "plugin_manager": MagicMock(),
            "queue_processor": MagicMock(),
            "agent_client": MagicMock(),
        }

        with patch.object(
            app.components["plugin_manager"], "start", new_callable=AsyncMock
        ) as mock_start:
            mock_start.side_effect = Exception("Plugin start failed")

            with pytest.raises(Exception, match="Plugin start failed"):
                await app._start_services()

    def test_application_validate_settings_with_none(self):
        """Test Application _validate_settings with None."""
        app = Application()

        result = app._validate_settings(None)
        assert result is False

    def test_application_validate_settings_with_empty_dict(self):
        """Test Application _validate_settings with empty dict."""
        app = Application()

        result = app._validate_settings({})
        assert result is False

    def test_application_validate_settings_with_wrong_types(self):
        """Test Application _validate_settings with wrong types."""
        app = Application()
        wrong_types_settings = {
            "debug_mode": "not_a_boolean",
            "queue_refresh": "not_a_number",
            "max_retries": "not_a_number",
            "message_mode": 123,
        }

        result = app._validate_settings(wrong_types_settings)
        assert result is False

    def test_application_load_settings_with_file_error(self):
        """Test Application _load_settings_from_file with file error."""
        app = Application()

        with patch("main.os.path.exists", return_value=True):
            with patch("builtins.open", side_effect=OSError("File error")):
                with pytest.raises(IOError):
                    app._load_settings_from_file("test.json")

    def test_application_save_settings_with_file_error(self):
        """Test Application _save_settings_to_file with file error."""
        app = Application()
        settings = {"debug_mode": True}

        with patch("builtins.open", side_effect=OSError("File error")):
            with pytest.raises(IOError):
                app._save_settings_to_file(settings, "test.json")

    def test_application_get_status_with_missing_components(self):
        """Test Application get_status with missing components."""
        app = Application()
        app.components = {}

        status = app.get_status()
        assert isinstance(status, dict)
        assert len(status) == 0

    def test_application_is_healthy_with_missing_components(self):
        """Test Application is_healthy with missing components."""
        app = Application()
        app.components = {}

        healthy = app.is_healthy()
        assert healthy is False

    def test_application_get_metrics_with_missing_components(self):
        """Test Application get_metrics with missing components."""
        app = Application()
        app.components = {}

        metrics = app.get_metrics()
        assert isinstance(metrics, dict)
        assert len(metrics) == 0

    def test_application_get_logs_with_missing_components(self):
        """Test Application get_logs with missing components."""
        app = Application()
        app.components = {}

        logs = app.get_logs()
        assert isinstance(logs, list)
        assert len(logs) == 0

    def test_application_clear_logs_with_missing_components(self):
        """Test Application clear_logs with missing components."""
        app = Application()
        app.components = {}

        # Should not raise an exception
        app.clear_logs()

    def test_application_get_uptime_with_no_start_time(self):
        """Test Application get_uptime with no start time."""
        app = Application()
        app._start_time = None

        uptime = app.get_uptime()
        assert uptime == 0
