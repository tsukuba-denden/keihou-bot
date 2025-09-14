from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.main import pipeline_once
from src.models import SchoolGuidance


def test_pipeline_sends_school_guidance():
    # 最小のXML（東京23区に関係する1件）
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<Report>
  <Head>
    <Title>気象警報・注意報</Title>
    <ReportDateTime>2024-01-01T12:00:00Z</ReportDateTime>
  </Head>
  <Body>
    <Warning>
      <Item>
        <Area><Name>東京都千代田区</Name></Area>
        <Kind><Name>大雨警報</Name><Status>警報</Status></Kind>
      </Item>
    </Warning>
  </Body>
.</Report>'''.encode('utf-8')

    with patch("src.main.JmaClient") as mock_jma, \
         patch("src.main.DiscordNotifier") as mock_discord, \
         patch("src.main.decide_school_guidance") as mock_decide:

        mock_jma_instance = mock_jma.return_value
        mock_jma_instance.fetch.return_value = xml

        mock_discord_instance = mock_discord.return_value
        mock_discord_instance.send_school_guidance = MagicMock()

        mock_decide.return_value = SchoolGuidance(
            date="2024-01-01",
            decision_point="06",
            weekday=1,
            status="平常授業",
            attend_time="08:30",
            notes=["note"],
        )

        sent = pipeline_once("http://dummy", dry_run=True, force_send=True, no_store=True)

        # アラートも送られる（force_send）想定だが、ここではガイダンス呼び出しのみ確認
        assert mock_discord_instance.send_school_guidance.call_count == 1
        args, _ = mock_discord_instance.send_school_guidance.call_args
        assert isinstance(args[0], SchoolGuidance)
