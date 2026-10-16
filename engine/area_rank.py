"""The one ranking of the life areas (round 52, owner decision 2026-10-16: band first, then percentile).

Every sentence, card or line that names a strongest, weakest, highest, lowest or "most in need" life area calls `rank_areas` here:
the character card (public.py _card), the story (engine/story.py _drives and its priority line), the interpretation section 8
(engine/interpret.py), the clinical plan's lowest-area line (engine/synthesis.py), and the reading page's "highest" line and the
order of its life-area table (web/app.js, which reads the `ranking` the payload carries, never its own sort). The Chinese text is
the same call with lang="zh": it changes the words, never the pick.

The order, strongest first:
  1. band word: prominent above balanced above needs support. The word is the one the area already shows (engine/domains.py, from
     band_word: percentile cuts 75 / 25, for all six areas since D2, 2026-10-16), read, never recomputed, so no band cut moves.
  2. percentile inside a band (the standing among charts); with no reference file, the score stands in for it.
  3. the raw score.
  4. a fixed area order (AREA_ORDER), so two areas that tie on all three still come out the same way every time: the earlier
     area in AREA_ORDER ranks higher, which also makes the later one the weakest of an exact tie.
Why band first: until D2 (2026-10-16) learning's word came from fixed cut-offs and every other area's from its percentile, so a percentile-only ranking
called a "prominent" learning score (73, percentile 15) the weakest area. Every word now reads the percentile, so a word and a percentile can no longer
disagree; the ranking still reads the word it is given. A band is the page's own claim about an area; the ranking may not contradict it.

Who is ranked (AREAS_FOR), decided once, the story's age-voice set, for every surface:
  child  learning, health                   no money advice under 18 (owner 2026-10-10), and a child's reading does not weigh love,
  teen   learning, health, career           stability or work; a teen's reading adds study habits (the career area)
  adult  all six
  senior stability, wealth, learning, health   attraction and career are not a senior's reading
Before this round the story and the card used this set while the interpretation and the clinical plan removed only wealth for a minor, and
the reading page's table line removed nothing but wealth, so the sections named different areas for the same person.

If every ranked area shares one band the words "strongest" and "weakest" would claim a difference the page does not show, so
`same_band` is true and the callers say "the areas weighed here all read <band>; the highest standing is ..." instead ("weighed here" because a child's or
senior's reading weighs fewer than six areas, so "all your areas" would be untrue). In that case the highest and
lowest are still named, by the same order.
"""
from __future__ import annotations

from .area_reference import standing_key  # noqa: F401  (kept importable from here for the old callers' sake)

AREA_ORDER = ("attraction", "stability", "career", "wealth", "learning", "health")   # the order the engine scores them in
AREAS_FOR = {"child": {"learning", "health"}, "teen": {"learning", "health", "career"},
             "adult": {"attraction", "stability", "career", "wealth", "learning", "health"},
             "senior": {"stability", "wealth", "learning", "health"}}
BAND_RANK = {"prominent": 2, "balanced": 1, "needs support": 0}
GAP_FOR_PRIORITY = 60       # the story's priority line fires when the strongest leads the weakest by this many percentile points (unchanged)


def band_of(d: dict) -> str:
    """The English band word of a domain dict ("prominent 强" and "prominent" both give "prominent")."""
    return " ".join(w for w in str(d.get("band", "")).split() if w.isascii())


def rank_key(d: dict) -> tuple:
    """Sort key, larger is stronger: band, percentile (score when there is none), score, earlier area first."""
    p = d.get("percentile")
    k = d.get("key")
    return (BAND_RANK.get(band_of(d), 1), p if p is not None else d["score"], d["score"],
            -(AREA_ORDER.index(k) if k in AREA_ORDER else len(AREA_ORDER)))


def rank_all(domains: list[dict]) -> list[dict]:
    """Every given domain in rank order, strongest first (the order of the reading page's life-area table)."""
    return sorted(domains, key=rank_key, reverse=True)


def rank_areas(domains: list[dict], voice: str = "adult") -> dict:
    """The one answer to "which life area is strongest, weakest, highest, lowest, most in need".

    domains: the payload's domain dicts (key, score, band, percentile). voice: child / teen / adult / senior (AREAS_FOR).
    Returns {"voice", "ordered" (the ranked areas of this voice, strongest first), "strongest", "weakest" (None with fewer than two areas),
    "same_band" (every ranked area has one band word), "band" (that word, else None), "gap" (strongest minus weakest percentile, or score)}."""
    allowed = AREAS_FOR.get(voice, AREAS_FOR["adult"])
    ordered = rank_all([d for d in domains if d.get("key") in allowed])
    top = ordered[0] if ordered else None
    low = ordered[-1] if len(ordered) > 1 else None
    bands = {band_of(d) for d in ordered}
    same = len(ordered) > 1 and len(bands) == 1
    pv = lambda d: d["percentile"] if d.get("percentile") is not None else d["score"]
    return {"voice": voice, "ordered": ordered, "strongest": top, "weakest": low, "same_band": same,
            "band": next(iter(bands)) if same else None, "gap": (pv(top) - pv(low)) if low else 0}


def ranking_summary(domains: list[dict], voice: str = "adult") -> dict:
    """The JSON the payload carries for the reading page: keys only, so the page never sorts or picks by itself.
    `order` is every shown area in rank order; `strongest` and `weakest` are the picks of this voice."""
    r = rank_areas(domains, voice)
    return {"voice": voice, "order": [d["key"] for d in rank_all(domains)],
            "strongest": r["strongest"]["key"] if r["strongest"] else None,
            "weakest": r["weakest"]["key"] if r["weakest"] else None,
            "same_band": r["same_band"], "band": r["band"]}
