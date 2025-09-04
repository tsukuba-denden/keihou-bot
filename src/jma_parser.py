from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Iterable, List
from lxml import etree

from .models import Alert


@dataclass(frozen=True)
class ParsedAlert:
    title: str
    area: str
    category: str
    severity: str
    issued_at: datetime
    link: str | None
    raw: dict


def _text(node, xpath: str) -> str | None:
    res = node.xpath(xpath)
    if not res:
        return None
    if isinstance(res[0], etree._Element):
        return res[0].text
    return str(res[0])


def parse_jma_xml(xml_bytes: bytes) -> List[Alert]:
    """Parse a simplified subset of JMA XML and normalize to Alert objects.

    Note: JMA XML has multiple schemas; this function currently handles typical weather warnings
    and advisories. Extend as needed when integrating real feeds.
    """
    root = etree.fromstring(xml_bytes)

    # Very simplified extraction – replace with schema-aware parsing when available
    title = _text(root, "//Head/Title/text()") or _text(root, "//Report/Head/Headline/Text/text()")
    issued_str = _text(root, "//Head/ReportDateTime/text()") or _text(
        root, "//Report/Head/ReportDateTime/text()"
    )

    if issued_str:
        try:
            issued_at = datetime.fromisoformat(issued_str.replace("Z", "+00:00")).astimezone(
                timezone.utc
            )
        except (ValueError, TypeError):
            issued_at = datetime.now(timezone.utc)
    else:
        issued_at = datetime.now(timezone.utc)

    alerts: list[Alert] = []

    # Iterate over presumed area entries
    for area_node in root.xpath("//Body//Warning//Item | //Body//Area//Item | //Report/Body//Item"):
        area_name = (
            _text(area_node, "./Area/Name/text()") or _text(area_node, "./Area/text()") or "Unknown"
        )
        category = (
            _text(area_node, "./Kind/Name/text()") or _text(area_node, "./Kind/text()") or "Unknown"
        )
        severity = (
            _text(area_node, "./Kind/Status/text()")
            or _text(area_node, "./Status/text()")
            or "Unknown"
        )

        primitive = {
            "title": title or f"{category} - {area_name}",
            "area": area_name,
            "category": category,
            "severity": severity,
            "issued_at": issued_at.isoformat(),
        }
        alert_id = sha256(
            "|".join(
                [
                    primitive["area"],
                    primitive["category"],
                    primitive["severity"],
                    primitive["issued_at"],
                ]
            ).encode("utf-8")
        ).hexdigest()[:16]

        alerts.append(
            Alert(
                id=alert_id,
                title=primitive["title"],
                area=area_name,
                ward=None,
                category=category,
                severity=severity,
                issued_at=issued_at,
                expires_at=None,
                link=None,
                raw=primitive,
            )
        )

    # Fallback: if no items, produce a single area-less alert
    if not alerts and title:
        alert_id = sha256((title + issued_at.isoformat()).encode("utf-8")).hexdigest()[:16]
        alerts.append(
            Alert(
                id=alert_id,
                title=title,
                area="Unknown",
                ward=None,
                category="Unknown",
                severity="Unknown",
                issued_at=issued_at,
                expires_at=None,
                link=None,
                raw={"title": title},
            )
        )

    return alerts
