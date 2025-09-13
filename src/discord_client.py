from __future__ import annotations

import logging
import os
from typing import Iterable, Optional

import discord
from discord.errors import HTTPException

from .models import Alert

logger = logging.getLogger(__name__)


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
        dry_run: Optional[bool] = None,
    ) -> None:
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
        self.token = token or os.getenv("DISCORD_BOT_TOKEN")
        self.channel_id = channel_id or int(os.getenv("DISCORD_CHANNEL_ID", "0"))
        # Allow dry-run via parameter or env var
        env_dry = os.getenv("DRY_RUN", "").lower() in {"1", "true", "yes", "on"}
        self.dry_run = env_dry if dry_run is None else dry_run

        if not self.webhook_url and not (self.token and self.channel_id) and not self.dry_run:
            logger.warning("Discord notifier is not configured. Set DISCORD_WEBHOOK_URL.")

    def _format_alert(self, a: Alert) -> str:
        return (
            f"【{a.category} / {a.severity}】{a.title}\n"
            f"対象: {a.ward or a.area}\n発表: {a.issued_at.isoformat()}\n"
            + (f"詳細: {a.link}\n" if a.link else "")
        )

    def _send_via_webhook(self, messages: list[str]) -> None:
        from discord import SyncWebhook

        if not self.webhook_url:
            logger.error("Webhook URL is not set, cannot send alerts.")
            raise RuntimeError("DISCORD_WEBHOOK_URL is not set")

        webhook = SyncWebhook.from_url(self.webhook_url)
        logger.info(f"Sending {len(messages)} alerts via webhook.")
        for i, msg in enumerate(messages):
            try:
                webhook.send(msg)
                logger.debug(f"Sent message {i+1}/{len(messages)} successfully.")
            except HTTPException as e:
                logger.exception(f"Failed to send message {i+1} via webhook: {e}")
        logger.info("Finished sending alerts via webhook.")

    def send_alerts(self, alerts: Iterable[Alert]) -> None:
        msgs = [self._format_alert(a) for a in alerts]
        if not msgs:
            logger.info("No alert messages to send.")
            return

        if self.dry_run:
            logger.info("[DRY-RUN] Would send the following alerts:")
            for i, m in enumerate(msgs, 1):
                logger.info("[DRY-RUN %d/%d]\n%s", i, len(msgs), m)
            return

        # Prefer webhook
        if self.webhook_url:
            self._send_via_webhook(msgs)
            return

        logger.error("Discord not configured for sending alerts.")
        raise RuntimeError("Discord not configured. Set DISCORD_WEBHOOK_URL for sending.")
