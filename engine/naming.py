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


# Directional 三才 factors (reviewer's proposal 2026-10-04; school-dependent). Each pair is read
# upper → lower (天→人, 人→地):
#   上生下 "生" 1.0 · 同 "比" 0.8 · 下生上 "洩" 0.4 · 人剋对方 0.2 · 人被剋 0
SANCAI_FACTOR = {"生": 1.0, "比": 0.8, "洩": 0.4, "人剋": 0.2, "被剋": 0.0}


def sancai(grids: dict) -> dict:
    """三才 (天人地) harmony via the 生剋 cycle, scored by direction.

    `relations` keeps the short labels (生/比/洩/剋/受剋 read from the upper position);
    `detail` carries the plain reading and factor of each pair; `score` is the mean factor
    (0–1) and `verdict` 吉 ≥ 0.8 · 中 ≥ 0.4 · 凶 below."""
    els = [GRID_EL[grids[k]["num"] % 10] for k in ("天格", "人格", "地格")]
    names = ("天", "人", "地")

    def rel(i: int) -> tuple[str, str, str]:
        a, b = els[i], els[i + 1]
        up, lo = names[i], names[i + 1]
        if SHENG[a] == b:
            return "生", "生", f"{up}{a}生{lo}{b}"
        if a == b:
            return "比", "比", f"{up}{a}{lo}{b}比和"
        if SHENG[b] == a:
            return "洩", "洩", f"{lo}{b}生{up}{a}"
        upper_overcomes = KE[a] == b
        ren_is_upper = up == "人"
        if upper_overcomes:                       # 上剋下
            kind = "人剋" if ren_is_upper else "被剋"
            return "剋", kind, f"{up}{a}剋{lo}{b}"
        kind = "被剋" if ren_is_upper else "人剋"  # 下剋上
        return "受剋", kind, f"{lo}{b}剋{up}{a}"

    rs = [rel(0), rel(1)]
    factors = [SANCAI_FACTOR[k] for _, k, _ in rs]
    score = sum(factors) / 2
    verdict = "吉" if score >= 0.8 else "中" if score >= 0.4 else "凶"
    return {"elements": els, "relations": [r[0] for r in rs], "score": round(score, 3),
            "verdict": verdict,
            "detail": [{"pair": f"{names[i]}→{names[i + 1]}", "text": rs[i][2], "kind": rs[i][1],
                        "factor": factors[i]} for i in range(2)],
            "explanation": "，".join(r[2] for r in rs)}


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
        score = (lucky * 10 + sc["score"] * 16
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
                    trad: dict | None = None, meaning: str | None = None, sex: str | None = None) -> dict:
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
    mtags = meaning_tags()
    cat = _check_category(meaning)
    base = []
    for ch, e, pyn, in_pool in _universe():
        if ch in taken:
            continue
        if (ch in blocked or gender_mismatch(ch, sex)) and not q:
            continue                         # screened / other-gender characters surface only in a pinyin search
        if cat and cat not in (mtags.get(ch) or {}).get("tags", []):
            continue
        el = e.get("el")
        if q and not pyn.startswith(q):
            continue
        if el:
            if want and el not in want:
                continue
        elif not (q or cat):
            continue                         # 未定 characters need a pinyin query or a meaning category
        base.append((ch, e, in_pool))
    cache: dict[int, int] = {}

    def ji(ks: int) -> int:
        if ks not in cache:
            cache[ks] = projected_ji(s_ks, g_ks, slot, ks)
        return cache[ks]

    chips = sorted({e["ks"] for ch, e, _ in base if ch not in blocked}, key=lambda k: (-ji(k), k))[:6]
    rows = [r for r in base if not strokes or r[1]["ks"] in set(strokes)]
    rows.sort(key=lambda r: (r[0] in blocked, gender_mismatch(r[0], sex), not r[1].get("el"), not r[2], -ji(r[1]["ks"]),
                             r[1]["lvl"], r[1]["ks"], r[0]))
    start = max(0, (page - 1) * per)
    tiles = [{"ch": ch, "py": e.get("py") or "", "ks": e["ks"], "el": e.get("el"),
              "pool": in_pool, "lvl": e["lvl"], "ji": ji(e["ks"]),
              "contested": bool(e.get("el_contested")),
              "blocked": ch in blocked, "why": (blocked.get(ch) or {}).get("why"), **_char_extras(ch, sex)}
             for ch, e, in_pool in rows[start:start + per]]
    return {"slot": slot, "total": len(rows), "page": page, "per": per, "tiles": tiles,
            "chips": [{"ks": k, "ji": ji(k)} for k in chips],
            "fav": ys["favourable"], "els": sorted(want), "meaning": cat}


