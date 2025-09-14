from __future__ import annotations

import logging
import os
from pathlib import Path

import requests
from requests import exceptions as req_exc

logger = logging.getLogger(__name__)


class JmaClient:
    """Fetch JMA XML feeds.

    Note: URL endpoints may vary; use the appropriate JMA feed URL for warnings.
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def fetch(self, path: str = "") -> bytes:
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url

        # Support local file debugging: file://... or direct filesystem path
        if url.startswith("file://"):
            file_path = Path(url.replace("file://", "", 1))
            logger.info(f"Reading JMA XML from local file: {file_path}")
            try:
                return file_path.read_bytes()
            except OSError as e:
                logger.exception(f"Failed to read local file {file_path}: {e}")
                raise

        if os.path.exists(url):
            file_path = Path(url)
            logger.info(f"Reading JMA XML from local path: {file_path}")
            try:
                return file_path.read_bytes()
            except OSError as e:
                logger.exception(f"Failed to read local file {file_path}: {e}")
                raise

        logger.info(f"Fetching JMA feed from: {url}")
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            logger.info(f"Successfully fetched data from {url} (status: {resp.status_code})")
            return resp.content
        except req_exc.RequestException as e:
            logger.exception(f"Failed to fetch data from {url}: {e}")
            raise  # Re-raise the exception after logging
