"""Plain-language layer for the reading page (owner-approved templates, 2026-10-10).

Deterministic: every sentence is a fixed template whose slots are filled from fields the
payload already carries. Nothing is generated at runtime. The stem and season images follow
classical 天干 natures and the 窮通寶鑑 seasons the engine already cites, so the plain sentence
and the citation behind it say the same thing.
"""
from __future__ import annotations

EN = {"木": "Wood", "火": "Fire", "土": "Earth", "金": "Metal", "水": "Water"}
STEM_EL = dict(zip("甲乙丙丁戊己庚辛壬癸", "木木火火土土金金水水"))

STEM_IMAGE = {
    "甲": ("a tall tree", "Upright and principled, always growing toward the light"),
    "乙": ("a climbing vine", "Adaptable and persuasive, you find a way around obstacles"),
    "丙": ("the sun", "Warm and open, you want to be seen and to light things up"),
    "丁": ("lamplight", "Focused and attentive, you glow brightest close up"),
    "戊": ("a mountain", "Solid and dependable, you are hard to move once settled"),
    "己": ("garden soil", "Patient and nurturing, you make things grow around you"),
    "庚": ("raw iron", "Direct and decisive, you are built for hard work"),
    "辛": ("a cut jewel", "Refined and precise, you know your own worth"),
    "壬": ("a great river", "Restless and far-seeing, you carry others along"),
    "癸": ("soft rain", "Quiet and perceptive, you work by seeping in"),
}
SEASON = {"寅": "early spring", "卯": "spring", "辰": "late spring", "巳": "early summer",
          "午": "midsummer", "未": "late summer", "申": "early autumn", "酉": "autumn",
          "戌": "late autumn", "亥": "early winter", "子": "midwinter", "丑": "late winter"}
MEDICINE = {
    "火": dict(need="warmth", gives="energy, visibility and encouragement", colours="red, purple and orange",
              acts="sunlight, exercise that lifts your heart rate, and being seen"),
    "水": dict(need="water", gives="rest, reflection and flow", colours="black and deep blue",
              acts="real rest, time near water, travel and letting ideas run"),
    "木": dict(need="growth", gives="learning and fresh starts", colours="green",
              acts="learning something new, plants and early mornings"),
    "土": dict(need="steadiness", gives="routine and solid ground", colours="yellow, beige and brown",
              acts="routine, home life and keeping commitments"),
    "金": dict(need="structure", gives="clarity and discipline", colours="white, gold and silver",
              acts="order, precision and finishing what you start"),
}
STRENGTH = {
    "weak": dict(short="run low on your own fuel", head="You run on borrowed fuel",
                 means="Your chart has more pressure than support, so you do best when you protect your energy and accept help.",
                 todo="Drop one commitment this month and guard your recovery time."),
    "strong": dict(short="have energy to spare", head="You have strength to spare",
                   means="Your chart carries load easily. The risk is restlessness from too little challenge, not burnout.",
                   todo="Take on one real responsibility you have been putting off."),
    "balanced": dict(short="are evenly balanced", head="You are evenly balanced",
                     means="Neither side of your chart dominates, so timing matters more than temperament.",
                     todo="Use the good years below for your big moves."),
    "follower": dict(short="are shaped by one strong force", head="You go with your strongest current",
                     means="Your chart gives itself to its dominant element. You thrive by working with it, not against it.",
                     todo="Lean into the element that dominates your chart."),
}
BAND = {"weak 不足": "too little", "balanced": "about right", "excess 過旺": "too much"}
PHASE = {
    "growth": dict(word="Expanding", glyph="sun", means="Conditions favour building. What you start now tends to take root."),
    "consolidation": dict(word="Gathering", glyph="partsun", means="A decade for building reserves rather than big leaps."),
    "transition": dict(word="Changing", glyph="wind", means="Expect a shake-up at home or work. Stay flexible and keep options open."),
    "corrective": dict(word="Repairing", glyph="rain", means="A decade for care: protect health, money and the relationships that matter."),
}
YEAR = {"peak": dict(word="Strong year", head="{y} is one of your strongest years"),
        "steady": dict(word="Steady year", head="{y} is a steady year"),
        "careful": dict(word="Careful year", head="{y} asks for care")}
AREA = {"career": "work", "wealth": "money", "relationship": "relationships", "health": "health",
        "study": "learning", "movement": "travel"}
DIR_WORD = {"N": "north", "S": "south", "E": "east", "W": "west", "NE": "north-east",
            "NW": "north-west", "SE": "south-east", "SW": "south-west"}
GROUPS = [("比劫", ("比肩", "劫財", "劫财"), "Self and peers", "independence, competition, standing your ground"),
          ("食傷", ("食神", "傷官", "伤官"), "Expression", "creativity, speaking up, enjoyment"),
          ("財", ("正財", "正财", "偏財", "偏财"), "Money and results", "earning, managing, getting things done"),
          ("官殺", ("正官", "七殺", "七杀"), "Pressure and duty", "rules, deadlines, ambition under pressure"),
          ("印", ("正印", "偏印"), "Support and learning", "mentors, study, being looked after")]
