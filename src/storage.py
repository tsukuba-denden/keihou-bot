from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


class JsonStorage:
    """Persist a set of sent alert IDs to avoid duplicates."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(set())

    def _read(self) -> set[str]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return set(data)
        except FileNotFoundError:
            return set()

    def _write(self, items: Iterable[str]) -> None:
        self.path.write_text(json.dumps(sorted(set(items)), ensure_ascii=False, indent=2), encoding="utf-8")

    def has(self, alert_id: str) -> bool:
        return alert_id in self._read()

    def add(self, alert_id: str) -> None:
        items = self._read()
        items.add(alert_id)
        self._write(items)

    def add_many(self, alert_ids: Iterable[str]) -> None:
        items = self._read()
        items.update(alert_ids)
        self._write(items)
