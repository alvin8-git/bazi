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
import unicodedata
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


@lru_cache(maxsize=1)
def meaning_exclude() -> dict:
    """Characters screened out for clearly adverse meaning (data/naming/meaning_exclude.json)."""
    path = ROOT / "data/naming/meaning_exclude.json"
    if not path.exists():
        return {}
    return {k: v for k, v in json.loads(path.read_text("utf8")).items() if not k.startswith("_")}


def char_info(ch: str, trad: str | None = None) -> dict | None:
    """Dataset entry for one character. `trad` selects one of its traditional forms
    (data `trad_alts`); the returned `ks` is the 康熙 stroke count of that form."""
    e = _chardata().get(ch)
    if e is None or not trad or trad == e.get("trad"):
        return e
    alts = e.get("trad_alts") or {}
    if trad not in alts:
        raise ValueError(f"{trad} is not a traditional form of {ch}")
    return dict(e, trad=trad, ks=alts[trad])


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
    # 外格, the common convention:
    #   单姓双名 = 名末 + 1 · 单姓单名 = 2 · 复姓双名 = 姓首 + 名末 · 复姓单名 = 姓首 + 1
    if len(s) == 1:
        wai = (g[1] + 1) if len(g) > 1 else 2
    else:
        wai = (s[0] + g[1]) if len(g) > 1 else (s[0] + 1)
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


# ---------------------------------------------------------------- name builder
# Picker universe: 通用规范汉字表 levels 1–2 (data `lvl`), curated POOL first.
GRID_ORDER = ("天格", "人格", "地格", "外格", "總格")
ROLE_EN = {"用神": "useful element", "喜": "favourable", "忌": "unfavourable",
           "闲": "neutral", "未定": "element not set", "姓": "surname"}


def strip_pinyin(py: str | None) -> str:
    """Tone-free lowercase pinyin (ü → v) for prefix search."""
    s = (py or "").lower()
    for c in "üǖǘǚǜ":
        s = s.replace(c, "v")
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def _surname_ks(surname: str) -> list[int]:
    out = []
    for ch in surname:
        e = char_info(ch)
        if not e:
            raise ValueError(f"surname character {ch} not in dataset")
        out.append(e["ks"])
    if not 1 <= len(out) <= 2:
        raise ValueError("surname must be 1-2 characters")
    return out


def _ji_count(s_ks: list[int], g_ks: list[int]) -> int:
    """吉 among 人/地/外/總 — 天格 is fixed by the surname and not counted."""
    grids = five_grids(s_ks, g_ks)
    return sum(1 for k, v in grids.items() if k != "天格" and v["luck"] == "吉")


def projected_ji(s_ks: list[int], g_ks: list[int | None], slot: int, ks: int) -> int:
    """吉 count (of 4) if `slot` takes a character of `ks` strokes. With the partner slot
    still empty, the best reachable over partner stroke counts 1–30."""
    g = list(g_ks)
    g[slot] = ks
    if all(v is not None for v in g):
        return _ji_count(s_ks, g)
    other = next(i for i, v in enumerate(g) if v is None)
    best = 0
    for k in range(1, 31):
        t = list(g)
        t[other] = k
        best = max(best, _ji_count(s_ks, t))
    return best


def _role(el: str | None, ys: dict) -> str:
    fav, unf = ys["favourable"], ys["unfavourable"]
    if not el:
        return "未定"
    if fav and el == fav[0]:
        return "用神"
    if el in fav:
        return "喜"
    if el in unf:
        return "忌"
    return "闲"


@lru_cache(maxsize=1)
def _universe() -> tuple:
    pool = set(POOL)
    out = []
    for ch, e in _chardata().items():
        if e.get("lvl"):
            out.append((ch, e, strip_pinyin(e.get("py")), ch in pool))
    return tuple(out)


