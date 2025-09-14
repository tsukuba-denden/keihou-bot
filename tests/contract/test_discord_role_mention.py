from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import discord
import pytest

from src.discord_client import DiscordNotifier
from src.models import SchoolGuidance


class DummyWebhook:
    def __init__(self):
        self.sent = []

    def send(self, *, content: str | None = None, embed: discord.Embed | None = None):
        # Record the payload for assertions
        self.sent.append({"content": content, "embed": embed})


@pytest.fixture(autouse=True)
def _env_role_id(monkeypatch):
    # Default: role id is set for tests; overridable in specific tests
    monkeypatch.setenv("ROLE_ID", "123456789012345678")
    monkeypatch.setenv("DRY_RUN", "false")  # we want to pass through to webhook path
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://example.com/webhook")


@patch("src.discord_client.SyncWebhook")
def test_role_mention_when_time_differs(sync_webhook_mock):
    # Arrange: baseline != today
    wh = DummyWebhook()
    sync_webhook_mock.from_url.return_value = wh

    g = SchoolGuidance(
        date="2024-01-02",
        decision_point="06",
        weekday=2,
        status="平常授業",
        attend_time="09:00",  # differs from default baseline 08:10
        notes=["note"],
    )

    notifier = DiscordNotifier(dry_run=False)

    # Act
    notifier.send_school_guidance(g)

    # Assert
    assert len(wh.sent) == 1
    payload = wh.sent[0]
    assert isinstance(payload["embed"], discord.Embed)
    assert payload["content"].startswith("<@&123456789012345678>")
    # exactly once
    assert payload["content"].count("<@&123456789012345678>") == 1


@patch("src.discord_client.SyncWebhook")
def test_no_role_mention_when_same_as_baseline(sync_webhook_mock, monkeypatch):
    # Arrange: baseline == today
    wh = DummyWebhook()
    sync_webhook_mock.from_url.return_value = wh

    # Explicit baseline
    monkeypatch.setenv("SCHOOL_NORMAL_TIME", "08:30")

    g = SchoolGuidance(
        date="2024-01-02",
        decision_point="06",
        weekday=2,
        status="平常授業",
        attend_time="08:30",  # same as baseline
        notes=["note"],
    )

    notifier = DiscordNotifier(dry_run=False)

    # Act
    notifier.send_school_guidance(g)

    # Assert
    assert len(wh.sent) == 1
    payload = wh.sent[0]
    assert isinstance(payload["embed"], discord.Embed)
    assert (payload["content"] or "").strip() == ""
