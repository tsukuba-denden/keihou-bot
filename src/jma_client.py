from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)


class JmaClient:
    """Fetch JMA XML feeds.

    Note: URL endpoints may vary; use the appropriate JMA feed URL for warnings.
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def fetch(self, path: str = "") -> bytes:
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        logger.info(f"Fetching JMA feed from: {url}")
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            logger.info(f"Successfully fetched data from {url} (status: {resp.status_code})")
            return resp.content
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to fetch data from {url}: {e}")
            raise  # Re-raise the exception after logging