# ---- quantitative score (0–100) ------------------------------------------------
# Reviewer's weights (research/naming_method_review_2026-10-04.md §4), adopted 2026-10-04:
#   用神 30 — mean over the given characters of the role: 用神 1.0 · 喜 0.7 · 闲 0.3 · 未定 0.3 · 忌 0.
#   五格 25 — only the grids the given name controls (天格 is fixed by the surname).
#            双名: 人格 8 · 地格 7 · 總格 7 · 外格 3.
#            单名: 人格 = 總格 (one number) 15 · 地格 10 · 外格 unscored (a fixed convention).
#            A grid scores its weight when 吉, else 0 (one cited 吉 set; no 大吉/半吉 grades yet).
#   三才 15 — the mean directional factor of the two relations (see SANCAI_FACTOR).
#   音韵 5 — how the full name sounds (see SOUND_PENALTY and sound_score).
#   字义 10 — mean over the given characters: 1.0 with at least one meaning category,
#            0.5 allowed but uncategorised, 0 screened as adverse.
#   可信度 10 — how far each element assignment can be trusted: curated 1.0 · curated but
#            disputed 0.6 · inferred from the radical only 0.5 · no element 0.
GRID_WEIGHT = {"人格": 8, "地格": 7, "總格": 7, "外格": 3}
GRID_WEIGHT_SINGLE = {"人格": 15, "地格": 10}
ROLE_SCORE = {"用神": 1.0, "喜": 0.7, "闲": 0.3, "未定": 0.3, "忌": 0.0}
CONF_CURATED, CONF_CONTESTED, CONF_RADICAL = 1.0, 0.6, 0.5
SCORE_MAX = {"yongshen": 30, "wuge": 25, "sancai": 15, "meaning": 10, "sound": 5, "gender": 5, "confidence": 10}
# 性别 5 — mean over the given characters: neutral or matching the child's sex 1.0, a character
#          that reads as the other gender 0 (data/naming/gender_tags.json; no sex given → 1.0).
PART_LABEL = {"yongshen": {"zh": "用神", "en": "useful element"}, "wuge": {"zh": "五格", "en": "five grids (strokes)"},
              "sancai": {"zh": "三才", "en": "heaven · person · earth"}, "meaning": {"zh": "字义", "en": "meaning"},
              "sound": {"zh": "音韵", "en": "sound"},
              "gender": {"zh": "性别", "en": "gender fit"}, "confidence": {"zh": "可信度", "en": "element confidence"}}
GRADES = ((90, "上佳", "excellent"), (80, "佳", "good"), (65, "可", "fair"), (0, "待斟酌", "reconsider"))


@lru_cache(maxsize=1)
def gender_tags() -> dict:
    """{char: "F" | "M"} — characters that read clearly as one gender; the rest are neutral."""
    path = ROOT / "data/naming/gender_tags.json"
    if not path.exists():
        return {}
    return {k: v for k, v in json.loads(path.read_text("utf8")).items() if not k.startswith("_")}


def gender_mismatch(ch: str, sex: str | None) -> bool:
    g = gender_tags().get(ch)
    return bool(g and sex in ("M", "F") and g != sex)


