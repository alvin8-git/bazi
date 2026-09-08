"""sxtwl wrapper: pillars, 節氣, true-solar-time correction.

閏月/leap-month and all lunar-calendar edge cases are delegated entirely to
sxtwl — no custom lunar logic here.

Singapore timezone history matters for BaZi: clock time was UTC+7:30 before
1982-01-01 and UTC+8:00 from then on. Pre-1982 births (e.g. members born pre-1982) must use the historical offset before the solar correction is applied.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta

import sxtwl

from .wuxing import BRANCHES, STEMS

SG_LON = 103.8517

# sxtwl jqmc ordering: index 0 = 冬至, odd indices are the 12 節 (month boundaries)
JIEQI_NAMES = ["冬至", "小寒", "大寒", "立春", "雨水", "驚蟄", "春分", "清明", "穀雨",
               "立夏", "小滿", "芒種", "夏至", "小暑", "大暑", "立秋", "處暑", "白露",
               "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"]


def sg_utc_offset_hours(d: date) -> float:
    """Singapore civil-time UTC offset for a given date (post-1930s births)."""
    return 7.5 if d < date(1982, 1, 1) else 8.0


def equation_of_time_minutes(d: date) -> float:
    """Approximate equation of time (minutes, positive = sundial ahead)."""
    n = d.timetuple().tm_yday
    b = 2 * math.pi * (n - 81) / 364.0
    return 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)


def true_solar_datetime(local: datetime, lon: float = SG_LON,
                        utc_offset_hours: float | None = None) -> datetime:
    """Convert civil clock time to true solar time at longitude `lon`."""
    if utc_offset_hours is None:
        utc_offset_hours = sg_utc_offset_hours(local.date())
    utc = local - timedelta(hours=utc_offset_hours)
    mean_solar = utc + timedelta(hours=lon / 15.0)
    return mean_solar + timedelta(minutes=equation_of_time_minutes(local.date()))


def hour_branch_index(hour: int) -> int:
    """0-23h → branch index (子=0). 23:00-00:59 is 子."""
    return ((hour + 1) // 2) % 12


@dataclass(frozen=True)
class GZ:
    stem: str
    branch: str

    def __str__(self) -> str:  # e.g. 丙辰
        return self.stem + self.branch


def _gz(obj) -> GZ:
    return GZ(STEMS[obj.tg], BRANCHES[obj.dz])


def pillars_for(dt: datetime) -> dict:
    """Four pillars for an exact (already policy-adjusted) datetime.

    Year pillar changes at 立春; month pillars at the 12 節 — both via sxtwl.
    早/晚子時: hour 23 uses the NEXT day's stem for the 子 hour (子時換日 on the
    hour pillar only; day pillar stays with the civil date — 早晚子 school).
    ponytail: single school implemented; add a policy flag when another school is wanted.
    """
    day = sxtwl.fromSolar(dt.year, dt.month, dt.day)
    ygz, mgz, dgz = _gz(day.getYearGZ()), _gz(day.getMonthGZ()), _gz(day.getDayGZ())
    hour_day = day
    if dt.hour == 23:
        nxt = dt + timedelta(hours=2)
        hour_day = sxtwl.fromSolar(nxt.year, nxt.month, nxt.day)
    hgz = _gz(hour_day.getHourGZ(dt.hour))
    return {"year": ygz, "month": mgz, "day": dgz, "hour": hgz}


def _walk_to_jie(d: date, forward: bool, limit: int = 40) -> tuple[date, str]:
    """Nearest 節 (odd jqmc index) on/after (forward) or on/before (backward) d."""
    step = 1 if forward else -1
    cur = d
    for _ in range(limit):
        cur = cur + timedelta(days=step)
        day = sxtwl.fromSolar(cur.year, cur.month, cur.day)
        if day.hasJieQi() and day.getJieQi() % 2 == 1:
            return cur, JIEQI_NAMES[day.getJieQi()]
    raise RuntimeError("no 節 found within 40 days — should be impossible")


def dayun_start_age(birth: date, forward: bool) -> tuple[float, str]:
    """起運 age in years: days to the nearest 節 / 3 (1 day = 4 months)."""
    jie_date, jie_name = _walk_to_jie(birth, forward)
    days = abs((jie_date - birth).days)
    return days / 3.0, jie_name
