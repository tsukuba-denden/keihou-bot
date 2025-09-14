from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.main import pipeline_once
from src.models import Alert


class TestMainIntegration(unittest.TestCase):
    @patch("src.main.DiscordNotifier")
    @patch("src.main.JmaClient")
    def test_pipeline_once(self, mock_jma_client: MagicMock, mock_discord_notifier: MagicMock):
        """Test the main pipeline for fetching, filtering, and sending alerts."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
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
            <Item>
                <Area><Name>東京都八王子市</Name></Area>
                <Kind><Name>洪水注意報</Name><Status>注意報</Status></Kind>
            </Item>
            <Item>
                <Area><Name>東京都新宿区</Name></Area>
                <Kind><Name>強風注意報</Name><Status>注意報</Status></Kind>
            </Item>
        </Warning>
    </Body>
</Report>
""".encode("utf-8")
        # Mock JmaClient to return our test XML
        mock_jma_instance = mock_jma_client.return_value
        mock_jma_instance.fetch.return_value = xml_content

        # Mock DiscordNotifier
        mock_notifier_instance = mock_discord_notifier.return_value
        mock_notifier_instance.send_alerts = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup a temporary storage file
            storage_path = Path(tmpdir) / "sent_ids.json"
            with patch("src.main.SENT_IDS_FILE", storage_path):
                # --- First run: New alerts should be sent ---
                sent_count = pipeline_once("http://dummy.url/test.xml")

                # Assert that 2 alerts (Chiyoda, Shinjuku) were sent
                self.assertEqual(sent_count, 2)

                # Check that send_alerts was called once
                mock_notifier_instance.send_alerts.assert_called_once()

                # Verify the content of the sent alerts
                sent_alerts: list[Alert] = mock_notifier_instance.send_alerts.call_args[0][0]
                self.assertEqual(len(sent_alerts), 2)

                sent_areas = {alert.area for alert in sent_alerts}
                self.assertIn("東京都千代田区", sent_areas)
                self.assertIn("東京都新宿区", sent_areas)
                self.assertNotIn("東京都八王子市", sent_areas)

                # --- Second run: No new alerts should be sent ---
                mock_notifier_instance.send_alerts.reset_mock()
                sent_count_again = pipeline_once("http://dummy.url/test.xml")

                # Assert that no new alerts were sent
                self.assertEqual(sent_count_again, 0)
                mock_notifier_instance.send_alerts.assert_not_called()
