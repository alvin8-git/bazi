"""命卦 formula + full 乾/坎 rows of the published 八宅大遊年 table."""
from engine.bazhai import gua_group, ming_gua, youxing_stars


def test_family_ming_gua():
    assert ming_gua(1976, "M") == "乾"   # digit root 5 → 11-5=6
    assert ming_gua(1980, "F") == "巽"   # 9 → 9+4=13→4
    assert ming_gua(2007, "F") == "巽"
    assert ming_gua(2010, "M") == "艮"   # 3 → 11-3=8
    assert ming_gua(2015, "F") == "震"   # 8 → 8+4=12→3


def test_five_exceptions():
    # male 5 → 坤, female 5 → 艮 (e.g. 1977 male: root 6 → 11-6=5)
    assert ming_gua(1977, "M") == "坤"   # root 6 → 11-6=5 → 坤
    assert ming_gua(2008, "F") == "艮"   # root 1 → 1+4=5 → 艮


def test_groups():
    assert gua_group("乾") == "西四命 (West)"
    assert gua_group("巽") == "東四命 (East)"


def test_qian_row_published():
    # 乾命: 生氣兌, 天醫艮, 延年坤, 伏位乾, 禍害巽, 六煞坎, 五鬼震, 絕命離
    stars = youxing_stars("乾")
    assert stars == {"兌": "生氣", "艮": "天醫", "坤": "延年", "乾": "伏位",
                     "巽": "禍害", "坎": "六煞", "震": "五鬼", "離": "絕命"}


def test_kan_row_published():
    # 坎命: 生氣巽, 天醫震, 延年離, 伏位坎, 禍害兌, 六煞乾, 五鬼艮, 絕命坤
    stars = youxing_stars("坎")
    assert stars == {"巽": "生氣", "震": "天醫", "離": "延年", "坎": "伏位",
                     "兌": "禍害", "乾": "六煞", "艮": "五鬼", "坤": "絕命"}
