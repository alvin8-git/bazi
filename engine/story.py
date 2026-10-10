"""Story layer for the reading page (round 3, 2026-10-10; templates in review).

Each chapter is up to three short paragraphs (what is true, why, what to do) plus an optional
"if you do one thing" line. Every sentence is a fixed template whose slots come from payload
fields, and carries the ids of the evidence it rests on; the page turns those ids into numbered
markers that open the figure, rule or citation in place. Same payload in, same text out.
"""
from __future__ import annotations

from .plain import (ANIMAL, AREA, BAND_KEY, DIR_WORD, EL_ROOM, EN, MEDICINE, NEG_STARS, POLE, SEASON,
                    STEM_EL, and_join, strength_key)

GOD_NOUN = {"比肩": "peers and self-reliance", "劫財": "rivals and bold moves", "劫财": "rivals and bold moves",
            "食神": "ease and natural talent", "傷官": "sharp expression and challenge", "伤官": "sharp expression and challenge",
            "正財": "steady earning", "正财": "steady earning", "偏財": "deals and opportunity", "偏财": "deals and opportunity",
            "正官": "rules and responsibility", "七殺": "pressure and ambition", "七杀": "pressure and ambition",
            "正印": "mentors and learning", "偏印": "unusual knowledge and solitary study"}
ROLE = {"output": "expression: what you make, say and show", "resource": "support: the people, learning and care that feed you",
        "wealth": "results: earning and getting things done", "pressure": "structure: discipline and responsibility",
        "peer": "allies: friends, partners and teams"}
PHASE_ADJ = {"growth": "growth", "consolidation": "gathering", "transition": "changing", "corrective": "repairing"}
PHASE_RANK = {"growth": 3, "consolidation": 2, "transition": 1, "corrective": 0}
LU = dict(zip("甲乙丙丁戊己庚辛壬癸", "寅卯巳午巳午申酉亥子"))   # 祿: each stem's own station
NUM = dict(enumerate("zero one two three four five six seven eight nine ten".split()))
DOMAIN = {"attraction": "love and attraction", "stability": "relationship stability", "career": "career",
          "wealth": "money", "learning": "learning", "health": "health and stamina"}
PRIORITY = {   # lowest life area, when it trails the strongest by 40 points or more
    "health": "So the risk is your body, not your ambitions: protect your health first.",
    "wealth": "So money is the area to build on purpose, not leave to chance.",
    "stability": "So your relationships are where steady care pays off most.",
    "attraction": "So let people come to you through shared work rather than chasing them.",
    "career": "So give your working life a clear structure before you add more to it.",
    "learning": "So learn by doing, in short steps, rather than long courses.",
}
HEALTH_EV = "health"


def voice_of(age):
    """Four voices (owner 2026-10-10): child under 13, teen 13 to 17, adult, senior 65 and over."""
    if age is None: return "adult"
    return "child" if age < 13 else "teen" if age < 18 else "senior" if age >= 65 else "adult"


AREAS_FOR = {"child": {"learning", "health"}, "teen": {"learning", "health", "career"},
             "adult": {"attraction", "stability", "career", "wealth", "learning", "health"},
             "senior": {"stability", "wealth", "learning", "health"}}
PRIORITY_BY_VOICE = {
    "child": {"health": "So protect sleep, food and play first.", "learning": "So keep learning playful and in short steps."},
    "teen": {"health": "So protect sleep and exercise before anything else.", "career": "So build steady study habits before adding more."},
    "senior": {"health": "So health comes first now: pace yourself and keep regular check-ups.",
               "wealth": "So keep what you have safe rather than chasing more.",
               "stability": "So time with the people closest to you pays off most."},
}
ACTS_CHILD = {"火": "sunlight, outdoor play and active games", "水": "good sleep, swimming and quiet time",
              "木": "time outdoors, growing things and trying new skills", "土": "regular meals, routine and a calm home",
              "金": "tidy routines, music practice and finishing tasks"}
ACTS_SENIOR = {"火": "morning sunlight, gentle exercise and good company", "水": "rest, warmth and time near water",
               "木": "walks among trees, light stretching and learning something new", "土": "regular meals, routine and home comforts",
               "金": "order, calm breathing and finishing what you start"}
