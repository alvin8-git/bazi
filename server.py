"""FengShui Family Compass — local LAN server (M2).

Run: .venv/bin/uvicorn server:app --host 0.0.0.0 --port 8808
Endpoints per the design contract (eng review 1A). LAN-only by design;
no auth (accepted risk, design doc "NOT in scope").
"""
from __future__ import annotations

import base64
import datetime as _dt
import json
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from engine.bazi import CLOCK, TRUE_SOLAR, build_chart
from engine.careers import career_paths
from engine.windows import timing_windows
from engine.domains import health_map, industry_map, life_domains, personality_axes
from engine.bazi import TEN_GOD_EN, ten_god
from engine.liunian import year_ganzhi
from engine.wuxing import HIDDEN_STEMS
from engine.shensha import (TEN_GOD_MEANING, life_palaces, natal_interactions, pillar_extras,
                            shensha, ten_god_pct)
from engine.htmlreport import _tosimp, build_report
from engine.import_family import import_family, load_family
from engine.aspects import compose_family
from engine.compare import compare_arrangements, compare_homes, compare_rooms
from engine.interpret import (STRUCTURE_TEXT, interpret_dates, interpret_family,
                              interpret_forecast, interpret_house,
                              interpret_housetab, interpret_names,
                              interpret_person, interpret_unit)
from engine.join import score_direction
from engine.hehun import pair_compatibility
from engine.liunian import (annual_afflictions, dayun_detail, multi_year_outlook,
                            person_forecast)
from engine.optimizer import optimize, score_assignment
from engine.report import chart_json
from engine.sectors import assign_grid, assign_pie, feature_analysis, load_rooms
from engine.optimizer import PAIR_CHONG, PAIR_HE
from engine.primer import PRIMERS
from engine.wuxing import (CHONG_MAP, ELEMENT_EN, HE_MAP, MOUNTAIN_ORDER,
                           mountain_of_degrees, mountain_palace)
from engine.xingming import analyze_name
from engine.xuankong import (annual_chart, annual_star, boundary_info,
                             natal_chart, natal_chart_from_degrees)
from engine.yongshen import yong_shen
from engine.zeri import rate_month
from engine.bazhai import ming_gua, gua_group, youxing_stars, STAR_SCORE

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="FengShui Family Compass")


@lru_cache(maxsize=None)
def _family():
    fam = ROOT / "data/family.json"
    if not fam.exists():
        import_family(ROOT / "Names.xlsx", fam)
    return load_family(fam)


@lru_cache(maxsize=None)
def _house():
    return json.loads((ROOT / "data/house.json").read_text("utf8"))


@lru_cache(maxsize=None)
def _rooms():
    return load_rooms(ROOT / "data/rooms.json")


def _canon(name: str) -> str:
    """Resolve a 简体 or 繁體 name to the canonical 繁體 form in family.json.
    The UI works in 简体 (only the Names tab shows 繁體); the engine stays 繁體."""
    for m in _family():
        if m.name == name or _tosimp(m.name) == name:
            return m.name
    return name


# Charts and per-(person, palace, year, period) scores are cached (eng review:
# nothing slow may sit in the simulator's recompute path).
@lru_cache(maxsize=64)
def _chart(name: str, policy: str):
    name = _canon(name)
    m = next((m for m in _family() if m.name == name), None)
    if m is None:
        raise HTTPException(404, f"unknown person {name}")
    return build_chart(m.name, m.sex, m.birth_dt, policy)


@lru_cache(maxsize=64)
def _ys(name: str, policy: str):
    return yong_shen(_chart(name, policy))


@lru_cache(maxsize=16)
def _natal(period: int):
    # degree-aware: applies 兼向替卦 automatically near mountain boundaries
    return natal_chart_from_degrees(period, _house()["facing_deg"])


