"""Unit tests for runtime core message functionality."""


import pytest

from runtime.core.message import Message, MessageFormatter, MessageHandler


@pytest.mark.unit
@pytest.mark.asyncio
async def test_message_creation():
    """Test Message dataclass creation."""
    from datetime import datetime

    message = Message(
        content="Hello world",
        user_id="123",
        username="testuser",
        platform="telegram",
        timestamp=datetime.now(),
        metadata={"key": "value"},
    )

    assert message.content == "Hello world"
    assert message.user_id == "123"
    assert message.username == "testuser"
    assert message.platform == "telegram"
    assert message.timestamp is not None
    assert message.metadata == {"key": "value"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_message_formatter_format_message():
    """Test MessageFormatter.format_message."""
    formatter = MessageFormatter()

    # Test basic formatting
    formatted = formatter.format_message("Hello world", "user")
    assert "Hello world" in formatted
    assert "user" in formatted


@pytest.mark.unit
@pytest.mark.asyncio
async def test_message_formatter_format_response():
    """Test MessageFormatter.format_message (no format_response method)."""
    formatter = MessageFormatter()

    # Test message formatting with string
    formatted = formatter.format_message("Response text")
    assert "Response text" in formatted


@pytest.mark.unit
@pytest.mark.asyncio
async def test_message_handler_abstract():
    """Test that MessageHandler is abstract."""
    # MessageHandler is abstract, so we can't instantiate it directly
    with pytest.raises(TypeError):
        MessageHandler()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_message_handler_methods():
    """Test MessageHandler abstract methods exist."""

    # Create a concrete implementation for testing
    class TestMessageHandler(MessageHandler):
        async def handle_message(self, message: Message) -> None:
            pass

        async def send_message(self, message: Message) -> None:
            pass

    handler = TestMessageHandler()
    message = Message(content="test")

    # Test that methods can be called
    await handler.handle_message(message)
    await handler.send_message(message)