# 音韵 penalties, subtracted from 1.0 (floor 0). A house convention for a readable name,
# not a classical rule: the tradition gives preferences, not numbers.
SOUND_PENALTY = {"same_tone": 0.4,        # every syllable on one tone
                 "third_third": 0.2,      # the last two syllables both third tone
                 "neutral_end": 0.2,      # the name ends on a neutral tone
                 "same_syllable": 0.4,    # adjacent identical syllables (toneless) …
                 "reduplication": 0.1,    # … unless the given name repeats one character on purpose
                 "same_initial": 0.2, "same_final": 0.2, "repeat_cap": 0.4,
                 "homophone": 1.0, "near_homophone": 0.5}
_INITIALS = ("zh", "ch", "sh", "b", "p", "m", "f", "d", "t", "n", "l", "g", "k", "h", "j", "q", "x", "r",
             "z", "c", "s", "y", "w")
_TONE_MARKS = {c: t for t, cs in enumerate(("āēīōūǖ", "áéíóúǘ", "ǎěǐǒǔǚ", "àèìòùǜ"), 1) for c in cs}


@lru_cache(maxsize=1)
def sound_rules() -> dict:
    path = ROOT / "data/naming/sound_rules.json"
    return json.loads(path.read_text("utf8")) if path.exists() else {"surname_readings": {}, "homophones": []}


def _syllable(py: str) -> tuple[str, str, str, int]:
    """(toneless, initial, final, tone 1–5) of one tone-marked pinyin syllable (ü → v)."""
    tone = next((_TONE_MARKS[c] for c in py.lower() if c in _TONE_MARKS), 5)
    base = strip_pinyin(py)
    ini = next((i for i in _INITIALS if base.startswith(i)), "")
    return base, ini, base[len(ini):], tone


def _near(syl: str) -> str:
    """Fold the pairs speakers commonly merge: z/zh, c/ch, s/sh, n/l, -n/-ng."""
    for a, b in (("zh", "z"), ("ch", "c"), ("sh", "s")):
        if syl.startswith(a):
            syl = b + syl[2:]
    if syl.startswith("l"):
        syl = "n" + syl[1:]
    return syl[:-1] if syl.endswith("ng") else syl


def name_syllables(surname: str, given: str) -> list[tuple]:
    sr = sound_rules()["surname_readings"]
    pys = sr[surname].split() if surname in sr else [sr.get(ch) or (char_info(ch) or {}).get("py") or "" for ch in surname]
    pys += [(char_info(ch) or {}).get("py") or "" for ch in given]
    return [_syllable(py) for py in pys]


def sound_score(surname: str, given: str) -> dict:
    """音韵 of the full name: {score 0–1, tones, findings[{kind, zh, en, penalty}]}."""
    P = SOUND_PENALTY
    syl = name_syllables(surname, given)
    chars = surname + given
    tones = [t for *_, t in syl]
    out = []

    def add(kind: str, zh: str, en: str, pen: float | None = None):
        out.append({"kind": kind, "zh": zh, "en": en, "penalty": P[kind] if pen is None else pen})

    if len(set(tones)) == 1:
        add("same_tone", "声调全同", f"every syllable on tone {tones[0]}")
    elif tones[-2:] == [3, 3]:
        add("third_third", "末两字皆上声", "the last two syllables are both third tone")
    if tones[-1] == 5:
        add("neutral_end", "末字轻声", "the name ends on a neutral tone")
    rep, n_s = [], len(surname)
    for i in range(len(syl) - 1):
        a, b, pair = syl[i], syl[i + 1], f"{chars[i]}·{chars[i + 1]}"
        if a[0] == b[0]:
            if i >= n_s and chars[i] == chars[i + 1]:
                rep.append(("reduplication", "叠字", f"{pair} repeated on purpose"))
            else:
                rep.append(("same_syllable", "同音相连", f"{pair} are the same syllable"))
            continue
        if a[1] and a[1] == b[1]:
            rep.append(("same_initial", "声母相同", f"{pair} share the initial {a[1]}-"))
        if a[2] == b[2]:
            rep.append(("same_final", "韵母相同", f"{pair} share the final -{a[2]}"))
    left = P["repeat_cap"]
    for kind, zh, en in rep:
        pen = min(P[kind], left)
        left = round(left - pen, 2)
        add(kind, zh, en, pen)
    base = [x[0] for x in syl]
    hit = {}
    for h in sound_rules()["homophones"]:
        pat = h["pattern"].split()
        for i in range(len(base) - len(pat) + 1):
            run = base[i:i + len(pat)]
            kind = ("homophone" if run == pat else
                    "near_homophone" if [_near(x) for x in run] == [_near(x) for x in pat] else None)
            if kind and (h["sounds_like"] not in hit or kind == "homophone"):
                hit[h["sounds_like"]] = (kind, h, chars[i:i + len(pat)])
    for kind, h, run in hit.values():
        add(kind, f"{run} 音同「{h['sounds_like']}」" if kind == "homophone" else f"{run} 音近「{h['sounds_like']}」",
            f"{run} sounds {'like' if kind == 'homophone' else 'close to'} {h['sounds_like']} ({h['en']})")
    return {"score": round(max(0.0, 1.0 - sum(f["penalty"] for f in out)), 2), "tones": tones, "findings": out,
            "pinyin": [x[0] for x in syl]}