@app.get("/api/family")
def api_family(policy: str = TRUE_SOLAR, year: int = 2026, period: int = 8):
    out = []
    natal, annual = _natal(period), annual_chart(year)
    for m in _family():
        c = _chart(m.name, policy)
        ys = _ys(m.name, policy)
        clock_hour = str(_chart(m.name, CLOCK).pillars["hour"])
        solar_hour = str(_chart(m.name, TRUE_SOLAR).pillars["hour"])
        gua = ming_gua(c.lichun_year, c.sex)
        scores = sorted((score_direction(c, ys, natal, annual, p)
                         for p in natal["palaces"]), key=lambda s: -s["total"])
        out.append({
            "name": _tosimp(m.name), "sex": m.sex,
            "birth": m.birth_dt.strftime("%Y-%m-%d %H:%M"),
            "pillars": {k: str(v) for k, v in c.pillars.items()},
            "day_master": c.day_master, "strength": c.strength["verdict"],
            "hour_pillar_differs": clock_hour != solar_hour,
            "yongshen": {"favourable": [ELEMENT_EN[e] + e for e in ys["favourable"]],
                         "colours": ys["colours"]},
            "gua": gua, "group": gua_group(gua),
            "auspicious_dirs": [p for p, s in youxing_stars(gua).items() if STAR_SCORE[s] > 0],
            "top_sectors": [{"direction": s["direction"], "palace": s["palace"],
                             "total": s["total"]} for s in scores[:3]],
        })
    charts, ys_all = _charts_and_ys(policy)
    return {"policy": policy, "year": year, "period": period, "people": out,
            "interpretation": interpret_family(charts, ys_all)}


@app.get("/api/chart/{name}")
def api_chart(name: str, policy: str = TRUE_SOLAR, year: int = 2026):
    c = _chart(name, policy)
    return {"name": name, **chart_json(c), "yongshen": _ys(name, policy),
            "gua": ming_gua(c.lichun_year, c.sex),
            "group": gua_group(ming_gua(c.lichun_year, c.sex)),
            "youxing": youxing_stars(ming_gua(c.lichun_year, c.sex)),
            "shensha": shensha(c), "interactions": natal_interactions(c),
            "tengods_pct": ten_god_pct(c),
            "tengods_legend": {g: {"en": TEN_GOD_EN[g], "meaning": TEN_GOD_MEANING[g]}
                               for g in ten_god_pct(c)},
            "domains": life_domains(c, _ys(name, policy)),
            "dayun_detail": dayun_detail(c, year),
            "transit": (lambda st, br: {
                "year_gz": st + br,
                "year_stem_god": ten_god(c.day_master, st),
                "year_branch_god": ten_god(c.day_master, HIDDEN_STEMS[br][0]),
                "luck": next((d for d in dayun_detail(c, year) if d["current"]), None),
            })(*year_ganzhi(year)),
            "pillar_extras": pillar_extras(c), "personality": personality_axes(c),
            "health": health_map(c), "industries": industry_map(_ys(name, policy)),
            "careers": career_paths(c, _ys(name, policy)),
            "life_palaces": life_palaces(c),
            "windows": timing_windows(c, _ys(name, policy),
                                      dayun_detail(c, year), year),
            "interpretation": interpret_person(c, _ys(name, policy), year)}


@app.get("/api/house")
def api_house(year: int = 2026, method: str = "pie"):
    house, rooms = _house(), _rooms()
    return {"house": {**house, "facing_mountain": mountain_of_degrees(house["facing_deg"])},
            "natal": {str(p): _natal(p) for p in house["periods"]},
            "annual": annual_chart(year), "annual_center": annual_star(year),
            "afflictions": annual_afflictions(year),
            "default_assignment": {rid: [_tosimp(n) for n in names] for rid, names
                                   in rooms.get("default_assignment", {}).items()},
            "features": rooms.get("features") or {},
            "features_analysis": feature_analysis(
                rooms, mountain_palace(_natal(house["periods"][0])["sitting"])),
            "year": year, "method": method,
            "rooms": rooms["rooms"], "centroid": rooms["centroid"],
            "image_size": rooms["image_size"],
            "image_up_bearing": rooms["image_up_bearing"],
            "notes": [rooms["orientation_note"], rooms["trace_note"],
                      house["facing_note"], house["period_note"]],
            "interpretation": {str(p): interpret_housetab(_natal(p), annual_chart(year),
                                                          year, p)
                               for p in house["periods"]}}


