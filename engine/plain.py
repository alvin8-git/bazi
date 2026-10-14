"""Plain-language layer for the reading page (owner-approved templates, 2026-10-10).

Deterministic: every sentence is a fixed template whose slots are filled from fields the
payload already carries. Nothing is generated at runtime. The stem and season images follow
classical 天干 natures and the 窮通寶鑑 seasons the engine already cites, so the plain sentence
and the citation behind it say the same thing.
"""
from __future__ import annotations

from .i18n import T, zh_join
from .shensha import star_name_en

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


def _x(lang):
    """x(id, en): the word or phrase for this language (English unchanged)."""
    return lambda id, en: T(id, en, lang)


def _cap(s, lang):
    return s if lang == "zh" else s[:1].upper() + s[1:]


def _join(xs, lang):
    return zh_join(xs) if lang == "zh" else and_join(xs)


def _el(e, lang):
    return T(f"plain.EN.{e}", EN[e], lang)


def _dir(d, lang):
    return T(f"plain.DIR_WORD.{d}", DIR_WORD[d], lang)


def _med(e, key, lang):
    return T(f"plain.MEDICINE.{e}.{key}", MEDICINE[e][key], lang)


def _area(k, lang):
    return T(f"plain.AREA.{k}", AREA[k], lang)


def _phase(ph, key, lang):
    return T(f"plain.PHASE.{ph}.{key}", PHASE[ph][key], lang)


def _season(br, lang):
    return T(f"plain.SEASON.{br}", SEASON[br], lang)


def _animal(br, lang):
    return T(f"plain.ANIMAL.{br}", ANIMAL.get(br, br), lang) if br in ANIMAL else br


def _strength_text(sk, key, lang):
    return T(f"plain.STRENGTH.{sk}.{key}", STRENGTH[sk][key], lang)


def _identity(p, lang="en"):
    x = _x(lang)
    dm = p["day_master"]; img_en, trait_en = STEM_IMAGE[dm]
    img = x(f"plain.STEM_IMAGE.{dm}.image", img_en); trait = x(f"plain.STEM_IMAGE.{dm}.trait", trait_en)
    sk = strength_key(p["strength"]["verdict"]); med = p["yongshen"]["favourable"][0]; st = p["strength"]
    short = _strength_text(sk, "short", lang)
    if sk == "weak" and ((st.get("parts") or {}).get("season_pts") or 0) < 0 and (st.get("support_ratio") or 0) >= 50:
        short = x("plain._identity.01", "are well backed but born out of season")   # the season, not a lack of support, sets the verdict
    elif sk == "weak" and ((st.get("parts") or {}).get("season_pts") or 0) > 0 and (st.get("root_ratio") or 0) < 10:
        short = x("plain._identity.02", "are in season but have few roots")
    season = _season(p["pillars"]["month"][1], lang); need = _med(med, "need", lang)
    return {"head": T("plain._identity.03", f"You are {img} in {season}.", lang, img=img, p_pillars_month_season=season),
            "sub": T("plain._identity.04", f"{trait}. You {short}, and what you need most is {need}.", lang,
                     trait=trait, short=short, med_medicine_need=need),
            "signal": signal(p["strength"]["score"]),
            "why": T("plain._identity.05",
                     f"Day Master {dm} ({EN[STEM_EL[dm]]}) born in the {p['pillars']['month'][1]} month; strength "
                     f"{p['strength']['verdict']} (score {p['strength']['score']}); medicine {med} ({EN[med]}).", lang,
                     dm=dm, dm_stem_el_en=_el(STEM_EL[dm], lang), p_pillars_month=p["pillars"]["month"][1],
                     p_strength_verdict=p["strength"]["verdict"], p_strength_score=p["strength"]["score"],
                     med=med, med_en=_el(med, lang))}


def _helps(p, lang="en"):
    fav = p["yongshen"]["favourable"]; m = MEDICINE[fav[0]]; rest = [_el(e, lang) for e in fav[1:]]
    helps_word = T("plain._helps.02" if len(rest) == 1 else "plain._helps.03", "helps" if len(rest) == 1 else "help", lang)
    more = T("plain._helps.01", f" {and_join(rest)} {helps_word} too.", lang,
             and_join_rest=_join(rest, lang), helps_help=helps_word) if rest else ""
    gives, colours, acts = _med(fav[0], "gives", lang), _med(fav[0], "colours", lang), _med(fav[0], "acts", lang)
    return {"el": fav[0], "head": T("plain._helps.04", f"{EN[fav[0]]} helps you most.", lang, fav_en=_el(fav[0], lang)),
            "means": T("plain._helps.05", f"It brings {m['gives']}.{more}", lang, m_gives=gives, more=more),
            "todo": T("plain._helps.06", f"Wear and decorate with {m['colours']}; favour {m['acts']}.", lang,
                      m_colours=colours, m_acts=acts),
            "avoid": [_el(e, lang) for e in p["yongshen"]["unfavourable"]],
            "why": T("plain._helps.07",
                     f"用神 (useful elements): {' '.join(fav)}; avoid {' '.join(p['yongshen']['unfavourable'])}. {p.get('medicine_rank', '')}", lang,
                     join_fav=" ".join(fav), join_p_yongshen_unfavourable=" ".join(p["yongshen"]["unfavourable"]),
                     p_medicine_ran=p.get("medicine_rank", ""))}


