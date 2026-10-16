"""Story layer for the reading page (round 3, 2026-10-10; templates in review).

Each chapter is up to three short paragraphs (what is true, why, what to do) plus an optional
"if you do one thing" line. Every sentence is a fixed template whose slots come from payload
fields, and carries the ids of the evidence it rests on; the page turns those ids into numbered
markers that open the figure, rule or citation in place. Same payload in, same text out.
"""
from __future__ import annotations

from .area_rank import AREAS_FOR, GAP_FOR_PRIORITY, rank_areas   # the one ranking of the life areas (round 52); AREAS_FOR moved there
from .bazi import reading_year
from .i18n import T, an, num_word, zh_join
from .shensha import is_gonghe, star_name_en
from .plain import (status_paren, ANIMAL, AREA, BAND_KEY, DIR_WORD, EL_ROOM, EN, MEDICINE, NEG_STARS, POLE, SEASON,
                    STEM_EL, _day_label, _month_runs, _run_words, and_join, strength_key, vault_opener)

GOD_NOUN = {"比肩": "peers and self-reliance", "劫財": "rivals and bold moves", "劫财": "rivals and bold moves",
            "食神": "ease and natural talent", "傷官": "sharp expression and challenge", "伤官": "sharp expression and challenge",
            "正財": "steady earning", "正财": "steady earning", "偏財": "deals and opportunity", "偏财": "deals and opportunity",
            "正官": "rules and responsibility", "七殺": "pressure and ambition", "七杀": "pressure and ambition",
            "正印": "mentors and learning", "偏印": "unusual knowledge and solitary study"}
ROLE = {"output": "expression: what you make, say and show", "resource": "support: the people, learning and care that feed you",
        "wealth": "results: earning and getting things done", "pressure": "structure: discipline and responsibility",
        "peer": "allies: friends, partners and teams"}
PHASE_ADJ = {"growth": "expanding", "consolidation": "gathering", "transition": "changing", "corrective": "repairing"}
PHASE_RANK = {"growth": 3, "consolidation": 2, "transition": 1, "corrective": 0}
LU = dict(zip("甲乙丙丁戊己庚辛壬癸", "寅卯巳午巳午申酉亥子"))   # 祿: each stem's own station
NUM = dict(enumerate("zero one two three four five six seven eight nine ten".split()))
DOMAIN = {"attraction": "love and attraction", "stability": "relationship stability", "career": "career",
          "wealth": "money", "learning": "learning", "health": "health and stamina"}