class ScoreReq(BaseModel):
    assignment: dict[str, list[str]]   # room id → occupant names
    year: int = 2026
    period: int = 8
    method: str = "pie"                # pie | grid
    policy: str = TRUE_SOLAR


def _charts_and_ys(policy: str):
    charts = {m.name: _chart(m.name, policy) for m in _family()}
    ys = {m.name: _ys(m.name, policy) for m in _family()}
    return charts, ys


def _canon_assignment(assignment: dict[str, list[str]]) -> dict[str, list[str]]:
    return {rid: [_canon(n) for n in names] for rid, names in assignment.items()}


@app.post("/api/score")
def api_score(req: ScoreReq):
    charts, ys = _charts_and_ys(req.policy)
    rooms_by_id = {r["id"]: r for r in _rooms()["rooms"]}
    if any(rid not in rooms_by_id for rid in req.assignment):
        raise HTTPException(400, "unknown room in assignment")
    res = score_assignment(_canon_assignment(req.assignment), charts, ys, rooms_by_id,
                           _natal(req.period), annual_chart(req.year), req.method)
    return {**res, "method": req.method, "period": req.period, "year": req.year}


@app.post("/api/interpret")
def api_interpret(req: ScoreReq):
    """Deterministic plain-English narrative for the given arrangement (no LLM)."""
    charts, ys = _charts_and_ys(req.policy)
    couple = _rooms().get("default_assignment", {}).get("master", [])
    return interpret_house(charts, ys, _house(), _rooms()["rooms"], req.year, req.period,
                           req.method, current=_canon_assignment(req.assignment),
                           master_couple=couple)


class OptimizeReq(BaseModel):
    year: int = 2026
    period: int = 8
    method: str = "pie"
    policy: str = TRUE_SOLAR
    master_couple: list[str] = ["王大明", "李小华"]
    allow_master_split: bool = False
    lam: float = 1.0


@app.post("/api/optimize")
def api_optimize(req: OptimizeReq):
    charts, ys = _charts_and_ys(req.policy)
    try:
        res = optimize(charts, ys, _rooms()["rooms"], _natal(req.period),
                       annual_chart(req.year), req.method, req.lam,
                       [_canon(n) for n in req.master_couple], req.allow_master_split)
    except ValueError as e:
        raise HTTPException(422, str(e))
    for b in res["best"]:   # UI identifiers are 简体
        b["assignment"] = {k: [_tosimp(n) for n in v] for k, v in b["assignment"].items()}
    return res


def _room_of(name: str, method: str) -> str | None:
    name = _canon(name)
    default = _rooms().get("default_assignment", {})
    key = "palace_pie" if method == "pie" else "palace_grid"
    for rid, names in default.items():
        if name in names:
            room = next(r for r in _rooms()["rooms"] if r["id"] == rid)
            return room[key]
    return None


@app.get("/api/forecast/{name}")
def api_forecast(name: str, year: int = 2026, period: int = 8,
                 policy: str = TRUE_SOLAR, method: str = "pie"):
    chart = _chart(name, policy)
    fc = person_forecast(chart, _ys(name, policy), year, _room_of(name, method), period)
    return {"name": name, **fc,
            "outlook": multi_year_outlook(chart, _ys(name, policy), year),
            "interpretation": interpret_forecast(fc, _ys(name, policy), year)}


