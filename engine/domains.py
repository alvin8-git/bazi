"""Tier 2: life-domain signals (career, relationship, wealth, learning) — 0–100.

Deterministic, every point cited: scores start at 50 and add auditable chips
built from ten-god shares, 神煞 stars, spouse-palace checks and 用神 fit.
Modeled on the openfate.ai 'natal theme signals' (MaleValidation2.pdf) but
computed from our own engine. Tendencies, never guarantees.
"""
from __future__ import annotations

from .shensha import is_gonghe, natal_interactions, shensha, ten_god_distribution
from .wuxing import EARTH, ELEMENTS, FIRE, KE, METAL, SHENG_REV, STEM_ELEMENT, WATER, WOOD
from .area_reference import percentile, reference_version
from .i18n import ELEM, L, T, and_l, cap, dot, jn, zs  # noqa: F401

GROUPS = {"財": ("正財", "偏財"), "官殺": ("正官", "七殺"), "印": ("正印", "偏印"),
          "比劫": ("比肩", "劫財"), "食傷": ("食神", "傷官")}
VAULT = {WOOD: "未", FIRE: "戌", METAL: "丑", WATER: "辰", EARTH: "戌"}  # 墓庫


def personality_axes(chart, lang: str = "en") -> list[dict]:
    """Five deterministic personality axes from the ten-god distribution
    (MODERN SYNTHESIS — thresholds are stated in each basis string)."""
    dist = ten_god_distribution(chart)
    total = sum(dist.values()) or 1

    def s(gods):
        return sum(dist.get(g, 0) for g in gods) / total

    e, a = s(("食神", "傷官")), s(("七殺", "劫財"))
    guan, shang = s(("正官", "七殺")), dist.get("傷官", 0) / total
    r, w, b = s(("正印", "偏印")), s(("正財", "偏財")), s(("比肩", "劫財"))
    # zone = which pole the rule landed on; it is decided from the numbers, so the verdict text can be in any language
    zones = ["right" if e >= .2 else "left" if e <= .05 else "mid",
             "right" if a >= .25 else "left" if a <= .08 else "mid",
             "left" if shang >= .15 and shang > dist.get("正官", 0) / total else "right" if guan >= .25 else "mid",
             "right" if r >= .25 and r > w else "left" if w >= .25 and w > r else "mid",
             "right" if b >= .25 else "left" if r >= .25 and e < .1 else "mid"]
    axes = [
        (T("domains.personality_axes.01", "表達 Expression", lang),
         T("domains.personality_axes.02", "expressive & outspoken", lang) if e >= .2 else
         T("domains.personality_axes.03", "reserved output", lang) if e <= .05 else T("domains.personality_axes.04", "no strong tendency", lang),
         T("domains.personality_axes.05", f"食傷 {e:.0%} (≥20% expressive, ≤5% reserved)", lang, e=e)),
        (T("domains.personality_axes.06", "行動 Action", lang),
         T("domains.personality_axes.07", "decisive — acts under pressure", lang) if a >= .25 else
         T("domains.personality_axes.08", "deliberate — needs runway", lang) if a <= .08 else T("domains.personality_axes.09", "no strong tendency", lang),
         T("domains.personality_axes.10", f"七殺+劫財 {a:.0%} (≥25% decisive, ≤8% deliberate)", lang, a=a)),
        (T("domains.personality_axes.11", "權威 Authority stance", lang),
         T("domains.personality_axes.12", "challenges rules", lang) if shang >= .15 and shang > dist.get("正官", 0) / total else
         T("domains.personality_axes.13", "works within structure", lang) if guan >= .25 else T("domains.personality_axes.14", "no strong tendency", lang),
         f"官殺 {guan:.0%}, 傷官 {shang:.0%}"),
        (T("domains.personality_axes.15", "思維 Thinking style", lang),
         T("domains.personality_axes.16", "reflective & theoretical", lang) if r >= .25 and r > w else
         T("domains.personality_axes.17", "pragmatic & concrete", lang) if w >= .25 and w > r else T("domains.personality_axes.18", "no strong tendency", lang),
         T("domains.personality_axes.19", f"印 {r:.0%} vs 財 {w:.0%} (≥25% and larger wins)", lang, r=r, w=w)),
        (T("domains.personality_axes.20", "情感 Emotional display", lang),
         T("domains.personality_axes.21", "direct & open", lang) if b >= .25 else
         ("内敛含蓄" if lang == "zh" else "contained") if r >= .25 and e < .1 else T("domains.personality_axes.22", "no strong tendency", lang),
         T("domains.personality_axes.23", f"比劫 {b:.0%}; 印 {r:.0%} with 食傷 {e:.0%}", lang, b=b, r=r, e=e)),
    ]
    # Quantitative display layer (2026-09-20): the SAME rules above, with the
    # driving percentages and which pole the verdict landed on. No new logic —
    # several axes are two-metric (the rule compares two shares), so we expose
    # the metrics rather than invent a single fake scalar.
    poles = [
        (("内敛", "reserved"), ("外放", "expressive")),
        (("审慎", "deliberate"), ("果断", "decisive")),
        (("挑战权威", "challenges rules"), ("守规矩", "works within structure")),
        (("务实", "pragmatic"), ("思辨", "reflective")),
        (("内敛含蓄", "contained"), ("直接外显", "direct & open")),
    ]
    left_kw = ("reserved", "deliberate", "challenges", "pragmatic", "contained")
    metrics = [
        [("食傷", e)],
        [("七殺+劫財", a)],
        [("官殺", guan), ("傷官", shang)],
        [("印", r), ("財", w)],
        [("比劫", b), ("印", r), ("食傷", e)],
    ]
    out = []
    for i, (ax, v, basis) in enumerate(axes):
        out.append({"axis": ax, "verdict": v, "basis": basis, "zone": zones[i],
                    "poles": {"left": {"zh": poles[i][0][0], "en": poles[i][0][1]},
                              "right": {"zh": poles[i][1][0], "en": poles[i][1][1]}},
                    "metrics": [{"label": lbl, "pct": round(100 * val, 1)}
                                for lbl, val in metrics[i]]})
    return out


