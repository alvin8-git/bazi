"""調候 climate layer — the 窮通寶鑑 seasonal-adjustment table (10 day stems ×
12 month branches), surfaced as a DISCLOSURE beside the 扶抑 verdict, never as
an override.

Table provenance (2026-09-19): two independent reproductions of the standard
喜用提要 summary cross-checked cell-by-cell — a Sina blog carrying all ten
stems and a Sina News article carrying 甲–己 with the book's own explanations
(72 overlapping cells: 100% agreement on the PRIMARY god, one substantive
divergence 甲/未 resolved to the source whose explanation text supports it).
庚–癸 rest on the single full source plus spot-checks against well-known
提要 lines (三月庚金 甲丁 · 四月癸水 專用辛 · 七月壬水 戊丁 · 冬辛 用丙).
Gods are ordered primary-first, as in the 提要.
"""
from __future__ import annotations

from .wuxing import STEM_ELEMENT

TIAOHOU = {
    "甲": {"寅": "丙癸", "卯": "庚丙丁戊己", "辰": "庚丁壬", "巳": "癸庚丁", "午": "癸庚丁", "未": "癸庚丁", "申": "庚丁壬", "酉": "庚丁丙", "戌": "庚甲丁壬癸", "亥": "庚丁丙戊", "子": "丁庚丙", "丑": "丁庚丙"},
    "乙": {"寅": "丙癸", "卯": "丙癸", "辰": "癸丙戊", "巳": "癸", "午": "癸丙", "未": "癸丙", "申": "丙癸己", "酉": "癸丙丁", "戌": "癸辛", "亥": "丙戊", "子": "丙", "丑": "丙"},
    "丙": {"寅": "壬庚", "卯": "壬己", "辰": "壬甲", "巳": "壬癸庚", "午": "壬庚", "未": "壬庚", "申": "壬戊", "酉": "壬癸", "戌": "甲壬", "亥": "甲戊庚壬", "子": "壬戊己", "丑": "壬甲"},
    "丁": {"寅": "甲庚", "卯": "庚甲", "辰": "甲庚", "巳": "甲庚", "午": "壬庚癸", "未": "甲壬庚", "申": "甲庚丙戊", "酉": "甲庚丙戊", "戌": "甲庚戊", "亥": "甲庚", "子": "甲庚", "丑": "甲庚"},
    "戊": {"寅": "丙甲癸", "卯": "丙甲癸", "辰": "甲丙癸", "巳": "甲丙癸", "午": "壬甲丙", "未": "癸丙甲", "申": "丙癸甲", "酉": "丙癸", "戌": "甲丙癸", "亥": "甲丙", "子": "丙甲", "丑": "丙甲"},
    "己": {"寅": "丙庚甲", "卯": "甲癸丙", "辰": "丙癸甲", "巳": "癸丙", "午": "癸丙", "未": "癸丙", "申": "丙癸", "酉": "丙癸", "戌": "甲丙癸", "亥": "丙甲戊", "子": "丙甲戊", "丑": "丙甲戊"},
    "庚": {"寅": "戊甲丙壬丁", "卯": "丁甲丙庚", "辰": "甲丁壬癸", "巳": "壬丙丁戊", "午": "壬癸", "未": "丁甲", "申": "丁甲", "酉": "丁甲丙", "戌": "甲壬", "亥": "丁丙", "子": "丁甲丙", "丑": "丙丁甲"},
    "辛": {"寅": "己壬庚", "卯": "壬甲", "辰": "壬甲", "巳": "壬甲癸", "午": "壬己癸", "未": "壬庚甲", "申": "壬甲戊", "酉": "壬甲丁", "戌": "壬甲", "亥": "壬丙", "子": "丙戊壬甲", "丑": "丙壬戊己"},
    "壬": {"寅": "庚丙戊", "卯": "戊辛庚", "辰": "甲庚丙", "巳": "壬辛庚癸", "午": "癸庚辛", "未": "辛甲", "申": "戊丁", "酉": "甲庚", "戌": "甲丙", "亥": "戊丙庚", "子": "戊丙", "丑": "丙甲丁"},
    "癸": {"寅": "辛丙", "卯": "庚辛", "辰": "丙辛甲", "巳": "辛", "午": "庚壬癸", "未": "庚辛癸", "申": "丁", "酉": "辛丙", "戌": "辛甲癸壬", "亥": "庚辛戊丁", "子": "丙辛", "丑": "丙丁"},
}


def tiaohou_reading(c, ys: dict) -> dict:
    """Chart-specific 調候: the season's prescribed stems for this Day Master
    and month, whether each is visible (透) in this chart, and how the climate
    prescription sits against the 扶抑 favourable elements."""
    from .bazi import ten_god
    dm, mb = c.day_master, c.pillars["month"].branch
    gods = list(TIAOHOU.get(dm, {}).get(mb, ""))
    if not gods:
        return {}
    visible = {c.pillars[p].stem for p in ("year", "month", "hour")}
    fav = set(ys["favourable"])
    items = []
    for st in gods:
        items.append({"stem": st, "element": STEM_ELEMENT[st],
                      "god": ten_god(dm, st),
                      "visible": st in visible,
                      "aligned": STEM_ELEMENT[st] in fav})
    n_align = sum(1 for i in items if i["aligned"])
    verdict = ("agrees" if n_align == len(items) else
               "partially agrees" if n_align else "differs")
    line = (f"調候 (窮通寶鑑): a {dm} Day Master in the {mb} month calls for "
            + "、".join(f'{i["stem"]}({i["god"]}{"·透" if i["visible"] else "·不透"})'
                        for i in items)
            + f" — the climate prescription {verdict} with the 扶抑 verdict"
            + ("." if verdict == "agrees" else
               ": where they part, satisfy the 調候 stems through USE (timing, "
               "activity, environment) and the 扶抑 elements through SUPPORT "
               "(colours, sectors, fields) — both, not either."))
    return {"gods": items, "verdict": verdict, "line": line,
            "source_ref": "窮通寶鑑 喜用提要 (cross-checked reproduction; "
                          "primary god uncontested in all sources)"}
