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

    storage = JsonStorage(SENT_IDS_FILE)
    if force_send:
        new_alerts = list(tokyo_alerts)
    else:
        new_alerts = [a for a in tokyo_alerts if not storage.has(a.id)]
    if not new_alerts:
        logger.info("No new alerts to send.")
        return 0

    logger.info(f"Found {len(new_alerts)} new alerts to send.")
    DiscordNotifier(dry_run=dry_run).send_alerts(new_alerts)
    if not no_store:
        storage.add_many(a.id for a in new_alerts)
    else:
        logger.info("No-store mode enabled; not recording sent IDs.")
    logger.info("Finished sending and recording new alerts.")
    return len(new_alerts)


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
