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


# Outdoor areas never move the 太極點: the centre belongs to the enclosed dwelling.
# They still receive a palace reading from that centre (a balcony opens onto a palace).
OUTDOOR_TYPES = ("Balcony", "Patio", "Planter", "Ledge", "阳台", "露台", "花槽")


def is_outdoor(room: dict) -> bool:
    if room.get("outdoor") is True:
        return True
    rt = room.get("rtype") or room.get("type") or ""
    return any(rt.startswith(t) or t in rt for t in OUTDOOR_TYPES)


def enclosed_rooms(rooms: list[dict], include_outdoor: bool = False) -> list[dict]:
    base = [r for r in rooms if include_outdoor or not is_outdoor(r)]
    return base or list(rooms)


def _pie_geometry(rooms: list[dict], include_outdoor: bool):
    base = enclosed_rooms(rooms, include_outdoor)
    cx, cy = house_centroid(base)
    xs = [x for r in base for x, _ in r["poly"]]
    ys = [y for r in base for _, y in r["poly"]]
    return cx, cy, 0.08 * math.hypot(max(xs) - min(xs), max(ys) - min(ys))


def assign_pie(rooms: list[dict], image_up_bearing: float,
               include_outdoor: bool = False) -> dict[str, str]:
    cx, cy, center_zone = _pie_geometry(rooms, include_outdoor)
    out = {}
    for r in rooms:
        rx, ry = _centroid(r["poly"])
        if math.hypot(rx - cx, ry - cy) < center_zone:   # sits on the centre → 中宮
            out[r["id"]] = "中"
        else:
            out[r["id"]] = DIR_TO_PALACE[_dir_of(bearing_of_point(cx, cy, rx, ry, image_up_bearing))]
    return out


def room_bearings(rooms: list[dict], image_up_bearing: float,
                  include_outdoor: bool = False) -> dict[str, dict]:
    """Per room: bearing from the centre, margin to the nearest palace line, centre flag."""
    cx, cy, center_zone = _pie_geometry(rooms, include_outdoor)
    out = {}
    for r in rooms:
        rx, ry = _centroid(r["poly"])
        b = bearing_of_point(cx, cy, rx, ry, image_up_bearing)
        m = (b - 22.5) % 45
        margin = min(m, 45 - m)
        line = (b - m + 45) % 360 if m > 22.5 else (b - m) % 360   # nearest 22.5+45k
        out[r["id"]] = {"bearing": round(b, 1), "margin": round(margin, 1),
                        "centre": math.hypot(rx - cx, ry - cy) < center_zone,
                        "line": line,
                        "between": [DIR_TO_PALACE[_dir_of(line - 1)], DIR_TO_PALACE[_dir_of(line + 1)]]}
    return out


BOUNDARY_DEG = 3.0


def trace_checks(rooms: list[dict], image_up_bearing: float,
                 include_outdoor: bool = False) -> list[dict]:
    """Warnings about the trace itself (not the house): {code, zh, text, rooms}."""
    lab = lambda r: r.get("label") or r["id"]
    pie = assign_pie(rooms, image_up_bearing, include_outdoor)
    rb = room_bearings(rooms, image_up_bearing, include_outdoor)
    outdoor = [r for r in rooms if is_outdoor(r)]
    enclosed = [r for r in rooms if not is_outdoor(r)]
    out = []
    centre_beds = [lab(r) for r in rooms if r.get("sleeping") and pie[r["id"]] == "中"]
    if centre_beds:
        out.append({"code": "centre-bedroom", "zh": "卧室落中宫", "severity": "warn",
                    "text": "a bedroom sits on the centre and gets no palace star — the centre has "
                            "drifted (balconies traced as rooms, or enclosed areas missing); fix the "
                            "trace before reading its score", "rooms": centre_beds})
    near = [(lab(r), rb[r["id"]]) for r in rooms if not rb[r["id"]]["centre"]
            and rb[r["id"]]["margin"] <= BOUNDARY_DEG and not is_outdoor(r)]
    if near:
        out.append({"code": "boundary", "zh": "贴近宫界", "severity": "warn",
                    "text": "; ".join(f"{n} is {v['margin']}° from the {v['between'][0]}/{v['between'][1]} line"
                                      for n, v in near) + " — a small change in the trace flips its "
                            "palace; trace every enclosed area and check the box on the plan",
                    "rooms": [n for n, _ in near]})
    if outdoor and not include_outdoor:
        out.append({"code": "outdoor-excluded", "zh": "户外已排除", "severity": "info",
                    "text": f"{len(outdoor)} outdoor area(s) left out of the centre — each still "
                            "gets its own palace reading", "rooms": [lab(r) for r in outdoor]})
    if outdoor and include_outdoor:
        out.append({"code": "outdoor-included", "zh": "户外计入", "severity": "warn",
                    "text": "balconies are counting toward the centre — this is not the usual "
                            "doctrine; the 太極點 belongs to the enclosed home",
                    "rooms": [lab(r) for r in outdoor]})
    if len(enclosed) < 6:
        out.append({"code": "few-rooms", "zh": "描图不全", "severity": "info",
                    "text": "corridors, lobby, wardrobes and the yard move the centre — trace "
                            "every enclosed area, not only the rooms you care about", "rooms": []})
    return out


def assign_grid(rooms: list[dict], image_up_bearing: float,
                include_outdoor: bool = False) -> dict[str, str]:
    """九宮 3×3 over the enclosed bounding box, cells mapped by their bearing
    from the box centre so any image orientation works."""
    base = enclosed_rooms(rooms, include_outdoor)
    xs = [x for r in base for x, _ in r["poly"]]
    ys = [y for r in base for _, y in r["poly"]]
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
