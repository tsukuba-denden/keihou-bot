from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any


@dataclass(frozen=True, slots=True)
class Alert:
    """Normalized alert entity for JMA bulletins.

    Attributes:
        id: Stable identifier (e.g., hash of important fields)
        title: Short title/message
        area: Area name (e.g., Tokyo-to Chiyoda-ku)
        ward: Specific ward name if applicable (one of 23 wards)
        category: Alert category (e.g., "Weather Warning", "Earthquake Early Warning")
        severity: Level string (e.g., Advisory/Warning/Emergency)
        issued_at: Datetime when alert was issued (UTC)
        expires_at: Optional expiry time (UTC)
        link: Source link if any
        status: Alert lifecycle status ("active" or "cancelled")
        raw: Optional raw payload for debugging
    """

    id: str
    title: str
    area: str
    ward: Optional[str]
    category: str
    severity: str
    issued_at: datetime
    expires_at: Optional[datetime]
    link: Optional[str]
    status: str = "active"
    raw: Optional[Any] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "area": self.area,
            "ward": self.ward,
            "category": self.category,
            "severity": self.severity,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "link": self.link,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class SchoolGuidance:
    """Decision object for school attendance guidance based on warning policy.

    Attributes:
        date: Local date string (YYYY-MM-DD, Asia/Tokyo)
        decision_point: "06" | "08" | "10" | "pre6" (表示用)
        weekday: 0=Mon .. 6=Sun (Japan local)
        status: 「平常授業」「自宅待機」「自宅学習」「第3時限から授業」「午後から授業」など
        attend_time: 具体的な登校目安時刻（必要時）
        notes: 追加の注意書きリスト
    """

    date: str
    decision_point: str
    weekday: int
    status: str
    attend_time: Optional[str] = None
    notes: Optional[list[str]] = None


@dataclass(frozen=True, slots=True)
class RoleMentionSetting:
    """Configuration for Discord role mention when school guidance time differs.

    Fields:
      - role_id: Discord role ID (server-level). If None or invalid, mention is disabled.
      - enabled: Master flag to allow mention behavior.
      - suppress_policy: Placeholder for future suppression strategy (e.g., per-day-once).
      - window_minutes: Optional window for suppression if applied.
    """

    role_id: Optional[int]
    enabled: bool = True
    suppress_policy: str = "per-day-once"
    window_minutes: int = 0

    @staticmethod
    def _parse_int(value: str | None) -> Optional[int]:
        if not value:
            return None
        try:
            v = int(str(value))
            return v if v > 0 else None
        except Exception:
            return None

    @classmethod
    def from_env(cls) -> "RoleMentionSetting":
        import os

        rid = cls._parse_int(os.getenv("ROLE_ID"))
        enabled = (os.getenv("ROLE_MENTION_ENABLED", "true").lower() in {"1", "true", "yes", "on"})
        return cls(role_id=rid, enabled=enabled)
