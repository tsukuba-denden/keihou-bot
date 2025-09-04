from __future__ import annotations

import os
from typing import Iterable, Optional

import discord

from .models import Alert


class DiscordNotifier:
    """Send alert messages to Discord.

    Supports two modes:
      1) Webhook (recommended): set DISCORD_WEBHOOK_URL
      2) Bot token + channel ID: set DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID
    """

    def __init__(
        self,
        token: Optional[str] = None,
        channel_id: Optional[int] = None,
        webhook_url: Optional[str] = None,
    ) -> None:
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
        self.token = token or os.getenv("DISCORD_BOT_TOKEN")
        self.channel_id = channel_id or int(os.getenv("DISCORD_CHANNEL_ID", "0"))

    def _format_alert(self, a: Alert) -> str:
        return (
            f"【{a.category} / {a.severity}】{a.title}\n"
            f"対象: {a.ward or a.area}\n発表: {a.issued_at.isoformat()}\n"
            + (f"詳細: {a.link}\n" if a.link else "")
        )

    def _send_via_webhook(self, messages: list[str]) -> None:
        from discord import SyncWebhook

        if not self.webhook_url:
            raise RuntimeError("DISCORD_WEBHOOK_URL is not set")
        webhook = SyncWebhook.from_url(self.webhook_url)
        for msg in messages:
            webhook.send(msg)

    def send_alerts(self, alerts: Iterable[Alert]) -> None:
        msgs = [self._format_alert(a) for a in alerts]
        if not msgs:
            return

        # Prefer webhook
        if self.webhook_url:
            self._send_via_webhook(msgs)
            return

        # As a minimal fallback, require webhook.
        # Bot-token based sending can be added if needed later.
        raise RuntimeError("Discord not configured. Set DISCORD_WEBHOOK_URL for sending.")
