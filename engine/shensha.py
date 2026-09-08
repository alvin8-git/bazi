"""神煞 symbolic stars, natal branch interactions, ten-god distribution (Tier 1).

All pure lookup tables from classical rhymes (天乙: 甲戊庚牛羊…), verified against
the openfate.ai reading of the golden chart (丙辰 丁酉 戊寅 甲寅) in tests.
"""
from __future__ import annotations

from .wuxing import (BRANCHES, CHONG_MAP, EARTH, FIRE, HAI_MAP, HE_MAP, METAL,
                     SANHE, STEMS, STEM_ELEMENT, WATER, WOOD)

POS = ("year", "month", "day", "hour")

# ---- star tables ------------------------------------------------------------
TIANYI = {"甲": "丑未", "戊": "丑未", "庚": "丑未", "乙": "子申", "己": "子申",
          "丙": "亥酉", "丁": "亥酉", "壬": "卯巳", "癸": "卯巳", "辛": "午寅"}
TAIJI = {"甲": "子午", "乙": "子午", "丙": "卯酉", "丁": "卯酉",
         "戊": "辰戌丑未", "己": "辰戌丑未", "庚": "寅亥", "辛": "寅亥",
         "壬": "巳申", "癸": "巳申"}
WENCHANG = {"甲": "巳", "乙": "午", "丙": "申", "戊": "申", "丁": "酉",
            "己": "酉", "庚": "亥", "辛": "子", "壬": "寅", "癸": "卯"}
XUETANG = {WOOD: "亥", FIRE: "寅", EARTH: "寅", METAL: "巳", WATER: "申"}  # 長生學堂, 土寄火
_TRINE = {b: grp for grp, _ in SANHE for b in grp}
TRINE_STARS = {  # branch-trine → {star: target branch}
    ("申", "子", "辰"): {"桃花": "酉", "驛馬": "寅", "華蓋": "辰", "將星": "子", "劫煞": "巳"},
    ("寅", "午", "戌"): {"桃花": "卯", "驛馬": "申", "華蓋": "戌", "將星": "午", "劫煞": "亥"},
    ("巳", "酉", "丑"): {"桃花": "午", "驛馬": "亥", "華蓋": "丑", "將星": "酉", "劫煞": "寅"},
    ("亥", "卯", "未"): {"桃花": "子", "驛馬": "巳", "華蓋": "未", "將星": "卯", "劫煞": "申"},
}
YANGREN = {"甲": "卯", "丙": "午", "戊": "午", "庚": "酉", "壬": "子"}
LUSHEN = {"甲": "寅", "乙": "卯", "丙": "巳", "戊": "巳", "丁": "午", "己": "午",
          "庚": "申", "辛": "酉", "壬": "亥", "癸": "子"}
TIANDE = {"寅": "丁", "卯": "申", "辰": "壬", "巳": "辛", "午": "亥", "未": "甲",
          "申": "癸", "酉": "寅", "戌": "丙", "亥": "乙", "子": "巳", "丑": "庚"}
YUEDE = {"寅": "丙", "午": "丙", "戌": "丙", "申": "壬", "子": "壬", "辰": "壬",
         "亥": "甲", "卯": "甲", "未": "甲", "巳": "庚", "酉": "庚", "丑": "庚"}

# 納音 (60-cycle sound elements), in cycle order — one name per stem-branch pair
_NAYIN = ["海中金", "爐中火", "大林木", "路旁土", "劍鋒金",
          "山頭火", "澗下水", "城頭土", "白蠟金", "楊柳木",
          "泉中水", "屋上土", "霹靂火", "松柏木", "長流水",
          "沙中金", "山下火", "平地木", "壁上土", "金箔金",
          "覆燈火", "天河水", "大驛土", "釵釧金", "桑柘木",
          "大溪水", "沙中土", "天上火", "石榴木", "大海水"]


