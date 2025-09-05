from __future__ import annotations

from datetime import datetime, timezone

from src.jma_parser import parse_jma_xml


def test_parse_jma_xml_basic():
    """Test basic JMA XML parsing with weather warning format."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Report>
    <Head>
        <Title>大雨警報</Title>
        <ReportDateTime>2024-01-01T12:00:00Z</ReportDateTime>
    </Head>
    <Body>
        <Warning>
            <Item>
                <Area>
                    <Name>東京都千代田区</Name>
                </Area>
                <Kind>
                    <Name>大雨警報</Name>
                    <Status>警報</Status>
                </Kind>
            </Item>
        </Warning>
    </Body>
</Report>""".encode(
        "utf-8"
    )

    alerts = parse_jma_xml(xml_content)
    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.title == "大雨警報"
    assert alert.area == "東京都千代田区"
    assert alert.category == "大雨警報"
    assert alert.severity == "警報"
    assert alert.issued_at == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert alert.ward is None
    assert alert.expires_at is None
    assert alert.link is None
    assert len(alert.id) == 16  # SHA256 hash truncated to 16 chars


def test_parse_jma_xml_alternative_format():
    """Test JMA XML parsing with alternative element structure."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Root>
    <Report>
        <Head>
            <Headline>
                <Text>地震速報</Text>
            </Headline>
            <ReportDateTime>2024-01-02T15:30:00+09:00</ReportDateTime>
        </Head>
        <Body>
            <Item>
                <Area>東京都新宿区</Area>
                <Kind>地震速報</Kind>
                <Status>注意</Status>
            </Item>
        </Body>
    </Report>
</Root>""".encode(
        "utf-8"
    )

    alerts = parse_jma_xml(xml_content)
    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.title == "地震速報"
    assert alert.area == "東京都新宿区"
    assert alert.category == "地震速報"
    assert alert.severity == "注意"
    # Should handle timezone conversion to UTC
    assert alert.issued_at.tzinfo == timezone.utc


def test_parse_jma_xml_multiple_areas():
    """Test JMA XML parsing with multiple area items."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Report>
    <Head>
        <Title>強風注意報</Title>
        <ReportDateTime>2024-01-03T09:15:00Z</ReportDateTime>
    </Head>
    <Body>
        <Warning>
            <Item>
                <Area>
                    <Name>東京都港区</Name>
                </Area>
                <Kind>
                    <Name>強風注意報</Name>
                    <Status>注意報</Status>
                </Kind>
            </Item>
            <Item>
                <Area>
                    <Name>東京都渋谷区</Name>
                </Area>
                <Kind>
                    <Name>強風注意報</Name>
                    <Status>注意報</Status>
                </Kind>
            </Item>
        </Warning>
    </Body>
</Report>""".encode(
        "utf-8"
    )

    alerts = parse_jma_xml(xml_content)
    assert len(alerts) == 2

    areas = [alert.area for alert in alerts]
    assert "東京都港区" in areas
    assert "東京都渋谷区" in areas

    for alert in alerts:
        assert alert.title == "強風注意報"
        assert alert.category == "強風注意報"
        assert alert.severity == "注意報"


def test_parse_jma_xml_empty_body():
    """Test JMA XML parsing with empty body but valid title."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Report>
    <Head>
        <Title>システムメンテナンス通知</Title>
        <ReportDateTime>2024-01-04T20:00:00Z</ReportDateTime>
    </Head>
    <Body>
    </Body>
</Report>""".encode(
        "utf-8"
    )

    alerts = parse_jma_xml(xml_content)
    # Should create fallback alert when no items found but title exists
    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.title == "システムメンテナンス通知"
    assert alert.area == "Unknown"
    assert alert.category == "Unknown"
    assert alert.severity == "Unknown"


def test_parse_jma_xml_missing_elements():
    """Test JMA XML parsing with missing optional elements."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Report>
    <Head>
        <ReportDateTime>2024-01-05T14:45:00Z</ReportDateTime>
    </Head>
    <Body>
        <Item>
            <Area>
                <Name>東京都品川区</Name>
            </Area>
        </Item>
    </Body>
</Report>""".encode(
        "utf-8"
    )

    alerts = parse_jma_xml(xml_content)
    assert len(alerts) == 1
    alert = alerts[0]
    # Should handle missing title by generating one
    assert "Unknown" in alert.title or "東京都品川区" in alert.title
    assert alert.area == "東京都品川区"
    assert alert.category == "Unknown"
    assert alert.severity == "Unknown"


def test_parse_jma_xml_invalid_datetime():
    """Test JMA XML parsing with invalid datetime format."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Report>
    <Head>
        <Title>テスト警報</Title>
        <ReportDateTime>invalid-datetime</ReportDateTime>
    </Head>
    <Body>
        <Item>
            <Area>
                <Name>東京都</Name>
            </Area>
            <Kind>
                <Name>テスト</Name>
                <Status>警報</Status>
            </Kind>
        </Item>
    </Body>
</Report>""".encode(
        "utf-8"
    )

    # Should not raise exception but handle gracefully
    alerts = parse_jma_xml(xml_content)
    assert len(alerts) == 1
    alert = alerts[0]
    # Should use current time when parsing fails
    assert alert.issued_at.tzinfo == timezone.utc
    assert alert.title == "テスト警報"
