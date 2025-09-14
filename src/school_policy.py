from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
import os
from typing import Iterable

from .models import Alert, SchoolGuidance

# 対象となる警報キーワード（名称に含まれる場合にカウント）
TARGET_WARNINGS = ("暴風雪", "大雨", "洪水", "暴風", "大雪")


def _is_target_warning(alert: Alert) -> bool:
    """対象5種の警報（および特別警報を含む）かを判定。

    - Kind/Name に対象語が含まれ、かつ "警報" または "特別警報" を含む
    - 注意報は対象外
    """
    name = (alert.category or "").strip()
    sev = (alert.severity or "").strip()
    if "注意報" in sev:
        return False
    if not any(key in name for key in TARGET_WARNINGS):
        return False
    return ("警報" in name) or ("特別警報" in name) or ("警報" in sev) or ("特別警報" in sev)


def _jst_now(now: datetime | None = None) -> datetime:
    # Pythonの標準でJSTタイムゾーンを持たないため、UTCから+9時間で近似
    # 既にtimezone awareなUTCが渡る前提はないので、そのまま扱う
    if now is None:
        n = datetime.now(timezone.utc)
    else:
        n = now
    # aware datetime を JST 相当に変換（固定オフセット +9h）
    return (n.astimezone(timezone.utc) + timedelta(hours=9))


def decide_school_guidance(
    alerts: Iterable[Alert], *, now: datetime | None = None
) -> SchoolGuidance:
    """与えられたアラート群（東京23区向けにフィルタ済みを想定）から、現時点の登校ガイダンスを決定する。

    ルール要約：
      - 6時時点: 1つでも対象警報 → 自宅待機 / すべて解除 → 平常授業
      - 8時時点: 1つでも対象警報 → 月土=自宅学習、火水木金=自宅待機 / 解除 → 第3時限から授業
      - 10時時点: 1つでも対象警報 → 自宅学習 / 解除 → 火水木金=午後から授業（※月土は要確認）
    """
    jst = _jst_now(now)
    hhmm = jst.strftime("%H%M")
    weekday = jst.weekday()  # Mon=0..Sun=6
    date_str = jst.strftime("%Y-%m-%d")

    # 判定対象のフラグ
    has_target = any(_is_target_warning(a) and getattr(a, "status", "active") != "cancelled" for a in alerts)

    # 登校時刻の既定（環境変数で調整可能）
    # 既定値は学校の運用に合わせる（ユーザー提供値）
    normal_time = os.getenv("SCHOOL_NORMAL_TIME", "08:10")  # 平常授業の登校時刻
    period3_time = os.getenv("SCHOOL_PERIOD3_TIME", "10:20")  # 第3時限開始
    afternoon_time = os.getenv("SCHOOL_AFTERNOON_START", "13:10")  # 5時限（午後から）

    notes: list[str] = []
    notes.append("6〜8時の登校中に警報が発令された場合は、自宅にもどって待機してください。")
    notes.append("東京23区外の通学区域に警報が出ている場合、遅刻・欠席扱いにはなりません。")

    # 決定ポイント
    if hhmm < "0600":
        # 事前案内：6時時点の判定が確定ではない
        status = "参考: 6時の判定前"
        attend_time = None
        decision_point = "pre6"
    elif hhmm < "0800":
        # 6時判定
        decision_point = "06"
        if has_target:
            status = "自宅待機"
            attend_time = None
        else:
            status = "平常授業"
            attend_time = normal_time
    elif hhmm < "1000":
        # 8時判定
        decision_point = "08"
        if has_target:
            if weekday in (0, 5):  # Mon or Sat
                status = "自宅学習"
                attend_time = None
            else:
                status = "自宅待機"
                attend_time = None
        else:
            status = "第3時限から授業"
            attend_time = period3_time
    else:
        # 10時判定
        decision_point = "10"
        if has_target:
            status = "自宅学習"
            attend_time = None
        else:
            if weekday in (1, 2, 3, 4):  # Tue-Fri
                status = "午後から授業"
                attend_time = afternoon_time
            else:
                # 原文に記載なし → 暫定で自宅学習継続（要確認）
                status = "自宅学習"
                attend_time = None

    return SchoolGuidance(
        date=date_str,
        decision_point=decision_point,
        weekday=weekday,
        status=status,
        attend_time=attend_time,
        notes=notes,
    )
