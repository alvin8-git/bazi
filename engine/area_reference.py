"""Layer 2 of the life-area scores: the comparison figure.

The classical score (engine/domains.py) is an absolute reading of one chart. This module adds a second, separate number: the
percentile of that score inside a frozen reference sample of fictional charts (data/area_reference_v3.json, built once by
scripts/build_area_reference.py and pinned by a checksum test). It says where a score stands among charts, not how strong the
area is. The raw score never reads it. Since round 45 (A3, 2026-10-15) the band WORD does: see `band_word` below.

The file stores, per area, a histogram {score: count}. The percentile is the mid-rank share: charts scoring below plus half of
those scoring equal, as a whole number from 0 to 100.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

# History (never overwrite, a rule change means a new reference):
#   area_reference_v1.json  built against life-areas-v2 (seed 20261011), kept untouched as the historical record. Nothing reads it any more.
#   area_reference_v2.json  built against life-areas-v3 (seed 20261043), 2026-10-15: the stability "single clear spouse star" cut at 8%,
#                           拱合 no longer counted as a combined spouse palace, and 六害 on its own at -2 instead of -5.
#   area_reference_v3.json  built against life-areas-v4 (seed 20261044), 2026-10-15: the duplicate strong-or-weak chips are gone from career and
#                           wealth (round 45, A1), so those two areas have new score distributions and the band word now reads the percentile.
#                           area_reference_v2.json stays untouched as the record of life-areas-v3; nothing reads it any more.
REF_V1_PATH = Path(__file__).resolve().parent.parent / "data" / "area_reference_v1.json"
REF_V2_PATH = Path(__file__).resolve().parent.parent / "data" / "area_reference_v2.json"
REF_PATH = Path(__file__).resolve().parent.parent / "data" / "area_reference_v3.json"
ENGINE_VERSION = "life-areas-v4"   # the scoring rules the reference was built against; changing a chip means a new version, not a regeneration

# Band words from percentiles (round 45, A3, owner-approved 2026-10-15). The top quarter of the reference reads "prominent", the bottom
# quarter "needs support", the middle half "balanced": equal chances of strength and weakness, whatever the area's raw scale. The cut
# is on the whole-number mid-rank percentile (>= 75 and <= 25), so a score's word depends only on where it stands, never on the score.
BAND_HIGH, BAND_LOW = 75, 25
# ONE stated exception (owner, 2026-10-15): learning keeps the fixed cut-offs (70 prominent, 45 balanced, under 45 needs support). 35.7% of charts sit on
# learning's cap of 95, so a percentile word would read a score of 75 (which most charts beat) as "needs support" and 36% of charts as "prominent". The percentile
# itself is still computed and shown for learning; only its word comes from the fixed cut-offs. To be revisited if learning's chips are ever recalibrated.
FIXED_CUTOFF_AREAS = frozenset({"learning"})


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


def band_word(area: str, score: int) -> tuple[str, bool]:
    """(band word, from_reference). Learning is the one exception: its word always comes from the fixed 70 / 45 cut-offs (FIXED_CUTOFF_AREAS).
    For every other area the word comes from the percentile: >= 75 prominent, <= 25 needs support, else balanced. With no
    reference loaded (file missing or unreadable) it falls back to the fixed cut-offs the engine used before A3 (70 and 45), so a reading
    never shows without a word."""
    if area in FIXED_CUTOFF_AREAS:
        return ("prominent" if score >= 70 else "balanced" if score >= 45 else "needs support"), False
    p = percentile(area, score)
    if p is None:
        return ("prominent" if score >= 70 else "balanced" if score >= 45 else "needs support"), False
    return ("prominent" if p >= BAND_HIGH else "needs support" if p <= BAND_LOW else "balanced"), True


def standing_key(d: dict) -> tuple:
    """Sort key for comparing life areas: percentile first (the fair comparison across areas), the raw score to break ties.
    Falls back to the score alone for a domain dict that carries no percentile."""
    p = d.get("percentile")
    return (p if p is not None else d["score"], d["score"])