@app.get("/api/dates")
def api_dates(year: int = 2026, month: int = 1):
    if not 1 <= month <= 12:
        raise HTTPException(400, "month must be 1-12")
    members = [{"name": m.name,
                "year_branch": _chart(m.name, TRUE_SOLAR).pillars["year"].branch,
                "day_branch": _chart(m.name, TRUE_SOLAR).pillars["day"].branch}
               for m in _family()]
    days = rate_month(year, month, members)
    return {"year": year, "month": month, "days": days,
            "interpretation": interpret_dates(days)}


@app.get("/api/pair")
def api_pair(a: str, b: str, policy: str = TRUE_SOLAR):
    """合婚 pair compatibility between any two members."""
    a, b = _canon(a), _canon(b)
    if a == b:
        raise HTTPException(400, "pick two different people")
    res = pair_compatibility(_chart(a, policy), _chart(b, policy),
                             _ys(a, policy), _ys(b, policy))
    couple = _rooms().get("default_assignment", {}).get("master", [])
    from engine.aspects import palace_rooms_map
    from engine.remedies import arbitrate, pair_remedies
    acts = pair_remedies(_chart(a, policy), _chart(b, policy),
                         palace_rooms_map(_rooms()["rooms"]),
                         shared_room=(a in couple and b in couple))
    res["actions"], res["superseded"] = arbitrate(acts)
    return res


def _aspects_payload(assignment: dict[str, list[str]], year: int, period: int,
                     method: str, policy: str) -> dict:
    charts, ys = _charts_and_ys(policy)
    natal = _natal(period)
    res = compose_family(charts, ys, _rooms()["rooms"], assignment, natal,
                         annual_chart(year), year, method,
                         STRUCTURE_TEXT.get(natal["structure"], "a mixed structure"),
                         couple=_rooms().get("default_assignment",
                                             {}).get("master", []))
    res["people"] = {_tosimp(n): cards for n, cards in res["people"].items()}
    res["rooms"] = {_tosimp(n): c for n, c in res["rooms"].items()}
    for cards in res["people"].values():
        for c in cards:
            c["subject"]["id"] = c["subject"]["label"] = _tosimp(c["subject"]["id"])
    for c in res["rooms"].values():
        c["subject"]["label"] = _tosimp(c["subject"]["label"])
    return res


@app.get("/api/aspects")
def api_aspects(year: int = 2026, period: int = 8, method: str = "pie",
                policy: str = TRUE_SOLAR):
    """Aspect cards (INTERPRET layer) for the default arrangement — §3 cards."""
    return _aspects_payload(_rooms().get("default_assignment", {}), year,
                            period, method, policy)


@app.post("/api/aspects")
def api_aspects_for(req: ScoreReq):
    """Aspect cards for an ARBITRARY arrangement — the live site's reactive
    path (2A: live reactive, snapshot static)."""
    rooms_by_id = {r["id"]: r for r in _rooms()["rooms"]}
    if any(rid not in rooms_by_id for rid in req.assignment):
        raise HTTPException(400, "unknown room in assignment")
    return _aspects_payload(_canon_assignment(req.assignment), req.year,
                            req.period, req.method, req.policy)


@app.get("/api/compare")
def api_compare(kind: str = "homes", person: str | None = None,
                year: int = 2026, period: int = 8, method: str = "pie",
                policy: str = TRUE_SOLAR):
    """M2 Compare 对比: same cards side-by-side. kinds: homes | rooms |
    arrangements. `person` required for kind=rooms."""
    charts, ys = _charts_and_ys(policy)
    if kind == "homes":
        res = compare_homes(charts, ys, year, period, method)
    elif kind == "rooms":
        if not person:
            raise HTTPException(400, "kind=rooms needs ?person=")
        name = _canon(person)
        if name not in charts:
            raise HTTPException(404, f"unknown person {person}")
        res = compare_rooms(charts[name], ys[name], _rooms()["rooms"],
                            _natal(period), annual_chart(year), year, method)
        res["person"] = _tosimp(res["person"])
    elif kind == "arrangements":
        default = _rooms().get("default_assignment", {})
        res = compare_arrangements(charts, ys, _rooms()["rooms"], default,
                                   _natal(period), annual_chart(year), year,
                                   method, default.get("master", []))
    else:
        raise HTTPException(400, f"unknown kind {kind}")
    for col in res["columns"]:
        for c in col["cards"]:
            c["subject"]["label"] = _tosimp(c["subject"]["label"])
    return res


