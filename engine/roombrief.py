"""Per-room brief (P1 of docs/designs/home-fengshui-deterministic-v2.md).

For one traced room: the palace's element brief (colours to use / avoid, with
scope), the materials and objects that offset its stars, each occupant's
personal palette with the precedence rule applied, and a 二五 severity that
ranks two afflicted palaces by the palace's 運星 element.

Every string is a template over the inputs. Nothing here needs a photograph.
Rules are numbered as in the design doc (A1–A5, B1–B7, §2).
"""
from __future__ import annotations

from .wuxing import EARTH, ELEMENT_COLOURS, FIRE, METAL, STAR_ELEMENT, WATER, WOOD

ZH = {WOOD: "木", FIRE: "火", EARTH: "土", METAL: "金", WATER: "水"}
# the element that DRAINS (洩) each element: X 生 drain(X)
DRAINS = {WOOD: FIRE, FIRE: EARTH, EARTH: METAL, METAL: WATER, WATER: WOOD}
# palette words shown to users (simplified)
PALETTE = {WOOD: "绿/青", FIRE: "红/橙/紫", EARTH: "黄/米/棕", METAL: "白/灰/金属色",
           WATER: "蓝/黑"}
OBJECT_OF = {  # one object-scale item per element for A3 compensation
    WOOD: "一株健康的小盆栽 one healthy potted plant",
    FIRE: "一盏暖光灯或红色小物 one warm lamp or small red object",
    EARTH: "一件陶瓷或石质小摆件 one ceramic or stone object",
    METAL: "一件铜或钢小件 one small brass or steel object",
    WATER: "一个加盖的小水器 one small covered water vessel",
}


def _item(what: str, scope: str, why: str, doctrine: str) -> dict:
    return {"what": what, "scope": scope, "why": why, "doctrine": doctrine}


def _obj(what: str, where: str, why: str, doctrine: str) -> dict:
    return {"what": what, "where": where, "why": why, "doctrine": doctrine}


def severity(mountain: int, water: int, run_star_element: str | None) -> int:
    """§2: 2/5 pair → 2, one of them → 1, else 0; 運星 火/土 feeds (+1), 金 drains (−1)."""
    s = {mountain, water}
    base = 2 if {2, 5} <= s else (1 if s & {2, 5} else 0)
    if base and run_star_element in (FIRE, EARTH):
        base += 1
    elif base and run_star_element == METAL:
        base -= 1
    return max(base, 0)


