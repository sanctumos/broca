"""Unit tests for plugin system."""

from collections.abc import Callable
from unittest.mock import MagicMock

import pytest

from plugins import Event, EventType, Plugin


@pytest.mark.unit
def test_plugin_abstract():
    """Test Plugin abstract class."""
    # Plugin is abstract, so we can't instantiate it directly
    with pytest.raises(TypeError):
        Plugin()


@pytest.mark.unit
def test_plugin_concrete_implementation():
    """Test concrete Plugin implementation."""

    class TestPlugin(Plugin):
        def get_name(self) -> str:
            return "test_plugin"

        def get_platform(self) -> str:
            return "test_platform"

        async def start(self) -> None:
            pass

        async def stop(self) -> None:
            pass

        def get_message_handler(self) -> Callable:
            return MagicMock()

        def register_event_handler(
            self, event_type: EventType, handler: Callable[[Event], None]
        ) -> None:
            pass

        def emit_event(self, event: Event) -> None:
            pass

    plugin = TestPlugin()
    assert plugin.get_name() == "test_plugin"
    assert plugin.get_platform() == "test_platform"


@pytest.mark.unit
def test_event_creation():
    """Test Event dataclass creation."""
    event = Event(
        type=EventType.MESSAGE, data={"message": "test"}, source="test_plugin"
    )
    assert event.type == EventType.MESSAGE
    assert event.data == {"message": "test"}
    assert event.source == "test_plugin"


@pytest.mark.unit
def test_event_type_enum():
    """Test EventType enum values."""
    assert EventType.MESSAGE is not None
    assert EventType.STATUS is not None
    assert EventType.ERROR is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_plugin_lifecycle():
    """Test plugin lifecycle methods."""

    class TestPlugin(Plugin):
        def __init__(self):
            self.started = False
            self.stopped = False

        def get_name(self) -> str:
            return "test_plugin"

        def get_platform(self) -> str:
            return "test_platform"

        async def start(self) -> None:
            self.started = True

        async def stop(self) -> None:
            self.stopped = True

        def get_message_handler(self) -> Callable:
            return MagicMock()

        def register_event_handler(
            self, event_type: EventType, handler: Callable[[Event], None]
        ) -> None:
            pass

        def emit_event(self, event: Event) -> None:
            pass

    plugin = TestPlugin()
    assert not plugin.started
    assert not plugin.stopped

    await plugin.start()
    assert plugin.started
    assert not plugin.stopped

    await plugin.stop()
    assert plugin.started
    assert plugin.stopped


@pytest.mark.unit
@pytest.mark.asyncio
async def test_plugin_message_handling():
    """Test plugin message handling."""

    class TestPlugin(Plugin):
        def __init__(self):
            self.handled_messages = []

        def get_name(self) -> str:
            return "test_plugin"

        def get_platform(self) -> str:
            return "test_platform"

        async def start(self) -> None:
            pass

        async def stop(self) -> None:
            pass

        def get_message_handler(self) -> Callable:
            return MagicMock()

        def register_event_handler(
            self, event_type: EventType, handler: Callable[[Event], None]
        ) -> None:
            pass

        def emit_event(self, event: Event) -> None:
            pass

        async def handle_message(self, message: dict) -> None:
            self.handled_messages.append(message)

    plugin = TestPlugin()
    test_message = {"content": "Hello", "user": "test_user"}

    await plugin.handle_message(test_message)
    assert len(plugin.handled_messages) == 1
    assert plugin.handled_messages[0] == test_message


@pytest.mark.unit
def test_plugin_validation():
    """Test plugin validation methods."""

    class TestPlugin(Plugin):
        def get_name(self) -> str:
            return "test_plugin"

        def get_platform(self) -> str:
            return "test_platform"

        async def start(self) -> None:
            pass

        async def stop(self) -> None:
            pass

        def get_message_handler(self) -> Callable:
            return MagicMock()

        def register_event_handler(
            self, event_type: EventType, handler: Callable[[Event], None]
        ) -> None:
            pass

        def emit_event(self, event: Event) -> None:
            pass

        async def handle_message(self, message: dict) -> None:
            pass

        def validate_settings(self, settings: dict) -> bool:
            return "required_key" in settings

    plugin = TestPlugin()

    valid_settings = {"required_key": "value"}
    invalid_settings = {"other_key": "value"}

    assert plugin.validate_settings(valid_settings) is True
    assert plugin.validate_settings(invalid_settings) is False


@pytest.mark.unit
def test_plugin_event_emission():
    """Test plugin event emission."""

    class TestPlugin(Plugin):
        def __init__(self):
            self.events = []

        def get_name(self) -> str:
            return "test_plugin"

        def get_platform(self) -> str:
            return "test_platform"

        async def start(self) -> None:
            pass

        async def stop(self) -> None:
            pass

        def get_message_handler(self) -> Callable:
            return MagicMock()

        def register_event_handler(
            self, event_type: EventType, handler: Callable[[Event], None]
        ) -> None:
            pass

        def emit_event(self, event: Event) -> None:
            self.events.append(event)

    plugin = TestPlugin()
    event = Event(type=EventType.MESSAGE, data={"test": "data"}, source="test_plugin")
    plugin.emit_event(event)

    assert len(plugin.events) == 1
    assert plugin.events[0].type == EventType.MESSAGE
    assert plugin.events[0].data == {"test": "data"}


@pytest.mark.unit
def test_plugin_settings_handling():
    """Test plugin settings handling."""

    class TestPlugin(Plugin):
        def __init__(self):
            self.settings = {}

        def get_name(self) -> str:
            return "test_plugin"

        def get_platform(self) -> str:
            return "test_platform"

        async def start(self) -> None:
            pass

        async def stop(self) -> None:
            pass

        def get_message_handler(self) -> Callable:
            return MagicMock()

        def register_event_handler(
            self, event_type: EventType, handler: Callable[[Event], None]
        ) -> None:
            pass

        def emit_event(self, event: Event) -> None:
            pass

        async def handle_message(self, message: dict) -> None:
            pass

        def load_settings(self, settings: dict) -> None:
            self.settings = settings

        def get_settings(self) -> dict:
            return self.settings

    plugin = TestPlugin()
    test_settings = {"key1": "value1", "key2": "value2"}

    plugin.load_settings(test_settings)
    assert plugin.get_settings() == test_settings


@pytest.mark.unit
def test_plugin_error_handling():
    """Test plugin error handling."""

    class TestPlugin(Plugin):
        def __init__(self):
            self.errors = []

        def get_name(self) -> str:
            return "test_plugin"

        def get_platform(self) -> str:
            return "test_platform"

        async def start(self) -> None:
            pass

        async def stop(self) -> None:
            pass

        def get_message_handler(self) -> Callable:
            return MagicMock()

        def register_event_handler(
            self, event_type: EventType, handler: Callable[[Event], None]
        ) -> None:
            pass

        def emit_event(self, event: Event) -> None:
            pass

        async def handle_message(self, message: dict) -> None:
            pass

        def handle_error(self, error: Exception) -> None:
            self.errors.append(str(error))

    plugin = TestPlugin()
    test_error = Exception("Test error")

    plugin.handle_error(test_error)
    assert len(plugin.errors) == 1
    assert plugin.errors[0] == "Test error"
