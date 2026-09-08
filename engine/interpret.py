"""Rule-based whole-house interpretation — deterministic, no LLM.

Every sentence is a template filled from engine facts (flying-star structure,
命卦 group mix, current-vs-optimal assignment, 八宅 directions, 用神 colours),
so the same script produces the analogous narrative for ANY family.json /
house.json / rooms.json.

CLI: .venv/bin/python -m engine.interpret [--year 2026] [--period 8]
     [--family data/family.json] [--house data/house.json] [--rooms data/rooms.json]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .bazhai import EAST_GROUP, STAR_SCORE, gua_group, ming_gua, youxing_stars
from .optimizer import optimize, score_assignment
from .remedies import bazhai_compensation, wardrobe_phrase
from .wuxing import (BRANCH_ELEMENT, ELEMENT_EN, PALACES, STEM_ELEMENT,
                     mountain_of_degrees)
from .xuankong import annual_chart, natal_chart, natal_chart_from_degrees

STRUCTURE_TEXT = {
    "旺山旺向": "one of the BEST flying-star structures: the prosperous mountain star "
              "sits at the sitting (people & health) AND the prosperous water star at "
              "the facing (wealth). The house itself grades very well",
    "上山下水": "the weakest flying-star structure: the prosperity stars are inverted "
              "(mountain star at the facing, water star at the sitting). In-room "
              "compensations and door/bed placement matter more than usual here",
    "雙星到向": "both prosperity stars gather at the facing: good for wealth, weaker "
              "for health/people — support the sitting side of the home",
    "雙星到坐": "both prosperity stars gather at the sitting: good for people/health, "
              "weaker for wealth — activate the facing side of the home",
    "旺山": "the prosperous mountain star is correctly placed at the sitting (good for "
          "people & health) but the water star is not at the facing — wealth luck needs "
          "support (water feature / activity at the facing-side sector)",
    "旺向": "the prosperous water star is correctly placed at the facing (good for "
          "wealth) but the mountain star is not at the sitting — health/people luck "
          "needs support (solid, quiet backing at the sitting-side sector)",
}


def _band(x: float) -> str:
    if x >= 1.0:
        return "excellent fit"
    if x >= 0.3:
        return "good fit"
    if x > -0.3:
        return "neutral"
    if x > -1.0:
        return "challenged"
    return "poor fit"


def _good_dirs(gua: str, top: int = 3) -> str:
    from .remedies import good_dirs   # 7A: remedies.py is the single source
    return good_dirs(gua, top)


TEN_GOD_GROUP = {"比肩": "比劫", "劫財": "比劫", "食神": "食傷", "傷官": "食傷",
                 "偏財": "財", "正財": "財", "七殺": "官殺", "正官": "官殺",
                 "偏印": "印", "正印": "印"}
GROUP_MEANING = {
    "比劫": "peers & independence (self-reliance, siblings, competition for resources)",
    "食傷": "output & expression (creativity, performance, children)",
    "財": "wealth (practical results, money; classically the spouse star in a man's chart)",
    "官殺": "authority (career, discipline, status, pressure; classically the spouse star "
          "in a woman's chart)",
    "印": "resource (learning, protection, support from elders)",
}


def _fav_word(el: str, ys: dict) -> str:
    if el in ys["favourable"]:
        return "favourable 喜"
    if el in ys["unfavourable"]:
        return "unfavourable 忌"
    return "neutral"


def interpret_person(chart, ys: dict, year: int) -> dict:
    """Plain-English narrative for one BaZi chart — deterministic templates."""
    paras = []
    dm_el = STEM_ELEMENT[chart.day_master]
    strong = chart.strength["verdict"].startswith("身強")
    season = chart.strength["steps"][0]["value"]
    paras.append(
        f"[§2] The Day Master — the stem that represents the person — is {chart.day_master} "
        f"({ELEMENT_EN[dm_el]}{dm_el}), judged {chart.strength['verdict']} "
        f"(score {chart.strength['score']:+.2f}; season state {season}). "
        + ("A strong chart can carry responsibility, output and wealth — it benefits more "
           "from productive outlets (食傷·財·官殺) than from further support."
           if strong else
           "A weak chart thrives on support — resource 印 and peers 比劫 strengthen it, "
           "while heavy drain (overwork, over-extension, excessive pressure) taxes it.")
        + " Strength is a measure of balance, not ability — it only decides which "
          "elements act as this person's medicine.")

    w = chart.element_weights
    hi, lo = max(w, key=w.get), min(w, key=w.get)
    paras.append(
        "[§1·§5] BaZi treats a chart as a five-element ecosystem that wants balance. This one "
        f"tilts: strongest {ELEMENT_EN[hi]}{hi} ({w[hi]}), weakest {ELEMENT_EN[lo]}{lo} "
        f"({w[lo]}). The elements that would correct the tilt are the 用神 — here "
        f"{'·'.join(ys['favourable'])} — and they become practical levers: "
        f"{wardrobe_phrase(ys)}.")

    counts: dict[str, float] = {}
    for g in chart.ten_gods.values():
        if g in TEN_GOD_GROUP:
            counts[TEN_GOD_GROUP[g]] = counts.get(TEN_GOD_GROUP[g], 0) + 1
    for hidden in chart.hidden_gods.values():
        for _, g in hidden:
            counts[TEN_GOD_GROUP[g]] = counts.get(TEN_GOD_GROUP[g], 0) + 1
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:2]
    paras.append("[§3–4] BaZi classifies every other character by its relationship to the Day "
                 "Master into ten archetypes (十神) covering five life domains; where a "
                 "chart's characters concentrate shows where its energy naturally goes. "
                 "Here the concentration is: "
                 + "; ".join(f"{g} ×{n:g} — {GROUP_MEANING[g]}" for g, n in top) + ".")

    age = year - chart.birth_local.year
    cur = next((d for d in chart.dayun if d.covers(age)), None)
    if cur:
        se, be = STEM_ELEMENT[cur.gz.stem], BRANCH_ELEMENT[cur.gz.branch]
        fav = sum(el in ys["favourable"] for el in (se, be))
        unfav = sum(el in ys["unfavourable"] for el in (se, be))
        mood = ("a supportive decade for this chart." if fav == 2 else
                "a demanding decade — lean harder on the compensations above."
                if unfav == 2 else
                "a mixed decade — activate the favourable half.")
        paras.append(
            f"[§6] Luck cycle 大運 in {year} (age {age}): pillar {cur.gz} "
            f"(ages {cur.start_age:.0f}–{cur.end_age:.0f}) carries {ELEMENT_EN[se]}{se} "
            f"({_fav_word(se, ys)}) over {ELEMENT_EN[be]}{be} ({_fav_word(be, ys)}) — {mood} "
            "Each decade-pillar overlays its two elements on the birth chart, tilting the "
            "balance for or against it — this is why the same chart has easier and harder "
            "decades.")
    else:
        paras.append(f"[§6] In {year} (age {age}) the first 10-year luck pillar has not "
                     "started yet — the birth chart itself dominates.")

    from .domains import life_domains
    doms = life_domains(chart, ys)
    best = max(doms, key=lambda d: d["score"])
    low = min(doms, key=lambda d: d["score"])
    paras.append(
        f"[§8] Life-domain signals (rule-derived, 0–100): strongest {best['en']} "
        f"{best['zh']} ({best['score']} — {best['band']}); most in need of support "
        f"{low['en']} {low['zh']} ({low['score']}). Each score is assembled from "
        "auditable parts — star shares, 神煞 and palace checks, listed under the "
        "cards below — and reads as a structural tendency, not a prediction.")

    gua = ming_gua(chart.lichun_year, chart.sex)
    paras.append(f"[§7] Directions (八宅): {gua}命 · {gua_group(gua)} — best directions "
                 f"{_good_dirs(gua)}. Sleep with the headboard toward, or face while "
                 "working/studying, one of these where the room allows. The belief: the "
                 "hours spent aligned to supportive directions (a third of life is spent "
                 "asleep) let the home reinforce the chart instead of fighting it.")
    return {"paragraphs": paras}


def interpret_family(charts: dict, ys_map: dict) -> dict:
    """Household-level narrative for the Family tab."""
    paras = []
    weak = [n for n, c in charts.items() if c.strength["verdict"].startswith("身弱")]
    strong = [n for n in charts if n not in weak]
    bits = []
    if strong:
        bits.append(f"{len(strong)} strong chart(s) ({', '.join(strong)}) — they can "
                    "carry activity, output and pressure")
    if weak:
        bits.append(f"{len(weak)} weak chart(s) ({', '.join(weak)}) — they recharge "
                    "through support, rest and their favourable elements at home")
    paras.append(f"The household has {len(charts)} members: " + "; ".join(bits) + ". "
                 "(Strength describes balance, not capability — a 'weak' chart simply "
                 "needs topping up, a 'strong' one needs outlets; when rooms are scarce, "
                 "give the weak charts the supportive sectors first.)")

    guas = {n: ming_gua(c.lichun_year, c.sex) for n, c in charts.items()}
    east = [n for n, g in guas.items() if g in EAST_GROUP]
    west = [n for n, g in guas.items() if g not in EAST_GROUP]
    if east and west:
        minority = east if len(east) <= len(west) else west
        paras.append("Mixed East/West-group family (東四命: "
                     f"{', '.join(east)}; 西四命: {', '.join(west)}) — no sector suits "
                     f"everyone, so room assignment is a trade-off; {', '.join(minority)} "
                     "(minority group) need the most in-room compensation.")
    else:
        paras.append("All members share one East/West group — the same sectors suit the "
                     "whole family, which makes room assignment easy.")

    common = set.intersection(*(set(ys["favourable"]) for ys in ys_map.values()))
    if common:
        from .wuxing import ELEMENT_COLOURS
        cols = "·".join(c for e in sorted(common) for c in ELEMENT_COLOURS[e])
        paras.append(f"Element(s) favourable to EVERYONE: {'·'.join(sorted(common))} — "
                     f"safe colours for shared spaces: {cols}.")
    else:
        paras.append("No single element suits every member — keep shared spaces neutral "
                     "and personalise each bedroom with its occupant's colours.")
    return {"paragraphs": paras}


def interpret_housetab(natal: dict, annual: dict, year: int, period: int) -> dict:
    """House-tab narrative: structure + where the year's good/bad stars sit."""
    def _dirname(p):
        return "centre 中宮" if p == "中" else f"{PALACES[p]['dir']} ({p}宮)"
    paras = []
    struct = natal["structure"]
    paras.append(f"{natal['sitting']}山{natal['facing']}向 in Period {period}: {struct} — "
                 + STRUCTURE_TEXT.get(struct, "a mixed structure") + ".")
    mt = next((p for p, st in natal["palaces"].items() if p != "中"
               and st["mountain"] == period), None)
    wt = next((p for p, st in natal["palaces"].items() if p != "中"
               and st["water"] == period), None)
    if mt and wt:
        paras.append(f"The period's prosperous mountain star {period} sits in "
                     f"{_dirname(mt)} — the best sector for beds and rest — and the "
                     f"prosperous water star {period} in {_dirname(wt)} — the best sector "
                     "for the door, desks and activity.")
    five = [p for p, s in annual.items() if s == 5]
    two = [p for p, s in annual.items() if s == 2]
    paras.append("Two visiting stars deserve respect: flying-star theory treats 五黃 "
                 "(5-yellow) as the year's most afflictive energy and 二黑 (2-black) as "
                 f"the illness star, and disturbing their sectors is believed to activate "
                 f"them. In {year} the 五黃 sits in "
                 + "、".join(_dirname(p) for p in five) + " and 二黑 in "
                 + "、".join(_dirname(p) for p in two)
                 + " — avoid renovation, drilling and ground-breaking in those sectors "
                 "this year; keep them quiet and uncluttered.")
    from .liunian import annual_afflictions
    af = annual_afflictions(year)
    paras.append(
        f"Annual afflicted directions: 太歲 sits in {_dirname(af['taisui']['palace'])} "
        f"({af['taisui']['branch']}) — fine to sit with your back to it, avoid facing "
        f"it for long periods; 歲破 in {_dirname(af['suipo']['palace'])} — the year "
        f"breaker; and 三煞 covers "
        + "、".join(_dirname(p) for p in af["sansha"]["palaces"])
        + " — acceptable to face, avoid sitting toward it. No ground-breaking or "
        "renovation in any of these sectors this year.")
    return {"paragraphs": paras}