def _year(p, lang="en", minor=False):
    """`minor` (no money advice under 18, owner 2026-10-10) leaves the wealth area out of the window and caution lists; engine.minors recomputes the card with it."""
    areas = [k for k in AREA if not (minor and k == "wealth")]
    ys = (p.get("windows") or {}).get("years") or []
    if not ys:
        return None
    y = ys[0]
    win = [_area(k, lang) for k in areas if (y.get(k) or {}).get("flag") == "window"]
    cau = [_area(k, lang) for k in areas if (y.get(k) or {}).get("flag") == "caution"]
    tail = ([T("plain._year.01", f"a window for {and_join(win)}", lang, and_join_win=_join(win, lang))] if win else []) + \
           ([T("plain._year.02", f"go carefully with {and_join(cau)}", lang, and_join_cau=_join(cau, lang))] if cau else [])
    if lang == "zh":
        means = ("；".join(tail) + "。") if tail else T("plain._year.03", "", lang)
    else:
        means = (tail[0][0].upper() + tail[0][1:] + (f"; {tail[1]}" if len(tail) > 1 else "") + ".") if tail \
            else "No single area is strongly switched on or off."
    ov = y["overall"]
    head = T(f"plain.YEAR.{ov}.head", YEAR[ov]["head"].format(y=y["y"]), lang, y=y["y"]) + ("。" if lang == "zh" else ".")
    bits = "；" if lang == "zh" else "; "
    return {"y": y["y"], "gz": y["gz"], "overall": y["overall"], "word": T(f"plain.YEAR.{ov}.word", YEAR[ov]["word"], lang),
            "head": head, "means": means,
            "why": T("plain._year.04", f"Year {y['y']} {y['gz']}: overall {y['overall']} ({y['overall_zh']}). ", lang,
                     y_y=y["y"], y_gz=y["gz"], y_overall=y["overall"], y_overall_zh=y["overall_zh"]) +
                   bits.join(f"{k} {y[k]['flag']}: {y[k]['note']}" for k in areas if (y.get(k) or {}).get("flag", "quiet") != "quiet")}


def _actions(p, lang="en"):
    fav = p["yongshen"]["favourable"][0]
    out = [T("plain._actions.01", f"Bring {EN[fav]} into the rooms where you spend hours: {MEDICINE[fav]['colours']}.", lang,
             fav_en=_el(fav, lang), fav_medicine_colours=_med(fav, "colours", lang))]
    pl = {x["key"]: x for x in p.get("placements") or []}
    if "bed" in pl and "desk" in pl:   # owner convention 2026-10-10: say which way each thing faces
        out.append(T("plain._actions.02", f"Point your bed head {DIR_WORD[pl['bed']['dir']]}, and face {DIR_WORD[pl['desk']['dir']]} at your desk.", lang,
                     pl_bed_dir_dir_word=_dir(pl["bed"]["dir"], lang), pl_desk_dir_dir_word=_dir(pl["desk"]["dir"], lang)))
    return out


def _band_label(word, lang):
    """The reader-facing label for an English band word (the English word stays the key)."""
    ids = {"too little": "plain.BAND.weak_不足", "about right": "plain.BAND.balanced", "too much": "plain.BAND.excess_過旺",
           "a little thin": "plain.band_word.01"}
    return T(ids[word], word, lang) if word in ids else word


def _balance(p, lang="en"):
    dm_el = STEM_EL[p["day_master"]]; fav = set(p["yongshen"]["favourable"]); med = p["yongshen"]["favourable"][0]
    weak = strength_key(p["strength"]["verdict"]) == "weak"; rows = []
    for h in sorted(p.get("health") or [], key=lambda h: -h["share"]):
        band = band_word(h["status"]); note = ""
        if h["element"] == dm_el and band == "too much" and weak:
            note = T("plain._balance.01", "Your own element, and plentiful, but out of season, so it gives less strength than the number suggests.", lang)
        elif band == "too little" and h["element"] in fav:
            note = T("plain._balance.02", "You are short of the thing that helps you most.", lang)
        elif band == "about right" and h["element"] == med:
            note = T("plain._balance.03", "Enough to keep you balanced, but more of it is what helps you most.", lang)
        elif band == "too much" and h["element"] not in fav:
            note = T("plain._balance.04", "Already plenty; add no more.", lang)
        row = {"el": h["element"], "en": _el(h["element"], lang) if lang == "zh" else h["en"], "share": h["share"],
               "band": _band_label(band, lang), "medicine": h["element"] == med, "note": note}
        if lang == "zh":
            row["band_key"] = band   # colours and logic key on the English word
        rows.append(row)
    return rows