@app.get("/api/extras")
def api_extras(year: int = 2026, method: str = "pie", policy: str = TRUE_SOLAR):
    """Battlecard extras for the report: per-person BaZi profiles, the house
    placement audit and the family harmony matrix."""
    from engine.extras import harmony_matrix, house_audit, person_profile
    charts, ys = _charts_and_ys(policy)
    rooms = _rooms()["rooms"]
    master = _rooms().get("default_assignment", {}).get("master") or list(charts)
    profiles = {_tosimp(n): person_profile(c, ys[n], rooms, year, method)
                for n, c in charts.items()}
    audit = house_audit(charts, rooms, _natal(8), annual_chart(year),
                        master[0], method)
    for row in audit:
        row["text"] = _tosimp(row["text"])
    hm = harmony_matrix(charts, ys)
    hm["names"] = [_tosimp(n) for n in hm["names"]]
    for p in hm["pairs"]:
        p["a"], p["b"] = _tosimp(p["a"]), _tosimp(p["b"])
        p["band"] = _tosimp(p["band"])
        p["chips"] = [_tosimp(c) for c in p["chips"]]
    return {"profiles": profiles, "audit": audit, "harmony": hm}


@app.get("/api/planner")
def api_planner(year: int = 2026, month: int = 1, period: int = 8,
                method: str = "pie"):
    """M3 Planner 择时: reno-window card + best-day cards for one month."""
    if not 1 <= month <= 12:
        raise HTTPException(400, "month must be 1-12")
    from engine.aspects import palace_rooms_map
    from engine.planner import month_plan, reno_card
    members = [{"name": _tosimp(m.name),
                "year_branch": _chart(m.name, TRUE_SOLAR).pillars["year"].branch,
                "day_branch": _chart(m.name, TRUE_SOLAR).pillars["day"].branch}
               for m in _family()]
    days = rate_month(year, month, members)
    return {"year": year, "month": month, "v": 1,
            "reno": reno_card(year, annual_chart(year),
                              palace_rooms_map(_rooms()["rooms"], method)),
            **month_plan(days)}


@app.get("/api/primer")
def api_primer():
    """FengShui/BaZi 101 text for the per-tab 'How to read this page' panels."""
    return PRIMERS


@app.get("/api/names")
def api_names():
    from engine.xingming import name_interpretation
    people = [analyze_name(m.name) for m in _family()]
    for p in people:
        p["reading"] = name_interpretation(p)
    return {"people": people, "interpretation": interpret_names(people)}


class EvaluateReq(BaseModel):
    facing_deg: float
    period: int = 9              # candidate new units today are Period 9 builds
    year: int = 2026
    policy: str = TRUE_SOLAR


@app.post("/api/evaluate_unit")
def api_evaluate_unit(req: EvaluateReq):
    """Coarse mode (outside voice #4): schematic 8-direction evaluation of a
    candidate unit — no polygons, no on-site compass. Approximate by design."""
    natal = natal_chart_from_degrees(req.period, req.facing_deg)
    annual = annual_chart(req.year)
    charts, ys = _charts_and_ys(req.policy)
    people = []
    for name, c in charts.items():
        scores = sorted((score_direction(c, ys[name], natal, annual, p)
                         for p in natal["palaces"]), key=lambda s: -s["total"])
        people.append({"name": name,
                       "sectors": [{"direction": s["direction"], "palace": s["palace"],
                                    "total": s["total"]} for s in scores]})
    household = round(sum(p["sectors"][0]["total"] for p in people), 3)
    result = {"disclaimer": "APPROXIMATE — coarse mode: schematic sectors, unverified facing. "
                            "Confirm with an on-site compass reading before deciding.",
              "facing_deg": req.facing_deg, "facing_mountain": natal["facing"],
              "period": req.period, "structure": natal["structure"],
              "household_best_sum": household, "people": people}
    return {**result, "interpretation": interpret_unit(result)}