_STATUS_ID = {"excess 過旺": "01", "weak 不足": "02", "watch 偏弱 (day-master element thin, 無根)": "03"}


def _status_l(status: str, lang: str = "en") -> str:
    """The reader's words for a health status (the status itself stays the English code plain.py and the page read)."""
    return T(f"domains.health_map.{_STATUS_ID[status]}", status, lang) if status in _STATUS_ID else status


def _formation(chart) -> str:
    """"follower" (從格 candidate), "dominant" (專旺 candidate) or "ordinary", from the strength numbers alone.
    Same boundaries as bazi.analyze (no 通根 and support under 12%; support over 75%). It reads no text, so it cannot depend on lang."""
    st = chart.strength
    if st.get("root_ratio", 100) == 0 and st.get("support_ratio", 100) < 12:
        return "follower"
    return "dominant" if st.get("support_ratio", 0) > 75 else "ordinary"


def _scores_as_he(i: dict) -> bool:
    """Does this day-pillar interaction count as the spouse palace being combined (日支合)? 六合 and 三合 do; a half-trine does too,
    unless it holds no cardinal branch (拱合), which the engine lists but never scores (one rule everywhere, 2026-10-15, fix 5)."""
    return "合" in i["kind"] and not (i["kind"] == "半合" and is_gonghe(i["pair"][0], i["pair"][1]))


