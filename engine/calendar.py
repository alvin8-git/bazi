"""sxtwl wrapper: pillars, 節氣, true-solar-time correction.

閏月/leap-month and all lunar-calendar edge cases are delegated entirely to
sxtwl — no custom lunar logic here.

Singapore timezone history matters for BaZi: clock time was UTC+7:30 before
1982-01-01 and UTC+8:00 from then on. Pre-1982 births (e.g. members born pre-1982) must use the historical offset before the solar correction is applied.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

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


def utc_offset_hours(local: datetime, tz: str) -> float | None:
    """Clock offset from UTC for a civil time in an IANA zone (daylight saving and history included).
    None when the zone database is missing on this host."""
    try:
        from zoneinfo import ZoneInfo
        off = ZoneInfo(tz).utcoffset(local)
    except Exception:
        return None
    return off.total_seconds() / 3600 if off is not None else None


def tz_database_available() -> bool:
    return utc_offset_hours(datetime(2020, 7, 1, 12), "America/New_York") == -4.0


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


BEIJING = timezone(timedelta(hours=8))   # sxtwl's clock: its 節 moments are Beijing time, UTC+8 (checked 2026-10-15 against JPL-based tables)


def civil_utc_offset(local: datetime, place: dict | None = None) -> float:
    """UTC offset of the civil clock a birth was read on: the place's own zone when it is outside Singapore (host zone
    database, else standard time from longitude to the half hour, the same fallback build_chart uses), otherwise Singapore's."""
    if place and place.get("cc") != "SG" and place.get("tz") and place.get("lon") is not None:
        off = utc_offset_hours(local, place["tz"])
        return off if off is not None else round(place["lon"] / 15 * 2) / 2
    return sg_utc_offset_hours(local.date())


def _jie_moment(day) -> datetime | None:
    """Exact moment of the 節 that falls on this sxtwl day, as a naive Beijing-clock datetime; None if the day has no 節
    (a 中氣 day does not count: only the odd jqmc indices open a month)."""
    if not day.hasJieQi() or day.getJieQi() % 2 == 0:
        return None
    t = sxtwl.JD2DD(day.getJieQiJD())
    return datetime(t.Y, t.M, t.D, int(t.h), int(t.m)) + timedelta(seconds=t.s)


def pillars_for(dt: datetime, instant: datetime | None = None) -> dict:
    """Four pillars. `dt` is the (policy-adjusted, e.g. true solar) clock reading that sets the DAY and HOUR pillars.

    Year and month pillars turn at the exact MOMENT of the 節 (立春 for the year, the 12 節 for the month; never the 中氣),
    not at the start of its civil day. That moment comes from sxtwl, which gives it in Beijing time (UTC+8), and it is
    compared as an absolute instant: `instant` is the birth's real moment, a timezone-aware datetime (the civil clock time
    with its own UTC offset), converted here to Beijing clock. Without `instant`, `dt` itself is taken as a Beijing-clock
    (UTC+8) reading, which is Singapore's clock today; date-only callers do not come here: they use `date_pillars`, where a 節 day belongs to the new term from its first minute.
    So a birth on a 節 day before that 節's moment keeps the previous month (and, on 立春, the previous year), whatever
    the true-solar shift does to `dt`. Day and hour never read `instant`.
    晚子時 (owner 2026-10-10): from 23:00 the 子 hour takes the SAME day's stem (乙 day → 丙子), and the
    day pillar stays with the civil date. sxtwl's getHourGZ(23) already rolls to the next day's 子, so
    the late 子 hour is read as hour 0 of the same day. (The old code shifted twice: 乙 day gave 庚子.)
    ponytail: single school implemented; add a policy flag when another school is wanted.
    """
    bj = instant.astimezone(BEIJING).replace(tzinfo=None) if instant is not None else dt
    moment = _jie_moment(sxtwl.fromSolar(bj.year, bj.month, bj.day))
    # sxtwl's year/month are day-level: before the 節 moment of a 節 day, step back to the day before it. `_term_day` also keeps the eve of a 節 that
    # lands just after midnight in the old term (sxtwl turns it a day early there).
    bday = _term_day(bj.date() - timedelta(days=1) if moment is not None and bj < moment else bj.date())
    day = sxtwl.fromSolar(dt.year, dt.month, dt.day)
    ygz, mgz, dgz = _gz(bday.getYearGZ()), _gz(bday.getMonthGZ()), _gz(day.getDayGZ())
    hgz = _gz(day.getHourGZ(0 if dt.hour == 23 else dt.hour))
    return {"year": ygz, "month": mgz, "day": dgz, "hour": hgz}


