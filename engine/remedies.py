"""PRESCRIBE layer — cited findings → concrete actions (design doc §4).

Deterministic rule tables, no LLM. Single source of ALL remedy text (7A):
interpret.py narratives render these actions, never their own copies.

RemedyAction = {trigger, action, category, priority, source_ref, resource}
  priority: 1 annual-star safety > 2 八宅 personal > 3 用神/element > 4 activation
  resource: the physical thing the action occupies (T1-A arbitration — at most
  one winning action per resource per card; losers go to the audit tagged
  "superseded by <winner>").
"""
from __future__ import annotations

from .bazhai import STAR_SCORE, youxing_stars
from .liunian import BRANCH_PALACE, annual_afflictions
from .shensha import TRINE_STARS, WENCHANG
from .wuxing import ELEMENT_COLOURS, ELEMENT_EN, ELEMENTS, PALACES, SHENG, SHENG_REV

# 五行 materials map (design doc §4 R1)
MATERIALS = {
    "木": "plants, wood furniture", "火": "lights, red textiles",
    "土": "ceramics, stone, earth tones", "金": "metal decor, white",
    "水": "water feature, glass, black-blue",
}

# 紫白 annual-star remedy table (design doc §4 R2)
ANNUAL_STAR_RULES = {
    5: ("五黃 most afflictive", "place metal here (brass, six-coin, metal pendulum "
        "clock); avoid red/fire decor; no drilling or renovation in this sector", 1),
    2: ("二黑 illness star", "place metal here (brass or a metal pendulum clock); "
        "avoid red/fire decor; keep this sector quiet", 1),
    3: ("三碧 conflict star", "add red/fire tones here — Fire drains the quarrelsome "
        "Wood star", 2),
    7: ("七赤 robbery star", "add water colours (black/blue) here to drain it; avoid "
        "clutter of metal objects", 2),
}
AUSPICIOUS_STARS = (8, 9, 1, 4)

_RESOURCE_ORDER = ["headboard", "desk", "room_colour", "zone_object", "schedule",
                   "wardrobe"]


def _act(trigger, action, category, priority, source_ref, resource):
    return {"trigger": trigger, "action": action, "category": category,
            "priority": priority, "source_ref": source_ref, "resource": resource}


def good_dirs(gua: str, top: int = 3) -> str:
    """Best 八宅 directions for a 命卦, strongest star first (7A: shared by
    interpret.py so remedy text and narrative name the same directions)."""
    good = sorted(((p, st) for p, st in youxing_stars(gua).items() if STAR_SCORE[st] > 0),
                  key=lambda x: -STAR_SCORE[x[1]])
    return ", ".join(f"{PALACES[p]['dir']} ({st})" for p, st in good[:top])


# ---------- R1 · element imbalance (person) ---------------------------------

def element_remedies(chart, ys) -> list[dict]:
    """Excess → 洩 drain via the element it generates; deficient → supplement +
    mother (生). Controlling (剋) offered as secondary, labelled harsher."""
    w = chart.element_weights
    total = sum(w.values()) or 1
    out = []
    for e in ELEMENTS:
        share = w[e] / total
        if share >= 0.30:
            drain = SHENG[e]
            out.append(_act(
                f"{e} excess {share:.0%} — element_weights",
                f"favour {ELEMENT_EN[drain]}{drain} to drain the excess: colours "
                f"{'·'.join(ELEMENT_COLOURS[drain])}, {MATERIALS[drain]} "
                f"(洩 drain preferred; controlling it with "
                f"{ELEMENT_EN[_ke_of(e)]}{_ke_of(e)} is harsher — secondary)",
                "colour", 3, "五行生剋 — 洩法 drain preferred over 剋", "wardrobe"))
        elif share <= 0.07:
            mother = SHENG_REV[e]
            out.append(_act(
                f"{e} deficient {share:.0%} — element_weights",
                f"supplement {ELEMENT_EN[e]}{e} directly (colours "
                f"{'·'.join(ELEMENT_COLOURS[e])}, {MATERIALS[e]}) plus its mother "
                f"{ELEMENT_EN[mother]}{mother} ({MATERIALS[mother]}) — {mother}生{e}",
                "colour", 3, "五行相生 — supplement + mother", "wardrobe"))
    return out


def _ke_of(e: str) -> str:
    from .wuxing import KE
    return next(x for x in ELEMENTS if KE[x] == e)


# ---------- 7A shared phrases (single source of remedy text) ----------------

def bazhai_compensation(gua: str, ys) -> dict:
    """The in-room compensation for a person poorly placed — the exact phrase
    interpret_house renders (wording-parity guarded)."""
    return _act(
        f"negative room fit — 八宅 {gua}命 mismatch",
        f"point headboard/desk toward {good_dirs(gua)}; decorate with 用神 colours "
        f"{'·'.join(ys['colours'])}",
        "placement", 2, "八宅遊年 + 用神 (in-room compensation)", "headboard")


