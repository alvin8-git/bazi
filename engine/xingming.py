"""M4c: 姓名學 — 康熙 traditional-stroke validation + 三才五格 + 81數理.

This is the fan-ti check from the original brief, in its correct home: a
separate module complementing BaZi (design premise 1 — names are NOT a BaZi
input). Strokes are 康熙字典 counts (radicals count by full form: 氵=4水,
王=5玉 in composition, 艹=6艸, 辶=7辵 …).

Validation is LOUD: a char missing from the stroke table, or written in
simplified form, raises with the fix named — never a silent wrong number.
ponytail: table covers the family + common chars; extend KANGXI_STROKES as
names are added — unknown chars refuse to compute by design.
"""
from __future__ import annotations

from .wuxing import EARTH, ELEMENT_EN, FIRE, KE, METAL, SHENG, WATER, WOOD

KANGXI_STROKES = {
    # family
    "黃": 12, "優": 17, "仁": 4, "趙": 14, "美": 9, "雁": 12,
    "凱": 12, "琳": 13, "顯": 23, "暄": 13,
    # common, verified Kangxi counts
    "王": 4, "李": 7, "林": 8, "吳": 7, "周": 8, "何": 7, "徐": 10,
    "張": 11, "陳": 16, "劉": 15, "楊": 13, "許": 11, "謝": 17,
    "曾": 12, "洪": 10, "郭": 15, "賴": 16, "廖": 14,
    "明": 8, "華": 14, "德": 15, "文": 4, "偉": 11, "俊": 9,
    "安": 6, "宏": 7, "志": 7, "嘉": 14, "家": 10, "欣": 8,
    "怡": 9, "雅": 12, "婷": 12, "芳": 10, "淑": 12, "慧": 15,
}
SIMPLIFIED_TO_TRAD = {
    "黄": "黃", "优": "優", "赵": "趙", "显": "顯", "凯": "凱",
    "陈": "陳", "刘": "劉", "张": "張", "杨": "楊", "郑": "鄭",
    "谢": "謝", "苏": "蘇", "叶": "葉", "吴": "吳", "许": "許",
    "赖": "賴", "华": "華", "伟": "偉", "晓": "曉", "凤": "鳳",
}

LUCKY = {1, 3, 5, 6, 7, 8, 11, 13, 15, 16, 17, 18, 21, 23, 24, 25, 29, 31, 32,
         33, 35, 37, 39, 41, 45, 47, 48, 52, 57, 61, 63, 65, 67, 68, 81}
HALF = {26, 27, 30, 38, 42, 49, 51, 53, 55, 58, 71, 72, 73, 75, 77, 78}
GRID_ELEMENT = {1: WOOD, 2: WOOD, 3: FIRE, 4: FIRE, 5: EARTH,
                6: EARTH, 7: METAL, 8: METAL, 9: WATER, 0: WATER}


def strokes(char: str) -> int:
    if char in SIMPLIFIED_TO_TRAD:
        raise ValueError(f"'{char}' is simplified — use the 繁體 form "
                         f"'{SIMPLIFIED_TO_TRAD[char]}' (姓名學 requires 康熙 traditional strokes)")
    if char not in KANGXI_STROKES:
        raise ValueError(f"'{char}' not in the Kangxi stroke table — add it to "
                         f"engine/xingming.py KANGXI_STROKES (康熙字典 count) before scoring")
    return KANGXI_STROKES[char]


def _num81(n: int) -> int:
    return n if n <= 81 else n - 80


def _luck(n: int) -> str:
    n = _num81(n)
    return "吉" if n in LUCKY else ("半吉" if n in HALF else "凶")