def interpret_name(given: str) -> dict:
    """A possible reading of the given name, composed from the stored per-character
    name-sense phrases (no model call). `partial` when a character has no curated sense."""
    tags = meaning_tags()
    zh, en, cats, partial = [], [], [], False
    for ch in given:
        t = tags.get(ch) or {}
        if t.get("sense"):
            zh.append(t["sense"]["zh"]); en.append(t["sense"]["en"])
        else:
            partial = True
            gl = ((t.get("gloss") or (meaning_exclude().get(ch) or {}).get("gloss") or "").split(";")[0].split(",")[0]).strip()
            zh.append(f"「{ch}」"); en.append(gl or f"the character {ch}")
        cats.append((t.get("tags") or [None])[0])
    if len(zh) == 1:
        return {"zh": zh[0], "en": f"A name suggesting {en[0]}.", "partial": partial}
    if cats[0] and cats[0] == cats[1]:
        z = f"{zh[0]}，{zh[1]}，相得益彰"
    else:
        z = f"既{zh[0]}，又{zh[1]}"
    return {"zh": z, "en": f"A name suggesting: {en[0]}; {en[1]}.", "partial": partial}


def grid_weights(n_given: int) -> dict:
    return GRID_WEIGHT_SINGLE if n_given == 1 else GRID_WEIGHT


def confidence(entry: dict | None) -> float:
    """How far the element assignment can be trusted (the 可信度 part)."""
    if not entry or not entry.get("el"):
        return 0.0
    if (entry.get("el_src") or "").startswith("curated:"):
        return CONF_CONTESTED if entry.get("el_contested") else CONF_CURATED
    return CONF_RADICAL


@lru_cache(maxsize=1)
def meaning_tags() -> dict:
    """{char: {tags: [category ids], gloss}} — data/naming/meaning_tags.json."""
    path = ROOT / "data/naming/meaning_tags.json"
    if not path.exists():
        return {}
    return {k: v for k, v in json.loads(path.read_text("utf8")).items() if not k.startswith("_")}


@lru_cache(maxsize=1)
def meaning_categories() -> list:
    path = ROOT / "data/naming/meaning_tags.json"
    return json.loads(path.read_text("utf8"))["_categories"] if path.exists() else []


def meaning_value(ch: str) -> float:
    """字义 credit of one character: categorised 1.0 · plain 0.5 · screened 0."""
    if ch in meaning_exclude():
        return 0.0
    return 1.0 if (meaning_tags().get(ch) or {}).get("tags") else 0.5


