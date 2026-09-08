"""M4a: 流年流月 — year/month stars, 太歲 interactions, per-person forecast.

Monthly center star (紫白): for the 寅 month (first solar month), year-branch
group 子午卯酉→8, 辰戌丑未→5, 寅申巳亥→2; decreasing by one each solar month.
Year is 立春-bounded throughout.
"""
from __future__ import annotations

from .bazi import Chart
from .wuxing import (BRANCH_ELEMENT, BRANCHES, CHONG_MAP, ELEMENT_EN, HAI_MAP,
                     HE_MAP, SANHE, STEM_ELEMENT, STEMS)
from .xuankong import _fly, annual_star, star_quality

MONTH_BRANCH_ORDER = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]


def year_ganzhi(lichun_year: int) -> tuple[str, str]:
    return STEMS[(lichun_year - 4) % 10], BRANCHES[(lichun_year - 4) % 12]


def monthly_center_star(lichun_year: int, month_index: int) -> int:
    """month_index 0 = 寅月 … 11 = 丑月."""
    _, yb = year_ganzhi(lichun_year)
    first = {"子": 8, "午": 8, "卯": 8, "酉": 8,
             "辰": 5, "戌": 5, "丑": 5, "未": 5,
             "寅": 2, "申": 2, "巳": 2, "亥": 2}[yb]
    return (first - 1 - month_index) % 9 + 1


def monthly_chart(lichun_year: int, month_index: int) -> dict[str, int]:
    return _fly(monthly_center_star(lichun_year, month_index), forward=True)


def taisui_interactions(chart: Chart, lichun_year: int) -> list[dict]:
    """Person vs 太歲: 值/沖/合/害 on the YEAR branch (classical 犯太歲 basis),
    plus the same checks on the day branch as secondary notes."""
    ys, yb = year_ganzhi(lichun_year)
    out = []
    for pos, weight in (("year", "primary"), ("day", "secondary")):
        b = chart.pillars[pos].branch
        rels = []
        if b == yb:
            rels.append(("值太歲", "same branch as the year — a 本命年-type year: keep a low profile"))
        if CHONG_MAP.get(b) == yb:
            rels.append(("沖太歲", "clashes the year branch — expect movement/disruption; avoid major risks"))
        if HE_MAP.get(b) == yb:
            rels.append(("合太歲", "六合 with the year branch — harmonious, supported year"))
        if HAI_MAP.get(b) == yb:
            rels.append(("害太歲", "六害 with the year branch — friction with people; document agreements"))
        for trio, el in SANHE:
            if b in trio and yb in trio and b != yb:
                rels.append(("三合太歲", f"三合 ({''.join(trio)} → {el}) with the year — allies and momentum"))
        for name, why in rels:
            out.append({"rule_id": f"taisui-{name}", "layer": "liunian",
                        "source_ref": f"太歲 {ys}{yb} vs {pos} branch {b} ({weight})",
                        "explanation": f"{name}: {why}"})
    if not out:
        out.append({"rule_id": "taisui-none", "layer": "liunian",
                    "source_ref": f"太歲 {ys}{yb}",
                    "explanation": "no 值/沖/合/害/三合 with year or day branch — a neutral 太歲 year"})
    return out


def year_element_read(chart: Chart, ys_fav: list[str], lichun_year: int) -> dict:
    stem, branch = year_ganzhi(lichun_year)
    se, be = STEM_ELEMENT[stem], BRANCH_ELEMENT[branch]
    def verdict(el: str) -> str:
        return ("favourable 喜" if el in ys_fav else "unfavourable 忌")
    return {"rule_id": "year-element", "layer": "liunian",
            "source_ref": f"流年 {stem}{branch} ({ELEMENT_EN[se]}{se}/{ELEMENT_EN[be]}{be}) vs 用神",
            "explanation": f"year stem {stem} {ELEMENT_EN[se]} is {verdict(se)}; "
                           f"year branch {branch} {ELEMENT_EN[be]} is {verdict(be)}"}


