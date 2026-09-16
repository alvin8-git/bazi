"""面相 (face reading) rule engine — PoC.

Input: geometric DESCRIPTORS (ratios measured from facial landmarks — see
scripts/mianxiang_poc.py for the landmark pipeline). Output: readings where
EVERY entry carries rule_id / source_ref / explanation, mirroring the
citation pattern of yongshen/shensha. Deterministic: same descriptors, same
reading, forever.

Encoded canon (PoC subset — the classical core, uncontroversial across
schools): 三停 three courts (麻衣神相), 五行形 five-element face shapes
(麻衣神相/柳庄相法), a 十二宫 subset (命宫, 田宅宫, 财帛宫), and 五官
proportion reads (eyes 监察官, brows 保寿官, nose 审辨官, mouth 出纳官).
Ears (采听官) are deliberately absent: face-mesh landmarks do not measure
ears reliably, and we do not fake what we cannot measure.

Descriptor contract (all ratios, resolution-independent):
  court_upper / court_middle / court_lower : the 三停 heights, summing ~1
  face_wh          : face width / face height
  jaw_ratio        : jaw width / cheekbone width
  forehead_ratio   : forehead width / cheekbone width
  eye_gap_ratio    : inner-canthus gap / one eye width   (~1.0 canonical)
  brow_eye_gap     : brow-to-eye gap / face height        (田宅宫)
  brow_len_ratio   : brow length / eye width              (保寿官)
  nose_ratio       : nose width / face width
  mouth_nose_ratio : mouth width / nose width             (出纳官)
"""
from __future__ import annotations

# 五行形 classification thresholds (calibrated on canonical proportion lore:
# 木 long, 金 square, 水 round/full, 火 wide-brow narrow-jaw, 土 heavy square)
# ponytail: coarse threshold classifier, refine with measured population data
_COURTS_BALANCED_TOL = 0.045     # each court within ±4.5% of a third


def _entry(rule_id, zh, source, explanation, reading):
    return {"rule_id": rule_id, "zh": zh, "source_ref": source,
            "explanation": explanation, "reading": reading}


def _courts(d):
    thirds = [("upper", "上停", d["court_upper"], "early years 15–30 · 天"),
              ("middle", "中停", d["court_middle"], "middle years 31–50 · 人"),
              ("lower", "下停", d["court_lower"], "later years 51+ · 地")]
    out = []
    if all(abs(v - 1 / 3) <= _COURTS_BALANCED_TOL for _, _, v, _ in thirds):
        out.append(_entry(
            "sancting-balanced", "三停平等", "麻衣神相·三停",
            "the three courts are near-equal (each within ±4.5% of a third)",
            "三停平等 — the classical mark of an even, steady life arc: no "
            "phase of life dominates or starves the others."))
    else:
        longest = max(thirds, key=lambda t: t[2])
        shortest = min(thirds, key=lambda t: t[2])
        out.append(_entry(
            f"sancting-long-{longest[0]}", f"{longest[1]}偏长", "麻衣神相·三停",
            f"{longest[1]} measures {longest[2]:.0%} of face height "
            f"(balanced = 33%)",
            f"{longest[1]} is the strongest court — the {longest[3]} phase "
            "carries the most natural momentum."))
        out.append(_entry(
            f"sancting-short-{shortest[0]}", f"{shortest[1]}偏短", "麻衣神相·三停",
            f"{shortest[1]} measures {shortest[2]:.0%} of face height",
            f"{shortest[1]} is the leanest court — the {shortest[3]} phase "
            "rewards deliberate preparation rather than momentum."))
    return out


def _face_shape(d):
    wh, jaw, fh = d["face_wh"], d["jaw_ratio"], d["forehead_ratio"]
    if wh < 0.74:
        elem, zh, why = "木", "木形 (long)", f"width/height {wh:.2f} < 0.74"
        reading = ("木形 — the tree: growth-minded, principled, benevolent "
                   "(仁). Suits long-arc careers; thrives with room to grow.")
    elif wh >= 0.74 and jaw >= 0.92 and fh >= 0.88:
        elem, zh, why = "金", "金形 (square)", (
            f"width/height {wh:.2f}, jaw {jaw:.2f} and forehead {fh:.2f} "
            "both broad — square outline")
        reading = ("金形 — the metal square: decisive, dutiful, justice-"
                   "minded (义). Executes; suits structure and authority.")
    elif wh >= 0.86 and jaw >= 0.88:
        elem, zh, why = "水", "水形 (round)", (
            f"width/height {wh:.2f} with full rounded outline")
        reading = ("水形 — the water round: adaptive, sociable, resourceful "
                   "(智). Flows around obstacles; suits people-facing work.")
    elif fh >= 0.92 and jaw <= 0.80:
        elem, zh, why = "火", "火形 (pointed)", (
            f"broad forehead {fh:.2f} tapering to narrow jaw {jaw:.2f}")
        reading = ("火形 — the fire taper: quick, expressive, propriety-"
                   "keyed (礼). Ignites projects; needs earth-type ballast.")
    else:
        elem, zh, why = "土", "土形 (solid)", (
            f"width/height {wh:.2f}, jaw {jaw:.2f}, forehead {fh:.2f} — "
            "even, grounded outline")
        reading = ("土形 — the earth square: stable, trustworthy (信), "
                   "load-bearing. The classical anchor shape.")
    e = _entry(f"wuxingxing-{elem}", zh, "麻衣神相·五行形 / 柳庄相法",
               why, reading)
    e["element"] = elem
    return e