def _strength(p, lang="en"):
    sk = strength_key(p["strength"]["verdict"])
    return {"head": _strength_text(sk, "head", lang) + ("。" if lang == "zh" else "."), "means": _strength_text(sk, "means", lang),
            "todo": _strength_text(sk, "todo", lang), "signal": signal(p["strength"]["score"]),
            "why": T("plain._strength.01", f"Strength verdict {p['strength']['verdict']}, score {p['strength']['score']}, support {p['strength'].get('support_ratio')}%.", lang,
                     p_strength_verdict=p["strength"]["verdict"], p_strength_score=p["strength"]["score"],
                     p_strength_support_rati=p["strength"].get("support_ratio"))}


def _flows(p, lang="en"):
    er = p.get("element_relations")
    if not er:
        return None
    pr, rs = er["flows"]["pressure"], er["flows"]["resource"]
    if pr["share"] > rs["share"]:
        tail = T("plain._flows.01", "Pressure outweighs support, so pace yourself.", lang)
    elif rs["el"] in p["yongshen"]["unfavourable"]:
        tail = T("plain._flows.02", f"You already have more than enough {EN[rs['el']]}, so its support adds weight rather than help.", lang,
                 rs_el_en=_el(rs["el"], lang))
    else:
        tail = T("plain._flows.03", "Support holds the pressure, so you can take more on.", lang)
    pe, re_ = _el(pr["el"], lang), _el(rs["el"], lang)
    return {"head": T("plain._flows.04", f"{pe} presses on you hardest; {re_} feeds you.", lang, pr_el_en=pe, rs_el_en=re_),
            "means": T("plain._flows.05", f"{pe} brings pressure ({pr['share']}%), {re_} brings support ({rs['share']}%). {tail}", lang,
                       pr_el_en=pe, pr_share=pr["share"], rs_el_en=re_, rs_share=rs["share"], tail=tail),
            "why": T("plain._flows.06", f"生剋 flows: pressure {pr['el']} {pr['share']}%, resource {rs['el']} {rs['share']}%.", lang,
                     pr_el=pr["el"], pr_share=pr["share"], rs_el=rs["el"], rs_share=rs["share"])}


def _decades(p, lang="en"):
    W = p.get("windows") or {}
    decs = [{"gz": d["gz"], "ages": d["ages"], "phase": d["phase"], "word": _phase(d["phase"], "word", lang),
             "glyph": PHASE[d["phase"]]["glyph"], "current": bool(d.get("current"))} for d in W.get("decades") or []]
    cur = next((d for d in W.get("decades") or [] if d.get("current")), None)
    if cur:
        w = _phase(cur["phase"], "word", lang).lower()
        art = "an" if w[0] in "aeiou" else "a"
        notes = ("；" if lang == "zh" else "; ").join(cur.get("notes") or [])
        now = {"head": T("plain._decades.01", f"You are in {art} {w} decade.", lang, an_a="", w=w),
               "means": _phase(cur["phase"], "means", lang) + T("plain._decades.03", f" This decade runs through ages {cur['ages']}.", lang, cur_ages=cur["ages"]),
               "why": T("plain._decades.04", f"大運 {cur['gz']} (ages {cur['ages']}): phase {cur['phase']} ({cur['phase_zh']}), score {cur['score']}. ", lang,
                        cur_gz=cur["gz"], cur_ages=cur["ages"], cur_phase=cur["phase"], cur_phase_zh=cur["phase_zh"], cur_score=cur["score"]) + notes}
    elif decs:
        a0 = str(decs[0]["ages"]).split("–")[0].split("-")[0]
        now = {"head": T("plain._decades.05", "Your first luck decade has not begun yet.", lang),
               "means": T("plain._decades.06", f"It starts at age {a0}.", lang, str_decs_ages=a0), "why": ""}
    else:
        now = None
    return decs, now


def _makeup(p, lang="en"):
    ia = p.get("interactions") or []; kinds = {x["kind"] for x in ia}
    if any("沖" in k or "冲" in k for k in kinds):
        head, means = (T("plain._makeup.01", "Parts of your life pull hard against each other.", lang),
                       T("plain._makeup.02", "Some of your pillars clash, so change tends to arrive through friction between home, work and family.", lang))
    elif ia:
        head, means = (T("plain._makeup.03", "Parts of your life rub quietly against each other.", lang),
                       T("plain._makeup.04", "No open clashes, but small frictions between your pillars wear on you over time. Name them and they lose their grip.", lang))
    else:
        head, means = (T("plain._makeup.05", "Your four pillars sit comfortably together.", lang),
                       T("plain._makeup.06", "No strong pulls between the parts of your life, so your energy is not spent on inner conflict.", lang))
    life = lambda k: T(f"plain.PILLAR_LIFE.{k}", PILLAR_LIFE[k], lang)
    pairs = [{"a": life(x["pillars"][0]), "b": life(x["pillars"][1]), "kind": x["kind"],
              "note": x["note"].split(" — ")[-1]} for x in ia[:5]]
    sep = "；" if lang == "zh" else "; "
    listed = sep.join(T("plain._makeup.08", f"{x['kind']} {x['pair']} ({x['pillars'][0]} and {x['pillars'][1]})", lang,
                        x_kind=x["kind"], x_pair=x["pair"], x_pillars=x["pillars"][0], x_pillars_2=x["pillars"][1]) for x in ia) \
        or T("plain._makeup.09", "none", lang)
    return {"head": head, "means": means, "pairs": pairs,
            "why": T("plain._makeup.07", "Branch interactions: ", lang) + listed}