ONE_THING = {
    "child": {"weak": "If you do one thing: protect sleep and downtime, and keep the schedule light.",
              "strong": "If you do one thing: give that energy a sport, an instrument or a project."},
    "teen": {"weak": "If you do one thing: protect sleep, and do not overload the timetable.",
             "strong": "If you do one thing: give that energy a sport, a craft or a team."},
    "adult": {"weak": "If you do one thing: guard your recovery time, and drop a commitment before you add one.",
              "strong": "If you do one thing: keep a demanding project running, so your strength has somewhere to go."},
    "senior": {"weak": "If you do one thing: pace your days, and rest before you are tired.",
               "strong": "If you do one thing: keep a steady purpose, such as a craft, a garden or helping family."},
}
PHASE_BY_VOICE = {
    "child": {"growth": "A good decade to grow, learn and try new things.", "consolidation": "A steady decade: routines and good habits pay off.",
              "transition": "Expect changes at home or school; keep routines steady.", "corrective": "A decade for care: protect health and keep home calm."},
    "teen": {"growth": "A good decade to learn and try new things.", "consolidation": "A steady decade: good habits pay off.",
             "transition": "Expect changes at home or school; keep routines steady.", "corrective": "A decade for care: protect health and keep habits steady."},
    "senior": {"growth": "A kind decade: good for health, family and the things you care about.",
               "consolidation": "A steady decade: keep routines and reserves.",
               "transition": "Expect change at home; keep things simple and close.",
               "corrective": "A decade for care: protect health and keep close ties near."},
}
AREA_BY_VOICE = {"child": {"career": "schoolwork", "wealth": None, "relationship": None},
                 "teen": {"career": "school and work", "wealth": None, "relationship": None},
                 "senior": {"career": "commitments"}}
STAR_GIST = {   # one plain line per common star; the engine's own gloss is the fallback
    "天乙貴人": "so helpful people appear at the moments that matter", "天乙贵人": "so helpful people appear at the moments that matter",
    "太極貴人": "a pull toward philosophy and deep study", "太极贵人": "a pull toward philosophy and deep study",
    "華蓋": "a taste for solitude, depth and the arts", "华盖": "a taste for solitude, depth and the arts",
    "文昌": "so study and exams tend to go well", "學堂": "the mark of a natural learner", "学堂": "the mark of a natural learner",
    "桃花": "charm that draws people in", "驛馬": "movement, travel and relocation", "驿马": "movement, travel and relocation",
    "將星": "natural authority among others", "将星": "natural authority among others", "祿神": "the means to a steady income", "禄神": "the means to a steady income",
    "天德": "protection that softens hard years", "月德": "protection that softens hard years", "金輿": "comfort and support from others", "金舆": "comfort and support from others",
    "空亡": "so the part of life it sits in can feel empty until a year wakes it", "劫煞": "so guard what you own and avoid needless risk",
    "羊刃": "a strong will that needs a check on impulsiveness", "災煞": "so take care with accidents and hasty moves", "灾煞": "so take care with accidents and hasty moves",
    "亡神": "so keep plans and money matters private", "孤辰": "a streak of independence and solitude", "寡宿": "a streak of independence and solitude",
}


def S(t, *ev):
    return {"t": t, "ev": list(dict.fromkeys(ev))}


cap = lambda s: s[:1].upper() + s[1:]


def ljoin(xs):   # names that already contain "and" take an Oxford comma so the list still parses
    xs = list(xs)
    return and_join(xs) if not any(" and " in x for x in xs) or len(xs) < 2 else ", ".join(xs[:-1]) + ", and " + xs[-1]


def _age(p, year):
    """Age on today's date in the reading year (a birthday not yet reached this year counts one less)."""
    import datetime as _dt
    try:
        b = _dt.date.fromisoformat(str(p.get("effective_time", ""))[:10])
    except ValueError:
        return None
    today = _dt.date.today(); ref = today if today.year == year else _dt.date(year, 7, 1)
    return year - b.year - ((ref.month, ref.day) < (b.month, b.day))


def _year_now(p):
    return (p.get("afflictions") or {}).get("year") or (((p.get("windows") or {}).get("years") or [{}])[0].get("y")) or 2026


