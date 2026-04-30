"""Contract tests for AgentTurnTimeoutInFlight (queue / Letta timeout semantics)."""

import pytest

from common.exceptions import AgentTurnTimeoutInFlight, BrocaError


@pytest.mark.unit
class TestAgentTurnTimeoutInFlightContract:
    """Ensure the exception type is stable for queue error handling."""

    def test_is_broca_error_subclass(self) -> None:
        exc = AgentTurnTimeoutInFlight("turn timed out")
        assert isinstance(exc, BrocaError)
        assert isinstance(exc, Exception)

    def test_recoverable_false(self) -> None:
        exc = AgentTurnTimeoutInFlight("x")
        assert exc.recoverable is False

    def test_message_and_str(self) -> None:
        exc = AgentTurnTimeoutInFlight("wall clock exceeded")
        assert exc.message == "wall clock exceeded"
        assert "wall clock" in str(exc)

    def test_context_optional(self) -> None:
        exc = AgentTurnTimeoutInFlight("msg", context={"k": "v"})
        assert exc.context == {"k": "v"}

    def test_distinct_from_builtin_timeout_error(self) -> None:
        """Queue branches ``except asyncio.TimeoutError`` vs this type; must not overlap."""
        exc = AgentTurnTimeoutInFlight("x")
        assert isinstance(exc, Exception)
        assert not isinstance(exc, TimeoutError)