def room_month_watch(room_palace: str, lichun_year: int) -> list[dict]:
    """Months when 五黃/二黑 fly into the person's bedroom palace."""
    out = []
    for mi, mb in enumerate(MONTH_BRANCH_ORDER):
        star = monthly_chart(lichun_year, mi).get(room_palace)
        if star in (2, 5):
            label = "五黃" if star == 5 else "二黑"
            out.append({"rule_id": f"month-{label}", "layer": "liunian",
                        "source_ref": f"流月紫白, {mb}月 (solar month {mi + 1})",
                        "explanation": f"{label} enters your room's palace {room_palace} in the "
                                       f"{mb} month — avoid renovation/ground-breaking there; keep it quiet"})
    return out


def person_forecast(chart: Chart, ys: dict, lichun_year: int,
                    room_palace: str | None, natal_period: int) -> dict:
    months = []
    for mi, mb in enumerate(MONTH_BRANCH_ORDER):
        center = monthly_center_star(lichun_year, mi)
        room_star = monthly_chart(lichun_year, mi).get(room_palace) if room_palace else None
        q = star_quality(room_star, natal_period) if room_star else (0, "")
        months.append({"month_branch": mb, "solar_month": mi + 1, "center": center,
                       "room_star": room_star, "room_quality": q[0], "room_note": q[1]})
    return {"year": lichun_year, "year_ganzhi": "".join(year_ganzhi(lichun_year)),
            "annual_center": annual_star(lichun_year),
            "taisui": taisui_interactions(chart, lichun_year),
            "year_element": year_element_read(chart, ys["favourable"], lichun_year),
            "room_palace": room_palace,
            "room_watch": room_month_watch(room_palace, lichun_year) if room_palace else [],
            "months": months}


# ---------- Tier 3: timing extensions ----------------------------------------
TG_KEY = {"比肩": "self-drive & peers", "劫財": "competition & bold moves",
          "食神": "enjoyment & easy output", "傷官": "expression & disruption",
          "偏財": "opportunities & ventures", "正財": "cashflow & practical resources",
          "七殺": "pressure & decisive action", "正官": "rules & stable responsibility",
          "偏印": "intuition & niche skills", "正印": "learning & support"}


def dayun_detail(chart: Chart, year: int) -> list[dict]:
    """Each 大運 decade labelled by the ten gods of its stem and branch main qi."""
    from .bazi import ten_god
    from .wuxing import HIDDEN_STEMS
    age = year - chart.birth_local.year
    out = []
    for d in chart.dayun:
        sg = ten_god(chart.day_master, d.gz.stem)
        bg = ten_god(chart.day_master, HIDDEN_STEMS[d.gz.branch][0])
        out.append({"gz": str(d.gz), "ages": f"{d.start_age:.0f}–{d.end_age:.0f}",
                    "stem_god": sg, "branch_god": bg,
                    "keywords": f"{TG_KEY[sg]} / {TG_KEY[bg]}",
                    "current": d.covers(age)})
    return out


_OUTLOOK_ADVICE = {
    "steady": "a good year to build up gradually — keep your rhythm.",
    "moderate movement": "align direction before pushing; preserve room to adjust.",
    "high volatility": "slow major decisions down; put budgets, contracts and "
                       "boundaries in writing first.",
}


def _mxo_xing():
    from .shensha import _XING_PAIRS
    return _XING_PAIRS


def _mxo_trine():
    from .shensha import _TRINE
    return _TRINE