def _ages(d):
    a, _, b = str(d["ages"]).replace("-", "–").partition("–")
    return int(a), int(b or a)


# ---- chapters ---------------------------------------------------------------------------------
def _makeup(p, kid):
    pct = p.get("tengods_pct") or {}
    ranked = sorted(pct.items(), key=lambda kv: -kv[1])
    p1 = []
    if len(ranked) >= 6 and ranked[0][1] - ranked[3][1] < 3:
        p1.append(S("Your chart is unusually even: no single role leads, and you carry a little of everything.", "gods"))
    elif ranked:
        (g1, v1), *rest = ranked
        n1 = GOD_NOUN.get(g1, g1)
        if rest and rest[0][1] == v1:   # a tie is a shared lead, not "followed by"
            p1.append(S(f"{cap(n1)} and {GOD_NOUN.get(rest[0][0], rest[0][0])} share the lead in your chart, at {v1:g}% each.", "gods"))
        else:
            tail = f", followed by {GOD_NOUN.get(rest[0][0], rest[0][0])} at {rest[0][1]:g}%" if rest else ""
            p1.append(S(f"{cap(n1)} {'lead' if ' and ' in n1 else 'leads'} your chart at {v1:g}%{tail}.", "gods"))
    pal = {x["key"]: x for x in (p.get("palaces") or {}).get("pillars") or []}
    y, m = (pal.get("year") or {}).get("stem_god"), (pal.get("month") or {}).get("stem_god")
    if y in GOD_NOUN and m in GOD_NOUN:
        work = "will set the climate of your working life" if kid else "set the climate of your working life"
        p1.append(S(f"{cap(GOD_NOUN[y])} shaped your early years, and {GOD_NOUN[m]} {work}.", "pillars"))

    axes = [a for a in p.get("personality") or [] if a.get("zone") in ("left", "right")]
    p2 = [S(POLE[a["poles"][a["zone"]]["en"]][1], "personality") for a in axes if a["poles"][a["zone"]]["en"] in POLE][:3]

    p3 = []
    stars = p.get("shensha") or []
    good = next((s for s in stars if s["star"] not in NEG_STARS), None)
    bad = next((s for s in stars if s["star"] in NEG_STARS), None)
    for s, lead in ((good, "A helpful star sits in your chart"), (bad, "One star asks for care")):
        if s:
            name, _, gist = s["meaning"].partition(" — ")
            gist = STAR_GIST.get(s["star"], (gist or s["meaning"]).split(";")[0])
            p3.append(S(f"{lead}: the {name}, {gist}.", "stars"))
    ia = p.get("interactions") or []
    hard = sum(1 for x in ia if any(k in x["kind"] for k in ("沖", "冲", "刑")))
    if hard >= 3:
        p3.append(S("Your pillars clash more than most, so change in one part of your life tends to shake the others; "
                    "steady routines are worth more to you than to most people.", "interactions"))
    elif any(any(k in x["kind"] for k in ("沖", "冲")) for x in ia):
        p3.append(S("Some of your pillars clash, so change tends to arrive through friction between home, work and family.", "interactions"))
    elif any("刑" in x["kind"] for x in ia):
        p3.append(S("Some of your pillars punish one another, so strain tends to build slowly inside your own circle; name it early.", "interactions"))
    elif ia and all("合" in x["kind"] for x in ia):
        p3.append(S("Your pillars mostly combine, so the parts of your life tend to back each other up.", "interactions"))
    elif ia:
        p3.append(S("Your pillars rub quietly against each other: small frictions, but no open clash.", "interactions"))
    else:
        p3.append(S("Your four pillars sit comfortably together, so little of your energy goes on inner conflict.", "interactions"))
    return {"paras": [x for x in (p1, p2, p3) if x], "chart_after": 0}


