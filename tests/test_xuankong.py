"""Flying stars vs published references.

八運乾山巽向 is a published 旺山旺向 chart:
  base: 中8 乾9 兌1 艮2 離3 坎4 坤5 震6 巽7
  山星 (from 9, 天元午 yin → reverse): 中9 乾8 兌7 艮6 離5 坎4 坤3 震2 巽1
  向星 (from 7, 天元酉 yin → reverse): 中7 乾6 兌5 艮4 離3 坎2 坤1 震9 巽8
"""
from engine.xuankong import (annual_chart, annual_star, base_chart, natal_chart,
                             star_quality)


def test_base_chart_period8():
    assert base_chart(8) == {"中": 8, "乾": 9, "兌": 1, "艮": 2, "離": 3,
                             "坎": 4, "坤": 5, "震": 6, "巽": 7}


def test_qianshan_xunxiang_period8_full_grid():
    n = natal_chart(8, "巽")           # facing 巽 = 乾山巽向
    assert n["sitting"] == "乾" and n["structure"] == "旺山旺向"
    m = {p: v["mountain"] for p, v in n["palaces"].items()}
    w = {p: v["water"] for p, v in n["palaces"].items()}
    assert m == {"中": 9, "乾": 8, "兌": 7, "艮": 6, "離": 5, "坎": 4, "坤": 3, "震": 2, "巽": 1}
    assert w == {"中": 7, "乾": 6, "兌": 5, "艮": 4, "離": 3, "坎": 2, "坤": 1, "震": 9, "巽": 8}
    assert n["palaces"][n["sitting_palace"]]["mountain"] == 8   # 旺山
    assert n["palaces"][n["facing_palace"]]["water"] == 8       # 旺向


def test_annual_stars_published():
    # 2000=9白 anchor, decreasing yearly: 2024=3, 2025=2, 2026=1
    assert annual_star(2024) == 3
    assert annual_star(2025) == 2
    assert annual_star(2026) == 1
    assert annual_chart(2026)["中"] == 1


def test_star_quality_period_parameterized():
    assert star_quality(8, 8)[0] == 2.0     # 當運 in P8
    assert star_quality(9, 8)[0] == 1.5     # 生氣 in P8
    assert star_quality(8, 9)[0] == -0.5    # 退氣 in P9 — same star, other period
    assert star_quality(9, 9)[0] == 2.0
    assert star_quality(5, 8)[0] == -2.0 and star_quality(2, 9)[0] == -1.5


def test_double_star_structures():
    """雙星 refinements (TowerC exposed these): both period-stars at one palace."""
    from engine.xuankong import natal_chart
    assert natal_chart(8, "壬")["structure"] == "雙星到向"   # TowerC 丙山壬向 P8
    assert natal_chart(9, "壬")["structure"] == "雙星到坐"
    assert natal_chart(9, "乾")["structure"] == "雙星到向"   # TowerB P9 refined
    assert natal_chart(8, "巽")["structure"] == "旺山旺向"   # unchanged classics
    assert natal_chart(8, "乾")["structure"] == "旺山旺向"


def test_tigua_boundary_zones():
    from engine.xuankong import boundary_info
    assert boundary_info(135)["zone"] == "正向"            # TowerA 巽 centre
    assert boundary_info(343)["zone"] == "正向"            # TowerC 壬 −2°
    b = boundary_info(307)                                 # TowerB compass reading
    assert (b["mountain"], b["offset_deg"], b["zone"], b["neighbor"]) == \
        ("戌", 7.0, "騎線", "乾")
    assert boundary_info(305)["zone"] == "兼向"            # 戌 +5°


def test_tigua_chen_xu_p8_wangshanwangxiang():
    """Published 沈氏玄空 result: 八運 辰山戌向 兼向用替 → 旺山旺向
    (the 下卦 chart of the same axis is 上山下水)."""
    from engine.xuankong import natal_chart
    xia = natal_chart(8, "戌")
    ti = natal_chart(8, "戌", use_tigua=True)
    assert xia["structure"] == "上山下水" and xia["chart_type"] == "下卦"
    assert ti["structure"] == "旺山旺向" and ti["chart_type"] == "替卦"
    assert ti["palaces"]["巽"]["mountain"] == 8            # 山星8 at sitting
    assert ti["palaces"]["乾"]["water"] == 8               # 向星8 at facing


def test_tigua_no_replacement_when_stars_match():
    """八運 巽山乾向: both replacement stars equal the originals (酉→7, 午→9)
    so the 替卦 chart is identical to the 下卦 chart (替而不變)."""
    from engine.xuankong import natal_chart
    xia, ti = natal_chart(8, "乾"), natal_chart(8, "乾", use_tigua=True)
    assert xia["palaces"] == ti["palaces"]
    assert xia["structure"] == ti["structure"] == "旺山旺向"


def test_qixian_attaches_alternate_chart():
    from engine.xuankong import natal_chart_from_degrees
    n = natal_chart_from_degrees(8, 307)                   # TowerB
    assert n["chart_type"] == "替卦" and n["boundary"]["zone"] == "騎線"
    assert n["structure"] == "旺山旺向"                     # 辰山戌向兼 用替
    alt = n["alternate"]
    assert alt["facing"] == "乾" and alt["structure"] == "旺山旺向"
    # both boundary charts agree on the headline structure — but sector
    # details differ (e.g. N water star 3 vs 4), so both are surfaced
    assert n["palaces"]["坎"]["water"] != alt["palaces"]["坎"]["water"]
