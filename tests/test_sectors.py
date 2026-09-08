"""Sector-assignment geometry: pie vs grid, orientation handling."""
from pathlib import Path

from engine.sectors import assign_grid, assign_pie, bearing_of_point, load_rooms

ROOT = Path(__file__).resolve().parent.parent

SQUARE = [  # simple 3x3 house, up = North
    {"id": "nw", "poly": [[0, 0], [10, 0], [10, 10], [0, 10]]},
    {"id": "n",  "poly": [[10, 0], [20, 0], [20, 10], [10, 10]]},
    {"id": "ne", "poly": [[20, 0], [30, 0], [30, 10], [20, 10]]},
    {"id": "w",  "poly": [[0, 10], [10, 10], [10, 20], [0, 20]]},
    {"id": "c",  "poly": [[10, 10], [20, 10], [20, 20], [10, 20]]},
    {"id": "e",  "poly": [[20, 10], [30, 10], [30, 20], [20, 20]]},
    {"id": "sw", "poly": [[0, 20], [10, 20], [10, 30], [0, 30]]},
    {"id": "s",  "poly": [[10, 20], [20, 20], [20, 30], [10, 30]]},
    {"id": "se", "poly": [[20, 20], [30, 20], [30, 30], [20, 30]]},
]
EXPECT_N_UP = {"nw": "乾", "n": "坎", "ne": "艮", "w": "兌", "c": "中",
               "e": "震", "sw": "坤", "s": "離", "se": "巽"}


def test_square_house_north_up_both_methods():
    assert assign_pie(SQUARE, 0) == EXPECT_N_UP
    assert assign_grid(SQUARE, 0) == EXPECT_N_UP


def test_rotated_image():
    # image top faces East (90°): screen-up room "n" is now in the East palace
    pie = assign_pie(SQUARE, 90)
    assert pie["n"] == "震" and pie["s"] == "兌" and pie["e"] == "離"


def test_bearing_math():
    assert bearing_of_point(0, 0, 0, -10, 0) == 0.0        # straight up, up=N → N
    assert bearing_of_point(0, 0, 10, 0, 0) == 90.0        # right → E
    assert bearing_of_point(0, 0, 10, 0, 315) % 360 == 45.0  # right, up=NW → NE


def test_real_rooms_load():
    cfg = load_rooms(ROOT / "data/rooms.json")
    ids = {r["id"] for r in cfg["rooms"]}
    assert {"master", "br2", "br3", "br4"} <= ids
    for r in cfg["rooms"]:
        assert r["palace_pie"] and r["palace_grid"]
    # with up=NW(315°): master (bottom-right of image) sits toward E/SE of centre
    master = next(r for r in cfg["rooms"] if r["id"] == "master")
    assert master["palace_pie"] in ("震", "巽", "離")
    sleeping = [r for r in cfg["rooms"] if r["sleeping"]]
    assert sum(r["capacity"] for r in sleeping) >= 5   # family fits (outside voice #3)
