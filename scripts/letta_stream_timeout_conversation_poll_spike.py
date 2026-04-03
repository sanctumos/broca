#!/usr/bin/env python3
"""
Spike REPL: force a short streaming timeout, then inspect Letta via conversation messages.

Use this to learn how "thinking" / long-running models (e.g. DeepSeek) show up on the
conversation API *before* Broca implements Plan B continuation polling.

Env (same names as Broca where possible):
  AGENT_ENDPOINT or LETTA_BASE_URL
  AGENT_API_KEY or LETTA_API_KEY
  AGENT_ID                     — Letta agent id (set to Ada, Athena, or a dev agent)
  SPIKE_STREAM_TIMEOUT_SEC     — default 25 (intentionally short to trigger timeout)
  SPIKE_SENDER_ID              — optional Letta identity id (scopes thread like Broca)

See: docs/broca-3.1-streaming-timeout-continuation-planning.md

Copyright (c) 2026 Mark Rizzn Hopkins / Sanctum OS
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import uuid
from typing import Any

try:
    from letta_client import Letta
except ImportError as e:
    print("Install Letta SDK in this environment: pip install letta-client", file=sys.stderr)
    raise SystemExit(1) from e


def _env(name: str, *alts: str, default: str | None = None) -> str | None:
    for k in (name, *alts):
        v = os.environ.get(k)
        if v:
            return v
    return default


def _serialize(obj: Any, depth: int = 0) -> Any:
    if depth > 8:
        return "…"
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _serialize(v, depth + 1) for k, v in list(obj.items())[:60]}
    if isinstance(obj, (list, tuple)):
        return [_serialize(x, depth + 1) for x in obj[:80]]
    if hasattr(obj, "model_dump"):
        try:
            return _serialize(obj.model_dump(), depth + 1)
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        return {
            k: _serialize(v, depth + 1)
            for k, v in vars(obj).items()
            if not k.startswith("_")
        }
    return repr(obj)[:400]


def _user_messages(text: str, sender_id: str | None) -> list[dict]:
    m: dict[str, Any] = {"role": "user", "content": text, "otid": str(uuid.uuid4())}
    if sender_id:
        m["sender_id"] = sender_id
    return [m]


def _extract_conversation_id_from_event(event: Any) -> str | None:
    if hasattr(event, "conversation_id") and event.conversation_id:
        return str(event.conversation_id)
    if hasattr(event, "conversation") and getattr(event.conversation, "id", None):
        return str(event.conversation.id)
    if hasattr(event, "run") and getattr(event.run, "conversation_id", None):
        return str(event.run.conversation_id)
    if hasattr(event, "data") and getattr(event.data, "conversation_id", None):
        return str(event.data.conversation_id)
    return None


def _event_brief(event: Any) -> dict[str, Any]:
    mt = getattr(event, "message_type", None)
    cid = _extract_conversation_id_from_event(event)
    rid = None
    if hasattr(event, "run") and event.run is not None:
        rid = getattr(event.run, "id", None)
    return {
        "message_type": mt,
        "conversation_id": cid,
        "run_id": str(rid) if rid else None,
        "id": getattr(event, "id", None),
    }


async def _consume_stream(
    stream: Any, state: dict[str, Any]
) -> None:
    loop = asyncio.get_running_loop()

    def _next() -> tuple[bool, Any]:
        it = state["_iterator"]
        try:
            return True, next(it)
        except StopIteration:
            return False, None

    state["_iterator"] = iter(stream)
    while True:
        ok, event = await loop.run_in_executor(None, _next)
        if not ok:
            break
        state["events"].append(event)
        cid = _extract_conversation_id_from_event(event)
        if cid and not state["conversation_id"]:
            state["conversation_id"] = cid
        if getattr(event, "message_type", None) in ("assistant_message", "assistant"):
            if hasattr(event, "id") and event.id:
                state["message_id"] = str(event.id)


async def spike_turn(
    client: Letta,
    agent_id: str,
    text: str,
    sender_id: str | None,
    timeout_sec: float,
) -> None:
    messages = _user_messages(text, sender_id)
    state: dict[str, Any] = {
        "conversation_id": None,
        "message_id": None,
        "events": [],
    }

    def _open_stream() -> Any:
        try:
            return client.agents.messages.create(
                agent_id,
                messages=messages,
                streaming=True,
                background=True,
                include_pings=True,
            )
        except (TypeError, AttributeError):
            return client.agents.messages.create_stream(
                agent_id,
                messages=messages,
                include_pings=True,
            )

    stream = await asyncio.to_thread(_open_stream)

    try:
        await asyncio.wait_for(_consume_stream(stream, state), timeout=timeout_sec)
        print("\n--- Stream finished within timeout (no TimeoutError). ---\n")
    except asyncio.TimeoutError:
        print(
            f"\n*** SPIKE: asyncio.TimeoutError after {timeout_sec}s "
            "(local wait — model may still be thinking) ***\n"
        )

    print("Captured conversation_id:", state["conversation_id"])
    print("Captured assistant message_id (if any):", state["message_id"])
    print("Stream events seen:", len(state["events"]))
    if state["events"]:
        tail = state["events"][-8:]
        print("Last events (brief):")
        for i, ev in enumerate(tail, start=len(state["events"]) - len(tail)):
            print(f"  [{i}]", json.dumps(_serialize(_event_brief(ev)), indent=2))

    cid = state["conversation_id"]
    if cid:
        print(f"\n--- conversations.messages.list({cid!r}, order='desc', limit=20) ---\n")
        try:
            resp = await asyncio.to_thread(
                client.conversations.messages.list,
                cid,
                order="desc",
                limit=20,
            )
            print(json.dumps(_serialize(resp), indent=2))
        except Exception as ex:
            print("conversation poll failed:", ex)
    else:
        print("\n(No conversation_id yet — trying agents.messages.list fallback.)\n")
        try:
            resp = await asyncio.to_thread(
                client.agents.messages.list,
                agent_id,
                limit=20,
            )
            print(json.dumps(_serialize(resp), indent=2))
        except Exception as ex:
            print("agents.messages.list failed:", ex)

    if state["message_id"]:
        print(
            f"\n--- messages.retrieve (if SDK supports) id={state['message_id']!r} ---\n"
        )
        try:
            msg = await asyncio.to_thread(client.messages.retrieve, state["message_id"])
            print(json.dumps(_serialize(msg), indent=2))
        except Exception as ex:
            print("messages.retrieve skipped or failed:", ex)


def _build_client() -> tuple[Letta, str]:
    base = _env("AGENT_ENDPOINT", "LETTA_BASE_URL")
    key = _env("AGENT_API_KEY", "LETTA_API_KEY")
    agent_id = _env("AGENT_ID", "LETTA_SPIKE_AGENT_ID")
    if not base or not key or not agent_id:
        print(
            "Set AGENT_ENDPOINT (or LETTA_BASE_URL), "
            "AGENT_API_KEY (or LETTA_API_KEY), AGENT_ID (or LETTA_SPIKE_AGENT_ID).",
            file=sys.stderr,
        )
        raise SystemExit(2)
    try:
        return Letta(base_url=base, token=key, timeout=120.0), agent_id
    except TypeError:
        return Letta(base_url=base, api_key=key, max_retries=0), agent_id


async def _async_main(args: argparse.Namespace) -> None:
    client, agent_id = _build_client()
    timeout_sec = float(
        args.timeout
        if args.timeout is not None
        else _env("SPIKE_STREAM_TIMEOUT_SEC", default="25")
    )
    sender_id = _env("SPIKE_SENDER_ID")

    if args.message:
        await spike_turn(client, agent_id, args.message, sender_id, timeout_sec)
        return

    print(
        "Letta stream timeout → conversation poll spike.\n"
        f"agent_id={agent_id!r} timeout={timeout_sec}s\n"
        "Type a message (empty line exits).\n"
    )
    while True:
        try:
            line = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            break
        await spike_turn(client, agent_id, line, sender_id, timeout_sec)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=None,
        help="Stream consume timeout seconds (default env SPIKE_STREAM_TIMEOUT_SEC or 25)",
    )
    p.add_argument(
        "-m",
        "--message",
        default=None,
        help="Single shot: send this message and exit (still uses short timeout)",
    )
    args = p.parse_args()
    asyncio.run(_async_main(args))


if __name__ == "__main__":
    main()