def interpret_names(people: list[dict]) -> dict:
    """Summary narrative for the Names tab."""
    ok = [p for p in people if p["valid"]]
    paras = []
    if len(ok) == len(people):
        paras.append(f"All {len(ok)} names validate against Kangxi traditional stroke "
                     "counts — the counts the Five-Grid numbers below are built on.")
    else:
        bad = len(people) - len(ok)
        paras.append(f"⚠ {bad} name(s) failed stroke validation — fix them before "
                     "trusting their grids.")
    bad_grids = [(p["name"], g, v["number"]) for p in ok
                 for g, v in p["grids"].items() if v["luck"] == "凶"]
    if bad_grids:
        paras.append("Unlucky (凶) grid numbers: "
                     + "; ".join(f"{n} {g} {num}" for n, g, num in bad_grids)
                     + " — classically softened with a usage name or complementary "
                     "elements rather than a legal rename.")
    else:
        paras.append("No name carries an unlucky (凶) grid number — a well-chosen set.")
    sancai_bad = [p["name"] for p in ok if p["sancai"]["verdict"] != "吉"]
    if sancai_bad:
        paras.append("三才 flow (heaven→person→earth elements) is not fully generative "
                     f"for: {', '.join(sancai_bad)}.")
    else:
        paras.append("Every name's 三才 elements flow generatively — 吉 across the board.")
    return {"paragraphs": paras}


