from __future__ import annotations

from datetime import datetime, timezone

from src.models import Alert, RoleMentionSetting


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


def test_role_mention_setting_from_env_parses_role_id(monkeypatch):
    monkeypatch.setenv("ROLE_ID", "123456789012345678")
    s = RoleMentionSetting.from_env()
    assert s.role_id == 123456789012345678
    assert s.enabled is True


def test_role_mention_setting_invalid_role_id(monkeypatch):
    monkeypatch.delenv("ROLE_ID", raising=False)
    monkeypatch.setenv("ROLE_MENTION_ENABLED", "true")
    s = RoleMentionSetting.from_env()
    assert s.role_id is None
    assert s.enabled is True
