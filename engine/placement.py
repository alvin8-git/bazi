"""P3: auto bed/desk placement + form-school door-doctrine audit.

Pure geometry over axis-aligned room rects. Every input comes from the traced
plan (rect, doors, windows, image_up_bearing) and the occupant's 八宅 stars —
nothing else. Doors/windows are fractions of a room edge so they are
resolution-independent: {edge: 0 top|1 right|2 bottom|3 left, offset: 0-1
along the edge (x→ or y↓), width: 0-1, hinge: "lo"|"hi"} and windows carry
`bay` instead of `hinge`.

Doctrine encoded: 門沖床 entry strip, door-swing clearance, 床在門後
(hinge-corner), headboard-under-window, commanding position, 門對門 pairs.
形勢為先: form flags outrank a marginally better star.
"""
from __future__ import annotations

from engine.bazhai import STAR_SCORE

PALACES = "坎艮震巽離坤兌乾"
DIRS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
_EDGE_TURN = [0.0, 90.0, 180.0, 270.0]     # outward normal vs image-up


def edge_bearing(edge: int, up_bearing: float) -> float:
    return (up_bearing + _EDGE_TURN[edge]) % 360


def bearing_palace(b: float) -> str:
    return PALACES[round(b / 45) % 8]


def _edge_len(rect, edge):
    x, y, w, h = rect
    return w if edge in (0, 2) else h


def _span(item, rect, edge):
    """(lo, hi) of a door/window along its edge, absolute units."""
    length = _edge_len(rect, edge)
    lo = item["offset"] * length
    return lo, lo + item["width"] * length


def _sub_intervals(length, spans, margin=0.0):
    """Free intervals of [0, length] after removing spans (± margin)."""
    free, pos = [], 0.0
    for lo, hi in sorted(spans):
        lo, hi = max(0.0, lo - margin), min(length, hi + margin)
        if lo > pos:
            free.append((pos, lo))
        pos = max(pos, hi)
    if pos < length:
        free.append((pos, length))
    return free


def _bed_rect(rect, edge, along_lo, bed_w, bed_len):
    """Bed rect with headboard centred on `edge` at along-interval start."""
    x, y, w, h = rect
    if edge == 0:
        return [x + along_lo, y, bed_w, bed_len]
    if edge == 2:
        return [x + along_lo, y + h - bed_len, bed_w, bed_len]
    if edge == 3:
        return [x, y + along_lo, bed_len, bed_w]
    return [x + w - bed_len, y + along_lo, bed_len, bed_w]


def _strip_rect(rect, edge, lo, hi):
    """Entry strip: the door span projected across the whole room."""
    x, y, w, h = rect
    if edge in (0, 2):
        return [x + lo, y, hi - lo, h]
    return [x, y + lo, w, hi - lo]