def _balance(p, v):
    dm_el = STEM_EL[p["day_master"]]; st = p["strength"]; sk = strength_key(st["verdict"])
    fav, unfav = p["yongshen"]["favourable"], p["yongshen"]["unfavourable"]; med = fav[0]
    H = sorted(p.get("health") or [], key=lambda h: -h["share"])
    fl = (p.get("element_relations") or {}).get("flows") or {}
    season = (st.get("parts") or {}).get("season_pts", 0) or 0
    p1, p2, p3 = [], [], []
    if H:
        own = ", and it is your own element" if H[0]["element"] == dm_el else ""
        p1.append(S(f"{H[0]['en']} is the heaviest element in your chart, at {H[0]['share']:g}%{own}.", "elements"))
    pr, rs = fl.get("pressure"), fl.get("resource")
    if sk == "weak" and pr and rs and pr["share"] > rs["share"]:
        p1.append(S(f"The pressure on you, from {EN[pr['el']]}, outweighs the support that feeds you, from {EN[rs['el']]}, "
                    "which is why the reading calls you weak.", "flows", "strength"))
    elif sk == "weak":
        p1.append(S("The reading calls you weak.", "strength"))
    elif sk == "strong" and pr and rs and pr["share"] > rs["share"]:
        p1.append(S(f"The reading calls you strong, even though the pressure from {EN[pr['el']]} outweighs the support from "
                    f"{EN[rs['el']]}: your own element carries the load.", "strength", "flows"))
    elif sk == "strong":
        p1.append(S("You have more support than you spend, which is why the reading calls you strong.", "strength"))
    elif sk == "balanced":
        p1.append(S("Support and pressure roughly cancel out, so the reading calls you balanced.", "strength"))
    else:
        p1.append(S("Your chart gives itself to its strongest element, so you do best by going with it.", "strength"))

    # why: the strength paradox, then the scarce element and the role it plays
    if sk == "weak" and season < 0:
        p2.append(S(f"You were born in {SEASON[p['pillars']['month'][1]]}, a season that works against {EN[dm_el]}, "
                    f"so the {EN[dm_el]} you have gives you less strength than the number suggests.", "strength"))
        med_high = any(h["element"] == med and h["status"].startswith("excess") for h in H)
        if (st.get("support_ratio") or 0) >= 50 and not med_high:
            p2.append(S(f"You are not short of backing; you are short of {MEDICINE[med]['need']}.", "strength", "medicine"))
    elif sk == "weak" and (st.get("root_ratio") or 0) < 10:
        p2.append(S("You were born in a helpful season, but your own element has few roots in the branches, "
                    "so that help does not hold.", "strength"))
    elif sk == "strong":
        p2.append(S("So what helps you is not more of what you have, but outlets for it.", "strength", "medicine"))
    role = next((k for k, f in fl.items() if f.get("el") == med), None)
    scarce = H[-1]["element"] if H else None
    if scarce == med:
        p2.append(S(f"{EN[med]} is both the element you have least of and the one that helps you most.", "elements", "medicine"))
    else:
        p2.append(S(f"Of the elements that help you, {EN[med]} matters most.", "medicine"))
    if role in ROLE:
        p2.append(S(f"For {EN[dm_el]}, {EN[med]} is {ROLE[role]}.", "flows"))
        exp = next((a for a in p.get("personality") or [] if a["axis"].endswith("Expression")), None)
        if role == "output" and exp and exp.get("zone") == "left":
            p2.append(S("Your personality reading says you hold your output back, so what you most need is a way "
                        "for your energy to come out.", "personality"))

    m = MEDICINE[med]; acts = (ACTS_CHILD if v == "child" else ACTS_SENIOR if v == "senior" else {}).get(med, m["acts"])
    p3.append(S(f"In practice: {acts}, with {m['colours']} in the rooms where you spend hours.", "medicine"))
    if unfav:
        p3.append(S(f"{and_join([EN[e] for e in unfav])} take more than they give, so go easy on them.", "medicine"))
    hi = next((h for h in H if h["status"].startswith("excess")), None)
    lo = [h for h in H if h["status"].startswith("weak")]
    if hi or lo:
        bits = ([f"{hi['en']} runs high"] if hi else []) + ([f"{and_join([h['en'] for h in lo])} run{'s' if len(lo) == 1 else ''} low"] if lo else [])
        organs = and_join([(hi or lo[0])["organs"].split(", ")[0]] + [h["organs"].split(", ")[0] for h in lo if h is not (hi or lo[0])])
        p3.append(S(f"Your body follows the same shape: {' and '.join(bits)}, so look after your {organs}. "
                    "This is a traditional pairing, not medical advice.", HEALTH_EV))
    one = S(ONE_THING[v][sk], "strength") if sk in ONE_THING[v] else None
    return {"paras": [x for x in (p1, p2, p3) if x], "chart_after": 1, "one": one}


