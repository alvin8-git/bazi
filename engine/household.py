"""Household roles and the parents-in-master default assignment (pure, no engine calls).

assign_roles: who the parents are, from ages alone. default_assignment: parents take the
master room, everyone else is placed by a caller-supplied optimiser (or greedily by each
person's own room ranking when the optimiser cannot run).
"""
from __future__ import annotations

ADULT = 18
GAP = 16            # a parent is at least this much older than every non-parent


def assign_roles(people: list[dict]) -> dict[str, str]:
    """people = [{name, age}] → {name: "parent" | "adult" | "child"}."""
    roles = {p["name"]: ("child" if p["age"] < ADULT else "adult") for p in people}
    adults = sorted((p for p in people if p["age"] >= ADULT), key=lambda p: -p["age"])
    minors = [p for p in people if p["age"] < ADULT]
    if not adults:
        return roles
    if len(adults) == 1:
        if minors:
            roles[adults[0]["name"]] = "parent"
        return roles
    if len(adults) == 2 and not minors:
        for p in adults:
            roles[p["name"]] = "parent"
        return roles
    top2 = adults[:2]
    others = adults[2:] + minors
    youngest_parent = min(p["age"] for p in top2)
    if others and all(p["age"] <= youngest_parent - GAP for p in others):
        for p in top2:
            roles[p["name"]] = "parent"
    return roles


def master_room(rooms: list[dict]) -> str | None:
    """The master bedroom id: typed as master, named master, or the largest sleeping room."""
    sleeping = [r for r in rooms if r.get("sleeping")]
    if not sleeping:
        return None
    for r in sleeping:
        if (r.get("rtype") or "").startswith("Master") or r["id"] == "master" \
                or r["id"].startswith("master_") or "master" in (r.get("label") or "").lower():
            return r["id"]
    return max(sleeping, key=lambda r: r.get("capacity") or 0)["id"]


def default_assignment(roles: dict, rooms: list[dict], person_rooms: dict,
                       optimise_rest=None) -> dict | None:
    """{room_id: [names]} with parents in the master room; None when no parents or no
    master. `person_rooms` = {name: [room ids best → worst]}; `optimise_rest(names, rooms)`
    may return {room_id: [names]} for the remaining people or raise."""
    parents = [n for n, r in roles.items() if r == "parent"]
    master = master_room(rooms)
    if not parents or master is None:
        return None
    by_id = {r["id"]: r for r in rooms}
    if (by_id[master].get("capacity") or 0) < len(parents):
        return None
    assignment = {master: list(parents)}
    rest = [n for n in roles if n not in parents]
    rest_rooms = [r for r in rooms if r.get("sleeping") and r["id"] != master]
    if not rest:
        return assignment
    if optimise_rest is not None:
        try:
            placed = optimise_rest(rest, rest_rooms)
            if placed is not None:
                assignment.update({rid: list(ns) for rid, ns in placed.items() if ns})
                return assignment
        except (ValueError, KeyError, IndexError):
            pass
    free = {r["id"]: (r.get("capacity") or 0) for r in rest_rooms}
    for n in rest:
        for rid in person_rooms.get(n, []):
            if free.get(rid, 0) > 0:
                assignment.setdefault(rid, []).append(n)
                free[rid] -= 1
                break
        else:
            return None                      # nobody fits: let the caller use the optimal
    return assignment
