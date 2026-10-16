"""No money advice under 18 (owner 2026-10-10), applied to the reading payload.

engine/story.py already holds the rule for the story ("no money advice under 18") and exposes the one test for it, is_minor. The full report
and the strategy block ask the same test. This module is the last place the reading page was still telling a child or a teenager about money:
the opening report, the This year card, the narrative section on life domains, the life-domain table, and the strategy lines for handling a child's ten gods.

It is applied by the public chart route after chart_payload has built the whole payload, the same way attach_standing is, so chart_payload's own
output (and every pinned payload hash) is byte for byte what it was. It changes what is shown, never a score: the wealth area keeps its number
in the engine and is simply not part of a minor's reading.

What stays, on purpose: the names and one-line meanings of the ten gods (Direct Wealth, Rob Wealth ...) and of the five groups they fall into,
because they name the structure of the chart rather than advise on money; career fields; room and direction advice.
"""
from __future__ import annotations

from .story import is_minor

# the strategy line for a child's ten gods that is about money: dropped whole (the line is the money advice), or cut to its first clause
HANDLE_DROP = ("正財", "偏財")
HANDLE_FIRST_CLAUSE = ("劫財",)
# "the big asks: raises, launches, moves, proposals" in the years advice: the pay raise comes out of the list, the rest of the sentence stays
MONEY_STARS = ("祿神", "禄神")          # "Salary star: innate earning capacity", a money outlook with no advice in it, left out of a minor's stars
RAISE = {"en": "raises, ", "zh": "加薪、"}


def payload_year(p: dict) -> int | None:
    return (p.get("afflictions") or {}).get("year") or (((p.get("windows") or {}).get("years") or [{}])[0].get("y"))


def withhold_money(p: dict, c, ys: dict, year: int, lang: str = "en") -> dict:
    """The payload for a reader under 18 with the money out of it; an adult's payload is returned untouched."""
    if not is_minor(p["effective_time"], year):
        return p
    from scripts.bazi_report import GOD_HANDLE
    from .i18n import L
    from .interpret import interpret_person
    from .synthesis import clinical_report

    p = dict(p)
    p["minor"] = True                                       # the reading script drops the one money clause it holds itself (the 五鬼 line)
    p["domains"] = [d for d in p["domains"] if d["key"] != "wealth"]
    from .area_rank import ranking_summary
    from .story import payload_voice
    p["ranking"] = ranking_summary(p["domains"], payload_voice(p))     # the table order loses wealth; the strongest and weakest are the same two areas
    p["shensha"] = [x for x in p["shensha"] if x["star"] not in MONEY_STARS]
    p["interpretation"] = interpret_person(c, ys, year, lang=lang, minor=True)
    p["synthesis"] = clinical_report(p, lang=lang, minor=True)
    st = dict(p["strategy"])
    s10 = dict(st["s10"])
    table = L("bazi_report.GOD_HANDLE", GOD_HANDLE, lang)
    by_text = {table[g]: g for g in table}
    handle = []
    for line in s10["handle"]:
        god = by_text.get(line)
        if god in HANDLE_DROP:
            continue
        if god in HANDLE_FIRST_CLAUSE:
            line = line.replace("；", ";").split(";")[0].strip()
        handle.append(line)
    s10["handle"] = handle
    st["s10"] = s10
    if st.get("s13"):
        s13 = dict(st["s13"])
        s13["advice"] = [a.replace(RAISE[lang], "") for a in s13["advice"]]
        st["s13"] = s13
    p["strategy"] = st
    from .plain import _next_ten, _year
    from .story import compose_story
    plain = dict(p["plain"])                               # keeps what attach_standing added to it
    plain["money"] = None                                  # the wealth-store card: a minor has no wealth area, and the page never draws it
    plain["year"] = _year(p, lang, minor=True)            # "A window for money and relationships" on the This year card
    plain["next_ten"] = _next_ten(p, lang, minor=True)
    p["plain"] = plain
    p["story"] = compose_story(p, plain, lang)             # the story names stars from the same list
    return p