def _drives(p, v):
    kid = v in ("child", "teen")
    D = sorted([d for d in p.get("domains") or [] if d["key"] in AREAS_FOR[v]], key=lambda d: -d["score"])
    p1, p2, p3 = [], [], []
    one = None
    if D:
        top, low = D[0], D[-1]
        nm = lambda d: DOMAIN.get(d["key"], d["en"].lower())
        p1.append(S(f"Your strongest life area is {nm(top)} ({top['score']} of 100); your weakest is {nm(low)} ({low['score']}).", "domains"))
        pri = {**PRIORITY, **PRIORITY_BY_VOICE.get(v, {})}
        if top["score"] - low["score"] >= 40 and low["key"] in pri:
            p1.append(S(pri[low["key"]], "domains"))
    C = (p.get("careers") or {})
    top3 = [c["en"].lower().replace("&", "and") for c in (C.get("top") or [])[:3]]
    if top3:
        lead = {"child": "Strengths to grow into later point toward", "teen": "Later on, the work that suits you best is",
                "senior": "For work, volunteering or mentoring, you suit"}.get(v, "You do best in")
        p2.append(S(f"{lead} {top3[0]}" + (f", then {ljoin(top3[1:])}." if top3[1:] else "."), "work"))
    av = [c["en"].lower().replace("&", "and") for c in C.get("avoid") or []]
    if av and v != "child":
        p2.append(S(f"{cap(ljoin(av))}{',' if len(av) > 1 else ''} {'is' if len(av) == 1 else 'are'} harder going for this chart, not off limits.", "work"))
    V = (p.get("palaces") or {}).get("vault") or {}
    ys = {y["y"]: y for y in (p.get("windows") or {}).get("years") or []}
    if v in ("child", "teen"):
        pass   # no money advice under 18 (owner 2026-10-10)
    elif V.get("present") and not V.get("open"):
        br = V.get("state", "").split(" opens in ")[-1][:1]
        nxt = next((y for y in range(_year_now(p), _year_now(p) + 13) if "子丑寅卯辰巳午未申酉戌亥"[(y - 4) % 12] == br), None)
        if nxt:
            also = (", a good year to put your affairs in order" if v == "senior"
                    else ", which is also a window for money" if (ys.get(nxt, {}).get("wealth") or {}).get("flag") == "window" else "")
            p2.append(S(f"You have a store of wealth that opens in {ANIMAL.get(br, br)} years; the next is {nxt}{also}.", "money", "years"))
    elif V.get("present"):
        p2.append(S("Your wealth store is open, so money moves freely; keep a buffer.", "money"))
    else:
        p2.append(S("Your chart has no store for wealth, so keep savings simple and safe rather than chasing returns." if v == "senior" else
                    "Your chart has no store for wealth, so money flows rather than stays: " + ("when you start earning, " if kid else "")
                    + "save automatically rather than counting on windfalls.", "money"))
    dom = {d["key"]: d for d in p.get("domains") or []}
    if not kid and "stability" in dom:
        st = BAND_KEY(dom["stability"]["band"])
        p3.append(S({"strong": "Your relationships hold steady.", "even": "Your relationships stay steady when tended.",
                     "weak": "Lasting relationships need deliberate care."}[st], "domains"))
        day = next((x for x in (p.get("palaces") or {}).get("pillars") or [] if x["key"] == "day"), {})
        g = (day.get("hidden") or [""])[0]
        if g in GOD_NOUN:
            p3.append(S(f"Your partner tends to bring {GOD_NOUN[g]}.", "domains"))
        if st == "weak":
            p3.append(S("Keep shared routines, and say the quiet things out loud.", "domains"))
    elif v == "teen":
        p3.append(S("Relationships are a theme for later in life, so this reading leaves them for now.", "domains"))
    return {"paras": [x for x in (p1, p2, p3) if x], "chart_after": 0, "one": one}


