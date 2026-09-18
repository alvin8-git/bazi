"""玄空飛星: natal (運盤/山星/向星), annual and monthly stars, plus 兼向/替卦
replacement-star charts and 騎線 dual-chart boundary handling (boundary_info,
natal_chart_from_degrees).

The evaluation year/period are runtime parameters everywhere (eng review
architectural constraint) — never hardcoded. Validated against the published
八運乾山巽向 旺山旺向 chart and the 八運辰山戌向兼 替卦成旺山旺向 result in tests.
"""
from __future__ import annotations

from .wuxing import (FLIGHT_ORDER, MOUNTAIN_ORDER, MOUNTAINS, NUM_TO_PALACE,
                     OPPOSITE_MOUNTAIN, PALACES, STAR_ELEMENT,
                     mountain_of_degrees, mountain_palace, mountain_yuan)

# 替卦 replacement stars (沈氏玄空 兼向訣): 子癸甲申→貪狼1 · 壬卯乙未坤→巨門2
# · 戌乾亥辰巽巳→武曲6 · 酉辛丑艮丙→破軍7 · 寅午庚丁→右弼9. 五黃無替.
TIGUA = {"子": 1, "癸": 1, "甲": 1, "申": 1,
         "壬": 2, "卯": 2, "乙": 2, "未": 2, "坤": 2,
         "戌": 6, "乾": 6, "亥": 6, "辰": 6, "巽": 6, "巳": 6,
         "酉": 7, "辛": 7, "丑": 7, "艮": 7, "丙": 7,
         "寅": 9, "午": 9, "庚": 9, "丁": 9}


def _fly(center: int, forward: bool) -> dict[str, int]:
    """Fill palaces in Luoshu flight order from a center star."""
    out = {}
    n = center
    for palace in FLIGHT_ORDER:
        out[palace] = (n - 1) % 9 + 1
        n = n + 1 if forward else n - 1
    return out


def base_chart(period: int) -> dict[str, int]:
    """運盤: period star in the center, flown forward."""
    return _fly(period, forward=True)


def _polarity_for(star: int, mountain_of_chart: str) -> bool:
    """順/逆 for a 山星/向星: the star's trigram palace holds three mountains;
    take the one in the same 元 category as the sitting/facing mountain.

    When the star is 5 (中宮 has no mountains), borrow the polarity of the
    corresponding 元 mountain of the palace the star flew FROM (the
    sitting/facing palace itself) — the common 起星 rule. The 兼向
    replacement-star (替卦) pass shipped when the TowerB compass reading
    landed at 307° — see natal_chart(use_tigua=) and TIGUA above.
    """
    yuan = mountain_yuan(mountain_of_chart)
    if star == 5:
        ref_palace = mountain_palace(mountain_of_chart)
    else:
        ref_palace = NUM_TO_PALACE[star]
    return MOUNTAINS[ref_palace][yuan][1]


def _ref_mountain(star: int, mountain_of_chart: str) -> str:
    """The mountain whose polarity (and, for 替卦, replacement star) governs
    the flight of a 山星/向星 — same lookup as _polarity_for."""
    yuan = mountain_yuan(mountain_of_chart)
    ref_palace = (mountain_palace(mountain_of_chart) if star == 5
                  else NUM_TO_PALACE[star])
    return MOUNTAINS[ref_palace][yuan][0]


def _tigua_center(star: int, mountain_of_chart: str) -> int:
    """兼向: the star that actually flies is the ref mountain's 替卦 star.
    五黃無替 — a 5 flies as itself (no mountain of its own to replace)."""
    if star == 5:
        return 5
    return TIGUA[_ref_mountain(star, mountain_of_chart)]


