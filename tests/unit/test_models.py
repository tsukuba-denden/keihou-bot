from __future__ import annotations

from datetime import datetime, timezone

from src.models import Alert


def test_alert_to_dict_roundtrip():
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    a = Alert(
        id="abc",
        title="大雨警報",
        area="東京都千代田区",
        ward="千代田区",
        category="気象警報",
        severity="警報",
        issued_at=now,
        expires_at=None,
        link=None,
    )
    d = a.to_dict()
    assert d["title"] == "大雨警報"
    assert d["area"] == "東京都千代田区"
    assert d["ward"] == "千代田区"
    assert d["issued_at"] == now.isoformat()
