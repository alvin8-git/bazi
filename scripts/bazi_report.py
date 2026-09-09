"""Standalone per-member BaZi strategy reports — birth data only, no property.

Structure per report:
  命卡 snapshot → 本命 Who you are (element makeup figure + readings, strength
  meaning, ten-god profile, narrative) → the five consultation question
  categories (career fit with corporate-vs-entrepreneur dial, relationship
  risk-point, wealth pattern + timing, health, decision windows) each ending
  in a 💡 what-to-do block → personal rhythm & handling → exam overlay
  (children) → shared family-strategy section.

The point is interpretation, not just calculation: every figure is followed
by what it MEANS and what to DO — all advice rule-selected (authored rules,
no runtime AI), every number engine-computed.

Writes data/out/bazi{Name}.html ×5.
Usage: .venv/bin/python scripts/bazi_report.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.bazi import TRUE_SOLAR, build_chart
from engine.bazhai import gua_group, ming_gua, youxing_stars
from engine.careers import career_paths
from engine.domains import health_map, personality_axes
from engine.htmlreport import _tosimp
from engine.import_family import load_family
from engine.interpret import interpret_person
from engine.liunian import dayun_detail
from engine.shensha import (ANIMALS, TEN_GOD_MEANING, WENCHANG, life_palaces,
                            shensha, ten_god_pct)
from engine.windows import timing_windows
from engine.wuxing import BRANCH_ELEMENT, HE_MAP, KE, SANHE, STEM_ELEMENT
from engine.yongshen import yong_shen

ROOT = Path(__file__).resolve().parent.parent
YEAR = 2026
FILE_NAME = {"王大明": "Member1", "李小华": "Member2", "王一心": "Member3",
             "王二强": "Member4", "王三美": "Member5"}
ROLE = {"王大明": "dad", "李小华": "mum", "王一心": "eldest daughter",
        "王二强": "son", "王三美": "youngest daughter"}
KIDS = ("王一心", "王二强", "王三美")
PALACE_DIR = {"坎": "N", "艮": "NE", "震": "E", "巽": "SE", "離": "S",
              "坤": "SW", "兌": "W", "乾": "NW"}
EL_COL = {"木": "#2e7d32", "火": "#c0392b", "土": "#b8860b", "金": "#909497",
          "水": "#2471a3"}
EL_EN = {"木": "Wood", "火": "Fire", "土": "Earth", "金": "Metal", "水": "Water"}

# ---- authored interpretation rules (the "human geomancer" layer) ------------
ELEMENT_READING = {  # element → (excess meaning+advice, deficient meaning+advice)
    "木": ("drive and growth in surplus — plans multiply, patience thins, "
           "frustration builds in the body. Burn it kinetically: stretching, "
           "sport, deadlines with finish lines; prune projects rather than add.",
           "growth impulse under-supplied — starting is the hard part. Borrow "
           "structure: morning routines, green surroundings, one live project "
           "always on the desk."),
    "火": ("visibility and urgency in surplus — quick warmth, quick burn. "
           "Guard sleep, cut evening stimulants, keep one cool hour a day; "
           "let others own the spotlight sometimes.",
           "warmth and confidence under-supplied — energy dips and ideas stay "
           "private. Morning sun, cardio, red accents, deliberately social "
           "lunches; present work before it feels ready."),
    "土": ("stability in surplus — reliable but heavy: rumination, over-"
           "caution, digestion sluggish after worry. Move after meals, decide "
           "with deadlines, delegate the double-checking.",
           "grounding under-supplied — routines drift. Fixed mealtimes, one "
           "anchoring weekly ritual, finish small things daily."),
    "金": ("precision in surplus — high standards that cut inward and "
           "outward: rigidity, dry skin/airways. Add softness on purpose: "
           "flexibility practice, humid air, forgiving deadlines, music.",
           "structure under-supplied — edges blur, follow-through leaks. "
           "Checklists, decluttered desk, breathing practice, metal-white "
           "accents in the work zone."),
    "水": ("flow in surplus —深 thinking that can pool into fear or fatigue; "
           "keep warm, protect the lower back and kidneys, cap late nights.",
           "reserves under-supplied — wisdom-on-demand but shallow recovery. "
           "Hydration, real rest cycles, swimming or baths, early nights in "
           "winter; schedule thinking time, don't steal it from sleep."),
}
STRENGTH_ADVICE = {
    True: ("A weak Day Master is not a weak person — it is a chart that runs "
           "on borrowed fuel. Protect energy deliberately: fewer, deeper "
           "commitments; recover before the tank empties. Borrow strength "
           "where the chart says to — 印 (mentors, study, institutions) and "
           "比劫 (peers, alliances) are structural supports, not crutches. "
           "Say no early; this chart pays compound interest on rest."),
    False: ("A strong Day Master carries load well — the risk is under-"
            "loading, not burnout. Seek output channels: responsibility, "
            "production, expression. Idle strength turns inward as "
            "stubbornness; keep a demanding project running at all times."),
}
CAREER_ADVICE = {
    "corp": ["Negotiate for scope and expertise, not just title — this chart "
             "compounds inside institutions with deep technical ladders.",
             "Scratch any venture itch through intrapreneurship: own a new "
             "capability inside the structure rather than leaving it.",
             "Change employers rarely and deliberately, in window years only."],
    "vent": ["Tie pay to performance wherever possible — fixed salary "
             "undervalues this chart's opportunity engine.",
             "Keep personal fixed costs low; volatility charts win on staying "
             "power, and low burn IS staying power.",
             "One mentor plus written quarterly goals — the 貴人 channel keeps "
             "the deal-chasing pointed."],
    "ambi": ["Sequence it: structured roles first to bank capital, skill and "
             "network; option the venture mode for a supportive decade.",
             "In corporate phases, keep one small side asset alive so the "
             "switch, if it comes, is a step not a leap."],
}
REL_ADVICE = {
    "selection": ["Slow the funnel: extend the getting-to-know phase past the "
                  "first impression this chart falls for.",
                  "Weigh stability markers (how they handle stress, money, "
                  "family) above spark — the spark self-supplies.",
                  "Let trusted friends meet candidates early; outside eyes "
                  "correct this chart's blind spot."],
    "communication": ["The 24-hour rule: write the hard message, sleep, then "
                      "say it — 傷官 edges dull overnight.",
                      "Schedule check-ins so issues surface on calm days, not "
                      "only when they boil.",
                      "Have hard conversations on neutral ground (a walk, a "
                      "drive) — not across the dinner table."],
    "division": ["Write the ownership map: who owns money, schooling, "
                 "household, and revisit it yearly — parity charts fight over "
                 "undefined territory, not real differences.",
                 "Avoid working in the same role as a partner; adjacent beats "
                 "identical.",
                 "Score decisions by domain owner, not by who feels stronger "
                 "that week."],
    "none": ["No structural fix needed — use the Windows table: invest in the "
             "relationship in window years, and treat caution years as "
             "maintenance mode, not verdicts."],
}
WEALTH_ADVICE = {
    "steady": ["Automate a fixed savings percentage before spending touches "
               "it — this chart wins by compounding, not by timing.",
               "Prefer boring instruments (index, property, CPF top-ups); "
               "FOMO trades fight the chart's nature.",
               "Review once a quarter, not once a day."],
    "opportunistic": ["Cap each deal at a fixed share of net worth, decided "
                      "in advance, and take profits mechanically.",
                      "Pair with a steady-accumulator for sign-off (see the "
                      "family delegation map) — the pairing is the remedy.",
                      "Act in window years, and force a written thesis before "
                      "any deal in a caution year."],
    "competence": ["Raise rates and skills, not risk — this chart converts "
                   "expertise to income better than capital to income.",
                   "Build assets from the skill itself: royalties, tooling, "
                   "teaching, IP.",
                   "Let structure hold the money: auto-invest what expertise "
                   "earns, then ignore it."],
    "weak-carry": ["Route income out of easy reach on arrival — automatic "
                   "transfers are the container the chart lacks.",
                   "Make large financial moves only in window years, with a "
                   "co-pilot's sign-off.",
                   "Grow the container first (health, seniority, routine) — "
                   "capacity, then exposure."],
}
WINDOWS_ADVICE = [
    "Book the big asks — raises, launches, moves, proposals — into window "
    "years; the same effort lands softer ground in a caution year.",
    "Caution years are for maintenance, consolidation and preparation — they "
    "reward finishing, not starting.",
    "Recheck this table each 立春 (early Feb): the annual layer rolls forward "
    "and next year's weather becomes visible.",
]
ORGAN_CARE = {
    "水": "kidneys/bladder care: drink water through the day (not one late flood), "
          "guard sleep before midnight, keep the lower back warm",
    "木": "liver/gallbladder care: limit alcohol, stretch daily, give the eyes "
          "screen breaks, walk off frustration the same day",
    "火": "heart/circulation care: regular cardio, fixed lights-out, taper "
          "caffeine after noon",
    "土": "spleen/stomach care: regular mealtimes, chew slowly, a 10-minute walk "
          "after dinner, park the worrying at the table's edge",
    "金": "lungs/skin care: breathing practice, moisturise, mind air quality "
          "(purifier in haze season), sing or swim for lung volume",
}
BOSS_FIT = [
    (lambda p: p.get("七殺", 0) > p.get("正官", 0) and p.get("七殺", 0) >= 10,
     "Under management: demanding, decisive bosses get your best — slow "
     "committees and vague briefs frustrate you."),
    (lambda p: p.get("正官", 0) >= 10,
     "Under management: fair, rule-based managers get your best — arbitrary "
     "authority gets quiet resistance."),
    (lambda p: True,
     "Under management: negotiate autonomy and judge-me-by-output "
     "arrangements — heavy supervision wastes this chart."),
]
PARTNER_SUPPLY = {
    "財": "someone who spots opportunities and closes deals (財-rich)",
    "官殺": "someone who enforces structure, deadlines and discipline (官殺-rich)",
    "印": "someone who researches, documents and keeps institutional memory (印-rich)",
    "食傷": "someone who presents, markets and charms the room (食傷-rich)",
    "比劫": "someone who brings manpower, network and shared grind (比劫-rich)",
}
GOD_GROUPS = {"財": ("正財", "偏財"), "官殺": ("正官", "七殺"),
              "印": ("正印", "偏印"), "食傷": ("食神", "傷官"),
              "比劫": ("比肩", "劫財")}
CORPORATE_GODS = {"正官": 1.0, "七殺": 1.0, "正印": 1.0, "偏印": 0.7, "正財": 0.5}
VENTURE_GODS = {"偏財": 1.5, "傷官": 1.0, "劫財": 0.5, "食神": 0.5}
GOD_HANDLE = {
    "正官": "give clear rules, fair process and visible standards — they honour them",
    "七殺": "give autonomy plus hard deadlines; pressure motivates, micromanagement backfires",
    "正印": "teach the why; they absorb through study and trusted mentors",
    "偏印": "let them learn sideways — unusual methods and niche depth are features",
    "比肩": "respect their independence; ask, don't command; peer framing works",
    "劫財": "channel competitiveness into team wins; watch impulsive sharing/spending",
    "食神": "give them room to craft and finish; praise the work, not the speed",
    "傷官": "let them speak and perform; correct in private, never on stage",
    "正財": "steady routines and visible savings goals; they compound",
    "偏財": "give opportunity and a budget cap; teach them to finish one deal before the next",
}
MONTH_RANGE = {"寅": "Feb", "卯": "Mar", "辰": "Apr", "巳": "May", "午": "Jun",
               "未": "Jul", "申": "Aug", "酉": "Sep", "戌": "Oct", "亥": "Nov",
               "子": "Dec", "丑": "Jan"}
EXAMS = {12: "PSLE", 16: "O-Levels", 18: "A-Levels"}
CLASH = {"子": "午", "午": "子", "丑": "未", "未": "丑", "寅": "申", "申": "寅",
         "卯": "酉", "酉": "卯", "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳"}


def sugg(items):
    return ('<div class="sugg"><b>💡 What to do with this</b>'
            + "".join(f"<div>· {i}</div>" for i in items) + "</div>")


def dial(pct):
    corp = sum(pct.get(g, 0) * w for g, w in CORPORATE_GODS.items())
    vent = sum(pct.get(g, 0) * w for g, w in VENTURE_GODS.items())
    ratio = corp / ((corp + vent) or 1)
    mode = "corp" if ratio >= .6 else "vent" if ratio <= .4 else "ambi"
    verdict = {"corp": "built for STRUCTURED environments — corporate ladders, "
                       "institutions, expert tracks",
               "vent": "built for HIGH-VOLATILITY work — ventures, deals, "
                       "performance-paid roles",
               "ambi": "AMBIDEXTROUS — can run either mode; pick by season of life"}[mode]
    ev = [f"{g} {pct[g]:.0f}%" for g in CORPORATE_GODS if pct.get(g, 0) >= 8]
    vv = [f"{g} {pct[g]:.0f}%" for g in VENTURE_GODS if pct.get(g, 0) >= 8]
    return {"pct_corp": round(ratio * 100), "mode": mode, "verdict": verdict,
            "corp_ev": ev, "vent_ev": vv}


def relationship_risk(chart, pct, w):
    p = chart.pillars
    day_hits = [k for k in ("year", "month", "hour")
                if p[k].branch == CLASH.get(p["day"].branch)]
    spouse_gods = ("正財", "偏財") if chart.sex == "M" else ("正官", "七殺")
    mixed = all(pct.get(g, 0) > 0 for g in spouse_gods)
    absent = all(pct.get(g, 0) == 0 for g in spouse_gods)
    scores = {"selection": 0, "communication": 0, "division": 0}
    ev = {k: [] for k in scores}
    if mixed:
        scores["selection"] += 2
        ev["selection"].append("both 正/偏 spouse stars present — attracts mixed signals")
    if absent:
        scores["selection"] += 2
        ev["selection"].append("no spouse star — partners found through activity, not gravity")
    if "牆外" in w["taohua"]["type"]:
        scores["selection"] += 1
        ev["selection"].append("桃花 outside the walls — variable attraction")
    if pct.get("傷官", 0) >= 14:
        scores["communication"] += 2
        ev["communication"].append(f"傷官 {pct['傷官']:.0f}% — sharp expression cuts close partners first")
    if day_hits:
        scores["communication"] += 2
        ev["communication"].append(f"day branch clashed by the {'/'.join(day_hits)} pillar — "
                                   "friction lives in daily contact")
    if pct.get("比肩", 0) + pct.get("劫財", 0) >= 25:
        scores["division"] += 2
        ev["division"].append("heavy 比劫 — parity struggles: who leads, who yields")
    if pct.get("七殺", 0) >= 20 and pct.get("正官", 0) == 0:
        scores["division"] += 1
        ev["division"].append("七殺 without 正官 — control asserted under stress")
    key = max(scores, key=lambda k: scores[k])
    if scores[key] == 0:
        key, note = "none", "no dominant structural risk point — pattern risks are situational"
    else:
        note = {"selection": "partner SELECTION — who is chosen matters more than how it's run",
                "communication": "COMMUNICATION — the relationship works when the channel does",
                "division": "ROLE DIVISION — agree who owns what, explicitly"}[key]
    return {"key": key, "note": note, "evidence": ev.get(key, [])}


def wealth_pattern(chart, pct, w):
    zf, pf = pct.get("正財", 0), pct.get("偏財", 0)
    weak = chart.strength["verdict"].startswith("身弱")
    if pf >= 15 and pf > zf:
        mode, pat = "opportunistic", ("OPPORTUNISTIC 偏財 — lumpy income: deals, "
                                      "ventures, timing plays")
    elif zf >= 12:
        mode, pat = "steady", ("STEADY ACCUMULATOR 正財 — salary, savings and "
                               "compounding beat speculation")
    elif zf + pf > 0:
        mode, pat = "competence", ("MODEST wealth stars — income follows competence "
                                   "(食傷生財 route): monetise skill, not capital")
    else:
        mode, pat = "competence", ("NO wealth star — earn through expertise and let "
                                   "structure hold the money")
    if weak:
        mode = "weak-carry"
        carry = ("the chart is WEAK relative to its wealth element — money that "
                 "arrives tends to pass through; build the container (health, "
                 "routine, seniority) before scaling exposure")
    else:
        carry = "the chart can HOLD wealth — favourable periods reward decisive action"
    wins = [f'{y["y"]} {y["gz"]} — {y["wealth"]["note"]}'
            for y in w["years"] if y["wealth"]["flag"] == "window"]
    cautions = [str(y["y"]) for y in w["years"] if y["wealth"]["flag"] == "caution"]
    return {"mode": mode, "pattern": pat, "carry": carry, "windows": wins,
            "cautions": cautions}


def element_section(chart, ys, hm):
    weights = chart.element_weights
    total = sum(weights.values()) or 1
    bars = "".join(
        f'<div class="ebar"><span class="el">{el} {EL_EN[el]}</span>'
        f'<div class="et"><div style="width:{w / total * 100:.0f}%;'
        f'background:{EL_COL[el]}"></div></div>'
        f'<span class="ev">{w / total * 100:.0f}%</span></div>'
        for el, w in weights.items())
    status = {h["element"]: h["status"] for h in hm}
    reads = []
    for el in weights:
        st = status.get(el, "balanced")
        if "excess" in st:
            reads.append(f'<div class="cite">⬆ <b>{el} {EL_EN[el]} excess</b> — '
                         f'{ELEMENT_READING[el][0]}</div>')
        elif "weak" in st or "deficien" in st:
            reads.append(f'<div class="cite">⬇ <b>{el} {EL_EN[el]} deficient</b> — '
                         f'{ELEMENT_READING[el][1]}</div>')
    if not reads:
        reads = ['<div class="cite">◎ all five elements in workable balance — an '
                 'adaptable chart; imbalances arrive with the years, not from birth '
                 '(see the health trigger years below).</div>']
    fav = "·".join(ys["favourable"])
    return (f'<div class="ebars">{bars}</div>' + "".join(reads)
            + f'<div class="cite" style="margin-top:5px"><b>Bottom line:</b> feed this '
              f'chart {fav} (colours, environments, seasons, fields) and it runs '
              f'smoother everywhere — the same 用神 drives every recommendation in '
              f'this report.</div>')


def tengod_section(pct, chart):
    top = sorted(pct.items(), key=lambda kv: -kv[1])[:3]
    tmax = max(pct.values()) or 1
    bars = "".join(
        f'<div class="ebar"><span class="el">{g}</span>'
        f'<div class="et"><div style="width:{v / tmax * 100:.0f}%;background:#b8860b">'
        f'</div></div><span class="ev">{v:.0f}%</span></div>'
        for g, v in sorted(pct.items(), key=lambda kv: -kv[1]) if v > 0)
    reads = "".join(
        f'<div class="cite"><b>{g} {v:.0f}%</b> — {TEN_GOD_MEANING.get(g, "")}</div>'
        for g, v in top)
    axes = [f'{a["axis"]}: <b>{a["verdict"]}</b> <span class="dim">({a["basis"]})</span>'
            for a in personality_axes(chart) if "no strong" not in a["verdict"]]
    ax = ("".join(f'<div class="cite">{a}</div>' for a in axes)
          or '<div class="cite">no strong temperament tilt — situational range</div>')
    return bars + reads + '<div class="cite" style="margin-top:5px"><b>Temperament read:</b></div>' + ax


def monthly_rhythm(ys):
    fav, unfav = set(ys["favourable"]), set(ys["unfavourable"])
    out = []
    for br in "寅卯辰巳午未申酉戌亥子丑":
        el = BRANCH_ELEMENT[br]
        cls = "good" if el in fav else "bad" if el in unfav else "mid"
        out.append((MONTH_RANGE[br], br, el, cls))
    return out


def exam_overlay(chart, w):
    wc_branch = WENCHANG[chart.day_master]
    rows = []
    for age, exam in EXAMS.items():
        y = chart.lichun_year + age
        if y < YEAR:
            continue
        yr = next((r for r in w["years"] if r["y"] == y), None)
        bits = []
        if yr:
            bits.append(f'{yr["overall_zh"]} overall')
            if yr["gz"][1] == wc_branch:
                bits.append("文昌 year — the scholar star itself arrives ✓")
            for k in ("career", "health"):
                if yr[k]["flag"] == "caution":
                    bits.append(f'{k} caution: {yr[k]["note"]}')
        rows.append({"exam": exam, "year": y,
                     "note": " · ".join(bits) or "beyond the 10-year window — recheck nearer"})
    return rows


def people_compat(chart, pct, ys, others):
    """Who energizes, who drains, who complements — element + zodiac level."""
    yb = chart.pillars["year"].branch
    trine = next((set(g) for g, _ in SANHE if yb in g), set()) - {yb}
    allies = [ANIMALS[HE_MAP[yb]]] + [ANIMALS[b] for b in sorted(trine)]
    clash = ANIMALS[CLASH[yb]]
    fav, unfav = set(ys["favourable"]), set(ys["unfavourable"])
    boost = [n for n, el in others if el in fav]
    drain = [n for n, el in others if el in unfav]
    weakest = min(GOD_GROUPS, key=lambda g: sum(pct.get(x, 0)
                                                for x in GOD_GROUPS[g]))
    boss = next(txt for cond, txt in BOSS_FIT if cond(pct))
    return {"allies": allies, "clash": clash, "boost": boost, "drain": drain,
            "partner": PARTNER_SUPPLY[weakest], "weak_group": weakest,
            "boss": boss,
            "el_line": (f"people whose charts run rich in {'·'.join(fav)} "
                        f"energize you; heavy-{'·'.join(unfav)} people are fine "
                        "in small doses but tiring as daily fixtures")}


def birth_time_confidence(chart):
    eff = chart.effective_dt
    mins = eff.hour * 60 + eff.minute
    starts = [23 * 60] + [h * 60 for h in range(1, 23, 2)]
    dist = min(min(abs(mins - s), 1440 - abs(mins - s)) for s in starts)
    return (f"effective (true-solar) time sits {dist} min from the nearest "
            "hour-pillar boundary — the Hour Pillar is stable ✓" if dist >= 15 else
            f"only {dist} min from an hour-pillar boundary — a small clock error "
            "could flip the Hour Pillar; consider chart rectification ⚠")


def strategy_payload(chart, ys, year=YEAR, others=()) -> dict:
    """The strategy report's advice blocks, keyed by the Reading section each
    belongs to (s2 strength, s5 用神 rhythm, s8 relationships, s10 handling,
    s11 health, s12 career, s13 windows/wealth) — the Reading tab renders
    them in place, replacing the separate strategy report link."""
    pct = ten_god_pct(chart)
    w = timing_windows(chart, ys, dayun_detail(chart, year), year)
    d = dial(pct)
    rr = relationship_risk(chart, pct, w)
    wp = wealth_pattern(chart, pct, w)
    pc = people_compat(chart, pct, ys, list(others))
    hm = health_map(chart)
    weak = chart.strength["verdict"].startswith("身弱")
    is_kid = (year - chart.lichun_year) < 18
    imbal = [ELEMENT_READING[h["element"]][0 if "excess" in h["status"] else 1]
             for h in hm if h["status"] != "balanced"]
    trig = [f'{y["y"]} ({y["health"]["note"]})' for y in w["years"]
            if y["health"]["flag"] == "caution"]
    rec = [str(y["y"]) for y in w["years"] if y["health"]["flag"] == "window"]
    nxt = next((dd for i, dd in enumerate(w["decades"])
                if i and w["decades"][i - 1]["current"]), None)
    handoff = None
    if nxt:
        start = chart.lichun_year + int(nxt["ages"].split("–")[0].split("-")[0])
        handoff = (f'{nxt["gz"]} begins ~{start} as a {nxt["phase_zh"]} '
                   f'{nxt["phase"]} phase'
                   + (f' — {"; ".join(nxt["notes"])}' if nxt["notes"] else ""))
    top2 = [g for g, _ in sorted(pct.items(), key=lambda kv: -kv[1])[:2]
            if g in GOD_HANDLE]
    return {
        "s2": {"advice": STRENGTH_ADVICE[weak]},
        "s5": {"rhythm": [{"mon": mo, "br": b, "el": e, "cls": c}
                          for mo, b, e, c in monthly_rhythm(ys)]},
        "s8": {"risk": rr["note"], "evidence": rr["evidence"],
               "advice": REL_ADVICE[rr["key"]], "kid": is_kid,
               "allies": pc["allies"], "clash": pc["clash"],
               "el_line": pc["el_line"], "taohua": w["taohua"]["branch"]},
        "s10": {"handle": [GOD_HANDLE[g] for g in top2], "kid": is_kid},
        "s11": {"advice": (imbal or ["keep the balanced baseline: seasonal "
                                     "food, regular sleep, and use recovery "
                                     "years for elective procedures and "
                                     "habit resets."])
                + [ORGAN_CARE[h["element"]] for h in hm
                   if h["status"] != "balanced"]
                + ["Double the care in trigger years; schedule check-ups "
                   "into them in advance."],
                "trigger_years": trig, "recovery_years": rec},
        "s12": {"pct_corp": d["pct_corp"], "verdict": d["verdict"],
                "corp_ev": d["corp_ev"], "vent_ev": d["vent_ev"],
                "advice": CAREER_ADVICE[d["mode"]] + [
                    f"Fields carry elements: prefer "
                    f"{'·'.join(ys['favourable'])}-flavoured industries even "
                    "inside the same job title — the same work in the right "
                    "field costs less energy.",
                    pc["boss"],
                    f"Ideal collaborator: this chart's thinnest resource is "
                    f"{pc['weak_group']} — team up with {pc['partner']}."]},
        "s13": {"wealth_pattern": wp["pattern"], "wealth_carry": wp["carry"],
                "act_windows": wp["windows"], "cautions": wp["cautions"],
                "wealth_advice": WEALTH_ADVICE[wp["mode"]],
                "advice": WINDOWS_ADVICE, "handoff": handoff,
                "exams": exam_overlay(chart, w) if is_kid else []},
    }


def build_person(m, chart, ys, fam_section, others):
    """m needs .name/.sex/.birth_dt; works for any person, not just the family
    (ROLE/KIDS fall back to age-based defaults for workspace users)."""
    name = _tosimp(m.name)
    pct = ten_god_pct(chart)
    pc = people_compat(chart, pct, ys,
                       [(n, el) for n, el in others if n != _tosimp(m.name)])
    w = timing_windows(chart, ys, dayun_detail(chart, YEAR), YEAR)
    lp = life_palaces(chart)
    gua = ming_gua(chart.lichun_year, chart.sex)
    yx = youxing_stars(gua)
    cp = career_paths(chart, ys)
    d = dial(pct)
    rr = relationship_risk(chart, pct, w)
    wp = wealth_pattern(chart, pct, w)
    is_kid = m.name in KIDS or (YEAR - chart.lichun_year) < 18
    role = ROLE.get(m.name, "child" if is_kid else "adult")
    hm = health_map(chart)
    weak = chart.strength["verdict"].startswith("身弱")
    narrative = interpret_person(chart, ys, YEAR)["paragraphs"]

    def sec(title, body):
        return f'<div class="sec"><h2>{title}</h2>{body}</div>'

    pill = "".join(f"""<div class="pcol{' dm' if k == 'day' else ''}">
        <div class="pl">{lab}</div><div class="pg">{chart.ten_gods[k]}</div>
        <div class="pz">{chart.pillars[k]}</div>
        <div class="ph">{'<br>'.join(f'{s}({g})' for s, g in chart.hidden_gods[k])}</div></div>"""
        for k, lab in (("hour", "時"), ("day", "日"), ("month", "月"), ("year", "年")))
    dy = "".join(f'<div class="dy{" now" if dd["current"] else ""}">'
                 f'<div>{dd["ages"]}</div><b>{dd["gz"]}</b>'
                 f'<div class="ph2 p-{dd["phase"]}">{dd["phase_zh"]}</div></div>'
                 for dd in w["decades"])
    dirs = (f'<span class="ok">good: '
            + " ".join(f"{PALACE_DIR[p]}({s})" for p, s in yx.items()
                       if s in ("生氣", "天醫", "延年", "伏位"))
            + '</span> · <span class="no">avoid: '
            + " ".join(f"{PALACE_DIR[p]}({s})" for p, s in yx.items()
                       if s not in ("生氣", "天醫", "延年", "伏位")) + "</span>")
    snapshot = sec("命卡 Chart snapshot", f"""
      <div class="facts">生肖 {lp['animal']} · 命卦 {gua} ({gua_group(gua)}) · 命星 {lp['life_star_zh']}
        {lp['life_star_element']} · 命宮 {lp['ming_gong']} · 胎元 {lp['tai_yuan']} ·
        {chart.strength['verdict']} · 用神 {'·'.join(ys['favourable'])}
        <em>avoid {'·'.join(ys['unfavourable'])}</em></div>
      <div class="cite">{birth_time_confidence(chart)}</div>
      <div class="pgrid">{pill}</div>
      <div class="dyrow">{dy}</div>
      <div class="cite">{dirs}</div>
      <div class="cite">神煞: {' · '.join(dict.fromkeys(s['star'] for s in shensha(chart)))}</div>""")

    who = sec("本命 · Who you are 五行十神", f"""
      <h3>Element makeup 五行占比</h3>{element_section(chart, ys, hm)}
      <h3>Day Master strength — and what it asks of you</h3>
      <div class="cite">{chart.strength['verdict']} (score {chart.strength['score']},
        support ratio {chart.strength['support_ratio']}%)</div>
      <p>{STRENGTH_ADVICE[weak]}</p>
      <h3>Ten-god profile 十神</h3>{tengod_section(pct, chart)}
      <details><summary>Full narrative 解读 (rule-generated, no AI)</summary>
        {''.join(f'<p class="cite">{p}</p>' for p in narrative)}</details>""")

    q1 = sec("Q1 · Career & industry fit 事业", f"""
      <div class="dial"><div class="dialbar"><div style="width:{d['pct_corp']}%"></div></div>
        <div class="dialcap"><span>venture 创业型</span><b>{d['pct_corp']}% structured</b>
        <span>corporate 体制型</span></div></div>
      <p class="verdict">{d['verdict']}</p>
      <div class="cite">structure evidence: {', '.join(d['corp_ev']) or '—'} ·
        volatility evidence: {', '.join(d['vent_ev']) or '—'}</div>
      <p><b>Top fields:</b> {' · '.join(f"{a['en']} {a['zh']}" for a in cp['top'][:3])}.
        <b>Priced against:</b> {' · '.join(a['en'] for a in cp['avoid'])}.</p>
      {sugg(CAREER_ADVICE[d['mode']] + [
        f"Fields carry elements: prefer {'·'.join(ys['favourable'])}-flavoured industries even inside the same job title — the same work in the right field costs less energy.",
        pc['boss'],
        f"Ideal collaborator: this chart's thinnest resource is {pc['weak_group']} — team up with {pc['partner']}."])}""")

    rel_title = ("Q2 · Partnership & friendship patterns 关系"
                 if is_kid else "Q2 · Relationship patterns 感情")
    q2 = sec(rel_title, f"""
      <p class="verdict">Primary risk point: {rr['note']}</p>
      {''.join(f'<div class="cite">· {e}</div>' for e in rr['evidence'])}
      <div class="cite">桃花: {w['taohua']['branch']} — {w['taohua']['type']}</div>
      {'<div class="cite">Framed as friendship/collaboration patterns — marriage indications are deliberately not analysed for the children.</div>' if is_kid else ''}
      <h3>People compatibility 人和 — who fits this chart</h3>
      <div class="cite"><b>生肖 allies:</b> {', '.join(pc['allies'])}-born people combine
        or trine this chart's year branch — cooperation flows with less translation.
        <b>Friction 生肖:</b> {pc['clash']}-born — workable, but agreements need to be
        explicit, not assumed.</div>
      <div class="cite"><b>Element fit:</b> {pc['el_line']}.</div>
      <div class="cite"><b>In this family:</b>
        {('energized by ' + ', '.join(pc['boost'])) if pc['boost'] else 'no member dominantly carries the feeding element'}{('; tiring in long doses: ' + ', '.join(pc['drain'])) if pc['drain'] else ''}
        — element-level only; the full pair chemistry is in the harmony matrix.</div>
      {sugg(REL_ADVICE[rr['key']])}""")

    q3 = sec("Q3 · Wealth pattern & timing 财富", f"""
      <p class="verdict">{wp['pattern']}</p><p>{wp['carry']}</p>
      {'<div class="cite"><b>Act-year windows:</b><br>' + '<br>'.join('◉ ' + x for x in wp['windows']) + '</div>' if wp['windows'] else '<div class="cite">no wealth-activation years in the next decade — build, don\'t chase</div>'}
      {f'<div class="cite">⚠ hold-back years: {", ".join(wp["cautions"])}</div>' if wp['cautions'] else ''}
      {sugg(WEALTH_ADVICE[wp['mode']])}""")

    trig = [f'{y["y"]} ({y["health"]["note"]})' for y in w["years"]
            if y["health"]["flag"] == "caution"]
    rec = [str(y["y"]) for y in w["years"] if y["health"]["flag"] == "window"]
    imbal_advice = [ELEMENT_READING[h["element"]][0 if "excess" in h["status"] else 1]
                    for h in hm if h["status"] != "balanced"]
    q4 = sec("Q4 · Health tendencies 健康", f"""
      {''.join(f'<div class="cite">{"⚠" if h["status"] != "balanced" else "·"} <b>{h["element"]} {h["en"]}</b> {h["share"]}% {h["status"]} — {h["organs"]}; {h["aspects"]}</div>' for h in hm)}
      <div class="cite" style="margin-top:6px"><b>Trigger years:</b>
        {', '.join(trig) or 'none flagged in the next decade'} ·
        <b>recovery years:</b> {', '.join(rec) or '—'}</div>
      {sugg((imbal_advice or ['keep the balanced baseline: seasonal food, regular sleep, and use recovery years for elective procedures and habit resets.'])
            + [ORGAN_CARE[h['element']] for h in hm if h['status'] != 'balanced']
            + ['Double the care in trigger years; schedule check-ups into them in advance.',
               'Reference, not medical advice — patterns to watch, not diagnoses.'])}""")

    yr_rows = "".join(f"""<tr><th>{y['y']} {y['gz']}</th>
        <td class="v-{y['overall']}">{y['overall_zh']}</td>
        <td class="f-{y['career']['flag']}">{y['career']['note']}</td>
        <td class="f-{y['wealth']['flag']}">{y['wealth']['note']}</td>
        <td class="f-{y['relationship']['flag']}">{y['relationship']['note']}</td>
        <td class="f-{y['health']['flag']}">{y['health']['note']}</td></tr>"""
        for y in w["years"])
    nxt = next((dd for i, dd in enumerate(w["decades"])
                if i and w["decades"][i - 1]["current"]), None)
    handoff = ""
    if nxt:
        start = chart.lichun_year + int(nxt["ages"].split("–")[0].split("-")[0])
        handoff = (f'<div class="cite"><b>Next-decade handoff:</b> {nxt["gz"]} begins ~{start} '
                   f'as a {nxt["phase_zh"]} {nxt["phase"]} phase'
                   + (f' — {"; ".join(nxt["notes"])}' if nxt["notes"] else "") + ".</div>")
    q5 = sec("Q5 · Key decision windows 时机", f"""
      <table class="wt"><tr><th>Year</th><th>Overall</th><th>事业</th><th>财富</th><th>感情</th><th>健康</th></tr>
      {yr_rows}</table>{handoff}
      {sugg(WINDOWS_ADVICE)}""")

    rhythm = "".join(f'<span class="mo {cls}">{mon} {br}{el}</span>'
                     for mon, br, el, cls in monthly_rhythm(ys))
    extras = sec("Personal rhythm & handling 节律", f"""
      <div class="cite"><b>Monthly rhythm (recurring every year):</b> green months feed
        this chart, red months drain it — schedule pushes into green months and recovery
        into red ones.</div>
      <div class="mos">{rhythm}</div>
      <div class="cite" style="margin-top:6px"><b>{'How to parent them' if is_kid else 'How to work with them'}:</b>
        {' '.join(GOD_HANDLE[g] + '.' for g, v in sorted(pct.items(), key=lambda kv: -kv[1])[:2] if g in GOD_HANDLE)}</div>""")

    exams = ""
    if is_kid:
        rows = exam_overlay(chart, w)
        if rows:
            exams = sec("Exam-year overlay 考试年", "".join(
                f'<div class="cite"><b>{r["exam"]} — {r["year"]}:</b> {r["note"]}</div>'
                for r in rows)
                + sugg(["Front-load preparation before any caution-flagged exam year; "
                        "tuition and habit changes belong in the year prior.",
                        "In 文昌/peak exam years, aim higher — stretch schools and "
                        "subjects are structurally supported."]))

    css = """body{font-family:system-ui,'Noto Sans SC',sans-serif;max-width:840px;margin:24px auto;
      padding:0 16px;color:#222;background:#fafafa}
    h1{font-size:21px}h2{font-size:15.5px;margin:0 0 8px;color:#8a6d1f;border-bottom:1px solid #eee;
      padding-bottom:4px}h3{font-size:13.5px;margin:12px 0 4px;color:#b03a2e}
    .sub{color:#777;font-size:12.5px}.sec{background:#fff;border:1px solid #ddd;border-radius:10px;
      padding:12px 16px;margin:12px 0}
    .facts{font-size:13.5px;margin-bottom:6px}.facts em{color:#b03a2e;font-style:normal;font-size:12px}
    .cite{color:#666;font-size:12.5px;margin:2px 0}.dim{color:#999;font-size:11px}
    .verdict{font-size:15px;font-weight:600;margin:8px 0 4px}
    p{font-size:13.5px;margin:6px 0}
    .sugg{background:#fbf6ea;border:1px solid #eadfc4;border-left:4px solid #b8860b;
      border-radius:8px;padding:8px 12px;margin-top:8px;font-size:13px}
    .sugg div{margin:3px 0}
    .pgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:8px 0}
    .pcol{border:1px solid #e3e3e3;border-radius:8px;padding:5px;text-align:center;font-size:11px;color:#777}
    .pcol.dm{border-color:#b03a2e;box-shadow:0 0 0 1px #b03a2e}
    .pz{font-size:24px;font-weight:700;color:#222}.pg{color:#8a6d1f;font-weight:600}
    .ph{border-top:1px dashed #ddd;margin-top:3px;padding-top:3px}
    .dyrow{display:flex;gap:4px;overflow-x:auto;margin:8px 0}
    .dy{border:1px solid #ddd;border-radius:7px;padding:3px 6px;min-width:60px;text-align:center;
      font-size:10.5px;color:#777}
    .dy.now{border-color:#b03a2e;box-shadow:0 0 0 1px #b03a2e}.dy b{font-size:15px;color:#222}
    .ph2{border-radius:5px;font-size:10px;padding:0 3px;display:inline-block}
    .p-growth{background:#e9f7ee;color:#1e7d32}.p-corrective{background:#fdecea;color:#b03a2e}
    .p-transition{background:#fff4e5;color:#9a6700}.p-consolidation{background:#f3efe7;color:#6b6357}
    .ok{color:#1e7d32}.no{color:#b03a2e}
    .ebar{display:flex;align-items:center;gap:8px;font-size:12px;margin:2px 0}
    .ebar .el{width:90px;color:#666}.ebar .ev{width:34px;text-align:right;color:#888}
    .et{flex:1;background:#f0ece4;border-radius:6px;height:11px;overflow:hidden}
    .et div{height:100%;border-radius:6px}
    .dial{margin:6px 0}.dialbar{background:#fdecea;border-radius:8px;height:14px;overflow:hidden}
    .dialbar div{height:100%;background:#dbe9fd;border-right:3px solid #1a56b0}
    .dialcap{display:flex;justify-content:space-between;font-size:11.5px;color:#777}
    table.wt{border-collapse:collapse;width:100%;font-size:11.5px;margin:6px 0}
    .wt th,.wt td{border:1px solid #e5e5e5;padding:3px 6px;text-align:left;vertical-align:top}
    .wt th{background:#f4f4f4;white-space:nowrap}
    td.f-window{background:#e9f7ee}td.f-caution{background:#fdecea}td.f-quiet{color:#999}
    td.v-peak{background:#e9f7ee;font-weight:600}td.v-careful{background:#fdecea;font-weight:600}
    .mos{display:flex;flex-wrap:wrap;gap:3px}
    .mo{border-radius:7px;padding:1px 7px;font-size:11.5px;border:1px solid #ddd}
    .mo.good{background:#e9f7ee;border-color:#b7e1c3}.mo.bad{background:#fdecea;border-color:#f5c6c0}
    details summary{cursor:pointer;font-size:12.5px;color:#8a6d00;margin-top:6px}
    .note{border-left:4px solid #b03a2e;background:#fff;padding:10px 14px;font-size:12.5px;margin:14px 0}"""
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>{name} — BaZi strategy report 命理战略</title><style>{css}</style></head><body>
<h1>🧬 {name} — personal BaZi strategy report</h1>
<div class="sub">{role} · birth-data only, valid in any home · calculation +
interpretation: every figure is followed by what it means and what to do · all advice
rule-selected, no runtime AI · regenerate with <code>python scripts/bazi_report.py</code></div>
{snapshot}{who}{q1}{q2}{q3}{q4}{q5}{extras}{exams}{fam_section}
<div class="note"><b>Method:</b> 子平 four-pillars with true-solar time; strength by
得令/得地/得势 with 調候 cross-check; timing = 大運/流年 × natal pillars × 用神. These are
structural tendencies and windows, not predictions — a caution is a navigation note.
Known contested point: this chart school reads {'a borderline chart — the alternative strong-reading school would advise the opposite colours; the lived 壬寅 decade supports this reading' if m.name == '王大明' else 'this chart consistently'} — full validation notes in the repo.</div>
</body></html>"""
    return _tosimp(html)


def family_section(members, charts, ys_map, axis_note=""):
    wmap = {m.name: timing_windows(charts[m.name], ys_map[m.name],
                                   dayun_detail(charts[m.name], YEAR), YEAR)
            for m in members}
    rows = []
    for i in range(10):
        y = YEAR + i
        score, careful, peak = 0, [], []
        for m in members:
            r = wmap[m.name]["years"][i]
            if r["overall"] == "peak":
                score += 1
                peak.append(_tosimp(m.name))
            elif r["overall"] == "careful":
                score -= 1
                careful.append(_tosimp(m.name))
        rows.append((y, score, peak, careful))
    best = sorted(rows, key=lambda r: -r[1])[:3]
    joint = "".join(f'<div class="cite">◉ <b>{y}</b> — family score {s:+d}'
                    + (f' (peak for {", ".join(p)})' if p else "")
                    + (f' <span class="no">· {", ".join(c)} in a careful year — '
                       "their caution vetoes big joint moves</span>" if c else "")
                    + "</div>"
                    for y, s, p, c in best)
    veto = [f'{y} ({", ".join(c)})' for y, s, p, c in rows if c]
    deleg = []
    for m in members:
        c = charts[m.name]
        wel = KE[STEM_ELEMENT[c.day_master]]
        partners = [_tosimp(o.name) for o in members if o.name != m.name
                    and wel in ys_map[o.name]["favourable"]]
        deleg.append(f'<div class="cite"><b>{_tosimp(m.name)}</b>: wealth element {wel} — '
                     + (f'natural money co-pilots: {", ".join(partners)}' if partners
                        else "no family member carries this element as favourable — "
                             "external adviser adds value") + "</div>")
    return f"""<div class="sec"><h2>Family strategy 家族策略 <span style="font-weight:400;
      font-size:11.5px;color:#999">(identical section in all five reports)</span></h2>
      <div class="cite"><b>Joint-move years</b> (all five members' windows intersected —
      best years for relocation, family ventures, big purchases):</div>{joint}
      <div class="cite" style="margin-top:4px"><b>Years where someone needs shelter:</b>
      {"; ".join(veto) or "none in the decade"}</div>
      <div class="cite" style="margin-top:8px"><b>Delegation map 财务搭档</b> — whose
      favourable elements carry whose wealth element:</div>{"".join(deleg)}
      {f'<div class="cite" style="margin-top:6px"><b>Known friction axis:</b> {axis_note}</div>' if axis_note else ''}</div>"""


def main():
    members = load_family(ROOT / "data/family.json")
    charts = {m.name: build_chart(m.name, m.sex, m.birth_dt, TRUE_SOLAR)
              for m in members}
    ys_map = {n: yong_shen(c) for n, c in charts.items()}
    (ROOT / "data/out").mkdir(parents=True, exist_ok=True)
    fam = family_section(members, charts, ys_map,
                         axis_note="the 寅申 clash runs through 二强 and both "
                                   "parents — remedies in the harmony handbook; his "
                                   "solo room and the sisters as buffers are "
                                   "structural, not optional.")
    others = [(_tosimp(m.name),
               max(charts[m.name].element_weights,
                   key=charts[m.name].element_weights.get))
              for m in members]
    for m in members:
        out = ROOT / "data/out" / f"bazi{FILE_NAME[m.name]}.html"
        out.write_text(build_person(m, charts[m.name], ys_map[m.name], fam,
                                    others), "utf8")
        print(f"{out.name} written ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
