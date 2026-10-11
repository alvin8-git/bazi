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
from .i18n import ELEM, L, T, and_l, cap, dot, jn, zs  # noqa: F401

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


# 歲刑: who punishes whom, from 《欽定協紀辨方書》卷三〈義例一〉考原 (曾門經): 子刑夘 丑刑戌 寅刑巳 夘刑子 巳刑申 未刑丑 申刑寅 戌刑未,
# and 辰午酉亥 punish themselves (自刑). The same table gives the 歲刑 sector (the branch the year's 太歲 punishes) and, read as unordered
# pairs, the personal 刑太歲 test: a branch that punishes the 太歲 or is punished by it. 《淵海子平》〈論征太歲〉 marks the same pairs for a
# person ("又忌寅刑巳、巳刑申、申刑寅"). shensha._XING_PAIRS holds the unordered pairs; a test pins the two tables to each other.
XING_TARGET = {"子": "卯", "丑": "戌", "寅": "巳", "卯": "子", "辰": "辰", "巳": "申",
               "午": "午", "未": "丑", "申": "寅", "酉": "酉", "戌": "未", "亥": "亥"}
SELF_XING = frozenset("辰午酉亥")
# 破 (六破: 子酉 丑辰 寅亥 卯午 巳申 未戌) is deliberately NOT emitted: no text we could read (協紀辨方書 卷三 to 卷十, 三命通會, 淵海子平)
# states it, so naming a source for it would be inventing one. Add it when a verified source is in hand.


def taisui_tiers(b: str, t: str) -> list[str]:
    """How branch `b` meets the year's 太歲 branch `t`, as rule names, in the fixed order 值 沖 合 害 刑 (三合 is added by the caller,
    which needs the trine's element). 刑 is 'b and t punish each other' (b != t) or the 自刑 of 辰午酉亥 when b == t."""
    from .shensha import _XING_PAIRS
    out = []
    if b == t:
        out.append("值太歲")
    if CHONG_MAP.get(b) == t:
        out.append("沖太歲")
    if HE_MAP.get(b) == t:
        out.append("合太歲")
    if HAI_MAP.get(b) == t:
        out.append("害太歲")
    if (b != t and frozenset((b, t)) in _XING_PAIRS) or (b == t and b in SELF_XING):
        out.append("刑太歲")
    return out


def taisui_interactions(chart: Chart, lichun_year: int, lang: str = "en") -> list[dict]:
    """Person vs 太歲: 值/沖/合/害/刑 on the YEAR branch (classical 犯太歲 basis),
    plus the same checks on the day branch as secondary notes.
    刑太歲: 《淵海子平》〈論征太歲〉 and 《協紀辨方書》卷三 歲刑 table (XING_TARGET). 合太歲 is read as 晦, a dulled and reversing year, not
    as support: 《淵海子平》〈論征太歲〉 "日干支合太歲干支曰晦...遇此者主晦氣，一年反覆、欲速不達" (owner correction, round A).
    The other rules and their texts are unchanged; the new texts carry ids so the Chinese page has them."""
    ys, yb = year_ganzhi(lichun_year)
    out = []
    for pos, weight in (("year", "primary"), ("day", "secondary")):
        b = chart.pillars[pos].branch
        tiers = taisui_tiers(b, yb)
        rels = []
        where = T("liunian.taisui_interactions.07" if pos == "year" else "liunian.taisui_interactions.08", f"{pos} branch", lang)
        wt = T("liunian.taisui_interactions.09" if pos == "year" else "liunian.taisui_interactions.10", weight, lang)
        for name in tiers:
            if name == "值太歲":
                rels.append((name, "same branch as the year — a 本命年-type year: keep a low profile", None))
            elif name == "沖太歲":
                rels.append((name, "clashes the year branch — expect movement/disruption; avoid major risks", None))
            elif name == "合太歲":
                rels.append((name, T("liunian.taisui_interactions.03", "六合 with the year branch, which 淵海子平 reads as 晦: a dulled year of reversals, so go slowly and do not expect a lift", lang),
                             T("liunian.taisui_interactions.05", f"太歲 {ys}{yb} vs {where} {b} ({wt}) · 《淵海子平》〈論征太歲〉 日干支合太歲干支曰晦", lang,
                               ys=ys, yb=yb, where=where, b=b, wt=wt)))
            elif name == "害太歲":
                rels.append((name, "六害 with the year branch — friction with people; document agreements", None))
            elif b == yb:      # 刑太歲 of a branch that punishes itself
                rels.append((name, T("liunian.taisui_interactions.02", "自刑, the branch punishes itself: the strain is self-made, so pace yourself and check things twice", lang),
                             T("liunian.taisui_interactions.06", f"太歲 {ys}{yb} vs {where} {b} ({wt}) · 《協紀辨方書》卷三〈義例一〉歲刑表 辰午酉亥為自刑", lang,
                               ys=ys, yb=yb, where=where, b=b, wt=wt)))
            else:
                rels.append((name, T("liunian.taisui_interactions.01", "strain builds slowly rather than breaking at once, so put big commitments in writing", lang),
                             T("liunian.taisui_interactions.04", f"太歲 {ys}{yb} vs {where} {b} ({wt}) · 《淵海子平》〈論征太歲〉 and 《協紀辨方書》卷三〈義例一〉歲刑表", lang,
                               ys=ys, yb=yb, where=where, b=b, wt=wt)))
        for trio, el in SANHE:
            if b in trio and yb in trio and b != yb:
                rels.append(("三合太歲", f"三合 ({''.join(trio)} → {el}) with the year — allies and momentum", None))
        for name, why, src in rels:
            out.append({"rule_id": f"taisui-{name}", "layer": "liunian",
                        "source_ref": src or f"太歲 {ys}{yb} vs {pos} branch {b} ({weight})",
                        "explanation": f"{zs(name, lang)}{'：' if lang == 'zh' else ': '}{why}"})
    if not out:
        out.append({"rule_id": "taisui-none", "layer": "liunian",
                    "source_ref": f"太歲 {ys}{yb}",
                    "explanation": "no 值/沖/合/害/三合 with year or day branch — a neutral 太歲 year"})
    return out


