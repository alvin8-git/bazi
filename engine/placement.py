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