def five_grids(name: str) -> dict:
    """單姓 names of 1-2 given chars (all five family names are 單姓雙名)."""
    chars = list(name)
    if len(chars) not in (2, 3):
        raise ValueError(f"{name!r}: only single-surname names of 1-2 given chars supported")
    s = [strokes(c) for c in chars]
    surname, given = s[0], s[1:]
    if len(given) == 1:
        tian, ren, di = surname + 1, surname + given[0], given[0] + 1
        wai = 2
    else:
        tian, ren, di = surname + 1, surname + given[0], given[0] + given[1]
        wai = given[1] + 1
    zong = sum(s)
    grids = {"天格": tian, "人格": ren, "地格": di, "外格": wai, "總格": zong}
    out = {}
    for label, n in grids.items():
        el = GRID_ELEMENT[_num81(n) % 10]
        out[label] = {"number": n, "luck": _luck(n),
                      "element": el, "element_en": ELEMENT_EN[el]}
    return out


def sancai(grids: dict) -> dict:
    els = [grids[g]["element"] for g in ("天格", "人格", "地格")]
    def rel(a: str, b: str) -> str:
        if a == b:
            return "比和 (same) — stable"
        if SHENG[a] == b:
            return f"{a}生{b} — supportive"
        if SHENG[b] == a:
            return f"{b}生{a} — nourishing"
        if KE[a] == b:
            return f"{a}剋{b} — conflicting"
        return f"{b}剋{a} — pressured"
    tr, rd = rel(els[0], els[1]), rel(els[1], els[2])
    bad = ("剋" in tr) + ("剋" in rd)
    verdict = "吉" if bad == 0 else ("中" if bad == 1 else "凶")
    return {"elements": "".join(els), "天→人": tr, "人→地": rd, "verdict": verdict,
            "citation": {"rule_id": "sancai", "layer": "xingming",
                         "source_ref": "三才配置 (五行生剋 between 天/人/地格)",
                         "explanation": f"{''.join(els)}: 天人 {tr}; 人地 {rd} → {verdict}"}}


def analyze_name(name: str) -> dict:
    per_char = []
    problems = []
    for ch in name:
        try:
            per_char.append({"char": ch, "kangxi_strokes": strokes(ch), "ok": True})
        except ValueError as e:
            per_char.append({"char": ch, "ok": False, "problem": str(e)})
            problems.append(str(e))
    if problems:
        return {"name": name, "valid": False, "chars": per_char, "problems": problems}
    grids = five_grids(name)
    return {"name": name, "valid": True, "chars": per_char, "grids": grids,
            "sancai": sancai(grids),
            "citation": {"rule_id": "wuge", "layer": "xingming",
                         "source_ref": "熊崎氏 五格剖象 + 81數理 (common variant)",
                         "explanation": ", ".join(f"{g} {v['number']}{v['luck']}"
                                                  for g, v in grids.items())}}


# ---------- per-person 三才五格 reading --------------------------------------
GRID_AREA = {"天格": "inherited / ancestry — least personal",
             "人格": "core character — the most important number",
             "地格": "early life & foundations",
             "外格": "social face & external relations",
             "總格": "the whole life arc"}
LUCK_PHRASE = {"吉": "auspicious", "半吉": "mixed — workable with awareness",
               "凶": "unlucky — classically softened with a usage name, not a legal rename"}


def name_interpretation(p: dict) -> list[str]:
    """Plain-English reading of one analyzed name (grids + 三才)."""
    if not p.get("valid"):
        return []
    lines = [f"{g} {v['number']} ({v['element']}) {v['luck']} — {GRID_AREA[g]}: "
             f"{LUCK_PHRASE[v['luck']]}."
             for g, v in p["grids"].items()]
    sc = p["sancai"]
    lines.append(
        f"三才 {sc['elements']} ({sc['verdict']}): 天→人 {sc['天→人']}; 人→地 "
        f"{sc['人→地']}. The three levels should GENERATE each other — a generating "
        "flow means the phases of life feed one another; a controlling link marks "
        "friction at that junction, softened by leaning on the favourable elements "
        "in colours and surroundings.")
    return lines
