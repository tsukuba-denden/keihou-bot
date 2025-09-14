from __future__ import annotations

import pytest

from src.jma_parser import parse_jma_xml


def test_parse_jma_xml_cancellation_by_info_type():
    """InfoType=取消 が含まれるレポートは、全アイテムが cancellation と判定される。"""
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<Report>
  <Head>
    <Title>気象警報・注意報</Title>
    <InfoType>取消</InfoType>
    <ReportDateTime>2024-01-01T12:34:56Z</ReportDateTime>
  </Head>
  <Body>
    <Warning>
      <Item>
        <Area><Name>東京都千代田区</Name></Area>
        <Kind><Name>大雨警報</Name><Status>警報</Status></Kind>
      </Item>
    </Warning>
  </Body>
</Report>'''
    alerts = parse_jma_xml(xml.encode("utf-8"))
    assert len(alerts) == 1
    a = alerts[0]
    # 解除判定用の status プロパティを追加する実装を前提（REDフェーズ）
    assert getattr(a, "status") == "cancelled"
    assert a.category == "大雨警報"
    assert a.area == "東京都千代田区"


def test_parse_jma_xml_cancellation_by_kind_status():
    """Kind/Status=解除 を含むアイテムは cancellation と判定される。"""
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<Report>
  <Head>
    <Title>気象警報・注意報</Title>
    <ReportDateTime>2024-01-01T12:34:56Z</ReportDateTime>
  </Head>
  <Body>
    <Warning>
      <Item>
        <Area><Name>東京都新宿区</Name></Area>
        <Kind><Name>強風注意報</Name><Status>解除</Status></Kind>
      </Item>
    </Warning>
  </Body>
</Report>'''
    alerts = parse_jma_xml(xml.encode("utf-8"))
    assert len(alerts) == 1
    a = alerts[0]
    assert getattr(a, "status") == "cancelled"
    assert a.category == "強風注意報"
    assert a.area == "東京都新宿区"
