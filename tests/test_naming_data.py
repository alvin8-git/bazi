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
    # contested radicals (玉/王, 貝, 心) must NOT be auto-assigned — curated only
    assert data["琪"]["el"] is None and data["财"]["el"] is None
