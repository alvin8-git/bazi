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
KIND_EN = {"六合": "Six Harmony", "半三合": "Half Three Harmony", "六沖": "Six Clash",
           "刑": "Punishment", "六害": "Six Harm"}
PALACES = ("year", "month", "day", "hour")
PALACE_ZH = {"year": "年柱", "month": "月柱", "day": "日柱", "hour": "时柱"}

# ---------------------------------------------------------------------------
# 2026-10-10 batch 2 (owner-approved "recommended" set): the relations the page already listed
# but the score ignored. Light weights for the fourteen grid cells the day-day and year-year
# rules leave out, capped; medium weights for the stem rules. Classical basis: stem 五合, branch
# 刑冲会合 and 天干相冲 (三命通會, 淵海子平; chapter titles not verified). Reading them across two
# charts, counting a contested 合 once, leaving 拱合 half-trines unscored, the day-over-other
# weighting, the caps, and scoring only same-polarity 相克 (the 七殺 relation; 正官-type control
# is not scored) are our modern synthesis. Reviewed blind 2026-10-10 (review-batch2.md).
# ---------------------------------------------------------------------------
_CROSS_WUHE = 3                                    # a Day Master with a partner's non-day stem, once per direction
_CELL_PTS = {"day": {"六合": 4, "半三合": 3, "六沖": -4, "刑": -2, "六害": -2},        # cell touches a day pillar
             "other": {"六合": 2, "半三合": 1, "六沖": -2, "刑": -1, "六害": -1}}
_CELL_CAP = 6                                      # bonds and frictions capped separately
_DM_CHONG, _DM_KE = -5, -2                         # Day Masters 天干相冲 / 相克
_CARDINAL = set("子午卯酉")                         # a half-trine without one is 拱合: shown, not scored
_STEM_CHONG = {frozenset(x) for x in ("甲庚", "乙辛", "丙壬", "丁癸")}
_STEM_KE = {frozenset(x) for x in ("甲戊", "乙己", "丙庚", "丁辛", "戊壬", "己癸")}   # same-polarity 克, not a 冲 or 合


