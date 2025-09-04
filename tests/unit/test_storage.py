from __future__ import annotations

from pathlib import Path

from src.storage import JsonStorage


def test_json_storage_add_and_has(tmp_path: Path):
    path = tmp_path / "sent.json"
    s = JsonStorage(path)
    assert not s.has("x")
    s.add("x")
    assert s.has("x")


def test_json_storage_add_many(tmp_path: Path):
    path = tmp_path / "sent.json"
    s = JsonStorage(path)
    s.add_many(["a", "b", "c"])
    for k in ["a", "b", "c"]:
        assert s.has(k)