def _drives(p, lang="en"):
    x = _x(lang)
    pct = p.get("tengods_pct") or {}
    groups = sorted(({"zh": zh, "name": x(f"plain.GROUPS.{zh}.name", name), "gloss": x(f"plain.GROUPS.{zh}.gloss", gloss),
                      "pct": round(sum(pct.get(g, 0) for g in gods), 1)}
                     for zh, gods, name, gloss in GROUPS), key=lambda g: -g["pct"])
    top = groups[0]
    return {"head": T("plain._drives.01", f"You are driven most by {top['name'].lower()}.", lang, top_name=top["name"].lower()),
            "means": T("plain._drives.02", f"Your chart leans toward {top['gloss']}.", lang, top_gloss=top["gloss"]),
            "groups": groups,
            "why": T("plain._drives.03", "Ten-god shares: ", lang) + ("，" if lang == "zh" else ", ").join(f"{k} {v}%" for k, v in pct.items())}


def _space(p, lang="en"):
    pl = {x["key"]: x for x in p.get("placements") or []}
    if not ("bed" in pl and "desk" in pl):
        return None
    marks = {}
    for key, label, i in (("bed", "Bed head", "01"), ("desk", "Desk", "02"), ("door", "Door", "03")):
        if key in pl:
            marks.setdefault(pl[key]["dir"], []).append(T(f"plain._space.{i}", label, lang))
    return {"head": T("plain._space.04", "Where to sleep and where to face.", lang), "means": _actions(p, lang)[1], "marks": marks,
            "why": T("plain._space.05",
                     f"八宅 placements for {p.get('gua', '')} ({p.get('group', '')}): bed head toward {pl['bed']['star']} "
                     f"({pl['bed']['dir']}), desk facing {pl['desk']['star']} ({pl['desk']['dir']}).", lang,
                     p_gua=p.get("gua", ""), p_group=p.get("group", ""), pl_bed_star=pl["bed"]["star"], pl_bed_dir=pl["bed"]["dir"],
                     pl_desk_star=pl["desk"]["star"], pl_desk_dir=pl["desk"]["dir"])}


def plain_reading(p: dict, lang: str = "en") -> dict:
    decades, decade_now = _decades(p, lang)
    return {"identity": _identity(p, lang), "helps": _helps(p, lang), "year": _year(p, lang), "actions": _actions(p, lang),
            "balance": _balance(p, lang), "strength": _strength(p, lang), "flows": _flows(p, lang),
            "decades": decades, "decade_now": decade_now,
            "years": [{"y": y["y"], "gz": y["gz"], "overall": y["overall"], "word": T(f"plain.YEAR.{y['overall']}.word", YEAR[y["overall"]]["word"], lang)}
                      for y in (p.get("windows") or {}).get("years") or []],
            "makeup": _makeup(p, lang), "drives": _drives(p, lang), "space": _space(p, lang), **plain_round2(p, lang)}


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


def _star_parts(s, lang):
    """(name, gist) of a symbolic star. The engine's own gloss is English; in Chinese the star's own name and the
    approved one-line gist (story.STAR_GIST) are used, with the engine gloss as the fallback."""
    name, _, gist = s["meaning"].partition(" — ")
    gist = (gist or s["meaning"]).split(";")[0]
    if lang == "zh":
        from .htmlreport import _tosimp
        from .i18n.zh import ZH
        name = _tosimp(s["star"])
        gist = ZH.get(f"story.STAR_GIST.{s['star']}", gist)
    else:
        name = star_name_en(name, s["star"])
    return name, gist


