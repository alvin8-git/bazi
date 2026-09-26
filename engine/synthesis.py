"""綜合論斷 — the one-voice synthesis above the reading tabs, plus the
spouse/marriage reading (audit 2026-09-19: the page answered what the engine
finds easy, not what the client came with).

Deterministic sentences assembled from fields the payload already computes:
strength, ten-god shares, rooting, 用神, decade phases. Every sentence names
its evidence; nothing here invents a number.
"""
from __future__ import annotations

from .wuxing import (ELEMENT_EN, ELEMENTS, HIDDEN_STEMS, KE, SHENG,
                     SHENG_REV, STEM_ELEMENT)

_WEALTH = ("正財", "偏財")
_OFFICER = ("正官", "七殺")
_RESOURCE = ("正印", "偏印")
_PEERS = ("比肩", "劫財")
_OUTPUT = ("食神", "傷官")


def _grp(pct: dict, gods) -> float:
    return round(sum(pct.get(g, 0) for g in gods), 1)


def geju_line(c) -> str:
    """One-line 格局 frame (follow-up audit): the month branch's ruling hidden
    stem (本氣 司令) plus which month-hidden gods are 透干. Frames, not fate."""
    from .bazi import ten_god
    mb = c.pillars["month"].branch
    hidden = HIDDEN_STEMS[mb]
    ruler = hidden[0]
    ruler_god = ten_god(c.day_master, ruler)
    visible = [c.pillars[p].stem for p in ("year", "month", "hour")]
    tou = [st for st in hidden if st in visible]
    if tou:
        g = ten_god(c.day_master, tou[0])
        frame = f"{g}格 (月支藏干 {tou[0]} 透干)"
    else:
        frame = (f"no 月支藏干 is 透 — the chart frames on the 司令 "
                 f"{ruler_god} with the transparent stems as actors")
    return (f"格局: 月令 {mb}, 本氣 {ruler} ({ruler_god}) 司令 · {frame}. "
            "The 格 names the chart's operating frame; the strength verdict "
            "below says how well the frame is carried.")


def medicine_ranking(c, ys: dict) -> str:
    """Rank the 用神 elements instead of listing them flat, with the classical
    ceiling where it applies (e.g. 土多金埋 for a 金 Day Master fed by 土)."""
    dm_el = STEM_ELEMENT[c.day_master]
    fav = ys["favourable"]
    if not fav:
        return ""
    # ONE convention site-wide (2026-09-20): the primary medicine is yong_shen()'s
    # own first pick (weak DM → 印 before 比劫), which is what the badges, colours
    # and 喜忌 table already show. Previously this promoted the Day Master's own
    # element, so the page could say "金 primary" while the badges led with 土.
    primary, rest = fav[0], fav[1:]
    bits = [f"{primary} ({ELEMENT_EN[primary]}) primary"]
    bits += [f"{e} ({ELEMENT_EN[e]}) secondary" for e in rest]
    line = "Medicine, ranked: " + " · ".join(bits) + "."
    if dm_el == "金" and "土" in fav:
        line += (" Within 土, wet earth 濕土 (辰丑) genuinely generates 金; dry "
                 "earth 燥土 (未戌) is neutral-to-unhelpful — and the ceiling is "
                 "土多金埋: past sufficiency, more earth buries the metal it "
                 "was meant to feed.")
    return line


_BAND_ZH = {"用": "用神 the medicine", "喜": "喜神 supports the medicine",
            "忌": "忌神 works against", "仇": "仇神 feeds the opposition",
            "閒": "閒神 neutral"}