class TraceRoom(BaseModel):
    id: str
    label: str
    sleeping: bool = False
    capacity: int = 0
    poly: list[list[float]]


class TraceSave(BaseModel):
    name: str
    facing_deg: float
    periods: list[int] = [8, 9]
    image_up_bearing: float
    image_size: list[int]
    orientation_note: str = ""
    trace_note: str = ""
    facing_note: str = ""
    period_note: str = ""
    rooms: list[TraceRoom]
    default_assignment: dict[str, list[str]] = {}
    features: dict[str, list[float]] = {}   # e.g. {"main_door": [x, y], "stove": [x, y]}
    image: str | None = None      # data URI when a new floorplan was uploaded
    dry_run: bool = False


@app.get("/api/trace/current")
def api_trace_current():
    """Raw configs for the trace editor (no computed fields)."""
    return {"house": json.loads((ROOT / "data/house.json").read_text("utf8")),
            "rooms": json.loads((ROOT / "data/rooms.json").read_text("utf8"))}


@app.post("/api/trace/save")
def api_trace_save(req: TraceSave):
    ids = [r.id for r in req.rooms]
    if not req.rooms:
        raise HTTPException(422, "trace at least one room")
    if len(set(ids)) != len(ids):
        raise HTTPException(422, "duplicate room ids")
    for r in req.rooms:
        if len(r.poly) < 3:
            raise HTTPException(422, f"room '{r.id}': polygon needs ≥3 points")
    if not any(r.sleeping for r in req.rooms):
        raise HTTPException(422, "mark at least one room as sleeping")
    if not req.periods or any(p not in (8, 9) for p in req.periods):
        raise HTTPException(422, "periods must be a non-empty subset of [8, 9]")
    if not 0 <= req.facing_deg < 360:
        raise HTTPException(422, "facing_deg must be 0-359")

    room_dicts = [r.model_dump() for r in req.rooms]
    pie = assign_pie(room_dicts, req.image_up_bearing)
    grid = assign_grid(room_dicts, req.image_up_bearing)
    fm = mountain_of_degrees(req.facing_deg)
    preview = {"facing_mountain": fm,
               "boundary": boundary_info(req.facing_deg),
               "palaces": {rid: {"pie": pie[rid], "grid": grid[rid]} for rid in ids},
               "structures": {p: natal_chart_from_degrees(p, req.facing_deg)["structure"]
                              for p in sorted(set(req.periods))}}
    if req.dry_run:
        return {"saved": False, **preview}

    today = _dt.date.today().isoformat()
    rooms_cfg = {"image": "floorplan.jpeg", "image_size": req.image_size,
                 "image_up_bearing": req.image_up_bearing,
                 "orientation_note": req.orientation_note
                 or f"traced via /trace {today} — verify image_up_bearing with a compass",
                 "trace_note": req.trace_note or f"traced via /trace {today}",
                 "rooms": room_dicts,
                 "features": {k: v for k, v in req.features.items() if len(v) == 2},
                 "default_assignment": {k: v for k, v in req.default_assignment.items()
                                        if k in ids}}
    house_cfg = {"name": req.name, "facing_deg": req.facing_deg,
                 "facing_note": req.facing_note
                 or f"set via /trace {today} — verify with an on-site compass reading",
                 "periods": sorted(set(req.periods)),
                 "period_note": req.period_note or f"set via /trace {today}",
                 "provisional": True}

    ts = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backups = []
    targets = [(ROOT / "data/rooms.json", json.dumps(rooms_cfg, ensure_ascii=False, indent=2)),
               (ROOT / "data/house.json", json.dumps(house_cfg, ensure_ascii=False, indent=2))]
    img_bytes = None
    if req.image:
        try:
            img_bytes = base64.b64decode(req.image.split("base64,", 1)[1])
        except Exception:
            raise HTTPException(422, "image must be a base64 data URI")
    for path, _ in targets + ([(ROOT / "floorplan.jpeg", None)] if img_bytes else []):
        if path.exists():
            bak = path.with_name(f"{path.name}.bak-{ts}")
            bak.write_bytes(path.read_bytes())
            backups.append(str(bak.relative_to(ROOT)))
    for path, text in targets:
        path.write_text(text + "\n", "utf8")
    if img_bytes:
        (ROOT / "floorplan.jpeg").write_bytes(img_bytes)
    _house.cache_clear()
    _rooms.cache_clear()
    _natal.cache_clear()
    return {"saved": True, "backups": backups, **preview}