def _sides(p, lang="en"):
    pal = {x["key"]: x for x in (p.get("palaces") or {}).get("pillars") or []}
    out = []
    for k in ("year", "month", "day", "hour"):
        gz = p["pillars"][k]; stem, br = gz[0], gz[1]; P = pal.get(k, {})
        img = T(f"plain.STEM_IMAGE.{stem}.image", STEM_IMAGE[stem][0], lang)
        prefix = T(f"plain.SIDE.{k}.head", SIDE[k][0], lang); area = T(f"plain.SIDE.{k}.phrase", SIDE[k][1], lang)
        season = _season(br, lang)
        if k == "day":   # the identity sentence owns the birth season; the home card is you, unqualified
            role = T("plain._sides.01", "This is you, the Day Master, at the centre of the whole chart.", lang)
            head = T("plain._sides.02", f"{img[0].upper() + img[1:]}, at your most yourself.", lang, img_img=_cap(img, lang))
            line = T("plain._sides.03", f"{prefix} you are {img}, at your most yourself.", lang, prefix=prefix, img=img)
        else:
            god = P.get("stem_god") or (p.get("ten_gods") or {}).get(k, "")
            role = T(f"plain.GOD_ROLE.{god}", GOD_ROLE.get(god, ""), lang) if god in GOD_ROLE else ""
            head = T("plain._sides.04", f"{img[0].upper() + img[1:]} in {season}.", lang, img_img=_cap(img, lang), br_season=season)
            line = T("plain._sides.05", f"{prefix} you are {img} in {season}.", lang, prefix=prefix, img=img, br_season=season)
        out.append({"key": k, "area": area, "stem": stem, "head": head, "line": line,
                    "role": role, "ages": (P.get("ages") or "").replace("ages ", ""),
                    "why": T("plain._sides.06", f"{P.get('zh', k)} {gz}: stem {stem}, branch {br}. {P.get('line', '')}", lang,
                             P_zh=P.get("zh", k), gz=gz, stem=stem, br=br, P_line=P.get("line", ""))})
    return out


def _stars(p, lang="en"):
    S = p.get("shensha") or []
    good = next((s for s in S if s["star"] not in NEG_STARS), None)
    bad = next((s for s in S if s["star"] in NEG_STARS), None)
    side = lambda x: T(f"plain.SIDE.{x}.phrase", SIDE[x][1], lang)
    out = []
    if good:
        name, gist = _star_parts(good, lang)
        where = _join([side(x) for x in good["pillars"]], lang)
        out.append({"head": T("plain._stars.01", f"You carry a helpful star: {name}.", lang, name=name),
                    "means": T("plain._stars.02", f"{gist[0].upper() + gist[1:]}. It sits in {where}.", lang, gist_gist=_cap(gist, lang), and_join_x=where),
                    "why": T("plain._stars.03", f"{good['star']} in the {', '.join(good['pillars'])} pillar. {good['meaning']} ({good.get('source_ref', '')}).", lang,
                             good_star=good["star"], join_good_pillars=", ".join(good["pillars"]), good_meaning=good["meaning"],
                             good_source_ref=good.get("source_ref", ""))})
    if bad:
        name, gist = _star_parts(bad, lang)
        where = _join([side(x) for x in bad["pillars"]], lang)
        out.append({"head": T("plain._stars.04", f"One star asks for care: {name}.", lang, name=name),
                    "means": T("plain._stars.02", f"{gist[0].upper() + gist[1:]}. It sits in {where}.", lang, gist_gist=_cap(gist, lang), and_join_x=where),
                    "why": T("plain._stars.06", f"{bad['star']} in the {', '.join(bad['pillars'])} pillar. {bad['meaning']} ({bad.get('source_ref', '')}).", lang,
                             bad_star=bad["star"], join_bad_pillars=", ".join(bad["pillars"]), bad_meaning=bad["meaning"],
                             bad_source_ref=bad.get("source_ref", ""))})
    return out


def _health(p, lang="en"):
    H = p.get("health") or []
    hi = next((h for h in H if h["status"].startswith("excess")), None)
    lo = [h for h in H if h["status"].startswith("weak")]
    if not hi and not lo:
        return {"head": T("plain._health.01", "No organ system is flagged.", lang),
                "means": T("plain._health.02", "All five elements sit in range. This is the engine's own element-to-organ pairing, not medical advice.", lang), "why": ""}
    main = hi or lo[0]
    org = lambda h: _join(h["organs"].split(", "), lang)
    body, _, mood = main["aspects"].partition("; ")
    watch = _join(body.split(", "), lang) + (T("plain._health.03", f", and watch for {mood}", lang, mood=mood) if mood else "")
    head = T("plain._health.04", f"Look after your {org(main)}.", lang, org_main=org(main))
    main_en = _el(main["element"], lang) if lang == "zh" else main["en"]
    means = (T("plain._health.05", f"{main['en']} runs high in your chart, which traditionally strains the {org(main)}; notice {watch}. ", lang,
               main_en=main_en, org_main=org(main), watch=watch)
             if hi else T("plain._health.06", f"{main['en']} runs low in your chart; the {org(main)} want support, so notice {watch}. ", lang,
                          main_en=main_en, org_main=org(main), watch=watch))
    means += T("plain._health.07", "This is the engine's own element-to-organ pairing, not medical advice.", lang)
    rest = [h for h in lo if h is not main]
    sep = T("plain._health.09", ", and your ", lang)
    joined = sep.join(org(h) for h in rest)
    sep_why = "；" if lang == "zh" else "; "
    return {"head": head, "means": means,
            "todo": (T("plain._health.08", f"Support your {joined} too; your chart is short of them.", lang, join_x=joined) if rest else None),
            "why": sep_why.join(f"{h['en']} {h['share']}% ({h['status']}): {h['organs']}" for h in H)}