def interpret_unit(result: dict) -> dict:
    """Narrative for one candidate-unit evaluation (coarse mode)."""
    paras = []
    struct = result["structure"]
    paras.append(f"{result['facing_mountain']}向, Period {result['period']}: {struct} — "
                 + STRUCTURE_TEXT.get(struct, "a mixed structure") + ".")
    fits, poor = [], []
    for p in result["people"]:
        best = max(s["total"] for s in p["sectors"])
        (fits if best >= 1.0 else poor).append(f"{p['name']} ({best:+.1f})")
    if fits:
        paras.append("Members with at least one excellent sector here: "
                     + ", ".join(fits) + ".")
    if poor:
        paras.append("Members whose BEST sector is still mediocre: " + ", ".join(poor)
                     + " — this unit gives them little to work with.")
    paras.append(f"Household best-sum {result['household_best_sum']:+.2f} — each member's "
                 "best sector added up. Use it only to RANK candidate units against each "
                 "other (higher is better), not as an absolute grade; this coarse mode "
                 "knows nothing about the actual floorplan.")
    return {"paragraphs": paras}


def interpret_forecast(f: dict, ys: dict, year: int) -> dict:
    """Plain-English narrative for one person's annual forecast dict."""
    paras = []
    gz = f["year_ganzhi"]
    se, be = STEM_ELEMENT[gz[0]], BRANCH_ELEMENT[gz[1]]
    refs = " ".join(t["source_ref"] + t["explanation"] for t in f.get("taisui", []))
    if "沖" in refs:
        mood = ("a clash (沖太歲) year: expect movement and disruption — keep big, risky "
                "commitments conservative and pick dates carefully (Dates tab).")
    elif "值" in refs:
        mood = ("your own zodiac year (值太歲): a year of change — traditionally handled "
                "with steadiness rather than bold moves.")
    elif "害" in refs:
        mood = ("a 害 (harm) interaction with the 太歲 — minor frictions; double-check "
                "agreements and dates.")
    elif "合" in refs:
        mood = ("a combining (合) year with the 太歲 — allies, support and momentum; a "
                "good year to advance plans.")
    else:
        mood = "no direct 太歲 interaction — an astrologically neutral year."
    paras.append(f"{year} is the {gz} year (annual centre star {f['annual_center']}): {mood}")

    fav = sum(el in ys["favourable"] for el in (se, be))
    unfav = sum(el in ys["unfavourable"] for el in (se, be))
    emood = ("both of the year's elements feed your 用神 — the year's energy generally "
             "works in your favour." if fav == 2 else
             "both of the year's elements are ones your chart avoids — pace yourself and "
             "lean on your favourable colours and directions." if unfav == 2 else
             "elementally mixed — favourable in part, so time bigger moves to the "
             "supportive months below.")
    paras.append(f"The year carries {ELEMENT_EN[se]}{se} over {ELEMENT_EN[be]}{be}: {emood}")

    if f.get("room_palace"):
        bad = [m for m in f["months"] if m.get("room_star") in (5, 2)]
        good = [m for m in f["months"] if (m.get("room_quality") or 0) >= 1.5]
        if bad:
            paras.append(f"Your bedroom ({f['room_palace']}宮): the troublesome 五黃/二黑 "
                         "monthly stars visit in the "
                         + "、".join(m["month_branch"] + "月" for m in bad)
                         + " months — avoid renovation, drilling or ground-breaking in "
                         "that room then, and keep it quiet.")
        else:
            paras.append(f"Your bedroom ({f['room_palace']}宮) receives no 五黃/二黑 "
                         "monthly star this year — no month needs special caution there.")
        if good:
            paras.append("Supportive months for that room: "
                         + "、".join(m["month_branch"] + "月" for m in good)
                         + " — good windows for changes or fresh starts in it.")
    return {"paragraphs": paras}


