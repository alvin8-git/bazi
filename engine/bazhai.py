"""八宅 East/West life groups: 命卦 from 立春-bounded birth year + sex, and the
eight 遊年 stars per direction, derived from trigram line transformations
(verified against the published 乾/坎 rows in tests)."""
from __future__ import annotations

from .wuxing import PALACES

EAST_GROUP = {"坎", "離", "震", "巽"}

# line-change pattern (bottom, mid, top; True = flip) → 遊年 star
_TRANSFORM = {
    (False, False, True): "生氣",   # 上變
    (False, True, False): "絕命",   # 中變
    (True, False, False): "禍害",   # 下變
    (False, True, True): "五鬼",    # 上中變
    (True, False, True): "六煞",    # 上下變
    (True, True, False): "天醫",    # 中下變
    (True, True, True): "延年",     # 三變
    (False, False, False): "伏位",  # 不變
}
STAR_SCORE = {"生氣": 3.0, "天醫": 2.5, "延年": 2.0, "伏位": 1.0,
              "禍害": -1.0, "六煞": -1.5, "五鬼": -2.0, "絕命": -3.0}


def _digit_root(n: int) -> int:
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n


def ming_gua(lichun_year: int, sex: str) -> str:
    """命卦 by the digital-root method on the full (立春-bounded) year."""
    s = _digit_root(lichun_year)
    if sex == "M":
        g = _digit_root(11 - s)
        if g == 5:
            g = 2  # 男五寄坤
    else:
        g = _digit_root(s + 4)
        if g == 5:
            g = 8  # 女五寄艮
    return next(p for p, v in PALACES.items() if v["num"] == g)


def gua_group(gua: str) -> str:
    return "東四命 (East)" if gua in EAST_GROUP else "西四命 (West)"


def youxing_stars(gua: str) -> dict[str, str]:
    """direction palace → 遊年 star for a given 命卦."""
    base = PALACES[gua]["lines"]
    out = {}
    for palace, info in PALACES.items():
        flips = tuple(a != b for a, b in zip(base, info["lines"]))
        out[palace] = _TRANSFORM[flips]
    return out


def bazhai_citation(gua: str, palace: str, star: str) -> dict:
    return {"rule_id": f"bazhai-{star}", "layer": "bazhai",
            "source_ref": "八宅大遊年 (trigram line transformation)",
            "explanation": f"命卦 {gua} → {palace}宮 ({PALACES[palace]['dir']}) is {star}"}
