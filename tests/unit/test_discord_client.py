from __future__ import annotations

import os
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from src.discord_client import DiscordNotifier
from src.models import Alert


def make_alert(**kwargs) -> Alert:
    """Helper function to create test alerts."""
    defaults = {
        "id": "test-alert-id",
        "title": "大雨警報",
        "area": "東京都千代田区",
        "ward": "千代田区",
        "category": "気象警報",
        "severity": "警報",
        "issued_at": datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        "expires_at": None,
        "link": None,
    }
    defaults.update(kwargs)
    return Alert(**defaults)


def test_init_with_webhook_url():
    """Test initialization with webhook URL."""
    webhook_url = "https://discord.com/api/webhooks/123/abc"
    notifier = DiscordNotifier(webhook_url=webhook_url)

    assert notifier.webhook_url == webhook_url
    assert notifier.token is None
    assert notifier.channel_id == 0


def test_init_with_bot_token_and_channel():
    """Test initialization with bot token and channel ID."""
    token = "bot_token_123"
    channel_id = 123456789
    notifier = DiscordNotifier(token=token, channel_id=channel_id)

    assert notifier.token == token
    assert notifier.channel_id == channel_id
    assert notifier.webhook_url is None


def test_init_with_environment_variables():
    """Test initialization from environment variables."""
    with patch.dict(
        os.environ,
        {
            "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/env/test",
            "DISCORD_BOT_TOKEN": "env_bot_token",
            "DISCORD_CHANNEL_ID": "987654321",
        },
    ):
        notifier = DiscordNotifier()

        assert notifier.webhook_url == "https://discord.com/api/webhooks/env/test"
        assert notifier.token == "env_bot_token"
        assert notifier.channel_id == 987654321


def test_init_with_missing_channel_id_env():
    """Test initialization with missing DISCORD_CHANNEL_ID environment variable."""
    with patch.dict(os.environ, {"DISCORD_BOT_TOKEN": "env_bot_token"}, clear=True):
        notifier = DiscordNotifier()

        assert notifier.channel_id == 0


def test_format_alert_basic():
    """Test basic alert formatting."""
    notifier = DiscordNotifier()
    alert = make_alert()

    formatted = notifier._format_alert(alert)

    expected = "【気象警報 / 警報】大雨警報\n" "対象: 千代田区\n発表: 2024-01-01T12:00:00+00:00\n"
    assert formatted == expected


def test_format_alert_with_link():
    """Test alert formatting with link."""
    notifier = DiscordNotifier()
    alert = make_alert(link="https://example.com/alert")

    formatted = notifier._format_alert(alert)

    expected = (
        "【気象警報 / 警報】大雨警報\n"
        "対象: 千代田区\n発表: 2024-01-01T12:00:00+00:00\n"
        "詳細: https://example.com/alert\n"
    )
    assert formatted == expected


def test_format_alert_without_ward():
    """Test alert formatting when ward is None, using area instead."""
    notifier = DiscordNotifier()
    alert = make_alert(ward=None, area="神奈川県横浜市")

    formatted = notifier._format_alert(alert)

    expected = (
        "【気象警報 / 警報】大雨警報\n" "対象: 神奈川県横浜市\n発表: 2024-01-01T12:00:00+00:00\n"
    )
    assert formatted == expected


@patch("discord.SyncWebhook")
def test_send_via_webhook_success(mock_webhook_class):
    """Test successful webhook sending."""
    mock_webhook = Mock()
    mock_webhook_class.from_url.return_value = mock_webhook

    webhook_url = "https://discord.com/api/webhooks/123/abc"
    notifier = DiscordNotifier(webhook_url=webhook_url)

    messages = ["Message 1", "Message 2"]
    notifier._send_via_webhook(messages)

    mock_webhook_class.from_url.assert_called_once_with(webhook_url)
    assert mock_webhook.send.call_count == 2
    mock_webhook.send.assert_any_call("Message 1")
    mock_webhook.send.assert_any_call("Message 2")


def test_send_via_webhook_no_url():
    """Test webhook sending without URL raises error."""
    notifier = DiscordNotifier()

    with pytest.raises(RuntimeError, match="DISCORD_WEBHOOK_URL is not set"):
        notifier._send_via_webhook(["test message"])


@patch("discord.SyncWebhook")
def test_send_alerts_empty_list(mock_webhook_class):
    """Test sending empty alerts list does nothing."""
    webhook_url = "https://discord.com/api/webhooks/123/abc"
    notifier = DiscordNotifier(webhook_url=webhook_url)

    notifier.send_alerts([])

    # Should not call webhook at all
    mock_webhook_class.from_url.assert_not_called()


@patch("discord.SyncWebhook")
def test_send_alerts_with_webhook(mock_webhook_class):
    """Test sending alerts via webhook."""
    mock_webhook = Mock()
    mock_webhook_class.from_url.return_value = mock_webhook

    webhook_url = "https://discord.com/api/webhooks/123/abc"
    notifier = DiscordNotifier(webhook_url=webhook_url)

    alerts = [
        make_alert(title="警報1", ward="千代田区"),
        make_alert(title="警報2", ward="新宿区"),
    ]

    notifier.send_alerts(alerts)

    mock_webhook_class.from_url.assert_called_once_with(webhook_url)
    assert mock_webhook.send.call_count == 2


def test_send_alerts_no_configuration():
    """Test sending alerts without proper configuration raises error."""
    notifier = DiscordNotifier()

    alerts = [make_alert()]

    with pytest.raises(
        RuntimeError, match="Discord not configured. Set DISCORD_WEBHOOK_URL for sending."
    ):
        notifier.send_alerts(alerts)


@patch("discord.SyncWebhook")
def test_send_alerts_prefers_webhook(mock_webhook_class):
    """Test that webhook is preferred over bot token when both are available."""
    mock_webhook = Mock()
    mock_webhook_class.from_url.return_value = mock_webhook

    webhook_url = "https://discord.com/api/webhooks/123/abc"
    notifier = DiscordNotifier(webhook_url=webhook_url, token="bot_token", channel_id=123456789)

    alerts = [make_alert()]
    notifier.send_alerts(alerts)

    # Should use webhook, not bot token
    mock_webhook_class.from_url.assert_called_once_with(webhook_url)
    mock_webhook.send.assert_called_once()