def interpret_dates(days: list[dict]) -> dict:
    """Plain-English narrative for one month's 擇日 day-rating table."""
    paras = []
    best = sorted(days, key=lambda d: -d["score"])[:5]
    paras.append("Best days this month: "
                 + ", ".join(f"{d['date'][-2:]} ({d['officer']}日 {d['score']:+.1f})"
                             for d in best)
                 + " — favour these for moving, renovation starts and signings.")
    worst = [d for d in days if d["score"] <= -2]
    if worst:
        paras.append("Avoid " + ", ".join(f"{d['date'][-2:]} ({d['officer']}日)" for d in worst)
                     + " — 破 'Destruction' or heavily clashed days; postpone important "
                     "starts.")
    else:
        paras.append("No strongly negative days this month.")
    per: dict[str, list[str]] = {}
    for d in days:
        for fl in d["person_flags"]:
            if fl["kind"].startswith("沖"):
                per.setdefault(fl["name"], []).append(d["date"][-2:])
    for name, ds in per.items():
        paras.append(f"{name} is personally clashed (沖) on day(s) {', '.join(ds)} — that "
                     "member should sit out big personal moves those days even when the "
                     "general score looks fine.")
    paras.append("Within a chosen day, prefer the 吉時 hours shown in the table — 貴人 "
                 "(the day's nobleman hours) and 合日 (hours combining the day branch) — "
                 "and avoid the 時破 hour, which clashes the day itself.")
    return {"paragraphs": paras}


