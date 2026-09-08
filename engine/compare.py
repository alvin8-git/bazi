"""Compare 对比 — N subjects rendered as the same cards, side by side (M2).

Generic column contract: {"id", "label", "headline", "cards": [AspectCard...]}.
Presets: homes (the battlecard's three homes, live), rooms (one person across
every sleeping room of the active house), arrangements (current vs optimal).
"""
from __future__ import annotations

import json
from pathlib import Path

from .aspects import compose_family, room_fit_card
from .battlecard import HOMES
from .interpret import STRUCTURE_TEXT
from .optimizer import optimize, score_assignment
from .sectors import load_rooms
from .xuankong import annual_chart, natal_chart_from_degrees

ROOT = Path(__file__).resolve().parent.parent


def compare_homes(charts: dict, ys_map: dict, year: int, period: int,
                  method: str = "pie") -> dict:
    """One column per registered home: home cards + recommended-fit headline."""
    columns = []
    annual = annual_chart(year)
    for tag, label, hf, rf in HOMES:
        house = json.loads((ROOT / hf).read_text("utf8"))
        rooms_cfg = load_rooms(ROOT / rf)
        natal = natal_chart_from_degrees(period, house["facing_deg"])
        default = rooms_cfg.get("default_assignment", {})
        couple = default.get("master", [])
        # compare homes on each home's OPTIMAL arrangement (battlecard parity)
        try:
            assignment = optimize(charts, ys_map, rooms_cfg["rooms"], natal,
                                  annual, method, 1.0, couple,
                                  False)["best"][0]["assignment"]
        except ValueError:
            assignment = default
        res = compose_family(charts, ys_map, rooms_cfg["rooms"], assignment,
                             natal, annual, year, method,
                             STRUCTURE_TEXT.get(natal["structure"],
                                                "a mixed structure"), couple)
        rooms_by_id = {r["id"]: r for r in rooms_cfg["rooms"]}
        fit = score_assignment(assignment, charts, ys_map, rooms_by_id, natal,
                               annual, method)["household_total"]
        kind = f" ({natal['chart_type']})" if natal.get("chart_type") == "替卦" else ""
        columns.append({
            "id": tag, "label": label,
            "headline": f"{natal['structure']}{kind} · optimal fit {fit:+.2f}",
            "boundary": natal.get("boundary"),
            "cards": res["home"]})
    return {"kind": "homes", "year": year, "period": period, "method": method,
            "columns": columns}


def compare_rooms(chart, ys, rooms: list[dict], natal: dict,
                  annual: dict[str, int], year: int,
                  method: str = "pie") -> dict:
    """One column per sleeping room: this person's suitability card in each."""
    key = "palace_pie" if method == "pie" else "palace_grid"
    columns = []
    for room in rooms:
        if not room["sleeping"]:
            continue
        card = room_fit_card(chart, ys, room, room[key], natal, annual, year)
        columns.append({"id": room["id"], "label": room["label"],
                        "headline": f"fit {card['raw_fit']:+.2f}",
                        "cards": [card]})
    columns.sort(key=lambda c: -c["cards"][0]["score"])
    return {"kind": "rooms", "person": chart.person, "year": year,
            "period": natal["period"], "method": method, "columns": columns}


def compare_arrangements(charts: dict, ys_map: dict, rooms: list[dict],
                         current: dict[str, list[str]], natal: dict,
                         annual: dict[str, int], year: int, method: str,
                         couple: list[str]) -> dict:
    """Current arrangement vs the optimizer's best, as room-card columns."""
    key = "palace_pie" if method == "pie" else "palace_grid"
    rooms_by_id = {r["id"]: r for r in rooms}

    def column(cid, label, assignment):
        total = score_assignment(assignment, charts, ys_map, rooms_by_id, natal,
                                 annual, method)["household_total"]
        cards = []
        for rid, names in assignment.items():
            room = rooms_by_id.get(rid)
            if room is None:
                continue
            for n in names:
                cards.append(room_fit_card(charts[n], ys_map[n], room,
                                           room[key], natal, annual, year))
        cards.sort(key=lambda c: -c["score"])
        return {"id": cid, "label": label,
                "headline": f"household total {total:+.2f}", "cards": cards}

    columns = [column("current", "Current 当前", current)]
    try:
        best = optimize(charts, ys_map, rooms, natal, annual, method, 1.0,
                        couple, False)["best"][0]
        columns.append(column("optimal", "Optimal 最优", best["assignment"]))
    except ValueError as e:
        columns.append({"id": "optimal", "label": "Optimal 最优",
                        "headline": f"no feasible arrangement: {e}", "cards": []})
    return {"kind": "arrangements", "year": year, "period": natal["period"],
            "method": method, "columns": columns}
