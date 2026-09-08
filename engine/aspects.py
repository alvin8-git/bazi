"""INTERPRET layer — aspect cards on a single 0–100 scale (design doc §3/§5).

WEIGHTS is the ONE table the composition runs from (T2-A): golden tests derive
expectations from it, and the primer publishes it labelled "calibration, not
classical truth". Each component has a unique rule_id per card (1A registry —
pytest asserts no duplicates inside any card's audit).

Bands (T5-A, quantised — the band word is the primary visual):
  ≥80 旺 strong · 65–79 优 good · 45–64 平 fair · 30–44 弱 weak · <30 忌 poor
Rooms' zero-centred fit maps affinely: score = clamp(50 + 25·fit, 5, 95);
real family fits span −1.20…+1.34 — a saturation-guard test (T3-A) asserts
every produced card stays inside the linear region |fit| ≤ 1.8.
"""
from __future__ import annotations

from .bazhai import STAR_SCORE, gua_group, ming_gua, youxing_stars
from .domains import health_map, life_domains
from .join import score_direction
from .liunian import multi_year_outlook, room_month_watch
from .remedies import (arbitrate, bazhai_compensation, element_remedies,
                       home_remedies, pair_remedies, room_remedies,
                       study_remedies, taohua_palace, timing_remedies,
                       wenchang_palace)
from .wuxing import BRANCH_ELEMENT, PALACES, STEM_ELEMENT
from .xuankong import natal_chart, star_quality

SCHEMA_V = 1
ASPECTS = ["health", "career", "study", "wealth", "relationship", "luck"]
ASPECT_ZH = {"health": "健康", "career": "事业", "study": "学业", "wealth": "财富",
             "relationship": "感情", "luck": "运势"}

# T2-A: the calibration table. component rule_ids must be unique per card (1A).
WEIGHTS = {
    "health": [("tcm-balance", 40), ("bed-mountain-star", 25),
               ("tianyi-access", 20), ("year-room-watch", 15)],
    "career": [("domain-career", 50), ("shengqi-access", 25),
               ("wang-water-usable", 25)],
    "study": [("domain-learning", 40), ("personal-wenchang", 35),
              ("house-wenchang", 25)],
    "wealth": [("domain-wealth", 50), ("wang-water-activation", 30),
               ("p9-durability", 20)],
    "relationship": [("domain-attraction-stability", 50), ("bedroom-fit", 30),
                     ("taohua-access", 20)],
    "luck": [("room-fit", 50), ("year-outlook", 30), ("dayun-favourability", 20)],
}

BAND_EDGES = [(80, "strong"), (65, "good"), (45, "fair"), (30, "weak")]
BAND_ZH = {"strong": "旺", "good": "优", "fair": "平", "weak": "弱", "poor": "忌"}

MEANING = {
    "health": {
        "strong": "the chart and bedroom both support this person's health",
        "good": "health support is solid; keep the current setup",
        "fair": "health support is ordinary — the actions below add margin",
        "weak": "the chart or room placement leaves health under-supported",
        "poor": "health is the aspect most in need of attention here"},
    "career": {
        "strong": "career structure and home support line up well",
        "good": "career support is solid; activate what the actions name",
        "fair": "career support is ordinary — usable, not amplified",
        "weak": "career support is thin in chart or home placement",
        "poor": "career is the least supported aspect here"},
    "study": {
        "strong": "study alignment is excellent — the 文昌 setup works",
        "good": "study support is solid; small desk adjustments remain",
        "fair": "study support is ordinary — desk direction is the easy win",
        "weak": "study alignment is weak — fix the desk/文昌 placement",
        "poor": "study is the aspect most in need of attention here"},
    "wealth": {
        "strong": "wealth capacity and the home's wealth star both cooperate",
        "good": "wealth support is solid; keep the wealth zone lively",
        "fair": "wealth support is ordinary — activation adds margin",
        "weak": "wealth support is thin — activate the facing-side zone",
        "poor": "wealth is the least supported aspect here"},
    "relationship": {
        "strong": "relationship signals and bedroom placement both support",
        "good": "relationship support is solid",
        "fair": "relationship support is ordinary — steady, not sparkling",
        "weak": "relationship signals need support — see the actions",
        "poor": "relationship is the aspect most in need of attention here"},
    "luck": {
        "strong": "room fit, year and decade all run in this person's favour",
        "good": "overall luck support is solid this year",
        "fair": "an ordinary year — neither tailwind nor headwind",
        "weak": "this year asks for patience — time big moves carefully",
        "poor": "a demanding stretch — lean on the compensations below"},
}