PRIORITY = {   # lowest life area (by standing among charts), when it trails the strongest by 60 percentile points or more
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


def is_minor(effective_time, year) -> bool:
    """The reading's one test for "under 18" (child or teen voice, owner 2026-10-10: no money advice). The full report asks it here too."""
    return voice_of(_age({"effective_time": effective_time}, year)) in ("child", "teen")


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
    return (p.get("afflictions") or {}).get("year") or (((p.get("windows") or {}).get("years") or [{}])[0].get("y")) or reading_year()


def payload_voice(p) -> str:
    """The age voice (child / teen / adult / senior) of an assembled payload: the one the story, the card, the interpretation and the clinical plan all rank the life areas for."""
    return voice_of(_age(p, _year_now(p)))


def _ages(d):
    a, _, b = str(d["ages"]).replace("-", "–").partition("–")
    return int(a), int(b or a)


# ---- chapters ---------------------------------------------------------------------------------
def _gn(g, lang):
    """The ten-god noun phrase; the English table's value when the key is unknown."""
    return T(f"story.GOD_NOUN.{g}", GOD_NOUN.get(g, g), lang) if g in GOD_NOUN else g


def _fav_el(e, lang):
    return T(f"plain.EN.{e}", EN[e], lang)


def _acts(med, v, lang):
    table, tid = (ACTS_CHILD, "ACTS_CHILD") if v == "child" else (ACTS_SENIOR, "ACTS_SENIOR") if v == "senior" else ({}, "")
    if med in table:
        return T(f"story.{tid}.{med}", table[med], lang)
    return T(f"plain.MEDICINE.{med}.acts", MEDICINE[med]["acts"], lang)


def _makeup(p, kid, lang="en"):
    pct = p.get("tengods_pct") or {}
    ranked = sorted(pct.items(), key=lambda kv: -kv[1])
    p1 = []
    if len(ranked) >= 6 and ranked[0][1] - ranked[3][1] < 3:
        p1.append(S(T("story._makeup.01", "Your chart is unusually even: no single role leads, and you carry a little of everything.", lang), "gods"))
    elif ranked:
        (g1, v1), *rest = ranked
        n1 = _gn(g1, lang)
        if rest and rest[0][1] == v1:   # a tie is a shared lead, not "followed by"
            p1.append(S(T("story._makeup.02", f"{cap(n1)} and {_gn(rest[0][0], lang)} share the lead in your chart, at {v1:g}% each.", lang,
                          cap_n1=n1, GOD_NOUN_rest=_gn(rest[0][0], lang), v1=v1), "gods"))
        else:
            tail = T("story._makeup.03", f", followed by {_gn(rest[0][0], lang)} at {rest[0][1]:g}%", lang,
                     GOD_NOUN_rest=_gn(rest[0][0], lang), rest=rest[0][1]) if rest else ""
            lead_word = T("story._makeup.05" if " and " in n1 else "story._makeup.06", "lead" if " and " in n1 else "leads", lang)
            p1.append(S(T("story._makeup.04", f"{cap(n1)} {lead_word} your chart at {v1:g}%{tail}.", lang,
                          cap_n1=n1, lead_leads=lead_word, v1=v1, tail=tail), "gods"))
    pal = {x["key"]: x for x in (p.get("palaces") or {}).get("pillars") or []}
    y, m = (pal.get("year") or {}).get("stem_god"), (pal.get("month") or {}).get("stem_god")
    if y in GOD_NOUN and m in GOD_NOUN:
        work = T("story._makeup.07", "will set the climate of your working life", lang) if kid else T("story._makeup.08", "set the climate of your working life", lang)
        p1.append(S(T("story._makeup.09", f"{cap(_gn(y, lang))} shaped your early years, and {_gn(m, lang)} {work}.", lang,
                      cap_y_god_noun=_gn(y, lang), m_god_noun=_gn(m, lang), work=work), "pillars"))

    axes = [a for a in p.get("personality") or [] if a.get("zone") in ("left", "right")]
    p2 = [S(T(f"plain.POLE.{a['poles'][a['zone']]['en'].replace(' ', '_')}.line", POLE[a["poles"][a["zone"]]["en"]][1], lang), "personality")
          for a in axes if a["poles"][a["zone"]]["en"] in POLE][:3]

    p3 = []
    stars = p.get("shensha") or []
    good = next((s for s in stars if s["star"] not in NEG_STARS), None)
    bad = next((s for s in stars if s["star"] in NEG_STARS), None)
    for s, lead, lid in ((good, "A helpful star sits in your chart", "story._makeup.10"), (bad, "One star asks for care", "story._makeup.11")):
        if s:
            name, _, gist = s["meaning"].partition(" — ")
            gist = STAR_GIST.get(s["star"], (gist or s["meaning"]).split(";")[0])
            if lang == "zh":
                from .htmlreport import _tosimp
                from .i18n.zh import ZH
                name, gist = _tosimp(s["star"]), ZH.get(f"story.STAR_GIST.{s['star']}", gist)
            else:
                name = star_name_en(name, s["star"])
            lead_l = T(lid, lead, lang)
            p3.append(S(T("story._makeup.12", f"{lead_l}: the {name}, {gist}.", lang, lead=lead_l, name=name, gist=gist), "stars"))
    # a half trine with no cardinal branch (拱合) is listed but never counted, so it is not a combination here either
    ia = [x for x in (p.get("interactions") or []) if not (x["kind"] == "半合" and is_gonghe(x["pair"][0], x["pair"][1]))]
    hard = sum(1 for x in ia if any(k in x["kind"] for k in ("沖", "冲", "刑")))
    if hard >= 3:
        p3.append(S(T("story._makeup.13", "Your pillars clash more than most, so change in one part of your life tends to shake the others; "
                      "steady routines are worth more to you than to most people.", lang), "interactions"))
    elif any(any(k in x["kind"] for k in ("沖", "冲")) for x in ia):
        p3.append(S(T("story._makeup.14", "Some of your pillars clash, so change tends to arrive through friction between home, work and family.", lang), "interactions"))
    elif any("刑" in x["kind"] for x in ia):
        p3.append(S(T("story._makeup.15", "Some of your pillars punish one another, so strain tends to build slowly inside your own circle; name it early.", lang), "interactions"))
    elif ia and all("合" in x["kind"] for x in ia):
        p3.append(S(T("story._makeup.16", "Your pillars mostly combine, so the parts of your life tend to back each other up.", lang), "interactions"))
    elif ia:
        p3.append(S(T("story._makeup.17", "Your pillars rub quietly against each other: small frictions, but no open clash.", lang), "interactions"))
    else:
        p3.append(S(T("story._makeup.18", "Your four pillars sit comfortably together, so little of your energy goes on inner conflict.", lang), "interactions"))
    return {"paras": [x for x in (p1, p2, p3) if x], "chart_after": 0}


def _balance(p, v, lang="en"):
    dm_el = STEM_EL[p["day_master"]]; st = p["strength"]; sk = strength_key(st["verdict"])
    fav, unfav = p["yongshen"]["favourable"], p["yongshen"]["unfavourable"]; med = fav[0]
    H = sorted(p.get("health") or [], key=lambda h: -h["share"])
    fl = (p.get("element_relations") or {}).get("flows") or {}
    season = (st.get("parts") or {}).get("season_pts", 0) or 0
    p1, p2, p3 = [], [], []
    el = lambda e: _fav_el(e, lang)
    hname = lambda h: el(h["element"]) if lang == "zh" else h["en"]
    if H:
        own = T("story._balance.01", ", and it is your own element", lang) if H[0]["element"] == dm_el else ""
        p1.append(S(T("story._balance.02", f"{H[0]['en']} is the heaviest element in your chart, at {H[0]['share']:g}%{own}.", lang,
                      H_en=hname(H[0]), H_share=H[0]["share"], own=own), "elements"))
    pr, rs = fl.get("pressure"), fl.get("resource")
    if sk == "weak" and pr and rs and pr["share"] > rs["share"]:
        p1.append(S(T("story._balance.03", f"The pressure on you, from {EN[pr['el']]}, outweighs the support that feeds you, from {EN[rs['el']]}, "
                      "which is why the reading calls you weak.", lang, pr_el_en=el(pr["el"]), rs_el_en=el(rs["el"])), "flows", "strength"))
    elif sk == "weak":
        p1.append(S(T("story._balance.04", "The reading calls you weak.", lang), "strength"))
    elif sk == "strong" and pr and rs and pr["share"] > rs["share"]:
        p1.append(S(T("story._balance.05", f"The reading calls you strong, even though the pressure from {EN[pr['el']]} outweighs the support from "
                      f"{EN[rs['el']]}: your own element carries the load.", lang, pr_el_en=el(pr["el"]), rs_el_en=el(rs["el"])), "strength", "flows"))
    elif sk == "strong":
        p1.append(S(T("story._balance.06", "You have more support than you spend, which is why the reading calls you strong.", lang), "strength"))
    elif sk == "balanced":
        p1.append(S(T("story._balance.07", "Support and pressure roughly cancel out, so the reading calls you balanced.", lang), "strength"))
    else:
        p1.append(S(T("story._balance.08", "Your chart gives itself to its strongest element, so you do best by going with it.", lang), "strength"))

    # why: the strength paradox, then the scarce element and the role it plays
    need = T(f"plain.MEDICINE.{med}.need", MEDICINE[med]["need"], lang)
    if sk == "weak" and season < 0:
        sea = T(f"plain.SEASON.{p['pillars']['month'][1]}", SEASON[p["pillars"]["month"][1]], lang)
        p2.append(S(T("story._balance.09", f"You were born in {SEASON[p['pillars']['month'][1]]}, a season that works against {EN[dm_el]}, "
                      f"so the {EN[dm_el]} you have gives you less strength than the number suggests.", lang,
                      p_pillars_month_season=sea, dm_el_en=el(dm_el)), "strength"))
        med_high = any(h["element"] == med and h["status"].startswith("excess") for h in H)
        if (st.get("support_ratio") or 0) >= 50 and not med_high:
            p2.append(S(T("story._balance.10", f"You are not short of backing; you are short of {MEDICINE[med]['need']}.", lang, med_medicine_need=need), "strength", "medicine"))
    elif sk == "weak" and (st.get("root_ratio") or 0) < 10:
        p2.append(S(T("story._balance.11", "You were born in a helpful season, but your own element has few roots in the branches, "
                      "so that help does not hold.", lang), "strength"))
    elif sk == "strong":
        p2.append(S(T("story._balance.12", "So what helps you is not more of what you have, but outlets for it.", lang), "strength", "medicine"))
    role = next((k for k, f in fl.items() if f.get("el") == med), None)
    scarce = H[-1]["element"] if H else None
    if scarce == med:
        p2.append(S(T("story._balance.13", f"{EN[med]} is both the element you have least of and the one that helps you most.", lang, med_en=el(med)), "elements", "medicine"))
    else:
        p2.append(S(T("story._balance.14", f"Of the elements that help you, {EN[med]} matters most.", lang, med_en=el(med)), "medicine"))
    if role in ROLE:
        p2.append(S(T("story._balance.15", f"For {EN[dm_el]}, {EN[med]} is {ROLE[role]}.", lang, dm_el_en=el(dm_el), med_en=el(med),
                      role_role=T(f"story.ROLE.{role}", ROLE[role], lang)), "flows"))
        exp = next((a for a in p.get("personality") or [] if a["poles"]["right"]["en"] == "prolific"), None)   # the 食傷 output axis (pole names are English in both languages)
        if role == "output" and exp and exp.get("zone") == "left":
            p2.append(S(T("story._balance.16", "Your personality reading says you hold your output back, so what you most need is a way "
                          "for your energy to come out.", lang), "personality"))

    # 病藥 (round A): at most one sentence, only when the chart carries a classical built-in strain. The balance reading (扶抑) leads: when the
    # medicine is an element it avoids, the sentence says to treat the medicine as a short-term fix. Money strains are not told to children or teens.
    by = (p.get("yongshen") or {}).get("bingyao") or {}
    if by.get("pattern") and (by["pattern"] == "傷官見官" or v not in ("child", "teen")):
        base = {"傷官見官": ("story._balance.22", "Your chart has one built-in strain: sharp expression meets rules and responsibility, so candour can cost you standing; 《淵海子平》〈傷官說〉 names mentors and learning as the remedy"),
                "比劫奪財": ("story._balance.23", "Your chart has one built-in strain: peers and rivals draw off what you earn, so money tends to leak to people close to you; 《淵海子平》〈論陽刃〉 names rules and responsibility as the remedy"),
                "財多身弱": ("story._balance.24", "Your chart has one built-in strain: more opportunity than you can carry, so money passes through without staying; 《三命通會》卷六〈論正財〉 is the text the engine follows, and it names mentors and learning")}[by["pattern"]]
        tail = {"agrees": T("story._balance.25", ", which your balance reading also favours.", lang),
                "parts": T("story._balance.26", ", but your balance reading points elsewhere, so treat that remedy as a short-term fix.", lang)}.get(by["status"], "。" if lang == "zh" else ".")
        p2.append(S(T(base[0], base[1], lang) + tail, "medicine"))

    m = MEDICINE[med]; acts = _acts(med, v, lang); colours = T(f"plain.MEDICINE.{med}.colours", m["colours"], lang)
    p3.append(S(T("story._balance.17", f"In practice: {acts}, with {m['colours']} in the rooms where you spend hours.", lang, acts=acts, m_colours=colours), "medicine"))
    if unfav:
        names = [el(e) for e in unfav]
        p3.append(S(T("story._balance.18", f"{and_join([EN[e] for e in unfav])} take more than they give, so go easy on them.", lang,
                      and_join_x=zh_join(names) if lang == "zh" else and_join(names)), "medicine"))
    hi = next((h for h in H if h["status"].startswith("excess")), None)
    lo = [h for h in H if h["status"].startswith("weak")]
    if hi or lo:
        bits = ([T("story._balance.19", f"{hi['en']} runs high", lang, hi_en=hname(hi))] if hi else []) + \
               ([T("story._balance.20", f"{and_join([h['en'] for h in lo])} run{'s' if len(lo) == 1 else ''} low", lang,
                   and_join_x=zh_join([hname(h) for h in lo]), s_x="")] if lo else [])
        organs = and_join([(hi or lo[0])["organs"].split(", ")[0]] + [h["organs"].split(", ")[0] for h in lo if h is not (hi or lo[0])])
        if lang == "zh":
            organs = zh_join([(hi or lo[0])["organs"].split(", ")[0]] + [h["organs"].split(", ")[0] for h in lo if h is not (hi or lo[0])])
        joined = "，".join(bits) if lang == "zh" else " and ".join(bits)
        p3.append(S(T("story._balance.21", f"Your body follows the same shape: {' and '.join(bits)}, so look after your {organs}. "
                      "This is the engine's own element-to-organ pairing, not medical advice.", lang, join_bits=joined, organs=organs), HEALTH_EV))
    one = S(T(f"story.ONE_THING.{v}.{sk}", ONE_THING[v][sk], lang), "strength") if sk in ONE_THING[v] else None
    return {"paras": [x for x in (p1, p2, p3) if x], "chart_after": 1, "one": one}


def _drives(p, v, lang="en"):
    kid = v in ("child", "teen")
    # Round 52 (owner 2026-10-16): the strongest and weakest area come from the one shared ranking (engine/area_rank.py): band word first, then the
    # standing among charts, then the score. The raw scores sit on different scales (learning averages 76, stability 46), so the sentence below still
    # states the raw scores and only picks by band and standing. The same call names the area in the card, the interpretation and the clinical plan.
    rk = rank_areas(p.get("domains") or [], v)
    D = rk["ordered"]
    p1, p2, p3 = [], [], []
    one = None
    jn = (lambda xs: zh_join(xs)) if lang == "zh" else ljoin
    if D:
        top, low = rk["strongest"], rk["weakest"] or rk["strongest"]
        nm = lambda d: T(f"story.DOMAIN.{d['key']}", DOMAIN.get(d["key"], d["en"].lower()), lang) if d["key"] in DOMAIN else d["en"].lower()
        if rk["same_band"]:   # every area reads one band: no area is "strongest" or "weakest", so the sentence says so (round 52, copy for approval)
            bw = T(f"card.band.{rk['band'].replace(' ', '_')}", rk["band"], lang)
            p1.append(S(T("story._drives.same_band", f"Compared with other charts, the life areas weighed here all read {bw}; the highest standing is {nm(top)} ({top['score']} of 100) and the lowest is {nm(low)} ({low['score']}).", lang,
                          band=bw, nm_top=nm(top), top_score=top["score"], nm_low=nm(low), low_score=low["score"]), "domains"))
        else:
            p1.append(S(T("story._drives.01", f"Compared with other charts, your strongest life area is {nm(top)} ({top['score']} of 100); your weakest is {nm(low)} ({low['score']}).", lang,
                          nm_top=nm(top), top_score=top["score"], nm_low=nm(low), low_score=low["score"]), "domains"))
        # the old trigger was a raw-score gap of 40, which fired for 95% of readings; the percentile gap of 60 fires about half as often for adults.
        # Round 52: it never fires when every area reads one band (there is no weakest area to build on), and the area it names is the shared weakest.
        if rk["gap"] >= GAP_FOR_PRIORITY and not rk["same_band"] and (low["key"] in PRIORITY or low["key"] in PRIORITY_BY_VOICE.get(v, {})):
            k = low["key"]
            en = PRIORITY_BY_VOICE.get(v, {}).get(k) or PRIORITY[k]
            tid = f"story.PRIORITY_BY_VOICE.{v}.{k}" if k in PRIORITY_BY_VOICE.get(v, {}) else f"story.PRIORITY.{k}"
            p1.append(S(T(tid, en, lang), "domains"))
    C = (p.get("careers") or {})
    top3 = [c["en"].lower().replace("&", "and") for c in (C.get("top") or [])[:3]]
    if top3:
        leads = {"child": ("story._drives.02", "Strengths to grow into later point toward"), "teen": ("story._drives.03", "Later on, the work that suits you best is"),
                 "senior": ("story._drives.04", "For work, volunteering or mentoring, you suit")}
        lid, len_ = leads.get(v, ("story._drives.05", "You do best in"))
        lead = T(lid, len_, lang)
        rest_t = T("story._drives.06", f", then {ljoin(top3[1:])}.", lang, ljoin_top3=jn(top3[1:])) if top3[1:] else ("。" if lang == "zh" else ".")
        p2.append(S((f"{lead} {top3[0]}" if lang != "zh" else f"{lead}{top3[0]}") + rest_t, "work"))
    av = [c["en"].lower().replace("&", "and") for c in C.get("avoid") or []]
    if av and v != "child":
        p2.append(S(T("story._drives.07", f"{cap(ljoin(av))}{',' if len(av) > 1 else ''} {'is' if len(av) == 1 else 'are'} harder going for this chart, not off limits.", lang,
                      cap_ljoin_av=jn(av), x_x="", is_are=""), "work"))
    V = (p.get("palaces") or {}).get("vault") or {}
    ys = {y["y"]: y for y in (p.get("windows") or {}).get("years") or []}
    if v in ("child", "teen"):
        pass   # no money advice under 18 (owner 2026-10-10)
    elif V.get("present") and not V.get("open"):
        br = vault_opener(V)
        nxt = next((y for y in range(_year_now(p), _year_now(p) + 13) if "子丑寅卯辰巳午未申酉戌亥"[(y - 4) % 12] == br), None)
        if nxt:
            also = (T("story._drives.10", ", a good year to put your affairs in order", lang) if v == "senior"
                    else T("story._drives.11", ", which is also a window for money", lang) if (ys.get(nxt, {}).get("wealth") or {}).get("flag") == "window" else "")
            p2.append(S(T("story._drives.12", f"You have a store of wealth that opens in {ANIMAL.get(br, br)} years; the next is {nxt}{also}.", lang,
                          ANIMAL_br=T(f"plain.ANIMAL.{br}", ANIMAL.get(br, br), lang) if br in ANIMAL else br, nxt=nxt, also=also), "money", "years"))
    elif V.get("present"):
        p2.append(S(T("story._drives.13", "Your wealth store is open, so money moves freely; keep a buffer.", lang), "money"))
    else:
        if v == "senior":
            txt = T("story._drives.14", "Your chart has no store for wealth, so keep savings simple and safe rather than chasing returns.", lang)
        else:
            txt = T("story._drives.15", "Your chart has no store for wealth, so money flows rather than stays: ", lang) \
                + (T("story._drives.16", "when you start earning, ", lang) if kid else "") \
                + T("story._drives.17", "save automatically rather than counting on windfalls.", lang)
        p2.append(S(txt, "money"))
    dom = {d["key"]: d for d in p.get("domains") or []}
    if not kid and "stability" in dom:
        st = BAND_KEY(dom["stability"]["band"])
        p3.append(S({"strong": T("story._drives.18", "Your relationships hold steady.", lang),
                     "even": T("story._drives.19", "Your relationships stay steady when tended.", lang),
                     "weak": T("story._drives.20", "Lasting relationships need deliberate care.", lang)}[st], "domains"))
        day = next((x for x in (p.get("palaces") or {}).get("pillars") or [] if x["key"] == "day"), {})
        g = (day.get("hidden") or [""])[0]
        if g in GOD_NOUN:
            p3.append(S(T("story._drives.21", f"Your partner tends to bring {GOD_NOUN[g]}.", lang, g_god_noun=_gn(g, lang)), "domains"))
        if st == "weak":
            p3.append(S(T("story._drives.22", "Keep shared routines, and say the quiet things out loud.", lang), "domains"))
    elif v == "teen":
        p3.append(S(T("story._drives.23", "Relationships are a theme for later in life, so this reading leaves them for now.", lang), "domains"))
    return {"paras": [x for x in (p1, p2, p3) if x], "chart_after": 0, "one": one}


# the next-decade closing line and verb read the phase that is coming (approved English fix, 2026-10-11)
NEXT_EASIER = {"growth": ("story._timing.10", "a kinder stretch ahead"), "consolidation": ("story._timing.10c", "a steadier stretch ahead"),
               "transition": ("story._timing.10t", "an easier stretch than this one")}
NEXT_VERB = {"consolidation": "settles into", "transition": "shifts into", "corrective": "cools into"}


def _timing(p, v, lang="en"):
    AREA_V = {**AREA, **AREA_BY_VOICE.get(v, {})}
    W = p.get("windows") or {}; decs = W.get("decades") or []; Y = W.get("years") or []
    now = _year_now(p); age = _age(p, now)
    zh = lang == "zh"
    area = lambda k: (T(f"story.AREA_BY_VOICE.{v}.{k}", AREA_BY_VOICE[v][k], lang) if k in AREA_BY_VOICE.get(v, {}) else T(f"plain.AREA.{k}", AREA[k], lang))
    jn = (lambda xs: zh_join(xs)) if zh else ljoin
    adj = lambda ph: T(f"story.PHASE_ADJ.{ph}", PHASE_ADJ[ph], lang)
    turn = lambda y: T("story._timing.01", f" (the year you turn {y - (now - age)})", lang, y_now_age=y - (now - age)) if age is not None and age < 30 else ""
    p1, p2, p3 = [], [], []
    i = next((k for k, d in enumerate(decs) if d.get("current")), None)
    if i is None and decs:
        p1.append(S(T("story._timing.02", f"Your first luck decade starts at age {_ages(decs[0])[0]}.", lang, ages_decs=_ages(decs[0])[0]), "decades"))
    elif i is not None:
        d = decs[i]; ph = d["phase"]; a = i; b = i
        while a > 0 and decs[a - 1]["phase"] == ph:
            a -= 1
        while b + 1 < len(decs) and decs[b + 1]["phase"] == ph:
            b += 1
        n, word = b - a + 1, adj(ph)
        nw = num_word(n, lang, NUM)
        if n == 1:
            lead = T("story._timing.03", f"You are in {an(word)} decade, ages {d['ages']}.", lang, word=word, d_ages=d["ages"])
        elif i == b:
            lead = T("story._timing.04", f"You are in the last of {nw} {word} decades in a row, ages {d['ages']}.", lang, NUM_n=nw, word=word, d_ages=d["ages"])
        elif i == a:
            lead = T("story._timing.05", f"You are in the first of {nw} {word} decades in a row, ages {d['ages']}.", lang, NUM_n=nw, word=word, d_ages=d["ages"])
        else:
            lead = T("story._timing.06", f"You are in the middle of {nw} {word} decades in a row, ages {d['ages']}.", lang, NUM_n=nw, word=word, d_ages=d["ages"])
        from .plain import PHASE
        by_voice = PHASE_BY_VOICE.get(v, {}).get(ph)
        means = T(f"story.PHASE_BY_VOICE.{v}.{ph}", by_voice, lang) if by_voice else T(f"plain.PHASE.{ph}.means", PHASE[ph]["means"], lang)
        p1.append(S(lead + ("" if zh else " ") + means, "decades"))
        lu = next((k for k, x in enumerate(decs) if x["gz"][1] == LU[p["day_master"]]), None)
        if lu is not None and decs[lu]["phase"] in ("growth", "consolidation"):
            if lu < i:
                p1.append(S(T("story._timing.07", f"Your chart's turning point came at ages {decs[lu]['ages']}, when your own element arrived.", lang, decs_lu_ages=decs[lu]["ages"]), "decades"))
            elif lu == i:
                p1.append(S(T("story._timing.08", "This decade is your chart's turning point: your own element arrives in it.", lang), "decades"))
            else:
                p1.append(S(T("story._timing.09", f"Your own element arrives at ages {decs[lu]['ages']}, the turning point of your chart.", lang, decs_lu_ages=decs[lu]["ages"]), "decades"))
        if i + 1 < len(decs) and age is not None:
            nx = decs[i + 1]; start = _ages(nx)[0]; left = max(start - age, 1)
            one = left == 1; yrs = "year" if one else "years"; left = NUM.get(left, left) if not zh else num_word(left, lang); dn, up = PHASE_RANK[nx["phase"]], PHASE_RANK[ph]
            yrs_l = "年" if zh else yrs
            nadj = adj(nx["phase"])
            within = T("story._timing.11", "Within a year", lang) if one else T("story._timing.12", f"In about {left} {yrs}", lang, left=left, yrs=yrs_l)
            if dn > up and v == "senior":
                tid, tail = NEXT_EASIER[nx["phase"]]
                p2.append(S(T(tid, f"{within} the climate turns: the next decade, from {start}, is {an(nadj)} one, {tail}.", lang,
                              Within_a=within, start=start, nx_phase_phase_adj=nadj), "decades"))
            elif dn > up:
                p2.append(S(T("story._timing.13", f"Within a year the climate turns: the next decade, from {start}, is {an(nadj)} one, so this year is the run-up.", lang,
                              start=start, nx_phase_phase_adj=nadj) if one else
                            T("story._timing.14", f"In about {left} {yrs} the climate turns: the next decade, from {start}, is {an(nadj)} one, "
                              f"so the next {left} {yrs} are the run-up.", lang, left=left, yrs=yrs_l, start=start, nx_phase_phase_adj=nadj), "decades"))
            elif dn < up:
                when = T("story._timing.15", "this year", lang) if one else T("story._timing.16", f"the next {left} {yrs}", lang, left=left, yrs=yrs_l)
                this_yea = T("story._timing.15", "this year", lang) if one else T("story._timing.23", f"in the next {left} {yrs}", lang, left=left, yrs=yrs_l)
                lead2 = T("story._timing.17", f"From {start} the climate {NEXT_VERB[nx['phase']]} {an(nadj)} decade, so ", lang, start=start, nx_phase_phase_adj=nadj)
                tails = {"senior": T("story._timing.18", f"use {when} for what matters most to you.", lang, when=when),
                         "child": T("story._timing.19", f"{when} are a good time to learn and build habits.", lang, when=when),
                         "teen": T("story._timing.19", f"{when} are a good time to learn and build habits.", lang, when=when)}
                p2.append(S(lead2 + tails.get(v, T("story._timing.21", f"what you start {'this year' if one else f'in the next {left} {yrs}'} has the best weather behind it.", lang, this_yea=this_yea)), "decades"))
            else:
                p2.append(S(T("story._timing.24", f"The next decade, from {start}, is also {an(nadj)} one.", lang, start=start, nx_phase_phase_adj=nadj), "decades"))
            if ph in ("consolidation", "corrective") and nx["phase"] in ("consolidation", "corrective", "transition"):
                peaks = [y["y"] for y in Y if y["overall"] == "peak"]
                inside = T("story._timing.25", f" The strong years inside them, such as {and_join([str(y) for y in peaks[:2]])}, are where to move.", lang,
                           and_join_x=zh_join([str(y) for y in peaks[:2]]) if zh else and_join([str(y) for y in peaks[:2]])) if peaks else ""
                hold = {"child": T("story._timing.26", "These are years for steady habits rather than big changes.", lang),
                        "teen": T("story._timing.26", "These are years for steady habits rather than big changes.", lang),
                        "senior": T("story._timing.28", "These are years for keeping things steady and close.", lang)}.get(v, T("story._timing.29", "These are years for holding structure, not for expansion.", lang))
                p2.append(S(hold + ("" if v in ("child", "senior") else inside), "decades", "years"))
    if Y:
        y0 = Y[0]
        win = [area(k) for k in AREA_V if AREA_V[k] and (y0.get(k) or {}).get("flag") == "window"]
        cau = [area(k) for k in AREA_V if AREA_V[k] and (y0.get(k) or {}).get("flag") == "caution"]
        lid = {"peak": ("story._timing.30", "is one of your strongest years"), "steady": ("story._timing.31", "is a steady year"),
               "careful": ("story._timing.32", "asks for care")}[y0["overall"]]
        lead = T(lid[0], f"{y0['y']} {lid[1]}", lang, y0_y=y0["y"])
        tail = (T("story._timing.33", f", with a window for {ljoin(win)}", lang, ljoin_win=jn(win)) if win else "") + \
               ((T("story._timing.34", ", but go carefully with ", lang) if y0["overall"] == "peak" else T("story._timing.35", "; go carefully with ", lang)) + jn(cau) if cau else "")
        p3.append(S(lead + tail + ("。" if zh else "."), "years"))
        # 犯太歲 (round A): one sentence when the YEAR branch punishes the 太歲 (刑) or itself (自刑); the sourced tiers only (liunian.taisui_finding).
        # 沖 is the travel caution already, and 值 and 害 have no classical source in hand, so they get no sentence. Adults and seniors only.
        tz = (y0.get("taisui") or {}).get("sentence")
        if tz and v in ("adult", "senior"):
            an_ = T(f"plain.ANIMAL.{y0['taisui']['branch']}", ANIMAL[y0["taisui"]["branch"]], lang)
            p3.append(S(T("story._timing.40", f"It is also a punishment year for the {an_}: strain tends to build slowly, so put big commitments in writing.", lang, an_=an_) if tz == "刑" else
                        T("story._timing.41", f"It is also a self-punishment year for the {an_}: the strain tends to be self-made, so pace yourself and check things twice.", lang, an_=an_), "years"))
        dims = [k for k in AREA_V if k in y0 and AREA_V[k]]
        rest = Y[1:] or Y
        rank = {"peak": 2, "steady": 1, "careful": 0}
        best = max(rest, key=lambda y: (rank[y["overall"]], sum((y.get(k) or {}).get("flag") == "window" for k in dims)))
        careful = [y for y in rest if y["overall"] == "careful"]
        worst = max(careful, key=lambda y: sum((y.get(k) or {}).get("flag") == "caution" for k in dims)) if careful else best
        cw = [area(k) for k in dims if (worst.get(k) or {}).get("flag") == "caution"]
        bw = [area(k) for k in dims if (best.get(k) or {}).get("flag") == "window"]
        line = T("story._timing.36", f"Looking further ahead, push in {best['y']}{turn(best['y'])}", lang, best_y=best["y"], turn_best_y=turn(best["y"]))
        line += T("story._timing.37", f", a window for {ljoin(bw)}", lang, ljoin_bw=jn(bw)) if bw else ""
        line += (T("story._timing.38", f"; protect {worst['y']}{turn(worst['y'])}, which asks for care with {ljoin(cw)}.", lang,
                   worst_y=worst["y"], turn_worst_y=turn(worst["y"]), ljoin_cw=jn(cw)) if cw and worst is not best else ("。" if zh else "."))
        p3.append(S(line, "years"))
    RH, _good, runs = _month_runs(p)
    if RH and runs:
        shown = _run_words(runs, lang)
        p3.append(S(T("story._timing.months_head", f"Within each year, your best months are {and_join(shown)}.", lang, runs=zh_join(shown) if zh else and_join(shown)), "months"))
    Dd = (p.get("daily") or {}).get("best")
    if Dd:
        day = _day_label(Dd["date"], lang)
        p3.append(S(T("story._timing.days_head", f"Your next good day is {day}.", lang, day=day), "days"))
    return {"paras": [x for x in (p1, p2, p3) if x], "chart_after": 0}


def _space(p, kid, lang="en"):
    med = p["yongshen"]["favourable"][0]; m = MEDICINE[med]; side, what = EL_ROOM[med]
    pl = {x["key"]: x for x in p.get("placements") or []}
    A = p.get("afflictions") or {}
    hit = {DIR_WORD.get(A[k]["dir"]) for k in ("taisui", "suipo") if A.get(k)}
    el_med = _fav_el(med, lang); colours = T(f"plain.MEDICINE.{med}.colours", m["colours"], lang)
    what_l = T(f"plain.EL_ROOM.{med}.what", what, lang)
    full_stop = "。" if lang == "zh" else "."
    objects = T("story._space.03", ", using objects rather than building work this year.", lang)
    if side == "centre":   # the centre is not a side of the room
        put = T("story._space.02c", f"Put {EN[med]} in the centre of your main room, with {what}", lang, med_en=el_med, what=what_l)
    else:
        side_l = T(f"plain.DIR_WORD.{next(k for k, vv in DIR_WORD.items() if vv == side)}", side, lang)
        put = T("story._space.02", f"Put {EN[med]} on the {side} side of your main room, with {what}", lang, med_en=el_med, side=side_l, what=what_l)
    p1 = [S(T("story._space.01", f"Bring {m['colours']} into the rooms where you spend hours: they carry {EN[med]}, the element you need.", lang, m_colours=colours, med_en=el_med), "medicine"),
          S(put + (objects if side in hit else full_stop), "medicine")]
    p2 = []
    dw = lambda d: T(f"plain.DIR_WORD.{d}", DIR_WORD[d], lang)
    if "bed" in pl and "desk" in pl:   # owner convention: say which way each thing faces
        p2.append(S(T("story._space.04", f"Point your bed head {DIR_WORD[pl['bed']['dir']]}, and face {DIR_WORD[pl['desk']['dir']]} at your desk.", lang,
                      pl_bed_dir_dir_word=dw(pl["bed"]["dir"]), pl_desk_dir_dir_word=dw(pl["desk"]["dir"])), "placements"))
    if "door" in pl:
        p2.append(S(T("story._space.05", f"Your best door faces {DIR_WORD[pl['door']['dir']]}.", lang, pl_door_dir_dir_word=dw(pl["door"]["dir"])), "placements"))
    p3 = []   # owner 2026-10-10: the chart's own directions always win; a year's afflictions only govern building work
    if A:
        ts, sp = A["taisui"]["dir"], A["suipo"]["dir"]
        ss = [DIR_WORD[d] for d in A["sansha"]["dirs"] if d not in (ts, sp)]
        ss_l = [dw(d) for d in A["sansha"]["dirs"] if d not in (ts, sp)]
        p3.append(S(T("story._space.06", f"This year, leave the {DIR_WORD[ts]} and {DIR_WORD[sp]} sides of your home undisturbed: no renovation or digging there",
                      lang, ts_dir_word=dw(ts), sp_dir_word=dw(sp))
                    + (T("story._space.07", f", and the same care on the {and_join(ss)}.", lang, and_join_ss=zh_join(ss_l) if lang == "zh" else and_join(ss)) if ss else full_stop), "afflict"))
        if A.get("collisions"):
            p3.append(S(T("story._space.08", "Your bed and desk directions above still hold; this year only asks you not to build or dig on those sides.", lang), "afflict"))
    return {"paras": [x for x in (p1, p2, p3) if x], "chart_after": 1 if p2 else 0}


EVIDENCE_LABEL = {
    "gods": "The ten roles, and how much of each you carry", "pillars": "Your four pillars", "personality": "Personality axes",
    "stars": "Symbolic stars", "interactions": "How your pillars pull on each other", "elements": "How much of each element you carry",
    "strength": "Why the strength verdict", "flows": "What feeds you and what presses on you", "medicine": "What helps you, and why",
    "health": "Body: the engine's element-to-organ table", "domains": "Your life areas", "work": "Work that fits", "money": "Your wealth store",
    "decades": "Your luck decades", "years": "Year by year", "months": "Month by month", "days": "Day by day",
    "placements": "Where to sleep and face", "afflict": "This year's afflictions",
}


def _vault_why(V, lang="en"):
    """The wealth store in one plain line (the engine's state string repeats 'vault' once glossed)."""
    an_ = lambda b: T(f"plain.ANIMAL.{b}", ANIMAL.get(b, b), lang) if b in ANIMAL else b
    if not V.get("present"):
        return T("story._vault_why.01", "No wealth store (财库) in the chart: money flows rather than stays.", lang)
    br = V.get("branch", "")
    if V.get("open"):
        return T("story._vault_why.02", f"Wealth store (财库): the {br} ({ANIMAL.get(br, br)}) branch, already open.", lang, br=br, ANIMAL_br=an_(br))
    opens = vault_opener(V)
    return T("story._vault_why.03", f"Wealth store (财库): the {br} ({ANIMAL.get(br, br)}) branch, sealed; it opens in {ANIMAL.get(opens, opens)} ({opens}) years, "
             "which the timing windows mark as years to save and build.", lang, br=br, ANIMAL_br=an_(br), ANIMAL_opens=an_(opens), opens=opens)


def _why(p, plain, lang="en"):
    st = p["strength"]; V = (p.get("palaces") or {}).get("vault") or {}
    zh = lang == "zh"
    elem = ("，" if zh else ", ").join(f"{(_fav_el(h['element'], lang) if zh else h['en'])} {h['share']}%{'' if zh else ' '}{status_paren(h['status'], lang)}" for h in p.get("health") or [])
    return {
        "gods": plain["drives"]["why"], "pillars": "\n".join(s["why"] for s in plain["sides"]),   # one note per line
        "personality": (plain.get("personality") or {}).get("why", ""), "stars": "",   # the stars figure lists each star once
        "interactions": plain["makeup"]["why"],
        "elements": T("story._why.01", "Weighted element shares: ", lang) + elem + ("。" if zh else "."),
        "strength": T("story._why.02", f"Strength verdict {st['verdict']}, score {st['score']}; support {st.get('support_ratio')}%, roots "
                      f"{st.get('root_ratio')}%, season points {(st.get('parts') or {}).get('season_pts')}. {(p.get('synthesis') or {}).get('assessment', '')}", lang,
                      st_verdict=st["verdict"], st_score=st["score"], st_support_rati=st.get("support_ratio"), st_root_ratio=st.get("root_ratio"),
                      x_season_pts=(st.get("parts") or {}).get("season_pts"), x_assessment=(p.get("synthesis") or {}).get("assessment", "")),
        "flows": (plain.get("flows") or {}).get("why", ""), "medicine": plain["helps"]["why"],
        "health": plain["health"]["why"], "domains": "",   # the life-areas table and its key carry every score
        "work": "",   # the work figure lists every field, role and reason once
        "money": _vault_why(V, lang),
        "decades": (p.get("windows") or {}).get("arc", ""), "years": (plain.get("next_ten") or {}).get("why", ""),
        "months": "",   # the month rhythm figure shows every month's branch, element and rating; no word wall
        "days": (plain.get("days") or {}).get("why", ""),
        "placements": (plain.get("space") or {}).get("why", ""), "afflict": (plain.get("afflict") or {}).get("why", ""),
    }


def compose_story(p: dict, plain: dict, lang: str = "en") -> dict:
    age = _age(p, _year_now(p)); v = voice_of(age); kid = v in ("child", "teen")
    ch = {"makeup": _makeup(p, kid, lang), "balance": _balance(p, v, lang), "drives": _drives(p, v, lang),
          "timing": _timing(p, v, lang), "space": _space(p, kid, lang)}
    why = _why(p, plain, lang)
    used = {e for c in ch.values() for para in c["paras"] + [[c["one"]] if c.get("one") else []] for s in para for e in s["ev"]}
    return {"age": age, "young": kid, "voice": v, "chapters": ch,
            "evidence": {k: {"label": T(f"story.EVIDENCE_LABEL.{k}", EVIDENCE_LABEL[k], lang), "why": why.get(k, "")} for k in EVIDENCE_LABEL if k in used}}


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
