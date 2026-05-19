"""Unit tests for common.ephemeral_upload (tmpfiles + sanctum fallback)."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from common.ephemeral_upload import (
    SANCTUM_TMP_UPLOAD_URL,
    upload_file,
    view_url_to_direct_url,
)


@pytest.mark.unit
def test_view_url_sanctum_host():
    view = "https://tmp.sanctumos.org/Ab12cd34/photo.jpg"
    assert view_url_to_direct_url(view) == "https://tmp.sanctumos.org/dl/Ab12cd34/photo.jpg"


@pytest.mark.unit
def test_upload_file_uses_tmpfiles_when_primary_ok():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"\x89PNG")
        path = Path(f.name)
    try:
        with patch("common.ephemeral_upload._tmpfiles.upload_file", return_value="https://tmpfiles.org/dl/x/y.png") as m:
            assert upload_file(path) == "https://tmpfiles.org/dl/x/y.png"
            m.assert_called_once()
    finally:
        path.unlink(missing_ok=True)


@pytest.mark.unit
def test_upload_file_falls_back_to_sanctum_when_tmpfiles_fails():
    api_response = json.dumps(
        {
            "status": "success",
            "data": {
                "url": "https://tmp.sanctumos.org/xy12ZZ99/uploaded.png",
                "direct_url": "https://tmp.sanctumos.org/dl/xy12ZZ99/uploaded.png",
            },
        }
    ).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = api_response
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"\x89PNG")
        path = Path(f.name)
    try:
        with patch("common.ephemeral_upload._tmpfiles.upload_file", side_effect=RuntimeError("down")):
            with patch("common.ephemeral_upload.urlopen", return_value=mock_resp):
                result = upload_file(path)
        assert result == "https://tmp.sanctumos.org/dl/xy12ZZ99/uploaded.png"
    finally:
        path.unlink(missing_ok=True)


@pytest.mark.unit
def test_upload_file_both_fail_raises():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"\x89PNG")
        path = Path(f.name)
    try:
        with patch("common.ephemeral_upload._tmpfiles.upload_file", side_effect=RuntimeError("a")):
            with patch(
                "common.ephemeral_upload._upload_sanctum_tmp",
                side_effect=RuntimeError("b"),
            ):
                with pytest.raises(RuntimeError, match="tmpfiles.org") as exc:
                    upload_file(path)
                assert "sanctum tmp" in str(exc.value)
    finally:
        path.unlink(missing_ok=True)


@pytest.mark.unit
def test_sanctum_upload_url_default():
    assert "tmp.sanctumos.org" in SANCTUM_TMP_UPLOAD_URL
