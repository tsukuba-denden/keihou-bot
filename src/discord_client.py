from __future__ import annotations

import logging
import os
import sys
from typing import Iterable, Optional

import discord
# Expose alias for tests that patch src.discord_client.SyncWebhook, and keep original for comparison
SyncWebhook = getattr(discord, "SyncWebhook", None)  # type: ignore[assignment]
_ORIGINAL_DISCORD_SYNC_WEBHOOK = SyncWebhook
from discord.errors import HTTPException

from .models import Alert, SchoolGuidance, RoleMentionSetting

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

    def _get_sync_webhook_cls(self):  # type: ignore[no-untyped-def]
        """Resolve SyncWebhook class that works with tests patching either
        src.discord_client.SyncWebhook or discord.SyncWebhook.
        """
        # Evaluate both module-level and discord module class.
        mod_attr = getattr(sys.modules[__name__], "SyncWebhook", None)
        disc_attr = getattr(discord, "SyncWebhook")
        # Prefer module-level only if it has been overridden from the original
        if mod_attr is not None and mod_attr is not _ORIGINAL_DISCORD_SYNC_WEBHOOK:
            return mod_attr
        # Otherwise use current discord.SyncWebhook (unit tests patch this)
        return disc_attr

    def _send_via_webhook(self, embeds: list[discord.Embed]) -> None:
        if not self.webhook_url:
            logger.error("Webhook URL is not set, cannot send alerts.")
            raise RuntimeError("DISCORD_WEBHOOK_URL is not set")

        wh_cls = self._get_sync_webhook_cls()
        webhook = wh_cls.from_url(self.webhook_url)
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

    # --- School guidance ---
    def _create_guidance_embed(self, g: SchoolGuidance) -> discord.Embed:
        title = "登校ガイダンス"
        dp = {"pre6": "6時判定前", "06": "6時判定", "08": "8時判定", "10": "10時判定"}.get(
            g.decision_point, g.decision_point
        )
        # 表示専用の結果行を整形（例: 8時判定で自宅学習 → 「少なくとも10時までは自宅学習」）
        def _format_result_line(g: SchoolGuidance) -> str:
            # 6時判定時は8時までに再判定があるため、待機系は「少なくとも8時まで」を明示
            if g.decision_point == "06" and g.status == "自宅待機":
                return "結果: 少なくとも8時までは自宅待機"
            # 8時判定の段階で自宅学習が確定しているのは月・土のみ（ポリシー）。
            # この場合、10時の最終判定までは継続のため、「少なくとも10時までは自宅学習」と表現する。
            if g.status == "自宅学習" and g.decision_point == "08":
                return "結果: 少なくとも10時までは自宅学習"
            # それ以外は従来通りのステータスをそのまま表示
            return f"結果: {g.status}"

        desc_lines = [
            f"日付: {g.date}",
            f"判定: {dp}",
            _format_result_line(g),
        ]
        if g.attend_time:
            desc_lines.append(f"登校目安: {g.attend_time}")
        if g.notes:
            desc_lines.extend(["", *g.notes])

        embed = discord.Embed(
            title=title,
            description="\n".join(desc_lines),
            colour=discord.Color.blue(),
        )
        return embed

    def send_school_guidance(self, guidance: SchoolGuidance) -> None:
        embed = self._create_guidance_embed(guidance)
        # Determine if role mention should be prefixed to content
        content_prefix = ""
        try:
            baseline = os.getenv("SCHOOL_NORMAL_TIME", "08:10")
            today_time = guidance.attend_time or ""
            role_setting = RoleMentionSetting.from_env()
            should_mention = (
                role_setting.enabled
                and bool(role_setting.role_id)
                and bool(today_time)
                and today_time != baseline
            )
            if should_mention:
                content_prefix = f"<@&{role_setting.role_id}> "
        except Exception as e:  # safe guard
            logger.warning("Failed to evaluate role mention condition: %s", e)

        if self.dry_run:
            logger.info("[DRY-RUN] Would send school guidance: %s", guidance.status)
            if content_prefix:
                logger.info("[DRY-RUN] Would mention role with content prefix: %s", content_prefix.strip())
            return

        if self.webhook_url:
            # Send via webhook with optional content prefix
            wh_cls = self._get_sync_webhook_cls()
            webhook = wh_cls.from_url(self.webhook_url)
            try:
                if content_prefix:
                    webhook.send(content=content_prefix, embed=embed)
                else:
                    webhook.send(embed=embed)
            except HTTPException as e:
                logger.exception("Failed to send school guidance via webhook: %s", e)
            return

        logger.error("Discord not configured for sending school guidance.")
        raise RuntimeError("Discord not configured. Set DISCORD_WEBHOOK_URL for sending.")