def room_brief(palace: str, stars: dict, period: int, occupants: list[dict],
               annual_star: int | None = None,
               run_star_element: str | None = None) -> dict:
    """stars = {mountain, water[, base]}; occupants = [{name, favourable[], unfavourable[]}]."""
    m, w = stars["mountain"], stars["water"]
    base = stars.get("base")                 # 運星 of the palace
    present = {m, w} | ({base} if base else set())
    timely = {period, period % 9 + 1}
    use: list[dict] = []
    avoid: list[dict] = []
    mats_use: list[dict] = []
    mats_avoid: list[dict] = []
    objects: list[dict] = []
    afflicted = False           # A1 fired a cure that overrides personal palettes
    cure_element: str | None = None
    notes: list[str] = []

    # ---- A1 palace brief -------------------------------------------------
    if m in (2, 5) or w in (2, 5):
        afflicted, cure_element = True, METAL
        pair = f"山{m}向{w}"
        use.append(_item(PALETTE[METAL], "planes",
                         f"{pair} 二五 earth affliction — metal drains it (金洩土)", "玄空·五行"))
        avoid.append(_item(f"{PALETTE[FIRE]} · {PALETTE[EARTH]}", "planes",
                           "fire feeds earth, earth adds to the pair (火生土)", "玄空·五行"))
        # B1 metal by material
        mats_use.append(_item("brushed brass / bronze pulls, legs and reveals; brushed stainless",
                              "objects", "the remedy is the METAL, not the colour", "玄空·五行 金洩土"))
        mats_avoid.append(_item("gold-coloured paint or laminate; polished or mirror brass at "
                                "surface scale; stone mass (travertine, slab); warm timber planes",
                                "planes", "no metal in gold paint; stone and timber feed the pair",
                                "玄空·五行"))
        objects.append(_obj("one brass object that MOVES or rings (clock, six-rod hollow chime)",
                            f"the {palace} corner of the room", "motion in metal drains 2/5",
                            "玄空 [modern convention]"))
        # B6 plants as 生氣
        objects.append(_obj("2–3 live round-leaved plants in zinc or steel pots",
                            "spread across the room, not a wall of them",
                            "a 二五 palace stagnates; living green is 生氣, not a 木剋土 cure",
                            "形勢 [modern convention]"))
        mats_avoid.append(_item("terracotta pots; red-leaved or spiky plants; green paint on a plane",
                                "planes", "earth pots and fire foliage feed the pair", "五行"))
        notes.append("二五 sector: stillness and quiet; no renovation, drilling or plumbing moves")
    if w == 3:
        afflicted, cure_element = True, FIRE
        use.append(_item(PALETTE[FIRE] + " (textiles, warm light)", "textiles",
                         "向星3 quarrel star — fire drains wood (木生火)", "玄空·五行"))
        avoid.append(_item(PALETTE[WOOD], "planes", "green planes and large plants feed the 3",
                           "玄空·五行"))
        objects.append(_obj("warm textiles and a warm 2700–3000K lamp; no speakers or noisy electronics",
                            "the whole room", "向星3 is the argument star — keep it acoustically calm",
                            "玄空 [modern convention]"))
    if 4 in (m, w):
        avoid.append(_item(PALETTE[METAL] + " and metal objects at scale", "planes",
                           "金剋木 — metal chops the 4綠 文昌 star", "玄空·五行"))
        if 7 in present:
            # B4 no metal where 7 (山, 向 or 運星) sits on wood
            mats_avoid.append(_item("metal frames, chrome lamps, metal fittings at scale",
                                    "objects", "7赤金 already chops 3碧/4綠; more metal sharpens 是非 "
                                    "and attacks 文昌", "玄空 七赤剋三四"))
            mats_use.append(_item("timber or laminate frames and fittings", "objects",
                                  "wood stays whole in this palace", "玄空"))
    if w in timely:
        use.append(_item("light, bright, open — pale planes", "planes",
                         f"向星{w} is timely — it works through light and activity", "玄空 向星要動"))
        avoid.append(_item("dark heavy planes; tall joinery on the window side", "planes",
                           "mass and darkness smother a timely water star", "玄空"))
        # A4 drain rule
        wel = STAR_ELEMENT[w]
        drain = DRAINS[wel]
        avoid.append(_item(PALETTE[drain], "planes",
                           f"{ZH[drain]} drains the timely 向星{w} ({ZH[wel]}生{ZH[drain]}洩{ZH[wel]}) — "
                           "keep it off walls and carcass, textiles are fine", "五行 生剋"))
    if m == 7 and w == 9:
        avoid.append(_item("strong 红/橙 blocks; sharp metal decor", "planes",
                           "七九合轍 — the classical fire-hazard pair", "玄空"))
        notes.append("七九: no candles, flame diffusers or heaters left plugged in; no extension-lead "
                     "chains behind the bed")
    if w == 7:
        notes.append("向星7 robbery star: secure the window, no valuables on display, no clutter of "
                     "metal objects")
    if m in timely:
        # B2 mass for the timely mountain star
        objects.append(_obj("full-height closed heavy joinery (bookcase or wardrobe), closed back",
                            f"the {palace} corner", f"山星{m} is timely — it acts through stillness and "
                            "solid mass; never an open shelf toward a pillow", "玄空 山星要靜"))
        mats_avoid.append(_item("open, wire or metal-framed shelving in that corner", "objects",
                                "light open units give the mountain star nothing to stand on", "玄空"))
        if not afflicted:
            # B7 earth welcome
            mats_use.append(_item("terracotta, stone, ceramic; heavy pots", "objects",
                                  "no affliction to drain — earth materials are welcome here; metal "
                                  "planters not needed", "五行"))
    if not use:
        use.append(_item("neutral — follow the occupant's 用神 palette", "planes",
                         f"山{m}向{w} sets no colour of its own", "玄空"))

    # ---- E1–E5 lighting, F3 timing ----------------------------------------
    erwu = m in (2, 5) or w in (2, 5)
    fire_people = [o["name"] for o in occupants if FIRE in (o.get("favourable") or [])]
    lnotes: list[dict] = []
    if erwu:
        fixed_k, lamps_k = "4000K", "2700–3000K switchable lamps only"
        lnotes.append({"code": "E1", "zh": "二五忌暖光", "text": "no amber cove, LED strip or "
                       "concealed warm backlight — a warm plane is 火生土 feeding the pair; warmth "
                       "lives in switchable lamps", "doctrine": "玄空·五行"})
    elif w == 3 or (fire_people and not afflicted):
        fixed_k = lamps_k = "2700–3000K"
        trig = "向星3 quarrel star — fire drains wood" if w == 3 else \
            f"{'、'.join(fire_people)}'s 用神 火"
        lnotes.append({"code": "E2", "zh": "暖光", "text": f"warm throughout: {trig}",
                       "doctrine": "玄空·五行" if w == 3 else "五行 用神"})
    elif m in timely:
        fixed_k, lamps_k = "3000K low output", "2700K lamps"
        lnotes.append({"code": "E3", "zh": "山星宜靜", "text": "low and warm, no bright "
                       "downlights — the people star acts through stillness",
                       "doctrine": "玄空 山星要靜"})
    else:
        fixed_k, lamps_k = "3000–3500K", "2700K lamps"
    lnotes.append({"code": "E4", "zh": "枕上无灯", "text": "no ceiling fitting directly above the "
                   "pillow — pendant or downlight sits over the foot or the circulation, bedside "
                   "lamps carry the head end", "doctrine": "形勢 [modern convention]",
                   "bedroom_only": True})
    if {7, 9} <= {m, w}:
        lnotes.append({"code": "E5", "zh": "七九忌火", "text": "no candles, flame diffusers or "
                       "heaters left plugged in; no extension-lead chains behind the bed",
                       "doctrine": "玄空 七九合轍"})
    lighting = {"fixed_k": fixed_k, "lamps_k": lamps_k, "notes": lnotes}
    timing_rules: list[dict] = []
    if erwu:
        timing_rules.append({"code": "F3", "zh": "二五不動", "text": "no renovation, drilling or "
                             "plumbing moves in this palace in any year — furniture-fit and finish "
                             "only", "doctrine": "玄空"})

    # ---- A2 / A3 occupants ----------------------------------------------
    occ_out = []
    for o in occupants:
        fav = list(o.get("favourable") or [])
        unf = list(o.get("unfavourable") or [])
        pal = [PALETTE[e] for e in fav if e in PALETTE]
        pal_avoid = [PALETTE[e] for e in unf if e in PALETTE]
        scope = "textiles" if afflicted else "planes"
        comp = []
        cost = None
        if fav:
            comp.append(_obj(OBJECT_OF.get(fav[0], ""), "at the bedside or seat — never a plane",
                             f"{ZH.get(fav[0], fav[0])} is the first 用神", "五行 用神 [modern convention]"))
        if cure_element and cure_element in unf:
            cost = (f"the palace cure is {ZH[cure_element]}, which is this occupant's 忌神 — the palace "
                    "outranks the person here; compensate at object scale only")
        # B5 water, small and covered
        if WATER in fav and not (m in (2, 5) or w in (2, 5)):
            objects.append(_obj("a small covered water vessel", f"{o['name']}'s side of the room",
                                "水 is a 用神 — small and covered, never open or moving in a bedroom",
                                "五行 用神"))
        if (m in (2, 5) or w in (2, 5)) and METAL in unf and WATER in fav:
            objects.append(_obj("the metal remedy IN water: a blackened-steel or pewter vessel holding "
                                "still, covered water", f"{o['name']}'s side",
                                "土生金，金生水 — the metal drains the pair and discharges into the "
                                "occupant's 用神 instead of fighting them", "五行 生剋"))
        occ_out.append({"name": o["name"], "palette_personal": pal,
                        "palette_avoid": pal_avoid, "palette_scope": scope,
                        "compensation": comp, "cost": cost})

    override_note = None
    if afflicted:
        override_note = ("palace cure outranks personal 用神 in this room: the cure stays on walls and "
                         "large surfaces, personal palettes move to bedding, curtains and objects")
    return {"palace": palace, "mountain": m, "water": w, "base": stars.get("base"),
            "severity": severity(m, w, run_star_element),
            "run_star_element": ZH.get(run_star_element) if run_star_element else None,
            "colours_use": use, "colours_avoid": avoid,
            "materials_use": mats_use, "materials_avoid": mats_avoid,
            "objects": objects, "notes": notes, "override_note": override_note,
            "occupants": occ_out, "lighting": lighting, "timing_rules": timing_rules}


