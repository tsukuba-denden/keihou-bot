from __future__ import annotations

from datetime import datetime, timezone

from src.school_policy import decide_school_guidance
from src.models import Alert


def make_alert(category: str, severity: str = "警報") -> Alert:
    return Alert(
        id="x",
        title=category,
        area="東京都千代田区",
        ward="千代田区",
        category=category,
        severity=severity,
        issued_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        expires_at=None,
        link=None,
    )


def test_6am_with_warning_wait_at_home():
    now = datetime(2024, 1, 2, 21, 0, 0, tzinfo=timezone.utc)  # JST=2024-01-03 06:00
    g = decide_school_guidance([make_alert("大雨警報")], now=now)
    assert g.decision_point == "06"
    assert g.status == "自宅待機"


def test_6am_all_clear_normal_class():
    now = datetime(2024, 1, 2, 21, 30, 0, tzinfo=timezone.utc)  # JST~06:30
    g = decide_school_guidance([], now=now)
    assert g.decision_point == "06"
    assert g.status == "平常授業"
    assert g.attend_time is not None


def test_8am_tue_with_warning_wait_at_home():
    # 2024-01-02 Tue 23:10Z => JST 08:10
    now = datetime(2024, 1, 2, 23, 10, 0, tzinfo=timezone.utc)
    g = decide_school_guidance([make_alert("暴風警報")], now=now)
    assert g.decision_point == "08"
    assert g.status == "自宅待機"


def test_8am_mon_with_warning_home_study():
    # 2023-12-31 Sun 23:15Z => JST 08:15 Mon (2024-01-01 Mon)
    now = datetime(2023, 12, 31, 23, 15, 0, tzinfo=timezone.utc)
    g = decide_school_guidance([make_alert("大雪警報")], now=now)
    assert g.decision_point == "08"
    assert g.status == "自宅学習"


def test_10am_clear_weekday_afternoon_class():
    # 2024-01-02 Tue 01:10Z => JST 10:10 Tue
    now = datetime(2024, 1, 2, 1, 10, 0, tzinfo=timezone.utc)
    g = decide_school_guidance([], now=now)
    assert g.decision_point == "10"
    assert g.status == "午後から授業"
    assert g.attend_time is not None


def test_advisory_only_is_ignored():
    # 注意報のみは対象外
    now = datetime(2024, 1, 2, 21, 0, 0, tzinfo=timezone.utc)  # JST=06:00
    g = decide_school_guidance([make_alert("強風注意報", severity="注意報")], now=now)
    assert g.status == "平常授業"


def test_10am_clear_saturday_no_class():
    # 2024-01-06 Sat 01:10Z => JST 10:10 Sat (2024-01-06 土)
    now = datetime(2024, 1, 6, 1, 10, 0, tzinfo=timezone.utc)
    g = decide_school_guidance([], now=now)
    assert g.decision_point == "10"
    # 月・土は午後授業がないため、自宅学習（授業なし）
    assert g.status == "自宅学習"
    assert g.attend_time is None