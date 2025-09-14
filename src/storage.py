from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterable, Dict

logger = logging.getLogger(__name__)


class JsonStorage:
    """Persist a mapping of alert IDs to status to avoid duplicates and track cancellations.

    File format (new):
        { "<id>": "active" | "cancelled", ... }

    Backward compatibility: if file is a list of IDs, treat them as "active".
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            logger.info(f"Storage file not found at {self.path}, creating a new one.")
            self._write(set())

    def _read(self) -> Dict[str, str]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, list):  # backward compat
                logger.debug("Detected legacy list format; converting to map.")
                return {str(x): "active" for x in data}
            if isinstance(data, dict):
                # validate values
                return {str(k): ("cancelled" if v == "cancelled" else "active") for k, v in data.items()}
            logger.warning("Unexpected storage format; returning empty map.")
            return {}
        except FileNotFoundError:
            logger.warning(f"Storage file not found at {self.path} on read, returning empty set.")
            return {}
        except json.JSONDecodeError:
            logger.exception(f"Failed to decode JSON from {self.path}, returning empty set.")
            return {}

    def _write(self, items: Dict[str, str] | Iterable[str]) -> None:
        # Accept either mapping (new) or iterable of ids (legacy path)
        if isinstance(items, dict):
            payload = items
        else:
            payload = {str(x): "active" for x in set(items)}
        try:
            self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            logger.debug(f"Wrote {len(payload)} IDs to {self.path}")
        except OSError as e:
            logger.exception(f"Failed to write to storage file {self.path}: {e}")

    def has(self, alert_id: str) -> bool:
        return alert_id in self._read()

    def add(self, alert_id: str, status: str = "active") -> None:
        items = self._read()
        if alert_id not in items:
            items[alert_id] = status if status in {"active", "cancelled"} else "active"
            self._write(items)
            logger.info(f"Added alert ID {alert_id} with status={items[alert_id]} to storage.")

    def add_many(self, alert_ids: Iterable[str], status: str = "active") -> None:
        items = self._read()
        count = 0
        for aid in alert_ids:
            if aid not in items:
                items[str(aid)] = status if status in {"active", "cancelled"} else "active"
                count += 1
        if count:
            self._write(items)
            logger.info(f"Added {count} new alert IDs to storage with status={status}.")

    def get_status(self, alert_id: str) -> str | None:
        return self._read().get(alert_id)

    def update_status(self, alert_id: str, status: str) -> None:
        if status not in {"active", "cancelled"}:
            logger.warning("Unsupported status '%s' ignored.", status)
            return
        items = self._read()
        if alert_id in items:
            items[alert_id] = status
            self._write(items)
            logger.info("Updated alert %s to status=%s", alert_id, status)
