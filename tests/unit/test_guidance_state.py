from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path
import tempfile

from src.guidance_state import GuidanceController
from src.models import SchoolGuidance


def make_guidance(dp: str, status: str = "平常授業") -> SchoolGuidance:
    return SchoolGuidance(
        date="2024-01-01",
        decision_point=dp,
        weekday=1,
        status=status,
        attend_time=None,
        notes=[],
    )


def jst(year, month, day, hour, minute):
    # return UTC time that corresponds to JST given
    jst_dt = datetime(year, month, day, hour, minute, tzinfo=timezone.utc) - timedelta(hours=9)
    return jst_dt


def test_send_once_at_each_decision_point():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "state.json"
        ctl = GuidanceController(path)

        # 無警報日の06/08/10は送られない
        assert not ctl.should_send(guidance=make_guidance("06"), has_target=False, now=jst(2024,1,1,6,0))
        assert not ctl.should_send(guidance=make_guidance("08"), has_target=False, now=jst(2024,1,1,8,0))
        assert not ctl.should_send(guidance=make_guidance("10"), has_target=False, now=jst(2024,1,1,10,0))

        # その後、対象警報が出現した日には DP 送信が有効化される
        assert ctl.should_send(guidance=make_guidance("06"), has_target=True, now=jst(2024,1,2,6,0))
        # 同じDPは一度だけ
        assert not ctl.should_send(guidance=make_guidance("06"), has_target=True, now=jst(2024,1,2,6,5))
        # 08, 10 はそれぞれ初回送信される
        assert ctl.should_send(guidance=make_guidance("08"), has_target=True, now=jst(2024,1,2,8,0))
        assert ctl.should_send(guidance=make_guidance("10"), has_target=True, now=jst(2024,1,2,10,0))


def test_flip_between_6_and_10_triggers_update():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "state.json"
        ctl = GuidanceController(path)
        # 初期（06直後）：無警報なら送らない
        assert not ctl.should_send(guidance=make_guidance("06"), has_target=False, now=jst(2024,1,1,6,0))
        # 同日ののちに対象が出現したケース（06の再評価が来たタイミングであれば初回扱いで送る）
        assert ctl.should_send(guidance=make_guidance("06"), has_target=True, now=jst(2024,1,1,6,5))
        # 8:15に対象が発生 → 追加配信
        assert ctl.should_send(guidance=make_guidance("08"), has_target=True, now=jst(2024,1,1,8,15))
        # 同じ状態では配信しない
        assert not ctl.should_send(guidance=make_guidance("08"), has_target=True, now=jst(2024,1,1,8,20))
        # 9:40に解除 → 更新配信
        assert ctl.should_send(guidance=make_guidance("08"), has_target=False, now=jst(2024,1,1,9,40))
        # 10:00は決定ポイントなので必ず配信
        assert ctl.should_send(guidance=make_guidance("10"), has_target=False, now=jst(2024,1,1,10,0))
