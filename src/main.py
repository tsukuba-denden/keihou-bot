from __future__ import annotations

import os
from datetime import timezone, datetime
from pathlib import Path
from typing import Iterable

from apscheduler.schedulers.background import BackgroundScheduler

from .discord_client import DiscordNotifier
from .filter import pick_23_wards
from .jma_client import JmaClient
from .jma_parser import parse_jma_xml
from .storage import JsonStorage


DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
SENT_IDS_FILE = DATA_DIR / "sent_ids.json"


def pipeline_once(jma_url: str) -> int:
    client = JmaClient(jma_url)
    xml = client.fetch()
    alerts = parse_jma_xml(xml)
    tokyo_alerts = pick_23_wards(alerts)

    storage = JsonStorage(SENT_IDS_FILE)
    new_alerts = [a for a in tokyo_alerts if not storage.has(a.id)]
    if not new_alerts:
        return 0

    DiscordNotifier().send_alerts(new_alerts)
    storage.add_many(a.id for a in new_alerts)
    return len(new_alerts)


def run_scheduler(jma_url: str, interval_minutes: int = 5) -> None:
    scheduler = BackgroundScheduler(timezone=timezone.utc)

    def job():
        try:
            count = pipeline_once(jma_url)
            print(f"[{datetime.now(timezone.utc).isoformat()}] Sent {count} new alerts")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Error: {exc}")

    scheduler.add_job(job, "interval", minutes=interval_minutes, next_run_time=datetime.now(timezone.utc))
    scheduler.start()

    try:
        import time

        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        scheduler.shutdown()


if __name__ == "__main__":
    url = os.getenv("JMA_FEED_URL", "https://www.data.jma.go.jp/developer/xml/feed/extra.xml")
    run_scheduler(url, interval_minutes=int(os.getenv("FETCH_INTERVAL_MIN", "5")))