def interpret_house(charts: dict, ys_map: dict, house: dict, rooms: list[dict],
                    year: int, period: int, method: str = "pie",
                    current: dict[str, list[str]] | None = None,
                    master_couple: list[str] | None = None,
                    allow_master_split: bool = False, lam: float = 1.0) -> dict:
    """→ {"sections": [{"heading", "lines": [...]}]} — plain-English narrative."""
    annual = annual_chart(year)
    natal = natal_chart_from_degrees(period, house["facing_deg"])
    rooms_by_id = {r["id"]: r for r in rooms}
    sections = []

    # 1. structure verdict, for every declared period (兼向替卦-aware)
    lines, structures = [], {}
    for p in house.get("periods", [period]):
        n = natal_chart_from_degrees(p, house["facing_deg"])
        structures[p] = n["structure"]
        txt = STRUCTURE_TEXT.get(n["structure"], "a mixed structure")
        kind = f" ({n['chart_type']})" if n.get("chart_type") == "替卦" else ""
        lines.append(f"Period {p}: {n['sitting']}山{n['facing']}向{kind} → "
                     f"{n['structure']} — {txt}.")
    b = natal.get("boundary")
    if b and b["zone"] != "正向":
        lines.append(f"⚠ 兼向: facing {house['facing_deg']}° sits {b['offset_deg']:+.1f}° "
                     f"from the {b['mountain']} centre ({b['zone']}) — the chart above "
                     "uses 替卦 replacement stars (沈氏玄空).")
    if b and b["zone"] == "騎線" and natal.get("alternate"):
        alt = natal["alternate"]
        lines.append(f"⚠ 騎線: the reading is within 1° of the {b['mountain']}/"
                     f"{b['neighbor']} boundary. If the true facing is {b['neighbor']}, "
                     f"the chart becomes {alt['sitting']}山{alt['facing']}向 "
                     f"({alt['chart_type']}) → {alt['structure']}. Re-measure at 2–3 "
                     "spots away from metal before committing to either chart.")
    if len(set(structures.values())) > 1:
        lines.append("⚠ The structural verdict DIFFERS between the declared periods — "
                     "the renovation date decides which chart applies. Confirm it before "
                     "trusting either verdict.")
    sections.append({"heading": "House structure (玄空飛星)", "lines": lines})

    # 2. East/West group mix
    guas = {n: ming_gua(c.lichun_year, c.sex) for n, c in charts.items()}
    east = [n for n, g in guas.items() if g in EAST_GROUP]
    west = [n for n, g in guas.items() if g not in EAST_GROUP]
    lines = [f"{n}: {guas[n]}命 · {gua_group(guas[n])} — best directions {_good_dirs(guas[n])}"
             for n in charts]
    if east and west:
        minority = east if len(east) <= len(west) else west
        lines.append(
            "Mixed East/West household: a sector auspicious for one group is inauspicious "
            "for the other BY DEFINITION, so no floorplan can give every member positive "
            f"八宅 scores everywhere. Most constrained: {', '.join(minority)} (minority "
            "group) — prioritise their in-room compensations below.")
    else:
        lines.append("All members share one group — every sleeping sector can in principle "
                     "suit the whole household.")
    sections.append({"heading": "Family 命卦 East/West mix", "lines": lines})

    # 3. current vs optimal assignment
    cur_res = (score_assignment(current, charts, ys_map, rooms_by_id, natal, annual,
                                method, lam) if current else None)
    try:
        opt = optimize(charts, ys_map, rooms, natal, annual, method, lam,
                       master_couple, allow_master_split)
    except ValueError as e:
        opt = None
        opt_err = str(e)
    lines = []
    if cur_res:
        lines.append(f"Current arrangement: household total {cur_res['household_total']:+.2f}.")
        lines.extend(f"⚠ {v}" for v in cur_res["violations"])
    if opt:
        best = opt["best"][0]
        lines.append(f"Best of {opt['evaluated']} feasible arrangements: "
                     f"{best['household_total']:+.2f}"
                     + (" (parents kept together)" if not allow_master_split and master_couple
                        else "") + ".")
        if cur_res and not cur_res["violations"] and \
                best["household_total"] > cur_res["household_total"] + 0.05:
            cur_room = {n: rid for rid, ns in current.items() for n in ns}
            best_room = {n: rid for rid, ns in best["assignment"].items() for n in ns}
            moves = [f"{n}: {rooms_by_id[cur_room[n]]['label']} → {rooms_by_id[best_room[n]]['label']}"
                     for n in charts
                     if cur_room.get(n) and best_room.get(n) and cur_room[n] != best_room[n]]
            if moves:
                lines.append("Recommended moves: " + "; ".join(moves)
                             + f" (gain {best['household_total'] - cur_res['household_total']:+.2f}).")
        elif cur_res and not cur_res["violations"]:
            lines.append("The current arrangement is already (near-)optimal — keep it.")
    else:
        lines.append(f"⚠ Optimizer found no feasible arrangement: {opt_err}")
    sections.append({"heading": "Room assignment verdict", "lines": lines})

    # 4. per-person placement + compensation (based on the current arrangement)
    if cur_res:
        lines = []
        for s in cur_res["scores"]:
            name = s["person"]
            line = f"{name} in {s['room_label']}: {s['total']:+.2f} ({_band(s['total'])})."
            worst = min(s["breakdown"], key=lambda b: b["contribution"])
            if s["total"] < 0:
                comp = bazhai_compensation(guas[name], ys_map[name])
                line += (f" Main drag: {worst['explanation']}."
                         f" Compensate inside the room: {comp['action']}.")
            else:
                line += f" Well placed; personal best directions remain {_good_dirs(guas[name])}."
            lines.append(line)
        sections.append({"heading": "Per-person placement & compensation", "lines": lines})

    # 5. how to read this
    lines = ["Every score blends three layers — 八宅 personal directions (40%), the "
             "sector's flying stars (40%) and 用神 element match (20%) — plus small "
             "roommate 沖/合 compatibility terms; each line above cites its rule.",
             "Scores are zero-centred fit measures between one person's chart and one "
             "sector — a negative score marks a person/room MISMATCH, not a bad house "
             "and not a prediction of harm. In a mixed-group family some negatives are "
             "unavoidable; the goal is the arrangement that minimises them."]
    if house.get("provisional"):
        lines.append("⚠ PROVISIONAL inputs: facing degrees, period (8 vs 9) and room "
                     "tracing await the on-site compass check and renovation date. The "
                     "structural verdict can flip if the true facing crosses a mountain "
                     "boundary.")
    sections.append({"heading": "How to read these scores", "lines": lines})

    return {"year": year, "period": period, "method": method, "sections": sections}


