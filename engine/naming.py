"""起名 naming engine v1 — ranked given-name candidates with cited working.

Layers (all cited per candidate):
  1. 用神 element fit — candidate characters must carry the baby's favourable
     elements (data/naming/chardata.json: curated layer > radical rules;
     contested characters surface both readings and rank slightly lower).
  2. 三才五格 stroke numerology — 康熙 strokes (validated 42/42 against
     published tables): 天/人/地/外/總 five grids scored against the 81數理
     auspiciousness table, 三才 harmony from the five-element 生剋 cycle.

v1 scope: candidate universe = the curated common-name pool (all element-
covered, auspicious-by-construction); two-character and single-character
given names; no sound/meaning pairing yet. Correctness gate (design doc):
outputs are candidates for HUMAN CHOICE, spot-check against references
before real-world use.
"""
from __future__ import annotations

import json
from functools import lru_cache
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/naming/chardata.json"

# Common given-name candidate pool (element-covered by the curated layer —
# doubles as a v1 allow-list: every entry is an established auspicious name
# character, which is the lightweight blocklist-by-construction).
POOL = ("伟明华建文军杰涛强磊婷慧芳敏静丽娟雅欣怡佳俊宇轩泽睿涵妍淇铭诗嘉"
        "晨昊彦心雨桐芯梓浩然宸熙哲瑞霖乐天佑成龙凤玲珍珠美丹红霞月星光"
        "志勇刚毅坚宏德仁义礼智信国安邦家宝玉琪琳琦璇莹雪冰清泉江河海洋"
        "松柏杨柳枫桂兰菊梅花草芝英茂盛春夏秋冬永远长久福禄寿喜财富贵"
        "金银铜铁钢山峰岭岩城基圣贤才学章书画琴棋")

# 81數理 — the widely-agreed auspicious set (standard 姓名学 convention).
LUCKY_81 = {1, 3, 5, 6, 7, 8, 11, 13, 15, 16, 17, 18, 21, 23, 24, 25, 29,
            31, 32, 33, 35, 37, 39, 41, 45, 47, 48, 52, 57, 61, 63, 65,
            67, 68, 81}
GRID_EL = {1: "木", 2: "木", 3: "火", 4: "火", 5: "土", 6: "土",
           7: "金", 8: "金", 9: "水", 0: "水"}
SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


@lru_cache(maxsize=1)
def _chardata() -> dict:
    return json.loads(DATA.read_text("utf8"))


def char_info(ch: str) -> dict | None:
    return _chardata().get(ch)


def _grid_luck(n: int) -> str:
    n = ((n - 1) % 81) + 1
    return "吉" if n in LUCKY_81 else "凶/平"


def five_grids(surname_ks: list[int], given_ks: list[int]) -> dict:
    """五格 from 康熙 stroke counts (single- or double-char surname/given)."""
    s, g = surname_ks, given_ks
    tian = (s[0] + 1) if len(s) == 1 else (s[0] + s[1])
    ren = s[-1] + g[0]
    di = (g[0] + g[1]) if len(g) > 1 else (g[0] + 1)
    zong = sum(s) + sum(g)
    wai = zong - ren + (1 if len(s) == 1 and len(g) > 1 else
                        2 if len(s) == 1 and len(g) == 1 else
                        1 if len(g) > 1 else 2)
    # standard convention: 外格 = 總格 − 人格 + 1 for 单姓; the widely-used
    # simple form for 单姓双名 is 第二名字笔画 + 1, for 单姓单名 it is 2.
    if len(s) == 1:
        wai = (g[1] + 1) if len(g) > 1 else 2
    grids = {"天格": tian, "人格": ren, "地格": di, "外格": wai, "總格": zong}
    return {k: {"num": v, "luck": _grid_luck(v)} for k, v in grids.items()}


