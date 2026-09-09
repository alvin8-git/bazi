"""bazifor.me public surfaces — stateless, workspace-token based.

Three surfaces, none touching the single-family global config:
  /start    — enter your own birth data, add up to 8 people, harmony matrix,
              full per-person strategy reports
  /fengshui — upload a floorplan, give the facing, draw rooms, assign people,
              get the flying-star chart + per-person room scores (cited)
  /baby     — newborn/expected-baby chart with 用神-based naming direction

Storage: one row per workspace token, 6-month TTL. Backend is Upstash Redis
(REST, stdlib urllib) when KV_REST_API_URL/UPSTASH_REDIS_REST_URL is set —
required on Vercel, where lambda /tmp is per-instance and ephemeral — else
SQLite under data/public_store/. No accounts, no payments — the
validation-first architecture from docs/designs/bazifor-me-wedge.md.
"""
from __future__ import annotations

import json
import re
import secrets
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from engine.bazhai import STAR_SCORE, gua_group, ming_gua, youxing_stars
from engine.bazi import TRUE_SOLAR, build_chart
from engine.careers import career_paths
from engine.domains import life_domains
from engine.extras import harmony_matrix
from engine.htmlreport import _tosimp
from engine.liunian import dayun_detail
from engine.optimizer import optimize, score_assignment
from engine.sectors import assign_pie
from engine.shensha import life_palaces
from engine.windows import timing_windows
from engine.xuankong import annual_chart, natal_chart_from_degrees
from engine.yongshen import yong_shen
from scripts.bazi_report import build_person, family_section

import os

ROOT = Path(__file__).resolve().parent
# Overridable so deploys that replace the code tree never wipe workspaces.
# On Vercel (read-only bundle) default to /tmp — ephemeral: workspaces live
# only while a lambda stays warm; durable serverless storage = Supabase later.
_DEFAULT_STORE = ("/tmp/bazifor_store" if os.environ.get("VERCEL")
                  else ROOT / "data/public_store")
STORE = Path(os.environ.get("BAZIFORME_STORE", _DEFAULT_STORE))
UPLOADS = STORE / "uploads"
YEAR = 2026
MAX_PEOPLE = 8
TTL_SECONDS = 183 * 24 * 3600          # ~6 months
MAX_UPLOAD = 8 * 1024 * 1024           # 8 MB floorplan cap

router = APIRouter()


# ---------------------------------------------------------------- store
# Durable serverless store: Upstash Redis over REST (Vercel marketplace sets
# these envs). Without it, Vercel workspaces die with each lambda instance.
_REDIS_URL = (os.environ.get("KV_REST_API_URL")
              or os.environ.get("UPSTASH_REDIS_REST_URL"))
_REDIS_TOK = (os.environ.get("KV_REST_API_TOKEN")
              or os.environ.get("UPSTASH_REDIS_REST_TOKEN"))