def _personality(p, lang="en"):
    axes = [a for a in p.get("personality") or [] if a.get("zone") in ("left", "right")]
    pole_id = lambda e: e.replace(" ", "_")
    traits = [(T(f"plain.POLE.{pole_id(e)}.trait", POLE[e][0], lang), T(f"plain.POLE.{pole_id(e)}.line", POLE[e][1], lang))
              for e in (a["poles"][a["zone"]]["en"] for a in axes) if e in POLE]
    if not traits:
        return None
    words = [t[0] for t in traits]
    return {"head": T("plain._personality.01", f"You are {and_join(words[:2])}.", lang, and_join_words=_join(words[:2], lang)),
            "means": ("" if lang == "zh" else " ").join(t[1] for t in traits[:4]),
            "why": ("；" if lang == "zh" else "; ").join(f"{a['axis']}: {a['verdict']} ({a.get('basis', '')})" for a in axes)}


def _work(p, lang="en"):
    top = ((p.get("careers") or {}).get("top") or [None])[0]
    lc = lambda r: r if r.split()[0].isupper() and len(r.split()[0]) > 1 else r[0].lower() + r[1:]
    roles = [lc(r["role"]).replace(" & ", " and ") for r in ((p.get("career_roles") or {}).get("top") or [])[:3]]
    ind = p.get("industries") or {}
    fav = [x["industries"].split(",")[0].strip() for x in ind.get("favourable") or []]
    avoid = [x["industries"].split(",")[0].strip() for x in ind.get("avoid") or []]
    if not top:
        return None
    top_en = top["en"].lower().replace("&", "and")
    means = (T("plain._work.02", f"Roles that suit you now: {and_join(roles)}. ", lang, and_join_roles=_join(roles, lang)) if roles else "") \
        + (T("plain._work.03", f"Fields that recharge you: {and_join(fav)}.", lang, and_join_fav=_join(fav, lang)) if fav else "")
    return {"head": T("plain._work.01", f"You do best in {top_en}.", lang, top_en=top_en),
            "means": means,
            "todo": T("plain._work.04", f"Treat {and_join(avoid)} as harder going, not off limits.", lang, and_join_avoid=_join(avoid, lang)) if avoid else None,
            "why": T("plain._work.05", f"Top archetype {top['en']} ({top['score']} pts): ", lang, top_en=top["en"], top_score=top["score"])
                   + ("；" if lang == "zh" else "; ").join(top["reasons"])}


def vault_opener(V) -> str:
    """The branch that opens a sealed 財庫: the 六沖 partner of the vault's own branch (interpret._VAULT_CLASH). Read from the branch,
    which is the same in every language, never from the state sentence, which is not."""
    from .interpret import _VAULT_CLASH
    return _VAULT_CLASH.get(V.get("branch", ""), "")


def _money(p, lang="en"):
    W = next((d for d in p.get("domains") or [] if d["key"] == "wealth"), None)
    if not W:
        return None
    bk = BAND_KEY(W["band"])
    head = {"strong": T("plain._money.01", "Money comes to you readily.", lang), "even": T("plain._money.02", "Money comes through steady effort.", lang),
            "weak": T("plain._money.03", "Money needs deliberate building.", lang)}[bk]
    V = (p.get("palaces") or {}).get("vault") or {}
    br = vault_opener(V) if V.get("present") and not V.get("open") else ""
    from .bazi import reading_year
    y0 = (((p.get("windows") or {}).get("years") or [{}])[0].get("y")) or reading_year()   # the reading's own year, never a constant
    nxt = next((y for y in range(y0, y0 + 14) if "子丑寅卯辰巳午未申酉戌亥"[(y - 4) % 12] == br), None) if br else None
    means = (T("plain._money.04", f"You have a store of wealth that opens in {ANIMAL.get(br, br)} years ({br}); the next is {nxt}. Those are your years to save and build.", lang,
               ANIMAL_br=_animal(br, lang), br=br, nxt=nxt) if br
             else T("plain._money.05", "Your wealth store is open, so money moves freely; keep a buffer.", lang) if V.get("present")
             else T("plain._money.06", "There is no fixed wealth store in your chart, so build one on purpose.", lang))
    return {"head": head, "means": means,
            "why": T("plain._money.07", f"Wealth domain {W['score']} ({W['band']}). Vault: {V.get('state', 'absent')}.", lang,
                     W_score=W["score"], W_band=W["band"], V_state=V.get("state", "absent"))}


