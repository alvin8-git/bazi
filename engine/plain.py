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
band_word = lambda status: next((v for k, v in BAND.items() if status.startswith(k.split()[0])), "a little thin" if status.startswith("watch") else status)
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
    sk = strength_key(p["strength"]["verdict"]); med = p["yongshen"]["favourable"][0]; st = p["strength"]
    short = STRENGTH[sk]["short"]
    if sk == "weak" and ((st.get("parts") or {}).get("season_pts") or 0) < 0 and (st.get("support_ratio") or 0) >= 50:
        short = "are well backed but born out of season"   # the season, not a lack of support, sets the verdict
    elif sk == "weak" and ((st.get("parts") or {}).get("season_pts") or 0) > 0 and (st.get("root_ratio") or 0) < 10:
        short = "are in season but have few roots"
    return {"head": f"You are {img} in {SEASON[p['pillars']['month'][1]]}.",
            "sub": f"{trait}. You {short}, and what you need most is {MEDICINE[med]['need']}.",
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
        band = band_word(h["status"]); note = ""
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
            "makeup": _makeup(p), "drives": _drives(p), "space": _space(p), **plain_round2(p)}


# ---- round 2 (2026-10-10): four sides, and every engine conclusion as a plain card ---------------
# Drafted for owner review before commit. Same rules: fixed templates, slots from payload fields only.
SIDE = {"year": ("In your roots", "your roots"), "month": ("At work", "you at work"),
        "day": ("At home", "you at home"), "hour": ("In your later years", "your later years")}
GOD_ROLE = {
    "比肩": "Peers and equals stand beside you here.",
    "劫財": "Rivals and bold moves shape this part of life.",
    "劫财": "Rivals and bold moves shape this part of life.",
    "食神": "Ease, enjoyment and natural talent show here.",
    "傷官": "Sharp expression and a will to challenge show here.",
    "伤官": "Sharp expression and a will to challenge show here.",
    "正財": "Steady earning and careful management show here.",
    "正财": "Steady earning and careful management show here.",
    "偏財": "Deals, windfalls and generosity show here.",
    "偏财": "Deals, windfalls and generosity show here.",
    "正官": "Rules, rank and responsibility shape this part of life.",
    "七殺": "Pressure and hard challenges shape this part of life, and make you decisive.",
    "七杀": "Pressure and hard challenges shape this part of life, and make you decisive.",
    "正印": "Mentors, learning and protection support you here.",
    "偏印": "Unusual knowledge and solitary study support you here.",
}
GOD_GIST = {"比肩": "companionship", "劫財": "competition", "劫财": "competition", "食神": "ease and enjoyment",
            "傷官": "spark and challenge", "伤官": "spark and challenge", "正財": "steady provision", "正财": "steady provision",
            "偏財": "generosity and deals", "偏财": "generosity and deals", "正官": "order and duty", "七殺": "pressure and drive",
            "七杀": "pressure and drive", "正印": "support and care", "偏印": "unusual insight"}
POLE = {  # personality axis pole → (one-word trait, plain sentence)
    "reserved": ("reserved", "You keep your thoughts to yourself until they are ready."),
    "expressive": ("expressive", "You say what you think and show what you make."),
    "deliberate": ("deliberate", "You take your time before you act."),
    "decisive": ("decisive", "You act fast, and best under pressure."),
    "challenges rules": ("independent-minded", "You question rules and push against them."),
    "works within structure": ("disciplined", "You work well inside rules and rank."),
    "pragmatic": ("practical", "You think in practical terms."),
    "reflective": ("reflective", "You think deeply and enjoy theory."),
    "contained": ("private", "You keep your feelings close."),
    "direct & open": ("open", "You show your feelings openly."),
}
NEG_STARS = {"劫煞", "空亡", "災煞", "亡神", "羊刃", "孤辰", "寡宿"}
EL_ROOM = {"木": ("east", "plants, timber and green accents"), "火": ("south", "warm light and a red or orange accent"),
           "土": ("centre", "ceramics, stone and yellow or brown tones"), "金": ("west", "metal frames and white or gold"),
           "水": ("north", "glass, a water feature, or blue and black")}
