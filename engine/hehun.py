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
        chips.append(("day branches (spouse palaces) neutral", 0))
    else:
        kind, sign = rel
        pts = {"六合": 15, "半三合": 10, "六沖": -15, "刑": -8, "六害": -8}[kind]
        chips.append((f"day branches {da.branch}{db.branch} {kind} — "
                      + ("spouse palaces bond" if sign > 0 else "spouse palaces clash"),
                      pts))
    if WUHE.get(da.stem) == db.stem:
        chips.append((f"day stems {da.stem}{db.stem} 五合 — classic stem bond", 10))

    # 2. year branches (生肖 relation)
    yrel = _branch_rel(ca.pillars["year"].branch, cb.pillars["year"].branch)
    if yrel:
        kind, _ = yrel
        pts = {"六合": 8, "半三合": 8, "六沖": -8, "刑": -4, "六害": -4}[kind]
        chips.append((f"year branches (生肖) {kind}", pts))

    # 3. mutual 用神 supply — does one chart carry what the other needs?
    wa, wb = ca.element_weights, cb.element_weights
    ta, tb = sum(wa.values()) or 1, sum(wb.values()) or 1
    for giver, gw, gt, taker, tys in ((ca, wa, ta, cb, ys_b), (cb, wb, tb, ca, ys_a)):
        n = 0
        for e in tys["favourable"]:
            if gw.get(e, 0) / gt >= 0.2 and n < 2:
                chips.append((f"{giver.person} is rich in {ELEMENT_EN[e]}{e} — "
                              f"an element {taker.person} needs", 6))
                n += 1
        dom = max(gw, key=gw.get)
        if dom in tys["unfavourable"]:
            chips.append((f"{giver.person}'s dominant {ELEMENT_EN[dom]}{dom} is an "
                          f"element {taker.person} avoids", -6))

    score = max(5, min(95, 50 + sum(d for _, d in chips)))
    band = ("very compatible 上等" if score >= 70 else
            "compatible 中上" if score >= 55 else
            "workable 中" if score >= 45 else "needs effort 需磨合")

    rel_ab = ten_god(da.stem, db.stem)
    rel_ba = ten_god(db.stem, da.stem)
    notes.append(f"In {ca.person}'s chart, {cb.person}'s Day Master {db.stem} appears "
                 f"as {rel_ab} ({TEN_GOD_EN[rel_ab]}); seen the other way, "
                 f"{ca.person} appears to {cb.person} as {rel_ba} "
                 f"({TEN_GOD_EN[rel_ba]}).")

    paras = [
        f"Overall: {score}/100 — {band}. The score adds the cited factors below to a "
        "neutral 50; classical 合婚 weighs the day pillars (the 'spouse palaces') "
        "heaviest, then the year branches, then whether each chart supplies elements "
        "the other needs.",
        notes[0] + " These relations describe the natural dynamic (who energises, "
        "who steadies whom), not the quality of the relationship.",
        "Element supply is the practical lever: when one person is rich in an element "
        "the other needs, simply spending time together, sharing rooms and colours "
        "aligned to that element, tends to feel supportive. A clash factor, if any, "
        "is managed the usual ways — separate work corners, calmer decor, and dates "
        "picked to avoid days clashing either person.",
    ]
    return {"a": ca.person, "b": cb.person,
            "day_pillars": [str(da), str(db)], "score": score, "band": band,
            "chips": [{"label": l, "delta": d} for l, d in chips],
            "relation": {"a_sees_b": rel_ab, "b_sees_a": rel_ba},
            "interpretation": {"paragraphs": paras},
            "source_ref": "合婚 pairwise tables (day/year branch relations + 五合 + "
                          "用神 supply — MODERN SYNTHESIS weights)"}
