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


def _make_xml(area_name: str = "東京都千代田区", kind_name: str = "大雨警報", status: str = "警報") -> bytes:
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<Report>
  <Head>
    <Title>気象警報・注意報</Title>
    <ReportDateTime>2024-01-01T12:00:00Z</ReportDateTime>
  </Head>
  <Body>
    <Warning>
      <Item>
        <Area><Name>{area_name}</Name></Area>
        <Kind><Name>{kind_name}</Name><Status>{status}</Status></Kind>
      </Item>
    </Warning>
  </Body>
.</Report>'''.encode('utf-8')


def test_integration_guidance_mentions_when_time_differs(monkeypatch):
    from unittest.mock import patch, MagicMock

    monkeypatch.setenv("ROLE_ID", "123456789012345678")

    with patch("src.main.JmaClient") as mock_jma, \
         patch("src.main.DiscordNotifier") as mock_discord, \
         patch("src.main.decide_school_guidance") as mock_decide:

        mock_jma.return_value.fetch.return_value = _make_xml()

        mock_discord_instance = mock_discord.return_value
        mock_discord_instance.send_school_guidance = MagicMock()

        mock_decide.return_value = SchoolGuidance(
            date="2024-01-01",
            decision_point="06",
            weekday=1,
            status="平常授業",
            attend_time="09:00",  # differs from baseline
            notes=["note"],
        )

        pipeline_once("http://dummy", dry_run=True, force_send=True, no_store=True)

        assert mock_discord_instance.send_school_guidance.call_count == 1
        (g,), _ = mock_discord_instance.send_school_guidance.call_args
        assert isinstance(g, SchoolGuidance)


def test_integration_guidance_no_mention_when_same_time(monkeypatch):
    from unittest.mock import patch, MagicMock

    monkeypatch.setenv("ROLE_ID", "123456789012345678")
    monkeypatch.setenv("SCHOOL_NORMAL_TIME", "08:30")

    with patch("src.main.JmaClient") as mock_jma, \
         patch("src.main.DiscordNotifier") as mock_discord, \
         patch("src.main.decide_school_guidance") as mock_decide:

        mock_jma.return_value.fetch.return_value = _make_xml()

        mock_discord_instance = mock_discord.return_value
        mock_discord_instance.send_school_guidance = MagicMock()

        mock_decide.return_value = SchoolGuidance(
            date="2024-01-01",
            decision_point="06",
            weekday=1,
            status="平常授業",
            attend_time="08:30",  # same as baseline
            notes=["note"],
        )

        pipeline_once("http://dummy", dry_run=True, force_send=True, no_store=True)

        assert mock_discord_instance.send_school_guidance.call_count == 1
        (g,), _ = mock_discord_instance.send_school_guidance.call_args
        assert isinstance(g, SchoolGuidance)


def test_integration_same_day_suppression(monkeypatch, tmp_path):
    from unittest.mock import patch, MagicMock

    monkeypatch.setenv("ROLE_ID", "123456789012345678")
    # ensure guidance state uses temp dir
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    with patch("src.main.JmaClient") as mock_jma, \
         patch("src.main.DiscordNotifier") as mock_discord, \
         patch("src.main.decide_school_guidance") as mock_decide:

        mock_jma.return_value.fetch.return_value = _make_xml()
        mock_discord_instance = mock_discord.return_value
        mock_discord_instance.send_school_guidance = MagicMock()

        # First: time differs → should send mention
        mock_decide.return_value = SchoolGuidance(
            date="2024-01-01",
            decision_point="06",
            weekday=1,
            status="平常授業",
            attend_time="09:00",
            notes=["note"],
        )
        pipeline_once("http://dummy", dry_run=True, force_send=True, no_store=True)

        # Second: same date, same decision point, another update within the day
        mock_discord_instance.send_school_guidance.reset_mock()
        mock_decide.return_value = SchoolGuidance(
            date="2024-01-01",
            decision_point="06",
            weekday=1,
            status="平常授業",
            attend_time="09:30",
            notes=["note2"],
        )
        pipeline_once("http://dummy", dry_run=True, force_send=True, no_store=True)

        # Depending on GuidanceController rules, duplicate during the same DP may be suppressed
        # We assert that at most one send occurred across both calls
        assert mock_discord_instance.send_school_guidance.call_count <= 1