@app.get("/trace")
def trace_page():
    return FileResponse(ROOT / "web/trace.html")


def _snapshot_baked(year: int) -> dict:
    """Every API response the UI can request, keyed by the exact fetch path."""
    policies, periods, methods = (TRUE_SOLAR, CLOCK), (8, 9), ("pie", "grid")
    names = [m.name for m in _family()]
    get: dict = {"/api/names": api_names(), "/api/primer": PRIMERS}
    for pol in policies:
        for per in periods:
            get[f"/api/family?year={year}&period={per}&policy={pol}"] = \
                api_family(pol, year, per)
        for n in names:
            sn = _tosimp(n)   # the UI addresses people in 简体
            get[f"/api/chart/{quote(sn)}?policy={pol}&year={year}"] = api_chart(n, pol, year)
            for per in periods:
                for meth in methods:
                    get[f"/api/forecast/{quote(sn)}?year={year}&period={per}"
                        f"&policy={pol}&method={meth}"] = api_forecast(n, year, per, pol, meth)
    for meth in methods:
        get[f"/api/house?year={year}&method={meth}"] = api_house(year, meth)
    for pol in policies:          # 2A: cards baked STATIC for the default arrangement
        for per in periods:
            for meth in methods:
                get[f"/api/aspects?year={year}&period={per}&method={meth}"
                    f"&policy={pol}"] = api_aspects(year, per, meth, pol)
                for kd in ("homes", "arrangements"):
                    get[f"/api/compare?kind={kd}&year={year}&period={per}"
                        f"&method={meth}&policy={pol}"] = \
                        api_compare(kd, None, year, per, meth, pol)
                for n in names:
                    sn = quote(_tosimp(n))
                    get[f"/api/compare?kind=rooms&person={sn}&year={year}"
                        f"&period={per}&method={meth}&policy={pol}"] = \
                        api_compare("rooms", n, year, per, meth, pol)
    for pol in policies:
        for meth in methods:
            get[f"/api/extras?year={year}&method={meth}&policy={pol}"] = \
                api_extras(year, meth, pol)
    for mo in range(1, 13):
        get[f"/api/dates?year={year}&month={mo}"] = api_dates(year, mo)
        for meth in methods:
            get[f"/api/planner?year={year}&month={mo}&period=8&method={meth}"] = \
                api_planner(year, mo, 8, meth)
    for pol in policies:
        for na in names:
            for nb in names:
                if na != nb:
                    get[f"/api/pair?a={quote(_tosimp(na))}&b={quote(_tosimp(nb))}"
                        f"&policy={pol}"] = api_pair(na, nb, pol)

    # per-(person, palace) base scores + roommate pair terms → the JS scorer
    base, pairs = {}, {}
    for pol in policies:
        base[pol] = {}
        for per in periods:
            natal, annual = _natal(per), annual_chart(year)
            base[pol][per] = {_tosimp(n): {p: score_direction(_chart(n, pol), _ys(n, pol),
                                                              natal, annual, p)
                                           for p in natal["palaces"]} for n in names}
        pairs[pol] = {}
        for a in names:
            for b in names:
                if a == b:
                    continue
                b1 = _chart(a, pol).pillars["day"].branch
                b2 = _chart(b, pol).pillars["day"].branch
                if CHONG_MAP.get(b1) == b2:
                    entry = {"rule_id": "pair-chong", "layer": "bazhai",
                             "source_ref": "地支六沖 (roommate day branches)",
                             "explanation": f"{a}({b1}) 沖 {b}({b2})",
                             "weight": 1.0, "contribution": round(PAIR_CHONG, 3)}
                elif HE_MAP.get(b1) == b2:
                    entry = {"rule_id": "pair-he", "layer": "bazhai",
                             "source_ref": "地支六合 (roommate day branches)",
                             "explanation": f"{a}({b1}) 合 {b}({b2})",
                             "weight": 1.0, "contribution": round(PAIR_HE, 3)}
                else:
                    continue
                pairs[pol].setdefault(_tosimp(a), {})[_tosimp(b)] = entry

    default = _rooms().get("default_assignment", {})
    interp = {f"{per}|{meth}|{pol}": api_interpret(ScoreReq(
                  assignment=default, year=year, period=per, method=meth, policy=pol))
              for per in periods for meth in methods for pol in policies}
    unit = {f"{m}|{per}": api_evaluate_unit(EvaluateReq(
                facing_deg=i * 15, period=per, year=year))
            for i, m in enumerate(MOUNTAIN_ORDER) for per in periods}

    img = base64.b64encode((ROOT / "floorplan.jpeg").read_bytes()).decode()
    return {"year": year, "generated": _dt.date.today().isoformat(),
            "people": [_tosimp(n) for n in names],
            "master_couple": [_tosimp(n) for n in default.get("master", [])],
            "rooms": _rooms()["rooms"], "MO": list(MOUNTAIN_ORDER),
            "floorplan": "data:image/jpeg;base64," + img,
            "get": get, "base": base, "pairs": pairs,
            "interpret": interp, "unit": unit}