ANIMAL = dict(zip("子丑寅卯辰巳午未申酉戌亥", ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]))
BAND_KEY = lambda band: "strong" if band.startswith("prominent") else "weak" if band.startswith("needs") else "even"


def _sides(p):
    pal = {x["key"]: x for x in (p.get("palaces") or {}).get("pillars") or []}
    out = []
    for k in ("year", "month", "day", "hour"):
        gz = p["pillars"][k]; stem, br = gz[0], gz[1]; P = pal.get(k, {})
        img = STEM_IMAGE[stem][0]; prefix, area = SIDE[k]
        if k == "day":   # the identity sentence owns the birth season; the home card is you, unqualified
            role, head = "This is you, the Day Master, at the centre of the whole chart.", f"{img[0].upper() + img[1:]}, at your most yourself."
            line = f"{prefix} you are {img}, at your most yourself."
        else:
            role = GOD_ROLE.get(P.get("stem_god") or (p.get("ten_gods") or {}).get(k, ""), "")
            head = f"{img[0].upper() + img[1:]} in {SEASON[br]}."
            line = f"{prefix} you are {img} in {SEASON[br]}."
        out.append({"key": k, "area": area, "stem": stem, "head": head, "line": line,
                    "role": role, "ages": (P.get("ages") or "").replace("ages ", ""),
                    "why": f"{P.get('zh', k)} {gz}: stem {stem}, branch {br}. {P.get('line', '')}"})
    return out


def _stars(p):
    S = p.get("shensha") or []
    good = next((s for s in S if s["star"] not in NEG_STARS), None)
    bad = next((s for s in S if s["star"] in NEG_STARS), None)
    def parts(s):
        name, _, gist = s["meaning"].partition(" — ")
        return name, (gist or s["meaning"]).split(";")[0]
    out = []
    if good:
        name, gist = parts(good)
        out.append({"head": f"You carry a helpful star: {name}.", "means": f"{gist[0].upper() + gist[1:]}. It sits in {and_join([SIDE[x][1] for x in good['pillars']])}.",
                    "why": f"{good['star']} in the {', '.join(good['pillars'])} pillar. {good['meaning']} ({good.get('source_ref', '')})."})
    if bad:
        name, gist = parts(bad)
        out.append({"head": f"One star asks for care: {name}.", "means": f"{gist[0].upper() + gist[1:]}. It sits in {and_join([SIDE[x][1] for x in bad['pillars']])}.",
                    "why": f"{bad['star']} in the {', '.join(bad['pillars'])} pillar. {bad['meaning']} ({bad.get('source_ref', '')})."})
    return out


def _health(p):
    H = p.get("health") or []
    hi = next((h for h in H if h["status"].startswith("excess")), None)
    lo = [h for h in H if h["status"].startswith("weak")]
    if not hi and not lo:
        return {"head": "No organ system is flagged.", "means": "All five elements sit in range. This is a traditional pairing, not medical advice.", "why": ""}
    main = hi or lo[0]
    org = lambda h: and_join(h["organs"].split(", "))
    body, _, mood = main["aspects"].partition("; ")
    watch = and_join(body.split(", ")) + (f", and watch for {mood}" if mood else "")
    head = f"Look after your {org(main)}."
    means = (f"{main['en']} runs high in your chart, which traditionally strains the {org(main)}; notice {watch}. "
             if hi else f"{main['en']} runs low in your chart; the {org(main)} want support, so notice {watch}. ")
    means += "This is a traditional pairing, not medical advice."
    rest = [h for h in lo if h is not main]
    return {"head": head, "means": means,
            "todo": (f"Support your {', and your '.join(org(h) for h in rest)} too; your chart is short of them." if rest else None),
            "why": "; ".join(f"{h['en']} {h['share']}% ({h['status']}): {h['organs']}" for h in H)}


