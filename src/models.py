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