def band_of(score: int) -> str:
    for edge, name in BAND_EDGES:
        if score >= edge:
            return name
    return "poor"


def affine_fit(fit: float) -> int:
    """Zero-centred room fit → 0–100 (§10 4A). Linear inside |fit| ≤ 1.8."""
    return round(min(95.0, max(5.0, 50 + 25 * fit)))


def _clamp(x: float) -> int:
    return round(min(95.0, max(5.0, x)))


def _audit(rule_id, sub, weight, explanation, source_ref):
    return {"rule_id": rule_id, "sub_score": sub, "weight": weight,
            "explanation": explanation, "source_ref": source_ref}


def _room_access(target_palace, own_palace, palace_rooms, what):
    """Common 'does a room sit on palace X' scorer."""
    if target_palace is None:
        return 50, f"no {what} palace derivable — neutral"
    d = PALACES[target_palace]["dir"]
    if own_palace == target_palace:
        return 88, f"own room sits on the {what} palace {d} ({target_palace}宮)"
    if palace_rooms.get(target_palace):
        labels = "、".join(r["label"] for r in palace_rooms[target_palace])
        return 70, f"{what} palace {d} holds {labels} — accessible"
    return 38, f"no traced room in the {what} palace {d} ({target_palace}宮)"


def person_cards(chart, ys, natal: dict, annual: dict[str, int], year: int,
                 room_palace: str | None, palace_rooms: dict[str, list[dict]],
                 room_label: str | None = None,
                 partner=None) -> list[dict]:
    """Six aspect cards for one person. Degrades honestly without a room.
    `partner`: the other half of the couple — adds R6 pair actions to the
    relationship card (M2)."""
    gua = ming_gua(chart.lichun_year, chart.sex)
    doms = {d["key"]: d for d in life_domains(chart, ys)}
    yx = youxing_stars(gua)
    period = natal["period"]

    fit = None
    if room_palace:
        fit = score_direction(chart, ys, natal, annual, room_palace)["total"]

    # remedies once, reused across cards
    elem_acts = element_remedies(chart, ys)
    room_res = (room_remedies(chart, ys, gua, room_palace, natal, annual, year)
                if room_palace else {"actions": [], "deferred": []})
    study_acts = study_remedies(chart, room_palace, palace_rooms)
    comp_act = bazhai_compensation(gua, ys) if fit is not None and fit < 0 else None

    wang_water = next((p for p, st in natal["palaces"].items()
                       if p != "中" and st["water"] == period), None)
    tianyi = next((p for p, st in yx.items() if st == "天醫"), None)
    shengqi = next((p for p, st in yx.items() if st == "生氣"), None)

    def component(rule_id):
        # each branch returns (sub 0-100, explanation, source_ref)
        if rule_id == "tcm-balance":
            flags = [h for h in health_map(chart) if h["status"] != "balanced"]
            sub = _clamp(90 - 20 * len(flags))
            why = ("all five elements in workable balance" if not flags else
                   "; ".join(f"{h['element']} {h['status']} ({h['share']}% — "
                             f"{h['organs']})" for h in flags))
            return sub, why, "TCM element-organ map (reference, not medical advice)"
        if rule_id == "bed-mountain-star":
            if not room_palace:
                return 50, "no assigned room — neutral", "玄空 山星 (degraded: unassigned)"
            q, why = star_quality(natal["palaces"][room_palace]["mountain"], period)
            return _clamp(50 + 22 * q), f"bedroom 山星: {why}", "玄空 山星 quality"
        if rule_id == "tianyi-access":
            sub, why = _room_access(tianyi, room_palace, palace_rooms, "天醫 health")
            return sub, why, "八宅 天醫 direction"
        if rule_id == "year-room-watch":
            if not room_palace:
                return 50, "no assigned room — neutral", "流月紫白 (degraded: unassigned)"
            n = len(room_month_watch(room_palace, year))
            why = (f"{n} month(s) with 五黃/二黑 in the bedroom palace in {year}"
                   if n else f"no 五黃/二黑 month visits the bedroom palace in {year}")
            return _clamp(90 - 25 * n), why, f"流月紫白 room watch, {year}"
        if rule_id == "domain-career":
            d = doms["career"]
            return d["score"], f"career structure signal {d['score']} ({d['band']})", d["source_ref"]
        if rule_id == "shengqi-access":
            sub, why = _room_access(shengqi, room_palace, palace_rooms, "生氣 vitality")
            return sub, why, "八宅 生氣 direction"
        if rule_id in ("wang-water-usable", "wang-water-activation"):
            if wang_water is None:
                return 45, f"no palace carries water star {period}", "玄空 向星要動"
            rooms = palace_rooms.get(wang_water, [])
            d = PALACES[wang_water]["dir"]
            if any(not r["sleeping"] for r in rooms):
                labels = "、".join(r["label"] for r in rooms if not r["sleeping"])
                return 82, f"向星{period} zone {d} holds active space ({labels})", "玄空 向星要動"
            if rooms:
                return 60, f"向星{period} zone {d} holds only bedrooms — mild activation", "玄空 向星要動"
            return 38, f"no traced room on the 向星{period} zone {d}", "玄空 向星要動"
        if rule_id == "domain-learning":
            d = doms["learning"]
            return d["score"], f"learning structure signal {d['score']} ({d['band']})", d["source_ref"]
        if rule_id == "personal-wenchang":
            sub, why = _room_access(wenchang_palace(chart), room_palace,
                                    palace_rooms, "personal 文昌")
            return sub, why, "文昌貴人 (day-stem table)"
        if rule_id == "house-wenchang":
            wc4 = next((p for p, st in natal["palaces"].items()
                        if p != "中" and st["water"] == 4), None)
            sub, why = _room_access(wc4, room_palace, palace_rooms, "house 文昌 (向星4)")
            return sub, why, "玄空 四綠文昌星"
        if rule_id == "domain-wealth":
            d = doms["wealth"]
            return d["score"], f"wealth capacity signal {d['score']} ({d['band']})", d["source_ref"]
        if rule_id == "p9-durability":
            s9 = natal_chart(9, natal["facing"],
                             use_tigua=natal.get("chart_type") == "替卦")["structure"]
            sub = {"旺山旺向": 90, "雙星到向": 78, "旺向": 70, "旺山": 45,
                   "雙星到坐": 45, "上山下水": 25}.get(s9, 50)
            return sub, f"after a Period-9 renovation this facing becomes {s9}", "玄空 九運 chart"
        if rule_id == "domain-attraction-stability":
            a, s = doms["attraction"], doms["stability"]
            sub = round((a["score"] + s["score"]) / 2)
            weaker = a if a["score"] <= s["score"] else s
            return sub, (f"mean of attraction {a['score']} and stability {s['score']} "
                         f"— weaker half: {weaker['en']} ({weaker['score']})"), \
                "life-domain signals (5A merge)"
        if rule_id == "bedroom-fit":
            if fit is None:
                return 50, "no assigned room — neutral", "3-layer fit (degraded: unassigned)"
            return affine_fit(fit), f"bedroom fit {fit:+.2f} → affine map", \
                "3-layer room fit (affine, raw kept)"
        if rule_id == "taohua-access":
            sub, why = _room_access(taohua_palace(chart), room_palace,
                                    palace_rooms, "桃花")
            return sub, why, "桃花位 (day-branch trine)"
        if rule_id == "room-fit":
            if fit is None:
                return 50, "no assigned room — neutral", "3-layer fit (degraded: unassigned)"
            return affine_fit(fit), f"assigned-room fit {fit:+.2f} → affine map", \
                "3-layer room fit (affine, raw kept)"
        if rule_id == "year-outlook":
            row = multi_year_outlook(chart, ys, year, 1)[0]
            sub = {"steady": 75, "moderate movement": 55, "high volatility": 30}[row["verdict"]]
            return sub, f"{year} {row['gz']}: {row['verdict']} ({row['points']} pts)", \
                "流年 interaction scan"
        if rule_id == "dayun-favourability":
            age = year - chart.birth_local.year
            cur = next((dd for dd in chart.dayun if dd.covers(age)), None)
            if cur is None:
                return 50, "first 大運 not started — birth chart dominates", "大運"
            se, be = STEM_ELEMENT[cur.gz.stem], BRANCH_ELEMENT[cur.gz.branch]
            fav = sum(el in ys["favourable"] for el in (se, be))
            unfav = sum(el in ys["unfavourable"] for el in (se, be))
            sub = 80 if fav == 2 else 30 if unfav == 2 else 55
            return sub, f"decade pillar {cur.gz}: {fav} favourable / {unfav} unfavourable element(s)", \
                "大運 vs 用神"
        raise KeyError(rule_id)

    pair_acts = (pair_remedies(chart, partner, palace_rooms, shared_room=True)
                 if partner is not None else [])
    aspect_actions = {
        "health": elem_acts + [a for a in room_res["actions"] if a["priority"] == 1],
        "career": [a for a in room_res["actions"] if a["resource"] == "headboard"],
        "study": study_acts,
        "wealth": [],
        "relationship": ([comp_act] if comp_act else []) + pair_acts,
        "luck": room_res["actions"] + ([comp_act] if comp_act else []),
    }

    cards = []
    for aspect in ASPECTS:
        audit, num, den = [], 0.0, 0
        for rule_id, weight in WEIGHTS[aspect]:
            sub, why, ref = component(rule_id)
            audit.append(_audit(rule_id, sub, weight, why, ref))
            num += sub * weight
            den += weight
        score = round(num / den)
        band = band_of(score)
        driver = max(audit, key=lambda a: a["weight"] * abs(a["sub_score"] - 50))
        winners, superseded = arbitrate(aspect_actions[aspect])
        deferred = room_res["deferred"] if aspect in ("health", "luck") else []
        if fit is not None:
            audit_extra = [{"rule_id": "raw-room-fit", "sub_score": None,
                            "weight": 0, "explanation": f"raw zero-centred fit {fit:+.2f}",
                            "source_ref": "kept for audit (4A)"}]
        else:
            audit_extra = []
        cards.append({
            "v": SCHEMA_V,
            "subject": {"type": "person", "id": chart.person, "label": chart.person},
            "aspect": aspect, "aspect_zh": ASPECT_ZH[aspect],
            "score": score, "band": band, "band_zh": BAND_ZH[band],
            "meaning": MEANING[aspect][band],
            "driver": driver["explanation"],
            "actions": winners[:3],
            "audit": audit + audit_extra,
            "superseded": superseded + deferred,
            "room": room_label,
            "source_ref": "aspect composition v1 (weights table §5) — MODERN SYNTHESIS",
        })
    return cards


