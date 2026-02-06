"""Unit tests for runtime.core.image_handling."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

import runtime.core.image_handling as image_handling
from runtime.core.image_handling import (
    build_message_for_agent,
    image_handling_enabled,
    tmpfiles_addendum_enabled,
)


def _reset_env_cache():
    image_handling._ENABLE_IMAGE_HANDLING = None
    image_handling._ENABLE_TMPFILES_IMAGE_ADDENDUM = None


@pytest.mark.unit
def test_image_handling_enabled_default_false():
    """When env is unset or false, image_handling_enabled is False."""
    _reset_env_cache()
    with patch("runtime.core.image_handling.get_env_var", return_value="false"):
        _reset_env_cache()
        assert image_handling_enabled() is False
    with patch("runtime.core.image_handling.get_env_var", return_value="true"):
        _reset_env_cache()
        assert image_handling_enabled() is True


@pytest.mark.unit
def test_tmpfiles_addendum_enabled_default_false():
    """When env is unset or false, tmpfiles_addendum_enabled is False."""
    _reset_env_cache()
    with patch("runtime.core.image_handling.get_env_var", return_value="false"):
        _reset_env_cache()
        assert tmpfiles_addendum_enabled() is False
    with patch("runtime.core.image_handling.get_env_var", return_value="true"):
        _reset_env_cache()
        assert tmpfiles_addendum_enabled() is True


@pytest.mark.unit
def test_build_message_for_agent_image_handling_off_returns_sanitized_text_only():
    """When image handling is off, return only sanitized text."""
    _reset_env_cache()
    with patch("runtime.core.image_handling.get_env_var", return_value="false"):
        _reset_env_cache()
        result = build_message_for_agent("  hello  world  ", [Path("/some/photo.png")])
    assert result == "hello world"
    assert "[Image Attachment:" not in result


@pytest.mark.unit
def test_build_message_for_agent_no_paths_returns_sanitized_text():
    """When image_paths is None or empty, return only sanitized text."""
    _reset_env_cache()
    with patch(
        "runtime.core.image_handling.get_env_var",
        side_effect=lambda n, **kw: "true" if "IMAGE" in n else kw.get("default", ""),
    ):
        _reset_env_cache()
        result = build_message_for_agent("caption", None)
        assert result == "caption"
        result = build_message_for_agent("caption", [])
        assert result == "caption"


@pytest.mark.unit
def test_build_message_for_agent_tmpfiles_off_returns_sanitized_text_only():
    """When image handling on but tmpfiles addendum off, no upload, text only."""
    _reset_env_cache()

    def env_get(name, default=None, **kwargs):
        if name == "ENABLE_IMAGE_HANDLING":
            return "true"
        if name == "ENABLE_TMPFILES_IMAGE_ADDENDUM":
            return "false"
        return default

    with patch("runtime.core.image_handling.get_env_var", side_effect=env_get):
        _reset_env_cache()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"\x89PNG")
            path = Path(f.name)
        try:
            result = build_message_for_agent("caption", [path])
            assert result == "caption"
            assert "[Image Attachment:" not in result
        finally:
            path.unlink(missing_ok=True)


@pytest.mark.unit
def test_build_message_for_agent_tmpfiles_on_appends_addendum():
    """When both flags on and paths given, upload and append [Image Attachment: url]."""
    _reset_env_cache()

    def env_get(name, default=None, **kwargs):
        if name == "ENABLE_IMAGE_HANDLING":
            return "true"
        if name == "ENABLE_TMPFILES_IMAGE_ADDENDUM":
            return "true"
        return default

    with patch("runtime.core.image_handling.get_env_var", side_effect=env_get):
        _reset_env_cache()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"\x89PNG")
            path = Path(f.name)
        try:
            with patch(
                "runtime.core.image_handling.tmpfiles_upload_file",
                return_value="https://tmpfiles.org/dl/1/photo.png",
            ):
                result = build_message_for_agent("caption", [path])
            assert result.startswith("caption\n")
            assert "[Image Attachment: https://tmpfiles.org/dl/1/photo.png]" in result
        finally:
            path.unlink(missing_ok=True)


@pytest.mark.unit
def test_build_message_for_agent_upload_failure_logs_and_skips():
    """When tmpfiles upload fails, log and skip that image; rest of message remains."""
    _reset_env_cache()

    def env_get(name, default=None, **kwargs):
        if name == "ENABLE_IMAGE_HANDLING":
            return "true"
        if name == "ENABLE_TMPFILES_IMAGE_ADDENDUM":
            return "true"
        return default

    with patch("runtime.core.image_handling.get_env_var", side_effect=env_get):
        _reset_env_cache()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"\x89PNG")
            path = Path(f.name)
        try:
            with patch(
                "runtime.core.image_handling.tmpfiles_upload_file",
                side_effect=RuntimeError("upload failed"),
            ):
                with patch("runtime.core.image_handling.logger") as mock_logger:
                    result = build_message_for_agent("caption", [path])
            assert result == "caption"
            mock_logger.warning.assert_called()
        finally:
            path.unlink(missing_ok=True)


@pytest.mark.unit
def test_build_message_for_agent_none_text_sanitized_to_empty():
    """None or empty text is sanitized to empty string."""
    _reset_env_cache()
    with patch("runtime.core.image_handling.get_env_var", return_value="false"):
        _reset_env_cache()
        result = build_message_for_agent(None, None)
        assert result == ""
        result = build_message_for_agent("", None)
        assert result == ""
