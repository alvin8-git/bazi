"""The join: person chart × house chart → per-direction ScoreBreakdown.

Three transparent layers (design premise 5):
  ① 八宅命卦 match (classical)
  ② 玄空飛星 sector star quality (classical)
  ③ 喜用神 element match — labeled "modern synthesis", no classical lineage
Weights are visible and adjustable; total = Σ contributions (eng review 1A).
"""
from __future__ import annotations

from .bazhai import STAR_SCORE, bazhai_citation, ming_gua, gua_group, youxing_stars
from .bazi import Chart
from .wuxing import CENTER_ELEMENT, PALACES, STAR_ELEMENT
from .xuankong import star_quality

DEFAULT_WEIGHTS = {"bazhai": 0.4, "xuankong": 0.4, "yongshen": 0.2}


def score_direction(chart: Chart, ys: dict, natal: dict, annual: dict[str, int],
                    palace: str, weights: dict | None = None) -> dict:
    """ScoreBreakdown for one person in one palace/direction sector."""
    w = weights or DEFAULT_WEIGHTS
    breakdown = []

    gua = ming_gua(chart.lichun_year, chart.sex)
    if palace == "中":
        bz_pts, bz_cit = 0.0, {"rule_id": "bazhai-center", "layer": "bazhai",
                               "source_ref": "八宅", "explanation": "中宮 has no 遊年 star"}
    else:
        star = youxing_stars(gua)[palace]
        bz_pts = STAR_SCORE[star]
        bz_cit = bazhai_citation(gua, palace, star)
    breakdown.append({**bz_cit, "weight": w["bazhai"],
                      "contribution": round(bz_pts * w["bazhai"], 3)})

    stars = natal["palaces"][palace]
    mq, mwhy = star_quality(stars["mountain"], natal["period"])
    wq, wwhy = star_quality(stars["water"], natal["period"])
    aq, awhy = star_quality(annual[palace], natal["period"])
    xk_pts = 0.5 * mq + 0.3 * wq + 0.2 * aq   # bedrooms: 山星 dominant
    breakdown.append({
        "rule_id": "xuankong-sector", "layer": "xuankong",
        "source_ref": f"{natal['period']}運 {natal['sitting']}山{natal['facing']}向 + 流年",
        "explanation": f"山星 {stars['mountain']} ({mwhy}); 向星 {stars['water']} ({wwhy}); "
                       f"流年 {annual[palace]} ({awhy})",
        "weight": w["xuankong"], "contribution": round(xk_pts * w["xuankong"], 3)})

    dir_el = CENTER_ELEMENT if palace == "中" else PALACES[palace]["element"]
    water_el = STAR_ELEMENT[stars["water"]]
    ys_pts = 0.0
    hits = []
    for el, label in ((dir_el, "direction"), (water_el, "向星")):
        if el in ys["favourable"]:
            ys_pts += 1.0
            hits.append(f"{label} element {el} is favourable")
        elif el in ys["unfavourable"]:
            ys_pts -= 0.5
            hits.append(f"{label} element {el} is unfavourable")
    breakdown.append({
        "rule_id": "yongshen-sector-match", "layer": "yongshen",
        "source_ref": "MODERN SYNTHESIS — builder's own rule, no classical lineage (premise 5)",
        "explanation": "; ".join(hits) or "no favourable/unfavourable element present",
        "weight": w["yongshen"], "contribution": round(ys_pts * w["yongshen"], 3)})

    total = round(sum(b["contribution"] for b in breakdown), 3)
    return {"person": chart.person, "palace": palace,
            "direction": "C" if palace == "中" else PALACES[palace]["dir"],
            "gua": gua, "group": gua_group(gua),
            "total": total, "breakdown": breakdown}


def score_all_directions(chart: Chart, ys: dict, natal: dict,
                         annual: dict[str, int]) -> list[dict]:
    scores = [score_direction(chart, ys, natal, annual, p)
              for p in natal["palaces"]]
    return sorted(scores, key=lambda s: -s["total"])