def slot_candidates(ys: dict, surname: str, given: list[str | None], slot: int,
                    els: list[str] | None = None, strokes: list[int] | None = None,
                    py: str = "", page: int = 1, per: int = 48,
                    trad: dict | None = None) -> dict:
    """Characters offered for one empty box of the name.

    `given` holds the chosen characters (None for an empty box); its length is the name
    length (1 or 2). Filters combine: `els` (default: the 用神 elements), `strokes`
    (康熙 counts) and `py` (tone-free prefix). Without a pinyin query only element-tagged
    characters are listed; with one, untagged characters appear as 未定.
    Returns {total, tiles[], chips[] (top six stroke counts by reachable 吉), fav, slot}."""
    if not 1 <= len(given) <= 2 or not 0 <= slot < len(given):
        raise ValueError("given must have 1-2 boxes and slot must index one of them")
    trad = trad or {}
    s_ks = _surname_ks(surname)
    g_ks = [None if ch is None else char_info(ch, trad.get(ch))["ks"] for ch in given]
    g_ks[slot] = None
    taken = set(surname) | {ch for ch in given if ch}
    want = set(els) if els is not None else set(ys["favourable"])
    q = strip_pinyin(py.strip())
    blocked = meaning_exclude()
    base = []
    for ch, e, pyn, in_pool in _universe():
        if ch in taken:
            continue
        if ch in blocked and not q:
            continue                         # screened characters surface only in a pinyin search
        el = e.get("el")
        if q:
            if not pyn.startswith(q):
                continue
            if el and want and el not in want:
                continue
        else:
            if not el or (want and el not in want):
                continue
        base.append((ch, e, in_pool))
    cache: dict[int, int] = {}

    def ji(ks: int) -> int:
        if ks not in cache:
            cache[ks] = projected_ji(s_ks, g_ks, slot, ks)
        return cache[ks]

    chips = sorted({e["ks"] for ch, e, _ in base if ch not in blocked}, key=lambda k: (-ji(k), k))[:6]
    rows = [r for r in base if not strokes or r[1]["ks"] in set(strokes)]
    rows.sort(key=lambda r: (r[0] in blocked, not r[2], -ji(r[1]["ks"]), r[1]["lvl"], r[1]["ks"], r[0]))
    start = max(0, (page - 1) * per)
    tiles = [{"ch": ch, "py": e.get("py") or "", "ks": e["ks"], "el": e.get("el"),
              "pool": in_pool, "lvl": e["lvl"], "ji": ji(e["ks"]),
              "contested": bool(e.get("el_contested")),
              "blocked": ch in blocked, "why": (blocked.get(ch) or {}).get("why")}
             for ch, e, in_pool in rows[start:start + per]]
    return {"slot": slot, "total": len(rows), "page": page, "per": per, "tiles": tiles,
            "chips": [{"ks": k, "ji": ji(k)} for k in chips],
            "fav": ys["favourable"], "els": sorted(want)}


# ---- quantitative score (0–100) ------------------------------------------------
# Three parts, each stated so it can be audited:
#   五格 50 — only the grids the given name controls (天格 is fixed by the surname).
#            双名: 人格 16 (主運, the core) · 總格 14 (後運) · 地格 12 (前運) · 外格 8 (副運).
#            单名: 人格 and 總格 are the same number, so it is scored once at 30; 地格 20;
#                  外格 is the fixed convention (2 or 姓首+1) and carries no points.
#            A grid scores its weight when 吉, 0 otherwise (one cited 吉 set; no 大吉/半吉
#            grades until a cited 81數理 table is supplied).
#   三才 25 — two relations (天→人, 人→地), 12.5 each: 生 or 比 full, 洩 half, 剋/受剋 zero.
#   用神 25 — mean over the given characters of role × element confidence.
#            role: 用神 1.0 · 喜 0.8 · 闲 0.4 · 未定 0.3 · 忌 0.
#            confidence: curated element 1.0 · curated but disputed 0.85 · inferred from the
#            radical only 0.8 (a radical is weak evidence of a character's element).
GRID_WEIGHT = {"人格": 16, "總格": 14, "地格": 12, "外格": 8}
GRID_WEIGHT_SINGLE = {"人格": 30, "地格": 20}
RELATION_SCORE = {"生": 1.0, "比": 1.0, "洩": 0.5, "剋": 0.0, "受剋": 0.0}
ROLE_SCORE = {"用神": 1.0, "喜": 0.8, "闲": 0.4, "未定": 0.3, "忌": 0.0}
CONF_CURATED, CONF_CONTESTED, CONF_RADICAL = 1.0, 0.85, 0.8


def grid_weights(n_given: int) -> dict:
    return GRID_WEIGHT_SINGLE if n_given == 1 else GRID_WEIGHT


def confidence(entry: dict | None) -> float:
    """How far the element assignment can be trusted (see the scoring note above)."""
    if not entry or not entry.get("el"):
        return 1.0                      # 未定 already carries its own low role score
    if (entry.get("el_src") or "").startswith("curated:"):
        return CONF_CONTESTED if entry.get("el_contested") else CONF_CURATED
    return CONF_RADICAL


