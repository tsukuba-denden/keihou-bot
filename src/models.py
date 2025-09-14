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
        }