def xiji_table(c, ys: dict, pct: dict) -> list[dict]:
    """The five-band 喜忌 summary (用/喜/忌/仇/閒) by element, with each band's
    ten gods for THIS Day Master. Convention: 喜 = the element generating the
    primary 用神; 仇 = the element generating the chief 忌神; rest 閒."""
    from .bazi import ten_god
    dm_el = STEM_ELEMENT[c.day_master]
    fav, unfav = list(ys["favourable"]), list(ys["unfavourable"])
    band_of = {}
    for e in fav:
        band_of[e] = "用"
    chief_ji = unfav[0] if unfav else None
    for e in unfav:
        band_of[e] = "忌"
    xi = SHENG_REV.get(fav[0]) if fav else None
    if xi and xi not in band_of:
        band_of[xi] = "喜"
    chou = SHENG_REV.get(chief_ji) if chief_ji else None
    if chou and chou not in band_of:
        band_of[chou] = "仇"
    for e in ELEMENTS:
        band_of.setdefault(e, "閒")
    # gods of each element relative to the DM (both polarities)
    from .wuxing import STEMS
    el_gods = {}
    for st in STEMS:
        g = ten_god(c.day_master, st)
        el_gods.setdefault(STEM_ELEMENT[st], []).append(g)
    rows = []
    for band in ("用", "喜", "忌", "仇", "閒"):
        els = [e for e in ELEMENTS if band_of[e] == band]
        if not els:
            continue
        gods = [g for e in els for g in el_gods.get(e, [])]
        rows.append({"band": band, "zh": _BAND_ZH[band],
                     "elements": els, "gods": gods})
    return rows


def synthesis(c, ys: dict, pct: dict, insights: dict, windows: dict,
              tiaohou: dict | None = None) -> list[str]:
    """~6 sentences, one voice: diagnosis → mechanism → latency → arc → counsel
    → confidence. Returns a list of sentences (rendered as one paragraph)."""
    dm = c.day_master
    dm_el = STEM_ELEMENT[dm]
    weak = c.strength["verdict"].startswith("身弱")
    strong = c.strength["verdict"].startswith("身強")
    wealth, res = _grp(pct, _WEALTH), _grp(pct, _RESOURCE)
    peers, officer = _grp(pct, _PEERS), _grp(pct, _OFFICER)
    out = _grp(pct, _OUTPUT)
    S = []
    # 1 · diagnosis
    heavy = max((("財", wealth), ("官殺", officer), ("食傷", out),
                 ("印", res), ("比劫", peers)), key=lambda x: x[1])
    S.append(f"This is a {dm} {ELEMENT_EN[dm_el]} chart judged "
             f"{c.strength['verdict']} (score {c.strength['score']}), with its "
             f"weight in {heavy[0]} ({heavy[1]}%)"
             + (f" — the classical {'財旺身弱' if heavy[0] == '財' else '官旺身弱'} "
                "shape: more to hold than the hands are yet strong enough to "
                "carry." if weak and heavy[0] in ("財", "官殺") else "."))
    # 2 · mechanism (the 病): wealth element attacks the resource element by cycle
    wealth_el = KE[dm_el]
    res_el = SHENG_REV[dm_el]
    if weak and wealth >= 15 and res >= 15 and KE.get(wealth_el) == res_el:
        S.append(f"Its working friction is 貪財壞印: the {ELEMENT_EN[wealth_el]} "
                 f"wealth camp ({wealth}%) directly controls the "
                 f"{ELEMENT_EN[res_el]} resource camp ({res}%) that feeds the Day "
                 "Master — chasing outcomes starves the support system that makes "
                 "outcomes durable.")
    # 3 · latency: resource present but not rooted/visible
    rooted = {r["god"] for r in insights.get("rooted", []) if r["state"] == "rooted"}
    if res >= 15 and not (set(_RESOURCE) & rooted):
        S.append("The protective 印 is present but 藏而不透 (hidden in branches, "
                 "no rooted visible stem): support does not arrive automatically — "
                 "it works when deliberately invoked (study, mentors, credentials).")
    if peers == 0:
        S.append("With 比劫 entirely absent, self-force must be built, not "
                 "assumed: structures and allies substitute for raw stamina.")
    # 4 · decade arc
    decs = windows.get("decades", [])
    cur = next((d for d in decs if d["current"]), None)
    first_growth = next((d for d in decs if d["phase"] == "growth"), None)
    if cur and first_growth and cur is not first_growth:
        S.append(f"The present {cur['gz']} decade is {cur['phase_zh']} "
                 f"({cur['phase']}); the chart's structural season arrives with "
                 f"{first_growth['gz']} at ages {first_growth['ages']} — a "
                 "late-building arc, so the early decades are for containers, "
                 "not conquest.")
    elif cur:
        S.append(f"The present {cur['gz']} decade is {cur['phase_zh']} — "
                 "the chart is already in its supported season.")
    # 5 · counsel from 用神
    fav = "·".join(ys["favourable"])
    S.append(f"The medicine is {fav}: choose environments, colours, fields and "
             "sectors that carry it, and treat the abundant elements as weather "
             "to dress for, not fuel to add.")
    # 6 · confidence — chart-specific when the 調候 table has this cell
    if tiaohou and tiaohou.get("verdict"):
        v = tiaohou["verdict"]
        gods = "、".join(i["stem"] for i in tiaohou["gods"])
        S.append(f"Confidence note: the verdict above is the 扶抑 method's; the "
                 f"窮通寶鑑 調候 prescription for this month is {gods}, which "
                 f"{v} with it"
                 + ("." if v == "agrees" else
                    " — satisfy the climate stems through use and the 扶抑 "
                    "elements through support; both, not either."))
    else:
        S.append("Confidence note: the verdict is the 扶抑 (support-the-weak) "
                 "method's; the 調候 climate school weighs the birth season "
                 "separately and can lean differently — where the two disagree, "
                 "satisfying both is the safe posture.")
    return S