def stroke_score(grids: dict, sc: dict, n_given: int = 2) -> tuple[float, float]:
    """(五格 part of 50, 三才 part of 25) — depends on stroke counts only."""
    wuge = sum(w for k, w in grid_weights(n_given).items() if grids[k]["luck"] == "吉")
    san = sum(12.5 * RELATION_SCORE[r] for r in sc["relations"])
    return float(wuge), san


def score_name(grids: dict, sc: dict, roles: list[str], confs: list[float] | None = None) -> dict:
    confs = confs or [1.0] * len(roles)
    wuge, san = stroke_score(grids, sc, len(roles))
    ysp = 25.0 * sum(ROLE_SCORE[r] * c for r, c in zip(roles, confs)) / max(1, len(roles))
    gw = ("人/總 30 · 地 20 (单名; 外格 unscored)" if len(roles) == 1 else "人16 總14 地12 外8")
    return {"total": round(wuge + san + ysp, 1),
            "parts": {"wuge": wuge, "sancai": san, "yongshen": round(ysp, 1)},
            "max": {"wuge": 50, "sancai": 25, "yongshen": 25},
            "basis": f"五格 50 ({gw}, 吉 only) + 三才 25 (生/比 full, 洩 half) + 用神 25 "
                     "(用神 1.0 · 喜 0.8 · 闲 0.4 · 未定 0.3 · 忌 0, × element confidence: "
                     "curated 1.0 · disputed 0.85 · radical-inferred 0.8)"}


def optimise_name(ys: dict, surname: str, given: list[str | None],
                  els: list[str] | None = None, trad: dict | None = None,
                  top: int = 12) -> dict:
    """Best completions of a partly chosen name, or single-character improvements of a
    complete one, ranked by `score_name` total.

    Ranking: total score ↓, then curated POOL characters first, 通用规范汉字表 level 1 before 2,
    fewer total strokes. Empty boxes are filled from the element-tagged level 1–2 universe,
    limited to `els` (default: the 用神 elements, so a 忌 element appears only when asked for).
    At most 2 results share the same first given character, for variety."""
    if not 1 <= len(given) <= 2:
        raise ValueError("given must have 1-2 boxes")
    trad = trad or {}
    s_ks = _surname_ks(surname)
    want = set(els) if els else set(ys["favourable"])
    fixed = [None if ch is None else char_info(ch, trad.get(ch)) for ch in given]
    if any(ch is not None and e is None for ch, e in zip(given, fixed)):
        raise ValueError("character not in dataset")
    taken = set(surname) | {ch for ch in given if ch}
    blocked = meaning_exclude()
    pool = [(ch, e, in_pool) for ch, e, _, in_pool in _universe()
            if e.get("el") in want and ch not in taken and ch not in blocked]
    pool.sort(key=lambda r: (-ROLE_SCORE[_role(r[1]["el"], ys)] * confidence(r[1]), not r[2],
                             r[1]["lvl"], r[1]["ks"], r[0]))
    by_ks: dict[int, list] = {}
    for r in pool:
        by_ks.setdefault(r[1]["ks"], []).append(r)
    scache: dict[tuple, tuple] = {}

    def strokes_part(g_ks: tuple) -> tuple:
        if g_ks not in scache:
            grids = five_grids(s_ks, list(g_ks))
            sc = sancai(grids)
            scache[g_ks] = (grids, sc, sum(stroke_score(grids, sc, len(g_ks))))
        return scache[g_ks]

    def row(chars: list[tuple], changed: list[int]) -> dict:
        """chars = [(ch, entry, in_pool)] for every given box."""
        grids, sc, _ = strokes_part(tuple(e["ks"] for _, e, _ in chars))
        roles = [_role(e.get("el"), ys) for _, e, _ in chars]
        confs = [confidence(e) for _, e, _ in chars]
        return {"given": "".join(ch for ch, _, _ in chars),
                "name": surname + "".join(ch for ch, _, _ in chars),
                "chars": [{"ch": ch, "py": e.get("py") or "", "el": e.get("el"), "role": ro,
                           "ks": e["ks"], "pool": ip, "conf": cf}
                          for (ch, e, ip), ro, cf in zip(chars, roles, confs)],
                "ji": sum(1 for v in grids.values() if v["luck"] == "吉"),
                "sancai": sc["verdict"], "zong": grids["總格"]["luck"],
                "score": score_name(grids, sc, roles, confs), "changed": changed,
                "_k": (not all(ip for _, _, ip in chars), max(e["lvl"] for _, e, _ in chars),
                       sum(e["ks"] for _, e, _ in chars))}

    empty = [i for i, ch in enumerate(given) if ch is None]
    as_item = lambda i: (given[i], fixed[i], given[i] in set(POOL))
    rows, mode, baseline = [], "fill", None
    if len(empty) == 0:
        mode = "improve"
        baseline = row([as_item(i) for i in range(len(given))], [])
        for i in range(len(given)):
            for r in pool:
                chars = [as_item(j) for j in range(len(given))]
                chars[i] = r
                rows.append(row(chars, [i]))
    elif len(given) == 1 or len(empty) == 1:
        i = empty[0]
        for r in pool:
            chars = [None if j == i else as_item(j) for j in range(len(given))]
            chars[i] = r
            rows.append(row(chars, [i]))
    else:                                    # both boxes empty: rank stroke pairs first, then expand
        pairs = sorted(((a, b) for a in by_ks for b in by_ks),
                       key=lambda ab: -strokes_part(ab)[2])
        for a, b in pairs[:60]:
            for ra in by_ks[a][:4]:
                for rb in by_ks[b][:4]:
                    if ra[0] != rb[0]:
                        rows.append(row([ra, rb], [0, 1]))
    rows.sort(key=lambda r: (-r["score"]["total"], r["_k"], r["given"]))
    out, per_first = [], {}
    for r in rows:
        first = r["given"][0]
        if mode == "fill" and len(given) == 2 and 0 in r["changed"]:
            if per_first.get(first, 0) >= 2:
                continue
            per_first[first] = per_first.get(first, 0) + 1
        if baseline and r["score"]["total"] <= baseline["score"]["total"]:
            continue                         # improvements only
        r.pop("_k")
        out.append(r)
        if len(out) >= top:
            break
    if baseline:
        baseline.pop("_k")
    return {"mode": mode, "baseline": baseline, "results": out, "els": sorted(want),
            "criteria": ["total score (五格 50 + 三才 25 + 用神 25), highest first",
                         "then curated name characters, common level 1 before 2, fewer strokes",
                         "empty boxes filled only from: " + "·".join(sorted(want))]}