def taisui_finding(chart: Chart, lichun_year: int, lang: str = "en") -> dict:
    """The 犯太歲 finding the reading page uses for one year (additive; the rule texts live in taisui_interactions).
    `sentence` is "刑" or "自刑" only when the YEAR branch punishes the 太歲 (or itself, 辰午酉亥); those are the tiers with a classical source
    in hand (《淵海子平》〈論征太歲〉, 《協紀辨方書》卷三 歲刑表). 值 and 害 are still emitted by taisui_interactions but get no sentence: no text
    we could read names them as a 犯太歲 type. 沖 is the travel caution already (windows._year_row). `cites` are the 刑 and 合(晦) rows, each
    with its source, for the evidence panel."""
    st, t = year_ganzhi(lichun_year)
    b = chart.pillars["year"].branch
    year_t = taisui_tiers(b, t)
    sentence = ("自刑" if b == t else "刑") if "刑太歲" in year_t else None
    cites = [{"rule_id": i["rule_id"], "source_ref": i["source_ref"], "explanation": i["explanation"]}
             for i in taisui_interactions(chart, lichun_year, lang) if i["rule_id"] in ("taisui-刑太歲", "taisui-合太歲")]
    return {"year": lichun_year, "taisui": st + t, "branch": b, "tiers": year_t,
            "day_tiers": taisui_tiers(chart.pillars["day"].branch, t), "sentence": sentence, "cites": cites}


def year_element_read(chart: Chart, ys_fav: list[str], lichun_year: int, lang: str = "en") -> dict:
    stem, branch = year_ganzhi(lichun_year)
    se, be = STEM_ELEMENT[stem], BRANCH_ELEMENT[branch]
    def verdict(el: str) -> str:
        return (T("liunian.year_element_read.01", "favourable 喜", lang) if el in ys_fav else T("liunian.year_element_read.02", "unfavourable 忌", lang))
    return {"rule_id": "year-element", "layer": "liunian",
            "source_ref": T("liunian.year_element_read.03", f"流年 {stem}{branch} ({ELEM(lang)[se]} {se}/{ELEM(lang)[be]} {be}) vs 用神", lang, stem=stem, branch=branch, se_element_en=ELEM(lang)[se], se=se, be_element_en=ELEM(lang)[be], be=be),
            "explanation": T("liunian.year_element_read.04", f"year stem {stem} {ELEM(lang)[se]} is {verdict(se)}; "
                           f"year branch {branch} {ELEM(lang)[be]} is {verdict(be)}", lang, stem=stem, se_element_en=ELEM(lang)[se], verdict_se=verdict(se), branch=branch, be_element_en=ELEM(lang)[be], verdict_be=verdict(be))}


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


def dayun_detail(chart: Chart, year: int, lang: str = "en") -> list[dict]:
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
                    "keywords": f"{L("liunian.TG_KEY", TG_KEY, lang)[sg]} / {L("liunian.TG_KEY", TG_KEY, lang)[bg]}",
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
            els.append(f"{ELEMENT_EN[e]} {e} {flag}")
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


def annual_afflictions(lichun_year: int, lang: str = "en") -> dict:
    """太歲 / 歲破 / 三煞 sectors for the year — the directions a geomancer
    checks before any renovation or seating decision."""
    _, yb = year_ganzhi(lichun_year)
    po = CHONG_MAP[yb]
    grp = next(g for g in _SANSHA if yb in g)
    sansha_branches = _SANSHA[grp]
    return {
        "taisui": {"branch": yb, "palace": BRANCH_PALACE[yb],
                   "rule": T("liunian.annual_afflictions.01", "太歲 可坐不可向 — sitting with your back to it is fine; "
                           "avoid FACING it for long periods, and never renovate or "
                           "dig in its sector this year", lang)},
        "suipo": {"branch": po, "palace": BRANCH_PALACE[po],
                  "rule": T("liunian.annual_afflictions.02", "歲破 (opposite 太歲) — the year breaker; avoid "
                          "ground-breaking and major disturbance in this sector", lang)},
        "sansha": {"branches": sansha_branches,
                   "palaces": sorted({BRANCH_PALACE[b] for b in sansha_branches}),
                   "rule": T("liunian.annual_afflictions.03", "三煞 可向不可坐 — facing it is acceptable; avoid SITTING "
                           "toward it and avoid renovation in its sectors", lang)},
        # additive (round A): 歲刑, the branch this year's 太歲 punishes. 《協紀辨方書》卷三〈義例一〉廣聖曆: "歲刑之地…動土興工亦須迴避，犯之多鬬爭".
        "suixing": {"branch": XING_TARGET[yb], "palace": BRANCH_PALACE[XING_TARGET[yb]], "self_xing": XING_TARGET[yb] == yb,
                    "rule": T("liunian.annual_afflictions.04", "歲刑 (the sector the 太歲 punishes): do not break ground or run heavy works here; "
                            "《協紀辨方書》卷三 says 動土興工亦須迴避，犯之多鬬爭", lang)},
    }