PILLAR_LIFE = {"year": "family roots", "month": "work and parents", "day": "you and your partner",
               "hour": "children and later years"}


def and_join(xs):
    xs = list(xs)
    return "" if not xs else xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def strength_key(verdict: str) -> str:
    if "從" in verdict or "从" in verdict:
        return "follower"
    return "weak" if "弱" in verdict else "strong" if ("強" in verdict or "强" in verdict) else "balanced"


def signal(score) -> str:
    """Display bin of the engine's own strength score (owner-approved thresholds)."""
    a = abs(float(score or 0))
    return "strong" if a >= 1.5 else "moderate" if a >= 0.5 else "faint"


def _identity(p):
    dm = p["day_master"]; img, trait = STEM_IMAGE[dm]
    sk = strength_key(p["strength"]["verdict"]); med = p["yongshen"]["favourable"][0]
    return {"head": f"You are {img} in {SEASON[p['pillars']['month'][1]]}.",
            "sub": f"{trait}. You {STRENGTH[sk]['short']}, and what you need most is {MEDICINE[med]['need']}.",
            "signal": signal(p["strength"]["score"]),
            "why": (f"Day Master {dm} ({EN[STEM_EL[dm]]}) born in the {p['pillars']['month'][1]} month; strength "
                    f"{p['strength']['verdict']} (score {p['strength']['score']}); medicine {med} ({EN[med]}).")}


def _helps(p):
    fav = p["yongshen"]["favourable"]; m = MEDICINE[fav[0]]; rest = [EN[e] for e in fav[1:]]
    more = f" {and_join(rest)} {'helps' if len(rest) == 1 else 'help'} too." if rest else ""
    return {"el": fav[0], "head": f"{EN[fav[0]]} helps you most.", "means": f"It brings {m['gives']}.{more}",
            "todo": f"Wear and decorate with {m['colours']}; favour {m['acts']}.",
            "avoid": [EN[e] for e in p["yongshen"]["unfavourable"]],
            "why": f"用神 (useful elements): {' '.join(fav)}; avoid {' '.join(p['yongshen']['unfavourable'])}. {p.get('medicine_rank', '')}"}


def _year(p):
    ys = (p.get("windows") or {}).get("years") or []
    if not ys:
        return None
    y = ys[0]
    win = [AREA[k] for k in AREA if (y.get(k) or {}).get("flag") == "window"]
    cau = [AREA[k] for k in AREA if (y.get(k) or {}).get("flag") == "caution"]
    tail = ([f"a window for {and_join(win)}"] if win else []) + ([f"go carefully with {and_join(cau)}"] if cau else [])
    means = (tail[0][0].upper() + tail[0][1:] + (f"; {tail[1]}" if len(tail) > 1 else "") + ".") if tail \
        else "No single area is strongly switched on or off."
    return {"y": y["y"], "gz": y["gz"], "overall": y["overall"], "word": YEAR[y["overall"]]["word"],
            "head": YEAR[y["overall"]]["head"].format(y=y["y"]) + ".", "means": means,
            "why": f"Year {y['y']} {y['gz']}: overall {y['overall']} ({y['overall_zh']}). " +
                   "; ".join(f"{k} {y[k]['flag']}: {y[k]['note']}" for k in AREA if (y.get(k) or {}).get("flag", "quiet") != "quiet")}


def _actions(p):
    fav = p["yongshen"]["favourable"][0]; out = [f"Bring {EN[fav]} into the rooms where you spend hours: {MEDICINE[fav]['colours']}."]
    pl = {x["key"]: x for x in p.get("placements") or []}
    if "bed" in pl and "desk" in pl:   # owner convention 2026-10-10: say which way each thing faces
        out.append(f"Point your bed head {DIR_WORD[pl['bed']['dir']]}, and face {DIR_WORD[pl['desk']['dir']]} at your desk.")
    return out


def _balance(p):
    dm_el = STEM_EL[p["day_master"]]; fav = set(p["yongshen"]["favourable"]); med = p["yongshen"]["favourable"][0]
    weak = strength_key(p["strength"]["verdict"]) == "weak"; rows = []
    for h in sorted(p.get("health") or [], key=lambda h: -h["share"]):
        band = BAND.get(h["status"], h["status"]); note = ""
        if h["element"] == dm_el and band == "too much" and weak:
            note = "Your own element, and plentiful, but out of season, so it gives less strength than the number suggests."
        elif band == "too little" and h["element"] in fav:
            note = "You are short of the thing that helps you most."
        elif band == "about right" and h["element"] == med:
            note = "Enough to keep you balanced, but more of it is what helps you most."
        elif band == "too much" and h["element"] not in fav:
            note = "Already plenty; add no more."
        rows.append({"el": h["element"], "en": h["en"], "share": h["share"], "band": band,
                     "medicine": h["element"] == med, "note": note})
    return rows


def _strength(p):
    S = STRENGTH[strength_key(p["strength"]["verdict"])]
    return {"head": S["head"] + ".", "means": S["means"], "todo": S["todo"], "signal": signal(p["strength"]["score"]),
            "why": f"Strength verdict {p['strength']['verdict']}, score {p['strength']['score']}, support {p['strength'].get('support_ratio')}%."}