def home_cards(member_cards: dict[str, list[dict]], natal: dict,
               annual: dict[str, int], year: int,
               palace_rooms: dict[str, list[dict]],
               structure_text: str) -> list[dict]:
    """Home aggregation (6A): family mean per aspect; driver ALWAYS names the
    weakest member and their top fix. Plus structure + timing cards."""
    cards = []
    for aspect in ASPECTS:
        rows = [(name, next(c for c in cs if c["aspect"] == aspect))
                for name, cs in member_cards.items()]
        score = round(sum(c["score"] for _, c in rows) / len(rows))
        band = band_of(score)
        weak_name, weak_card = min(rows, key=lambda r: r[1]["score"])
        fix = (weak_card["actions"][0]["action"] if weak_card["actions"]
               else "no specific action — see their audit")
        cards.append({
            "v": SCHEMA_V,
            "subject": {"type": "home", "id": "home", "label": "Our Home"},
            "aspect": aspect, "aspect_zh": ASPECT_ZH[aspect],
            "score": score, "band": band, "band_zh": BAND_ZH[band],
            "meaning": f"family mean across {len(rows)} members",
            "driver": f"weakest: {weak_name} ({weak_card['score']}) — top fix: {fix}",
            "actions": weak_card["actions"][:1],
            "audit": [{"rule_id": f"member-{name}", "sub_score": c["score"],
                       "weight": 1, "explanation": f"{name}: {c['score']} ({c['band']})",
                       "source_ref": "member card (6A mean)"} for name, c in rows],
            "superseded": [],
            "source_ref": "home aggregation (6A) — family mean, weakest flagged",
        })

    struct = natal["structure"]
    struct_score = {"旺山旺向": 90, "雙星到向": 70, "雙星到坐": 70, "旺向": 60,
                    "旺山": 60, "上山下水": 25}.get(struct, 50)
    band = band_of(struct_score)
    r3 = home_remedies(natal, palace_rooms)
    winners, superseded = arbitrate(r3)
    cards.append({
        "v": SCHEMA_V,
        "subject": {"type": "home", "id": "home", "label": "Our Home"},
        "aspect": "structure", "aspect_zh": "格局",
        "score": struct_score, "band": band, "band_zh": BAND_ZH[band],
        "meaning": structure_text,
        "driver": f"{natal['sitting']}山{natal['facing']}向 Period {natal['period']} → {struct}",
        "actions": winners[:3],
        "audit": [_audit("structure-class", struct_score, 100,
                         f"{struct} (structure classifier)", "玄空飛星 格局")],
        "superseded": superseded,
        "source_ref": "structure card — 玄空 classifier + R3 placement gaps",
    })

    r4 = timing_remedies(year, annual, palace_rooms)
    n = len(r4)
    timing_score = _clamp(85 - 15 * n)
    band = band_of(timing_score)
    cards.append({
        "v": SCHEMA_V,
        "subject": {"type": "home", "id": "home", "label": "Our Home"},
        "aspect": "timing", "aspect_zh": "流年",
        "score": timing_score, "band": band, "band_zh": BAND_ZH[band],
        "meaning": (f"{n} zone(s) carry a {year} affliction — fine to occupy, "
                    "bad to disturb" if n else
                    f"no traced room sits on a {year} afflicted zone"),
        "driver": (r4[0]["trigger"] if r4 else f"clear year, {year}"),
        "actions": r4[:3],
        "audit": [_audit(f"affliction-{i}", None, 0, a["trigger"], a["source_ref"])
                  for i, a in enumerate(r4)],
        "superseded": [],
        "source_ref": f"timing card — 流年神煞 + 紫白, {year}",
    })
    return cards


