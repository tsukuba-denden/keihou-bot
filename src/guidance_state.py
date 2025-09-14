from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from .models import SchoolGuidance


def _to_jst(dt: datetime) -> datetime:
    return dt.astimezone(timezone.utc) + timedelta(hours=9)


@dataclass
class DailyState:
    date: str
    last_sent_dp: Optional[str] = None
    last_seen_has_target: Optional[bool] = None
    any_seen_target_today: bool = False


class GuidanceController:
    """Decide whether to send school guidance based on time and state transitions.

    Rules:
      - Always send once when entering decision points 06/08/10 on that date.
      - Between 06:00 and 10:00 JST, if target-warning presence flips (add/remove), send update.
      - Persist minimal state per date to avoid duplicates.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> Optional[DailyState]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return DailyState(
                date=str(data.get("date", "")),
                last_sent_dp=data.get("last_sent_dp"),
                last_seen_has_target=data.get("last_seen_has_target"),
                any_seen_target_today=bool(data.get("any_seen_target_today", False)),
            )
        except Exception:
            return None

    def _write(self, st: DailyState) -> None:
        # Ensure parent directory exists (defensive on some platforms)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "date": st.date,
            "last_sent_dp": st.last_sent_dp,
            "last_seen_has_target": st.last_seen_has_target,
            "any_seen_target_today": st.any_seen_target_today,
        }
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def should_send(self, *, guidance: SchoolGuidance, has_target: bool, now: datetime) -> bool:
        jst = _to_jst(now)
        hhmm = jst.strftime("%H%M")
        date_str = jst.strftime("%Y-%m-%d")

        st = self._read()
        if not st or st.date != date_str:
            st = DailyState(date=date_str, last_sent_dp=None, last_seen_has_target=None, any_seen_target_today=False)

        decision_point = guidance.decision_point

        # 無警報日の定時配信を抑止するため、当日一度でも対象警報を観測した日だけ DP送信
        # Condition A: First send at 06/08/10 for the date (only if has ever seen target today)
        if decision_point in {"06", "08", "10"} and st.last_sent_dp != decision_point and (st.any_seen_target_today or has_target):
            st.last_sent_dp = decision_point
            st.last_seen_has_target = has_target
            st.any_seen_target_today = st.any_seen_target_today or has_target
            self._write(st)
            return True

        # Condition B: Between 06:00 and 09:59, flip of has_target triggers update
        if "0600" <= hhmm < "1000":
            if st.last_seen_has_target is None:
                # Record without sending (not a flip yet)
                st.last_seen_has_target = has_target
                st.any_seen_target_today = st.any_seen_target_today or has_target
                self._write(st)
                return False
            if st.last_seen_has_target != has_target:
                st.last_seen_has_target = has_target
                st.any_seen_target_today = st.any_seen_target_today or has_target
                # Keep last_sent_dp as-is; send update
                self._write(st)
                return True

        # No conditions met
        # Update last_seen_has_target for tracking
        if st.last_seen_has_target != has_target or (has_target and not st.any_seen_target_today):
            st.last_seen_has_target = has_target
            st.any_seen_target_today = st.any_seen_target_today or has_target
            self._write(st)
        return False
