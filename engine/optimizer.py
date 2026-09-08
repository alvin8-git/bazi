"""M3: constrained household room assignment.

HARD constraints first (outside voice #3): the master couple stays together in
the Master unless explicitly allowed to split; per-room occupant caps from
rooms.json. Then brute-force the tiny feasible set (≤4^5 assignments).

Objective (additive, eng review): maximize Σ person-room 3-layer scores
+ λ·Σ pairwise roommate terms (六合 bonus, 六沖 penalty), λ tunable.
"""
from __future__ import annotations

from itertools import product

from .join import score_direction
from .wuxing import CHONG_MAP, HE_MAP

PAIR_CHONG, PAIR_HE = -0.25, 0.15   # per directed pair, matches /api/score


def score_assignment(assignment: dict[str, list[str]], charts: dict, ys_map: dict,
                     rooms_by_id: dict, natal: dict, annual: dict,
                     method: str = "pie", lam: float = 1.0) -> dict:
    """Score one assignment. `charts`/`ys_map`: name → Chart / 用神 dict."""
    palace_key = "palace_pie" if method == "pie" else "palace_grid"
    results, violations, household = [], [], 0.0

    for room_id, names in assignment.items():
        room = rooms_by_id.get(room_id)
        if room is None:
            violations.append(f"unknown room {room_id}")
            continue
        if not room["sleeping"] and names:
            violations.append(f"{room['label']} is not a sleeping room")
        if room["capacity"] and len(names) > room["capacity"]:
            violations.append(f"{room['label']} over capacity ({len(names)}/{room['capacity']})")
        for name in names:
            c = charts[name]
            s = score_direction(c, ys_map[name], natal, annual, room[palace_key])
            for other in names:
                if other == name:
                    continue
                b1, b2 = c.pillars["day"].branch, charts[other].pillars["day"].branch
                if CHONG_MAP.get(b1) == b2:
                    s["breakdown"].append({
                        "rule_id": "pair-chong", "layer": "bazhai",
                        "source_ref": "地支六沖 (roommate day branches)",
                        "explanation": f"{name}({b1}) 沖 {other}({b2})",
                        "weight": lam, "contribution": round(PAIR_CHONG * lam, 3)})
                elif HE_MAP.get(b1) == b2:
                    s["breakdown"].append({
                        "rule_id": "pair-he", "layer": "bazhai",
                        "source_ref": "地支六合 (roommate day branches)",
                        "explanation": f"{name}({b1}) 合 {other}({b2})",
                        "weight": lam, "contribution": round(PAIR_HE * lam, 3)})
            s["total"] = round(sum(b["contribution"] for b in s["breakdown"]), 3)
            s["room"], s["room_label"] = room_id, room["label"]
            results.append(s)
            household += s["total"]

    assigned = [n for ns in assignment.values() for n in ns]
    for name in charts:
        if name not in assigned:
            violations.append(f"{name} has no room")
    for name in set(n for n in assigned if assigned.count(n) > 1):
        violations.append(f"{name} assigned to multiple rooms")
    return {"scores": results, "household_total": round(household, 3),
            "violations": violations}


def optimize(charts: dict, ys_map: dict, rooms: list[dict], natal: dict, annual: dict,
             method: str = "pie", lam: float = 1.0,
             master_couple: list[str] | None = None,
             allow_master_split: bool = False, top: int = 3) -> dict:
    """Enumerate every feasible assignment, return the top N with breakdowns."""
    sleeping = [r for r in rooms if r["sleeping"]]
    rooms_by_id = {r["id"]: r for r in rooms}
    names = list(charts)
    couple = master_couple if master_couple is not None else []

    if sum(r["capacity"] for r in sleeping) < len(names):
        raise ValueError("total sleeping capacity below household size — check rooms.json")

    free = [n for n in names if allow_master_split or n not in couple]
    candidates = []
    room_ids = [r["id"] for r in sleeping]
    for combo in product(room_ids, repeat=len(free)):
        assignment = {rid: [] for rid in room_ids}
        if not allow_master_split:
            for n in couple:
                assignment["master"].append(n)
        for n, rid in zip(free, combo):
            assignment[rid].append(n)
        if any(len(v) > rooms_by_id[rid]["capacity"] for rid, v in assignment.items()):
            continue
        res = score_assignment(assignment, charts, ys_map, rooms_by_id, natal, annual,
                               method, lam)
        if res["violations"]:
            continue
        candidates.append({"assignment": {k: v for k, v in assignment.items() if v}, **res})

    if not candidates:
        raise ValueError("no feasible assignment — constraints are unsatisfiable "
                         "(capacity vs household size, or master_couple misconfigured)")
    candidates.sort(key=lambda c: -c["household_total"])
    return {"evaluated": len(candidates), "constraints": {
                "master_couple": couple, "allow_master_split": allow_master_split,
                "lambda": lam},
            "best": candidates[:top]}
