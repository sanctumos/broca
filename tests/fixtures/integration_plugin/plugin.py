"""Minimal plugin for integration tests: no external deps, implements full Plugin interface."""

from plugins import Event, EventType, Plugin


class IntegrationTestPlugin(Plugin):
    """Minimal plugin for integration tests."""

    def __init__(self) -> None:
        self._running = False
        self._handlers: list = []

    async def start(self) -> None:
        self._running = True

    async def stop(self) -> None:
        self._running = False

    def get_name(self) -> str:
        return "integration_test"

    def get_platform(self) -> str:
        return "integration_test"

    def get_message_handler(self):
        async def handler(response: str, profile, message_id: int) -> None:
            pass

        return handler

    def register_event_handler(self, event_type: EventType, handler) -> None:
        self._handlers.append((event_type, handler))

    def emit_event(self, event: Event) -> None:
        for et, h in self._handlers:
            if et == event.type:
                h(event)