def spouse_reading(c, ys: dict, pct: dict, palaces: dict, windows: dict) -> dict:
    """The marriage/spouse block a paying client expects: star strength, palace
    condition, the operating pattern, and the activation years."""
    female = c.sex == "F"
    star_gods = _OFFICER if female else _WEALTH
    star_zh = "官殺 (husband star)" if female else "財星 (wife star)"
    share = _grp(pct, star_gods)
    band = ("prominent" if share >= 20 else "present" if share >= 8 else
            "faint" if share > 0 else "absent")
    star_line = (f"Spouse star {star_zh}: {share}% — {band}. "
                 + ("A prominent spouse star marks the theme as central; its "
                    "condition, not its size, decides the quality." if share >= 20
                    else "A quiet spouse star means the relationship follows the "
                         "palace and the years more than the natal weight."))
    sp = palaces.get("spouse", {})
    palace_line = (f"Spouse palace (day branch {sp.get('branch', '?')}): "
                   f"{sp.get('line', '')} The palace is {sp.get('state', '—')}.")
    pattern_line = ""
    if female and pct.get("傷官", 0) >= 8 and _grp(pct, ("正官",)) >= 8:
        pattern_line = ("傷官見官 in a woman's chart reads on the MARRIAGE axis "
                        "before the career one: the talent that critiques "
                        "authority also critiques the partner. Managed openly "
                        "(channel the critique into shared projects), it is "
                        "compatibility with texture, not an affliction.")
    mix_line = ""
    if female:
        natal_guan = pct.get("正官", 0) > 0
        natal_sha = pct.get("七殺", 0) + pct.get("七杀", 0) > 0
        if natal_guan != natal_sha:            # exactly one present natally
            missing = "七殺" if natal_guan else "正官"
            from .wuxing import HIDDEN_STEMS as _HS
            from .bazi import ten_god as _tg
            for d in getattr(c, "dayun", []):
                gz = str(d.gz)
                dg = {_tg(c.day_master, gz[0]),
                      _tg(c.day_master, _HS[gz[1]][0])}
                if missing in dg or missing.replace("殺", "杀") in dg:
                    mix_line = (f"Watch-window: the {gz} decade (ages "
                                f"{int(d.start_age)}–{int(d.end_age)}) introduces "
                                f"{missing} beside the natal "
                                f"{'正官' if natal_guan else '七殺'} — 官殺混雜 by "
                                "luck: two models of authority/partnership run at "
                                "once in that window; clarity about which applies "
                                "matters more than usual.")
                    break
    yrs = [y for y in windows.get("years", [])
           if y["relationship"]["flag"] != "quiet"]
    year_bits = [f"{y['y']} {y['gz']} — "
                 + ("⚠ " if y['relationship']['flag'] == 'caution' else "◉ ")
                 + y['relationship']['note'] for y in yrs[:6]]
    return {"star_line": star_line, "palace_line": palace_line,
            "pattern_line": pattern_line, "mix_line": mix_line,
            "years": year_bits,
            "source_ref": "spouse star (十神) × spouse palace (日支) × "
                          "activation years (流年) — the three-legged classical "
                          "marriage reading"}