def _personality(p):
    axes = [a for a in p.get("personality") or [] if a.get("zone") in ("left", "right")]
    traits = [POLE[a["poles"][a["zone"]]["en"]] for a in axes if a["poles"][a["zone"]]["en"] in POLE]
    if not traits:
        return None
    words = [t[0] for t in traits]
    return {"head": f"You are {and_join(words[:2])}.", "means": " ".join(t[1] for t in traits[:4]),
            "why": "; ".join(f"{a['axis']}: {a['verdict']} ({a.get('basis', '')})" for a in axes)}


def _work(p):
    top = ((p.get("careers") or {}).get("top") or [None])[0]
    lc = lambda r: r if r.split()[0].isupper() and len(r.split()[0]) > 1 else r[0].lower() + r[1:]
    roles = [lc(r["role"]).replace(" & ", " and ") for r in ((p.get("career_roles") or {}).get("top") or [])[:3]]
    ind = p.get("industries") or {}
    fav = [x["industries"].split(",")[0].strip() for x in ind.get("favourable") or []]
    avoid = [x["industries"].split(",")[0].strip() for x in ind.get("avoid") or []]
    if not top:
        return None
    return {"head": f"You do best in {top['en'].lower().replace('&', 'and')}.",
            "means": (f"Roles that suit you now: {and_join(roles)}. " if roles else "")
                     + (f"Fields that recharge you: {and_join(fav)}." if fav else ""),
            "todo": f"Treat {and_join(avoid)} as harder going, not off limits." if avoid else None,
            "why": f"Top archetype {top['en']} ({top['score']} pts): " + "; ".join(top["reasons"])}


def _money(p):
    W = next((d for d in p.get("domains") or [] if d["key"] == "wealth"), None)
    if not W:
        return None
    head = {"strong": "Money comes to you readily.", "even": "Money comes through steady effort.",
            "weak": "Money needs deliberate building."}[BAND_KEY(W["band"])]
    V = (p.get("palaces") or {}).get("vault") or {}
    br = V.get("state", "").split(" opens in ")[-1][:1] if V.get("present") and not V.get("open") else ""
    nxt = next((y for y in range(2026, 2040) if "子丑寅卯辰巳午未申酉戌亥"[(y - 4) % 12] == br), None) if br else None
    means = (f"You have a store of wealth that opens in {ANIMAL.get(br, br)} years ({br}); the next is {nxt}. Those are your years to save and build." if br
             else "Your wealth store is open, so money moves freely; keep a buffer." if V.get("present")
             else "There is no fixed wealth store in your chart, so build one on purpose.")
    return {"head": head, "means": means, "why": f"Wealth domain {W['score']} ({W['band']}). Vault: {V.get('state', 'absent')}."}


def _love(p):
    D = {d["key"]: d for d in p.get("domains") or []}
    st, at = D.get("stability"), D.get("attraction")
    if not st:
        return None
    head = {"strong": "Your relationships hold steady.", "even": "Your relationships stay steady when tended.",
            "weak": "Lasting relationships need deliberate care."}[BAND_KEY(st["band"])]
    pull = {"strong": "You draw people easily", "even": "You draw people at an even pace",
            "weak": "Attraction builds slowly"}[BAND_KEY(at["band"])] if at else ""
    sp = p.get("spouse_reading") or {}
    day = next((x for x in (p.get("palaces") or {}).get("pillars") or [] if x["key"] == "day"), {})
    gist = GOD_GIST.get((day.get("hidden") or [""])[0], "")
    return {"head": head, "means": (pull + ". " if pull else "") + (f"Your partner tends to bring {gist}." if gist else ""),
            "todo": "Keep shared routines and say the quiet things out loud." if BAND_KEY(st["band"]) == "weak" else None,
            "why": " ".join(x for x in (sp.get("star_line"), sp.get("palace_line")) if x)}