def natal_chart(period: int, facing_mountain: str, use_tigua: bool = False) -> dict:
    """Full natal chart: per-palace (運盤, 山星, 向星). use_tigua=True builds
    the 兼向替卦 chart (replacement centers, same polarities — 沈氏玄空)."""
    sitting = OPPOSITE_MOUNTAIN[facing_mountain]
    base = base_chart(period)
    sit_palace, face_palace = mountain_palace(sitting), mountain_palace(facing_mountain)

    mstar_center = base[sit_palace]
    m_fly = _tigua_center(mstar_center, sitting) if use_tigua else mstar_center
    mstars = _fly(m_fly, _polarity_for(mstar_center, sitting))
    wstar_center = base[face_palace]
    w_fly = _tigua_center(wstar_center, facing_mountain) if use_tigua else wstar_center
    wstars = _fly(w_fly, _polarity_for(wstar_center, facing_mountain))

    palaces = {p: {"base": base[p], "mountain": mstars[p], "water": wstars[p]}
               for p in FLIGHT_ORDER}
    # full classical taxonomy: each wang star is at the sitting, at the facing,
    # or exiled off-axis (出宮 — only possible under 替卦 replacement charts).
    # 上山下水 strictly requires the INVERSION (山星下水 AND 向星上山); the old
    # fallthrough mislabelled off-axis charts as 上山下水 (validation E2/W1).
    wang_shan = palaces[sit_palace]["mountain"] == period      # 山星到坐 旺山
    wang_xiang = palaces[face_palace]["water"] == period       # 向星到向 旺向
    shan_xiashui = palaces[face_palace]["mountain"] == period  # 山星下水
    xiang_shangshan = palaces[sit_palace]["water"] == period   # 向星上山
    if wang_shan and wang_xiang:
        structure = "旺山旺向"
    elif shan_xiashui and wang_xiang:
        structure = "雙星到向"
    elif wang_shan and xiang_shangshan:
        structure = "雙星到坐"
    elif shan_xiashui and xiang_shangshan:
        structure = "上山下水"
    elif wang_shan:
        structure = "旺山"                       # 向星出宮
    elif wang_xiang:
        structure = "旺向"                       # 山星出宮
    elif shan_xiashui:
        structure = "山星下水·向星出宮"
    elif xiang_shangshan:
        structure = "向星上山·山星出宮"
    else:
        structure = "旺星出宮"
    kind = "替卦" if use_tigua else "下卦"
    return {"period": period, "facing": facing_mountain, "sitting": sitting,
            "facing_palace": face_palace, "sitting_palace": sit_palace,
            "palaces": palaces,
            "structure": structure, "chart_type": kind,
            "citations": [{
                "rule_id": "xuankong-natal", "layer": "xuankong",
                "source_ref": f"{period}運 {sitting}山{facing_mountain}向 ({kind})",
                "explanation": f"period {period}, sitting {sit_palace}, facing {face_palace}; "
                               f"structure {'旺山旺向' if wang_shan and wang_xiang else 'see chart'}"}]}


def boundary_info(facing_deg: float) -> dict:
    """Where a facing sits inside its 15° mountain (兼向/騎線 detection).

    正向 |offset| ≤ 3° → normal 下卦 chart; 兼向 3–6.5° → 替卦 chart;
    騎線 within 1° of the boundary (≥6.5°) → both neighbouring charts must be
    considered — the compass reading itself decides which mountain rules.
    """
    m = mountain_of_degrees(facing_deg)
    idx = MOUNTAIN_ORDER.index(m)
    offset = ((facing_deg - idx * 15 + 180) % 360) - 180
    zone = ("正向" if abs(offset) <= 3 else
            "騎線" if abs(offset) >= 6.5 else "兼向")
    neighbor = MOUNTAIN_ORDER[(idx + (1 if offset > 0 else -1)) % 24]
    return {"mountain": m, "offset_deg": round(offset, 1), "zone": zone,
            "neighbor": neighbor,
            "rule_id": "xuankong-jianxiang", "layer": "xuankong",
            "source_ref": "兼向/替卦 (沈氏玄空) — 正向 ≤3° · 兼向 3–6.5° 用替 · "
                          "騎線 ≥6.5° 兩盤並列",
            "explanation": f"facing {facing_deg}° = {m} {offset:+.1f}° from centre "
                           f"({zone}); neighbouring mountain {neighbor}"}


def natal_chart_from_degrees(period: int, facing_deg: float) -> dict:
    """Degree-aware chart: applies 替卦 automatically for 兼向/騎線 facings and
    attaches the boundary analysis (TODO 兼向替卦, triggered by TowerB 307°)."""
    info = boundary_info(facing_deg)
    chart = natal_chart(period, info["mountain"], use_tigua=info["zone"] != "正向")
    chart["facing_deg"] = facing_deg
    chart["boundary"] = info
    chart["citations"].append(info)
    if info["zone"] == "騎線":
        alt = natal_chart(period, info["neighbor"], use_tigua=True)
        chart["alternate"] = alt
        chart["citations"].append({
            "rule_id": "xuankong-qixian", "layer": "xuankong",
            "source_ref": "騎線/空亡 — reading within 1° of the mountain boundary",
            "explanation": f"chart shown for {info['mountain']} (替卦) but the true "
                           f"facing may be {info['neighbor']}: alternate chart "
                           f"{alt['sitting']}山{alt['facing']}向 {alt['structure']} "
                           "attached; a ±1° compass error flips the verdict"})
    return chart


def annual_star(year: int) -> int:
    """流年紫白 center star, 立春-bounded year (2000 → 9白, decreasing yearly)."""
    return (9 - (year - 2000)) % 9 or 9


def annual_chart(year: int) -> dict[str, int]:
    return _fly(annual_star(year), forward=True)


# Star quality, parameterized by period (never hardcoded to an era).
def star_quality(star: int, period: int) -> tuple[float, str]:
    nxt = period % 9 + 1
    nxt2 = nxt % 9 + 1
    prev = (period - 2) % 9 + 1
    if star == period:
        return 2.0, f"當運旺星 ({star})"
    if star == nxt:
        return 1.5, f"生氣星 ({star}, next period)"
    if star == 5:
        return -2.0, "五黃 廉貞 — most afflictive"
    if star == 2:
        return -1.5, "二黑 病符 — illness star"
    if star == 3:
        return -1.0, "三碧 是非 — conflict star"
    if star == nxt2:
        return 1.0, f"進氣星 ({star})"
    if star == prev:
        return -0.5, f"退氣星 ({star})"
    if star in (1, 6):
        return 0.5, f"吉白星 ({star})"
    return 0.0, f"平星 ({star})"


