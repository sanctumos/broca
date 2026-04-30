"""
Exhaustive tests: no Letta turn requeue on wall-clock timeouts while work may continue.

Covers ``QueueProcessor._process_single_message`` and ``_process_with_core_block`` paths
that interact with ``asyncio.TimeoutError`` and ``AgentTurnTimeoutInFlight``.
"""

from __future__ import annotations

import inspect
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.exceptions import AgentTurnTimeoutInFlight
from runtime.core.queue import QueueProcessor


def _discard_unawaited_coroutine(awaitable: object) -> None:
    """Avoid RuntimeWarning when tests short-circuit ``asyncio.wait_for`` without awaiting."""
    if inspect.isawaitable(awaitable):
        close = getattr(awaitable, "close", None)
        if callable(close):
            try:
                close()
            except (RuntimeError, GeneratorExit):
                pass


@pytest.fixture(autouse=True)
def _mock_letta_client() -> None:
    with patch("runtime.core.queue.get_letta_client", return_value=MagicMock()):
        yield


def _queue_item(
    qid: int = 42,
    message_id: int = 7,
    letta_user_id: int = 3,
    attempts: int = 0,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=qid,
        message_id=message_id,
        letta_user_id=letta_user_id,
        attempts=attempts,
    )


@pytest.fixture
def live_queue_deps() -> None:
    """Minimal happy-path DB + profile chain for live-mode message processing."""
    with (
        patch(
            "runtime.core.queue.get_message_text",
            new_callable=AsyncMock,
            return_value=("user", "hello world"),
        ),
        patch(
            "runtime.core.queue.get_user_details",
            new_callable=AsyncMock,
            return_value=("Display", "user1"),
        ),
        patch(
            "runtime.core.queue.get_platform_profile_id",
            new_callable=AsyncMock,
            return_value=(99, "plat-user"),
        ),
        # Imported inside ``_process_single_message``; patch at source module.
        patch(
            "database.operations.users.get_platform_profile",
            new_callable=AsyncMock,
        ) as gp,
        patch(
            "runtime.core.queue.update_message_with_response",
            new_callable=AsyncMock,
        ),
        patch(
            "runtime.core.queue.update_queue_status",
            new_callable=AsyncMock,
        ),
        patch(
            "runtime.core.queue.requeue_failed_item",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch(
            "runtime.core.queue.QueueProcessor._route_response",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch("runtime.core.queue.asyncio.sleep", new_callable=AsyncMock),
    ):
        prof = MagicMock()
        prof.platform = "telegram"
        gp.return_value = prof
        yield


@pytest.mark.unit
@pytest.mark.asyncio
class TestQueueOuterTimeoutNoRequeue:
    async def test_message_process_timeout_raises_no_requeue(
        self, live_queue_deps: None
    ) -> None:
        """``asyncio.TimeoutError`` from outer ``wait_for`` → failed, never ``requeue_failed_item``."""

        async def boom_wait_for(coro, timeout=None):  # noqa: ARG002
            _discard_unawaited_coroutine(coro)
            raise TimeoutError()

        async def mp(_m: str, sender_id: str | None = None) -> str:  # pragma: no cover
            raise AssertionError("message_processor must not run")

        with patch.dict("os.environ", {"AGENT_ID": "agent-x"}):
            p = QueueProcessor(mp, message_mode="live")
        with patch("runtime.core.queue.asyncio.wait_for", side_effect=boom_wait_for):
            with patch(
                "runtime.core.queue.requeue_failed_item", new_callable=AsyncMock
            ) as rq_mock:
                with patch(
                    "runtime.core.queue.update_queue_status", new_callable=AsyncMock
                ) as uq:
                    await p._process_single_message(_queue_item())
        uq.assert_awaited_once_with(42, "failed")
        rq_mock.assert_not_awaited()

    async def test_outer_timeout_update_queue_raises_still_no_requeue(
        self, live_queue_deps: None
    ) -> None:
        """DB failure while marking failed must not fall through to generic requeue."""

        async def boom_wait_for(coro, timeout=None):  # noqa: ARG002
            _discard_unawaited_coroutine(coro)
            raise TimeoutError()

        async def mp(_m: str, sender_id: str | None = None) -> str:  # pragma: no cover
            raise AssertionError("no processor")

        with patch.dict("os.environ", {"AGENT_ID": "agent-x"}):
            p = QueueProcessor(mp, message_mode="live")
        with patch("runtime.core.queue.asyncio.wait_for", side_effect=boom_wait_for):
            rq_mod = "runtime.core.queue.requeue_failed_item"
            with patch(rq_mod, new_callable=AsyncMock) as rq_mock:
                with patch(
                    "runtime.core.queue.update_queue_status",
                    new_callable=AsyncMock,
                    side_effect=RuntimeError("db down"),
                ):
                    await p._process_single_message(_queue_item())
        rq_mock.assert_not_awaited()


@pytest.mark.unit
@pytest.mark.asyncio
class TestQueueAgentTurnTimeoutInFlightNoRequeue:
    async def test_inflight_timeout_inner_handler(
        self, live_queue_deps: None
    ) -> None:
        """``AgentTurnTimeoutInFlight`` from awaited core block → failed, no requeue."""

        async def passthrough_wait_for(coro, timeout=None):  # noqa: ARG002
            return await coro

        with patch.dict("os.environ", {"AGENT_ID": "agent-x"}):
            p = QueueProcessor(AsyncMock(), message_mode="live")

        async def core_raises(*_a, **_k):
            raise AgentTurnTimeoutInFlight("from core")

        p._process_with_core_block = core_raises  # type: ignore[method-assign]

        with patch(
            "runtime.core.queue.asyncio.wait_for", side_effect=passthrough_wait_for
        ):
            with patch(
                "runtime.core.queue.requeue_failed_item", new_callable=AsyncMock
            ) as rq_mock:
                with patch(
                    "runtime.core.queue.update_queue_status", new_callable=AsyncMock
                ) as uq:
                    await p._process_single_message(_queue_item())
        uq.assert_awaited_once_with(42, "failed")
        rq_mock.assert_not_awaited()

    async def test_inflight_update_queue_raises_still_no_requeue(
        self, live_queue_deps: None
    ) -> None:
        async def passthrough_wait_for(coro, timeout=None):  # noqa: ARG002
            return await coro

        async def core_raises(*_a, **_k):
            raise AgentTurnTimeoutInFlight("x")

        with patch.dict("os.environ", {"AGENT_ID": "agent-x"}):
            p = QueueProcessor(AsyncMock(), message_mode="live")
        p._process_with_core_block = core_raises  # type: ignore[method-assign]

        with patch(
            "runtime.core.queue.asyncio.wait_for", side_effect=passthrough_wait_for
        ):
            with patch(
                "runtime.core.queue.requeue_failed_item", new_callable=AsyncMock
            ) as rq_mock:
                with patch(
                    "runtime.core.queue.update_queue_status",
                    new_callable=AsyncMock,
                    side_effect=OSError("disk full"),
                ):
                    await p._process_single_message(_queue_item(attempts=3))
        rq_mock.assert_not_awaited()


@pytest.mark.unit
@pytest.mark.asyncio
class TestQueueBeltAndSuspendersInflight:
    async def test_inflight_escape_from_formatter_still_no_requeue(
        self, live_queue_deps: None
    ) -> None:
        """If ``AgentTurnTimeoutInFlight`` leaks past inner handler, outer belt catches."""

        with patch.dict("os.environ", {"AGENT_ID": "agent-x"}):
            p = QueueProcessor(AsyncMock(), message_mode="live")

        with patch.object(
            p.formatter,
            "format_message",
            side_effect=AgentTurnTimeoutInFlight("from formatter"),
        ):
            with patch(
                "runtime.core.queue.requeue_failed_item", new_callable=AsyncMock
            ) as rq_mock:
                with patch(
                    "runtime.core.queue.update_queue_status", new_callable=AsyncMock
                ) as uq:
                    await p._process_single_message(_queue_item(qid=99))
        uq.assert_awaited_once_with(99, "failed")
        rq_mock.assert_not_awaited()


@pytest.mark.unit
@pytest.mark.asyncio
class TestQueueNormalNoneResponseStillRequeues:
    async def test_core_returns_none_failed_requeues(
        self, live_queue_deps: None
    ) -> None:
        """Completed turn with no assistant text → existing backoff + requeue."""

        async def passthrough_wait_for(coro, timeout=None):  # noqa: ARG002
            return await coro

        async def core_none(*_a, **_k):
            return None, "failed"

        with patch.dict("os.environ", {"AGENT_ID": "agent-x"}):
            p = QueueProcessor(AsyncMock(), message_mode="live")
        p._process_with_core_block = core_none  # type: ignore[method-assign]

        with patch(
            "runtime.core.queue.asyncio.wait_for", side_effect=passthrough_wait_for
        ):
            with patch(
                "runtime.core.queue.requeue_failed_item", new_callable=AsyncMock
            ) as rq_mock:
                await p._process_single_message(_queue_item(attempts=1))
        rq_mock.assert_awaited_once_with(42)


@pytest.mark.unit
@pytest.mark.asyncio
class TestQueueSuccessPath:
    async def test_success_updates_message_queue_and_routes(
        self, live_queue_deps: None
    ) -> None:
        async def passthrough_wait_for(coro, timeout=None):  # noqa: ARG002
            return await coro

        async def core_ok(*_a, **_k):
            return "assistant says hi", "completed"

        with patch.dict("os.environ", {"AGENT_ID": "agent-x"}):
            p = QueueProcessor(AsyncMock(), message_mode="live")
        p._process_with_core_block = core_ok  # type: ignore[method-assign]

        with patch(
            "runtime.core.queue.asyncio.wait_for", side_effect=passthrough_wait_for
        ):
            with patch(
                "runtime.core.queue.update_message_with_response",
                new_callable=AsyncMock,
            ) as um:
                with patch(
                    "runtime.core.queue.update_queue_status", new_callable=AsyncMock
                ) as uq:
                    with patch(
                        "runtime.core.queue.requeue_failed_item",
                        new_callable=AsyncMock,
                    ) as rq:
                        with patch.object(
                            p, "_route_response", new_callable=AsyncMock
                        ) as route:
                            await p._process_single_message(_queue_item())
        um.assert_awaited_once_with(7, "assistant says hi")
        uq.assert_awaited_once_with(42, "completed")
        route.assert_awaited_once_with(7, "assistant says hi")
        rq.assert_not_awaited()


@pytest.mark.unit
@pytest.mark.asyncio
class TestQueueEchoMode:
    async def test_echo_never_invokes_wait_for(self, live_queue_deps: None) -> None:
        with patch.dict("os.environ", {"AGENT_ID": "agent-x"}):
            p = QueueProcessor(AsyncMock(), message_mode="echo")

        async def forbidden_wait_for(_c, timeout=None):  # noqa: ANN001, ARG002
            raise AssertionError("echo mode must not wrap agent in wait_for")

        with patch("runtime.core.queue.asyncio.wait_for", side_effect=forbidden_wait_for):
            with patch(
                "runtime.core.queue.requeue_failed_item", new_callable=AsyncMock
            ) as rq:
                with patch(
                    "runtime.core.queue.update_message_with_response",
                    new_callable=AsyncMock,
                ) as um:
                    with patch(
                        "runtime.core.queue.update_queue_status",
                        new_callable=AsyncMock,
                    ) as uq:
                        with patch.object(
                            p, "_route_response", new_callable=AsyncMock
                        ) as route:
                            await p._process_single_message(_queue_item())
        rq.assert_not_awaited()
        um.assert_awaited_once()
        uq.assert_awaited_once_with(42, "completed")
        route.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
class TestQueueMessageProcessTimeoutFloor:
    async def test_timeout_floor_covers_long_task_plus_buffer(
        self, live_queue_deps: None
    ) -> None:
        """``timeout_seconds = max(LONG_TASK_MAX_WAIT + BUFFER, MESSAGE_PROCESS_TIMEOUT)``."""

        timeouts: list[float] = []

        async def record_wait_for(coro, timeout=None):  # noqa: ARG002
            _discard_unawaited_coroutine(coro)
            timeouts.append(timeout)
            raise TimeoutError()

        async def mp(_m: str, sender_id: str | None = None) -> str:  # pragma: no cover
            raise AssertionError("no")

        def fake_get_env(
            key: str,
            default: str | None = None,
            required: bool = False,
            cast_type=None,
        ):
            if key == "MESSAGE_PROCESS_TIMEOUT":
                return "60"
            if key == "LONG_TASK_MAX_WAIT":
                return "600"
            if key == "MESSAGE_PROCESS_TIMEOUT_BUFFER":
                return "180"
            if key == "AGENT_ID":
                return "agent-x"
            return default

        with patch.dict("os.environ", {"AGENT_ID": "agent-x"}):
            p = QueueProcessor(mp, message_mode="live")
        with patch("runtime.core.queue.get_env_var", side_effect=fake_get_env):
            with patch(
                "runtime.core.queue.asyncio.wait_for", side_effect=record_wait_for
            ):
                with patch(
                    "runtime.core.queue.requeue_failed_item", new_callable=AsyncMock
                ):
                    with patch(
                        "runtime.core.queue.update_queue_status",
                        new_callable=AsyncMock,
                    ):
                        await p._process_single_message(_queue_item())
        assert timeouts == [780]

    async def test_timeout_uses_config_when_above_floor(
        self, live_queue_deps: None
    ) -> None:
        """Configured ``MESSAGE_PROCESS_TIMEOUT`` above floor must win."""
        timeouts: list[int | float | None] = []

        async def record_wait_for(coro, timeout=None):  # noqa: ARG002
            _discard_unawaited_coroutine(coro)
            timeouts.append(timeout)
            raise TimeoutError()

        async def mp(_m: str, sender_id: str | None = None) -> str:  # pragma: no cover
            raise AssertionError("no")

        def fake_get_env(
            key: str,
            default: str | None = None,
            required: bool = False,
            cast_type=None,
        ):
            if key == "MESSAGE_PROCESS_TIMEOUT":
                return "900"
            if key == "LONG_TASK_MAX_WAIT":
                return "600"
            if key == "MESSAGE_PROCESS_TIMEOUT_BUFFER":
                return "180"
            if key == "AGENT_ID":
                return "agent-x"
            return default

        with patch.dict("os.environ", {"AGENT_ID": "agent-x"}):
            p = QueueProcessor(mp, message_mode="live")
        with patch("runtime.core.queue.get_env_var", side_effect=fake_get_env):
            with patch(
                "runtime.core.queue.asyncio.wait_for", side_effect=record_wait_for
            ):
                with patch(
                    "runtime.core.queue.requeue_failed_item", new_callable=AsyncMock
                ):
                    with patch(
                        "runtime.core.queue.update_queue_status",
                        new_callable=AsyncMock,
                    ):
                        await p._process_single_message(_queue_item())
        assert timeouts == [900]


@pytest.mark.unit
@pytest.mark.asyncio
class TestQueueGenericExceptionStillRequeues:
    async def test_runtime_error_from_wait_for_path_requeues(
        self, live_queue_deps: None
    ) -> None:
        async def boom_wait_for(coro, timeout=None):  # noqa: ARG002
            _discard_unawaited_coroutine(coro)
            raise RuntimeError("unexpected")

        async def mp(_m: str, sender_id: str | None = None) -> str:  # pragma: no cover
            raise AssertionError("no")

        with patch.dict("os.environ", {"AGENT_ID": "agent-x"}):
            p = QueueProcessor(mp, message_mode="live")
        with patch("runtime.core.queue.asyncio.wait_for", side_effect=boom_wait_for):
            with patch(
                "runtime.core.queue.requeue_failed_item", new_callable=AsyncMock
            ) as rq:
                await p._process_single_message(_queue_item())
        rq.assert_awaited_once_with(42)


@pytest.mark.unit
@pytest.mark.asyncio
class TestQueuePostSuccessPersistenceFailure:
    """Failures after a successful agent tuple still use generic requeue (not timeout-in-flight)."""

    async def test_update_message_raises_triggers_requeue(
        self, live_queue_deps: None
    ) -> None:
        async def passthrough_wait_for(coro, timeout=None):  # noqa: ARG002
            return await coro

        async def core_ok(*_a, **_k):
            return "assistant ok", "completed"

        with patch.dict("os.environ", {"AGENT_ID": "agent-x"}):
            p = QueueProcessor(AsyncMock(), message_mode="live")
        p._process_with_core_block = core_ok  # type: ignore[method-assign]

        with patch(
            "runtime.core.queue.asyncio.wait_for", side_effect=passthrough_wait_for
        ):
            with patch(
                "runtime.core.queue.update_message_with_response",
                new_callable=AsyncMock,
                side_effect=RuntimeError("sqlite locked"),
            ) as um:
                with patch(
                    "runtime.core.queue.requeue_failed_item", new_callable=AsyncMock
                ) as rq:
                    await p._process_single_message(_queue_item())
        um.assert_awaited_once()
        rq.assert_awaited_once_with(42)


@pytest.mark.unit
@pytest.mark.asyncio
class TestProcessWithCoreBlockDetachOnInflight:
    async def test_detach_called_then_reraises(self) -> None:
        attach_detach = AsyncMock(return_value=None)

        async def mp(_m: str, sender_id: str | None = None) -> str:
            raise AgentTurnTimeoutInFlight("letta")

        with patch.dict("os.environ", {"AGENT_ID": "agent-x"}):
            p = QueueProcessor(mp, message_mode="live")

        with (
            patch(
                "runtime.core.queue.get_letta_user_block_id",
                new_callable=AsyncMock,
                return_value="block-uuid-1234",
            ),
            patch(
                "runtime.core.queue.get_letta_identity_id",
                new_callable=AsyncMock,
                return_value="ident-1",
            ),
            patch("runtime.core.queue.asyncio.to_thread", attach_detach),
        ):
            with pytest.raises(AgentTurnTimeoutInFlight, match="letta"):
                await p._process_with_core_block("msg", letta_user_id=1)

        # attach + detach on in-flight path (order: attach, then detach after timeout)
        assert attach_detach.await_count >= 2

    async def test_detach_failure_still_reraises_inflight(self) -> None:
        call_n = 0

        async def flaky_to_thread(fn, *args, **kwargs):  # noqa: ANN001
            nonlocal call_n
            call_n += 1
            if "detach" in getattr(fn, "__name__", str(fn)):
                raise ConnectionError("detach failed")
            return None

        async def mp(_m: str, sender_id: str | None = None) -> str:
            raise AgentTurnTimeoutInFlight("letta")

        with patch.dict("os.environ", {"AGENT_ID": "agent-x"}):
            p = QueueProcessor(mp, message_mode="live")

        with (
            patch(
                "runtime.core.queue.get_letta_user_block_id",
                new_callable=AsyncMock,
                return_value="block-uuid-1234",
            ),
            patch(
                "runtime.core.queue.get_letta_identity_id",
                new_callable=AsyncMock,
                return_value="ident-1",
            ),
            patch("runtime.core.queue.asyncio.to_thread", flaky_to_thread),
        ):
            with pytest.raises(AgentTurnTimeoutInFlight):
                await p._process_with_core_block("m", 1)


@pytest.mark.unit
@pytest.mark.asyncio
class TestQueueOrphanedPathsUnchanged:
    async def test_missing_message_row_requeues(self) -> None:
        with patch.dict("os.environ", {"AGENT_ID": "agent-x"}):
            p = QueueProcessor(AsyncMock(), message_mode="live")
        with patch(
            "runtime.core.queue.get_message_text",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with patch(
                "runtime.core.queue.requeue_failed_item", new_callable=AsyncMock
            ) as rq:
                await p._process_single_message(_queue_item())
        rq.assert_awaited_once_with(42)
