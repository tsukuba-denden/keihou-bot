from __future__ import annotations

from typing import Iterable, List

from .models import Alert


TOKYO_23_WARDS = {
    "千代田区",
    "中央区",
    "港区",
    "新宿区",
    "文京区",
    "台東区",
    "墨田区",
    "江東区",
    "品川区",
    "目黒区",
    "大田区",
    "世田谷区",
    "渋谷区",
    "中野区",
    "杉並区",
    "豊島区",
    "北区",
    "荒川区",
    "板橋区",
    "練馬区",
    "足立区",
    "葛飾区",
    "江戸川区",
}


def pick_23_wards(alerts: Iterable[Alert]) -> list[Alert]:
    """Return only alerts that match one of Tokyo's 23 wards by name in area."""
    result: list[Alert] = []
    for a in alerts:
        ward = next((w for w in TOKYO_23_WARDS if w in a.area or (a.ward and w in a.ward)), None)
        if ward:
            result.append(
                Alert(
                    id=a.id,
                    title=a.title,
                    area=a.area,
                    ward=ward,
                    category=a.category,
                    severity=a.severity,
                    issued_at=a.issued_at,
                    expires_at=a.expires_at,
                    link=a.link,
                    raw=a.raw,
                )
            )
    return result