def life_domains(chart, ys: dict, lang: str = "en") -> list[dict]:
    dist = ten_god_distribution(chart)
    total = sum(dist.values()) or 1

    def share(gods):
        return sum(dist.get(g, 0) for g in gods) / total

    stars = {s["star"] for s in shensha(chart, lang=lang)}
    strong = chart.strength["verdict"].startswith("身強")
    dm_el = STEM_ELEMENT[chart.day_master]
    day_hits = [i for i in natal_interactions(chart, lang=lang) if "day" in i["pillars"]]
    branches = [chart.pillars[p].branch for p in ("year", "month", "day", "hour")]

    spouse_gods = GROUPS["財"] if chart.sex == "M" else GROUPS["官殺"]
    officer_el = next(e for e in ELEMENTS if KE[e] == dm_el)
    spouse_el = KE[dm_el] if chart.sex == "M" else officer_el
    wealth_el = KE[dm_el]

    signals = []

    def add(key, zh, en, chips):
        chips = [c for c in chips if c]
        raw = 50 + sum(d for _, d in chips)
        score = max(5, min(95, raw))
        if raw > 95:
            chips = chips + [(T("domains.life_domains.01", "capped at 95", lang), 95 - raw)]
        band = ("prominent 强" if score >= 70 else
                "balanced 中" if score >= 45 else "needs support 待补")
        signals.append({"key": key, "zh": zh, "en": en, "score": score, "band": band,
                        "percentile": percentile(key, score), "reference_version": reference_version(),   # Layer 2: additive, never replaces score
                        "evidence": [{"label": l, "delta": d} for l, d in chips],
                        "source_ref": T("domains.life_domains.05", "structural signal — ten-god shares + 神煞 + "
                                      "palace checks (MODERN SYNTHESIS)", lang)})

    sp = share(spouse_gods)
    add("attraction", "桃花人缘", T("domains.life_domains.06", "Love & attraction", lang), [
        (T("domains.life_domains.07", "spouse star prominent", lang), 15) if sp >= .2 else
        (T("domains.life_domains.08", "spouse star present", lang), 5) if sp >= .08 else
        (T("domains.life_domains.09", "spouse star faint", lang), -5) if sp > 0 else (T("domains.life_domains.10", "spouse star absent", lang), -15),
        (T("domains.life_domains.11", "桃花 peach-blossom star", lang), 15) if "桃花" in stars else None,
        (T("domains.life_domains.12", "expressive 食傷 presence", lang), 5) if share(GROUPS["食傷"]) >= .1 else None,
        # A5 (blind review B, classified FIX): 比劫奪財. Rivals of the Day Master's own element take the wealth star that is a man's
        # spouse star (子平真詮, on 財; chapter not confirmed). A woman's spouse star is 官殺, so the chip does not apply to her.
        (T("domains.life_domains.51", "比劫 rivals crowd the wealth star", lang), -6) if chart.sex == "M" and share(GROUPS["比劫"]) >= .3 else None,
    ])

    mixed = all(dist.get(g, 0) > 0 for g in spouse_gods)
    add("stability", "感情稳定", T("domains.life_domains.13", "Relationship stability", lang), [
        # S2 (blind review B, classified FIX): the classics rank 沖 above 刑 above 害 as flaws of the spouse palace, so one flat -20
        # over-penalised 刑/害/自刑. 沖 keeps -20 (S1 is a size choice, left alone); 刑/害/自刑 take the review's -5.
        (T("domains.life_domains.14", "spouse palace clashed (日支沖)", lang), -20)
        if any(i["kind"] == "六沖" for i in day_hits) else
        (T("domains.life_domains.52", "spouse palace pressed (日支刑/害/自刑)", lang),
         # 2026-10-15 (owner): 六害 on its own presses the palace less than 刑 or 自刑 do. -2 when 六害 is the only trigger, -5 otherwise.
         -2 if all(i["kind"] == "六害" for i in day_hits if i["kind"] in ("六害", "刑", "自刑")) else -5)
        if any(i["kind"] in ("六害", "刑", "自刑") for i in day_hits) else
        (T("domains.life_domains.15", "spouse palace combined (日支合)", lang), 10)
        if any(_scores_as_he(i) for i in day_hits) else
        (T("domains.life_domains.16", "spouse palace undisturbed", lang), 5),
        # S4 (blind review B, classified FIX, the review's "wrong" row): 官殺混雜 in a woman's chart is a named classical flaw (-8);
        # mixed 正財/偏財 in a man's chart is the milder case (-4). Was a flat -10 for both.
        (T("domains.life_domains.17", "mixed 正/偏 spouse stars", lang), -4) if mixed and chart.sex == "M" else
        (T("domains.life_domains.53", "mixed 官/殺 spouse stars (官殺混雜)", lang), -8) if mixed else
        # Fix 2 (2026-10-15): "clear" needs the star to hold 8% of the chart or more, the same cut attraction uses for "present". A star under 8%
        # is "faint" there (-5), so it cannot also be a clear anchor here (+10); under 8% it earns no chip, and only an absent star costs -10.
        (T("domains.life_domains.18", "single clear spouse star", lang), 10) if sp >= .08 else
        None if sp > 0 else
        (T("domains.life_domains.19", "no spouse star to anchor", lang), -10),
        (T("domains.life_domains.20", "spouse element is favourable", lang), 10) if spouse_el in ys["favourable"] else
        (T("domains.life_domains.21", "spouse element is avoided", lang), -10) if spouse_el in ys["unfavourable"] else None,
    ])

    off = share(GROUPS["官殺"])
    add("career", "事业官星", T("domains.life_domains.22", "Career structure", lang), [
        (T("domains.life_domains.23", "authority stars prominent", lang), 15) if off >= .15 else
        (T("domains.life_domains.24", "authority stars faint", lang), -5) if off < .05 else None,
        (T("domains.life_domains.25", "power element favourable", lang), 10) if officer_el in ys["favourable"] else
        (T("domains.life_domains.26", "power element avoided — pressure", lang), -10)
        if officer_el in ys["unfavourable"] else None,
        # C3 / C4 (blind review B, classified FIX): 殺印相生 and 官印相生 need 官殺 to be present, so 印 only cushions pressure that exists.
        # The +10 cushion now needs 官殺 at 15% or more; with no 印 (under 5%) the chart loses -4, and only when 官殺 is at 15% or more.
        (T("domains.life_domains.27", "resource 印 cushions pressure", lang), 10) if off >= .15 and share(GROUPS["印"]) >= .1 else
        (T("domains.life_domains.54", "no resource 印 against pressure", lang), -4) if off >= .15 and share(GROUPS["印"]) < .05 else None,
        (T("domains.life_domains.28", "驛馬 mobility star", lang), 5) if "驛馬" in stars else None,
        (T("domains.life_domains.29", "將星 leadership star", lang), 10) if "將星" in stars else None,
        (T("domains.life_domains.30", "strong Day Master carries pressure", lang), 5) if strong else
        (T("domains.life_domains.31", "weak Day Master under pressure", lang), -5),
    ])

    wf = share(GROUPS["財"])
    add("wealth", "财富财库", T("domains.life_domains.32", "Wealth capacity", lang), [
        (T("domains.life_domains.33", "wealth stars prominent", lang), 15) if wf >= .15 else
        (T("domains.life_domains.34", "wealth stars present", lang), 5) if wf >= .08 else
        (T("domains.life_domains.35", "wealth stars faint", lang), -5) if wf > 0 else (T("domains.life_domains.36", "wealth stars absent", lang), -15),
        (T("domains.life_domains.37", "wealth element favourable", lang), 10) if wealth_el in ys["favourable"] else
        (T("domains.life_domains.38", "wealth element avoided", lang), -10) if wealth_el in ys["unfavourable"] else None,
        (T("domains.life_domains.39", "財庫 wealth vault branch present", lang), 10) if VAULT[wealth_el] in branches else None,
        (T("domains.life_domains.40", "祿神 salary star present", lang), 5) if "祿神" in stars else None,
        (T("domains.life_domains.41", "strong enough to carry wealth", lang), 10) if strong else
        (T("domains.life_domains.42", "wealth drains a weak chart — pace it", lang), -5),
    ])

    res = share(GROUPS["印"])
    add("learning", "学习文昌", T("domains.life_domains.43", "Learning structure", lang), [
        (T("domains.life_domains.44", "resource 印 prominent", lang), 20) if res >= .15 else
        (T("domains.life_domains.45", "resource 印 present", lang), 10) if res >= .08 else None,
        (T("domains.life_domains.46", "文昌/學堂 study star", lang), 15) if {"文昌貴人", "學堂"} & stars else None,
        (T("domains.life_domains.47", "華蓋 depth star", lang), 10) if "華蓋" in stars else None,
        (T("domains.life_domains.48", "expressive output supports learning", lang), 5)
        if share(GROUPS["食傷"]) >= .1 else None,
        # L2 (blind review B, classified FIX, the review's "wrong" row): thin 印 is a defect only for a weak Day Master, who needs it;
        # a strong one does not. Capped at -6 and applied as a gradient from 8% share (0) to none (-6), not a cliff at 8%.
        (T("domains.life_domains.55", "thin resource 印 for a weak Day Master", lang), -round(6 * (.08 - res) / .08))
        if not strong and res < .08 and round(6 * (.08 - res) / .08) > 0 else None,
        # L3 (blind review B, classified FIX): 官印雙全 / 官印相生, a classical learned structure (子平真詮, 論印綬 and 論正官).
        (T("domains.life_domains.56", "官印相生 authority feeds resource", lang), 5) if off >= .15 and res >= .08 else None,
        # L4 (blind review B, classified FIX, the review's "wrong as applied" row): 財壞印 (子平真詮, 論印綬). The structure bites only when
        # 印 is wanted (its element is favourable) and 比劫 are too thin (under 15%) to shield it from 財; it fires at 財 30% or more, 印 under 15%.
        (T("domains.life_domains.57", "財壞印 wealth overruns a wanted resource", lang), -6)
        if wf >= .3 and res < .15 and SHENG_REV[dm_el] in ys["favourable"] and share(GROUPS["比劫"]) < .15 else None,
    ])

    # Health = constitution tendency, read from the static natal chart on the classical basis (blind review B, Q1; owner 2026-10-11):
    # the Day Master's root (通根, 滴天髓), 中和 (滴天髓), and the supply of the 用神 (子平真詮: 用神有力無力). Base 50.
    # The TCM organ-map flags (health_map, 30% / 7%) no longer move points: the classics give no percentage cut and the engine's
    # hidden-stem weights are not a medical measure. They stay in the advice text. The classics read illness mostly through 大運
    # and 流年, so this is a tendency, not a forecast. Each chip below is a review FIX except the last, which is the H4 correction.
    w = chart.element_weights
    tw = sum(w.values()) or 1
    fav_supply = sum(w[e] for e in ys["favourable"]) / tw
    formation = _formation(chart)
    add("health", "身体底子", T("domains.life_domains.49", "Constitution", lang), [
        # H5 (FIX): 通根, the Day Master rooted in a branch's hidden stems; a rootless 日主 stands on weak ground.
        (T("domains.life_domains.58", "Day Master rooted (通根)", lang), 8) if chart.strength.get("root_ratio", 100) > 0 else
        (T("domains.life_domains.59", "Day Master rootless (無根)", lang), -5),
        # H6 (FIX): 中和 is the central classical health criterion; the strength score within 1.0 of zero counts as balanced.
        (T("domains.life_domains.60", "strength near balance (中和)", lang), 8) if abs(chart.strength["score"]) <= 1.0 else None,
        # H8 merged with H2 (FIX): 用神有力無力. The favourable elements hold 55% or more of the chart, or 35% or less.
        (T("domains.life_domains.61", "useful elements well supplied (用神有力)", lang), 6) if ys["favourable"] and fav_supply >= .55 else
        (T("domains.life_domains.62", "useful elements thin (用神無力)", lang), -5) if ys["favourable"] and fav_supply <= .35 else None,
        # H4 (blind review B, classified FIX, the review's "wrong" row): one element at 45% or more is 偏枯, except in a 專旺 or 從 chart
        # that runs with its 用神, which is a sound structure and is exempt.
        (T("domains.life_domains.63", "one element holds 45% or more (偏枯)", lang), -5)
        if max(w.values()) / tw >= .45 and formation == "ordinary" else None,
    ])

    return signals