def sancai(grids: dict) -> dict:
    """三才 (天人地) harmony via the 生剋 cycle."""
    els = [GRID_EL[grids[k]["num"] % 10] for k in ("天格", "人格", "地格")]

    def rel(a, b):
        if SHENG[a] == b:
            return "生", 1
        if a == b:
            return "比", 1
        if SHENG[b] == a:
            return "洩", 0
        if KE[a] == b:
            return "剋", -1
        return "受剋", -1
    r1, s1 = rel(els[0], els[1])
    r2, s2 = rel(els[1], els[2])
    score = s1 + s2
    verdict = "吉" if score >= 2 else "中" if score >= 0 else "凶"
    return {"elements": els, "relations": [r1, r2], "score": score,
            "verdict": verdict,
            "explanation": f"天{els[0]}{r1}人{els[1]}, 人{els[1]}{r2}地{els[2]}"}


def _candidates(ys: dict) -> list[dict]:
    data = _chardata()
    fav = set(ys["favourable"])
    out = []
    for ch in dict.fromkeys(POOL):
        e = data.get(ch)
        if not e or not e.get("el"):
            continue
        if e["el"] in fav:
            out.append({"ch": ch, **e})
    return out


def suggest_names(ys: dict, surname: str, top: int = 20,
                  single_ok: bool = True) -> dict:
    """Ranked given-name candidates for a chart's 用神 + a surname.

    Returns {surname_ks, candidates: [{name, chars, grids, sancai, score,
    reasons, contested}]} — every layer cited.
    """
    data = _chardata()
    s_ks = []
    for ch in surname:
        e = data.get(ch)
        if not e:
            raise ValueError(f"surname character {ch} not in dataset")
        s_ks.append(e["ks"])
    if not s_ks:
        raise ValueError("surname required")
    cands = _candidates(ys)
    fav = ys["favourable"]
    results = []

    def build(chars: list[dict]) -> dict | None:
        grids = five_grids(s_ks, [c["ks"] for c in chars])
        sc = sancai(grids)
        lucky = sum(1 for v in grids.values() if v["luck"] == "吉")
        contested = any(c.get("el_contested") for c in chars)
        score = (lucky * 10 + sc["score"] * 8
                 + sum(6 if c["el"] == fav[0] else 3 for c in chars)
                 - (4 if contested else 0))
        if sc["verdict"] == "凶":
            return None                      # 三才相剋 combinations dropped
        reasons = [
            f"用神: {'/'.join(c['ch'] + '=' + c['el'] for c in chars)} "
            f"(favourable {'·'.join(fav)})",
            f"五格: {lucky}/5 吉 "
            + " ".join(f"{k}{v['num']}{v['luck']}" for k, v in grids.items()),
            f"三才{''.join(sc['elements'])} {sc['verdict']} — {sc['explanation']}",
        ]
        if contested:
            alts = [f"{c['ch']}: {c['el']}(ours)/{c.get('el_alt', '?')}(others)"
                    for c in chars if c.get("el_contested")]
            reasons.append("⚑ contested element — " + "; ".join(alts))
        return {"name": surname + "".join(c["ch"] for c in chars),
                "given": "".join(c["ch"] for c in chars),
                "chars": [{"ch": c["ch"], "el": c["el"], "ks": c["ks"],
                           "py": c.get("py"),
                           "src": c.get("el_src")} for c in chars],
                "grids": grids, "sancai": sc, "score": score,
                "contested": contested, "reasons": reasons}

    for a, b in product(cands, cands):
        if a["ch"] == b["ch"]:
            continue
        r = build([a, b])
        if r:
            results.append(r)
    if single_ok:
        for a in cands:
            r = build([a])
            if r:
                results.append(r)
    results.sort(key=lambda r: -r["score"])
    return {"surname": surname, "surname_ks": s_ks,
            "pool_size": len(cands),
            "source_ref": "用神 element fit + 三才五格 (康熙 strokes, 81數理, "
                          "五行生剋) — v1, human choice + correctness gate "
                          "required before real-world use",
            "candidates": results[:top]}