def wardrobe_phrase(ys) -> str:
    """The 用神 colour/decor sentence fragment interpret_person embeds (7A)."""
    return (f"wear/decorate with the colours {'·'.join(ys['colours'])} and favour "
            f"room sectors of those elements; keep {'·'.join(ys['unfavourable'])} "
            f"understated in decor and wardrobe")


# ---------- R2 · room fit (person × room) -----------------------------------

def room_remedies(chart, ys, gua: str, palace: str, natal: dict,
                  annual: dict[str, int], year: int) -> dict:
    """Actions for one person's assigned room + 3A conflict resolution:
    annual-star safety beats person-用神 within the room for the current year.
    Returns {"actions": [...], "deferred": [...]}."""
    actions, deferred = [], []
    if palace and palace != "中":
        star = youxing_stars(gua)[palace]
        if STAR_SCORE[star] < 0:
            actions.append(_act(
                f"bedroom sits on your {star} direction — 八宅 {gua}命",
                f"point headboard/desk toward {good_dirs(gua)}",
                "direction", 2, f"八宅遊年 — {star} compensation", "headboard"))
        personal_colour = _act(
            f"用神 support in your own zone — {'·'.join(ys['favourable'][:2])}",
            f"use your 用神 colours {'·'.join(ys['colours'])} in your corner of the room",
            "colour", 3, "用神 — MODERN SYNTHESIS", "room_colour")

        astar = annual.get(palace)
        annual_rule = ANNUAL_STAR_RULES.get(astar)
        if annual_rule:
            label, action_txt, prio = annual_rule
            actions.append(_act(
                f"annual star {astar} ({label}) in your room's palace {palace}, {year}",
                action_txt, "material", prio,
                f"紫白訣 annual-star remedy, {year}", "room_colour"))
            fire_colours = set(ELEMENT_COLOURS["火"])
            if astar in (5, 2) and fire_colours & set(ys["colours"]):
                deferred.append({**personal_colour,
                                 "deferred": f"resumes 立春 {year + 1} (≈4 Feb) — "
                                             f"annual {label} forbids red/fire in this "
                                             "room this year (3A precedence)"})
            else:
                actions.append(personal_colour)
        else:
            actions.append(personal_colour)
            if astar in AUSPICIOUS_STARS:
                actions.append(_act(
                    f"auspicious annual star {astar} visits palace {palace}, {year}",
                    "activate it: keep this room bright, used and lively this year",
                    "habit", 4, f"紫白訣 — activate 吉星, {year}", "zone_object"))
    return {"actions": actions, "deferred": deferred}


# ---------- R3 · star placement gaps (home) ---------------------------------

def home_remedies(natal: dict, palace_rooms: dict[str, list[dict]]) -> list[dict]:
    """向星/山星 of the period without matching room use → activation cards."""
    period = natal["period"]
    out = []
    for palace, stars in natal["palaces"].items():
        if palace == "中":
            continue
        rooms = palace_rooms.get(palace, [])
        labels = "、".join(r["label"] for r in rooms) or "no traced room"
        d = PALACES[palace]["dir"]
        if stars["water"] == period:
            active = any(not r["sleeping"] for r in rooms)
            if not active:
                out.append(_act(
                    f"prosperous water star {period} in {d} ({palace}宮) — {labels}",
                    f"keep the {d} zone bright and lively; a moving object or water "
                    "feature here activates the wealth star",
                    "placement", 4, "玄空 — 向星要動 (water star wants activity)",
                    f"zone_object:{palace}"))
        if stars["mountain"] == period:
            has_bed = any(r["sleeping"] for r in rooms)
            if not has_bed:
                out.append(_act(
                    f"prosperous mountain star {period} in {d} ({palace}宮) — {labels}",
                    f"use heavy furniture / solid wall in the {d} zone and keep it "
                    "still — the people/health star wants stillness",
                    "placement", 4, "玄空 — 山星要靜 (mountain star wants stillness)",
                    f"zone_object:{palace}"))
    return out


# ---------- R4 · timing (year) ----------------------------------------------

def timing_remedies(year: int, annual: dict[str, int],
                    palace_rooms: dict[str, list[dict]]) -> list[dict]:
    """Afflicted sectors → no-disturbance windows with an end date."""
    out = []
    af = annual_afflictions(year)
    afflicted = {af["taisui"]["palace"]: "太歲", af["suipo"]["palace"]: "歲破"}
    for p in af["sansha"]["palaces"]:
        afflicted.setdefault(p, "三煞")
    for p, s in annual.items():
        if s in (5, 2) and p != "中":
            afflicted.setdefault(p, "五黃" if s == 5 else "二黑")
    for palace, label in afflicted.items():
        rooms = palace_rooms.get(palace, [])
        if not rooms:
            continue
        names = "、".join(r["label"] for r in rooms)
        out.append(_act(
            f"{label} occupies {PALACES[palace]['dir']} ({palace}宮) in {year}",
            f"no drilling, hacking or renovation in {names} until 立春 {year + 1} "
            "(≈4 Feb); fine to occupy quietly",
            "timing", 1, f"流年神煞 {label}, {year}", f"schedule:{palace}"))
    return out