def room_fit_card(chart, ys, room: dict, palace: str, natal: dict,
                  annual: dict[str, int], year: int) -> dict:
    """Person×room suitability card (subject type 'room' — M2 Our Home page).
    The audit IS the existing cited 3-layer breakdown; score is its affine map."""
    sb = score_direction(chart, ys, natal, annual, palace)
    fit = sb["total"]
    score = affine_fit(fit)
    band = band_of(score)
    gua = ming_gua(chart.lichun_year, chart.sex)
    worst = min(sb["breakdown"], key=lambda b: b["contribution"])
    best = max(sb["breakdown"], key=lambda b: b["contribution"])
    driver = worst if fit < 0 else best
    acts = room_remedies(chart, ys, gua, palace, natal, annual, year)
    actions = acts["actions"] + ([bazhai_compensation(gua, ys)] if fit < 0 else [])
    winners, superseded = arbitrate(actions)
    meaning = {"strong": "an excellent room for this person",
               "good": "a good room for this person",
               "fair": "a workable room — neither boost nor drag",
               "weak": "a mismatched room — apply the compensations",
               "poor": "the weakest pairing here — compensate or reassign"}[band]
    return {"v": SCHEMA_V,
            "subject": {"type": "room", "id": f"{chart.person}|{room['id']}",
                        "label": f"{chart.person} × {room['label']}"},
            "aspect": "suitability", "aspect_zh": "适配",
            "score": score, "band": band, "band_zh": BAND_ZH[band],
            "meaning": meaning,
            "driver": driver["explanation"],
            "actions": winners[:3],
            "audit": [{"rule_id": b["rule_id"], "sub_score": None,
                       "weight": b["weight"], "explanation": b["explanation"],
                       "source_ref": b["source_ref"],
                       "contribution": b["contribution"]}
                      for b in sb["breakdown"]] +
                     [{"rule_id": "raw-room-fit", "sub_score": None, "weight": 0,
                       "explanation": f"raw zero-centred fit {fit:+.2f}",
                       "source_ref": "kept for audit (4A)"}],
            "superseded": superseded + acts["deferred"],
            "room": room["label"],
            "source_ref": "3-layer room fit (八宅40·飞星40·用神20) → affine 0-100",
            "raw_fit": fit}


