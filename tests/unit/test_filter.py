from __future__ import annotations

from datetime import datetime, timezone

from src.filter import pick_23_wards
from src.models import Alert


def make_alert(area: str) -> Alert:
    return Alert(
        id="1",
        title="test",
        area=area,
        ward=None,
        category="cat",
        severity="sev",
        issued_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        expires_at=None,
        link=None,
    )


def test_pick_23_wards_matches():
    alerts = [make_alert("東京都千代田区"), make_alert("神奈川県横浜市")]
    out = pick_23_wards(alerts)
    assert len(out) == 1
    assert out[0].ward == "千代田区"
