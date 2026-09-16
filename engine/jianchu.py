"""入宅 move-in date selection: 建除十二神 officers + branch-clash filters.

Pure function of (date window, occupant year branches, house sitting bearing).
Officer = (day branch − month branch) mod 12 on the 建除 cycle; keep 成/定/開.
Drop days whose branch ① 六沖s any occupant's year branch, ② 沖s the sitting
branch (沖坐山), or ③ equals that year's 太歲 branch (值太歲). sxtwl supplies
all calendrical facts — no custom lunar logic.
"""
from __future__ import annotations

from datetime import date, timedelta

import sxtwl

GAN = "甲乙丙丁戊己庚辛壬癸"
ZHI = "子丑寅卯辰巳午未申酉戌亥"
OFFICERS = "建除滿平定執破危成收開閉"
GOOD_OFFICERS = set("成定開")
CHONG = {ZHI[i]: ZHI[(i + 6) % 12] for i in range(12)}
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


_PALACES = "坎艮震巽離坤兌乾"
_PALACE_BRANCHES = {"坎": ["子"], "艮": ["丑", "寅"], "震": ["卯"],
                    "巽": ["辰", "巳"], "離": ["午"], "坤": ["未", "申"],
                    "兌": ["酉"], "乾": ["戌", "亥"]}


def sitting_branches(facing_deg: float) -> list[str]:
    """Branch(es) of the sitting palace (facing + 180°). A stem or trigram
    sitting mountain (e.g. 丁山) borrows its 45° palace's branches — 離 → 午;
    corner palaces carry two (艮 → 丑寅)."""
    deg = (facing_deg + 180) % 360
    palace = _PALACES[round(deg / 45) % 8]
    return _PALACE_BRANCHES[palace]


def movein_dates(start: date, end: date, occupant_branches: list[str],
                 facing_deg: float) -> list[dict]:
    """Auspicious 入宅 days in [start, end], best-first (成 > 定 > 開)."""
    avoid = {CHONG[b]: f"沖{b}" for b in set(occupant_branches)}
    for sit in sitting_branches(facing_deg):
        avoid.setdefault(CHONG[sit], f"沖坐山{sit}")
    out = []
    d = start
    while d <= end:
        day = sxtwl.fromSolar(d.year, d.month, d.day)
        dgz, mgz, ygz = day.getDayGZ(), day.getMonthGZ(), day.getYearGZ()
        officer = OFFICERS[(dgz.dz - mgz.dz) % 12]
        if officer in GOOD_OFFICERS:
            db = ZHI[dgz.dz]
            reasons = []
            if db in avoid:
                reasons.append(avoid[db])
            if db == ZHI[ygz.dz]:
                reasons.append("值太歲")
            if not reasons:
                out.append({"date": d.isoformat(),
                            "weekday": WEEKDAYS[d.weekday()],
                            "ganzhi": GAN[dgz.tg] + ZHI[dgz.dz],
                            "officer": officer})
        d += timedelta(days=1)
    rank = {"成": 0, "定": 1, "開": 2}
    return sorted(out, key=lambda r: (rank[r["officer"]], r["date"]))


if __name__ == "__main__":  # self-check against independently verified almanac days
    got = movein_dates(date(2027, 2, 1), date(2027, 3, 31), ["午"], 0.0)
    days = {r["date"]: r for r in got}
    assert days["2027-02-12"]["ganzhi"] == "壬戌"      # 成日
    assert days["2027-02-20"]["ganzhi"] == "庚午"      # 定日
    assert "2027-03-17" not in days                    # 未日 值太歲 in 丁未
    assert all(d["ganzhi"][1] != "子" for d in got)    # 沖午 filtered
    assert sitting_branches(0.0) == ["午"]             # N facing → 離 sitting
    assert sitting_branches(315.0) == ["辰", "巳"]     # corner palace → two
    print(f"jianchu self-check ok — {len(got)} candidate days")
