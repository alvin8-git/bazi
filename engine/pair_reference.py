"""The pair score's comparison figure and its band words (round 45, 2026-10-15, owner-approved bands 15 / 35 / 35 / 15).

The pair score (engine/hehun.py) is a sum of cited rows added to a neutral 50, and a typical pair finishes near 61, so fixed cut-offs
(70, 55, 45) called about a quarter of random pairs "very compatible" and a tenth "needs effort". This module places a score inside a
frozen reference sample of 20,000 fictional pairs (data/pair_reference_v2.json, built once by scripts/build_pair_reference.py and pinned
by a checksum test) and reads the band word from that standing: the top 15% of random pairs read "very compatible", the next 35%
"compatible", the next 35% "workable", the bottom 15% "needs effort". The score itself never reads this file. If the file is missing
or unreadable, the band falls back to the fixed cut-offs the engine used before, so a pair never shows without a word.

The file stores a histogram {score: count}. The percentile is the mid-rank share (charts scoring below plus half of those scoring
equal), as a whole number from 0 to 100, the same figure the life-area percentile uses (engine/area_reference.py).
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

REF_PATH = Path(__file__).resolve().parent.parent / "data" / "pair_reference_v2.json"     # pair_reference_v1.json (pair-rules-r45, seed 20261051) stays untouched as the record
# The pair rules the reference was built against. A change to any pair rule, point value or threshold means a new version of both.
PAIR_ENGINE_VERSION = "pair-rules-r46"   # r46 (2026-10-15): the pair rules are the r45 rules; the 節 moment now sets year and month pillars, so the reference sample was redrawn (seed 20261062)

# Percentile cuts: >= 85 very compatible (top 15%), >= 50 compatible (next 35%), >= 15 workable (next 35%), else needs effort (bottom 15%).
CUT_VERY, CUT_COMPAT, CUT_WORKABLE = 85, 50, 15
# The fixed cut-offs of the engine before round 45. They stay as the fallback, and nothing else reads them.
FALLBACK_CUTS = (45, 55, 70)                                  # raw score minimum for workable, compatible, very compatible
WORDS = ("needs effort", "workable", "compatible", "very compatible")          # lowest to highest
ZH = {"very compatible": "上等", "compatible": "中上", "workable": "中", "needs effort": "需磨合"}


@lru_cache(maxsize=1)
def _ref() -> dict:
    try:
        return json.loads(REF_PATH.read_text("utf8"))
    except (OSError, ValueError):
        return {}


def reference_version() -> str | None:
    return _ref().get("version")


@lru_cache(maxsize=1)
def _cum() -> tuple[int, tuple[tuple[int, int, int], ...]] | None:
    hist = _ref().get("scores")
    if not hist:
        return None
    rows, below = [], 0
    for s in sorted(int(k) for k in hist):
        n = int(hist[str(s)])
        rows.append((s, below, n))
        below += n
    return below, tuple(rows)


def percentile(score: int) -> int | None:
    """Standing of `score` among the reference pairs, 0 to 100 (mid-rank); None if there is no reference file."""
    c = _cum()
    if c is None:
        return None
    total, rows = c
    below = equal = 0
    for s, b, n in rows:
        if s < score:
            below = b + n
        elif s == score:
            below, equal = b, n
            break
        else:
            break
    return max(0, min(100, round(100 * (below + equal / 2) / total)))


def _word_for_percentile(p: int) -> str:
    return "very compatible" if p >= CUT_VERY else "compatible" if p >= CUT_COMPAT else "workable" if p >= CUT_WORKABLE else "needs effort"


def band_word(score: int) -> str:
    """The English band word for a pair score: from the reference percentile, or from the fixed cut-offs when no reference is loaded."""
    p = percentile(score)
    if p is None:
        lo, mid, hi = FALLBACK_CUTS
        return "very compatible" if score >= hi else "compatible" if score >= mid else "workable" if score >= lo else "needs effort"
    return _word_for_percentile(p)


def band_label(score: int) -> str:
    """The engine's band string, English word and classical grade: "compatible 中上"."""
    w = band_word(score)
    return f"{w} {ZH[w]}"


@lru_cache(maxsize=1)
def cuts() -> tuple[int, int, int]:
    """The lowest raw score that reads "workable", "compatible" and "very compatible" (the gauge zones and the legend). From the reference
    when it is loaded; the fixed cut-offs otherwise. Bands are monotone in the score, so these three numbers describe them completely."""
    if _cum() is None:
        return FALLBACK_CUTS
    found = {}
    for s in range(5, 96):
        found.setdefault(band_word(s), s)
    return (found.get("workable", FALLBACK_CUTS[0]), found.get("compatible", FALLBACK_CUTS[1]), found.get("very compatible", FALLBACK_CUTS[2]))


def standing(score: int) -> dict:
    """Everything the page needs to show where a pair stands. `percentile` is None, and `higher_than` too, without a reference file."""
    p = percentile(score)
    return {"percentile": p, "higher_than": p, "of": 100, "reference_version": reference_version(),
            "word": band_word(score), "cuts": list(cuts()), "from_reference": p is not None}