def nayin(gz) -> str:
    idx = (6 * STEMS.index(gz.stem) - 5 * BRANCHES.index(gz.branch)) % 60
    return _NAYIN[idx // 2]


# 十二長生 growth stages: Day-Master stem vs a branch
_STAGES = ["長生", "沐浴", "冠帶", "臨官", "帝旺", "衰",
           "病", "死", "墓", "絕", "胎", "養"]
_CS_START = {"甲": ("亥", 1), "乙": ("午", -1), "丙": ("寅", 1), "戊": ("寅", 1),
             "丁": ("酉", -1), "己": ("酉", -1), "庚": ("巳", 1), "辛": ("子", -1),
             "壬": ("申", 1), "癸": ("卯", -1)}


def growth_stage(day_stem: str, branch: str) -> str:
    start, step = _CS_START[day_stem]
    off = (BRANCHES.index(branch) - BRANCHES.index(start)) * step % 12
    return _STAGES[off]


def pillar_extras(chart) -> dict:
    """納音 + growth stage for each pillar (openfate-mcp output parity)."""
    return {pos: {"nayin": nayin(chart.pillars[pos]),
                  "stage": growth_stage(chart.day_master, chart.pillars[pos].branch)}
            for pos in POS}


# plain-English gloss for each of the ten gods (shown inside the distribution)
TEN_GOD_MEANING = {
    "比肩": "peers & self-reliance — siblings, equals, standing your ground",
    "劫財": "rivals & boldness — shared resources, competition, risk appetite",
    "食神": "gentle output — enjoyment, nurture, easy creativity",
    "傷官": "sharp output — brilliance, critique, rebellion against rules",
    "偏財": "windfall wealth — opportunity, generosity, business flair",
    "正財": "steady wealth — salary, prudence, savings (spouse star in a man's chart)",
    "七殺": "raw pressure — ambition, decisiveness, discipline imposed from outside",
    "正官": "proper authority — rules, status, responsibility (spouse star in a woman's chart)",
    "偏印": "unconventional learning — intuition, niche skills, solitary study",
    "正印": "nurturing support — study, protection, elders, credentials",
}

MEANING = {
    "天乙貴人": "Nobleman — helpful people appear at critical moments",
    "太極貴人": "Tai Ji noble — affinity for philosophy, metaphysics, deep research",
    "文昌貴人": "Scholar star — study, writing, examinations",
    "學堂": "Study Hall — natural learner, academic aptitude",
    "桃花": "Peach Blossom — charm, attraction, social magnetism",
    "驛馬": "Travel Horse — movement, relocation, overseas links",
    "華蓋": "Canopy — solitary depth, spirituality, arts; thrives on niche study",
    "空亡": "Void — the tagged pillar's matters feel intangible until triggered",
    "羊刃": "Yang Blade — drive and decisiveness; watch impulsiveness",
    "天德貴人": "Heavenly Virtue — protective benevolence, eases crises",
    "月德貴人": "Monthly Virtue — quiet protection and goodwill",
    "將星": "General Star — leadership, command presence",
    "劫煞": "Robbery Sha — guard resources, avoid overexposure to risk",
    "祿神": "Salary star — innate earning capacity; steady income where it sits",
}


ANIMALS = {"子": "鼠", "丑": "牛", "寅": "虎", "卯": "兔", "辰": "龍", "巳": "蛇",
           "午": "馬", "未": "羊", "申": "猴", "酉": "雞", "戌": "狗", "亥": "豬"}
_LIFE_STAR = {1: ("一白", "水"), 2: ("二黑", "土"), 3: ("三碧", "木"),
              4: ("四綠", "木"), 5: ("五黃", "土"), 6: ("六白", "金"),
              7: ("七赤", "金"), 8: ("八白", "土"), 9: ("九紫", "火")}
_WUHU_DUN = {"甲": "丙", "己": "丙", "乙": "戊", "庚": "戊", "丙": "庚",
             "辛": "庚", "丁": "壬", "壬": "壬", "戊": "甲", "癸": "甲"}


def life_palaces(chart) -> dict:
    """命宮 Life Palace, 胎元 Conception Palace, 年命星 Life Star, 生肖.

    命宮: month and hour branches both counted from 寅=1; sum<14 → 14−sum,
    else 26−sum, counted on from 寅; stem by 五虎遁 from the year stem.
    胎元: month stem +1, month branch +3. 命星: 紫白 digit-root rule
    (male 11−root, female root+4). Validated against the Joey Yap Destiny
    chart for the 1976 戊寅 day master (命宮 甲午, 胎元 戊子, 命星 六白)."""
    def from_yin(b):
        return (BRANCHES.index(b) - 2) % 12 + 1
    s = from_yin(chart.pillars["month"].branch) + from_yin(chart.pillars["hour"].branch)
    idx = (14 - s) if s < 14 else (26 - s)
    mg_branch = BRANCHES[(2 + idx - 1) % 12]
    yin_stem = _WUHU_DUN[chart.pillars["year"].stem]
    mg_stem = STEMS[(STEMS.index(yin_stem) + idx - 1) % 10]
    ms, mb = chart.pillars["month"].stem, chart.pillars["month"].branch
    tai_yuan = (STEMS[(STEMS.index(ms) + 1) % 10]
                + BRANCHES[(BRANCHES.index(mb) + 3) % 12])
    root = 1 + (chart.lichun_year - 1) % 9
    n = 1 + ((11 - root) - 1) % 9 if chart.sex == "M" else 1 + (root + 4 - 1) % 9
    zh, el = _LIFE_STAR[n]
    return {"ming_gong": mg_stem + mg_branch, "tai_yuan": tai_yuan,
            "life_star": n, "life_star_zh": zh, "life_star_element": el,
            "animal": ANIMALS[chart.pillars["year"].branch],
            "source_ref": "命宮/胎元 (淵海子平 palace formulas) · 年命星 紫白 "
                          "digit-root rule — validated vs Joey Yap Destiny 2026 chart"}


def _void_branches(day_gz) -> str:
    """空亡 of the day pillar's 旬: the two branches its decade never reaches."""
    i, j = STEMS.index(day_gz.stem), BRANCHES.index(day_gz.branch)
    return BRANCHES[(j - i + 10) % 12] + BRANCHES[(j - i + 11) % 12]


def shensha(chart) -> list[dict]:
    """All symbolic stars found in the chart, with the pillar(s) carrying them."""
    p = chart.pillars
    stems = {pos: p[pos].stem for pos in POS}
    branches = {pos: p[pos].branch for pos in POS}
    found: dict[str, set] = {}

    def hit(star: str, pos: str):
        found.setdefault(star, set()).add(pos)

    # stem-keyed nobles: checked from BOTH day stem and year stem (classical)
    for base in (stems["day"], stems["year"]):
        for star, table in (("天乙貴人", TIANYI), ("太極貴人", TAIJI)):
            for pos, b in branches.items():
                if b in table.get(base, ""):
                    hit(star, pos)
        wc = WENCHANG.get(base)
        for pos, b in branches.items():
            if b == wc:
                hit("文昌貴人", pos)
    # 學堂 by Day-Master element
    xt = XUETANG[STEM_ELEMENT[stems["day"]]]
    for pos, b in branches.items():
        if b == xt:
            hit("學堂", pos)
    # trine-derived stars from year AND day branch groups
    for base_pos in ("year", "day"):
        grp = next(g for g in TRINE_STARS if branches[base_pos] in g)
        for star, target in TRINE_STARS[grp].items():
            for pos, b in branches.items():
                if b == target:
                    hit(star, pos)
    # 羊刃 and 祿神 from day stem
    yr = YANGREN.get(stems["day"])
    lu = LUSHEN[stems["day"]]
    for pos, b in branches.items():
        if b == yr:
            hit("羊刃", pos)
        if b == lu:
            hit("祿神", pos)
    # 天德/月德 from month branch → a stem OR branch anywhere in the chart
    for star, table in (("天德貴人", TIANDE), ("月德貴人", YUEDE)):
        target = table[branches["month"]]
        for pos in POS:
            if stems[pos] == target or branches[pos] == target:
                hit(star, pos)
    # 空亡 from the day pillar's 旬
    void = _void_branches(p["day"])
    for pos in ("year", "month", "hour"):
        if branches[pos] in void:
            hit("空亡", pos)

    return [{"star": s, "pillars": sorted(ps, key=POS.index), "meaning": MEANING[s],
             "source_ref": "神煞 classical tables"}
            for s, ps in sorted(found.items(), key=lambda kv: POS.index(sorted(kv[1], key=POS.index)[0]))]


# 刑 punishment pairs (openfate-mcp parity): 寅巳申 / 丑戌未 trios, 子卯, self-刑
_XING_PAIRS = {frozenset(p) for p in
               [("寅", "巳"), ("巳", "申"), ("寅", "申"),
                ("丑", "戌"), ("戌", "未"), ("丑", "未"), ("子", "卯")]}
_SELF_XING = set("辰午酉亥")


def natal_interactions(chart) -> list[dict]:
    """六合/六沖/六害/三合(半合)/刑 among the chart's own four branches."""
    b = {pos: chart.pillars[pos].branch for pos in POS}
    out = []
    # full trines first
    full = []
    for grp, el in SANHE:
        hits = [pos for pos in POS if b[pos] in grp]
        if len({b[pos] for pos in hits}) == 3:
            out.append({"kind": "三合", "pair": "".join(grp), "pillars": hits,
                        "note": f"full trine → {el}"})
            full.append(set(grp))
    for i, p1 in enumerate(POS):
        for p2 in POS[i + 1:]:
            x, y = b[p1], b[p2]
            if x == y:
                if x in _SELF_XING:
                    out.append({"kind": "自刑", "pair": x + y, "pillars": [p1, p2],
                                "note": "self-punishment — internal friction"})
                continue
            if frozenset((x, y)) in _XING_PAIRS:
                out.append({"kind": "刑", "pair": x + y, "pillars": [p1, p2],
                            "note": "punishment — hidden entanglement/stress"})
            if HE_MAP.get(x) == y:
                out.append({"kind": "六合", "pair": x + y, "pillars": [p1, p2],
                            "note": "binding & attraction"})
            elif CHONG_MAP.get(x) == y:
                out.append({"kind": "六沖", "pair": x + y, "pillars": [p1, p2],
                            "note": "clash — instability between these pillars"})
            elif HAI_MAP.get(x) == y:
                out.append({"kind": "六害", "pair": x + y, "pillars": [p1, p2],
                            "note": "harm — quiet friction"})
            elif _TRINE.get(x) == _TRINE.get(y) and _TRINE.get(x) is not None \
                    and not any({x, y} <= f for f in full):
                out.append({"kind": "半合", "pair": x + y, "pillars": [p1, p2],
                            "note": "half trine — latent alliance"})
    return out


def ten_god_distribution(chart) -> dict[str, float]:
    """Weighted ten-god counts: visible stems 1.0, hidden main 1.0, minors 1/3."""
    w: dict[str, float] = {}
    for pos in ("year", "month", "hour"):
        g = chart.ten_gods[pos]
        w[g] = w.get(g, 0) + 1.0
    for pos in POS:
        for k, (_, g) in enumerate(chart.hidden_gods[pos]):
            w[g] = w.get(g, 0) + (1.0 if k == 0 else 1 / 3)
    return w


def ten_god_pct(chart) -> dict[str, float]:
    w = ten_god_distribution(chart)
    total = sum(w.values()) or 1
    return {g: round(100 * v / total, 1)
            for g, v in sorted(w.items(), key=lambda kv: -kv[1])}