def _overlap(a, b):
    ox = max(0.0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]))
    oy = max(0.0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
    return ox * oy


def propose_bed(rect, doors, windows, up_bearing, stars) -> list[dict]:
    """Ranked headboard candidates for one occupant in one room."""
    x, y, w, h = rect
    out = []
    for edge in range(4):
        wall_len = _edge_len(rect, edge)
        depth = _edge_len(rect, (edge + 1) % 4)
        bearing = edge_bearing(edge, up_bearing)
        palace = bearing_palace(bearing)
        star = stars.get(palace, "")
        base = STAR_SCORE.get(star, 0)
        bed_w = min(0.45 * wall_len, 0.6 * wall_len)
        bed_len = min(0.55 * depth, 0.7 * depth)
        wall_doors = [d for d in doors if d["edge"] == edge]
        spans = [_span(d, rect, edge) for d in wall_doors]
        # keep the swing arc clear: margin = the door's own width
        margin = max((hi - lo for lo, hi in spans), default=0.0)
        # prefer a window-free span for the headboard; fall back to door-only
        win_spans = [_span(wn, rect, edge) for wn in windows
                     if wn["edge"] == edge]
        free = [iv for iv in _sub_intervals(wall_len, spans + win_spans, margin)
                if iv[1] - iv[0] >= bed_w]
        head_on_glass = False
        if not free:
            head_on_glass = bool(win_spans)
            free = [iv for iv in _sub_intervals(wall_len, spans, margin)
                    if iv[1] - iv[0] >= bed_w]
        if not free:
            continue                        # headboard wall fully claimed by door
        # centre the bed in the largest free interval
        lo, hi = max(free, key=lambda iv: iv[1] - iv[0])
        along = lo + ((hi - lo) - bed_w) / 2
        bed = _bed_rect(rect, edge, along, bed_w, bed_len)
        flags, score = [], float(base)
        for d in doors:
            dlo, dhi = _span(d, rect, d["edge"])
            dw = dhi - dlo
            strip = _strip_rect(rect, d["edge"], dlo, dhi)
            ov = _overlap(strip, bed)
            # ignore sliver grazes: require ≥ 25% of the strip's width engaged
            depth_ = bed_len if d["edge"] in (edge, (edge + 2) % 4) else bed_w
            if ov >= 0.25 * dw * min(depth_, dw * 4):
                if d["edge"] == (edge + 2) % 4:
                    # head-on strip from the facing wall — the real 門沖床
                    pillow = _bed_rect(rect, edge, along, bed_w, bed_len / 3)
                    if _overlap(strip, pillow) >= 0.25 * dw * (bed_len / 3):
                        flags.append({"code": "menchong", "zh": "門沖床",
                                      "text": "the door's entry line runs onto "
                                      "the pillow", "remedy": "shift the bed out "
                                      "of the strip, or screen with a wardrobe/"
                                      "high shelf between door and bed"})
                        score -= 3
                    else:
                        flags.append({"code": "strip", "zh": "入門線",
                                      "text": "the entry line crosses the bed "
                                      "body", "remedy": "a foot bench or low "
                                      "cabinet at the foot settles it"})
                        score -= 1.5
                elif d["edge"] != edge:
                    # adjacent wall: the strip sweeps ALONG the bed's flank —
                    # the interceptor case, not 門沖床
                    flags.append({"code": "strip", "zh": "入門線",
                                  "text": "the entry line runs along the bed's "
                                  "flank", "remedy": "station a wardrobe, desk "
                                  "or high shelf between door and bed to "
                                  "intercept the strip"})
                    score -= 1
            if d["edge"] != edge:
                # 床在門後: hinge corner shared with the headboard wall and the
                # bed hugging that corner (sliver grazes ignored)
                dlen = dw
                hinge_at = dlo if d.get("hinge", "lo") == "lo" else dhi
                near_corner = hinge_at < dlen or hinge_at > _edge_len(rect, d["edge"]) - dlen
                if near_corner and _overlap(_strip_rect(rect, d["edge"],
                                            max(0, hinge_at - dlen),
                                            min(_edge_len(rect, d["edge"]),
                                                hinge_at + dlen)),
                                            bed) >= 0.2 * dlen * dlen:
                    flags.append({"code": "behind", "zh": "床在門後",
                                  "text": "the opened leaf stands beside the bed",
                                  "remedy": "soft-close hinge or doorstop plus a "
                                  "bedside table"})
                    score -= 0.5
        if any(d["edge"] == edge for d in doors):
            flags.append({"code": "door-wall", "zh": "門同牆",
                          "text": "door shares the headboard wall — no sightline "
                          "to who enters", "remedy": "bedside mirror is NOT the "
                          "fix in a bedroom; prefer another wall"})
            score -= 0.5
        else:
            score += 0.5                    # commanding: door in view
        for win in windows:
            if win["edge"] != edge:
                continue
            wlo, whi = _span(win, rect, edge)
            if wlo < along + bed_w and whi > along:
                # the pillow never goes on glass — a bay is for the bed's
                # FLANK (platform), not the head; both cost the same
                if win.get("bay"):
                    flags.append({"code": "bay-head", "zh": "頭靠飄窗",
                                  "text": "headboard on the bay window glass",
                                  "remedy": "use the bay for the bed's FLANK "
                                  "(platform + solid raised rail) and keep the "
                                  "pillow on a solid wall"})
                else:
                    flags.append({"code": "window-head", "zh": "床頭靠窗",
                                  "text": "headboard under a window — no solid "
                                  "backing", "remedy": "prefer a solid wall, or "
                                  "a tall solid headboard + heavy curtains"})
                score -= 2.5
        out.append({"edge": edge, "dir": DIRS[round(bearing / 45) % 8],
                    "palace": palace, "star": star, "score": round(score, 2),
                    "bed": [round(v, 1) for v in bed], "flags": flags})
    # solid backing breaks ties: a wall without glass behind the head wins
    out.sort(key=lambda c: (-c["score"],
                            any(f["code"] in ("bay-head", "window-head")
                                for f in c["flags"])))
    return out


def propose_desk(rect, doors, up_bearing, stars, good_stars) -> dict | None:
    """Best desk spot: face an auspicious direction, stay clear of door
    strips, keep the door out of the square-behind zone."""
    x, y, w, h = rect
    best = None
    for edge in range(4):                   # the wall the desk faces
        bearing = edge_bearing(edge, up_bearing)
        star = stars.get(bearing_palace(bearing), "")
        if star not in good_stars:
            continue
        score = STAR_SCORE.get(star, 0)
        back_edge = (edge + 2) % 4
        if any(d["edge"] == back_edge for d in doors):
            score -= 2                      # door square behind the chair
            note = ("door lies behind the chair — high-back chair, door closed "
                    "while studying")
        else:
            note = None
        cand = {"edge": edge, "dir": DIRS[round(bearing / 45) % 8],
                "star": star, "score": score, "note": note}
        if best is None or cand["score"] > best["score"]:
            best = cand
    return best


def door_pairs(rooms: list[dict], gap_limit: float) -> list[dict]:
    """門對門: doors of different rooms facing each other across ≤ gap_limit."""
    entries = []
    for r in rooms:
        rect = r["rect"]
        for d in r.get("doors", []):
            lo, hi = _span(d, rect, d["edge"])
            x, y, w, h = rect
            if d["edge"] in (0, 2):
                a0, a1 = x + lo, x + hi
                pos = y if d["edge"] == 0 else y + h
            else:
                a0, a1 = y + lo, y + hi
                pos = x if d["edge"] == 3 else x + w
            entries.append({"room": r["id"], "label": r.get("label", r["id"]),
                            "axis": "x" if d["edge"] in (0, 2) else "y",
                            "a0": a0, "a1": a1, "pos": pos,
                            "outward": -1 if d["edge"] in (0, 3) else 1})
    pairs = []
    for i, a in enumerate(entries):
        for b in entries[i + 1:]:
            if a["room"] == b["room"] or a["axis"] != b["axis"]:
                continue
            if a["outward"] == b["outward"]:
                continue                    # must face each other
            gap = abs(b["pos"] - a["pos"])
            facing = ((a["outward"] == 1) == (a["pos"] < b["pos"]))
            lat = min(a["a1"], b["a1"]) - max(a["a0"], b["a0"])
            width = min(a["a1"] - a["a0"], b["a1"] - b["a0"])
            if facing and gap <= gap_limit and lat >= 0.3 * width:
                pairs.append({"a": a["label"], "b": b["label"],
                              "zh": "門對門",
                              "remedy": "keep both doors closed as a standing "
                              "habit; a corridor light softens the line"})
    return pairs


# ---------------- P2 (design doc v2 C2, C4, C5, C6, C7, B8) ----------------
# Remedy order 避 → 擋 → 化: move first, block second, dissolve last.
REMEDY_ORDER = {
    "menchong": "避: shift the bed along the same wall out of the door line · 擋: if it "
                "cannot move, a headboard-height closed unit or screen between pillow and "
                "door · 化: door closed at night",
    "strip": "避: slide the bed clear of the entry strip · 擋: a wardrobe, desk or high "
             "shelf stationed between door and bed intercepts the strip · 化: door closed "
             "at night",
    "behind": "擋: soft-close hinge or doorstop, a bedside unit at headboard height on the "
              "pillow's door side · 化: door closed at night",
    "door-wall": "避: pillow at the far end of the wall from the door; a bedside mirror is "
                 "NOT the fix in a bedroom",
    "window-head": "避: head to a solid wall · 擋: if not possible, a tall solid headboard "
                   "with heavy curtains behind it",
    "bay-head": "避: use the bay for the bed's FLANK (platform with a raised solid rail) and "
                "keep the pillow on a solid wall",
}
FORM_FIRST = ("形先於理 — a live door line is removed before the compass direction is "
              "optimised; a flagged wall ranks below a cleaner one even when its star is "
              "marginally better")
DESK_SIDE_REMEDY = {
    "behind-left": "solid high-back chair, door closed while studying, no mirror to 'see the door'",
    "behind-right": "solid high-back chair, door closed while studying, no mirror to 'see the door'",
    "square-behind": "move the desk so the door sits to the side; if it cannot move, a "
                     "high-back chair and a screen or tall unit behind the chair",
    "side": "fine — the sitter sees the door without sitting in its line",
    "front": "fine — commanding view of the door; keep the chair out of the entry strip",
    "none": "no door marked — mark it in the trace to unlock the door-line audit",
}
SITE_CHECKS = [
    {"code": "beam", "zh": "橫樑壓頂", "text": "no structural beam or ceiling bulkhead over the "
     "pillow zone — one photograph of the ceiling above the intended head settles it; if one "
     "crosses, shift the pillow clear or box it with a false ceiling first", "doctrine": "形勢"},
    {"code": "head-storage", "zh": "床頭無物", "text": "nothing stored above or behind the sleeping "
     "head; the head-end panel stays a plain solid back", "doctrine": "形勢 [modern convention]"},
    {"code": "headboard-solid", "zh": "靠山", "text": "the headboard piece must be solid, full "
     "height and closed — a desk hutch is light, open and used, and is not a headboard",
     "doctrine": "形勢 (靠山)"},
    {"code": "mirror-glass", "zh": "鏡對床", "text": "no mirror facing the bed; no clear or mirror "
     "glass on a run beside a bed — reeded or frosted glass in timber frames only, upper "
     "section, solid below", "doctrine": "形勢 (鏡對床) [modern convention on glass]"},
]
OVERHEAD_SEAT = {"code": "overhead-seat", "zh": "座上壓頂", "text": "no wall cabinet or shelf "
                 "cantilevered over the seated head — the same form as a beam; a high-level run "
                 "stops before the desk", "remedy": "stop high-level joinery at the bookcase; "
                 "shelving stands behind the desk, not over the chair", "site_check": True,
                 "doctrine": "形勢 (橫樑壓頂 analogue)"}


def annotate_bed_flags(beds: list[dict]) -> list[dict]:
    """C2: replace each flag's remedy with the 避→擋→化 text, add doctrine, and put the
    形先於理 sentence on the top-ranked bed when any flag is present."""
    for i, b in enumerate(beds):
        for f in b.get("flags", []):
            f["remedy"] = REMEDY_ORDER.get(f["code"], f.get("remedy", ""))
            f["doctrine"] = "形勢 [modern convention]"
        if i == 0 and b.get("flags"):
            b["note"] = FORM_FIRST
    return beds


def desk_door_side(rect, desk_edge: int, doors: list[dict]) -> str:
    """C4: where the door sits relative to a chair facing `desk_edge`."""
    if not doors:
        return "none"
    x, y, w, h = rect
    depth = _edge_len(rect, (desk_edge + 1) % 4)
    worst = "side"
    rank = {"side": 0, "front": 1, "behind-left": 2, "behind-right": 2, "square-behind": 3}
    for d in doors:
        e = d["edge"]
        if e == desk_edge:
            side = "front"
        elif e == (desk_edge + 2) % 4:
            side = "square-behind"
        else:
            lo, hi = _span(d, rect, e)
            centre = (lo + hi) / 2            # along the adjacent wall, from its origin
            # distance of the door centre from the facing wall, along the room depth
            if desk_edge == 0:
                dist = centre                 # adjacent walls run top→bottom from the top
            elif desk_edge == 2:
                dist = depth - centre
            elif desk_edge == 3:
                dist = centre                 # adjacent walls run left→right from the left
            else:
                dist = depth - centre
            behind = dist > 0.5 * depth
            right = (e == (desk_edge + 1) % 4)
            side = ("behind-right" if right else "behind-left") if behind else "side"
        if rank[side] > rank[worst]:
            worst = side
    return worst


def desk_rect_for(rect, desk_edge: int, bed: list[float] | None, doors: list[dict],
                  depth_units: float, width_units: float) -> list[float]:
    """A desk block against `desk_edge`, placed in the largest free interval of that wall
    not taken by the bed footprint or a door swing."""
    x, y, w, h = rect
    wall = _edge_len(rect, desk_edge)
    spans = [_span(d, rect, desk_edge) for d in doors if d["edge"] == desk_edge]
    if bed:
        bx, by, bw, bh = bed
        if desk_edge in (0, 2):
            spans.append((bx - x, bx - x + bw))
        else:
            spans.append((by - y, by - y + bh))
    free = [iv for iv in _sub_intervals(wall, spans) if iv[1] - iv[0] >= width_units * 0.8]
    lo, hi = max(free, key=lambda iv: iv[1] - iv[0]) if free else (0.0, wall)
    along = lo + max(0.0, ((hi - lo) - width_units) / 2)
    return _bed_rect(rect, desk_edge, along, width_units, depth_units)


def _gap(a, b):
    dx = max(0.0, max(a[0], b[0]) - min(a[0] + a[2], b[0] + b[2]))
    dy = max(0.0, max(a[1], b[1]) - min(a[1] + a[3], b[1] + b[3]))
    return (dx * dx + dy * dy) ** 0.5


def clearance_warnings(bed: list[float], bed_edge: int, desk: list[float] | None,
                       m_per_unit: float, approx: bool = False) -> list[dict]:
    """C5: pillow end to desk edge under 600 mm; plus the overhead-at-seat site check."""
    out = []
    if desk is not None:
        bx, by, bw, bh = bed
        # pillow = the head third of the bed, at the headboard edge
        if bed_edge == 0:
            pillow = [bx, by, bw, bh / 3]
        elif bed_edge == 2:
            pillow = [bx, by + bh * 2 / 3, bw, bh / 3]
        elif bed_edge == 3:
            pillow = [bx, by, bw / 3, bh]
        else:
            pillow = [bx + bw * 2 / 3, by, bw / 3, bh]
        gap_m = _gap(pillow, desk) * m_per_unit
        if gap_m < 0.6:
            out.append({"code": "desk-near-pillow", "zh": "書桌近枕",
                        "text": f"desk edge about {gap_m:.1f} m from the pillow end"
                                + (" (approx. scale)" if approx else ""),
                        "remedy": "keep 600 mm between pillow end and desk edge — a bookcase or "
                                  "bedside unit between them gives the gap and the divider",
                        "doctrine": "形勢 [modern convention]"})
    out.append(dict(OVERHEAD_SEAT))
    return out