def _flows(p):
    er = p.get("element_relations")
    if not er:
        return None
    pr, rs = er["flows"]["pressure"], er["flows"]["resource"]
    if pr["share"] > rs["share"]:
        tail = "Pressure outweighs support, so pace yourself."
    elif rs["el"] in p["yongshen"]["unfavourable"]:
        tail = f"You already have more than enough {EN[rs['el']]}, so its support adds weight rather than help."
    else:
        tail = "Support holds the pressure, so you can take more on."
    return {"head": f"{EN[pr['el']]} presses on you hardest; {EN[rs['el']]} feeds you.",
            "means": f"{EN[pr['el']]} brings pressure ({pr['share']}%), {EN[rs['el']]} brings support ({rs['share']}%). {tail}",
            "why": f"生剋 flows: pressure {pr['el']} {pr['share']}%, resource {rs['el']} {rs['share']}%."}


def _decades(p):
    W = p.get("windows") or {}
    decs = [{"gz": d["gz"], "ages": d["ages"], "phase": d["phase"], "word": PHASE[d["phase"]]["word"],
             "glyph": PHASE[d["phase"]]["glyph"], "current": bool(d.get("current"))} for d in W.get("decades") or []]
    cur = next((d for d in W.get("decades") or [] if d.get("current")), None)
    if cur:
        w = PHASE[cur["phase"]]["word"].lower()
        now = {"head": f"You are in {'an' if w[0] in 'aeiou' else 'a'} {w} decade.",
               "means": PHASE[cur["phase"]]["means"] + f" This decade runs through ages {cur['ages']}.",
               "why": f"大運 {cur['gz']} (ages {cur['ages']}): phase {cur['phase']} ({cur['phase_zh']}), score {cur['score']}. " + "; ".join(cur.get("notes") or [])}
    elif decs:
        now = {"head": "Your first luck decade has not begun yet.",
               "means": f"It starts at age {str(decs[0]['ages']).split('–')[0].split('-')[0]}.", "why": ""}
    else:
        now = None
    return decs, now


def _makeup(p):
    ia = p.get("interactions") or []; kinds = {x["kind"] for x in ia}
    if any("沖" in k or "冲" in k for k in kinds):
        head, means = ("Parts of your life pull hard against each other.",
                       "Some of your pillars clash, so change tends to arrive through friction between home, work and family.")
    elif ia:
        head, means = ("Parts of your life rub quietly against each other.",
                       "No open clashes, but small frictions between your pillars wear on you over time. Name them and they lose their grip.")
    else:
        head, means = ("Your four pillars sit comfortably together.",
                       "No strong pulls between the parts of your life, so your energy is not spent on inner conflict.")
    pairs = [{"a": PILLAR_LIFE[x["pillars"][0]], "b": PILLAR_LIFE[x["pillars"][1]], "kind": x["kind"],
              "note": x["note"].split(" — ")[-1]} for x in ia[:5]]
    return {"head": head, "means": means, "pairs": pairs,
            "why": "Branch interactions: " + ("; ".join(f"{x['kind']} {x['pair']} ({x['pillars'][0]} and {x['pillars'][1]})" for x in ia) or "none")}


def _drives(p):
    pct = p.get("tengods_pct") or {}
    groups = sorted(({"zh": zh, "name": name, "gloss": gloss, "pct": round(sum(pct.get(g, 0) for g in gods), 1)}
                     for zh, gods, name, gloss in GROUPS), key=lambda g: -g["pct"])
    top = groups[0]
    return {"head": f"You are driven most by {top['name'].lower()}.", "means": f"Your chart leans toward {top['gloss']}.",
            "groups": groups, "why": "Ten-god shares: " + ", ".join(f"{k} {v}%" for k, v in pct.items())}


def _space(p):
    pl = {x["key"]: x for x in p.get("placements") or []}
    if not ("bed" in pl and "desk" in pl):
        return None
    marks = {}
    for key, label in (("bed", "Bed head"), ("desk", "Desk"), ("door", "Door")):
        if key in pl:
            marks.setdefault(pl[key]["dir"], []).append(label)
    return {"head": "Where to sleep and where to face.", "means": _actions(p)[1], "marks": marks,
            "why": f"八宅 placements for {p.get('gua', '')} ({p.get('group', '')}): bed head toward {pl['bed']['star']} "
                   f"({pl['bed']['dir']}), desk facing {pl['desk']['star']} ({pl['desk']['dir']})."}


def plain_reading(p: dict) -> dict:
    decades, decade_now = _decades(p)
    return {"identity": _identity(p), "helps": _helps(p), "year": _year(p), "actions": _actions(p),
            "balance": _balance(p), "strength": _strength(p), "flows": _flows(p),
            "decades": decades, "decade_now": decade_now,
            "years": [{"y": y["y"], "gz": y["gz"], "overall": y["overall"], "word": YEAR[y["overall"]]["word"]}
                      for y in (p.get("windows") or {}).get("years") or []],
            "makeup": _makeup(p), "drives": _drives(p), "space": _space(p)}