def stroke_score(grids: dict, sc: dict, n_given: int = 2) -> tuple[float, float]:
    """(五格 part of 25, 三才 part of 15) — depends on stroke counts only."""
    wuge = sum(w for k, w in grid_weights(n_given).items() if grids[k]["luck"] == "吉")
    return float(wuge), round(SCORE_MAX["sancai"] * sc["score"], 2)


def score_name(grids: dict, sc: dict, roles: list[str], confs: list[float] | None = None,
               meanings: list[float] | None = None, genders: list[float] | None = None,
               sound: float = 1.0) -> dict:
    n = max(1, len(roles))
    confs = confs if confs is not None else [1.0] * len(roles)
    meanings = meanings if meanings is not None else [1.0] * len(roles)
    genders = genders if genders is not None else [1.0] * len(roles)
    wuge, san = stroke_score(grids, sc, len(roles))
    parts = {"yongshen": round(SCORE_MAX["yongshen"] * sum(ROLE_SCORE[r] for r in roles) / n, 1),
             "wuge": wuge, "sancai": san,
             "meaning": round(SCORE_MAX["meaning"] * sum(meanings) / n, 1),
             "sound": round(SCORE_MAX["sound"] * sound, 1),
             "gender": round(SCORE_MAX["gender"] * sum(genders) / n, 1),
             "confidence": round(SCORE_MAX["confidence"] * sum(confs) / n, 1)}
    gw = ("人/總 15 · 地 10 (单名; 外格 unscored)" if len(roles) == 1 else "人8 地7 總7 外3")
    total = round(sum(parts.values()), 1)
    _, gzh, gen = next(g for g in GRADES if total >= g[0])
    return {"total": total, "parts": parts, "max": dict(SCORE_MAX), "labels": PART_LABEL,
            "grade": {"zh": gzh, "en": gen},
            "basis": f"用神 30 (用神 1.0 · 喜 0.7 · 闲 0.3 · 未定 0.3 · 忌 0) + 五格 25 ({gw}, 吉 only) + "
                     "三才 15 (生 1.0 · 比 0.8 · 洩 0.4 · 人剋 0.2 · 被剋 0) + 字义 10 (categorised 1.0 · "
                     "plain 0.5 · adverse 0) + 音韵 5 (tone pattern, repeated sounds, unlucky homophones) + 性别 5 (neutral or matching 1.0 · "
                     "other gender 0) + 五行可信度 10 (curated 1.0 · disputed 0.6 · radical-inferred 0.5)"}


def _check_category(cat: str | None) -> str | None:
    if cat and cat not in {c["id"] for c in meaning_categories()}:
        raise ValueError(f"unknown meaning category {cat}")
    return cat or None


def char_value(e: dict, ys: dict, ch: str, sex: str | None = None) -> float:
    """Per-character contribution to the score that does not depend on strokes."""
    return (SCORE_MAX["yongshen"] * ROLE_SCORE[_role(e.get("el"), ys)]
            + SCORE_MAX["meaning"] * meaning_value(ch) + SCORE_MAX["confidence"] * confidence(e)
            + SCORE_MAX["gender"] * (not gender_mismatch(ch, sex)))


def _char_extras(ch: str, sex: str | None) -> dict:
    t = meaning_tags().get(ch) or {}
    return {"tags": t.get("tags", []), "gloss": t.get("gloss", ""), "sense": t.get("sense"),
            "gender": gender_tags().get(ch), "mismatch": gender_mismatch(ch, sex)}