def _love(p, lang="en"):
    D = {d["key"]: d for d in p.get("domains") or []}
    st, at = D.get("stability"), D.get("attraction")
    if not st:
        return None
    head = {"strong": T("plain._love.01", "Your relationships hold steady.", lang),
            "even": T("plain._love.02", "Your relationships stay steady when tended.", lang),
            "weak": T("plain._love.03", "Lasting relationships need deliberate care.", lang)}[BAND_KEY(st["band"])]
    pull = {"strong": T("plain._love.04", "You draw people easily", lang), "even": T("plain._love.05", "You draw people at an even pace", lang),
            "weak": T("plain._love.06", "Attraction builds slowly", lang)}[BAND_KEY(at["band"])] if at else ""
    sp = p.get("spouse_reading") or {}
    day = next((x for x in (p.get("palaces") or {}).get("pillars") or [] if x["key"] == "day"), {})
    g = (day.get("hidden") or [""])[0]
    gist = T(f"plain.GOD_GIST.{g}", GOD_GIST.get(g, ""), lang) if g in GOD_GIST else ""
    stop = "。" if lang == "zh" else ". "
    return {"head": head, "means": (pull + stop if pull else "") + (T("plain._love.07", f"Your partner tends to bring {gist}.", lang, gist=gist) if gist else ""),
            "todo": T("plain._love.08", "Keep shared routines and say the quiet things out loud.", lang) if BAND_KEY(st["band"]) == "weak" else None,
            "why": " ".join(x for x in (sp.get("star_line"), sp.get("palace_line")) if x)}


def _next_ten(p, lang="en", minor=False):
    Y = (p.get("windows") or {}).get("years") or []
    dims = [k for k in AREA if Y and k in Y[0] and not (minor and k == "wealth")]
    if not Y:
        return None
    best = max(Y, key=lambda y: sum((y.get(k) or {}).get("flag") == "window" for k in dims))
    worst = max(Y, key=lambda y: sum((y.get(k) or {}).get("flag") == "caution" for k in dims))
    win = [_area(k, lang) for k in dims if (best.get(k) or {}).get("flag") == "window"]
    cau = [_area(k, lang) for k in dims if (worst.get(k) or {}).get("flag") == "caution"]
    by, wy = best["y"], worst["y"]
    head = T("plain._next_ten.01", f"Push in {by}; protect {wy}.", lang, best_y=by, worst_y=wy) if cau \
        else T("plain._next_ten.02", f"Push in {by}.", lang, best_y=by)
    first = T("plain._next_ten.03", f"{by} opens windows for {and_join(win)}.", lang, best_y=by, and_join_win=_join(win, lang)) if win \
        else T("plain._next_ten.04", f"{by} is your strongest year ahead.", lang, best_y=by)
    second = T("plain._next_ten.05", f" {wy} asks for care with {and_join(cau)}.", lang, worst_y=wy, and_join_cau=_join(cau, lang)) if cau else ""
    why = f"{best['y']} {best['gz']}: {best['overall']}; {worst['y']} {worst['gz']}: {worst['overall']}."
    # round A: this year's 犯太歲 rows (刑, and 合 read as 晦), each with its classical source, as one more paragraph of the same panel
    cites = (Y[0].get("taisui") or {}).get("cites") or []
    if cites:
        lines = [T("plain._next_ten.07", f"{c['explanation']}. Source: {c['source_ref']}", lang, explanation=c["explanation"], source_ref=c["source_ref"]) for c in cites]
        why += "\n" + T("plain._next_ten.06", f"太歲 check for {Y[0]['y']}: " + " ".join(lines), lang, y=Y[0]["y"], lines="".join(lines) if lang == "zh" else " ".join(lines))
    return {"head": head, "means": first + second, "why": why}


def _month_runs(p):
    """Structured month data shared by the months card and the story: (rows, good rows, runs of consecutive good months)."""
    RH = ((p.get("strategy") or {}).get("s5") or {}).get("rhythm") or []
    good = [r for r in RH if r.get("cls") == "good"]
    order = [r["mon"] for r in RH]; idx = sorted(order.index(r["mon"]) for r in good); runs = []; i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and idx[j + 1] == idx[j] + 1:
            j += 1
        runs.append(order[idx[i]] if i == j else f"{order[idx[i]]}–{order[idx[j]]}"); i = j + 1
    return RH, good, runs


_MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def _mon_word(m, lang):
    return T(f"plain._days.{m}", m, lang) if m in _MON else m


def _run_words(runs, lang):
    """Month runs for display: Feb–Mar becomes 2月–3月 in Chinese."""
    if lang != "zh":
        return runs
    return ["–".join(_mon_word(m, lang) for m in r.split("–")) for r in runs]


def _months(p, lang="en"):
    RH, good, runs = _month_runs(p)
    if not RH:
        return None
    shown = _run_words(runs, lang)
    els = _join(sorted({_el(r["el"], lang) for r in good}), lang)
    one = len({r["el"] for r in good}) == 1
    helps_word = T("plain._months.04" if one else "plain._months.05", "helps" if one else "help", lang)
    return {"head": T("plain._months.01", f"Your best months: {and_join(shown)}.", lang, and_join_runs=_join(shown, lang)) if runs
            else T("plain._months.02", "No month carries your medicine.", lang),
            "means": T("plain._months.03", f"They carry {els}, which {helps_word} you. Keep the other months for steady work.", lang,
                       els=els, helps_help=helps_word) if runs else T("plain._months.06", "Pace the whole year evenly.", lang),
            "why": T("plain._months.07", "Month by month: ", lang) + ("，" if lang == "zh" else ", ").join(f"{r['mon']} {r['br']} {r['el']} {r['cls']}" for r in RH)}


