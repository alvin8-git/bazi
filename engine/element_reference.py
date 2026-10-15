"""Where one element's share stands among charts: the comparison figure behind the quiet line on the balance panel.

The share and its band word (engine/domains.py health_map, engine/plain.py _balance) are absolute readings of one chart, and nothing
here changes them. This module adds a second, separate figure: the standing of that share inside a frozen reference sample of
fictional charts (data/element_reference_v2.json, built once by scripts/build_element_reference.py and pinned by a checksum test).
The score path never reads it: only attach_standing, called by the public chart route after chart_payload has built the whole payload,
adds a standing to each balance row, so chart_payload's own output (and every pinned payload hash) is byte for byte what it was.

Why it exists: earth is structurally heavier than the other four elements (four of the twelve branches are earth), so a fixed
band cut treats a chart with 32% earth, which is only the 72nd percentile, as harshly as 32% wood, which is the 87th.

The file stores, per element, a histogram {tenths of a percent: count}. The standing is the mid-rank share, as a whole number 0 to 100.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

REF_PATH = Path(__file__).resolve().parent.parent / "data" / "element_reference_v2.json"     # element_reference_v1.json (seed 20261015) stays untouched as the record
ENGINE_VERSION = "element-share-v2"   # v2 (2026-10-15): same share formula; the 節 moment now sets year and month pillars, so the sample was redrawn (seed 20261063). v1 was the share formula the reference was built against; a change means a new version, not a regeneration

# The contradiction rule (owner 2026-10-14: show the comparison only where it contradicts the band word).
# A band word points to a side: "too much" says the share is high, "too little" and "a little thin" say it is low, "about right" says
# it is neither. The standing places the same share in the top fifth (HIGH_TAIL or above), the bottom fifth (LOW_TAIL or below) or
# the middle. The line is shown exactly when the band word and the standing disagree:
#   too much                      yet standing below HIGH_TAIL  (flagged, but not unusual among charts)
#   too little / a little thin    yet standing above LOW_TAIL   (flagged, but not unusual among charts)
#   about right                   yet standing at or above HIGH_TAIL, or at or below LOW_TAIL  (called fine, but extreme among charts)
HIGH_TAIL = 80
LOW_TAIL = 20


@lru_cache(maxsize=1)
def _ref() -> dict:
    try:
        return json.loads(REF_PATH.read_text("utf8"))
    except (OSError, ValueError):
        return {}


def reference_version() -> str | None:
    return _ref().get("version")


@lru_cache(maxsize=None)
def _cum(el: str) -> tuple[int, tuple[tuple[int, int, int], ...]] | None:
    hist = (_ref().get("elements") or {}).get(el)
    if not hist:
        return None
    rows, below = [], 0
    for s in sorted(int(k) for k in hist):
        n = int(hist[str(s)])
        rows.append((s, below, n))
        below += n
    return below, tuple(rows)


def percentile(el: str, share: float) -> int | None:
    """Standing of `share` (a percentage, one decimal, as the page prints it) in the reference for `el`, 0 to 100; None without a reference."""
    c = _cum(el)
    if c is None:
        return None
    total, rows = c
    key = round(share * 10)
    below = equal = 0
    for s, b, n in rows:
        if s < key:
            below = b + n
        elif s == key:
            below, equal = b, n
            break
        else:
            break
    return max(0, min(100, round(100 * (below + equal / 2) / total)))


def contradicts(band: str, pct: int) -> bool:
    """True when the band word and the standing disagree (rule above). `band` is the English band word, never the reader-facing label."""
    if band == "too much":
        return pct < HIGH_TAIL
    if band in ("too little", "a little thin"):
        return pct > LOW_TAIL
    if band == "about right":
        return pct >= HIGH_TAIL or pct <= LOW_TAIL
    return False


def standing(el: str, share: float, band: str) -> dict | None:
    """The additive payload for one balance row: {pct, side, n, contradicts}. `n` is the whole number the sentence prints, held to 1..99
    so no line ever says 'heavier than 100 in 100' or 'lighter than 0 in 100'."""
    p = percentile(el, share)
    if p is None:
        return None
    heavier = p >= 50
    return {"pct": p, "side": "heavier" if heavier else "lighter", "n": max(1, min(99, p if heavier else 100 - p)),
            "contradicts": contradicts(band, p)}


def attach_standing(payload: dict) -> dict:
    """Additive, in place: give each plain.balance row a `standing` and name the reference version. Reads only the share and the band word the
    payload already carries; changes neither. Returns the same payload so a route can wrap its return value."""
    plain = payload.get("plain") or {}
    for r in plain.get("balance") or []:
        r["standing"] = standing(r["el"], r["share"], r.get("band_key") or r["band"])
    if plain.get("balance"):
        plain["element_reference_version"] = reference_version()
    return payload