# ---------- R5 · study alignment (person) -----------------------------------

def wenchang_palace(chart) -> str | None:
    """Personal 文昌 palace from the day stem (文昌貴人 branch → palace)."""
    b = WENCHANG.get(chart.day_master)
    return BRANCH_PALACE.get(b) if b else None


def taohua_palace(chart) -> str | None:
    """桃花位 from the day-branch trine."""
    db = chart.pillars["day"].branch
    grp = next(g for g in TRINE_STARS if db in g)
    return BRANCH_PALACE.get(TRINE_STARS[grp]["桃花"])


def study_remedies(chart, room_palace: str | None,
                   palace_rooms: dict[str, list[dict]]) -> list[dict]:
    wc = wenchang_palace(chart)
    if wc is None:
        return []
    d = PALACES[wc]["dir"]
    if room_palace == wc:
        action = (f"your own room IS your 文昌 sector ({d}) — put the desk here and "
                  f"face {d} while studying")
    elif palace_rooms.get(wc):
        labels = "、".join(r["label"] for r in palace_rooms[wc])
        action = (f"relocate the desk to your 文昌 sector: {labels} ({d}); otherwise "
                  f"face {d} at your current desk")
    else:
        action = f"no traced room sits in your 文昌 sector — face {d} at your desk"
    return [_act(f"personal 文昌 (day stem {chart.day_master}) sits in {d} ({wc}宮)",
                 action, "direction", 2, "文昌貴人 — study star placement", "desk")]


# ---------- R6 · relationship (pair/couple) ---------------------------------

def pair_remedies(chart_a, chart_b, palace_rooms: dict[str, list[dict]],
                  shared_room: bool = True) -> list[dict]:
    """Actions for a pair: clash management, bond activation, 桃花位 use."""
    from .hehun import _branch_rel
    ba, bb = chart_a.pillars["day"].branch, chart_b.pillars["day"].branch
    rel = _branch_rel(ba, bb)
    out = []
    if rel and rel[1] < 0:
        kind = rel[0]
        trigger = f"day branches {ba}{bb} {kind} — spouse palaces clash"
        out.append(_act(trigger, "keep separate work/desk corners — don't share one "
                        "desk or face each other while working",
                        "placement", 2, f"合婚 {kind} management", "desk"))
        if shared_room:
            out.append(_act(trigger, "calmer decor in the shared bedroom: soft "
                            "colours, no mirrors facing the bed, low clutter",
                            "colour", 3, f"合婚 {kind} management", "room_colour"))
        out.append(_act(trigger, f"pick dates for big joint decisions that clash "
                        f"neither day branch ({ba} nor {bb}) — the Dates tab "
                        "filters these", "timing", 3, f"合婚 {kind} management",
                        "schedule:pair"))
    elif rel and rel[1] > 0:
        out.append(_act(f"day branches {ba}{bb} {rel[0]} — spouse palaces bond",
                        "a natural team — take big decisions and sign papers "
                        "together rather than separately",
                        "habit", 4, f"合婚 {rel[0]} activation", "zone_object"))
    th = taohua_palace(chart_a)
    if th and palace_rooms.get(th):
        labels = "、".join(r["label"] for r in palace_rooms[th])
        out.append(_act(f"桃花位 ({PALACES[th]['dir']} {th}宮) holds {labels}",
                        f"use {labels} together regularly — shared meals, evening "
                        "time — to keep the bond's palace active",
                        "habit", 4, "桃花位 activation", f"zone_object:{th}"))
    return out


# ---------- T1-A · resource arbitration -------------------------------------

def arbitrate(actions: list[dict]) -> tuple[list[dict], list[dict]]:
    """One winning action per physical resource (priority asc wins; earlier
    emission breaks ties). Losers returned tagged for the audit."""
    winners: dict[str, dict] = {}
    superseded = []
    for a in actions:
        r = a["resource"]
        cur = winners.get(r)
        if cur is None:
            winners[r] = a
        elif a["priority"] < cur["priority"]:
            superseded.append({**cur, "superseded_by": a["trigger"]})
            winners[r] = a
        else:
            superseded.append({**a, "superseded_by": cur["trigger"]})
    def _rank(a):
        base = a["resource"].split(":")[0]    # schedule:坎 → schedule
        idx = _RESOURCE_ORDER.index(base) if base in _RESOURCE_ORDER else len(_RESOURCE_ORDER)
        return (a["priority"], idx)
    return sorted(winners.values(), key=_rank), superseded