def star_element(star: int) -> str:
    return STAR_ELEMENT[star]


def palace_direction(palace: str) -> str:
    return "C" if palace == "中" else PALACES[palace]["dir"]


# ---- classical cross-checks (blindspot audit 2026-09-18: C1, C5, F10) ----

_SANBAN = ({1, 4, 7}, {2, 5, 8}, {3, 6, 9})
_YUAN_NAME = {0: "地元", 1: "天元", 2: "人元"}
_PALACE_RING = ["坎", "艮", "震", "巽", "離", "坤", "兌", "乾"]  # clockwise
_SHENGCHENG = ({1, 6}, {2, 7}, {3, 8}, {4, 9})


def jian_class(facing_deg: float) -> dict:
    """Two-axis 兼向 classification (audit C1): degree offset AND whether the
    兼 stays inside the facing mountain's own trigram (同卦相兼) or crosses out
    (出卦兼). Lineages that reserve 替卦 for 出卦兼 chart a 同卦 兼向 as 下卦;
    the engine's uniform ±3° rule is one lineage's election — this function
    exposes the other axis so verdicts can disclose both readings."""
    info = boundary_info(facing_deg)
    m, nb = info["mountain"], info["neighbor"]
    same_gua = mountain_palace(m) == mountain_palace(nb)
    pair = f'{_YUAN_NAME[mountain_yuan(m)]}兼{_YUAN_NAME[mountain_yuan(nb)]}'
    return {**info, "same_gua": same_gua,
            "jian_kind": ("同卦相兼" if same_gua else "出卦兼"),
            "yuan_pair": pair,
            "note": (f"{m}兼{nb} = {pair} "
                     + ("within one trigram — 沈氏/無常派 practice charts this "
                        "下卦; the ±3° 替卦 rule is the stricter election"
                        if same_gua else
                        "ACROSS the trigram boundary — a true 出卦, the worst "
                        "class of 兼; many lineages disqualify rather than 用替"))}


def classical_checks(chart: dict) -> dict:
    """合十 / 父母三般卦 / 全盤伏吟·反吟 screens (audit C5). 伏吟/反吟 are
    tested against the 元旦盤 (Luoshu resident numbers): full-盤 伏吟 when a
    star chart reproduces the Luoshu, 反吟 when it mirrors it (sum 10)."""
    pal = chart["palaces"]
    luoshu = {p: PALACES[p]["num"] for p in FLIGHT_ORDER if p != "中"}
    luoshu["中"] = 5
    def _all(f):
        return all(f(p) for p in FLIGHT_ORDER)
    heshi_shan = _all(lambda p: pal[p]["base"] + pal[p]["mountain"] == 10)
    heshi_xiang = _all(lambda p: pal[p]["base"] + pal[p]["water"] == 10)
    sanban = _all(lambda p: any(
        {pal[p]["base"], pal[p]["mountain"], pal[p]["water"]} <= s
        for s in _SANBAN))
    out = {"合十": ("山盤合十" if heshi_shan else "向盤合十" if heshi_xiang
                    else None),
           "父母三般卦": sanban}
    for key, star in (("山", "mountain"), ("向", "water")):
        fuyin = _all(lambda p: pal[p][star] == luoshu[p])
        fanyin = _all(lambda p: pal[p][star] + luoshu[p] == 10)
        out[f"{key}盤伏吟"] = fuyin
        out[f"{key}盤反吟"] = fanyin
    out["clean"] = not any((out["山盤伏吟"], out["山盤反吟"],
                            out["向盤伏吟"], out["向盤反吟"]))
    return out


def chengmen(period: int, facing_mountain: str) -> list[dict]:
    """城門訣 (沈氏 method, audit C5/F10): the two palaces flanking the facing
    palace are gate candidates. A gate WORKS when the 運盤 star resident there,
    flown from the centre with the yin/yang of its own trigram's 天元 mountain,
    returns the current period star to that palace. 五黃 cannot open a gate.
    正城門 = the flank in 生成 pair with the facing palace's Luoshu number."""
    face_pal = mountain_palace(facing_mountain)
    i = _PALACE_RING.index(face_pal)
    base = base_chart(period)
    out = []
    for flank in (_PALACE_RING[(i - 1) % 8], _PALACE_RING[(i + 1) % 8]):
        b = base[flank]
        if b == 5:
            out.append({"palace": flank, "valid": False, "why": "運盤五黃無門"})
            continue
        yang = MOUNTAINS[NUM_TO_PALACE[b]][1][1]        # 天元龍 polarity
        arrived = _fly(b, forward=yang)[flank]
        pair = {PALACES[face_pal]["num"], PALACES[flank]["num"]}
        rank = "正城門" if any(pair == s for s in _SHENGCHENG) else "副城門"
        out.append({"palace": flank, "valid": arrived == period, "rank": rank,
                    "why": f"運盤{b} {'順' if yang else '逆'}飛 → {arrived}"})
    return out
