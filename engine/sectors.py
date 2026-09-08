"""Floorplan → palace sector assignment (eng review 2A).

Two methods behind one interface:
  pie  — 米字 8×45° slices radiating from the enclosed-area centroid (primary)
  grid — 九宮 3×3 over the enclosed-area bounding box (toggle)
Rooms whose palace differs between methods are flagged. The house centroid
excludes PES / A-C ledge (they are simply not in rooms.json).

Screen geometry: image y grows downward. `image_up_bearing` is the compass
bearing (0=N, clockwise) that the TOP of the image points to.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from .wuxing import DIR_TO_PALACE, PALACES


def _centroid(poly: list[list[float]]) -> tuple[float, float]:
    xs, ys = zip(*poly)
    return sum(xs) / len(xs), sum(ys) / len(ys)


def house_centroid(rooms: list[dict]) -> tuple[float, float]:
    """Area-weighted centroid of all room rectangles (enclosed area only)."""
    tot_a = tot_x = tot_y = 0.0
    for r in rooms:
        xs, ys = zip(*r["poly"])
        a = (max(xs) - min(xs)) * (max(ys) - min(ys))
        cx, cy = _centroid(r["poly"])
        tot_a += a
        tot_x += cx * a
        tot_y += cy * a
    return tot_x / tot_a, tot_y / tot_a


def bearing_of_point(cx: float, cy: float, x: float, y: float,
                     image_up_bearing: float) -> float:
    """Compass bearing of (x,y) as seen from (cx,cy)."""
    screen_angle = math.degrees(math.atan2(x - cx, cy - y))  # 0 = screen-up, cw
    return (image_up_bearing + screen_angle) % 360


DIR_OF_BEARING = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def _dir_of(bearing: float) -> str:
    return DIR_OF_BEARING[int(((bearing + 22.5) % 360) // 45)]


def assign_pie(rooms: list[dict], image_up_bearing: float) -> dict[str, str]:
    cx, cy = house_centroid(rooms)
    xs = [x for r in rooms for x, _ in r["poly"]]
    ys = [y for r in rooms for _, y in r["poly"]]
    center_zone = 0.08 * math.hypot(max(xs) - min(xs), max(ys) - min(ys))
    out = {}
    for r in rooms:
        rx, ry = _centroid(r["poly"])
        if math.hypot(rx - cx, ry - cy) < center_zone:   # sits on the centre → 中宮
            out[r["id"]] = "中"
        else:
            out[r["id"]] = DIR_TO_PALACE[_dir_of(bearing_of_point(cx, cy, rx, ry, image_up_bearing))]
    return out


def assign_grid(rooms: list[dict], image_up_bearing: float) -> dict[str, str]:
    """九宮 3×3 over the enclosed bounding box, cells mapped by their bearing
    from the box centre so any image orientation works."""
    xs = [x for r in rooms for x, _ in r["poly"]]
    ys = [y for r in rooms for _, y in r["poly"]]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    out = {}
    for r in rooms:
        rx, ry = _centroid(r["poly"])
        col = min(2, max(0, int((rx - x0) / ((x1 - x0) / 3))))
        row = min(2, max(0, int((ry - y0) / ((y1 - y0) / 3))))
        if col == 1 and row == 1:
            out[r["id"]] = "中"
        else:
            cell_x, cell_y = x0 + (col + 0.5) * (x1 - x0) / 3, y0 + (row + 0.5) * (y1 - y0) / 3
            out[r["id"]] = DIR_TO_PALACE[_dir_of(bearing_of_point(cx, cy, cell_x, cell_y, image_up_bearing))]
    return out


def load_rooms(path: str | Path) -> dict:
    cfg = json.loads(Path(path).read_text("utf8"))
    up = cfg["image_up_bearing"]
    pie = assign_pie(cfg["rooms"], up)
    grid = assign_grid(cfg["rooms"], up)
    for r in cfg["rooms"]:
        r["palace_pie"] = pie[r["id"]]
        r["palace_grid"] = grid[r["id"]]
        r["method_disagrees"] = pie[r["id"]] != grid[r["id"]]
        r["direction_pie"] = "C" if pie[r["id"]] == "中" else PALACES[pie[r["id"]]]["dir"]
    cfg["centroid"] = house_centroid(cfg["rooms"])
    return cfg


def feature_analysis(cfg: dict, sitting_palace: str) -> list[dict]:
    """八宅 door & stove rules from marked feature points.

    House 宅卦 = the sitting trigram; door wants an auspicious house star,
    the stove classically PRESSES (sits on) an inauspicious one (壓凶)."""
    from .bazhai import STAR_SCORE, youxing_stars
    feats = cfg.get("features") or {}
    if not feats:
        return []
    yx = youxing_stars(sitting_palace)
    cx, cy = house_centroid(cfg["rooms"])
    upb = cfg["image_up_bearing"]
    out = []
    for name, (x, y) in feats.items():
        d = _dir_of(bearing_of_point(cx, cy, x, y, upb))
        pal = DIR_TO_PALACE[d]
        star = yx[pal]
        lucky = STAR_SCORE[star] > 0
        if name == "main_door":
            verdict = "good" if lucky else "caution"
            expl = (f"main door in {d} ({pal}宮) — house star {star}: "
                    + ("the mouth of 氣 opens into a supportive sector"
                       if lucky else
                       "an inauspicious sector for the entrance — keep it bright, "
                       "tidy and well-lit to mitigate"))
        elif name == "stove":
            verdict = "good" if not lucky else "caution"
            expl = (f"stove sits in {d} ({pal}宮) — house star {star}: "
                    + ("classical ideal — the stove PRESSES an unlucky sector (壓凶)"
                       if not lucky else
                       "the stove burns a lucky sector — classically wasteful; if "
                       "ever remodelling, prefer an unlucky sector for it"))
        else:
            verdict, expl = "info", f"{name} in {d} ({pal}宮), house star {star}"
        out.append({"feature": name, "dir": d, "palace": pal, "star": star,
                    "verdict": verdict, "explanation": expl,
                    "source_ref": f"八宅宅卦 — {sitting_palace}宅 遊年"})
    return out