def _timing(p, v):
    AREA_V = {**AREA, **AREA_BY_VOICE.get(v, {})}
    W = p.get("windows") or {}; decs = W.get("decades") or []; Y = W.get("years") or []
    now = _year_now(p); age = _age(p, now)
    turn = lambda y: f" (the year you turn {y - (now - age)})" if age is not None and age < 30 else ""
    p1, p2, p3 = [], [], []
    i = next((k for k, d in enumerate(decs) if d.get("current")), None)
    if i is None and decs:
        p1.append(S(f"Your first luck decade starts at age {_ages(decs[0])[0]}.", "decades"))
    elif i is not None:
        d = decs[i]; ph = d["phase"]; a = i; b = i
        while a > 0 and decs[a - 1]["phase"] == ph:
            a -= 1
        while b + 1 < len(decs) and decs[b + 1]["phase"] == ph:
            b += 1
        n, word = b - a + 1, PHASE_ADJ[ph]
        if n == 1:
            lead = f"You are in a {word} decade, ages {d['ages']}."
        elif i == b:
            lead = f"You are in the last of {NUM.get(n, n)} {word} decades in a row, ages {d['ages']}."
        elif i == a:
            lead = f"You are in the first of {NUM.get(n, n)} {word} decades in a row, ages {d['ages']}."
        else:
            lead = f"You are in the middle of {NUM.get(n, n)} {word} decades in a row, ages {d['ages']}."
        from .plain import PHASE
        p1.append(S(lead + " " + PHASE_BY_VOICE.get(v, {}).get(ph, PHASE[ph]["means"]), "decades"))
        lu = next((k for k, x in enumerate(decs) if x["gz"][1] == LU[p["day_master"]]), None)
        if lu is not None and decs[lu]["phase"] in ("growth", "consolidation"):
            if lu < i:
                p1.append(S(f"Your chart's turning point came at ages {decs[lu]['ages']}, when your own element arrived.", "decades"))
            elif lu == i:
                p1.append(S("This decade is your chart's turning point: your own element arrives in it.", "decades"))
            else:
                p1.append(S(f"Your own element arrives at ages {decs[lu]['ages']}, the turning point of your chart.", "decades"))
        if i + 1 < len(decs) and age is not None:
            nx = decs[i + 1]; start = _ages(nx)[0]; left = max(start - age, 1)
            one = left == 1; yrs = "year" if one else "years"; left = NUM.get(left, left); dn, up = PHASE_RANK[nx["phase"]], PHASE_RANK[ph]
            if dn > up and v == "senior":
                p2.append(S(f"{'Within a year' if one else f'In about {left} {yrs}'} the climate turns: the next decade, from {start}, "
                            f"is a {PHASE_ADJ[nx['phase']]} one, a kinder stretch ahead.", "decades"))
            elif dn > up:
                p2.append(S((f"Within a year the climate turns: the next decade, from {start}, is a {PHASE_ADJ[nx['phase']]} one, so this year is the run-up."
                             if one else f"In about {left} {yrs} the climate turns: the next decade, from {start}, is a {PHASE_ADJ[nx['phase']]} one, "
                             f"so the next {left} {yrs} are the run-up."), "decades"))
            elif dn < up:
                when = "this year" if one else f"the next {left} {yrs}"
                p2.append(S(f"From {start} the climate cools into a {PHASE_ADJ[nx['phase']]} decade, so "
                            + {"senior": f"use {when} for what matters most to you.", "child": f"{when} are a good time to learn and build habits.",
                               "teen": f"{when} are a good time to learn and build habits."}.get(v, f"what you start {'this year' if one else f'in the next {left} {yrs}'} has the best weather behind it."), "decades"))
            else:
                p2.append(S(f"The next decade, from {start}, is also a {PHASE_ADJ[nx['phase']]} one.", "decades"))
            if ph in ("consolidation", "corrective") and nx["phase"] in ("consolidation", "corrective", "transition"):
                peaks = [y["y"] for y in Y if y["overall"] == "peak"]
                inside = f" The strong years inside them, such as {and_join([str(y) for y in peaks[:2]])}, are where to move." if peaks else ""
                hold = {"child": "These are years for steady habits rather than big changes.", "teen": "These are years for steady habits rather than big changes.",
                        "senior": "These are years for keeping things steady and close."}.get(v, "These are years for holding structure, not for expansion.")
                p2.append(S(hold + ("" if v in ("child", "senior") else inside), "decades", "years"))
    if Y:
        y0 = Y[0]
        win = [AREA_V[k] for k in AREA_V if AREA_V[k] and (y0.get(k) or {}).get("flag") == "window"]
        cau = [AREA_V[k] for k in AREA_V if AREA_V[k] and (y0.get(k) or {}).get("flag") == "caution"]
        lead = {"peak": f"{y0['y']} is one of your strongest years", "steady": f"{y0['y']} is a steady year",
                "careful": f"{y0['y']} asks for care"}[y0["overall"]]
        tail = (f", with a window for {ljoin(win)}" if win else "") + \
               ((", but go carefully with " if y0["overall"] == "peak" else "; go carefully with ") + ljoin(cau) if cau else "")
        p3.append(S(lead + tail + ".", "years"))
        dims = [k for k in AREA_V if k in y0 and AREA_V[k]]
        rest = Y[1:] or Y
        rank = {"peak": 2, "steady": 1, "careful": 0}
        best = max(rest, key=lambda y: (rank[y["overall"]], sum((y.get(k) or {}).get("flag") == "window" for k in dims)))
        careful = [y for y in rest if y["overall"] == "careful"]
        worst = max(careful, key=lambda y: sum((y.get(k) or {}).get("flag") == "caution" for k in dims)) if careful else best
        cw = [AREA_V[k] for k in dims if (worst.get(k) or {}).get("flag") == "caution"]
        bw = [AREA_V[k] for k in dims if (best.get(k) or {}).get("flag") == "window"]
        line = f"Looking further ahead, push in {best['y']}{turn(best['y'])}" + (f", a window for {ljoin(bw)}" if bw else "")
        line += f"; protect {worst['y']}{turn(worst['y'])}, which asks for care with {ljoin(cw)}." if cw and worst is not best else "."
        p3.append(S(line, "years"))
    RH = ((p.get("strategy") or {}).get("s5") or {}).get("rhythm") or []
    if RH:
        from .plain import _months
        M = _months(p)
        if M and M["head"].startswith("Your best months: "):
            p3.append(S("Within each year, your best months are " + M["head"][len("Your best months: "):], "months"))
    Dd = (p.get("daily") or {}).get("best")
    if Dd:
        from .plain import _days
        p3.append(S(_days(p)["head"].replace("Your next good day: ", "Your next good day is "), "days"))
    return {"paras": [x for x in (p1, p2, p3) if x], "chart_after": 0}