def main() -> None:
    ap = argparse.ArgumentParser(description="Rule-based house interpretation (no LLM)")
    ap.add_argument("--family", default="data/family.json")
    ap.add_argument("--house", default="data/house.json")
    ap.add_argument("--rooms", default="data/rooms.json")
    ap.add_argument("--year", type=int, default=2026)
    ap.add_argument("--period", type=int, default=8)
    ap.add_argument("--method", default="pie", choices=["pie", "grid"])
    a = ap.parse_args()

    from .bazi import TRUE_SOLAR, build_chart
    from .import_family import load_family
    from .sectors import load_rooms
    from .yongshen import yong_shen

    members = load_family(Path(a.family))
    charts = {m.name: build_chart(m.name, m.sex, m.birth_dt, TRUE_SOLAR) for m in members}
    ys = {n: yong_shen(c) for n, c in charts.items()}
    house = json.loads(Path(a.house).read_text("utf8"))
    rooms_data = load_rooms(Path(a.rooms))
    current = rooms_data.get("default_assignment")
    couple = (current or {}).get("master", [])  # ponytail: couple = master-room occupants
    out = interpret_house(charts, ys, house, rooms_data["rooms"], a.year, a.period,
                          a.method, current=current, master_couple=couple)
    for sec in out["sections"]:
        print(f"\n== {sec['heading']} ==")
        for line in sec["lines"]:
            print("  - " + line)


if __name__ == "__main__":
    main()