def room_briefs(rooms: list[dict], natal: dict, assignment: dict, ys_map: dict,
                period: int, palace_key: str = "palace_pie") -> dict:
    """One brief per traced room keyed by room id; ranks 二五 palaces (worst flag)."""
    out = {}
    for r in rooms:
        pal = r.get(palace_key)
        if not pal or pal == "中":
            out[r["id"]] = {"palace": pal, "severity": 0, "note": "中宫 — no palace brief",
                            "colours_use": [], "colours_avoid": [], "materials_use": [],
                            "materials_avoid": [], "objects": [], "notes": [], "occupants": [],
                            "override_note": None, "timing_rules": [],
                            "lighting": {"fixed_k": "3000–3500K", "lamps_k": "2700K lamps",
                                         "notes": []}}
            continue
        stars = natal["palaces"][pal]
        run_el = STAR_ELEMENT.get(stars.get("base")) if stars.get("base") else None
        occ = []
        for n in assignment.get(r["id"], []):
            ys = ys_map.get(n)
            if ys:
                occ.append({"name": n, "favourable": ys["favourable"],
                            "unfavourable": ys["unfavourable"]})
        out[r["id"]] = room_brief(pal, stars, period, occ, run_star_element=run_el)
        out[r["id"]]["label"] = r.get("label", r["id"])
    afflicted = [(k, v) for k, v in out.items() if v.get("severity", 0) > 0]
    if afflicted:
        top = max(v["severity"] for _, v in afflicted)
        for k, v in afflicted:
            v["worst"] = v["severity"] == top and \
                sum(1 for _, x in afflicted if x["severity"] == top) < len(afflicted)
    return out