def _space(p, kid):
    med = p["yongshen"]["favourable"][0]; m = MEDICINE[med]; side, what = EL_ROOM[med]
    pl = {x["key"]: x for x in p.get("placements") or []}
    A = p.get("afflictions") or {}
    hit = {DIR_WORD.get(A[k]["dir"]) for k in ("taisui", "suipo") if A.get(k)}
    p1 = [S(f"Bring {m['colours']} into the rooms where you spend hours: they carry {EN[med]}, the element you need.", "medicine"),
          S(f"Put {EN[med]} on the {side} side of your main room, with {what}" + (", using objects rather than building work this year." if side in hit else "."), "medicine")]
    p2 = []
    if "bed" in pl and "desk" in pl:   # owner convention: say which way each thing faces
        p2.append(S(f"Point your bed head {DIR_WORD[pl['bed']['dir']]}, and face {DIR_WORD[pl['desk']['dir']]} at your desk.", "placements"))
    if "door" in pl:
        p2.append(S(f"Your best door faces {DIR_WORD[pl['door']['dir']]}.", "placements"))
    p3 = []   # owner 2026-10-10: the chart's own directions always win; a year's afflictions only govern building work
    if A:
        ts, sp = A["taisui"]["dir"], A["suipo"]["dir"]
        ss = [DIR_WORD[d] for d in A["sansha"]["dirs"] if d not in (ts, sp)]
        p3.append(S(f"This year, leave the {DIR_WORD[ts]} and {DIR_WORD[sp]} sides of your home undisturbed: no renovation or digging there"
                    + (f", and the same care on the {and_join(ss)}." if ss else "."), "afflict"))
        if A.get("collisions"):
            p3.append(S("Your bed and desk directions above still hold; this year only asks you not to build or dig on those sides.", "afflict"))
    return {"paras": [x for x in (p1, p2, p3) if x], "chart_after": 1 if p2 else 0}


