"""Tier 2: life-domain signals (career, relationship, wealth, learning) — 0–100.

Deterministic, every point cited: scores start at 50 and add auditable chips
built from ten-god shares, 神煞 stars, spouse-palace checks and 用神 fit.
Modeled on the openfate.ai 'natal theme signals' (MaleValidation2.pdf) but
computed from our own engine. Tendencies, never guarantees.
"""
from __future__ import annotations

from .shensha import natal_interactions, shensha, ten_god_distribution
from .wuxing import EARTH, ELEMENTS, FIRE, KE, METAL, STEM_ELEMENT, WATER, WOOD

GROUPS = {"財": ("正財", "偏財"), "官殺": ("正官", "七殺"), "印": ("正印", "偏印"),
          "比劫": ("比肩", "劫財"), "食傷": ("食神", "傷官")}
VAULT = {WOOD: "未", FIRE: "戌", METAL: "丑", WATER: "辰", EARTH: "戌"}  # 墓庫


def personality_axes(chart) -> list[dict]:
    """Five deterministic personality axes from the ten-god distribution
    (MODERN SYNTHESIS — thresholds are stated in each basis string)."""
    dist = ten_god_distribution(chart)
    total = sum(dist.values()) or 1

    def s(gods):
        return sum(dist.get(g, 0) for g in gods) / total

    e, a = s(("食神", "傷官")), s(("七殺", "劫財"))
    guan, shang = s(("正官", "七殺")), dist.get("傷官", 0) / total
    r, w, b = s(("正印", "偏印")), s(("正財", "偏財")), s(("比肩", "劫財"))
    axes = [
        ("表達 Expression",
         "expressive & outspoken" if e >= .2 else
         "reserved output" if e <= .05 else "no strong tendency",
         f"食傷 {e:.0%} (≥20% expressive, ≤5% reserved)"),
        ("行動 Action",
         "decisive — acts under pressure" if a >= .25 else
         "deliberate — needs runway" if a <= .08 else "no strong tendency",
         f"七殺+劫財 {a:.0%} (≥25% decisive, ≤8% deliberate)"),
        ("權威 Authority stance",
         "challenges rules" if shang >= .15 and shang > dist.get("正官", 0) / total else
         "works within structure" if guan >= .25 else "no strong tendency",
         f"官殺 {guan:.0%}, 傷官 {shang:.0%}"),
        ("思維 Thinking style",
         "reflective & theoretical" if r >= .25 and r > w else
         "pragmatic & concrete" if w >= .25 and w > r else "no strong tendency",
         f"印 {r:.0%} vs 財 {w:.0%} (≥25% and larger wins)"),
        ("情感 Emotional display",
         "direct & open" if b >= .25 else
         "contained" if r >= .25 and e < .1 else "no strong tendency",
         f"比劫 {b:.0%}; 印 {r:.0%} with 食傷 {e:.0%}"),
    ]
    return [{"axis": ax, "verdict": v, "basis": basis} for ax, v, basis in axes]