def name_card(ys: dict, surname: str, given: str, trad: dict | None = None) -> dict:
    """Everything the name card and certificate show for one complete name."""
    trad = trad or {}
    if not 1 <= len(given) <= 2:
        raise ValueError("given name must be 1-2 characters")
    s_ks = _surname_ks(surname)
    chars = []
    for i, ch in enumerate(surname + given):
        is_given = i >= len(surname)
        e = char_info(ch, trad.get(ch) if is_given else None)
        if not e:
            raise ValueError(f"character {ch} not in dataset")
        role = _role(e.get("el"), ys) if is_given else "姓"
        chars.append({"ch": ch, "py": e.get("py") or "", "el": e.get("el"), "ks": e["ks"],
                      "trad": e["trad"], "trad_alts": (char_info(ch) or {}).get("trad_alts") if is_given else None,
                      "role": role, "role_en": ROLE_EN[role], "conf": confidence(e) if is_given else 1.0,
                      "radical_inferred": bool(is_given and e.get("el") and not (e.get("el_src") or "").startswith("curated:")),
                      "contested": bool(e.get("el_contested")), "el_alt": e.get("el_alt"),
                      "surname": not is_given})
    grids = five_grids(s_ks, [c["ks"] for c in chars[len(surname):]])
    for k, v in grids.items():
        v["el"] = GRID_EL[v["num"] % 10]
    sc = sancai(grids)
    gv = chars[len(surname):]
    score = score_name(grids, sc, [c["role"] for c in gv], [c["conf"] for c in gv])
    blocked = meaning_exclude()
    warnings = [{"ch": c["ch"], "why": blocked[c["ch"]]["why"], "class": blocked[c["ch"]]["class"]}
                for c in gv if c["ch"] in blocked]
    return {"name": surname + given, "surname": surname, "given": given, "chars": chars, "score": score,
            "warnings": warnings,
            "grids": [{"grid": k, **grids[k]} for k in GRID_ORDER],
            "ji": sum(1 for v in grids.values() if v["luck"] == "吉"),
            "sancai": sc, "trad": "".join(c["trad"] for c in chars),
            "strokes": [c["ks"] for c in chars],
            "fav": ys["favourable"], "unfav": ys["unfavourable"]}
