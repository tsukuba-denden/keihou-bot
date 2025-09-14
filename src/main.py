from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
import argparse
try:
    from dotenv import load_dotenv  # type: ignore[reportMissingImports]
except Exception:  # pragma: no cover - fallback if python-dotenv is unavailable
    def load_dotenv(*args, **kwargs):  # type: ignore[no-redef]
        return False
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler

from .discord_client import DiscordNotifier
from .filter import pick_23_wards
from .jma_client import JmaClient
from .jma_parser import parse_jma_xml
from .storage import JsonStorage
from .school_policy import decide_school_guidance
from .guidance_state import GuidanceController

logger = logging.getLogger(__name__)

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
SENT_IDS_FILE = DATA_DIR / "sent_ids.json"


def pipeline_once(
    jma_url: str,
    *,
    dry_run: bool = False,
    force_send: bool = False,
    no_store: bool = False,
) -> int:
    """
    Fetches, parses, filters, and sends new JMA alerts.

    Returns:
        The number of new alerts sent.
    """
    logger.info("Starting pipeline run...")
    client = JmaClient(jma_url)
    xml = client.fetch()
    alerts = parse_jma_xml(xml)
    logger.info(f"Parsed {len(alerts)} alerts from JMA feed.")

    tokyo_alerts = pick_23_wards(alerts)
    logger.info(f"Filtered down to {len(tokyo_alerts)} alerts for Tokyo's 23 wards.")

    # Partition by cancellation status
    cancellations = [a for a in tokyo_alerts if getattr(a, "status", "active") == "cancelled"]
    actives = [a for a in tokyo_alerts if getattr(a, "status", "active") != "cancelled"]

    storage = JsonStorage(SENT_IDS_FILE)
    guidance_controller = GuidanceController(DATA_DIR / "guidance_state.json")

    # Determine which to send
    if force_send:
        to_send_active = list(actives)
        to_send_cancel = list(cancellations)
    else:
        to_send_active = [a for a in actives if not storage.has(a.id)]
        # For cancellations, send if unseen or not yet marked cancelled
        to_send_cancel = [
            a for a in cancellations if (not storage.has(a.id)) or (storage.get_status(a.id) != "cancelled")
        ]

    total = 0
    notifier = DiscordNotifier(dry_run=dry_run)

    if to_send_active:
        logger.info("Found %d new active alerts to send.", len(to_send_active))
        notifier.send_alerts(to_send_active)
        total += len(to_send_active)
        if not no_store:
            storage.add_many((a.id for a in to_send_active), status="active")

    if to_send_cancel:
        logger.info("Found %d cancellations to send.", len(to_send_cancel))
        notifier.send_cancellations(to_send_cancel)
        total += len(to_send_cancel)
        if not no_store:
            # Update existing entries to cancelled if present; otherwise add as cancelled
            for a in to_send_cancel:
                if storage.has(a.id):
                    storage.update_status(a.id, "cancelled")
                else:
                    storage.add(a.id, status="cancelled")

    # 学校ガイダンス送信ポリシー：
    # - 6/8/10の各判定直後は必ず1回配信
    # - 6:00〜9:59の間、対象警報の有無が変化したら更新配信
    try:
        guidance = decide_school_guidance(tokyo_alerts)
        has_target = any(getattr(a, "status", "active") != "cancelled" for a in tokyo_alerts)
        should = guidance_controller.should_send(
            guidance=guidance, has_target=has_target, now=datetime.now(timezone.utc)
        )
        if force_send:
            should = True
        if should:
            notifier.send_school_guidance(guidance)
    except Exception as e:  # pylint: disable=broad-except-clause
        logger.exception("Failed to process/send school guidance: %s", e)

    if total == 0:
        logger.info("No new alerts to send.")
        return 0

    logger.info("Finished sending and recording alerts. Total sent: %d", total)
    return total


def run_scheduler(jma_url: str, interval_minutes: int = 5) -> None:
    """
    Sets up and runs the alert fetching job on a schedule.
    """
    scheduler = BackgroundScheduler(timezone=timezone.utc)

    def job():
        try:
            count = pipeline_once(jma_url)
            if count > 0:
                logger.info(f"Successfully sent {count} new alerts.")
        except Exception as exc:  # pylint: disable=broad-except-clause
            logger.exception(f"An error occurred in the pipeline: {exc}")

    scheduler.add_job(job, "interval", minutes=interval_minutes, next_run_time=datetime.now(timezone.utc))
    scheduler.start()
    logger.info(f"Scheduler started. Checking for new alerts every {interval_minutes} minutes.")

    try:
        import time

        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Scheduler shutting down...")
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully.")


if __name__ == "__main__":
    # Load .env (do not override existing env variables)
    load_dotenv(override=False)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    parser = argparse.ArgumentParser(description="Keihou-bot runner")
    parser.add_argument("--once", action="store_true", help="Run pipeline once and exit")
    parser.add_argument(
        "--simulate",
        type=str,
        default=None,
        help="Use a local XML file (path or file://) instead of fetching from network",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not send to Discord; log messages instead",
    )
    parser.add_argument(
        "--force-send",
        action="store_true",
        help="Send alerts even if they were already recorded (bypass duplicate check)",
    )
    parser.add_argument(
        "--no-store",
        action="store_true",
        help="Do not record sent alert IDs to storage",
    )

    args = parser.parse_args()

    if args.simulate:
        url = args.simulate
    else:
        url = os.getenv(
            "JMA_FEED_URL", "https://www.data.jma.go.jp/developer/xml/feed/extra.xml"
        )

    if args.once:
        count = pipeline_once(
            url,
            dry_run=args.dry_run or (os.getenv("DRY_RUN", "").lower() in {"1","true","yes","on"}),
            force_send=args.force_send,
            no_store=args.no_store,
        )
        logger.info("Run once finished. New alerts sent: %d", count)
    else:
        run_scheduler(url, interval_minutes=int(os.getenv("FETCH_INTERVAL_MIN", "5")))
