from __future__ import annotations

import os
import discord
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
    """Test successful webhook sending with embeds."""
    mock_webhook = Mock()
    mock_webhook_class.from_url.return_value = mock_webhook

    webhook_url = "https://discord.com/api/webhooks/123/abc"
    notifier = DiscordNotifier(webhook_url=webhook_url)

    e1 = discord.Embed(title="Message 1")
    e2 = discord.Embed(title="Message 2")
    notifier._send_via_webhook([e1, e2])

    mock_webhook_class.from_url.assert_called_once_with(webhook_url)
    assert mock_webhook.send.call_count == 2
    mock_webhook.send.assert_any_call(embed=e1)
    mock_webhook.send.assert_any_call(embed=e2)


def test_send_via_webhook_no_url():
    """Test webhook sending without URL raises error."""
    notifier = DiscordNotifier()

    with pytest.raises(RuntimeError, match="DISCORD_WEBHOOK_URL is not set"):
        notifier._send_via_webhook([discord.Embed(title="test")])


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
    """Test sending alerts via webhook as embeds."""
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
    # Ensure embeds were sent
    for call in mock_webhook.send.call_args_list:
        assert isinstance(call.kwargs.get("embed"), discord.Embed)


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


def test_create_embed_from_alert_basic():
    """T001: Create a failing test for embed helper based on contract.

    Asserts that `_create_embed_from_alert(alert)` returns a discord.Embed with
    title, description, color, and timestamp mapped as specified.
    """
    notifier = DiscordNotifier()
    alert = make_alert(
        title="大雨警報",
        category="気象警報",
        ward="千代田区",
        severity="Warning",  # Use contract's severity terminology for color mapping
        link="https://example.com/alert",
    )

    # Method not yet implemented; this test should fail initially.
    embed = notifier._create_embed_from_alert(alert)  # type: ignore[attr-defined]

    assert isinstance(embed, discord.Embed)
    assert embed.title == alert.title
    # URL should be set when provided
    assert embed.url == alert.link
    # Timestamp should match alert.issued_at (aware datetime)
    assert embed.timestamp == alert.issued_at

    # Color mapping per contract: Warning -> orange
    assert embed.colour == discord.Color.orange()

    # Description should contain Category and Area lines as per contract format
    assert "**Category**: 気象警報" in (embed.description or "")
    assert "**Area**: 千代田区" in (embed.description or "")


def test_create_embed_truncates_long_description():
    """T004: Long description should be truncated and end with ellipsis."""
    notifier = DiscordNotifier()
    very_long_ward = "A" * 5000  # exceed 4096 limit when included in description
    alert = make_alert(ward=very_long_ward, severity="Advisory")

    embed = notifier._create_embed_from_alert(alert)

    assert isinstance(embed, discord.Embed)
    assert embed.description is not None
    # Discord embed description hard limit: 4096
    assert len(embed.description) <= 4096
    assert embed.description.endswith("...")