def optimise_name(ys: dict, surname: str, given: list[str | None],
                  els: list[str] | None = None, trad: dict | None = None,
                  top: int = 12, meaning: list[str | None] | None = None, sex: str | None = None) -> dict:
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
    mtags = meaning_tags()
    meaning = [_check_category(m) for m in (meaning or [None] * len(given))][:len(given)]
    meaning += [None] * (len(given) - len(meaning))
    pool = [(ch, e, in_pool) for ch, e, _, in_pool in _universe()
            if e.get("el") in want and ch not in taken and ch not in blocked
            and not gender_mismatch(ch, sex)]
    pool.sort(key=lambda r: (-char_value(r[1], ys, r[0]), not r[2], r[1]["lvl"], r[1]["ks"], r[0]))

    def pool_for(i: int) -> list:
        """Characters allowed in box i: the meaning category chosen for that box, if any."""
        cat = meaning[i]
        return pool if not cat else [r for r in pool if cat in (mtags.get(r[0]) or {}).get("tags", [])]

    def group(rows: list) -> dict:
        g: dict[int, list] = {}
        for r in rows:
            g.setdefault(r[1]["ks"], []).append(r)
        return g
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
        means = [meaning_value(ch) for ch, _, _ in chars]
        gens = [0.0 if gender_mismatch(ch, sex) else 1.0 for ch, _, _ in chars]
        return {"given": "".join(ch for ch, _, _ in chars),
                "name": surname + "".join(ch for ch, _, _ in chars),
                "chars": [{"ch": ch, "py": e.get("py") or "", "el": e.get("el"), "role": ro,
                           "ks": e["ks"], "pool": ip, "conf": cf, **_char_extras(ch, sex)}
                          for (ch, e, ip), ro, cf in zip(chars, roles, confs)],
                "ji": sum(1 for v in grids.values() if v["luck"] == "吉"),
                "sancai": sc["verdict"], "zong": grids["總格"]["luck"],
                "score": score_name(grids, sc, roles, confs, means, gens,
                                    sound_score(surname, "".join(ch for ch, _, _ in chars))["score"]),
                "changed": changed,
                "_k": (not all(ip for _, _, ip in chars), max(e["lvl"] for _, e, _ in chars),
                       sum(e["ks"] for _, e, _ in chars))}

    empty = [i for i, ch in enumerate(given) if ch is None]
    as_item = lambda i: (given[i], fixed[i], given[i] in set(POOL))
    rows, mode, baseline = [], "fill", None
    if len(empty) == 0:
        mode = "improve"
        baseline = row([as_item(i) for i in range(len(given))], [])
        for i in range(len(given)):
            for r in pool_for(i):
                chars = [as_item(j) for j in range(len(given))]
                chars[i] = r
                rows.append(row(chars, [i]))
    elif len(given) == 1 or len(empty) == 1:
        i = empty[0]
        for r in pool_for(i):
            chars = [None if j == i else as_item(j) for j in range(len(given))]
            chars[i] = r
            rows.append(row(chars, [i]))
    else:                                    # both boxes empty: rank stroke pairs first, then expand
        g0, g1 = group(pool_for(0)), group(pool_for(1))
        pairs = sorted(((a, b) for a in g0 for b in g1),
                       key=lambda ab: -(strokes_part(ab)[2] + char_value(g0[ab[0]][0][1], ys, g0[ab[0]][0][0])
                                        + char_value(g1[ab[1]][0][1], ys, g1[ab[1]][0][0])))
        for a, b in pairs[:80]:
            for ra in g0[a][:4]:
                for rb in g1[b][:4]:
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
    return {"mode": mode, "baseline": baseline, "results": out, "els": sorted(want), "meaning": meaning,
            "criteria": ["total score (用神 30 + 五格 25 + 三才 15 + 字义 10 + 音韵 5 + 性别 5 + 可信度 10), highest first",
                         "then curated name characters, common level 1 before 2, fewer strokes",
                         "empty boxes filled only from: " + "·".join(sorted(want))]}


_SANCAI_VERB = {"生": "supports", "比": "matches", "洩": "drains", "人剋": "strains", "被剋": "harms"}


