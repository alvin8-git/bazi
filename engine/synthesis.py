"""綜合論斷 — the one-voice synthesis above the reading tabs, plus the
spouse/marriage reading (audit 2026-09-19: the page answered what the engine
finds easy, not what the client came with).

Deterministic sentences assembled from fields the payload already computes:
strength, ten-god shares, rooting, 用神, decade phases. Every sentence names
its evidence; nothing here invents a number.
"""
from __future__ import annotations

import re

from .wuxing import (ELEMENT_EN, ELEMENTS, HIDDEN_STEMS, KE, SHENG,
                     SHENG_REV, STEM_ELEMENT)
from .area_reference import standing_key
from .i18n import ELEM, L, T, and_l, cap, dot, jn, zs  # noqa: F401
from .shensha import pos_label

_WEALTH = ("正財", "偏財")
_OFFICER = ("正官", "七殺")
_RESOURCE = ("正印", "偏印")
_PEERS = ("比肩", "劫財")
_OUTPUT = ("食神", "傷官")


def _grp(pct: dict, gods) -> float:
    return round(sum(pct.get(g, 0) for g in gods), 1)


def geju_line(c, lang: str = "en") -> str:
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
        frame = (T("synthesis.geju_line.01", f"no 月支藏干 is 透 — the chart frames on the 司令 "
                 f"{ruler_god} with the transparent stems as actors", lang, ruler_god=ruler_god))
    return (T("synthesis.geju_line.02", f"格局: 月令 {mb}, 本氣 {ruler} ({ruler_god}) 司令 · {frame}. "
            "The 格 names the chart's operating frame; the strength verdict "
            "below says how well the frame is carried.", lang, mb=mb, ruler=ruler, ruler_god=ruler_god, frame=frame))


def medicine_ranking(c, ys: dict, lang: str = "en") -> str:
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
    bits = [T("synthesis.medicine_ranking.01", f"{primary} ({ELEM(lang)[primary]}) primary", lang, primary=primary, primary_element_en=ELEM(lang)[primary])]
    bits += [T("synthesis.medicine_ranking.02", f"{e} ({ELEM(lang)[e]}) secondary", lang, e=e, e_element_en=ELEM(lang)[e]) for e in rest]
    line = T("synthesis.medicine_ranking.03", "Medicine, ranked: ", lang) + " · ".join(bits) + dot(lang)
    if dm_el == "金" and "土" in fav:
        line += (T("synthesis.medicine_ranking.04", " Within 土, wet earth 濕土 (辰丑) genuinely generates 金; dry "
                 "earth 燥土 (未戌) is neutral-to-unhelpful — and the ceiling is "
                 "土多金埋: past sufficiency, more earth buries the metal it "
                 "was meant to feed.", lang))
    return line


_BAND_ZH = {"用": "用神 the medicine", "喜": "喜神 supports the medicine",
            "忌": "忌神 works against", "仇": "仇神 feeds the opposition",
            "閒": "閒神 neutral"}


def xiji_table(c, ys: dict, pct: dict, lang: str = "en") -> list[dict]:
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
        rows.append({"band": band, "zh": L("synthesis._BAND_ZH", _BAND_ZH, lang)[band],
                     "elements": els, "gods": gods})
    return rows