# ---------------------------------------------------------------------------
# 綜合論斷 as a clinical report (2026-09-26). Built from the ASSEMBLED payload
# so every sentence reads the same numbers the dashboards draw. Deterministic:
# templates over fields; nothing here invents a number.
# ---------------------------------------------------------------------------
_DIR = {"坎": "N", "艮": "NE", "震": "E", "巽": "SE", "離": "S", "坤": "SW", "兌": "W", "乾": "NW"}
_GRP_EN = {"比劫": "peers", "印": "resource", "食傷": "output", "財": "wealth", "官殺": "authority"}
_SHADOW = {"比劫": "keep money and friendships in separate ledgers",
           "官殺": "budget recovery after every push",
           "財": "store before you spend",
           "食傷": "finish one thing before opening the next",
           "印": "act before you feel fully prepared"}
_NEG_STARS = ("劫煞", "空亡", "災煞", "亡神", "羊刃", "孤辰", "寡宿")


def _grp_of(g: str) -> str:
    g = g.replace("杀", "殺").replace("财", "財").replace("伤", "傷")
    if g in _PEERS: return "比劫"
    if g in _OUTPUT: return "食傷"
    if g in _WEALTH: return "財"
    if g in _OFFICER: return "官殺"
    return "印"


def _first_clause(s: str) -> str:
    return (s or "").split(" — ")[0].split("; ")[0].strip()