# ---------- health & industry element maps ----------------------------------
# Traditional TCM five-element correspondences — reference, not medical advice.
ELEMENT_ORGANS = {
    WOOD: ("liver, gallbladder", "eyes, tendons; stress and frustration"),
    FIRE: ("heart, small intestine", "circulation, sleep quality; anxiety"),
    EARTH: ("spleen, stomach", "digestion, muscle tone; overthinking"),
    METAL: ("lungs, large intestine", "respiratory system, skin; grief"),
    WATER: ("kidneys, bladder", "bones, ears, hormones; fatigue and fear"),
}
ELEMENT_INDUSTRIES = {
    WOOD: "education, publishing, textiles, botany & agriculture, design",
    FIRE: "energy, F&B, media & entertainment, tech/electronics, beauty",
    EARTH: "property, construction, insurance, land & farming, HR/admin",
    METAL: "finance, engineering, hardware, automotive, law",
    WATER: "logistics & shipping, tourism, trading, beverages, communication",
}


def health_map(chart, lang: str = "en") -> list[dict]:
    """Per-element balance vs the TCM organ systems (weak ≤7%, excess ≥30%)."""
    from .wuxing import ELEMENTS, ELEMENT_EN, STEM_ELEMENT
    w = chart.element_weights
    total = sum(w.values()) or 1
    out = []
    dm_el = STEM_ELEMENT[chart.day_master]
    rootless = chart.strength.get("root_ratio", 100) == 0
    for e in ELEMENTS:
        share = w[e] / total
        status = ("excess 過旺" if share >= .30 else
                  "weak 不足" if share <= .07 else
                  # audit 2026-09-19: the Day Master's OWN element, thin and 無根,
                  # deserves a watch flag even above the absolute 7% floor
                  "watch 偏弱 (day-master element thin, 無根)"
                  if e == dm_el and rootless and share <= .15 else "balanced")
        organs, aspects = L("domains.ELEMENT_ORGANS", ELEMENT_ORGANS, lang)[e]
        out.append({"element": e, "en": ELEM(lang)[e], "share": round(100 * share, 1),
                    "organs": organs, "aspects": aspects, "status": status})
    return out


def industry_map(ys: dict, lang: str = "en") -> dict:
    """用神 elements → classical industry families (career-direction hint)."""
    from .wuxing import ELEMENT_EN
    return {"favourable": [{"element": e, "en": ELEM(lang)[e],
                            "industries": L("domains.ELEMENT_INDUSTRIES", ELEMENT_INDUSTRIES, lang)[e]}
                           for e in ys["favourable"]],
            "avoid": [{"element": e, "en": ELEM(lang)[e],
                       "industries": L("domains.ELEMENT_INDUSTRIES", ELEMENT_INDUSTRIES, lang)[e]}
                      for e in ys["unfavourable"]]}
