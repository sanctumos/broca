"""
AgentClient timeout / ``AgentTurnTimeoutInFlight`` behavior (streaming + fallback).

Complements ``test_queue_timeout_inflight.py`` (queue-side) for production safety.
"""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.exceptions import AgentTurnTimeoutInFlight
from runtime.core.agent import AgentClient


def _slow_stream():
    while True:
        time.sleep(2)
        yield MagicMock()


@pytest.mark.unit
@pytest.mark.asyncio
class TestProcessMessageAsyncStreamTimeoutAndFallback:
    """``LONG_TASK_MAX_WAIT`` stream timeout → async fallback; ``AgentTurnTimeoutInFlight`` rules."""

    @staticmethod
    def _env(short_wait: bool = True):
        base = {
            "DEBUG_MODE": False,
            "AGENT_ID": "test-agent",
        }
        if short_wait:
            base["LONG_TASK_MAX_WAIT"] = "1"
        else:
            base["LONG_TASK_MAX_WAIT"] = "600"
        return lambda key, default=None, required=False, cast_type=None: base.get(
            key, default
        )

    @pytest.mark.parametrize(
        ("fb_return", "raises_inflight", "expected_value"),
        [
            (None, True, None),
            ("", False, ""),
            ("final", False, "final"),
            ("  trimmed  ", False, "  trimmed  "),
        ],
    )
    async def test_after_stream_timeout_fallback_outcomes(
        self,
        fb_return: str | None,
        raises_inflight: bool,
        expected_value: str | None,
    ) -> None:
        with patch("runtime.core.agent.get_env_var", side_effect=self._env(True)):
            with patch("runtime.core.agent.get_letta_client") as mock_get_client:
                mock_client = MagicMock()
                mock_get_client.return_value = mock_client
                mock_client.agents.messages.create.return_value = _slow_stream()

                with patch.object(
                    AgentClient, "_fallback_to_async", new_callable=AsyncMock
                ) as mock_fb:
                    mock_fb.return_value = fb_return
                    agent = AgentClient()
                    if raises_inflight:
                        with pytest.raises(AgentTurnTimeoutInFlight):
                            await agent.process_message_async("ping")
                    else:
                        out = await agent.process_message_async("ping")
                        assert out == expected_value

    async def test_fallback_raises_after_stream_timeout(self) -> None:
        with patch("runtime.core.agent.get_env_var", side_effect=self._env(True)):
            with patch("runtime.core.agent.get_letta_client") as mock_get_client:
                mock_client = MagicMock()
                mock_get_client.return_value = mock_client
                mock_client.agents.messages.create.return_value = _slow_stream()

                with patch.object(
                    AgentClient, "_fallback_to_async", new_callable=AsyncMock
                ) as mock_fb:
                    mock_fb.side_effect = ConnectionError("letta down")

                    agent = AgentClient()
                    with pytest.raises(AgentTurnTimeoutInFlight):
                        await agent.process_message_async("ping")


@pytest.mark.unit
@pytest.mark.asyncio
class TestProcessMessageAsyncDebugModeIgnoresStreamTimeout:
    async def test_debug_mode_returns_input_without_stream(self) -> None:
        with patch("runtime.core.agent.get_env_var") as ge:
            ge.side_effect = (
                lambda key, default=None, required=False, cast_type=None: {
                    "DEBUG_MODE": True,
                    "AGENT_ID": None,
                }.get(key, default)
            )
            agent = AgentClient()
            out = await agent.process_message_async("no network")
            assert out == "no network"


@pytest.mark.unit
@pytest.mark.asyncio
class TestProcessMessageAsyncNonTimeoutErrorsStillReturnNone:
    """Errors that are not ``asyncio.wait_for`` stream timeouts keep ``None`` (queue may requeue)."""

    async def test_stream_raises_immediately_fallback_returns_none(self) -> None:
        def broken_stream():
            if False:
                yield None
            raise ValueError("stream corrupt")

        with patch("runtime.core.agent.get_env_var") as ge:
            ge.side_effect = (
                lambda key, default=None, required=False, cast_type=None: {
                    "DEBUG_MODE": False,
                    "AGENT_ID": "test-agent",
                    "LONG_TASK_MAX_WAIT": "600",
                }.get(key, default)
            )
            with patch("runtime.core.agent.get_letta_client") as mock_get_client:
                mock_client = MagicMock()
                mock_get_client.return_value = mock_client
                mock_client.agents.messages.create.return_value = broken_stream()

                with patch.object(
                    AgentClient, "_fallback_to_async", new_callable=AsyncMock
                ) as mock_fb:
                    mock_fb.return_value = None
                    agent = AgentClient()
                    out = await agent.process_message_async("x")
                    assert out is None


@pytest.mark.unit
@pytest.mark.asyncio
class TestProcessMessageAsyncNoTimeoutPathUnchanged:
    async def test_stream_completes_with_assistant_content_no_fallback(self) -> None:
        """Fast stream with assistant text must not hit ``AgentTurnTimeoutInFlight``."""

        def stream_one_assistant():
            ev = MagicMock()
            ev.message_type = "assistant_message"
            ev.content = "quick reply"
            ev.id = "mid-1"
            ev.conversation_id = None
            yield ev

        with patch("runtime.core.agent.get_env_var", side_effect=lambda k, d=None, **kw: {
            "DEBUG_MODE": False,
            "AGENT_ID": "test-agent",
            "LONG_TASK_MAX_WAIT": "600",
        }.get(k, d)):
            with patch("runtime.core.agent.get_letta_client") as mock_get_client:
                mock_client = MagicMock()
                mock_get_client.return_value = mock_client
                mock_client.agents.messages.create.return_value = stream_one_assistant()

                agent = AgentClient()
                with patch.object(
                    AgentClient, "_fallback_to_async", new_callable=AsyncMock
                ) as fb:
                    out = await agent.process_message_async("hi")
                    assert out == "quick reply"
                    fb.assert_not_awaited()