def synthesis(c, ys: dict, pct: dict, insights: dict, windows: dict,
              tiaohou: dict | None = None, lang: str = "en") -> list[str]:
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
    S.append(T("synthesis.synthesis.01", f"This is a {dm} {ELEM(lang)[dm_el]} chart judged "
             f"{c.strength['verdict']} (score {c.strength['score']}), with its "
             f"weight in {heavy[0]} ({heavy[1]}%)", lang, dm=dm, dm_el_element_en=ELEM(lang)[dm_el], strength_verdict=c.strength['verdict'], strength_score=c.strength['score'], heavy=heavy[0], heavy_2=heavy[1])
             + (T("synthesis.synthesis.02", f" — the classical {'財旺身弱' if heavy[0] == '財' else '官旺身弱'} "
                "shape: more to hold than the hands are yet strong enough to "
                "carry.", lang, x_x='財旺身弱' if heavy[0] == '財' else '官旺身弱') if weak and heavy[0] in ("財", "官殺") else dot(lang)))
    # 2 · mechanism (the 病): wealth element attacks the resource element by cycle
    wealth_el = KE[dm_el]
    res_el = SHENG_REV[dm_el]
    if weak and wealth >= 15 and res >= 15 and KE.get(wealth_el) == res_el:
        S.append(T("synthesis.synthesis.03", f"Its working friction is 貪財壞印: the {ELEM(lang)[wealth_el]} "
                 f"wealth camp ({wealth}%) directly controls the "
                 f"{ELEM(lang)[res_el]} resource camp ({res}%) that feeds the Day "
                 "Master — chasing outcomes starves the support system that makes "
                 "outcomes durable.", lang, wealth_el_element_en=ELEM(lang)[wealth_el], wealth=wealth, res_el_element_en=ELEM(lang)[res_el], res=res))
    # 3 · latency: resource present but not rooted/visible
    rooted = {r["god"] for r in insights.get("rooted", []) if r["state"] == "rooted"}
    if res >= 15 and not (set(_RESOURCE) & rooted):
        S.append(T("synthesis.synthesis.04", "The protective 印 is present but 藏而不透 (hidden in branches, "
                 "no rooted visible stem): support does not arrive automatically — "
                 "it works when deliberately invoked (study, mentors, credentials).", lang))
    if peers == 0:
        S.append(T("synthesis.synthesis.05", "With 比劫 entirely absent, self-force must be built, not "
                 "assumed: structures and allies substitute for raw stamina.", lang))
    # 4 · decade arc
    decs = windows.get("decades", [])
    cur = next((d for d in decs if d["current"]), None)
    first_growth = next((d for d in decs if d["phase"] == "growth"), None)
    if cur and first_growth and cur is not first_growth:
        S.append(T("synthesis.synthesis.06", f"The present {cur['gz']} decade is {cur['phase_zh']} "
                 f"({cur['phase']}); the chart's structural season arrives with "
                 f"{first_growth['gz']} at ages {first_growth['ages']} — a "
                 "late-building arc, so the early decades are for containers, "
                 "not conquest.", lang, cur_gz=cur['gz'], cur_phase_zh=cur['phase_zh'], cur_phase="" if lang == "zh" else cur['phase'], first_growth_gz=first_growth['gz'], first_growth_ages=first_growth['ages']))
    elif cur:
        S.append(T("synthesis.synthesis.07", f"The present {cur['gz']} decade is {cur['phase_zh']} — "
                 "the chart is already in its supported season.", lang, cur_gz=cur['gz'], cur_phase_zh=cur['phase_zh']))
    # 5 · counsel from 用神
    fav = "·".join(ys["favourable"])
    S.append(T("synthesis.synthesis.08", f"The medicine is {fav}: choose environments, colours, fields and "
             "sectors that carry it, and treat the abundant elements as weather "
             "to dress for, not fuel to add.", lang, fav=fav))
    # 6 · confidence — chart-specific when the 調候 table has this cell
    if tiaohou and tiaohou.get("verdict"):
        v = tiaohou["verdict"]
        agrees_w = T("tiaohou.tiaohou_reading.01", "agrees", lang)
        gods = "、".join(i["stem"] for i in tiaohou["gods"])
        S.append(T("synthesis.synthesis.09", f"Confidence note: the verdict above is the 扶抑 method's; the "
                 f"窮通寶鑑 調候 prescription for this month is {gods}, which "
                 f"{v} with it", lang, gods=gods, v=v)
                 + (dot(lang) if v == agrees_w else
                    T("synthesis.synthesis.10", " — satisfy the climate stems through use and the 扶抑 "
                    "elements through support; both, not either.", lang)))
    else:
        S.append(T("synthesis.synthesis.11", "Confidence note: the verdict is the 扶抑 (support-the-weak) "
                 "method's; the 調候 climate school weighs the birth season "
                 "separately and can lean differently — where the two disagree, "
                 "satisfying both is the safe posture.", lang))
    return S