def _term_day(d: date):
    """The sxtwl day whose year and month pillars hold for the civil date `d` read at DAY level: a 節 day belongs to the new term from its first
    minute, so the day before a 節 day belongs to the old one. sxtwl does this except when a 節 lands within minutes after midnight (大雪 1917-12-08
    00:00:59, 白露 1927-09-09 00:05:24): it then turns the eve already. The eve of any 節 day is therefore read from the day before it."""
    nxt = d + timedelta(days=1)
    n = sxtwl.fromSolar(nxt.year, nxt.month, nxt.day)
    if n.hasJieQi() and n.getJieQi() % 2 == 1:
        d = d - timedelta(days=1)
    return sxtwl.fromSolar(d.year, d.month, d.day)


def date_pillars(d: date) -> dict:
    """Year, month and day pillars of a civil DATE, for every date-only caller (擇日 move-in dates, 建除 day officers, the 太歲 of a day, the 命卦 of a
    date of birth with no time). THE RULE (owner decision 2026-10-16): a 節 day belongs to the new month, and 立春 day to the new year, from the start
    of that day, whatever hour the 節 falls on. The moment inside the day is for charts that carry a birth instant (`pillars_for` with `instant`).
    Source for the month: 欽定協紀辨方書 (四庫全書本) 卷四 義例二 建除十二神, quoting 《歷書》: 「每月交節則疊兩值日」, so the 節 day takes the new month's
    建除 and repeats the officer of the day before; the year follows the same date at 立春 so that no two date tools can disagree about one day.
    Do not read month or year of a date anywhere else (not `pillars_for` at noon, not sxtwl's getMonthGZ directly)."""
    t = _term_day(d)
    return {"year": _gz(t.getYearGZ()), "month": _gz(t.getMonthGZ()), "day": _gz(sxtwl.fromSolar(d.year, d.month, d.day).getDayGZ())}


def day_month_branch(d: date) -> int:
    """Branch index (子 = 0) of the month a civil date belongs to; see `date_pillars` for the rule."""
    return _term_day(d).getMonthGZ().dz


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


def dayun_start_age(instant: datetime, forward: bool) -> tuple[float, str]:
    """起運 age in years, from the birth's absolute instant to the exact moment of a 節.

    Direction (the caller's rule: yang-year male or yin-year female runs forward): forward counts to the NEXT 節, backward to the
    PREVIOUS one. "Next" is the first 節 moment strictly after the birth; "previous" is the last one at or before it, the same tie rule
    `pillars_for` uses (a birth on the exact moment already belongs to the new month, so that 節 is behind it).
    Conversion (the 子平 起運 convention, unchanged): 3 days = 1 year, which is 1 day = 4 months and 1 時辰 (2 hours) = 10 days.
    The count is continuous, so the exact interval in days is divided by 3; only its two ends were day-level before (2026-10-15).
    `instant` is a timezone-aware datetime (civil clock with its own UTC offset); the 節 moments are sxtwl's Beijing time (UTC+8)."""
    bj = instant.astimezone(BEIJING).replace(tzinfo=None)
    step = 1 if forward else -1
    for k in range(0, 41):
        d = bj.date() + timedelta(days=step * k)
        moment = _jie_moment(sxtwl.fromSolar(d.year, d.month, d.day))
        if moment is not None and (moment > bj if forward else moment <= bj):
            return abs((moment - bj).total_seconds()) / 86400.0 / 3.0, JIEQI_NAMES[sxtwl.fromSolar(d.year, d.month, d.day).getJieQi()]
    raise RuntimeError("no 節 found within 40 days — should be impossible")
