"""Naming dataset goldens — 姓名学 strokes derived from Unihan, validated
against published 百家姓/given-name stroke tables (dataset spike, design doc
step 0). Regenerate the dataset with scripts/naming_spike.py."""
import json
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parent.parent / "data/naming/chardata.json"

SURNAME_GOLDEN = {
    "王": 4, "李": 7, "林": 8, "陳": 16, "張": 11, "黃": 12, "吳": 7,
    "劉": 15, "楊": 13, "周": 8, "徐": 10, "孫": 10, "馬": 10, "朱": 6,
    "何": 7, "高": 10, "許": 11, "郭": 15, "馮": 12, "曾": 12, "鄭": 19,
    "趙": 14, "潘": 16, "蔡": 17, "彭": 12, "袁": 10, "羅": 20, "韓": 17,
}
GIVEN_GOLDEN = {"海": 11, "明": 8, "华": 14, "伟": 11, "婷": 12, "俊": 9,
                "国": 11, "德": 15, "琳": 13, "淑": 12, "芳": 10, "英": 11,
                "沐": 8, "浩": 11}
ELEMENT_GOLDEN = {"海": "水", "林": "木", "铭": "金", "晖": "火", "峰": "土",
                  "芳": "木", "沐": "水", "城": "土", "秀": "木", "雪": "水"}


@pytest.fixture(scope="module")
def data():
    if not DATA.exists():
        pytest.skip("naming dataset not built — run scripts/naming_spike.py")
    return json.loads(DATA.read_text("utf8"))


def test_surname_strokes(data):
    for ch, want in SURNAME_GOLDEN.items():
        assert data[ch]["ks"] == want, f"{ch}: {data[ch]['ks']} != {want}"


def test_given_name_strokes(data):
    for ch, want in GIVEN_GOLDEN.items():
        assert data[ch]["ks"] == want, f"{ch}: {data[ch]['ks']} != {want}"


def test_radical_elements(data):
    for ch, want in ELEMENT_GOLDEN.items():
        assert data[ch]["el"] == want, f"{ch}: {data[ch]['el']} != {want}"
        assert data[ch]["el_src"]          # every element cites its rule


def test_dataset_shape(data):
    assert len(data) > 15000
    for ch in ("伟", "陳", "海"):
        e = data[ch]
        assert set(e) >= {"ks", "ms", "rad", "trad", "py", "el", "el_src"}
    # contested radicals (玉/王, 貝, 心) must NOT be auto-assigned by rules —
    # chars outside the curated layer stay None until reviewed
    assert data["悦"]["el"] is None and data["贺"]["el"] is None


def test_curated_layer(data):
    for ch, want in {"伟": "土", "文": "水", "俊": "火", "睿": "金",
                     "琳": "木", "财": "金", "德": "火", "安": "土"}.items():
        assert data[ch]["el"] == want, f"{ch}: {data[ch]['el']} != {want}"
        assert data[ch]["el_src"].startswith("curated:")
    # dictionary-disputed chars carry the contested flag for human sign-off
    for ch in ("玉", "心", "杰", "龙"):
        assert data[ch].get("el_contested") is True


# ---- traditional forms and 康熙 strokes (2026-10-04 fix) --------------------
# Unihan lists the character itself first when it also exists as a traditional
# character; the builder used to take that and count the SIMPLIFIED strokes.
TRAD_FIXED = {"优": ("優", 17), "宝": ("寶", 20), "乐": ("樂", 15), "涛": ("濤", 18),
              "凤": ("鳳", 14), "体": ("體", 23), "万": ("萬", 15), "丰": ("豐", 18),
              "岁": ("歲", 13), "画": ("畫", 12), "云": ("雲", 12), "历": ("歷", 16)}
TRAD_STABLE = {"国": ("國", 11), "华": ("華", 14), "东": ("東", 8), "龙": ("龍", 16),
               "伟": ("偉", 11), "杰": ("傑", 12), "泽": ("澤", 17), "轩": ("軒", 10),
               "婷": ("婷", 12), "禄": ("祿", 13)}
KEPT_SELF = {"志": 7, "松": 8, "冬": 5, "秋": 9, "才": 3}      # traditional in their own right


def test_traditional_forms_and_kangxi_strokes(data):
    for ch, (trad, ks) in {**TRAD_FIXED, **TRAD_STABLE}.items():
        assert (data[ch]["trad"], data[ch]["ks"]) == (trad, ks), f"{ch}: {data[ch]['trad']} {data[ch]['ks']}"
    for ch, ks in KEPT_SELF.items():
        assert data[ch]["trad"] == ch and data[ch]["ks"] == ks, ch
        assert len(data[ch]["trad_alts"]) >= 2                     # the other form stays switchable


def test_pool_characters_use_a_listed_traditional_form(data):
    from engine.naming import POOL
    for ch in dict.fromkeys(POOL):
        e = data[ch]
        alts = e.get("trad_alts")
        if alts:
            assert e["trad"] in alts and alts[e["trad"]] == e["ks"], ch


def test_common_level_one_list(data):
    l1 = (DATA.parent / "common_l1.txt").read_text("utf8").splitlines()
    assert l1[0].startswith("#") and len(l1[1]) == 3500 and len(set(l1[1])) == 3500
    assert sum(1 for v in data.values() if v.get("common")) == 3500
    assert data["明"]["common"] and not data["婷"].get("common")      # 婷 is level 2
    assert data["明"]["lvl"] == 1 and data["婷"]["lvl"] == 2 and "lvl" not in data["龘"]
    assert 2900 <= sum(1 for v in data.values() if v.get("lvl") == 2) <= 3000   # a few level-2 chars sit outside the URO block


def test_trad_overrides_are_valid_forms(data):
    ov = json.loads((DATA.parent / "trad_overrides.json").read_text("utf8"))
    for ch, ent in ov.items():
        if ch.startswith("_"):
            continue
        assert data[ch]["trad"] == ent["default"], ch
        for form in [ent["default"], *ent.get("alts", [])]:
            assert form in data[ch]["trad_alts"], f"{ch}: {form}"


def test_char_info_selects_a_traditional_form():
    from engine.naming import char_info
    assert char_info("云")["ks"] == 12 and char_info("云", "云")["ks"] == 4
    assert char_info("历", "曆")["trad"] == "曆"
    with pytest.raises(ValueError):
        char_info("云", "雨")