def _palaces(d):
    out = []
    eg = d["eye_gap_ratio"]
    if eg >= 0.95:
        out.append(_entry(
            "minggong-broad", "命宫开阔", "麻衣神相·十二宫·命宫",
            f"inter-brow/eye gap ratio {eg:.2f} ≥ 0.95 (canonical one eye-"
            "width)",
            "命宫 (the seal between the brows) is open — the classical sign "
            "of an unobstructed outlook; setbacks pass through rather than "
            "lodge."))
    else:
        out.append(_entry(
            "minggong-narrow", "命宫偏窄", "麻衣神相·十二宫·命宫",
            f"inter-brow/eye gap ratio {eg:.2f} < 0.95",
            "命宫 runs narrow — classically read as a tendency to hold "
            "worries close; the remedy is procedural, not facial: decide, "
            "write down, release."))
    beg = d["brow_eye_gap"]
    if beg >= 0.055:
        out.append(_entry(
            "tianzhai-wide", "田宅宫宽", "麻衣神相·十二宫·田宅宫",
            f"brow-to-eye gap {beg:.3f} of face height ≥ 0.055",
            "田宅宫 (brow–eye field) is generous — classically linked to "
            "ease with property and inheritance matters."))
    else:
        out.append(_entry(
            "tianzhai-tight", "田宅宫紧", "麻衣神相·十二宫·田宅宫",
            f"brow-to-eye gap {beg:.3f} of face height",
            "田宅宫 sits tight — property affairs reward double-checking "
            "paperwork rather than trusting momentum."))
    nr = d["nose_ratio"]
    if nr >= 0.26:
        out.append(_entry(
            "caibo-full", "财帛宫丰", "麻衣神相·十二宫·财帛宫",
            f"nose width {nr:.2f} of face width ≥ 0.26",
            "财帛宫 (the nose, seat of wealth) reads full — classical sign "
            "of holding power over money once earned."))
    else:
        out.append(_entry(
            "caibo-fine", "财帛宫清", "麻衣神相·十二宫·财帛宫",
            f"nose width {nr:.2f} of face width",
            "财帛宫 reads fine rather than full — wealth style favours flow "
            "and precision over accumulation; budgeting systems suit it."))
    return out


def _officers(d):
    out = []
    bl = d["brow_len_ratio"]
    out.append(_entry(
        "baoshou-brow", "眉·保寿官", "五官·保寿官",
        f"brow length {bl:.2f}× eye width "
        f"({'reaches past' if bl >= 1.0 else 'falls short of'} the eye)",
        "眉长过目 — brows clearing the eye mark the classical 保寿官 ideal: "
        "steady vitality and sibling/peer support." if bl >= 1.0 else
        "眉不及目 — shorter brows classically read as self-reliance over "
        "peer support; alliances are built, not assumed."))
    mn = d["mouth_nose_ratio"]
    out.append(_entry(
        "chunna-mouth", "口·出纳官", "五官·出纳官",
        f"mouth width {mn:.2f}× nose width "
        f"({'≥' if mn >= 1.5 else '<'} 1.5 canonical)",
        "口大容拳 in miniature — a generous mouth marks the 出纳官 at full "
        "strength: expression, appetite for life, income through voice." if mn >= 1.5 else
        "口小于度 — a finer mouth reads as considered speech; output gains "
        "from preparation and loses from improvisation."))
    return out


def analyze(descriptors: dict) -> dict:
    """Full PoC reading from a descriptor dict. Every entry cites its rule."""
    d = descriptors
    shape = _face_shape(d)
    return {
        "face_shape": shape,
        "courts": _courts(d),
        "palaces": _palaces(d),
        "officers": _officers(d),
        "cross_ref_note": (
            "面相 is one lens. The classical cross-check is agreement with "
            "the BaZi chart — e.g. a 金形 face on a person whose 用神 is "
            "metal is reinforcement; on one whose 忌神 is metal it flags "
            "tension worth reading closely. This cross-reference is the "
            "planned bazifor.me integration."),
        "disclaimer": (
            "PoC scope: proportions only, from a single front-facing photo. "
            "Classical practice also reads colour/qi (气色), moles, and "
            "profile — none of which this measures. Ears (采听官) are "
            "excluded because landmarks cannot measure them reliably."),
    }


if __name__ == "__main__":
    # self-check: balanced synthetic face must produce the canonical reads
    balanced = {"court_upper": 1 / 3, "court_middle": 1 / 3, "court_lower": 1 / 3,
                "face_wh": 0.78, "jaw_ratio": 0.93, "forehead_ratio": 0.9,
                "eye_gap_ratio": 1.0, "brow_eye_gap": 0.06,
                "brow_len_ratio": 1.05, "nose_ratio": 0.27,
                "mouth_nose_ratio": 1.6}
    r = analyze(balanced)
    assert r["courts"][0]["rule_id"] == "sancting-balanced"
    assert r["face_shape"]["element"] == "金"
    assert all("source_ref" in e for e in
               [r["face_shape"], *r["courts"], *r["palaces"], *r["officers"]])
    narrow = dict(balanced, face_wh=0.70)
    assert analyze(narrow)["face_shape"]["element"] == "木"
    print("mianxiang self-check ok")