EVIDENCE_LABEL = {
    "gods": "The ten roles, and how much of each you carry", "pillars": "Your four pillars", "personality": "Personality axes",
    "stars": "Symbolic stars", "interactions": "How your pillars pull on each other", "elements": "How much of each element you carry",
    "strength": "Why the strength verdict", "flows": "What feeds you and what presses on you", "medicine": "What helps you, and why",
    "health": "Body: the traditional pairing", "domains": "Your six life areas", "work": "Work that fits", "money": "Your wealth store",
    "decades": "Your luck decades", "years": "Year by year", "months": "Month by month", "days": "Day by day",
    "placements": "Where to sleep and face", "afflict": "This year's disturbances",
}


def _vault_why(V):
    """The wealth store in one plain line (the engine's state string repeats 'vault' once glossed)."""
    if not V.get("present"):
        return "No wealth store (财库) in the chart: money flows rather than stays."
    br = V.get("branch", "")
    if V.get("open"):
        return f"Wealth store (财库): the {br} ({ANIMAL.get(br, br)}) branch, already open."
    opens = V.get("state", "").split(" opens in ")[-1][:1]
    return (f"Wealth store (财库): the {br} ({ANIMAL.get(br, br)}) branch, sealed; it opens in {ANIMAL.get(opens, opens)} ({opens}) years, "
            "which the timing windows mark as years to save and build.")


def _why(p, plain):
    st = p["strength"]; V = (p.get("palaces") or {}).get("vault") or {}
    return {
        "gods": plain["drives"]["why"], "pillars": "\n".join(s["why"] for s in plain["sides"]),   # one note per line
        "personality": (plain.get("personality") or {}).get("why", ""), "stars": "",   # the stars figure lists each star once
        "interactions": plain["makeup"]["why"],
        "elements": "Weighted element shares: " + ", ".join(f"{h['en']} {h['share']}% ({h['status']})" for h in p.get("health") or []) + ".",
        "strength": (f"Strength verdict {st['verdict']}, score {st['score']}; support {st.get('support_ratio')}%, roots "
                     f"{st.get('root_ratio')}%, season points {(st.get('parts') or {}).get('season_pts')}. {(p.get('synthesis') or {}).get('assessment', '')}"),
        "flows": (plain.get("flows") or {}).get("why", ""), "medicine": plain["helps"]["why"],
        "health": plain["health"]["why"], "domains": "",   # the life-areas table and its key carry every score
        "work": "",   # the work figure lists every field, role and reason once
        "money": _vault_why(V),
        "decades": (p.get("windows") or {}).get("arc", ""), "years": (plain.get("next_ten") or {}).get("why", ""),
        "months": "",   # the month rhythm figure shows every month's branch, element and rating; no word wall
        "days": (plain.get("days") or {}).get("why", ""),
        "placements": (plain.get("space") or {}).get("why", ""), "afflict": (plain.get("afflict") or {}).get("why", ""),
    }


def compose_story(p: dict, plain: dict) -> dict:
    age = _age(p, _year_now(p)); v = voice_of(age); kid = v in ("child", "teen")
    ch = {"makeup": _makeup(p, kid), "balance": _balance(p, v), "drives": _drives(p, v),
          "timing": _timing(p, v), "space": _space(p, kid)}
    why = _why(p, plain)
    used = {e for c in ch.values() for para in c["paras"] + [[c["one"]] if c.get("one") else []] for s in para for e in s["ev"]}
    return {"age": age, "young": kid, "voice": v, "chapters": ch,
            "evidence": {k: {"label": EVIDENCE_LABEL[k], "why": why.get(k, "")} for k in EVIDENCE_LABEL if k in used}}


if __name__ == "__main__":   # self-check on the fictional chart
    import json, sys
    from .plain import plain_reading
    p = json.load(open(sys.argv[1], encoding="utf8"))
    st = compose_story(p, plain_reading(p))
    assert st == compose_story(p, plain_reading(p))
    for k, c in st["chapters"].items():
        print(f"## {k}")
        for para in c["paras"] + ([[c["one"]]] if c.get("one") else []):
            print(" ".join(f"{s['t']} {s['ev']}" for s in para)); print()
