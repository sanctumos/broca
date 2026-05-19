"""
Upload ephemeral files for agent image attachments.

Primary: tmpfiles.org (compatible API).
Fallback: Sanctum tmp host (tmp.sanctumos.org) when primary fails.

Returns direct download URLs suitable for Venice vision (GET raw bytes).
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from urllib.request import Request, urlopen

from common import tmpfiles as _tmpfiles

TIMEOUT = 30
USER_AGENT = "Sanctum-Broca/1.0 (ephemeral upload)"

SANCTUM_TMP_UPLOAD_URL = os.environ.get(
    "SANCTUM_TMP_UPLOAD_URL",
    "https://tmp.sanctumos.org/api/v1/upload.php",
).strip()

# Hosts that use /{id}/{filename} view URLs and /dl/{id}/{filename} direct URLs.
_COMPATIBLE_HOST_SUFFIXES = (
    "tmpfiles.org",
    "tmp.sanctumos.org",
)


def view_url_to_direct_url(view_url: str) -> str:
    """
    Convert view URL to direct download URL for supported ephemeral hosts.
    Falls back to tmpfiles.org rules for unknown hosts (legacy behavior).
    """
    parsed = urlparse(view_url)
    host = (parsed.hostname or "").lower()
    if any(host == suffix or host.endswith("." + suffix) for suffix in _COMPATIBLE_HOST_SUFFIXES):
        return _path_to_direct_url(parsed)
    return _tmpfiles.view_url_to_direct_url(view_url)


def upload_file(file_path: Path) -> str:
    """
    Upload file; return direct download URL.
    Tries tmpfiles.org first, then Sanctum tmp host.
    """
    errors: list[str] = []
    try:
        return _tmpfiles.upload_file(file_path)
    except Exception as e:
        errors.append(f"tmpfiles.org: {e}")
    try:
        return _upload_sanctum_tmp(file_path)
    except Exception as e:
        errors.append(f"sanctum tmp: {e}")
    raise RuntimeError("; ".join(errors))


def _path_to_direct_url(parsed) -> str:
    path = parsed.path.strip("/")
    parts = path.split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(f"Unexpected ephemeral file path (expected id/filename): {path}")
    id_part, filename = parts[0], parts[1]
    if "/" in filename or not re.match(r"^[A-Za-z0-9_-]+$", id_part):
        raise ValueError(f"Unexpected ephemeral file path (expected id/filename): {path}")
    direct_path = f"dl/{id_part}/{filename}"
    return urlunparse(
        (
            parsed.scheme or "https",
            parsed.netloc,
            direct_path,
            "",
            "",
            "",
        )
    )


def _upload_sanctum_tmp(file_path: Path) -> str:
    if not SANCTUM_TMP_UPLOAD_URL:
        raise RuntimeError("SANCTUM_TMP_UPLOAD_URL is not configured")
    body, content_type = _tmpfiles._multipart_body(file_path)
    req = Request(
        SANCTUM_TMP_UPLOAD_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": content_type,
            "User-Agent": USER_AGENT,
        },
    )
    with urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read().decode()
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from sanctum tmp: {raw[:300]}") from e
    if obj.get("status") != "success":
        raise RuntimeError(f"Upload failed: {raw[:500]}")
    data = obj.get("data") or {}
    direct = (data.get("direct_url") or "").strip()
    if direct:
        return direct
    view_url = (data.get("url") or "").strip()
    if not view_url:
        raise RuntimeError(f"No url in response: {raw[:500]}")
    return view_url_to_direct_url(view_url)
