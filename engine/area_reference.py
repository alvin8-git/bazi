"""Layer 2 of the life-area scores: the comparison figure.

The classical score (engine/domains.py) is an absolute reading of one chart. This module adds a second, separate number: the
percentile of that score inside a frozen reference sample of fictional charts (data/area_reference_v1.json, built once by
scripts/build_area_reference.py and pinned by a checksum test). It says where a score stands among charts, not how strong the
area is. The raw score and its band word never read it.

The file stores, per area, a histogram {score: count}. The percentile is the mid-rank share: charts scoring below plus half of
those scoring equal, as a whole number from 0 to 100.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

REF_PATH = Path(__file__).resolve().parent.parent / "data" / "area_reference_v1.json"
ENGINE_VERSION = "life-areas-v2"   # the scoring rules the reference was built against; changing a chip means a new version, not a regeneration


@lru_cache(maxsize=1)
def _ref() -> dict:
    try:
        return json.loads(REF_PATH.read_text("utf8"))
    except (OSError, ValueError):
        return {}


def reference_version() -> str | None:
    return _ref().get("version")


@lru_cache(maxsize=None)
def _cum(area: str) -> tuple[int, tuple[tuple[int, int, int], ...]] | None:
    hist = (_ref().get("areas") or {}).get(area)
    if not hist:
        return None
    rows, below = [], 0
    for s in sorted(int(k) for k in hist):
        n = int(hist[str(s)])
        rows.append((s, below, n))
        below += n
    return below, tuple(rows)


def percentile(area: str, score: int) -> int | None:
    """Standing of `score` in the reference sample for `area`, 0 to 100; None if there is no reference file."""
    c = _cum(area)
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


def standing_key(d: dict) -> tuple:
    """Sort key for comparing life areas: percentile first (the fair comparison across areas), the raw score to break ties.
    Falls back to the score alone for a domain dict that carries no percentile."""
    p = d.get("percentile")
    return (p if p is not None else d["score"], d["score"])
