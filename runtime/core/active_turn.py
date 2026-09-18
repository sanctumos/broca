"""Turn-scoped active-turn context for Broca (Doc #1387 §7).

Writes a small JSON sidecar immediately before AgentClient / Letta processing
so sibling tools (e.g. SMCP) can bind to the in-flight webchat turn.

Contract schema: ``sanctum.broca.active-turn`` v1.
No credentials or message body — ids and platform only.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SCHEMA = "sanctum.broca.active-turn"
VERSION = 1
DEFAULT_TTL = timedelta(minutes=10)
DEFAULT_ACTIVE_TURN_FILE = "/opt/broca-q/run/active_turn.json"
DEFAULT_RUN_DIR = "/opt/broca-q/run"


def resolve_active_turn_path() -> Path:
    """Resolve the active-turn JSON path.

    ``BROCA_ACTIVE_TURN_FILE``:
      - absolute → used as-is
      - relative → joined under ``BROCA_RUN_DIR`` (default ``/opt/broca-q/run``)
      - unset → ``/opt/broca-q/run/active_turn.json``
    """
    raw = (os.getenv("BROCA_ACTIVE_TURN_FILE") or "").strip()
    if not raw:
        return Path(DEFAULT_ACTIVE_TURN_FILE)
    path = Path(raw)
    if path.is_absolute():
        return path
    run_dir = Path(os.getenv("BROCA_RUN_DIR", DEFAULT_RUN_DIR))
    return run_dir / path


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_iso(value: str) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def new_turn_id() -> str:
    return f"turn_{uuid.uuid4().hex}"


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=".active_turn.",
        suffix=".tmp",
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, separators=(",", ":"), sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp_path, 0o600)
        os.replace(tmp_path, path)
        os.chmod(path, 0o600)
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def write_active_turn(
    *,
    platform: str,
    broca_message_id: int,
    turn_id: str | None = None,
    tasks_user_id: int | None = None,
    session_id: str | None = None,
    ttl: timedelta = DEFAULT_TTL,
    path: Path | None = None,
) -> str:
    """Atomically write the active-turn sidecar. Returns the turn_id used."""
    tid = turn_id or new_turn_id()
    issued = _utcnow()
    expires = issued + ttl
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "turn_id": tid,
        "platform": platform,
        "broca_message_id": int(broca_message_id),
        "issued_at": _iso(issued),
        "expires_at": _iso(expires),
    }
    if tasks_user_id is not None:
        payload["tasks_user_id"] = int(tasks_user_id)
    if session_id:
        payload["session_id"] = str(session_id)

    target = path or resolve_active_turn_path()
    _atomic_write_json(target, payload)
    logger.debug(
        "Wrote active turn %s platform=%s message_id=%s path=%s",
        tid,
        platform,
        broca_message_id,
        target,
    )
    return tid


def read_active_turn(
    *,
    path: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any] | None:
    """Read and validate active-turn JSON. Returns None if missing/invalid/expired."""
    target = path or resolve_active_turn_path()
    if not target.is_file():
        return None
    try:
        raw = target.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Failed to read active turn at %s: %s", target, exc)
        return None

    if not isinstance(data, dict):
        return None
    if data.get("schema") != SCHEMA:
        logger.warning("Active turn schema mismatch at %s: %r", target, data.get("schema"))
        return None
    if data.get("version") != VERSION:
        logger.warning("Active turn version mismatch at %s: %r", target, data.get("version"))
        return None
    if not data.get("turn_id"):
        return None

    expires_at = _parse_iso(str(data.get("expires_at", "")))
    if expires_at is None:
        logger.warning("Active turn missing/invalid expires_at at %s", target)
        return None
    clock = now or _utcnow()
    if clock.tzinfo is None:
        clock = clock.replace(tzinfo=timezone.utc)
    if clock >= expires_at:
        logger.debug("Active turn %s expired at %s", data.get("turn_id"), expires_at)
        return None

    return data


def clear_active_turn(
    turn_id: str,
    *,
    path: Path | None = None,
) -> bool:
    """Remove the active-turn file only if ``turn_id`` matches. Stale clear is a no-op."""
    if not turn_id:
        return False
    target = path or resolve_active_turn_path()
    if not target.is_file():
        return False
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Failed to parse active turn for clear at %s: %s", target, exc)
        return False
    if not isinstance(data, dict) or data.get("turn_id") != turn_id:
        logger.debug(
            "clear_active_turn no-op: file turn_id=%r requested=%r",
            data.get("turn_id") if isinstance(data, dict) else None,
            turn_id,
        )
        return False
    try:
        target.unlink()
    except OSError as exc:
        logger.warning("Failed to unlink active turn %s: %s", target, exc)
        return False
    logger.debug("Cleared active turn %s path=%s", turn_id, target)
    return True


def maybe_set_tasks_user_id(
    tasks_user_id: int,
    *,
    path: Path | None = None,
) -> bool:
    """If a valid active turn exists, rewrite it with ``tasks_user_id`` (Q plugin assist).

    Primary ownership remains queue dequeue ``write_active_turn``. This is a best-effort
    patch when chatter context is published and a turn file is already present.
    Preserves ``issued_at`` / ``expires_at`` / ``turn_id``.
    """
    if tasks_user_id <= 0:
        return False
    current = read_active_turn(path=path)
    if not current:
        return False
    try:
        payload = dict(current)
        payload["tasks_user_id"] = int(tasks_user_id)
        target = path or resolve_active_turn_path()
        _atomic_write_json(target, payload)
        return True
    except Exception as exc:
        logger.warning("maybe_set_tasks_user_id failed: %s", exc)
        return False


def extract_turn_ids_from_profile_metadata(
    metadata: str | dict[str, Any] | None,
    *,
    platform_user_id: str | None = None,
) -> tuple[int | None, str | None]:
    """Pull ``tasks_user_id`` / ``session_id`` from platform_profiles.metadata.

    Gap: Broca ``messages`` rows do not store provider metadata. Q webchat persists
    ``tasks_user_id`` and ``session_id`` on the platform profile metadata JSON (and
    ``platform_user_id`` as ``tasks:{id}``). Profile metadata is updated on each
    inbound message, so ``session_id`` is the latest session for that Tasks user —
    not a per-message column. If metadata is missing, only ``tasks:{id}`` can be
    recovered from ``platform_user_id``.
    """
    tasks_user_id: int | None = None
    session_id: str | None = None
    meta: dict[str, Any] = {}
    if isinstance(metadata, dict):
        meta = metadata
    elif isinstance(metadata, str) and metadata.strip():
        try:
            parsed = json.loads(metadata)
            if isinstance(parsed, dict):
                meta = parsed
        except json.JSONDecodeError:
            meta = {}

    raw_uid = meta.get("tasks_user_id")
    if raw_uid is not None:
        try:
            uid = int(raw_uid)
            if uid > 0:
                tasks_user_id = uid
        except (TypeError, ValueError):
            pass

    raw_session = meta.get("session_id")
    if raw_session:
        session_id = str(raw_session)

    if tasks_user_id is None and platform_user_id:
        text = str(platform_user_id)
        if text.startswith("tasks:"):
            try:
                uid = int(text.split(":", 1)[1])
                if uid > 0:
                    tasks_user_id = uid
            except (TypeError, ValueError):
                pass

    return tasks_user_id, session_id
