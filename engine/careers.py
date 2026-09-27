"""Rule-based career-path ranking — the Career Compass, computable.

Fifteen career archetypes, each scored on three cited terms:
  field  — the archetype's element(s) against the person's 用神 lists
  style  — ten-god shares matching its working style (counted at >=8%)
  talent — 神煞 stars that specifically serve it
Deterministic, no LLM; every reason names the rule that moved the score.
"Fit" means effort converts to reward efficiently — low ranks are priced
against the chart, never forbidden.
"""
from __future__ import annotations

from .shensha import shensha, ten_god_pct

GOD_STYLE = {
    "正官": "rules, legitimacy and diligence",
    "七殺": "decisive authority — thrives under pressure",
    "正印": "deep study and absorbed knowledge",
    "偏印": "unconventional methods and niche expertise",
    "比肩": "steady self-driven effort",
    "劫財": "peer networks and competitive drive",
    "食神": "product sense and craft output",
    "傷官": "expression, performance and persuasion",
    "正財": "patient, steady accumulation",
    "偏財": "opportunity-spotting and deal-making",
}

# key, en, zh, field elements, working-style gods {god: weight}, stars {star: bonus}
ARCHETYPES = [
    ("research", "Research & analysis", "研究分析", ["水"],
     {"正印": 2, "偏印": 2}, {"華蓋": 6, "學堂": 6, "文昌貴人": 6, "太極貴人": 6}),
    ("engineering", "Engineering & technical craft", "工程技术", ["金"],
     {"正官": 2, "食神": 1}, {"文昌貴人": 6}),
    ("tech", "Tech & software product", "科技产品", ["火"],
     {"食神": 2, "傷官": 1, "偏印": 1}, {}),
    ("teaching", "Teaching & training", "教育培训", ["木"],
     {"正印": 2, "傷官": 2}, {"學堂": 6}),
    ("media", "Communications & media", "传播媒体", ["水", "火"],
     {"傷官": 2, "劫財": 1}, {"桃花": 6}),
    ("law", "Law & compliance", "法律合规", ["金"],
     {"正官": 3}, {"文昌貴人": 6, "將星": 6}),
    ("finance", "Finance & investment", "金融投资", ["金"],
     {"正財": 2, "偏財": 1, "正官": 1}, {}),
    ("trading", "Trading & business development", "贸易商务", ["水"],
     {"偏財": 3, "劫財": 1}, {"驛馬": 6}),
    ("venture", "Entrepreneurship", "创业经营", [],
     {"偏財": 2, "七殺": 2, "食神": 1}, {"祿神": 6}),
    ("management", "Management & operations", "管理运营", ["土"],
     {"七殺": 2, "正官": 1, "正印": 1}, {"將星": 6}),
    ("public", "Public service & institutions", "公共机构", ["土"],
     {"正官": 2, "正印": 1}, {"將星": 6, "天乙貴人": 6}),
    ("property", "Property & asset stewardship", "产业资管", ["土"],
     {"正財": 2, "正印": 1}, {}),
    ("logistics", "Logistics & mobility", "物流运输", ["水"],
     {"七殺": 1, "偏財": 1}, {"驛馬": 10}),
    ("design", "Design & aesthetics", "设计美学", ["木", "火"],
     {"傷官": 2, "食神": 1}, {"桃花": 6}),
    ("care", "Care & wellbeing professions", "健康照护", ["木"],
     {"正印": 2, "食神": 1}, {"天德貴人": 4, "月德貴人": 4}),
]


def career_paths(chart, ys: dict, top: int = 5) -> dict:
    pct = ten_god_pct(chart)
    stars = {s["star"] for s in shensha(chart)}
    fav, unfav = set(ys["favourable"]), set(ys["unfavourable"])
    scored = []
    for key, en, zh, elements, gods, star_bonus in ARCHETYPES:
        score, reasons, negs = 0.0, [], []
        if elements:
            score += sum(12 if e in fav else -12 if e in unfav else 0
                         for e in elements) / len(elements)
            for e in elements:
                if e in fav:
                    reasons.append(f"field element {e} is a favourable 用神")
                elif e in unfav:
                    negs.append(f"field element {e} is on the avoid list")
        else:
            reasons.append("field-agnostic — pick the venture's domain from "
                           "the favourable elements")
        for god, w in gods.items():
            p = pct.get(god, 0)
            if p >= 8:
                score += w * p / 10
                reasons.append(f"{god} {p:.0f}% — {GOD_STYLE[god]}")
        for star, bonus in star_bonus.items():
            if star in stars:
                score += bonus
                reasons.append(f"{star} star serves this path")
        scored.append({"key": key, "en": en, "zh": zh,
                       "score": round(score, 1),
                       "reasons": reasons or ["no supporting structure"],
                       "negs": negs})
    scored.sort(key=lambda a: -a["score"])
    avoid = [{"en": a["en"], "zh": a["zh"], "score": a["score"],
              "reasons": a["negs"] or ["no supporting structure in the chart"]}
             for a in scored[-2:]]
    for a in scored:
        a.pop("negs")
    return {"top": scored[:top], "avoid": avoid,
            "source_ref": "career archetype ranking — 用神 field elements + "
                          "ten-god style + 神煞 (MODERN SYNTHESIS)"}


