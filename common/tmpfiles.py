"""
Upload files to tmpfiles.org and get direct download URLs.

tmpfiles.org API:
- POST https://tmpfiles.org/api/v1/upload with multipart file -> returns view URL
- View URL: https://tmpfiles.org/{id}/{filename} -> returns HTML page
- Direct URL: https://tmpfiles.org/dl/{id}/{filename} -> returns raw file

Uses stdlib only (urllib). No dependency on the tmp script.
"""

import hashlib
import mimetypes
import re
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from urllib.request import Request, urlopen

UPLOAD_URL = "https://tmpfiles.org/api/v1/upload"
TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def view_url_to_direct_url(view_url: str) -> str:
    """
    Convert tmpfiles.org view URL to direct download URL.

    View URL returns HTML. Direct URL returns the raw file.
    Example: https://tmpfiles.org/22907829/test.png -> https://tmpfiles.org/dl/22907829/test.png
    """
    parsed = urlparse(view_url)
    path = parsed.path.strip("/")
    if not re.match(r"^\d+/", path):
        raise ValueError(
            f"Unexpected tmpfiles path (expected {{id}}/{{filename}}): {path}"
        )
    direct_path = "dl/" + path
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


def _multipart_body(file_path: Path, field_name: str = "file") -> tuple[bytes, str]:
    """Build multipart/form-data body and boundary."""
    boundary = "----formdata-" + hashlib.sha1(str(file_path).encode()).hexdigest()[:16]
    content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    filename = file_path.name

    with open(file_path, "rb") as f:
        file_data = f.read()

    lines = [
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode(),
        f"Content-Type: {content_type}\r\n\r\n".encode(),
        file_data,
        f"\r\n--{boundary}--\r\n".encode(),
    ]
    body = b"".join(lines)
    return body, f"multipart/form-data; boundary={boundary}"


def upload_file(file_path: Path) -> str:
    """
    Upload a file to tmpfiles.org. Returns the direct download URL.

    Use this URL to fetch the raw file (e.g. for the agent or tools).
    On HTTP or API error, raises; caller should log and skip if desired.
    """
    body, content_type = _multipart_body(file_path)
    req = Request(
        UPLOAD_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": content_type,
            "User-Agent": USER_AGENT,
        },
    )
    with urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read().decode()
    if '"status":"success"' not in raw and '"status": "success"' not in raw:
        raise RuntimeError(f"Upload failed or unexpected response: {raw}")
    match = re.search(r'"url"\s*:\s*"([^"]+)"', raw)
    if not match:
        raise RuntimeError(f"Could not find url in response: {raw}")
    view_url = match.group(1).strip()
    if view_url.startswith("http://"):
        view_url = "https://" + view_url[7:]
    return view_url_to_direct_url(view_url)