def _score_notes(gv: list[dict], grids: dict, sc: dict, sex: str | None, snd: dict) -> dict:
    """One plain line per score part, generated from the facts of this name."""
    cat_en = {c["id"]: c["en"].split(" · ")[0] for c in meaning_categories()}
    blocked = meaning_exclude()
    w = grid_weights(len(gv))
    conf = {CONF_CURATED: "curated", CONF_CONTESTED: "curated but disputed", CONF_RADICAL: "inferred from its radical", 0.0: "no element"}
    mism = [c for c in gv if c["mismatch"]]
    who = {"F": "a girl", "M": "a boy"}.get(sex)
    return {
        "yongshen": ", ".join(f"{c['ch']} {c['el'] or '未定'} ({c['role_en']})" for c in gv),
        "wuge": f"{sum(1 for k in w if grids[k]['luck'] == '吉')} of {len(w)} scored grids auspicious"
                + (" (人格 = 總格 for a single name)" if len(gv) == 1 else ""),
        "sancai": ", ".join(f"{d['text']} {_SANCAI_VERB[d['kind']]}" for d in sc["detail"]),
        "meaning": ", ".join(f"{c['ch']} " + ("adverse meaning" if c["ch"] in blocked else
                                              cat_en[c["tags"][0]] if c["tags"] else "plain meaning") for c in gv),
        "sound": "tones " + "-".join(str(t) for t in snd["tones"]) + ", "
                 + ("; ".join(f["en"] for f in snd["findings"]) or "no clashes"),
        "gender": ("sex not given" if not who else
                   ", ".join(f"{c['ch']} reads as {'feminine' if c['gender'] == 'F' else 'masculine'}" for c in mism)
                   if mism else f"{'both suit' if len(gv) == 2 else 'suits'} {who}"),
        "confidence": ("elements from the curated list" if all(c["conf"] == CONF_CURATED for c in gv) else
                       ", ".join(f"{c['ch']} {conf[c['conf']]}" for c in gv)),
    }


def name_card(ys: dict, surname: str, given: str, trad: dict | None = None, sex: str | None = None) -> dict:
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
                      **(_char_extras(ch, sex) if is_given else
                         {"tags": [], "gloss": "", "sense": None, "gender": None, "mismatch": False}),
                      "radical_inferred": bool(is_given and e.get("el") and not (e.get("el_src") or "").startswith("curated:")),
                      "contested": bool(e.get("el_contested")), "el_alt": e.get("el_alt"),
                      "surname": not is_given})
    grids = five_grids(s_ks, [c["ks"] for c in chars[len(surname):]])
    for k, v in grids.items():
        v["el"] = GRID_EL[v["num"] % 10]
    sc = sancai(grids)
    gv = chars[len(surname):]
    score = score_name(grids, sc, [c["role"] for c in gv], [c["conf"] for c in gv],
                       [meaning_value(c["ch"]) for c in gv], [0.0 if c["mismatch"] else 1.0 for c in gv],
                       (snd := sound_score(surname, given))["score"])
    score["notes"] = _score_notes(gv, grids, sc, sex, snd)
    blocked = meaning_exclude()
    warnings = [{"ch": c["ch"], "why": blocked[c["ch"]]["why"], "class": blocked[c["ch"]]["class"]}
                for c in gv if c["ch"] in blocked]
    warnings += [{"ch": c["ch"], "class": "gender",
                  "why": ("女性字 usually a girl's name character" if c["gender"] == "F"
                          else "男性字 usually a boy's name character")} for c in gv if c["mismatch"]]
    warnings += [{"ch": surname + given, "class": "sound", "why": f"{f['zh']} — {f['en']}"}
                 for f in snd["findings"] if f["kind"] == "homophone"]
    return {"name": surname + given, "surname": surname, "given": given, "chars": chars, "score": score,
            "sound": snd, "interpretation": interpret_name(given),
            "warnings": warnings,
            "grids": [{"grid": k, **grids[k]} for k in GRID_ORDER],
            "ji": sum(1 for v in grids.values() if v["luck"] == "吉"),
            "sancai": sc, "trad": "".join(c["trad"] for c in chars),
            "strokes": [c["ks"] for c in chars],
            "fav": ys["favourable"], "unfav": ys["unfavourable"]}