def _day_label(d, lang):
    """2026-10-14 as '14 Oct' (English) or 10月14日 (Chinese)."""
    n, m = int(d[8:10]), int(d[5:7])
    return f"{n} {_MON[m - 1]}" if lang != "zh" else f"{T('plain._days.' + _MON[m - 1], _MON[m - 1], lang)}{n}日"


def _acts_text(xs, lang):
    return T("plain._days.01", "most things", lang) if len(xs) >= 5 else _join(list(xs)[:3], lang)


def _days(p, lang="en"):
    D = p.get("daily") or {}; B, W = D.get("best"), D.get("worst")
    if not B and not W:
        return None
    day = lambda d: _day_label(d, lang)
    acts = lambda xs: _acts_text(xs, lang)
    head = T("plain._days.02", f"Your next good day: {day(B['date'])}.", lang, day_B_date=day(B["date"])) if B \
        else T("plain._days.03", "No clear good day this month.", lang)
    m1 = T("plain._days.04", f"Good for {acts(B['for'])}. ", lang, acts_B_for=acts(B["for"])) if B else ""
    if W and W.get("avoid"):
        m2 = (T("plain._days.05", f"Hold off on big decisions on {day(W['date'])}.", lang, day_W_date=day(W["date"])) if len(W["avoid"]) >= 5
              else T("plain._days.06", f"On {day(W['date'])}, avoid {acts(W['avoid'])}.", lang, day_W_date=day(W["date"]), acts_W_avoid=acts(W["avoid"])))
    else:
        m2 = ""
    why = (T("plain._days.07", f"Best {B['date']} {B['gz']} ({B['officer']} day). ", lang, B_date=B["date"], B_gz=B["gz"], B_officer=B["officer"]) if B else "") \
        + (T("plain._days.08", f"Worst {W['date']} {W['gz']}: {W.get('why', '')}.", lang, W_date=W["date"], W_gz=W["gz"], W_why=W.get("why", "")) if W else "")
    return {"head": head, "means": m1 + m2, "why": why}


def _room(p, lang="en"):
    fav = p["yongshen"]["favourable"][0]; side, what = EL_ROOM[fav]
    what_l = T(f"plain.EL_ROOM.{fav}.what", what, lang)
    if side == "centre":   # the centre is not a side of the room
        head = T("plain._room.01c", f"Put {EN[fav]} in the centre of your main room.", lang, fav_en=_el(fav, lang))
    else:
        side_l = T(f"plain.EL_ROOM.{fav}.side", side, lang) if fav == "土" else _dir(next(k for k, v in DIR_WORD.items() if v == side), lang)
        head = T("plain._room.01", f"Put {EN[fav]} on the {side} side of your main room.", lang, fav_en=_el(fav, lang), side=side_l)
    return {"head": head, "means": T("plain._room.02", f"Use {what}.", lang, what=what_l),
            "why": T("plain._room.03", f"Medicine {fav} ({EN[fav]}) placed by its direction.", lang, fav=fav, fav_en=_el(fav, lang))}


def _afflictions(p, lang="en"):
    A = p.get("afflictions") or {}
    if not A:
        return None
    ts, sp, ss = A["taisui"]["dir"], A["suipo"]["dir"], A["sansha"]["dirs"]
    hits = A.get("collisions") or []
    dirs = _join([_dir(d, lang) for d in ss], lang)
    return {"head": T("plain._afflictions.01", f"Leave the {DIR_WORD[ts]} and {DIR_WORD[sp]} undisturbed this year.", lang,
                      ts_dir_word=_dir(ts, lang), sp_dir_word=_dir(sp, lang)),   # owner 2026-10-10: chart directions win
            "means": T("plain._afflictions.02", f"Do not renovate or dig there, and take the same care on the {and_join([DIR_WORD[d] for d in ss])}.", lang, and_join_x=dirs),
            "todo": T("plain._afflictions.03", "Your bed and desk directions still hold; this year only asks you not to build or dig on those sides.", lang) if hits else None,
            "why": " ".join(h["note"] for h in hits) or T("plain._afflictions.04", "None of this year's afflictions sits on your four favourable sectors.", lang)}


def plain_round2(p: dict, lang: str = "en") -> dict:
    return {"sides": _sides(p, lang), "stars": _stars(p, lang), "health": _health(p, lang), "personality": _personality(p, lang),
            "work": _work(p, lang), "money": _money(p, lang), "love": _love(p, lang), "next_ten": _next_ten(p, lang),
            "months": _months(p, lang), "days": _days(p, lang), "room": _room(p, lang), "afflict": _afflictions(p, lang)}