def relation_additions(ca, cb) -> list[dict]:
    """Batch 2 rows: cross-stem 五合, the unscored grid cells (capped), Day Master stem clash or control.
    Each row carries delta (after the cap), raw, bilingual label and plain English; pair_compatibility
    sums them and pair_breakdown lists them, so the two always reconcile."""
    from .wuxing import KE, STEM_ELEMENT
    na, nb = ca.person, cb.person
    sa = {k: ca.pillars[k].stem for k in PALACES}
    sb = {k: cb.pillars[k].stem for k in PALACES}
    rows = []
    # (a) cross-stem 五合, skipped when the Day Masters already combine (scored by the frozen rule)
    if WUHE.get(sa["day"]) != sb["day"]:
        for who, own, other, nm_o in ((na, sa, sb, nb), (nb, sb, sa, na)):
            hits = [k for k in ("year", "month", "hour") if WUHE.get(own["day"]) == other[k]]
            if hits:                                    # several matching stems count once (争合)
                ks = " and ".join(f"{k} stem {other[k]}" for k in hits)
                kz = "、".join(f"{PALACE_ZH[k]}天干{other[k]}" for k in hits)
                rows.append({"kind": "cross_stem", "delta": _CROSS_WUHE, "raw": _CROSS_WUHE, "pillars": "stem",
                             "zh": f"{who}日主{own['day']}合{nm_o}{kz}（五合）",
                             "en": f"{who}'s Day Master {own['day']} combines with {nm_o}'s {ks}: Five Combination",
                             "plain": f"{who}'s Day Master {own['day']} combines with {nm_o}'s {ks}: a Five Combination (五合), a pull between them rather than a lock",
                             "giver": who, "receiver": nm_o, "stem": own["day"], "hits": hits})
    # (b) the fourteen unscored cells; a branch pair counts once, and never again when the frozen day-day or
    # year-year rule already scored that same pair (reviewer, 2026-10-10); 拱合 half-trines are not scored
    best, order = {}, 0
    frozen_pairs = {(ca.pillars[k].branch, cb.pillars[k].branch) for k in ("day", "year") if _branch_rel(ca.pillars[k].branch, cb.pillars[k].branch)}
    for pa in PALACES:
        for pb in PALACES:
            if (pa == pb == "day") or (pa == pb == "year"):
                continue
            ba, bb = ca.pillars[pa].branch, cb.pillars[pb].branch
            r = _branch_rel(ba, bb)
            if not r or (ba, bb) in frozen_pairs:
                continue
            kind = r[0]
            if kind == "半三合" and not (set(ba + bb) & _CARDINAL):
                continue
            day = "day" in (pa, pb)
            pts = _CELL_PTS["day" if day else "other"][kind]
            key = (ba, bb)
            order += 1
            if key not in best or abs(pts) > abs(best[key]["raw"]):
                best[key] = {"kind": "cell", "raw": pts, "pillar_a": pa, "pillar_b": pb, "branch_a": ba, "branch_b": bb,
                             "relation": kind, "pillars": f"{pa}-{pb}", "_ord": (0 if day else 1, order),
                             "zh": f"{na}{PALACE_ZH[pa]}{ba}与{nb}{PALACE_ZH[pb]}{bb}{kind}",
                             "en": f"{na}'s {pa} pillar {ba} and {nb}'s {pb} pillar {bb}: {KIND_EN[kind]}",
                             "plain": f"{na}'s {pa} pillar {ba} and {nb}'s {pb} pillar {bb} " + ("form a " if pts > 0 else "meet in a ") + KIND_EN[kind]}
    pos = neg = 0
    for row in sorted(best.values(), key=lambda x: (-abs(x["raw"]), x.pop("_ord"))):   # largest first, day cells, then grid order
        pts = row["raw"]
        if pts > 0:
            take = max(0, min(pts, _CELL_CAP - pos)); pos += take
        else:
            take = min(0, max(pts, -_CELL_CAP - neg)); neg += take
        row["delta"] = take
        row["capped"] = take != pts
        if row["capped"]:
            row["en"] += " (cap reached)"; row["zh"] += "（已达上限）"
        rows.append(row)
    # (c) Day Master against Day Master: 天干相冲, or plain 相克
    pr = frozenset((sa["day"], sb["day"]))
    if pr in _STEM_CHONG:
        rows.append({"kind": "dm_stem", "delta": _DM_CHONG, "raw": _DM_CHONG, "pillars": "day-day", "relation": "相冲",
                     "zh": f"日主{sa['day']}{sb['day']}天干相冲", "en": f"Day Masters {sa['day']} and {sb['day']}: stem clash (天干相冲)",
                     "plain": f"their Day Masters {sa['day']} and {sb['day']} clash as stems (天干相冲)"})
    elif pr in _STEM_KE:
        ea, eb = STEM_ELEMENT[sa["day"]], STEM_ELEMENT[sb["day"]]
        who, e1, e2 = (na, ea, eb) if KE[ea] == eb else (nb, eb, ea)
        rows.append({"kind": "dm_stem", "delta": _DM_KE, "raw": _DM_KE, "pillars": "day-day", "relation": "相克",
                     "zh": f"日主{sa['day']}{sb['day']}相克", "en": f"Day Masters {sa['day']} and {sb['day']}: {who}'s element controls the other's (相克)",
                     "plain": f"{who}'s Day Master element ({ELEMENT_EN[e1]}) controls the other's ({ELEMENT_EN[e2]}) (相克)"})
    return rows


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

    # 4. batch 2: cross-stem 五合, the other grid cells (capped), Day Master stem clash or control
    for row in relation_additions(ca, cb):              # capped rows stay listed at 0, like "no link"
        chips.append((row["plain"][0].upper() + row["plain"][1:] + (" (cap reached)." if row.get("capped") else "."), row["delta"]))

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
                          "Combination, element supply, and (lightly weighted) the other "
                          "pillar relations and stem combinations between the two charts. "
                          "The element-supply and cross-chart weights are our own modern choice."}
