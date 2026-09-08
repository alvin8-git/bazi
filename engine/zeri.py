"""M4b: 擇日 — auspicious date selection, personalized to the household.

Layers, each cited:
  ① 十二建除 day officer — officer = offset of day branch from month branch
    (建 on the day whose branch equals the month branch). Simplified 宜忌 map.
    ponytail: officer repeat on 節-transition days ignored; full 通書 layers
    (28宿, 神煞) are out of scope — upgrade if verdicts disagree with an almanac.
  ② 破日: day branch 沖 month branch (also officer 破) — hard avoid.
  ③ Per-person: day branch 沖 a member's YEAR branch (沖生肖 — that member
    should not lead the event) or 沖 a member's DAY pillar branch (personal
    clash, softer), 六合 bonus.
"""
from __future__ import annotations

from datetime import date, timedelta

import sxtwl

from .wuxing import BRANCHES, CHONG_MAP, HAI_MAP, HE_MAP, STEMS

OFFICERS = ["建", "除", "滿", "平", "定", "執", "破", "危", "成", "收", "開", "閉"]
# simplified 宜忌 for move-in/renovation-type events
OFFICER_SCORE = {"建": 0.5, "除": 0.5, "滿": 0.5, "平": -0.5, "定": 1.0, "執": 0.0,
                 "破": -2.0, "危": -1.0, "成": 2.0, "收": 0.0, "開": 1.5, "閉": -1.0}


def day_info(d: date) -> dict:
    day = sxtwl.fromSolar(d.year, d.month, d.day)
    dgz, mgz = day.getDayGZ(), day.getMonthGZ()
    db, mb = BRANCHES[dgz.dz], BRANCHES[mgz.dz]
    officer = OFFICERS[(dgz.dz - mgz.dz) % 12]
    return {"date": d.isoformat(), "day_gz": STEMS[dgz.tg] + db, "day_branch": db,
            "month_branch": mb, "officer": officer}


def rate_day(d: date, members: list[dict]) -> dict:
    """members: [{name, year_branch, day_branch}]"""
    info = day_info(d)
    db = info["day_branch"]
    score = OFFICER_SCORE[info["officer"]]
    notes = [{"rule_id": "jianchu", "layer": "zeri",
              "source_ref": f"十二建除 — {info['officer']}日 (simplified 宜忌)",
              "explanation": f"officer {info['officer']}, base {score:+.1f}"}]
    if CHONG_MAP.get(db) == info["month_branch"]:
        score -= 1.0
        notes.append({"rule_id": "podi", "layer": "zeri", "source_ref": "月破",
                      "explanation": f"day {db} 沖 month {info['month_branch']} — 破日, avoid"})
    flags = []
    for m in members:
        if CHONG_MAP.get(db) == m["year_branch"]:
            score -= 1.0
            flags.append({"name": m["name"], "kind": "沖生肖",
                          "why": f"day {db} 沖 year branch {m['year_branch']} — {m['name']} should not lead this day"})
        elif CHONG_MAP.get(db) == m["day_branch"]:
            score -= 0.5
            flags.append({"name": m["name"], "kind": "沖日柱",
                          "why": f"day {db} 沖 day-pillar branch {m['day_branch']} — personally unfavourable"})
        elif HE_MAP.get(db) == m["day_branch"]:
            score += 0.25
            flags.append({"name": m["name"], "kind": "合日柱",
                          "why": f"day {db} 六合 day-pillar branch {m['day_branch']} — personally supportive"})
    return {**info, "score": round(score, 2), "person_flags": flags, "notes": notes,
            "hours": day_hours(info["day_gz"])}


def day_hours(day_gz: str) -> dict:
    """吉時 hour selection within one day: 貴人 hours (day stem's 天乙 branches),
    hours combining the day branch (合日), the clashing 時破 hour, and 害."""
    from .shensha import TIANYI
    ds, db = day_gz[0], day_gz[1]
    hours = []
    for i, hb in enumerate(BRANCHES):
        score, tags = 0.0, []
        if hb in TIANYI.get(ds, ""):
            score += 1.5
            tags.append("貴人")
        if HE_MAP.get(hb) == db:
            score += 1.0
            tags.append("合日")
        if CHONG_MAP.get(hb) == db:
            score -= 2.0
            tags.append("時破")
        if HAI_MAP.get(hb) == db:
            score -= 1.0
            tags.append("害")
        start = (23 + 2 * i) % 24
        hours.append({"branch": hb, "time": f"{start:02d}–{(start + 2) % 24:02d}",
                      "score": score, "tags": tags})
    best = sorted([h for h in hours if h["score"] > 0], key=lambda h: -h["score"])[:2]
    avoid = [h for h in hours if h["score"] <= -2]
    return {"best": best, "avoid": avoid}


def rate_month(year: int, month: int, members: list[dict]) -> list[dict]:
    d = date(year, month, 1)
    out = []
    while d.month == month:
        out.append(rate_day(d, members))
        d += timedelta(days=1)
    return out