# ---- roles for today's economy (2026-09-27; docs/designs/pair-compatibility-deep-dive.md §D) ----
# role, field elements, working-style gods (first weighs 2, rest 1), parent archetype keys, firm|arguable
ROLES = [
    ("Data scientist", "水", ["正印", "偏印"], ["research"], "arguable"),
    ("Machine-learning engineer", "火", ["食神", "傷官", "偏印"], ["tech"], "firm"),
    ("Software engineer", "金火", ["正官", "食神", "傷官"], ["engineering", "tech"], "arguable"),
    ("DevOps / SRE", "金", ["正官", "食神"], ["engineering"], "firm"),
    ("Cybersecurity analyst", "金", ["七殺", "正官"], ["engineering", "law"], "arguable"),
    ("Product manager", "火", ["傷官", "七殺"], ["venture", "management"], "arguable"),
    ("UX / UI designer", "木火", ["傷官", "食神"], ["design"], "firm"),
    ("Growth marketer", "水火", ["傷官", "劫財"], ["media"], "firm"),
    ("Social media creator", "火", ["傷官"], ["media"], "arguable"),
    ("Content strategist", "木", ["傷官", "正印", "劫財"], ["teaching", "media"], "arguable"),
    ("Podcaster", "火", ["傷官", "劫財"], ["media"], "firm"),
    ("Video editor", "火", ["食神"], ["design", "media"], "arguable"),
    ("Game designer", "木火", ["傷官", "食神"], ["design"], "firm"),
    ("Esports coach", "木", ["正印", "傷官"], ["teaching"], "arguable"),
    ("E-commerce seller", "水", ["偏財", "劫財"], ["trading"], "firm"),
    ("Logistics / supply-chain planner", "水", ["七殺", "偏財"], ["logistics"], "firm"),
    ("Fintech product manager", "金火", ["正財", "偏財", "正官"], ["finance", "tech"], "arguable"),
    ("Crypto / derivatives trader", "水", ["偏財", "劫財"], ["trading"], "arguable"),
    ("ESG / sustainability analyst", "木土", ["正印", "傷官"], ["research", "teaching"], "arguable"),
    ("HR business partner", "土", ["正官", "正印"], ["public"], "firm"),
    ("Recruiter", "水火", ["偏財", "傷官"], ["trading", "media"], "arguable"),
    ("Paralegal", "金", ["正官"], ["law"], "firm"),
    ("Compliance officer", "金", ["正官"], ["law"], "firm"),
    ("Teacher / tutor", "木", ["正印", "傷官"], ["teaching"], "firm"),
    ("Edtech product manager", "木火", ["正印", "食神", "傷官"], ["teaching", "tech"], "arguable"),
    ("Nurse practitioner", "木", ["正印", "食神"], ["care"], "arguable"),
    ("Physiotherapist", "木", ["正印", "食神"], ["care"], "firm"),
    ("Pharmacist", "金木", ["正官", "正印"], ["engineering", "care"], "arguable"),
    ("Biomedical researcher", "水", ["正印", "偏印"], ["research"], "firm"),
    ("Life coach / therapist", "木火", ["正印", "食神", "傷官"], ["care", "media"], "arguable"),
    ("Real-estate agent", "土", ["偏財", "正財"], ["property", "trading"], "firm"),
    ("Property manager", "土", ["正財", "正印"], ["property"], "firm"),
    ("Chef / F&B founder", "火", ["食神", "偏財", "七殺"], ["venture"], "firm"),
    ("Barista", "火", ["食神"], ["care"], "arguable"),
    ("Event / wedding planner", "火土", ["傷官", "正財"], ["media", "property"], "arguable"),
    ("Interior designer", "木火", ["傷官", "食神"], ["design"], "firm"),
    ("Architect", "金木", ["正官", "傷官", "食神"], ["engineering", "design"], "arguable"),
    ("Civil engineer", "金", ["正官", "食神"], ["engineering"], "firm"),
    ("Drone / robotics operator", "金", ["正官", "食神"], ["engineering"], "firm"),
]
_ARCH_EN = {a[0]: a[1] for a in ARCHETYPES}


def career_roles(chart, ys: dict, top: int = 8) -> dict:
    """Present-day roles scored by the SAME rules as the archetypes: field
    element vs 用神 (±12 averaged), ten-god style at ≥8% (first god ×2)."""
    pct = ten_god_pct(chart)
    fav, unfav = set(ys["favourable"]), set(ys["unfavourable"])
    scored = []
    for role, els, gods, parents, basis in ROLES:
        score, reasons = 0.0, []
        if els:
            score += sum(12 if e in fav else -12 if e in unfav else 0 for e in els) / len(els)
            for e in els:
                if e in fav:
                    reasons.append(f"field element {e} is a favourable 用神")
                elif e in unfav:
                    reasons.append(f"field element {e} is on the avoid list")
        for i, god in enumerate(gods):
            p = pct.get(god, 0)
            if p >= 8:
                w = 2 if i == 0 else 1
                score += w * p / 10
                reasons.append(f"{god} {p:.0f}% — {GOD_STYLE[god]}")
        scored.append({"role": role, "elements": list(els), "score": round(score, 1),
                       "reasons": reasons or ["no supporting structure"], "basis": basis,
                       "parent": " / ".join(_ARCH_EN.get(k, k) for k in parents)})
    scored.sort(key=lambda a: -a["score"])
    return {"top": scored[:top],
            "source_ref": "roles mapped onto the archetype rules — 用神 field elements + "
                          "ten-god style; element assignments per deep-dive §D (MODERN SYNTHESIS)"}
