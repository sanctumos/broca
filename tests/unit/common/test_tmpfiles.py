"""Unit tests for common.tmpfiles."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from common.tmpfiles import upload_file, view_url_to_direct_url


@pytest.mark.unit
def test_view_url_to_direct_url():
    """View URL is converted to direct download URL."""
    view_url = "https://tmpfiles.org/22907829/test.png"
    direct = view_url_to_direct_url(view_url)
    assert direct == "https://tmpfiles.org/dl/22907829/test.png"


@pytest.mark.unit
def test_view_url_to_direct_url_http_normalized():
    """HTTP view URL is converted and scheme stays in urlunparse; path uses dl/."""
    view_url = "http://tmpfiles.org/12345/photo.jpg"
    direct = view_url_to_direct_url(view_url)
    assert "dl/12345/photo.jpg" in direct
    assert direct.endswith("photo.jpg") or "/photo.jpg" in direct


@pytest.mark.unit
def test_view_url_to_direct_url_invalid_path_raises():
    """Invalid path (no id/filename) raises ValueError."""
    with pytest.raises(ValueError, match="Unexpected tmpfiles path"):
        view_url_to_direct_url("https://tmpfiles.org/notnumeric/file.png")


@pytest.mark.unit
def test_upload_file_returns_direct_url():
    """upload_file returns direct download URL when API returns success."""
    api_response = (
        b'{"status":"success","data":{"url":"https://tmpfiles.org/99999/uploaded.png"}}'
    )
    mock_resp = MagicMock()
    mock_resp.read.return_value = api_response
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        path = Path(f.name)

    try:
        with patch("common.tmpfiles.urlopen", return_value=mock_resp):
            result = upload_file(path)
        assert result == "https://tmpfiles.org/dl/99999/uploaded.png"
    finally:
        path.unlink(missing_ok=True)


@pytest.mark.unit
def test_upload_file_api_failure_raises():
    """upload_file raises when API does not return success."""
    api_response = b'{"status":"error","data":{}}'
    mock_resp = MagicMock()
    mock_resp.read.return_value = api_response
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"\x89PNG")
        path = Path(f.name)

    try:
        with patch("common.tmpfiles.urlopen", return_value=mock_resp):
            with pytest.raises(RuntimeError, match="Upload failed"):
                upload_file(path)
    finally:
        path.unlink(missing_ok=True)
