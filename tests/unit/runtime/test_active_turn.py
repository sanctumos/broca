"""Unit tests for sanctum.broca.active-turn lifecycle (Doc #1387 §7)."""

from __future__ import annotations

import json
import stat
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from runtime.core import active_turn as at


@pytest.fixture
def turn_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "active_turn.json"
    monkeypatch.setenv("BROCA_ACTIVE_TURN_FILE", str(path))
    return path


@pytest.mark.unit
def test_write_read_roundtrip(turn_path: Path) -> None:
    tid = at.write_active_turn(
        platform="web_chat",
        broca_message_id=42,
        tasks_user_id=7,
        session_id="sess-abc",
    )
    assert tid.startswith("turn_")
    assert turn_path.is_file()
    mode = stat.S_IMODE(turn_path.stat().st_mode)
    assert mode == 0o600

    data = at.read_active_turn()
    assert data is not None
    assert data["schema"] == at.SCHEMA
    assert data["version"] == at.VERSION
    assert data["turn_id"] == tid
    assert data["platform"] == "web_chat"
    assert data["broca_message_id"] == 42
    assert data["tasks_user_id"] == 7
    assert data["session_id"] == "sess-abc"
    assert "issued_at" in data and "expires_at" in data
    # No message body / credentials keys
    assert "message" not in data
    assert "content" not in data
    assert "password" not in data
    assert "token" not in data


@pytest.mark.unit
def test_write_omits_optional_unknown_fields(turn_path: Path) -> None:
    at.write_active_turn(platform="telegram", broca_message_id=1)
    data = json.loads(turn_path.read_text(encoding="utf-8"))
    assert "tasks_user_id" not in data
    assert "session_id" not in data


@pytest.mark.unit
def test_read_rejects_expired(turn_path: Path) -> None:
    tid = at.write_active_turn(
        platform="web_chat",
        broca_message_id=9,
        ttl=timedelta(minutes=10),
    )
    # Force expires_at into the past
    raw = json.loads(turn_path.read_text(encoding="utf-8"))
    past = datetime.now(timezone.utc) - timedelta(minutes=1)
    raw["expires_at"] = past.isoformat().replace("+00:00", "Z")
    turn_path.write_text(json.dumps(raw), encoding="utf-8")

    assert at.read_active_turn() is None
    # Clear by matching id still works (does not require unexpired)
    assert at.clear_active_turn(tid) is True
    assert not turn_path.exists()


@pytest.mark.unit
def test_read_rejects_bad_schema_or_version(turn_path: Path) -> None:
    at.write_active_turn(platform="web_chat", broca_message_id=1)
    raw = json.loads(turn_path.read_text(encoding="utf-8"))
    raw["schema"] = "other"
    turn_path.write_text(json.dumps(raw), encoding="utf-8")
    assert at.read_active_turn() is None

    at.write_active_turn(platform="web_chat", broca_message_id=1)
    raw = json.loads(turn_path.read_text(encoding="utf-8"))
    raw["version"] = 99
    turn_path.write_text(json.dumps(raw), encoding="utf-8")
    assert at.read_active_turn() is None


@pytest.mark.unit
def test_clear_matching_turn_id(turn_path: Path) -> None:
    tid = at.write_active_turn(platform="web_chat", broca_message_id=3)
    assert at.clear_active_turn(tid) is True
    assert not turn_path.exists()
    assert at.read_active_turn() is None


@pytest.mark.unit
def test_stale_clear_is_noop(turn_path: Path) -> None:
    tid = at.write_active_turn(platform="web_chat", broca_message_id=3)
    assert at.clear_active_turn("turn_someone_else") is False
    assert turn_path.is_file()
    data = at.read_active_turn()
    assert data is not None
    assert data["turn_id"] == tid


@pytest.mark.unit
def test_relative_path_under_run_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    monkeypatch.setenv("BROCA_RUN_DIR", str(run_dir))
    monkeypatch.setenv("BROCA_ACTIVE_TURN_FILE", "active_turn.json")
    resolved = at.resolve_active_turn_path()
    assert resolved == run_dir / "active_turn.json"
    tid = at.write_active_turn(platform="web_chat", broca_message_id=5)
    assert resolved.is_file()
    assert at.clear_active_turn(tid) is True


@pytest.mark.unit
def test_extract_turn_ids_from_profile_metadata() -> None:
    uid, sid = at.extract_turn_ids_from_profile_metadata(
        {"tasks_user_id": 12, "session_id": "s1"},
        platform_user_id="tasks:12",
    )
    assert uid == 12
    assert sid == "s1"

    uid, sid = at.extract_turn_ids_from_profile_metadata(
        None, platform_user_id="tasks:99"
    )
    assert uid == 99
    assert sid is None

    uid, sid = at.extract_turn_ids_from_profile_metadata(
        json.dumps({"tasks_user_id": "3", "session_id": "x"}),
    )
    assert uid == 3
    assert sid == "x"


@pytest.mark.unit
def test_maybe_set_tasks_user_id_preserves_ttl(turn_path: Path) -> None:
    tid = at.write_active_turn(platform="web_chat", broca_message_id=8)
    before = json.loads(turn_path.read_text(encoding="utf-8"))
    assert at.maybe_set_tasks_user_id(55) is True
    after = json.loads(turn_path.read_text(encoding="utf-8"))
    assert after["turn_id"] == tid
    assert after["tasks_user_id"] == 55
    assert after["issued_at"] == before["issued_at"]
    assert after["expires_at"] == before["expires_at"]


@pytest.mark.unit
def test_default_path_when_env_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BROCA_ACTIVE_TURN_FILE", raising=False)
    assert at.resolve_active_turn_path() == Path(at.DEFAULT_ACTIVE_TURN_FILE)
