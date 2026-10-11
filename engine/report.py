"""CLI: full-family engine report as JSON + terminal summary.

Usage: .venv/bin/python -m engine.report [--year 2026]
Emits data/out/m1_report.json. Period is a runtime parameter; both Period 8
and Period 9 charts are emitted until the renovation date is confirmed
(outside voice #2).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .plain import plain_reading
from .story import compose_story
from .bazi import CLOCK, TRUE_SOLAR, build_chart, localized_chart
from .i18n import L
from .import_family import import_family, load_family
from .interpret import interpret_house
from .join import score_all_directions
from .sectors import load_rooms
from .wuxing import ELEMENT_EN, mountain_of_degrees
from .xuankong import annual_chart, annual_star, natal_chart_from_degrees
from .yongshen import yong_shen
from .extras import compass_afflictions, placements

ROOT = Path(__file__).resolve().parent.parent


def chart_payload(name: str, c, ys: dict, year: int, lang: str = "en") -> dict:
    """The full Reading 命书 payload (13 sections) for ANY chart — shared by
    the family /api/chart route and the public workspace reading route."""
    from .bazhai import gua_group, ming_gua, youxing_stars
    from .bazi import ten_god
    from .careers import career_paths, career_roles
    from .domains import (health_map, industry_map, life_domains,
                          personality_axes)
    from .interpret import (element_relations, four_palaces, interpret_person,
                            ten_god_insights)
    from .liunian import dayun_detail, year_ganzhi
    from .shensha import (TEN_GOD_MEANING, life_palaces, natal_interactions,
                          pillar_extras, shensha, ten_god_pct)
    from .windows import timing_windows
    from .tiaohou import tiaohou_reading
    from .synthesis import (clinical_report, geju_line, medicine_ranking,
                            spouse_reading, synthesis, xiji_table)
    from .daily import daily_fortune
    from .bazi import TEN_GOD_EN
    from .wuxing import HIDDEN_STEMS
    # advice layer lives with the report templates; imported here so the
    # Reading tab carries the strategy content in-place (one source of truth)
    from scripts.bazi_report import strategy_payload
    st, br = year_ganzhi(year)
    _pct = ten_god_pct(c)
    _insights = ten_god_insights(c, ys, lang=lang)
    _palaces = four_palaces(c, ys, lang=lang)
    _dayun = dayun_detail(c, year, lang=lang)
    _windows = timing_windows(c, ys, _dayun, year, lang=lang)
    _tiaohou = tiaohou_reading(c, ys, lang=lang)
    _gua = ming_gua(c.lichun_year, c.sex)
    from .yongshen import yong_shen
    # the citations are display text; the favourable lists and colours are the caller's and stay as they are
    _ys = ys if lang != "zh" else {**ys, "citations": yong_shen(c, lang=lang)["citations"]}
    p = {"name": name, "sex": c.sex, **chart_json(c, lang), "yongshen": _ys,
            "synthesis_lines": synthesis(c, ys, _pct, _insights, _windows, _tiaohou, lang=lang),
            "geju": geju_line(c, lang=lang),
            "tiaohou": _tiaohou,
            "medicine_rank": medicine_ranking(c, ys, lang=lang),
            "xiji": xiji_table(c, ys, _pct, lang=lang),
            "spouse_reading": spouse_reading(c, ys, _pct, _palaces, _windows, lang=lang),
            "strategy": strategy_payload(c, ys, year, lang=lang),
            "element_relations": element_relations(c, lang=lang),
            "tengod_insights": _insights,
            "palaces": _palaces,
            "gua": _gua,
            "group": gua_group(_gua, lang=lang),
            "youxing": youxing_stars(_gua),
            "shensha": shensha(c, lang=lang), "interactions": natal_interactions(c, lang=lang),
            "tengods_pct": ten_god_pct(c),
            "tengods_legend": {g: {"en": L("bazi.TEN_GOD_EN", TEN_GOD_EN, lang)[g],
                                   "meaning": L("shensha.TEN_GOD_MEANING", TEN_GOD_MEANING, lang)[g]}
                               for g in ten_god_pct(c)},
            "domains": life_domains(c, ys, lang=lang),
            "dayun_detail": _dayun,
            "transit": {
                "year_gz": st + br,
                "year_stem_god": ten_god(c.day_master, st),
                "year_branch_god": ten_god(c.day_master, HIDDEN_STEMS[br][0]),
                "luck": next((d for d in _dayun
                              if d["current"]), None),
            },
            "pillar_extras": pillar_extras(c),
            "personality": personality_axes(c, lang=lang),
            "health": health_map(c, lang=lang), "industries": industry_map(ys, lang=lang),
            "careers": career_paths(c, ys, lang=lang),
            "life_palaces": life_palaces(c, lang=lang),
            "windows": _windows,
            "interpretation": interpret_person(c, ys, year, lang=lang)}
    # the geomancer's report reads the assembled payload so it cites the same numbers the tabs draw
    p["synthesis"] = clinical_report(p, lang=lang)
    p["daily"] = daily_fortune(c, ys, lang=lang)          # next 30 days from today, six activities
    p["career_roles"] = career_roles(c, ys, lang=lang)
    p["placements"] = placements(c, lang=lang)
    p["afflictions"] = compass_afflictions(c, year, lang=lang)
    p["plain"] = plain_reading(p, lang)              # plain-language layer, read from the assembled payload
    p["story"] = compose_story(p, p["plain"], lang)  # story layer: chapter paragraphs, each sentence tagged with its evidence
    return p


def chart_json(c, lang: str = "en") -> dict:
    lc = localized_chart(c, lang)      # the strength walkthrough and the citations are display text; every number is the same
    return {
        "policy": c.policy,
        "effective_time": c.effective_dt.strftime("%Y-%m-%d %H:%M"),
        "pillars": {k: str(v) for k, v in c.pillars.items()},
        "day_master": c.day_master,
        "ten_gods": c.ten_gods,
        "hidden_gods": {k: [f"{s}({g})" for s, g in v] for k, v in c.hidden_gods.items()},
        "element_weights": {ELEMENT_EN[e]: w for e, w in c.element_weights.items()},
        "strength": lc.strength,
        "dayun": [{"gz": str(d.gz), "ages": f"{d.start_age:.0f}-{d.end_age:.0f}"} for d in c.dayun],
        "citations": lc.citations,
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
    print(f"=== FengShui Family Compass: engine report ({args.year}) ===")
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