def multi_year_outlook(chart: Chart, ys: dict, start_year: int, n: int = 5) -> list[dict]:
    """Year-by-year volatility read: the coming years' branches vs the natal
    branches (沖/刑/自刑 = 2 pts, 害 = 1 pt; 合/半合 listed as support).
    Verdict: ≥3 high volatility, 1–2 moderate movement, 0 steady."""
    from .shensha import _SELF_XING, _TRINE, _XING_PAIRS
    natal = {pos: chart.pillars[pos].branch for pos in ("year", "month", "day", "hour")}
    rows = []
    for y in range(start_year, start_year + n):
        st, yb = year_ganzhi(y)
        events, support, pts = [], [], 0
        # 大運×流年 echo: the active luck pillar's branch vs the year branch
        age = y - chart.birth_local.year
        luck = next((d for d in chart.dayun if d.covers(age)), None)
        if luck is not None:
            lb = luck.gz.branch
            if CHONG_MAP.get(lb) == yb:
                events.append(f"大運{lb}-{yb} 沖 (luck)"); pts += 2
            elif lb != yb and frozenset((lb, yb)) in _mxo_xing():
                events.append(f"大運{lb}-{yb} 刑 (luck)"); pts += 2
            elif lb == yb:
                events.append(f"大運{lb} 伏吟 (luck echoes the year)"); pts += 1
            elif HAI_MAP.get(lb) == yb:
                events.append(f"大運{lb}-{yb} 害 (luck)"); pts += 1
            elif HE_MAP.get(lb) == yb:
                support.append(f"大運{lb}-{yb} 合 (luck)")
            elif _mxo_trine().get(lb) is not None and _mxo_trine().get(lb) == _mxo_trine().get(yb):
                support.append(f"大運{lb}-{yb} 半合 (luck)")
        for pos, nb in natal.items():
            if CHONG_MAP.get(nb) == yb:
                events.append(f"{nb}-{yb} 沖 ({pos})"); pts += 2
            elif nb != yb and frozenset((nb, yb)) in _XING_PAIRS:
                events.append(f"{nb}-{yb} 刑 ({pos})"); pts += 2
            elif nb == yb and yb in _SELF_XING:
                events.append(f"{yb} 自刑 ({pos})"); pts += 2
            elif HAI_MAP.get(nb) == yb:
                events.append(f"{nb}-{yb} 害 ({pos})"); pts += 1
            elif HE_MAP.get(nb) == yb:
                support.append(f"{nb}-{yb} 合 ({pos})")
            elif nb != yb and _TRINE.get(nb) is not None and _TRINE.get(nb) == _TRINE.get(yb):
                support.append(f"{nb}-{yb} 半合 ({pos})")
        verdict = ("high volatility" if pts >= 3 else
                   "moderate movement" if pts >= 1 else "steady")
        els = []
        for e in (STEM_ELEMENT[st], BRANCH_ELEMENT[yb]):
            flag = "喜" if e in ys["favourable"] else "忌" if e in ys["unfavourable"] else "·"
            els.append(f"{ELEMENT_EN[e]}{e} {flag}")
        rows.append({"year": y, "gz": st + yb, "verdict": verdict, "points": pts,
                     "events": events, "support": support, "elements": els,
                     "advice": _OUTLOOK_ADVICE[verdict]})
    return rows


# 支 → palace (for annual affliction sectors)
BRANCH_PALACE = {"子": "坎", "丑": "艮", "寅": "艮", "卯": "震", "辰": "巽", "巳": "巽",
                 "午": "離", "未": "坤", "申": "坤", "酉": "兌", "戌": "乾", "亥": "乾"}
_SANSHA = {  # year-branch trine → the three 煞 branches (opposite frame)
    ("申", "子", "辰"): "巳午未", ("寅", "午", "戌"): "亥子丑",
    ("巳", "酉", "丑"): "寅卯辰", ("亥", "卯", "未"): "申酉戌"}


def annual_afflictions(lichun_year: int) -> dict:
    """太歲 / 歲破 / 三煞 sectors for the year — the directions a geomancer
    checks before any renovation or seating decision."""
    _, yb = year_ganzhi(lichun_year)
    po = CHONG_MAP[yb]
    grp = next(g for g in _SANSHA if yb in g)
    sansha_branches = _SANSHA[grp]
    return {
        "taisui": {"branch": yb, "palace": BRANCH_PALACE[yb],
                   "rule": "太歲 可坐不可向 — sitting with your back to it is fine; "
                           "avoid FACING it for long periods, and never renovate or "
                           "dig in its sector this year"},
        "suipo": {"branch": po, "palace": BRANCH_PALACE[po],
                  "rule": "歲破 (opposite 太歲) — the year breaker; avoid "
                          "ground-breaking and major disturbance in this sector"},
        "sansha": {"branches": sansha_branches,
                   "palaces": sorted({BRANCH_PALACE[b] for b in sansha_branches}),
                   "rule": "三煞 可向不可坐 — facing it is acceptable; avoid SITTING "
                           "toward it and avoid renovation in its sectors"},
    }