def _redis_cmd(*cmd: str):
    import urllib.request
    req = urllib.request.Request(
        _REDIS_URL, data=json.dumps(cmd).encode(),
        headers={"Authorization": f"Bearer {_REDIS_TOK}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=6) as r:
        return json.loads(r.read())["result"]


def _db() -> sqlite3.Connection:
    STORE.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(STORE / "workspaces.db")
    con.execute("CREATE TABLE IF NOT EXISTS ws "
                "(token TEXT PRIMARY KEY, created REAL, payload TEXT)")
    return con


def _load(token: str) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_-]{8,64}", token or ""):
        raise HTTPException(404, "unknown workspace")
    if _REDIS_URL:
        raw = _redis_cmd("GET", f"ws:{token}")
        if not raw:
            raise HTTPException(404, "unknown or expired workspace")
        return json.loads(raw)
    with _db() as con:
        row = con.execute("SELECT created, payload FROM ws WHERE token=?",
                          (token,)).fetchone()
    if not row or time.time() - row[0] > TTL_SECONDS:
        raise HTTPException(404, "unknown or expired workspace")
    return json.loads(row[1])


def _save(token: str, ws: dict) -> None:
    if _REDIS_URL:
        _redis_cmd("SET", f"ws:{token}", json.dumps(ws, ensure_ascii=False),
                   "EX", str(TTL_SECONDS))   # every save renews the 6 months
        return
    with _db() as con:
        con.execute("INSERT INTO ws(token, created, payload) VALUES(?,?,?) "
                    "ON CONFLICT(token) DO UPDATE SET payload=excluded.payload",
                    (token, time.time(), json.dumps(ws, ensure_ascii=False)))


# ---------------------------------------------------------------- people
class PersonIn(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    sex: str = Field(pattern="^[MF]$")
    dob: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    birth_time: str = Field(default="12:00", pattern=r"^\d{2}:\d{2}$")
    time_known: bool = True


def _member(p: dict) -> SimpleNamespace:
    try:
        dt = datetime.strptime(f'{p["dob"]} {p.get("birth_time") or "12:00"}',
                               "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(400, "invalid date or time")
    if not 1900 <= dt.year <= datetime.now().year + 1:
        raise HTTPException(400, "year out of supported range (1900–next year)")
    return SimpleNamespace(name=p["name"].strip(), sex=p["sex"], birth_dt=dt)


def _chart_of(p: dict):
    m = _member(p)
    return m, build_chart(m.name, m.sex, m.birth_dt, TRUE_SOLAR)


def _summary(p: dict) -> dict:
    """Compact card payload for the workspace page."""
    m, c = _chart_of(p)
    ys = yong_shen(c)
    lp = life_palaces(c)
    doms = {d["key"]: d["score"] for d in life_domains(c, ys)}
    return {
        "name": _tosimp(m.name), "sex": m.sex, "dob": p["dob"],
        "birth_time": p.get("birth_time", "12:00"),
        "time_known": p.get("time_known", True),
        "pillars": {k: str(v) for k, v in c.pillars.items()},
        "day_master": c.day_master,
        "strength": c.strength["verdict"],
        "gua": ming_gua(c.lichun_year, c.sex),
        "group": gua_group(ming_gua(c.lichun_year, c.sex)),
        "life_star": lp["life_star_zh"], "animal": lp["animal"],
        "favourable": ys["favourable"], "unfavourable": ys["unfavourable"],
        "top_careers": [a["en"] for a in career_paths(c, ys)["top"][:3]],
        "domains": doms,
    }


def _ws_payload(token: str, ws: dict) -> dict:
    people = [_summary(p) for p in ws["people"]]
    harmony = None
    if len(ws["people"]) >= 2:
        charts, ys_map = {}, {}
        for p in ws["people"]:
            m, c = _chart_of(p)
            charts[m.name], ys_map[m.name] = c, yong_shen(c)
        hm = harmony_matrix(charts, ys_map)
        hm["names"] = [_tosimp(n) for n in hm["names"]]
        for pair in hm["pairs"]:
            pair["a"], pair["b"] = _tosimp(pair["a"]), _tosimp(pair["b"])
            pair["band"] = _tosimp(pair["band"])
            pair["chips"] = [_tosimp(x) for x in pair["chips"]]
        harmony = hm
    return {"token": token, "people": people, "harmony": harmony,
            "max_people": MAX_PEOPLE, "has_floorplan": bool(ws.get("floorplan"))}


@router.post("/api/pub/workspace")
def create_workspace(person: PersonIn):
    _member(person.model_dump())        # validate before storing
    # 8 chars ≈ 2.8e14 combos — short enough to read out, far beyond
    # enumeration; 5 chars would be brute-forceable and this IS the login.
    token = secrets.token_urlsafe(6)
    ws = {"people": [person.model_dump()]}
    _save(token, ws)
    return _ws_payload(token, ws)


@router.get("/api/pub/w/{token}")
def get_workspace(token: str):
    return _ws_payload(token, _load(token))


@router.post("/api/pub/w/{token}/person")
def add_person(token: str, person: PersonIn):
    ws = _load(token)
    if len(ws["people"]) >= MAX_PEOPLE:
        raise HTTPException(400, f"workspace holds at most {MAX_PEOPLE} people")
    _member(person.model_dump())
    ws["people"].append(person.model_dump())
    _save(token, ws)
    return _ws_payload(token, ws)


@router.delete("/api/pub/w/{token}/person/{idx}")
def remove_person(token: str, idx: int):
    ws = _load(token)
    if not 0 <= idx < len(ws["people"]):
        raise HTTPException(404, "no such person")
    ws["people"].pop(idx)
    _save(token, ws)
    return _ws_payload(token, ws)


@router.get("/api/pub/w/{token}/person/{idx}/chart")
def person_chart(token: str, idx: int, year: int = YEAR):
    """Full Reading 命书 payload (13 sections) for a workspace person —
    identical shape to the family /api/chart route."""
    from engine.report import chart_payload
    ws = _load(token)
    if not 0 <= idx < len(ws["people"]):
        raise HTTPException(404, "no such person")
    m, c = _chart_of(ws["people"][idx])
    return chart_payload(_tosimp(m.name), c, yong_shen(c), year)


@router.get("/w/{token}/person/{idx}/reading")
def person_reading_page(token: str, idx: int):
    ws = _load(token)
    if not 0 <= idx < len(ws["people"]):
        raise HTTPException(404, "no such person")
    return FileResponse(ROOT / "web/reading.html")


@router.get("/w/{token}/person/{idx}/report")
def person_report(token: str, idx: int):
    """The full strategy report — same composition the family reports use."""
    ws = _load(token)
    if not 0 <= idx < len(ws["people"]):
        raise HTTPException(404, "no such person")
    members, charts, ys_map = [], {}, {}
    for p in ws["people"]:
        m, c = _chart_of(p)
        members.append(m)
        charts[m.name], ys_map[m.name] = c, yong_shen(c)
    fam = (family_section(members, charts, ys_map)
           if len(members) >= 2 else "")
    others = [(_tosimp(m.name),
               max(charts[m.name].element_weights,
                   key=charts[m.name].element_weights.get)) for m in members]
    m = members[idx]
    html = build_person(m, charts[m.name], ys_map[m.name], fam, others)
    return HTMLResponse(html)


# ---------------------------------------------------------------- fengshui
class RoomIn(BaseModel):
    id: str = Field(min_length=1, max_length=24, pattern=r"^[A-Za-z0-9_-]+$")
    label: str = Field(min_length=1, max_length=40)
    sleeping: bool = False
    capacity: int = Field(default=2, ge=0, le=8)
    poly: list[list[float]] = Field(min_length=3, max_length=12)


class AnalyzeIn(BaseModel):
    facing_deg: float = Field(ge=0, lt=360)
    image_up_bearing: float | None = None   # default: image top = facing
    period: int = Field(default=9, ge=1, le=9)
    rooms: list[RoomIn] = Field(min_length=1, max_length=24)
    assignment: dict[str, list[str]] = {}


@router.post("/api/pub/w/{token}/floorplan")
async def upload_floorplan(token: str, file: UploadFile = File(...)):
    ws = _load(token)
    data = await file.read()
    if len(data) > MAX_UPLOAD:
        raise HTTPException(400, "floorplan too large (max 8 MB)")
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(400, "please upload an image (jpg/png)")
    UPLOADS.mkdir(parents=True, exist_ok=True)
    (UPLOADS / f"{token}.img").write_bytes(data)
    ws["floorplan"] = True
    _save(token, ws)
    return {"url": f"/api/pub/w/{token}/floorplan"}


@router.get("/api/pub/w/{token}/floorplan")
def get_floorplan(token: str):
    _load(token)
    f = UPLOADS / f"{token}.img"
    if not f.exists():
        raise HTTPException(404, "no floorplan uploaded")
    return FileResponse(f)


_PALACE_DIR = {"坎": "N", "艮": "NE", "震": "E", "巽": "SE",
               "離": "S", "坤": "SW", "兌": "W", "乾": "NW"}
_GOOD_STARS = ("生氣", "天醫", "延年", "伏位")


def _sector_trigram(deg: float) -> str:
    names = ["坎", "艮", "震", "巽", "離", "坤", "兌", "乾"]
    return names[int(((deg + 22.5) % 360) // 45)]


def _people_analysis(req, charts: dict, ys_map: dict, rooms: list[dict],
                     rooms_by_id: dict, natal: dict, annual: dict) -> dict:
    """The per-person deliverable: house compatibility, bed/desk directions,
    best/worst rooms, and the optimal whole-household assignment."""
    house_gua = _sector_trigram((req.facing_deg + 180) % 360)
    house_group = gua_group(house_gua)
    sleeping = [r for r in rooms if r["sleeping"]]
    people = []
    for name, c in charts.items():
        g = ming_gua(c.lichun_year, c.sex)
        grp = gua_group(g)
        yx = youxing_stars(g)
        dirs = [{"palace": p, "dir": _PALACE_DIR[p], "star": s}
                for p, s in yx.items() if p in _PALACE_DIR]
        dirs.sort(key=lambda d: -STAR_SCORE.get(d["star"], 0))
        ranking = []
        for r in sleeping:
            sc = score_assignment({r["id"]: [name]}, {name: c},
                                  {name: ys_map[name]}, rooms_by_id,
                                  natal, annual)
            s0 = sc["scores"][0]
            top = sorted(s0["breakdown"], key=lambda b: -abs(b["contribution"]))
            ranking.append({"id": r["id"], "label": r["label"],
                            "total": s0["total"],
                            "why": [f'{b["explanation"]} '
                                    f'({b["contribution"]:+.2f})'
                                    for b in top[:2]]})
        ranking.sort(key=lambda x: -x["total"])
        people.append({"name": name, "gua": g, "group": grp,
                       "match": grp == house_group,
                       "dirs_good": [d for d in dirs if d["star"] in _GOOD_STARS],
                       "dirs_bad": [d for d in dirs
                                    if d["star"] not in _GOOD_STARS][::-1],
                       "rooms": ranking})
    suggestion = None
    # optimize() enumerates rooms^people — only run when the space is small
    if sleeping and charts and len(sleeping) ** len(charts) <= 100_000:
        try:
            best = optimize(charts, ys_map, rooms, natal, annual, top=1)["best"][0]
            suggestion = {
                "assignment": {rooms_by_id[rid]["label"]: ns
                               for rid, ns in best["assignment"].items()},
                "household_total": best["household_total"]}
        except (ValueError, KeyError):
            pass                    # capacity infeasible → no suggestion
    return {"house": {"sitting_gua": house_gua, "dir": _PALACE_DIR[house_gua],
                      "group": house_group},
            "people": people, "suggestion": suggestion}


def _chart_block(ch: dict, rooms: list[dict], annual: dict) -> dict:
    pal_stars = {p: {"mountain": v["mountain"], "water": v["water"],
                     "annual": annual[p]}
                 for p, v in ch["palaces"].items()}
    return {"structure": ch["structure"], "chart_type": ch.get("chart_type"),
            "facing": ch["facing"], "sitting": ch["sitting"],
            "palaces": pal_stars,
            "rooms": {r["id"]: r["palace_pie"] for r in rooms}}


@router.post("/api/pub/w/{token}/analyze")
def analyze(token: str, req: AnalyzeIn):
    ws = _load(token)
    upb = req.image_up_bearing if req.image_up_bearing is not None else req.facing_deg
    rooms = [r.model_dump() for r in req.rooms]
    if len({r["id"] for r in rooms}) != len(rooms):
        raise HTTPException(400, "duplicate room ids")
    pie = assign_pie(rooms, upb)
    for r in rooms:
        r["palace_pie"] = pie[r["id"]]
    rooms_by_id = {r["id"]: r for r in rooms}
    known = {_tosimp(p["name"]): p for p in ws["people"]}
    assignment: dict[str, list[str]] = {}
    for rid, names in req.assignment.items():
        if rid not in rooms_by_id:
            raise HTTPException(400, f"unknown room {rid}")
        for n in names:
            if _tosimp(n) not in known:
                raise HTTPException(400, f"unknown person {n}")
        assignment[rid] = names
    charts, ys_map = {}, {}
    for p in ws["people"]:
        m, c = _chart_of(p)
        charts[_tosimp(m.name)], ys_map[_tosimp(m.name)] = c, yong_shen(c)
    natal = natal_chart_from_degrees(req.period, req.facing_deg)
    annual = annual_chart(YEAR)
    result = {"year": YEAR, "period": req.period,
              "boundary": natal.get("boundary"),
              "main": _chart_block(natal, rooms, annual)}
    result.update(_people_analysis(req, charts, ys_map, rooms, rooms_by_id,
                                   natal, annual))
    if assignment:
        sc = score_assignment(assignment, charts, ys_map, rooms_by_id,
                              natal, annual)
        result["scores"] = sc
    if natal.get("alternate"):
        alt = natal["alternate"]
        result["alternate"] = _chart_block(alt, rooms, annual)
        if assignment:
            result["alternate_scores"] = score_assignment(
                assignment, charts, ys_map, rooms_by_id, alt, annual)
    ws["home"] = {"facing_deg": req.facing_deg, "image_up_bearing": upb,
                  "period": req.period, "rooms": rooms,
                  "assignment": assignment}
    _save(token, ws)
    return result


# ---------------------------------------------------------------- baby
RADICAL_ELEMENTS = {
    "水": "氵 (海 涛 沐) · 冫 (冰 凝) · 雨 (霖 霈) · 水 (泉 淼)",
    "木": "木 (林 森 楷) · 艹 (芳 苗 若) · 竹 (筠 简) · 禾 (秀 穗)",
    "火": "火 (炎 烨 灿) · 日 (晖 明 晓) · 灬 (熙 然 煦) · 心 (思 慧)",
    "土": "土 (坤 培 均) · 山 (峰 岚 岳) · 石 (磊 硕) · 田 (畴 畅)",
    "金": "金 (鑫 铭 钧) · 钅 (锐 锦) · 玉/王 (琪 瑜 珊) · 白 (皓 皎)",
}


@router.post("/api/pub/baby", response_class=HTMLResponse)
def baby(name: str = Form("宝宝"), sex: str = Form(...), dob: str = Form(...),
         birth_time: str = Form("12:00"), surname: str = Form("")):
    if sex not in ("M", "F"):
        raise HTTPException(400, "sex must be M or F")
    p = {"name": name or "宝宝", "sex": sex, "dob": dob,
         "birth_time": birth_time}
    m, c = _chart_of(p)
    ys = yong_shen(c)
    lp = life_palaces(c)
    total = sum(c.element_weights.values()) or 1
    bars = "".join(
        f'<div class="eb"><span>{el}</span>'
        f'<div class="et"><div style="width:{w / total * 100:.0f}%"></div></div>'
        f'<span>{w / total * 100:.0f}%</span></div>'
        for el, w in c.element_weights.items())
    fav = ys["favourable"]
    rad = "".join(f'<div class="cite"><b>{el}</b> — {RADICAL_ELEMENTS[el]}</div>'
                  for el in fav)
    naming_html = ""
    if surname.strip():
        from engine.naming import suggest_names
        try:
            sug = suggest_names(ys, surname.strip(), top=12)
            from urllib.parse import urlencode

            def cert_url(given):
                return "/api/pub/certificate?" + urlencode(
                    {"surname": surname.strip(), "given": given, "sex": sex,
                     "dob": dob, "birth_time": birth_time})
            rows = "".join(f"""<div class="cand{' ct' if r['contested'] else ''}">
              <b class="nm">{_tosimp(r['name'])}</b>
              <span class="py">{' '.join(c.get('py') or '' for c in r['chars'])}</span>
              <span class="sc">score {r['score']} ·
                <a href="{cert_url(r['given'])}" target="_blank">命名證書 →</a></span>
              {''.join(f'<div class="cite">· {_tosimp(x)}</div>' for x in r['reasons'])}
            </div>""" for r in sug["candidates"])
            if name and name != "宝宝":
                rows = (f'<div class="cite" style="margin-bottom:6px">Your own '
                        f'choice: <a href="{cert_url(name)}" target="_blank">'
                        f'certificate for {_tosimp(surname + name)} →</a></div>'
                        + rows)
            naming_html = f"""<div class="sec"><h2>Ranked name candidates 候选名
              <small style="color:#8a8177;font-weight:400">姓 {_tosimp(surname)}
              ({'+'.join(map(str, sug['surname_ks']))}画 康熙) · pool
              {sug['pool_size']} chars · v1</small></h2>{rows}
              <div class="cite" style="margin-top:6px">{sug['source_ref']}.
              ⚑ marks characters whose element is disputed between dictionary
              schools — both readings shown. These are candidates for YOUR
              choice, not a verdict.</div></div>"""
        except ValueError as e:
            naming_html = f'<div class="sec cite">naming: {e}</div>'
    dy = "".join(f'<div class="dy"><div>{d["ages"]}</div><b>{d["gz"]}</b></div>'
                 for d in dayun_detail(c, YEAR)[:6])
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Baby BaZi 宝宝八字</title><style>
body{{font-family:system-ui,'Noto Sans SC',sans-serif;max-width:720px;margin:24px auto;
  padding:0 16px;color:#222;background:#faf7f2}}
h1{{font-size:20px;color:#b03a2e}}h2{{font-size:15px;color:#8a6d1f;margin:18px 0 6px}}
.sec{{background:#fff;border:1px solid #e5ded2;border-radius:10px;padding:12px 16px;margin:10px 0}}
.pz{{display:inline-block;border:1px solid #ecd9cf;border-radius:10px;padding:8px 14px;
  margin:3px;font-size:24px;font-weight:700;color:#b03a2e;background:#fff}}
.pz small{{display:block;font-size:10px;color:#999;font-weight:400}}
.cite{{color:#666;font-size:13px;margin:3px 0}}
.eb{{display:flex;align-items:center;gap:8px;font-size:12.5px;margin:2px 0}}
.eb span{{width:34px;color:#666}}.et{{flex:1;background:#f0ece4;border-radius:6px;height:11px}}
.et div{{height:100%;border-radius:6px;background:#b8860b}}
.dy{{display:inline-block;border:1px solid #ddd;border-radius:8px;padding:3px 8px;margin:2px;
  font-size:11px;color:#777;text-align:center}}.dy b{{display:block;font-size:15px;color:#222}}
.note{{border-left:4px solid #b03a2e;background:#fff;padding:8px 12px;font-size:12.5px;margin:12px 0}}
.cand{{border:1px solid #e5ded2;border-radius:8px;padding:7px 11px;margin:6px 0}}
.cand.ct{{border-color:#eedc9a;background:#fffdf5}}
.cand .nm{{font-size:19px;color:#b03a2e}}
.cand .py{{color:#8a8177;font-size:12px;margin-left:6px}}
.cand .sc{{float:right;color:#b8860b;font-size:12px}}
a{{color:#b03a2e}}</style></head><body>
<h1>👶 {_tosimp(surname + (name or "宝宝"))} — Baby BaZi 宝宝八字</h1>
<div class="cite">born {dob} {birth_time} (Singapore time assumed; true-solar applied)</div>
<div class="sec"><h2>Four Pillars 四柱</h2>
{"".join(f'<span class="pz">{c.pillars[k]}<small>{lab}</small></span>'
         for k, lab in (("year", "年"), ("month", "月"), ("day", "日"), ("hour", "時")))}
<div class="cite">Day Master 日主 <b>{c.day_master}</b> · {c.strength["verdict"]} ·
生肖 {lp["animal"]} · 命卦 {ming_gua(c.lichun_year, c.sex)} · 命星 {lp["life_star_zh"]}
· 命宮 {lp["ming_gong"]} · 胎元 {lp["tai_yuan"]}</div></div>
<div class="sec"><h2>Element balance 五行</h2>{bars}
<div class="cite"><b>用神 favourable elements: {"·".join(fav)}</b> — avoid
{"·".join(ys["unfavourable"])}. Derived by 扶抑法 with 調候 cross-check; the
naming direction below follows directly from this.</div></div>
<div class="sec"><h2>Naming direction 起名方向</h2>
<div class="cite">Characters whose radicals carry the baby's favourable elements
supplement the chart (部首五行 convention). Good radical families:</div>
{rad}
{'' if surname.strip() else '<div class="cite" style="margin-top:6px">Enter the family surname 姓 to get ranked name candidates with full 三才五格 working.</div>'}</div>
{naming_html}
<div class="sec"><h2>First luck cycles 大運</h2>{dy}
<div class="cite">The decade pillars begin from the month pillar; detailed phase
labels and exam-year overlays are in the full report (add this child on the
<a href="/start">workspace page</a>).</div></div>
<div class="note">Deterministic rule engine — no AI at runtime, every output
traces to a classical rule. Tendencies and timing, not fate. Birth data is not
stored by this page.</div>
</body></html>"""
    return HTMLResponse(html)


# ---------------------------------------------------------------- certificate
@router.get("/api/pub/certificate", response_class=HTMLResponse)
def certificate(surname: str, given: str, sex: str, dob: str,
                birth_time: str = "12:00"):
    """命名證書 — certificate-grade printable for one chosen name.

    Stateless: recomputes the full working from birth data + the name.
    Two audiences by design: formal presentation for the family elders,
    cited working for the skeptical parent."""
    from engine.naming import char_info, five_grids, sancai
    from engine.shensha import life_palaces as _lp
    if sex not in ("M", "F"):
        raise HTTPException(400, "sex must be M or F")
    if not (1 <= len(surname) <= 2 and 1 <= len(given) <= 2):
        raise HTTPException(400, "surname 1-2 chars, given name 1-2 chars")
    infos = []
    for ch in surname + given:
        e = char_info(ch)
        if not e:
            raise HTTPException(400, f"character {ch} not in the dataset")
        infos.append((ch, e))
    m, c = _chart_of({"name": given, "sex": sex, "dob": dob,
                      "birth_time": birth_time})
    ys = yong_shen(c)
    lp = _lp(c)
    s_ks = [e["ks"] for ch, e in infos[:len(surname)]]
    g_infos = infos[len(surname):]
    grids = five_grids(s_ks, [e["ks"] for _, e in g_infos])
    sc = sancai(grids)
    fav = ys["favourable"]
    full = surname + given
    trad = "".join(e.get("trad") or ch for ch, e in infos)
    pillars = "".join(
        f'<div class="pil"><b>{c.pillars[k]}</b><span>{lab}</span></div>'
        for k, lab in (("year", "年柱"), ("month", "月柱"),
                       ("day", "日柱"), ("hour", "時柱")))
    charrows = "".join(f"""<tr><td class="bigch">{ch}</td>
        <td>{e.get('py') or ''}</td><td>{e['ks']} 畫 (康熙)</td>
        <td>五行屬 <b>{e['el'] or '—'}</b></td>
        <td class="sm">{'契合用神 ✓' if e['el'] in fav else '姓氏' if ch in surname else ''}</td></tr>"""
        for ch, e in infos)
    gridcells = "".join(
        f'<div class="gr"><span>{k}</span><b>{v["num"]}</b>'
        f'<em class="{"ji" if v["luck"] == "吉" else "pg"}">{v["luck"]}</em></div>'
        for k, v in grids.items())
    contested = [(ch, e) for ch, e in g_infos if e.get("el_contested")]
    footnote = ("" if not contested else
                "註：" + "；".join(f"「{ch}」五行本典判屬{e['el']}，他派或作"
                                 f"{e.get('el_alt', '別解')}"
                                 for ch, e in contested) + "。")
    from datetime import date
    today = date.today().strftime("%Y年%m月%d日")
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>命名證書 · {full}</title><style>
@page{{size:A4;margin:14mm}}
body{{font-family:"Songti SC","Noto Serif SC","SimSun",serif;background:#f4efe6;
  color:#2b2620;margin:0;display:flex;justify-content:center;padding:24px 8px}}
.cert{{background:#fffdf7;width:min(760px,100%);border:3px double #9e2b25;
  outline:1px solid #c8a959;outline-offset:-10px;padding:46px 52px;position:relative}}
h1{{text-align:center;font-size:34px;letter-spacing:14px;color:#9e2b25;
  margin:0 0 2px;font-weight:600}}
.sub{{text-align:center;color:#8a7a5a;font-size:12px;letter-spacing:3px;
  margin-bottom:26px}}
.name{{text-align:center;font-size:64px;letter-spacing:12px;color:#1c1712;
  margin:10px 0 0;font-weight:700}}
.trad{{text-align:center;color:#8a7a5a;font-size:15px;letter-spacing:6px}}
.line{{border:0;border-top:1px solid #c8a959;margin:24px 10%}}
h2{{font-size:15px;color:#9e2b25;letter-spacing:4px;margin:20px 0 8px;
  text-align:center}}
.pils{{display:flex;justify-content:center;gap:14px}}
.pil{{border:1px solid #c8a959;padding:8px 14px;text-align:center;background:#fff}}
.pil b{{font-size:22px;display:block}}
.pil span{{font-size:10px;color:#8a7a5a;letter-spacing:2px}}
.meta{{text-align:center;font-size:13px;color:#4d463c;margin:10px 0;line-height:1.9}}
table{{margin:0 auto;border-collapse:collapse;font-size:13px}}
td{{border:1px solid #e0d3b8;padding:5px 12px;text-align:center}}
.bigch{{font-size:26px;font-weight:700}}
.sm{{font-size:11px;color:#9e2b25}}
.grs{{display:flex;justify-content:center;gap:10px;margin:8px 0}}
.gr{{border:1px solid #e0d3b8;background:#fff;padding:6px 12px;text-align:center}}
.gr span{{display:block;font-size:10px;color:#8a7a5a}}
.gr b{{font-size:20px}}
.gr em{{display:block;font-style:normal;font-size:11px}}
.ji{{color:#1e7d32}}.pg{{color:#8a7a5a}}
.sancai{{text-align:center;font-size:13.5px;color:#4d463c}}
.foot{{margin-top:26px;text-align:center;font-size:11px;color:#8a7a5a;
  line-height:1.8}}
.stamp{{position:absolute;right:44px;bottom:60px;width:74px;height:74px;
  border:3px solid #b03a2e;color:#b03a2e;display:flex;align-items:center;
  justify-content:center;font-size:20px;letter-spacing:2px;
  transform:rotate(-8deg);opacity:.85;font-weight:700}}
.noprint{{text-align:center;margin:14px}}
.noprint button{{background:#9e2b25;color:#fff;border:0;border-radius:8px;
  padding:9px 22px;font-size:14px;cursor:pointer}}
@media print{{body{{background:#fff;padding:0}}.noprint{{display:none}}
  .cert{{border-width:3px;width:100%}}}}
</style></head><body><div>
<div class="cert">
  <h1>命名證書</h1>
  <div class="sub">CERTIFICATE OF NAMING · 依古法推演 · 條條有據</div>
  <div class="name">{_tosimp(full)}</div>
  {f'<div class="trad">繁體 {trad}</div>' if trad != full else ''}
  <div class="meta">{'男' if sex == 'M' else '女'}嬰 · 生於 {dob} {birth_time}
    （新加坡時間，經真太陽時校正）<br>
    生肖屬{lp['animal']} · 日主 <b>{c.day_master}</b> · {c.strength['verdict'].split(' ')[0]}
    · 喜用神 <b>{'、'.join(fav)}</b></div>
  <hr class="line">
  <h2>八 字 四 柱</h2>
  <div class="pils">{pillars}</div>
  <h2>名 字 五 行</h2>
  <table>{charrows}</table>
  <h2>三 才 五 格</h2>
  <div class="grs">{gridcells}</div>
  <div class="sancai">三才 {'·'.join(sc['elements'])} —
    {sc['explanation']} · 評 <b class="{'ji' if sc['verdict'] == '吉' else 'pg'}">{sc['verdict']}</b></div>
  <hr class="line">
  <div class="foot">
    依據：喜用神扶抑法 · 康熙字典筆畫 · 八十一數理 · 五行生剋<br>
    {footnote}{'<br>' if footnote else ''}
    立於 {today} · bazifor.me · 名由家定，理由典出
  </div>
  <div class="stamp">名正<br>言順</div>
</div>
<div class="noprint"><button onclick="window.print()">🖨 列印 / 存為 PDF</button></div>
</div></body></html>"""
    return HTMLResponse(html)


# ---------------------------------------------------------------- pages
@router.get("/start")
def start_page():
    return FileResponse(ROOT / "web/start.html")


@router.get("/w/{token}")
def workspace_page(token: str):
    _load(token)
    return FileResponse(ROOT / "web/start.html")


@router.get("/fengshui")
def fengshui_page():
    return FileResponse(ROOT / "web/fs_analyze.html")


@router.get("/w/{token}/fengshui")
def fengshui_ws_page(token: str):
    _load(token)
    return FileResponse(ROOT / "web/fs_analyze.html")


@router.get("/baby")
def baby_page():
    return FileResponse(ROOT / "web/baby.html")