def clinical_report(p: dict) -> dict:
    """summary · findings · assessment · plan · confidence — the geomancer's
    report a client reads first. Every claim names its number or rule."""
    dm = p["day_master"]; dm_el = STEM_ELEMENT[dm]; en = ELEMENT_EN
    st = p["strength"]; weak = st["verdict"].startswith("身弱")
    parts = st.get("parts") or {}
    ys = p["yongshen"]; fav, unfav = list(ys["favourable"]), list(ys["unfavourable"])
    pct = p.get("tengods_pct") or {}
    legend = p.get("tengods_legend") or {}
    er = p.get("element_relations") or {}; share = er.get("share") or {}
    gods = sorted(pct.items(), key=lambda kv: -kv[1])
    g1, p1 = gods[0] if gods else ("—", 0)
    g2, p2 = gods[1] if len(gods) > 1 else ("—", 0)
    groups = {}
    for g, v in pct.items():
        groups[_grp_of(g)] = round(groups.get(_grp_of(g), 0) + v, 1)
    top_grp = max(groups.items(), key=lambda kv: kv[1]) if groups else ("—", 0)
    heavy_el = max(share.items(), key=lambda kv: kv[1])[0] if share else dm_el
    fav_en = " and ".join(en[e] for e in fav) if fav else "—"
    lack = fav[0] if fav else dm_el
    mb = p["pillars"]["month"][1]
    stage = ((p.get("pillar_extras") or {}).get("month") or {}).get("stage", "")
    season_pts = parts.get("season_pts", 0)
    season = ("out of season: the month works against it" if season_pts < 0 else
              "in season: the month carries it" if season_pts > 0 else "neutral to the month")
    # ---- summary
    summary = (f"A {'weak' if weak else 'strong'} {dm} {en[dm_el]} day master "
               f"{'carried by' if weak else 'driven by'} {_GRP_EN.get(top_grp[0], top_grp[0])} "
               f"({top_grp[0]} {top_grp[1]}%), {'short of' if weak else 'heavy in'} "
               f"{en[heavy_el] if not weak else en[lack]}: "
               f"{'supply' if weak else 'spend through'} {fav_en}, "
               f"pace {en[unfav[0]] if unfav else '—'} years.")
    F = []
    # ---- constitution
    F.append(("Constitution",
              f"{dm} {en[dm_el]} born in the {mb} month ({stage} stage): {st['verdict']}, score {st['score']}; "
              f"{(st.get('formation') or {}).get('status', '')}. {season[0].upper() + season[1:]}."))
    # ---- balance
    fav_share = ", ".join(f"{e} {en[e]} {share.get(e, 0)}%" for e in fav if e != heavy_el) if share else ""
    why = ("a weak day master is fed by its resource and its own element" if weak else
           "a strong day master spends through output, wealth and pressure")
    F.append(("Balance",
              f"{heavy_el} {en[heavy_el]} dominates the chart at {share.get(heavy_el, '—')}%"
              + (f"; {fav_share}" if fav_share else "") + ". "
              f"Medicine: {fav_en} — {why}. "
              f"Keep {'、'.join(unfav) if unfav else '—'} ({', '.join(en[e] for e in unfav)}) light — "
              f"{'they drain what the chart lacks' if weak else 'they add to what is already heavy'}."))
    # ---- drivers
    ins = p.get("tengod_insights") or {}
    favor = ins.get("favor") or []
    bad = next((f for f in favor if f.get("status") == "unfavourable"), None)
    rooted = [r for r in (ins.get("rooted") or []) if r.get("state") == "rooted"]
    axis = next((a for a in (p.get("personality") or []) if a.get("zone") and a["zone"] != "mid"), None)
    drv = (f"{g1} {legend.get(g1, {}).get('en', '')} {p1}% leads, {g2} {legend.get(g2, {}).get('en', '')} {p2}% second — "
           f"{_first_clause(legend.get(g1, {}).get('meaning', ''))}. ")
    drv += (f"{bad['god']} at {bad['pct']}% carries {bad['el']} {en.get(bad['el'], '')}, a 忌 element: it delivers, but on borrowed energy. "
            if bad else "The heavy gods all carry favourable elements: engine and medicine point the same way. ")
    if ins.get("rooted"):
        drv += f"{len(rooted)} of {len(ins['rooted'])} visible stems are rooted. "
    if axis:
        drv += f"Personality: {axis['verdict']}."
    F.append(("Drivers", drv.strip()))
    # ---- palaces & stars
    P = p.get("palaces") or {}
    sp, ch, vt = P.get("spouse") or {}, P.get("children") or {}, P.get("vault") or {}
    pal = ""
    if sp:
        pal += f"Spouse palace {sp.get('branch', '')} is {_first_clause(sp.get('state', ''))}. "
    if ch:
        pal += f"Children palace output stars {ch.get('output_share', '—')}%. "
    if vt:
        tail = (vt.get("state") or "").split(" — ")
        pal += ("Wealth vault " + (f"{vt.get('branch', '')} is {'open' if vt.get('open') else 'sealed'}"
                                    + (f"; {tail[1].split(' (')[0]}" if len(tail) > 1 else "") + ". "
                                    if vt.get("present") else "absent — wealth flows rather than stores. "))
    stars = p.get("shensha") or []
    pos = next((s for s in stars if s["star"] not in _NEG_STARS), None)
    neg = next((s for s in stars if s["star"] in _NEG_STARS), None)
    if pos:
        pal += f"{pos['star']} in the {'/'.join(pos['pillars'])} pillar: {_first_clause(pos['meaning'].split(' — ')[-1])}. "
    if neg:
        pal += f"Watch {neg['star']} in the {'/'.join(neg['pillars'])} pillar: {_first_clause(neg['meaning'].split(' — ')[-1])}."
    if not stars:
        pal += "No symbolic star is carried — the structure reads unadorned."
    F.append(("Palaces & stars", pal.strip()))
    # ---- timing now
    W = p.get("windows") or {}; T = p.get("transit") or {}; L = T.get("luck") or {}
    cur = next((d for d in W.get("decades", []) if d.get("current")), None)
    tim = ""
    if cur:
        tim += (f"The {cur['gz']} decade (ages {cur['ages']}, {cur['phase_zh']} {cur['phase']}) brings "
                f"{L.get('stem_god', '')}/{L.get('branch_god', '')}; ")
    tim += f"{T.get('year_gz', '')} this year adds {T.get('year_stem_god', '')}/{T.get('year_branch_god', '')}. "
    years = W.get("years") or []
    dims = ("career", "wealth", "relationship", "health")
    def flags(y, f): return [d for d in dims if (y.get(d) or {}).get("flag") == f]
    win = max(years, key=lambda y: len(flags(y, "window")), default=None)
    cau = max(years, key=lambda y: len(flags(y, "caution")), default=None)
    if win and flags(win, "window"):
        tim += f"Next window: {win['y']} {win['gz']} ({', '.join(flags(win, 'window'))}). "
    if cau and flags(cau, "caution"):
        tim += f"Next caution: {cau['y']} {cau['gz']} ({', '.join(flags(cau, 'caution'))})."
    F.append(("Timing now", tim.strip()))
    # ---- orientation
    yx = p.get("youxing") or {}
    dir_of = {s: _DIR.get(k, k) for k, s in yx.items()}
    best, worst = dir_of.get("生氣"), dir_of.get("絕命")
    F.append(("Orientation",
              f"{p.get('group', '')} ({p.get('gua', '')}): face {best or '—'} (生氣) for bed and desk; "
              f"keep {worst or '—'} (絕命) for storage. "
              f"Colours {'、'.join(ys.get('colours', []))} carry the medicine."))
    # ---- assessment
    A = []
    if bad and _grp_of(bad["god"]) == top_grp[0]:
        A.append(f"The chart's defining tension is that its engine is also its drain: {bad['god']} carries "
                 f"{bad['el']} {en.get(bad['el'], '')}, which a {'weak' if weak else 'strong'} {en[dm_el]} day master cannot afford to run on unchecked.")
    elif bad:
        A.append(f"The defining tension is {bad['god']} ({bad['pct']}%) on {bad['el']} {en.get(bad['el'], '')}: "
                 f"it supplies {_GRP_EN.get(_grp_of(bad['god']), '')} the chart uses, at the cost of the recovery a "
                 f"{'weak' if weak else 'strong'} day master {'needs' if weak else 'can spare'}.")
    else:
        A.append("The chart's heavy gods and its medicine point the same way: what drives this person also feeds them.")
    if parts:
        if weak and parts.get("support", 0) > parts.get("drain", 0):
            A.append(f"Support outweighs drain ({parts['support']} to {parts['drain']}) yet the {mb} month sets the verdict: "
                     "well-backed but under-lit — it needs warmth more than help.")
        elif weak:
            A.append(f"Drain exceeds support ({parts.get('drain')} to {parts.get('support')}): the chart is genuinely thin and every "
                     "favourable element added is felt.")
        elif parts.get("support", 0) > parts.get("drain", 0):
            A.append(f"Support exceeds drain ({parts['support']} to {parts['drain']}): the chart has surplus to spend, and spending it is the medicine.")
    if cur:
        A.append(f"The present {cur['gz']} decade is {cur['phase']}: "
                 + ("the timing supports building now." if cur.get("phase") in ("growth", "consolidation") else
                    "hold structure and pace effort until the next growth decade."))
    # ---- plan
    plan = []
    inds = ((p.get("industries") or {}).get("favourable") or [])
    ind = f" — fields: {inds[0]['industries'].split(',')[0].strip()}, {inds[0]['industries'].split(',')[1].strip()}" if inds and "," in inds[0].get("industries", "") else ""
    if fav:
        plan.append(f"Supply {fav[0]} {en[fav[0]]} first: {'、'.join(ys.get('colours', [])[:2])} in the rooms you spend hours in{ind}.")
    if best:
        plan.append(f"Set bed head and desk to face {best}; keep long sitting out of {worst or 'the 絕命 sector'}.")
    if win and flags(win, "window"):
        plan.append(f"Act in {win['y']} {win['gz']}" + (f"; protect {cau['y']} {cau['gz']} ({', '.join(flags(cau, 'caution'))})." if cau and flags(cau, "caution") else "."))
    doms = p.get("domains") or []
    if doms:
        low = min(doms, key=lambda d: d["score"])
        plan.append(f"Support {low['zh']} {low['en']} ({low['score']}), the lowest domain, with routine rather than effort spikes.")
    plan.append(f"Offset {g1}'s shadow: {_SHADOW.get(_grp_of(g1), '')}.")
    # ---- confidence
    th = p.get("tiaohou") or {}
    if th.get("verdict"):
        conf = (f"Method: the verdict is 扶抑's; the 窮通寶鑑 調候 prescription for the {mb} month "
                f"({'、'.join(g['stem'] for g in th.get('gods', []))}) {th['verdict']}"
                + ("." if th["verdict"] == "agrees" else " — satisfy both: climate stems through use, 扶抑 elements through support."))
    else:
        conf = "Method note: the verdict is the 扶抑 method's; the 調候 climate school can lean differently — where they disagree, satisfying both is the safe posture."
    return {"summary": summary, "findings": [{"label": l, "text": t} for l, t in F],
            "assessment": " ".join(A), "plan": plan, "confidence": conf}
