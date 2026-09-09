"""M1 CLI: full-family engine report as JSON + terminal summary.

Usage: .venv/bin/python -m engine.report [--year 2026]
Emits data/out/m1_report.json. Period is a runtime parameter; both Period 8
and Period 9 charts are emitted until the renovation date is confirmed
(outside voice #2).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .bazi import CLOCK, TRUE_SOLAR, build_chart
from .import_family import import_family, load_family
from .interpret import interpret_house
from .join import score_all_directions
from .sectors import load_rooms
from .wuxing import ELEMENT_EN, mountain_of_degrees
from .xuankong import annual_chart, annual_star, natal_chart_from_degrees
from .yongshen import yong_shen

ROOT = Path(__file__).resolve().parent.parent


def chart_payload(name: str, c, ys: dict, year: int) -> dict:
    """The full Reading 命书 payload (13 sections) for ANY chart — shared by
    the family /api/chart route and the public workspace reading route."""
    from .bazhai import gua_group, ming_gua, youxing_stars
    from .bazi import ten_god
    from .careers import career_paths
    from .domains import (health_map, industry_map, life_domains,
                          personality_axes)
    from .interpret import interpret_person
    from .liunian import dayun_detail, year_ganzhi
    from .shensha import (TEN_GOD_MEANING, life_palaces, natal_interactions,
                          pillar_extras, shensha, ten_god_pct)
    from .windows import timing_windows
    from .bazi import TEN_GOD_EN
    from .wuxing import HIDDEN_STEMS
    # advice layer lives with the report templates; imported here so the
    # Reading tab carries the strategy content in-place (one source of truth)
    from scripts.bazi_report import strategy_payload
    st, br = year_ganzhi(year)
    return {"name": name, "sex": c.sex, **chart_json(c), "yongshen": ys,
            "strategy": strategy_payload(c, ys, year),
            "gua": ming_gua(c.lichun_year, c.sex),
            "group": gua_group(ming_gua(c.lichun_year, c.sex)),
            "youxing": youxing_stars(ming_gua(c.lichun_year, c.sex)),
            "shensha": shensha(c), "interactions": natal_interactions(c),
            "tengods_pct": ten_god_pct(c),
            "tengods_legend": {g: {"en": TEN_GOD_EN[g],
                                   "meaning": TEN_GOD_MEANING[g]}
                               for g in ten_god_pct(c)},
            "domains": life_domains(c, ys),
            "dayun_detail": dayun_detail(c, year),
            "transit": {
                "year_gz": st + br,
                "year_stem_god": ten_god(c.day_master, st),
                "year_branch_god": ten_god(c.day_master, HIDDEN_STEMS[br][0]),
                "luck": next((d for d in dayun_detail(c, year)
                              if d["current"]), None),
            },
            "pillar_extras": pillar_extras(c),
            "personality": personality_axes(c),
            "health": health_map(c), "industries": industry_map(ys),
            "careers": career_paths(c, ys),
            "life_palaces": life_palaces(c),
            "windows": timing_windows(c, ys, dayun_detail(c, year), year),
            "interpretation": interpret_person(c, ys, year)}


def chart_json(c) -> dict:
    return {
        "policy": c.policy,
        "effective_time": c.effective_dt.strftime("%Y-%m-%d %H:%M"),
        "pillars": {k: str(v) for k, v in c.pillars.items()},
        "day_master": c.day_master,
        "ten_gods": c.ten_gods,
        "hidden_gods": {k: [f"{s}({g})" for s, g in v] for k, v in c.hidden_gods.items()},
        "element_weights": {ELEMENT_EN[e]: w for e, w in c.element_weights.items()},
        "strength": c.strength,
        "dayun": [{"gz": str(d.gz), "ages": f"{d.start_age:.0f}-{d.end_age:.0f}"} for d in c.dayun],
        "citations": c.citations,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2026)
    ap.add_argument("--facing-deg", type=float, default=None,
                    help="compass facing in degrees; default reads data/house.json")
    args = ap.parse_args()

    house = json.loads((ROOT / "data/house.json").read_text("utf8"))
    facing_deg = args.facing_deg if args.facing_deg is not None else house["facing_deg"]
    fam_json = ROOT / "data/family.json"
    if not fam_json.exists():
        import_family(ROOT / "Names.xlsx", fam_json)
    members = load_family(fam_json)

    annual = annual_chart(args.year)
    facing_mtn = mountain_of_degrees(facing_deg)
    natal = {p: natal_chart_from_degrees(p, facing_deg) for p in house["periods"]}

    report = {"year": args.year, "annual_center_star": annual_star(args.year),
              "house": {**house, "facing_mountain": facing_mtn,
                        "provisional": house.get("provisional", True)},
              "natal_charts": natal, "people": []}

    primary_charts, ys_map = {}, {}
    for m in members:
        charts = {p: build_chart(m.name, m.sex, m.birth_dt, p) for p in (TRUE_SOLAR, CLOCK)}
        primary = charts[TRUE_SOLAR]
        ys = yong_shen(primary)
        primary_charts[m.name], ys_map[m.name] = primary, ys
        person = {"name": m.name, "sex": m.sex,
                  "birth": m.birth_dt.strftime("%Y-%m-%d %H:%M"),
                  "charts": {p: chart_json(c) for p, c in charts.items()},
                  "hour_pillar_differs":
                      str(charts[CLOCK].pillars["hour"]) != str(charts[TRUE_SOLAR].pillars["hour"]),
                  "yongshen": {**ys, "favourable": [ELEMENT_EN[e] + e for e in ys["favourable"]],
                               "unfavourable": [ELEMENT_EN[e] + e for e in ys["unfavourable"]]},
                  "direction_scores": {str(p): score_all_directions(primary, ys, n, annual)
                                       for p, n in natal.items()}}
        report["people"].append(person)

    rooms_path = ROOT / "data/rooms.json"
    if rooms_path.exists():
        rooms_data = load_rooms(rooms_path)
        current = rooms_data.get("default_assignment")
        report["interpretation"] = interpret_house(
            primary_charts, ys_map, house, rooms_data["rooms"], args.year,
            house["periods"][0], current=current,
            master_couple=(current or {}).get("master", []))

    out = ROOT / "data/out/m1_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), "utf8")

    # terminal summary
    print(f"=== FengShui Family Compass — M1 engine report ({args.year}) ===")
    print(f"House: facing {facing_deg}° → {facing_mtn}山向 | periods {house['periods']}"
          f" | annual center star {annual_star(args.year)}"
          + (" | PROVISIONAL facing/period" if report['house']['provisional'] else ""))
    for p, n in natal.items():
        print(f"  Period {p}: {n['sitting']}山{n['facing']}向 → {n['structure']}")
    for person in report["people"]:
        pri = person["charts"][TRUE_SOLAR]
        flag = " (hour differs from clock chart!)" if person["hour_pillar_differs"] else ""
        print(f"\n{person['name']} ({person['sex']}) {person['birth']}{flag}")
        print(f"  pillars [{pri['effective_time']} solar]: "
              + " ".join(pri['pillars'][k] for k in ('year', 'month', 'day', 'hour'))
              + f" | DM {pri['day_master']} {pri['strength']['verdict']}")
        print(f"  用神: {' '.join(person['yongshen']['favourable'])}"
              f" | colours: {'、'.join(person['yongshen']['colours'])}")
        for p in natal:
            top = person["direction_scores"][str(p)][:3]
            tops = ", ".join(f"{s['direction']}({s['total']:+.2f})" for s in top)
            print(f"  best sectors P{p}: {tops}")
    for sec in report.get("interpretation", {}).get("sections", []):
        print(f"\n== {sec['heading']} ==")
        for line in sec["lines"]:
            print("  - " + line)
    print(f"\nfull report → {out}")


if __name__ == "__main__":
    main()
