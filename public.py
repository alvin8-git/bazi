"""bazifor.me public surfaces — stateless, workspace-token based.

Three surfaces, none touching the single-family global config:
  /start    — enter your own birth data, add up to 8 people, harmony matrix,
              full per-person strategy reports
  /fengshui — upload a floorplan, give the facing, draw rooms, assign people,
              get the flying-star chart + per-person room scores (cited)
  /baby     — newborn/expected-baby chart with 用神-based naming direction

Storage: one SQLite row per workspace token (nanoid-style, unguessable),
6-month TTL, uploads under data/public_store/. No accounts, no payments —
the validation-first architecture from docs/designs/bazifor-me-wedge.md.
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

from engine.bazhai import gua_group, ming_gua
from engine.bazi import TRUE_SOLAR, build_chart
from engine.careers import career_paths
from engine.domains import life_domains
from engine.extras import harmony_matrix
from engine.htmlreport import _tosimp
from engine.liunian import dayun_detail
from engine.optimizer import score_assignment
from engine.sectors import assign_pie
from engine.shensha import life_palaces
from engine.windows import timing_windows
from engine.xuankong import annual_chart, natal_chart_from_degrees
from engine.yongshen import yong_shen
from scripts.bazi_report import build_person, family_section

ROOT = Path(__file__).resolve().parent
STORE = ROOT / "data/public_store"
UPLOADS = STORE / "uploads"
YEAR = 2026
MAX_PEOPLE = 8
TTL_SECONDS = 183 * 24 * 3600          # ~6 months
MAX_UPLOAD = 8 * 1024 * 1024           # 8 MB floorplan cap

router = APIRouter()


# ---------------------------------------------------------------- store
def _db() -> sqlite3.Connection:
    STORE.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(STORE / "workspaces.db")
    con.execute("CREATE TABLE IF NOT EXISTS ws "
                "(token TEXT PRIMARY KEY, created REAL, payload TEXT)")
    return con


def _load(token: str) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_-]{16,64}", token or ""):
        raise HTTPException(404, "unknown workspace")
    with _db() as con:
        row = con.execute("SELECT created, payload FROM ws WHERE token=?",
                          (token,)).fetchone()
    if not row or time.time() - row[0] > TTL_SECONDS:
        raise HTTPException(404, "unknown or expired workspace")
    return json.loads(row[1])


def _save(token: str, ws: dict) -> None:
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
    token = secrets.token_urlsafe(18)
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
<div class="cite" style="margin-top:6px">Stroke numerology (三才五格) uses 繁體
stroke counts with the surname{f" {_tosimp(surname)}" if surname else ""} — full
ranked character candidates with cited working and a printable 命名證書 are the
next milestone of bazifor.me.</div></div>
<div class="sec"><h2>First luck cycles 大運</h2>{dy}
<div class="cite">The decade pillars begin from the month pillar; detailed phase
labels and exam-year overlays are in the full report (add this child on the
<a href="/start">workspace page</a>).</div></div>
<div class="note">Deterministic rule engine — no AI at runtime, every output
traces to a classical rule. Tendencies and timing, not fate. Birth data is not
stored by this page.</div>
</body></html>"""
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