def spouse_reading(c, ys: dict, pct: dict, palaces: dict, windows: dict, lang: str = "en") -> dict:
    """The marriage/spouse block a paying client expects: star strength, palace
    condition, the operating pattern, and the activation years."""
    female = c.sex == "F"
    zh = lang == "zh"
    star_gods = _OFFICER if female else _WEALTH
    star_zh = T("synthesis.spouse_reading.01", "官殺 (husband star)", lang) if female else T("synthesis.spouse_reading.02", "財星 (wife star)", lang)
    share = _grp(pct, star_gods)
    band = (T("synthesis.spouse_reading.03", "prominent", lang) if share >= 20 else T("synthesis.spouse_reading.04", "present", lang) if share >= 8 else
            T("synthesis.spouse_reading.05", "faint", lang) if share > 0 else T("synthesis.spouse_reading.06", "absent", lang))
    star_line = (T("synthesis.spouse_reading.07", f"Spouse star {star_zh}: {share}% — {band}. ", lang, star_zh=star_zh, share=share, band=band)
                 + (T("synthesis.spouse_reading.08", "A prominent spouse star marks the theme as central; its "
                    "condition, not its size, decides the quality.", lang) if share >= 20
                    else T("synthesis.spouse_reading.09", "A quiet spouse star means the relationship follows the "
                         "palace and the years more than the natal weight.", lang)))
    sp = palaces.get("spouse", {})
    palace_line = (T("synthesis.spouse_reading.10", f"Spouse palace (day branch {sp.get('branch', '?')}): "
                   f"{sp.get('line', '')} The palace is {sp.get('state', '—')}.", lang, sp_branch=sp.get('branch', '?'), sp_line=sp.get('line', '') + ("。" if zh and sp.get('line') else ""), sp_state=sp.get('state', '—')))
    pattern_line = ""
    if female and pct.get("傷官", 0) >= 8 and _grp(pct, ("正官",)) >= 8:
        pattern_line = (T("synthesis.spouse_reading.11", "傷官見官 in a woman's chart reads on the MARRIAGE axis "
                        "before the career one: the talent that critiques "
                        "authority also critiques the partner. Managed openly "
                        "(channel the critique into shared projects), it is "
                        "compatibility with texture, not an affliction.", lang))
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
                    mix_line = (T("synthesis.spouse_reading.12", f"Watch-window: the {gz} decade (ages "
                                f"{int(d.start_age)}–{int(d.end_age)}) introduces "
                                f"{missing} beside the natal "
                                f"{'正官' if natal_guan else '七殺'} — 官殺混雜 by "
                                "luck: two models of authority/partnership run at "
                                "once in that window; clarity about which applies "
                                "matters more than usual.", lang, gz=gz, int_start_age=int(d.start_age), int_end_age=int(d.end_age), missing=missing, x_x='正官' if natal_guan else '七殺'))
                    break
    yrs = [y for y in windows.get("years", [])
           if y["relationship"]["flag"] != "quiet"]
    year_bits = [f"{y['y']} {y['gz']}{'：' if lang == 'zh' else ' — '}"
                 + ("⚠ " if y['relationship']['flag'] == 'caution' else "◉ ")
                 + y['relationship']['note'] for y in yrs[:6]]
    return {"star_line": star_line, "palace_line": palace_line,
            "pattern_line": pattern_line, "mix_line": mix_line,
            "years": year_bits,
            "source_ref": T("synthesis.spouse_reading.13", "spouse star (十神) × spouse palace (日支) × "
                          "activation years (流年) — the three-legged classical "
                          "marriage reading", lang)}


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
_MONEY_SHADOW = ("比劫", "財")
_NEG_STARS = ("劫煞", "空亡", "災煞", "亡神", "羊刃", "孤辰", "寡宿")


def _grp_of(g: str) -> str:
    g = g.replace("杀", "殺").replace("财", "財").replace("伤", "傷")
    if g in _PEERS: return "比劫"
    if g in _OUTPUT: return "食傷"
    if g in _WEALTH: return "財"
    if g in _OFFICER: return "官殺"
    return "印"


