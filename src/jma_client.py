from __future__ import annotations

from typing import Optional

import requests


class JmaClient:
    """Fetch JMA XML feeds.

    Note: URL endpoints may vary; use the appropriate JMA feed URL for warnings.
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def fetch(self, path: str = "") -> bytes:
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.content
