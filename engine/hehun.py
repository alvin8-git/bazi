"""合婚 pair compatibility — deterministic pairwise chart comparison.

Works for any two members (couple, parent-child, siblings): spouse-palace (day
branch) interactions, day-stem 五合, year-branch (生肖) relations, and mutual
用神 element supply. Score = 50 + cited chips, clamped 5–95 — same contract as
the life-domain signals.
"""
from __future__ import annotations

from .bazi import TEN_GOD_EN, ten_god
from .shensha import _TRINE, _XING_PAIRS
from .wuxing import CHONG_MAP, ELEMENT_EN, HAI_MAP, HE_MAP

WUHE = {"甲": "己", "己": "甲", "乙": "庚", "庚": "乙", "丙": "辛",
        "辛": "丙", "丁": "壬", "壬": "丁", "戊": "癸", "癸": "戊"}


def _branch_rel(a: str, b: str) -> tuple[str, int] | None:
    if HE_MAP.get(a) == b:
        return "六合", 1
    if a != b and _TRINE.get(a) is not None and _TRINE.get(a) == _TRINE.get(b):
        return "半三合", 1
    if CHONG_MAP.get(a) == b:
        return "六沖", -1
    if a != b and frozenset((a, b)) in _XING_PAIRS:
        return "刑", -1
    if HAI_MAP.get(a) == b:
        return "六害", -1
    return None


def pair_compatibility(ca, cb, ys_a: dict, ys_b: dict) -> dict:
    chips, notes = [], []
    da, db = ca.pillars["day"], cb.pillars["day"]

    # 1. spouse palaces (day branches) — the heart of classical 合婚
    rel = _branch_rel(da.branch, db.branch)
    if rel is None:
        chips.append(("Day branches: no link", 0))
    else:
        kind, sign = rel
        pts = {"六合": 15, "半三合": 10, "六沖": -15, "刑": -8, "六害": -8}[kind]
        chips.append((f"Day branches {da.branch} and {db.branch}: {kind}, "
                      + ("a bond." if sign > 0 else "a clash."), pts))
    if WUHE.get(da.stem) == db.stem:
        chips.append((f"Day stems {da.stem} and {db.stem}: Five Combination, a classic stem bond.", 10))

    # 2. year branches (生肖 relation)
    yrel = _branch_rel(ca.pillars["year"].branch, cb.pillars["year"].branch)
    if yrel:
        kind, _ = yrel
        pts = {"六合": 8, "半三合": 8, "六沖": -8, "刑": -4, "六害": -4}[kind]
        chips.append((f"Zodiac years: {kind}", pts))

    # 3. mutual 用神 supply — does one chart carry what the other needs?
    wa, wb = ca.element_weights, cb.element_weights
    ta, tb = sum(wa.values()) or 1, sum(wb.values()) or 1
    for giver, gw, gt, taker, tys in ((ca, wa, ta, cb, ys_b), (cb, wb, tb, ca, ys_a)):
        n = 0
        for e in tys["favourable"]:
            if gw.get(e, 0) / gt >= 0.2 and n < 2:
                chips.append((f"{giver.person} has plenty of {ELEMENT_EN[e]}, "
                              f"which {taker.person} needs.", 6))
                n += 1
        dom = max(gw, key=gw.get)
        if dom in tys["unfavourable"]:
            chips.append((f"{ELEMENT_EN[dom]} is {giver.person}'s strongest element, "
                          f"and {taker.person} does better with less of it.", -6))

    score = max(5, min(95, 50 + sum(d for _, d in chips)))
    band = ("very compatible 上等" if score >= 70 else
            "compatible 中上" if score >= 55 else
            "workable 中" if score >= 45 else "needs effort 需磨合")

    rel_ab = ten_god(da.stem, db.stem)
    rel_ba = ten_god(db.stem, da.stem)
    notes.append(f"To {ca.person}, {cb.person} comes across as {TEN_GOD_EN[rel_ab]} "
                 f"({rel_ab}). To {cb.person}, {ca.person} comes across "
                 f"as {TEN_GOD_EN[rel_ba]} ({rel_ba}).")

    paras = [
        f"{score} out of 100: {band}. The score adds the factors below to a neutral 50. "
        "The classical method weighs the day pillars most, then the year branches, "
        "then whether each chart supplies elements the other needs.",
        notes[0] + " These roles describe the natural dynamic, who energises and who "
        "steadies, not how good the relationship is.",
        "Element supply is the practical lever. When one person has plenty of an element "
        "the other needs, spending time together in rooms and colours that match it "
        "tends to feel supportive. If there is a clash, the usual fixes help: separate "
        "work corners, calmer decor, and dates that avoid clashing days for either person.",
    ]
    return {"a": ca.person, "b": cb.person,
            "day_pillars": [str(da), str(db)], "score": score, "band": band,
            "chips": [{"label": l, "delta": d} for l, d in chips],
            "relation": {"a_sees_b": rel_ab, "b_sees_a": rel_ba},
            "interpretation": {"paragraphs": paras},
            "source_ref": "Method: day and year branch relations, the Day Master Five "
                          "Combination, and element supply. The element-supply weights "
                          "are our own modern choice."}
