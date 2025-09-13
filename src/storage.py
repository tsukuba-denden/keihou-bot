from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)


class JsonStorage:
    """Persist a set of sent alert IDs to avoid duplicates."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            logger.info(f"Storage file not found at {self.path}, creating a new one.")
            self._write(set())

    def _read(self) -> set[str]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            logger.debug(f"Read {len(data)} IDs from {self.path}")
            return set(data)
        except FileNotFoundError:
            logger.warning(f"Storage file not found at {self.path} on read, returning empty set.")
            return set()
        except json.JSONDecodeError:
            logger.exception(f"Failed to decode JSON from {self.path}, returning empty set.")
            return set()

    def _write(self, items: Iterable[str]) -> None:
        item_set = set(items)
        try:
            self.path.write_text(
                json.dumps(sorted(item_set), ensure_ascii=False, indent=2), encoding="utf-8"
            )
            logger.debug(f"Wrote {len(item_set)} IDs to {self.path}")
        except OSError as e:
            logger.exception(f"Failed to write to storage file {self.path}: {e}")

    def has(self, alert_id: str) -> bool:
        return alert_id in self._read()

    def add(self, alert_id: str) -> None:
        items = self._read()
        if alert_id not in items:
            items.add(alert_id)
            self._write(items)
            logger.info(f"Added alert ID {alert_id} to storage.")

    def add_many(self, alert_ids: Iterable[str]) -> None:
        items = self._read()
        new_ids = set(alert_ids) - items
        if new_ids:
            items.update(new_ids)
            self._write(items)
            logger.info(f"Added {len(new_ids)} new alert IDs to storage.")