def life_domains(chart, ys: dict) -> list[dict]:
    dist = ten_god_distribution(chart)
    total = sum(dist.values()) or 1

    def share(gods):
        return sum(dist.get(g, 0) for g in gods) / total

    stars = {s["star"] for s in shensha(chart)}
    strong = chart.strength["verdict"].startswith("身強")
    dm_el = STEM_ELEMENT[chart.day_master]
    day_hits = [i for i in natal_interactions(chart) if "day" in i["pillars"]]
    branches = [chart.pillars[p].branch for p in ("year", "month", "day", "hour")]

    spouse_gods = GROUPS["財"] if chart.sex == "M" else GROUPS["官殺"]
    officer_el = next(e for e in ELEMENTS if KE[e] == dm_el)
    spouse_el = KE[dm_el] if chart.sex == "M" else officer_el
    wealth_el = KE[dm_el]

    signals = []

    def add(key, zh, en, chips):
        chips = [c for c in chips if c]
        score = max(5, min(95, 50 + sum(d for _, d in chips)))
        band = ("prominent 强" if score >= 70 else
                "balanced 中" if score >= 45 else "needs support 待补")
        signals.append({"key": key, "zh": zh, "en": en, "score": score, "band": band,
                        "evidence": [{"label": l, "delta": d} for l, d in chips],
                        "source_ref": "structural signal — ten-god shares + 神煞 + "
                                      "palace checks (MODERN SYNTHESIS)"})

    sp = share(spouse_gods)
    add("attraction", "桃花人缘", "Love & attraction", [
        ("spouse star prominent", 15) if sp >= .2 else
        ("spouse star present", 5) if sp >= .08 else
        ("spouse star faint", -5) if sp > 0 else ("spouse star absent", -15),
        ("桃花 peach-blossom star", 15) if "桃花" in stars else None,
        ("expressive 食傷 presence", 5) if share(GROUPS["食傷"]) >= .1 else None,
    ])

    mixed = all(dist.get(g, 0) > 0 for g in spouse_gods)
    add("stability", "感情稳定", "Relationship stability", [
        ("spouse palace clashed (日支沖/害/刑)", -20)
        if any(i["kind"] in ("六沖", "六害", "刑", "自刑") for i in day_hits) else
        ("spouse palace combined (日支合)", 10)
        if any("合" in i["kind"] for i in day_hits) else
        ("spouse palace undisturbed", 5),
        ("mixed 正/偏 spouse stars", -10) if mixed else
        ("single clear spouse star", 10) if sp > 0 else
        ("no spouse star to anchor", -10),
        ("spouse element is favourable", 10) if spouse_el in ys["favourable"] else
        ("spouse element is avoided", -10) if spouse_el in ys["unfavourable"] else None,
    ])

    off = share(GROUPS["官殺"])
    add("career", "事业官星", "Career structure", [
        ("authority stars prominent", 15) if off >= .15 else
        ("authority stars faint", -5) if off < .05 else None,
        ("power element favourable", 10) if officer_el in ys["favourable"] else
        ("power element avoided — pressure", -10)
        if officer_el in ys["unfavourable"] else None,
        ("resource 印 cushions pressure", 10) if share(GROUPS["印"]) >= .1 else None,
        ("驛馬 mobility star", 5) if "驛馬" in stars else None,
        ("將星 leadership star", 10) if "將星" in stars else None,
        ("strong Day Master carries pressure", 5) if strong else
        ("weak Day Master under pressure", -5),
    ])

    wf = share(GROUPS["財"])
    add("wealth", "财富财库", "Wealth capacity", [
        ("wealth stars prominent", 15) if wf >= .15 else
        ("wealth stars present", 5) if wf >= .08 else
        ("wealth stars faint", -5) if wf > 0 else ("wealth stars absent", -15),
        ("wealth element favourable", 10) if wealth_el in ys["favourable"] else
        ("wealth element avoided", -10) if wealth_el in ys["unfavourable"] else None,
        ("財庫 wealth vault branch present", 10) if VAULT[wealth_el] in branches else None,
        ("祿神 salary star present", 5) if "祿神" in stars else None,
        ("strong enough to carry wealth", 10) if strong else
        ("wealth drains a weak chart — pace it", -5),
    ])

    res = share(GROUPS["印"])
    add("learning", "学习文昌", "Learning structure", [
        ("resource 印 prominent", 20) if res >= .15 else
        ("resource 印 present", 10) if res >= .08 else None,
        ("文昌/學堂 study star", 15) if {"文昌貴人", "學堂"} & stars else None,
        ("華蓋 depth star", 10) if "華蓋" in stars else None,
        ("expressive output supports learning", 5)
        if share(GROUPS["食傷"]) >= .1 else None,
    ])

    imbal = [h for h in health_map(chart) if h["status"] != "balanced"]
    add("health", "身体底子", "Constitution", [
        (f'{h["element"]} {h["status"]} — {h["organs"]}', -8) for h in imbal
    ] or [("five elements in workable balance", 20)])

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


def health_map(chart) -> list[dict]:
    """Per-element balance vs the TCM organ systems (weak ≤7%, excess ≥30%)."""
    from .wuxing import ELEMENTS, ELEMENT_EN
    w = chart.element_weights
    total = sum(w.values()) or 1
    out = []
    for e in ELEMENTS:
        share = w[e] / total
        status = ("excess 過旺" if share >= .30 else
                  "weak 不足" if share <= .07 else "balanced")
        organs, aspects = ELEMENT_ORGANS[e]
        out.append({"element": e, "en": ELEMENT_EN[e], "share": round(100 * share, 1),
                    "organs": organs, "aspects": aspects, "status": status})
    return out


def industry_map(ys: dict) -> dict:
    """用神 elements → classical industry families (career-direction hint)."""
    from .wuxing import ELEMENT_EN
    return {"favourable": [{"element": e, "en": ELEMENT_EN[e],
                            "industries": ELEMENT_INDUSTRIES[e]}
                           for e in ys["favourable"]],
            "avoid": [{"element": e, "en": ELEMENT_EN[e],
                       "industries": ELEMENT_INDUSTRIES[e]}
                      for e in ys["unfavourable"]]}