def _next_ten(p):
    Y = (p.get("windows") or {}).get("years") or []
    dims = [k for k in AREA if Y and k in Y[0]]
    if not Y:
        return None
    best = max(Y, key=lambda y: sum((y.get(k) or {}).get("flag") == "window" for k in dims))
    worst = max(Y, key=lambda y: sum((y.get(k) or {}).get("flag") == "caution" for k in dims))
    win = [AREA[k] for k in dims if (best.get(k) or {}).get("flag") == "window"]
    cau = [AREA[k] for k in dims if (worst.get(k) or {}).get("flag") == "caution"]
    return {"head": f"Push in {best['y']}; protect {worst['y']}." if cau else f"Push in {best['y']}.",
            "means": (f"{best['y']} opens windows for {and_join(win)}." if win else f"{best['y']} is your strongest year ahead.")
                     + (f" {worst['y']} asks for care with {and_join(cau)}." if cau else ""),
            "why": f"{best['y']} {best['gz']}: {best['overall']}; {worst['y']} {worst['gz']}: {worst['overall']}."}


def _months(p):
    RH = ((p.get("strategy") or {}).get("s5") or {}).get("rhythm") or []
    good = [r for r in RH if r.get("cls") == "good"]
    if not RH:
        return None
    order = [r["mon"] for r in RH]; idx = sorted(order.index(r["mon"]) for r in good); runs = []; i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and idx[j + 1] == idx[j] + 1:
            j += 1
        runs.append(order[idx[i]] if i == j else f"{order[idx[i]]}–{order[idx[j]]}"); i = j + 1
    els = and_join(sorted({EN[r["el"]] for r in good}))
    return {"head": f"Your best months: {and_join(runs)}." if runs else "No month carries your medicine.",
            "means": f"They carry {els}, which {'helps' if len({r['el'] for r in good}) == 1 else 'help'} you. Keep the other months for steady work." if runs else "Pace the whole year evenly.",
            "why": "Month by month: " + ", ".join(f"{r['mon']} {r['br']} {r['el']} {r['cls']}" for r in RH)}


def _days(p):
    D = p.get("daily") or {}; B, W = D.get("best"), D.get("worst")
    if not B and not W:
        return None
    MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    day = lambda d: f"{int(d[8:10])} {MON[int(d[5:7]) - 1]}"
    acts = lambda xs: "most things" if len(xs) >= 5 else and_join(list(xs)[:3])
    return {"head": f"Your next good day: {day(B['date'])}." if B else "No clear good day this month.",
            "means": (f"Good for {acts(B['for'])}. " if B else "") + ((f"Hold off on big decisions on {day(W['date'])}." if len(W["avoid"]) >= 5 else f"On {day(W['date'])}, avoid {acts(W['avoid'])}.") if W and W.get("avoid") else ""),
            "why": (f"Best {B['date']} {B['gz']} ({B['officer']} day). " if B else "") + (f"Worst {W['date']} {W['gz']}: {W.get('why', '')}." if W else "")}


def _room(p):
    fav = p["yongshen"]["favourable"][0]; side, what = EL_ROOM[fav]
    return {"head": f"Put {EN[fav]} on the {side} side of your main room.", "means": f"Use {what}.",
            "why": f"Medicine {fav} ({EN[fav]}) placed by its direction."}


def _afflictions(p):
    A = p.get("afflictions") or {}
    if not A:
        return None
    ts, sp, ss = A["taisui"]["dir"], A["suipo"]["dir"], A["sansha"]["dirs"]
    hits = A.get("collisions") or []
    return {"head": f"Leave the {DIR_WORD[ts]} and {DIR_WORD[sp]} undisturbed this year.",   # owner 2026-10-10: chart directions win
            "means": f"Do not renovate or dig there, and take the same care on the {and_join([DIR_WORD[d] for d in ss])}.",
            "todo": "Your bed and desk directions still hold; this year only asks you not to build or dig on those sides." if hits else None,
            "why": " ".join(h["note"] for h in hits) or "None of this year's afflictions sits on your four favourable sectors."}


def plain_round2(p: dict) -> dict:
    return {"sides": _sides(p), "stars": _stars(p), "health": _health(p), "personality": _personality(p),
            "work": _work(p), "money": _money(p), "love": _love(p), "next_ten": _next_ten(p),
            "months": _months(p), "days": _days(p), "room": _room(p), "afflict": _afflictions(p)}