_CLAUSE = re.compile(r" — |：")        # the dash of the English sentences, the colon of the Chinese ones
_SEMI = re.compile(r"; |；")


def _clauses(s: str) -> list[str]:
    return _CLAUSE.split(s or "")


def _first_clause(s: str) -> str:
    return _SEMI.split(_clauses(s)[0])[0].strip()


def clinical_report(p: dict, lang: str = "en", minor: bool = False) -> dict:
    """summary · findings · assessment · plan · confidence — the geomancer's
    report a client reads first. Every claim names its number or rule.
    `minor` (owner 2026-10-10, no money advice under 18) leaves out the wealth-vault sentence, the wealth item of a window or caution list,
    the wealth area from the lowest-standing pick, and the shadow line that is about money. Default False: the payload hashes are unchanged."""
    dm = p["day_master"]; dm_el = STEM_ELEMENT[dm]; en = ELEM(lang)
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
    fav_en = and_l([en[e] for e in fav], lang) if fav else "—"
    lack = fav[0] if fav else dm_el
    mb = p["pillars"]["month"][1]
    stage = ((p.get("pillar_extras") or {}).get("month") or {}).get("stage", "")
    season_pts = parts.get("season_pts", 0)
    season = (T("synthesis.clinical_report.01", "out of season: the month works against it", lang) if season_pts < 0 else
              T("synthesis.clinical_report.02", "in season: the month carries it", lang) if season_pts > 0 else T("synthesis.clinical_report.03", "neutral to the month", lang))
    # ---- summary
    w_s = T("synthesis.clinical_report.05", "weak", lang) if weak else T("synthesis.clinical_report.06", "strong", lang)
    carried = T("synthesis.clinical_report.07", "carried by", lang) if weak else T("synthesis.clinical_report.08", "driven by", lang)
    grp_en = L("synthesis._GRP_EN", _GRP_EN, lang).get(top_grp[0], top_grp[0])
    short_of = T("synthesis.clinical_report.09", "short of", lang) if weak else T("synthesis.clinical_report.10", "heavy in", lang)
    heavy_name = en[heavy_el] if not weak else en[lack]
    supply = T("synthesis.clinical_report.11", "supply", lang) if weak else T("synthesis.clinical_report.12", "spend through", lang)
    pace = en[unfav[0]] if unfav else "—"
    summary = T("synthesis.clinical_report.04",
                f"A {w_s} {dm} {en[dm_el]} day master {carried} {grp_en} ({top_grp[0]} {top_grp[1]}%), {short_of} {heavy_name}: "
                f"{supply} {fav_en}, pace {pace} years.", lang,
                weak_strong=w_s, dm=dm, en_dm_el=en[dm_el], carried_driven_b=carried, _GRP_EN_top_grp=grp_en, top_grp=top_grp[0],
                top_grp_2=top_grp[1], short_of_heavy_in=short_of, en_heavy_el=heavy_name, supply_spend_th=supply, fav_en=fav_en, x=pace)
    F = []
    # ---- constitution
    F.append((T("synthesis.clinical_report.13", "Constitution", lang),
              T("synthesis.clinical_report.14", f"{dm} {en[dm_el]} born in the {mb} month ({stage} stage): {st['verdict']}, score {st['score']}; "
              f"{(st.get('formation') or {}).get('status', '')}. {cap(season, lang)}.", lang, dm=dm, en_dm_el=en[dm_el], mb=mb, stage=stage, st_verdict=st['verdict'], st_score=st['score'], x_status=(st.get('formation') or {}).get('status', ''), season_season=cap(season, lang))))
    # ---- balance
    fav_share = jn([f"{e} {share.get(e, 0)}%" if lang == "zh" else f"{e} {en[e]} {share.get(e, 0)}%"
                    for e in fav if e != heavy_el], lang) if share else ""
    why = (T("synthesis.clinical_report.15", "a weak day master is fed by its resource and its own element", lang) if weak else
           T("synthesis.clinical_report.16", "a strong day master spends through output, wealth and pressure", lang))
    drains = (T("synthesis.clinical_report.20", "they drain what the chart lacks", lang) if weak
              else T("synthesis.clinical_report.21", "they add to what is already heavy", lang))
    F.append((T("synthesis.clinical_report.17", "Balance", lang),
              T("synthesis.clinical_report.18", f"{heavy_el} {en[heavy_el]} dominates the chart at {share.get(heavy_el, '—')}%", lang, heavy_el=heavy_el, en_heavy_el=en[heavy_el], share_heavy_el=share.get(heavy_el, '—'))
              + (f"{'；' if lang == 'zh' else '; '}{fav_share}" if fav_share else "")
              + T("synthesis.clinical_report.19", f". Medicine: {fav_en} — {why}. "
                  f"Keep {'、'.join(unfav) if unfav else '—'} ({jn([en[e] for e in unfav], lang)}) light — {drains}.", lang,
                  fav_en=fav_en, why=why, x='、'.join(unfav) if unfav else '—', join_x=jn([en[e] for e in unfav], lang),
                  they_dra_they_add=drains)))
    # ---- drivers
    ins = p.get("tengod_insights") or {}
    favor = ins.get("favor") or []
    bad = next((f for f in favor if f.get("status") == "unfavourable"), None)
    rooted = [r for r in (ins.get("rooted") or []) if r.get("state") == "rooted"]
    axis = next((a for a in (p.get("personality") or []) if a.get("zone") and a["zone"] != "mid"), None)
    drv = (T("synthesis.clinical_report.22", f"{g1} {legend.get(g1, {}).get('en', '')} {p1}% leads, {g2} {legend.get(g2, {}).get('en', '')} {p2}% second — "
           f"{_first_clause(legend.get(g1, {}).get('meaning', ''))}. ", lang, g1=g1, legend_g1_en=legend.get(g1, {}).get('en', ''), p1=p1, g2=g2, legend_g2_en=legend.get(g2, {}).get('en', ''), p2=p2, first_clause_legend_g1_meani=_first_clause(legend.get(g1, {}).get('meaning', ''))))
    drv += (T("synthesis.clinical_report.23", f"{bad['god']} at {bad['pct']}% carries {bad['el']} {en.get(bad['el'], '')}, a 忌 element: it delivers, but on borrowed energy. ", lang, bad_god=bad['god'], bad_pct=bad['pct'], bad_el=bad['el'], en_bad_el=en.get(bad['el'], ''))
            if bad else T("synthesis.clinical_report.24", "The heavy gods all carry favourable elements: engine and medicine point the same way. ", lang))
    if ins.get("rooted"):
        drv += T("synthesis.clinical_report.25", f"{len(rooted)} of {len(ins['rooted'])} visible stems are rooted. ", lang, len_rooted=len(rooted), len_ins_rooted=len(ins['rooted']))
    if axis:
        drv += T("synthesis.clinical_report.26", f"Personality: {axis['verdict']}.", lang, axis_verdict=axis['verdict'])
    F.append((T("synthesis.clinical_report.27", "Drivers", lang), drv.strip()))
    # ---- palaces & stars
    P = p.get("palaces") or {}
    sp, ch, vt = P.get("spouse") or {}, P.get("children") or {}, P.get("vault") or {}
    zh = lang == "zh"
    pal = ""
    if sp:
        pal += T("synthesis.clinical_report.28", f"Spouse palace {sp.get('branch', '')} is {_first_clause(sp.get('state', ''))}. ", lang, sp_branch=sp.get('branch', ''), first_clause_sp_state=_first_clause(sp.get('state', '')))
    if ch:
        pal += T("synthesis.clinical_report.29", f"Children palace output stars {ch.get('output_share', '—')}%. ", lang, ch_output_share=ch.get('output_share', '—'))
    if vt and not minor:
        tail = _clauses(vt.get("state") or "")
        open_sealed = T("synthesis.clinical_report.32", "open", lang) if vt.get("open") else T("synthesis.clinical_report.33", "sealed", lang)
        vault_line = (T("synthesis.clinical_report.31", f"{vt.get('branch', '')} is {open_sealed}", lang, vt_branch=vt.get('branch', ''), open_sealed=open_sealed)
                      + (f"{'；' if zh else '; '}{re.split(r' \(|（', tail[1])[0]}" if len(tail) > 1 else "") + ("。" if zh else ". "))
        pal += T("synthesis.clinical_report.30", "Wealth vault ", lang) + (vault_line if vt.get("present") else
                T("synthesis.clinical_report.34", "absent — wealth flows rather than stores. ", lang))
    stars = p.get("shensha") or []
    pos = next((s for s in stars if s["star"] not in _NEG_STARS), None)
    neg = next((s for s in stars if s["star"] in _NEG_STARS), None)
    if pos:
        pal += T("synthesis.clinical_report.35", f"{pos['star']} in the {'/'.join(pos_label(x, lang) for x in pos['pillars'])} pillar: {_first_clause(_clauses(pos['meaning'])[-1])}. ", lang, pos_star=pos['star'], join_pos_pillars='/'.join(pos_label(x, lang) for x in pos['pillars']), first_clause_pos_meaning_x=_first_clause(_clauses(pos['meaning'])[-1]))
    if neg:
        pal += T("synthesis.clinical_report.36", f"Watch {neg['star']} in the {'/'.join(pos_label(x, lang) for x in neg['pillars'])} pillar: {_first_clause(_clauses(neg['meaning'])[-1])}.", lang, neg_star=neg['star'], join_neg_pillars='/'.join(pos_label(x, lang) for x in neg['pillars']), first_clause_neg_meaning_x=_first_clause(_clauses(neg['meaning'])[-1]))
    if not stars:
        pal += T("synthesis.clinical_report.37", "No symbolic star is carried — the structure reads unadorned.", lang)
    F.append((T("synthesis.clinical_report.38", "Palaces & stars", lang), pal.strip()))
    # ---- timing now
    W = p.get("windows") or {}; Tr = p.get("transit") or {}; Lk = Tr.get("luck") or {}
    cur = next((d for d in W.get("decades", []) if d.get("current")), None)
    tim = ""
    if cur:
        tim += T("synthesis.clinical_report.39", f"The {cur['gz']} decade (ages {cur['ages']}, {cur['phase_zh']} {cur['phase']}) brings "
                 f"{Lk.get('stem_god', '')}/{Lk.get('branch_god', '')}; ", lang, cur_gz=cur['gz'], cur_ages=cur['ages'], cur_phase_zh=cur['phase_zh'], cur_phase="" if zh else cur['phase'], L_stem_god=Lk.get('stem_god', ''), L_branch_god=Lk.get('branch_god', ''))
    tim += T("synthesis.clinical_report.40", f"{Tr.get('year_gz', '')} this year adds {Tr.get('year_stem_god', '')}/{Tr.get('year_branch_god', '')}. ", lang, T_year_gz=Tr.get('year_gz', ''), T_year_stem_go=Tr.get('year_stem_god', ''), T_year_branch_=Tr.get('year_branch_god', ''))
    years = W.get("years") or []
    dims = ("career", "relationship", "health") if minor else ("career", "wealth", "relationship", "health")
    def flags(y, f): return [d for d in dims if (y.get(d) or {}).get("flag") == f]
    def dims_l(ds): return jn([T(f"plain.AREA.{d}", d, lang) for d in ds], lang)
    win = max(years, key=lambda y: len(flags(y, "window")), default=None)
    cau = max(years, key=lambda y: len(flags(y, "caution")), default=None)
    if win and flags(win, "window"):
        tim += T("synthesis.clinical_report.41", f"Next window: {win['y']} {win['gz']} ({dims_l(flags(win, 'window'))}). ", lang, win_y=win['y'], win_gz=win['gz'], join_flags_win=dims_l(flags(win, 'window')))
    if cau and flags(cau, "caution"):
        tim += T("synthesis.clinical_report.42", f"Next caution: {cau['y']} {cau['gz']} ({dims_l(flags(cau, 'caution'))}).", lang, cau_y=cau['y'], cau_gz=cau['gz'], join_flags_cau=dims_l(flags(cau, 'caution')))
    F.append((T("synthesis.clinical_report.43", "Timing now", lang), tim.strip()))
    # ---- orientation
    yx = p.get("youxing") or {}
    dir_of = {s: T(f"plain.DIR_WORD.{_DIR.get(k, k)}", _DIR.get(k, k), lang) for k, s in yx.items()}
    best, worst = dir_of.get("生氣"), dir_of.get("絕命")
    F.append((T("synthesis.clinical_report.44", "Orientation", lang),
              T("synthesis.clinical_report.45", f"{p.get('group', '')} ({p.get('gua', '')}): face {best or '—'} (生氣) for bed and desk; "
              f"keep {worst or '—'} (絕命) for storage. "
              f"Colours {'、'.join(ys.get('colours', []))} carry the medicine.", lang, p_group=p.get('group', ''), p_gua=p.get('gua', ''), x=best or '—', x_2=worst or '—', join_ys_colours='、'.join(ys.get('colours', [])))))
    # ---- assessment
    A = []
    if bad and _grp_of(bad["god"]) == top_grp[0]:
        w_s2 = T("synthesis.clinical_report.47", "weak", lang) if weak else T("synthesis.clinical_report.48", "strong", lang)
        A.append(T("synthesis.clinical_report.46", f"The chart's defining tension is that its engine is also its drain: {bad['god']} carries "
                 f"{bad['el']} {en.get(bad['el'], '')}, which a {w_s2} {en[dm_el]} day master cannot afford to run on unchecked.", lang, bad_god=bad['god'], bad_el=bad['el'], en_bad_el=en.get(bad['el'], ''), weak_strong=w_s2, en_dm_el=en[dm_el]))
    elif bad:
        w_s3 = T("synthesis.clinical_report.50", "weak", lang) if weak else T("synthesis.clinical_report.51", "strong", lang)
        needs = T("synthesis.clinical_report.52", "needs", lang) if weak else T("synthesis.clinical_report.53", "can spare", lang)
        bad_grp = L("synthesis._GRP_EN", _GRP_EN, lang).get(_grp_of(bad['god']), '')
        A.append(T("synthesis.clinical_report.49", f"The defining tension is {bad['god']} ({bad['pct']}%) on {bad['el']} {en.get(bad['el'], '')}: "
                 f"it supplies {bad_grp} the chart uses, at the cost of the recovery a "
                 f"{w_s3} day master {needs}.", lang, bad_god=bad['god'], bad_pct=bad['pct'], bad_el=bad['el'], en_bad_el=en.get(bad['el'], ''), _GRP_EN_grp_of_bad_god=bad_grp, weak_strong=w_s3, needs_can_spar=needs))
    else:
        A.append(T("synthesis.clinical_report.54", "The chart's heavy gods and its medicine point the same way: what drives this person also feeds them.", lang))
    if parts:
        if weak and parts.get("support", 0) > parts.get("drain", 0):
            A.append(T("synthesis.clinical_report.55", f"Support outweighs drain ({parts['support']} to {parts['drain']}) yet the {mb} month sets the verdict: "
                     "well-backed but under-lit — it needs warmth more than help.", lang, parts_support=parts['support'], parts_drain=parts['drain'], mb=mb))
        elif weak:
            A.append(T("synthesis.clinical_report.56", f"Drain exceeds support ({parts.get('drain')} to {parts.get('support')}): the chart is genuinely thin and every "
                     "favourable element added is felt.", lang, parts_drain=parts.get('drain'), parts_support=parts.get('support')))
        elif parts.get("support", 0) > parts.get("drain", 0):
            A.append(T("synthesis.clinical_report.57", f"Support exceeds drain ({parts['support']} to {parts['drain']}): the chart has surplus to spend, and spending it is the medicine.", lang, parts_support=parts['support'], parts_drain=parts['drain']))
    if cur:
        A.append(T("synthesis.clinical_report.58", f"The present {cur['gz']} decade is {cur['phase']}: ", lang, cur_gz=cur['gz'], cur_phase=T(f"plain.PHASE.{cur['phase']}.word", cur['phase'], lang))
                 + (T("synthesis.clinical_report.59", "the timing supports building now.", lang) if cur.get("phase") in ("growth", "consolidation") else
                    T("synthesis.clinical_report.60", "hold structure and pace effort until the next growth decade.", lang)))
    # ---- plan
    plan = []
    inds = ((p.get("industries") or {}).get("favourable") or [])
    fields = re.split(r"[,、]", inds[0]["industries"]) if inds else []         # "a, b, c" in English, "a、b、c" in Chinese
    ind = (T("synthesis.clinical_report.61", f" — fields: {fields[0].strip()}, {fields[1].strip()}", lang,
             inds_industries=fields[0].strip(), inds_industries_2=fields[1].strip()) if len(fields) > 1 else "")
    if fav:
        plan.append(T("synthesis.clinical_report.62", f"Supply {fav[0]} {en[fav[0]]} first: {'、'.join(ys.get('colours', [])[:2])} in the rooms you spend hours in{ind}.", lang, fav=fav[0], en_fav=en[fav[0]], join_ys_colours='、'.join(ys.get('colours', [])[:2]), ind=ind))
    if best:
        worst_l = worst or T("synthesis.clinical_report.64", "the 絕命 sector", lang)
        plan.append(T("synthesis.clinical_report.63", f"Set bed head and desk to face {best}; keep long sitting out of {worst_l}.", lang, best=best, x=worst_l))
    if win and flags(win, "window"):
        plan.append(T("synthesis.clinical_report.65", f"Act in {win['y']} {win['gz']}", lang, win_y=win['y'], win_gz=win['gz']) + (T("synthesis.clinical_report.66", f"; protect {cau['y']} {cau['gz']} ({dims_l(flags(cau, 'caution'))}).", lang, cau_y=cau['y'], cau_gz=cau['gz'], join_flags_cau=dims_l(flags(cau, 'caution'))) if cau and flags(cau, "caution") else ("。" if zh else ".")))
    doms = [d for d in (p.get("domains") or []) if not (minor and d.get("key") == "wealth")]
    if doms:
        low = min(doms, key=standing_key)   # Layer 2: the lowest standing among charts, not the lowest raw number; the sentence still states the score
        plan.append(T("synthesis.clinical_report.67", f"Support {low['zh']} {low['en']} ({low['score']}), the domain that stands lowest among charts, with routine rather than effort spikes.", lang, low_zh=low['zh'], low_en=low['en'], low_score=low['score']))
    if not (minor and _grp_of(g1) in _MONEY_SHADOW):    # the 比劫 and 財 shadow lines are about money
        plan.append(T("synthesis.clinical_report.68", f"Offset {g1}'s shadow: {L("synthesis._SHADOW", _SHADOW, lang).get(_grp_of(g1), '')}.", lang, g1=g1, _SHADOW_grp_of_g1=L("synthesis._SHADOW", _SHADOW, lang).get(_grp_of(g1), '')))
    # ---- confidence
    th = p.get("tiaohou") or {}
    if th.get("verdict"):
        conf = (T("synthesis.clinical_report.69", f"Method: the verdict is 扶抑's; the 窮通寶鑑 調候 prescription for the {mb} month "
                f"({'、'.join(g['stem'] for g in th.get('gods', []))}) {th['verdict']}", lang, mb=mb, join_x='、'.join(g['stem'] for g in th.get('gods', [])), th_verdict=th['verdict'])
                + (dot(lang) if th["verdict"] == T("tiaohou.tiaohou_reading.01", "agrees", lang) else T("synthesis.clinical_report.70", " — satisfy both: climate stems through use, 扶抑 elements through support.", lang)))
    else:
        conf = T("synthesis.clinical_report.71", "Method note: the verdict is the 扶抑 method's; the 調候 climate school can lean differently — where they disagree, satisfying both is the safe posture.", lang)
    return {"summary": summary, "findings": [{"label": l, "text": t} for l, t in F],
            "assessment": jn(A, lang, " ", ""), "plan": plan, "confidence": conf}