def palace_rooms_map(rooms: list[dict], method: str = "pie") -> dict[str, list[dict]]:
    key = "palace_pie" if method == "pie" else "palace_grid"
    out: dict[str, list[dict]] = {}
    for r in rooms:
        out.setdefault(r[key], []).append(r)
    return out


def compose_family(charts: dict, ys_map: dict, rooms: list[dict],
                   assignment: dict[str, list[str]], natal: dict,
                   annual: dict[str, int], year: int, method: str,
                   structure_text: str,
                   couple: list[str] | None = None) -> dict:
    """All person cards + home cards + per-member room cards for one
    arrangement. `couple` members get R6 pair actions on their
    relationship cards (M2)."""
    key = "palace_pie" if method == "pie" else "palace_grid"
    rooms_by_id = {r["id"]: r for r in rooms}
    proom = {}
    for rid, names in assignment.items():
        for n in names:
            if rid in rooms_by_id:
                proom[n] = rooms_by_id[rid]
    palace_rooms = palace_rooms_map(rooms, method)
    couple = [n for n in (couple or []) if n in charts]
    people, room_cards = {}, {}
    for name, chart in charts.items():
        room = proom.get(name)
        partner = (charts[couple[1 - couple.index(name)]]
                   if name in couple and len(couple) == 2 else None)
        people[name] = person_cards(
            chart, ys_map[name], natal, annual, year,
            room[key] if room else None, palace_rooms,
            room["label"] if room else None, partner=partner)
        if room is not None:
            room_cards[name] = room_fit_card(chart, ys_map[name], room,
                                             room[key], natal, annual, year)
    return {"v": SCHEMA_V, "year": year, "period": natal["period"],
            "method": method, "people": people, "rooms": room_cards,
            "home": home_cards(people, natal, annual, year, palace_rooms,
                               structure_text)}
