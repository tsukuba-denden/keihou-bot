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

    def _create_embed_from_alert(self, alert: Alert) -> discord.Embed:  # T002
        """Create a Discord Embed from an Alert per the contract.

        Mapping:
        - title -> alert.title
        - url -> alert.link (if any)
        - timestamp -> alert.issued_at
        - color -> mapped from alert.severity
        - description -> "**Category**: {category}\n**Area**: {ward or area}\n\n" (+ optional body)
        """

        def _severity_to_color(severity: str) -> discord.Color:
            s = (severity or "").strip().lower()
            # English mapping (contract)
            if s == "emergency":
                return discord.Color.dark_red()
            if s == "warning":
                return discord.Color.orange()
            if s == "advisory":
                return discord.Color.gold()

            # Common Japanese severities
            if s in {"特別警報".lower(), "tokubetsu-keihou"}:
                return discord.Color.dark_red()
            if s in {"警報".lower(), "keihou", "warning"}:
                return discord.Color.orange()
            if s in {"注意報".lower(), "chuuihou", "advisory"}:
                return discord.Color.gold()

            return discord.Color.light_grey()

        # Build description core (category omitted as it's now the title)
        area_text = alert.ward or alert.area
        description_lines = [
            f"**Area**: {area_text}",
            "",
        ]
        description = "\n".join(description_lines)
        # T004: Truncate description to Discord's embed limit (4096 chars)
        MAX_DESC = 4096
        if len(description) > MAX_DESC:
            description = description[: MAX_DESC - 3] + "..."

        embed = discord.Embed(
            title=alert.category,
            description=description,
            url=alert.link or None,
            timestamp=alert.issued_at,
            colour=_severity_to_color(alert.severity),
        )
        return embed

    def _create_cancellation_embed(self, alert: Alert) -> discord.Embed:
        """Create a Discord Embed for cancellation per the contract specs/003-/contracts/discord_cancellation_embed.md.

        Structure:
        - title: "【解除】気象警報・注意報"
        - description: "以下の地域の警報・注意報は解除されました。"
        - color: green
        - fields: 地域, 解除された警報・注意報
        - footer: 気象庁 | JMA
        """
        embed = discord.Embed(
            title="【解除】気象警報・注意報",
            description="以下の地域の警報・注意報は解除されました。",
            colour=discord.Color.green(),
            url=alert.link or None,
            timestamp=alert.issued_at,
        )
        embed.add_field(name="地域", value=alert.ward or alert.area, inline=False)
        embed.add_field(name="解除された警報・注意報", value=alert.category, inline=False)
        embed.set_footer(text="気象庁 | JMA")
        return embed

    def _send_via_webhook(self, embeds: list[discord.Embed]) -> None:
        from discord import SyncWebhook

        if not self.webhook_url:
            logger.error("Webhook URL is not set, cannot send alerts.")
            raise RuntimeError("DISCORD_WEBHOOK_URL is not set")

        webhook = SyncWebhook.from_url(self.webhook_url)
        logger.info(f"Sending {len(embeds)} alerts via webhook.")
        for i, embed in enumerate(embeds):
            try:
                webhook.send(embed=embed)
                logger.debug(f"Sent embed {i+1}/{len(embeds)} successfully.")
            except HTTPException as e:
                logger.exception(f"Failed to send embed {i+1} via webhook: {e}")
        logger.info("Finished sending alerts via webhook.")

    def send_alerts(self, alerts: Iterable[Alert]) -> None:
        embeds = [self._create_embed_from_alert(a) for a in alerts]
        if not embeds:
            logger.info("No alert embeds to send.")
            return

        if self.dry_run:
            logger.info("[DRY-RUN] Would send the following alerts:")
            for i, e in enumerate(embeds, 1):
                logger.info("[DRY-RUN %d/%d] title=%s", i, len(embeds), e.title)
            return

        # Prefer webhook
        if self.webhook_url:
            self._send_via_webhook(embeds)
            return

        logger.error("Discord not configured for sending alerts.")
        raise RuntimeError("Discord not configured. Set DISCORD_WEBHOOK_URL for sending.")

    def send_cancellations(self, alerts: Iterable[Alert]) -> None:
        """Send cancellation embeds. Alerts should have status='cancelled'."""
        cancels = [a for a in alerts if getattr(a, "status", "active") == "cancelled"]
        if not cancels:
            logger.info("No cancellations to send.")
            return
        embeds = [self._create_cancellation_embed(a) for a in cancels]

        if self.dry_run:
            logger.info("[DRY-RUN] Would send %d cancellation alerts.", len(embeds))
            for i, e in enumerate(embeds, 1):
                logger.info("[DRY-RUN %d/%d] cancellation title=%s", i, len(embeds), e.title)
            return

        if self.webhook_url:
            self._send_via_webhook(embeds)
            return

        logger.error("Discord not configured for sending cancellation alerts.")
        raise RuntimeError("Discord not configured. Set DISCORD_WEBHOOK_URL for sending.")
