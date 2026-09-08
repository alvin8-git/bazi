"""Validates the full 干支/五行 tables against classical references (3A)."""
from engine import wuxing as w


def test_stem_elements_complete():
    assert [w.STEM_ELEMENT[s] for s in w.STEMS] == [
        w.WOOD, w.WOOD, w.FIRE, w.FIRE, w.EARTH, w.EARTH,
        w.METAL, w.METAL, w.WATER, w.WATER]
    assert [s for s in w.STEMS if w.STEM_YANG[s]] == list("甲丙戊庚壬")


def test_branch_elements_complete():
    assert [w.BRANCH_ELEMENT[b] for b in w.BRANCHES] == [
        w.WATER, w.EARTH, w.WOOD, w.WOOD, w.EARTH, w.FIRE,
        w.FIRE, w.EARTH, w.METAL, w.METAL, w.EARTH, w.WATER]
    assert [b for b in w.BRANCHES if w.BRANCH_YANG[b]] == list("子寅辰午申戌")


def test_hidden_stems_reference():
    expect = {"子": "癸", "丑": "己癸辛", "寅": "甲丙戊", "卯": "乙", "辰": "戊乙癸",
              "巳": "丙庚戊", "午": "丁己", "未": "己丁乙", "申": "庚壬戊", "酉": "辛",
              "戌": "戊辛丁", "亥": "壬甲"}
    assert {b: "".join(v) for b, v in w.HIDDEN_STEMS.items()} == expect


def test_sheng_ke_cycles():
    # each element generates exactly one and controls exactly one, both cycles cover all 5
    assert set(w.SHENG) == set(w.SHENG.values()) == set(w.ELEMENTS)
    assert set(w.KE) == set(w.KE.values()) == set(w.ELEMENTS)
    assert w.SHENG[w.WOOD] == w.FIRE and w.KE[w.WOOD] == w.EARTH
    assert w.SHENG[w.WATER] == w.WOOD and w.KE[w.METAL] == w.WOOD


def test_chong_he_pairs():
    assert w.CHONG_MAP["子"] == "午" and w.CHONG_MAP["寅"] == "申"
    assert w.HE_MAP["辰"] == "酉" and w.HE_MAP["午"] == "未"
    assert len(w.CHONG_MAP) == 12 and len(w.HE_MAP) == 12


def test_luoshu_palaces():
    assert {p: v["num"] for p, v in w.PALACES.items()} == {
        "坎": 1, "坤": 2, "震": 3, "巽": 4, "乾": 6, "兌": 7, "艮": 8, "離": 9}
    assert w.PALACES["巽"]["dir"] == "SE" and w.PALACES["乾"]["dir"] == "NW"


def test_24_mountains():
    assert len(w.MOUNTAIN_ORDER) == 24
    assert w.mountain_of_degrees(0) == "子"
    assert w.mountain_of_degrees(135) == "巽"
    assert w.mountain_of_degrees(120) == "辰"      # SE1
    assert w.mountain_of_degrees(150) == "巳"      # SE3
    assert w.OPPOSITE_MOUNTAIN["巽"] == "乾"
    assert w.OPPOSITE_MOUNTAIN["子"] == "午"
    # polarity spot-checks (地元,天元,人元)
    assert w.MOUNTAINS["乾"] == [("戌", False), ("乾", True), ("亥", True)]
    assert w.MOUNTAINS["兌"] == [("庚", True), ("酉", False), ("辛", False)]
    assert w.mountain_yuan("乾") == 1 and w.mountain_yuan("庚") == 0
