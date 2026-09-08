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
    wang_shan = palaces[sit_palace]["mountain"] == period
    wang_xiang = palaces[face_palace]["water"] == period
    # 雙星 refinements: both period-stars gathered at one palace
    shuang_xiang = (palaces[face_palace]["mountain"] == period and wang_xiang)
    shuang_zuo = (wang_shan and palaces[sit_palace]["water"] == period)
    structure = ("旺山旺向" if wang_shan and wang_xiang else
                 "雙星到向" if shuang_xiang else
                 "雙星到坐" if shuang_zuo else
                 "上山下水" if not wang_shan and not wang_xiang else
                 "旺山" if wang_shan else "旺向")
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
