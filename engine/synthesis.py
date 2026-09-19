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
    if dm_el in fav:
        primary, rest = dm_el, [e for e in fav if e != dm_el]
    else:
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


def synthesis(c, ys: dict, pct: dict, insights: dict, windows: dict) -> list[str]:
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
    # 6 · confidence
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