@app.get("/snapshot")
def snapshot(year: int = 2026):
    """The identical interactive website as ONE offline file — save & email it."""
    html = (ROOT / "web/index.html").read_text("utf8")
    css = (ROOT / "web/style.css").read_text("utf8")
    js = (ROOT / "web/app.js").read_text("utf8")
    baked = json.dumps(_snapshot_baked(year), ensure_ascii=False).replace("</", "<\\/")
    html = html.replace('<link rel="stylesheet" href="/static/style.css">',
                        f"<style>{css}</style>")
    html = html.replace('<script src="/static/app.js"></script>',
                        f"<script>window.__BAKED__={baked};</script>\n<script>{js}</script>")
    return HTMLResponse(html, headers={
        "Content-Disposition": 'inline; filename="fengshuiTowerA.html"'})


@app.get("/report")
def report(year: int = 2026, period: int = 8, month: int | None = None,
           policy: str = TRUE_SOLAR):
    """Self-contained emailable HTML report — save the page and attach it."""
    return HTMLResponse(build_report(year, period, month, policy))


@app.get("/")
def index():
    return FileResponse(ROOT / "web/index.html")


@app.get("/floorplan.jpeg")
def floorplan():
    return FileResponse(ROOT / "floorplan.jpeg")


from public import router as public_router  # noqa: E402  (bazifor.me surfaces)
app.include_router(public_router)

app.mount("/static", StaticFiles(directory=ROOT / "web"), name="static")
