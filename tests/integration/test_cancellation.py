from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.main import pipeline_once


def test_cancellation_pipeline_end_to_end():
    """解除電文を受け取った場合に、送信ロジックが解除通知として動作すること。

    1) 初回: 警報が発表 → 通常の送信（ここではモックのみ）
    2) 次回: 解除電文 → 解除通知として送信（ここではモックのみ）
    
    現段階では main/pipeline と DiscordNotifier に解除専用のメソッドが未実装のため、
    少なくとも 2 回目の呼び出しで send_alerts が呼ばれること（RED）を確認する。
    """
    xml_warning = '''<?xml version="1.0" encoding="UTF-8"?>
<Report>
  <Head>
    <Title>気象警報・注意報</Title>
    <ReportDateTime>2024-01-01T10:00:00Z</ReportDateTime>
  </Head>
  <Body>
    <Warning>
      <Item>
        <Area><Name>東京都千代田区</Name></Area>
        <Kind><Name>大雨警報</Name><Status>警報</Status></Kind>
      </Item>
    </Warning>
  </Body>
</Report>'''.encode('utf-8')

    xml_cancel = '''<?xml version="1.0" encoding="UTF-8"?>
<Report>
  <Head>
    <Title>気象警報・注意報</Title>
    <InfoType>取消</InfoType>
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
</Report>'''.encode('utf-8')

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "sent_ids.json"

        with patch("src.main.JmaClient") as mock_jma, patch("src.main.DiscordNotifier") as mock_discord:
            mock_jma_instance = mock_jma.return_value
            mock_discord_instance = mock_discord.return_value
            mock_discord_instance.send_alerts = MagicMock()
            mock_discord_instance.send_cancellations = MagicMock()

            # 1) 初回: 発表
            mock_jma_instance.fetch.return_value = xml_warning
            with patch("src.main.SENT_IDS_FILE", storage_path):
                sent = pipeline_once("http://dummy")
                assert sent == 1
                assert mock_discord_instance.send_alerts.call_count == 1

            # 2) 解除: InfoType=取消 → send_cancellations が呼ばれる
            mock_discord_instance.send_alerts.reset_mock()
            mock_discord_instance.send_cancellations.reset_mock()
            mock_jma_instance.fetch.return_value = xml_cancel
            with patch("src.main.SENT_IDS_FILE", storage_path):
                sent_cancel = pipeline_once("http://dummy", force_send=True)
                assert sent_cancel == 1
                mock_discord_instance.send_alerts.assert_not_called()
                assert mock_discord_instance.send_cancellations.call_count == 1
