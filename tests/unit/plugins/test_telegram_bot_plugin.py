"""Unit tests for telegram bot plugin."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from plugins.telegram_bot.plugin import TelegramBotPlugin, TelegramBotPluginWrapper


class TestTelegramBotPlugin:
    """Test cases for TelegramBotPlugin."""

    def test_plugin_wrapper_initialization(self):
        """Test plugin wrapper initialization."""
        wrapper = TelegramBotPluginWrapper()
        assert wrapper is not None
        assert wrapper._plugin is not None

    def test_plugin_wrapper_get_name(self):
        """Test plugin wrapper get_name method."""
        wrapper = TelegramBotPluginWrapper()

        with patch.object(wrapper._plugin, "get_name", return_value="telegram_bot"):
            name = wrapper.get_name()
            assert name == "telegram_bot"

    def test_plugin_wrapper_get_platform(self):
        """Test plugin wrapper get_platform method."""
        wrapper = TelegramBotPluginWrapper()

        with patch.object(wrapper._plugin, "get_platform", return_value="telegram"):
            platform = wrapper.get_platform()
            assert platform == "telegram"

    def test_plugin_wrapper_get_message_handler(self):
        """Test plugin wrapper get_message_handler method."""
        wrapper = TelegramBotPluginWrapper()

        mock_handler = MagicMock()
        with patch.object(
            wrapper._plugin, "get_message_handler", return_value=mock_handler
        ):
            handler = wrapper.get_message_handler()
            assert handler == mock_handler

    def test_plugin_wrapper_get_settings(self):
        """Test plugin wrapper get_settings method."""
        wrapper = TelegramBotPluginWrapper()

        mock_settings = {"token": "test_token"}
        with patch.object(wrapper._plugin, "get_settings", return_value=mock_settings):
            settings = wrapper.get_settings()
            assert settings == mock_settings

    def test_plugin_wrapper_apply_settings(self):
        """Test plugin wrapper apply_settings method."""
        wrapper = TelegramBotPluginWrapper()

        test_settings = {"token": "test_token"}

        # Test with apply_settings method
        with patch.object(wrapper._plugin, "apply_settings") as mock_apply:
            wrapper.apply_settings(test_settings)
            mock_apply.assert_called_once_with(test_settings)

    def test_plugin_wrapper_apply_settings_fallback(self):
        """Test plugin wrapper apply_settings fallback."""
        wrapper = TelegramBotPluginWrapper()

        test_settings = {"token": "test_token"}

        # Test fallback to validate_settings
        with patch.object(
            wrapper._plugin, "apply_settings", side_effect=AttributeError
        ):
            with patch.object(wrapper._plugin, "validate_settings") as mock_validate:
                wrapper.apply_settings(test_settings)
                mock_validate.assert_called_once_with(test_settings)

    def test_plugin_wrapper_validate_settings(self):
        """Test plugin wrapper validate_settings method."""
        wrapper = TelegramBotPluginWrapper()

        test_settings = {"token": "test_token"}

        with patch.object(
            wrapper._plugin, "validate_settings", return_value=True
        ) as mock_validate:
            result = wrapper.validate_settings(test_settings)
            mock_validate.assert_called_once_with(test_settings)
            assert result is True

    def test_plugin_wrapper_validate_settings_fallback(self):
        """Test plugin wrapper validate_settings fallback."""
        wrapper = TelegramBotPluginWrapper()

        test_settings = {"token": "test_token"}

        # Test fallback when validate_settings doesn't exist
        with patch.object(
            wrapper._plugin, "validate_settings", side_effect=AttributeError
        ):
            result = wrapper.validate_settings(test_settings)
            assert result is False

    @pytest.mark.asyncio
    async def test_plugin_wrapper_start(self):
        """Test plugin wrapper start method."""
        wrapper = TelegramBotPluginWrapper()

        with patch.object(
            wrapper._plugin, "start", new_callable=AsyncMock
        ) as mock_start:
            await wrapper.start()
            mock_start.assert_called_once()

    @pytest.mark.asyncio
    async def test_plugin_wrapper_stop(self):
        """Test plugin wrapper stop method."""
        wrapper = TelegramBotPluginWrapper()

        with patch.object(wrapper._plugin, "stop", new_callable=AsyncMock) as mock_stop:
            await wrapper.stop()
            mock_stop.assert_called_once()

    def test_plugin_wrapper_register_event_handler(self):
        """Test plugin wrapper register_event_handler method."""
        wrapper = TelegramBotPluginWrapper()

        mock_handler = MagicMock()

        with patch.object(wrapper._plugin, "register_event_handler") as mock_register:
            wrapper.register_event_handler("test_event", mock_handler)
            mock_register.assert_called_once_with("test_event", mock_handler)

    def test_plugin_wrapper_emit_event(self):
        """Test plugin wrapper emit_event method."""
        wrapper = TelegramBotPluginWrapper()

        mock_event = MagicMock()

        with patch.object(wrapper._plugin, "emit_event") as mock_emit:
            wrapper.emit_event(mock_event)
            mock_emit.assert_called_once_with(mock_event)

    def test_telegram_bot_plugin_initialization(self):
        """Test TelegramBotPlugin initialization."""
        with patch("plugins.telegram_bot.plugin.TelegramBotSettings") as mock_settings:
            mock_settings.return_value = MagicMock()

            plugin = TelegramBotPlugin()
            assert plugin is not None

    def test_telegram_bot_plugin_get_name(self):
        """Test TelegramBotPlugin get_name method."""
        with patch("plugins.telegram_bot.plugin.TelegramBotSettings") as mock_settings:
            mock_settings.return_value = MagicMock()

            plugin = TelegramBotPlugin()
            name = plugin.get_name()
            assert name == "telegram_bot"

    def test_telegram_bot_plugin_get_platform(self):
        """Test TelegramBotPlugin get_platform method."""
        with patch("plugins.telegram_bot.plugin.TelegramBotSettings") as mock_settings:
            mock_settings.return_value = MagicMock()

            plugin = TelegramBotPlugin()
            platform = plugin.get_platform()
            assert platform == "telegram"

    def test_telegram_bot_plugin_get_message_handler(self):
        """Test TelegramBotPlugin get_message_handler method."""
        with patch("plugins.telegram_bot.plugin.TelegramBotSettings") as mock_settings:
            mock_settings.return_value = MagicMock()

            plugin = TelegramBotPlugin()
            handler = plugin.get_message_handler()
            assert handler is not None

    def test_telegram_bot_plugin_get_settings(self):
        """Test TelegramBotPlugin get_settings method."""
        with patch("plugins.telegram_bot.plugin.TelegramBotSettings") as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings.return_value = mock_settings_instance

            plugin = TelegramBotPlugin()
            settings = plugin.get_settings()
            assert settings == mock_settings_instance

    def test_telegram_bot_plugin_validate_settings(self):
        """Test TelegramBotPlugin validate_settings method."""
        with patch("plugins.telegram_bot.plugin.TelegramBotSettings") as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings_instance.validate.return_value = True
            mock_settings.return_value = mock_settings_instance

            plugin = TelegramBotPlugin()
            test_settings = {"token": "test_token"}
            result = plugin.validate_settings(test_settings)
            assert result is True

    def test_telegram_bot_plugin_apply_settings(self):
        """Test TelegramBotPlugin apply_settings method."""
        with patch("plugins.telegram_bot.plugin.TelegramBotSettings") as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings.return_value = mock_settings_instance

            plugin = TelegramBotPlugin()
            test_settings = {"token": "test_token"}
            plugin.apply_settings(test_settings)

            # Verify settings were applied
            mock_settings_instance.update.assert_called_once_with(test_settings)

    @pytest.mark.asyncio
    async def test_telegram_bot_plugin_start(self):
        """Test TelegramBotPlugin start method."""
        with patch("plugins.telegram_bot.plugin.TelegramBotSettings") as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings.return_value = mock_settings_instance

            plugin = TelegramBotPlugin()

            with patch.object(
                plugin, "_start_bot", new_callable=AsyncMock
            ) as mock_start_bot:
                await plugin.start()
                mock_start_bot.assert_called_once()

    @pytest.mark.asyncio
    async def test_telegram_bot_plugin_stop(self):
        """Test TelegramBotPlugin stop method."""
        with patch("plugins.telegram_bot.plugin.TelegramBotSettings") as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings.return_value = mock_settings_instance

            plugin = TelegramBotPlugin()

            with patch.object(
                plugin, "_stop_bot", new_callable=AsyncMock
            ) as mock_stop_bot:
                await plugin.stop()
                mock_stop_bot.assert_called_once()

    def test_telegram_bot_plugin_register_event_handler(self):
        """Test TelegramBotPlugin register_event_handler method."""
        with patch("plugins.telegram_bot.plugin.TelegramBotSettings") as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings.return_value = mock_settings_instance

            plugin = TelegramBotPlugin()

            mock_handler = MagicMock()
            plugin.register_event_handler("test_event", mock_handler)

            # Verify handler was registered
            assert "test_event" in plugin._event_handlers
            assert mock_handler in plugin._event_handlers["test_event"]

    def test_telegram_bot_plugin_emit_event(self):
        """Test TelegramBotPlugin emit_event method."""
        with patch("plugins.telegram_bot.plugin.TelegramBotSettings") as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings.return_value = mock_settings_instance

            plugin = TelegramBotPlugin()

            mock_event = MagicMock()
            mock_event.type = "test_event"

            mock_handler = MagicMock()
            plugin.event_handlers["test_event"] = [mock_handler]

            plugin.emit_event(mock_event, "test_data")

            # Verify handler was called
            mock_handler.assert_called_once_with(mock_event)

    def test_telegram_bot_plugin_emit_event_no_handlers(self):
        """Test TelegramBotPlugin emit_event with no handlers."""
        with patch("plugins.telegram_bot.plugin.TelegramBotSettings") as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings.return_value = mock_settings_instance

            plugin = TelegramBotPlugin()

            mock_event = MagicMock()
            mock_event.type = "test_event"

            # No handlers registered
            plugin.emit_event(mock_event)

            # Should not raise an exception

    @pytest.mark.asyncio
    async def test_telegram_bot_plugin_start_bot(self):
        """Test TelegramBotPlugin _start_bot method."""
        with patch("plugins.telegram_bot.plugin.TelegramBotSettings") as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings_instance.bot_token = "test_token"
            mock_settings.from_env.return_value = mock_settings_instance

            plugin = TelegramBotPlugin()

            with patch("aiogram.Bot") as mock_bot:
                with patch("aiogram.Dispatcher") as mock_dispatcher:
                    mock_bot_instance = MagicMock()
                    mock_bot.return_value = mock_bot_instance

                    mock_dispatcher_instance = MagicMock()
                    mock_dispatcher_instance.start_polling = AsyncMock()
                    mock_dispatcher.return_value = mock_dispatcher_instance

                    await plugin.start()

                    # Verify bot and dispatcher were created
                    mock_bot.assert_called_once_with(token="test_token")
                    mock_dispatcher.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_telegram_bot_plugin_stop_bot(self):
        """Test TelegramBotPlugin _stop_bot method."""
        with patch("plugins.telegram_bot.plugin.TelegramBotSettings") as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings.return_value = mock_settings_instance

            plugin = TelegramBotPlugin()

            # Set up mock bot and dispatcher
            plugin.bot = MagicMock()
            plugin.bot.session.close = AsyncMock()

            await plugin.stop()

            # Verify bot was stopped
            plugin.bot.session.close.assert_called_once()
