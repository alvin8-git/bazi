"""Self-contained emailable HTML report — the whole analysis in one static file.

No JavaScript, floorplan embedded as base64, descriptions in 简体 with names
kept 繁體 (简体) — same conventions as the website. Deterministic: rendered
entirely from engine facts via the interpret templates.

CLI: .venv/bin/python -m engine.htmlreport [--year 2026] [--period 8]
     [--month N] [-o data/out/report.html]
Server: GET /report?year=&period=&month=
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import math
import re
from pathlib import Path

from .bazhai import STAR_SCORE, gua_group, ming_gua, youxing_stars
from .domains import health_map, industry_map, life_domains, personality_axes
from .bazi import TEN_GOD_EN
from .shensha import (TEN_GOD_MEANING, natal_interactions, pillar_extras, shensha,
                      ten_god_pct)
from .bazi import TRUE_SOLAR, build_chart
from .import_family import load_family
from .interpret import (interpret_dates, interpret_family, interpret_forecast,
                        interpret_house, interpret_housetab, interpret_names,
                        interpret_person)
from .join import score_direction
from .liunian import dayun_detail, multi_year_outlook, person_forecast
from .primer import PRIMERS
from .optimizer import score_assignment
from .sectors import load_rooms
from .wuxing import ELEMENT_EN, mountain_of_degrees
from .xuankong import annual_chart, annual_star, natal_chart_from_degrees
from .yongshen import yong_shen
from .zeri import rate_month

ROOT = Path(__file__).resolve().parent.parent

# Traditional → Simplified (same table as web/app.js)
_T2S_PAIRS = (
    "氣气醫医禍祸絕绝遊游東东調调飛飞運运節节沖冲歲岁學学體体筆笔畫画數数宮宫兌兑離离盤盘"
    "書书擇择評评時时陰阴陽阳貪贪貞贞祿禄輔辅軍军門门龍龙剋克強强對对與与為为後后應应屬属"
    "顯显凱凯優优趙赵黃黄簡简單单總总滿满執执開开閉闭關关藥药殺杀傷伤財财梟枭納纳當当進进"
    "錯错雙双靜静動动護护顏颜綠绿紅红藍蓝廚厨廁厕臥卧廳厅羅罗兩两個个這这裡里從从洩泄勢势"
    "幫帮論论據据見见訣诀經经續续變变讓让選选適适頭头帶带極极過过還还沒没內内發发間间問问"
    "題题響响環环風风師师傳传統统現现綜综標标準准側侧測测記记計计認认證证誤误說说詳详註注"
    "釋释義义儀仪報报號号業业決决")
_T2S = {_T2S_PAIRS[i]: _T2S_PAIRS[i + 1] for i in range(0, len(_T2S_PAIRS), 2)}


def _tosimp(s: str) -> str:
    return "".join(_T2S.get(c, c) for c in s)


def _simp_protect(html: str, names: list[str]) -> str:
    """Convert to 简体 but keep family names AND their individual characters
    (stroke tags) in 繁體 — used only for the Names section."""
    keep = list(names) + sorted(set("".join(names)))
    pat = re.compile("(" + "|".join(map(re.escape, keep)) + ")")
    return "".join(p if i % 2 else _tosimp(p)
                   for i, p in enumerate(pat.split(html)))


def _dn(name: str) -> str:
    # names render 简体 everywhere except the Names section (Kangxi strokes
    # are only meaningful on 繁體 forms)
    return _tosimp(name)


CSS = """
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{margin:0 auto;max-width:900px;padding:20px;background:#faf7f2;color:#2b2620;
  font:15px/1.55 "Noto Sans","PingFang SC","PingFang TC","Microsoft JhengHei",sans-serif}
@media (max-width:720px){
  body{padding:12px max(10px,env(safe-area-inset-right))
    calc(30px + env(safe-area-inset-bottom)) max(10px,env(safe-area-inset-left))}
  table{display:block;overflow-x:auto;max-width:100%;-webkit-overflow-scrolling:touch}
  .primer-grid,.domain-grid{grid-template-columns:1fr}
  svg{max-width:100%}
}
h1{color:#b03a2e;font-size:23px;margin:6px 0}
h2{color:#b03a2e;font-size:19px;border-bottom:2px solid #e5ded2;padding-bottom:4px;margin-top:28px}
h3{color:#b8860b;font-size:15.5px;margin:14px 0 6px}
h4{color:#b03a2e;font-size:14px;margin:10px 0 4px}
.sub{color:#8a8177;font-size:13px}
.warn{color:#8a6d00;background:#fff6df;border:1px solid #eedc9a;border-radius:6px;padding:6px 10px;font-size:13px}
.interp{background:#fbf6ea;border:1px solid #eadfc4;border-left:4px solid #b8860b;
  border-radius:8px;padding:8px 14px;margin:10px 0;font-size:14px;color:#4d463c}
.interp p{margin:6px 0}
table{border-collapse:collapse;margin:8px 0;background:#fff;font-size:13.5px}
th,td{border:1px solid #e5ded2;padding:4px 9px;text-align:left}
th{background:#f6f1e8}
td.good{color:#2e7d32}td.bad{color:#b03a2e}
.cite{color:#8a8177;font-size:12.5px;margin:2px 0 2px 10px}
.gz{font-size:20px;font-weight:700;color:#b03a2e;letter-spacing:3px}
.tag{display:inline-block;font-size:12px;border-radius:5px;padding:1px 7px;
  margin-right:4px;background:#f3efe7;border:1px solid #e5ded2}
.pagebreak{page-break-before:always}
.primer-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px;margin:6px 0}
.pcard{background:#fff;border:1px solid #eadfc4;border-radius:8px;padding:9px 12px}
.pcard h5{margin:0 0 4px;color:#b8860b;font-size:13px}
.pcard p{margin:0;font-size:12.5px;line-height:1.5;color:#5a5348}
"""


def _interp_block(paras: list[str]) -> str:
    return ('<div class="interp">'
            + "".join(f"<p>{p}</p>" for p in paras) + "</div>")


def _sections_block(sections: list[dict]) -> str:
    return ('<div class="interp">'
            + "".join(f"<h4>{s['heading']}</h4>"
                      + "".join(f"<p>· {l}</p>" for l in s["lines"])
                      for s in sections) + "</div>")


def _floorplan_svg(rooms_data: dict, natal: dict, annual: dict) -> str:
    iw, ih = rooms_data["image_size"]
    cx, cy = rooms_data["centroid"]
    upb = rooms_data["image_up_bearing"]
    img = base64.b64encode((ROOT / "floorplan.jpeg").read_bytes()).decode()
    R = max(iw, ih)
    parts = [f'<image href="data:image/jpeg;base64,{img}" width="{iw}" height="{ih}"/>']
    for i in range(8):
        a = math.radians(i * 45 + 22.5 - upb)
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + R * math.sin(a):.0f}" '
                     f'y2="{cy - R * math.cos(a):.0f}" stroke="rgba(184,134,11,.6)" '
                     'stroke-dasharray="4 3"/>')
    for r in rooms_data["rooms"]:
        pts = " ".join(f"{x},{y}" for x, y in r["poly"])
        rx = sum(x for x, _ in r["poly"]) / len(r["poly"])
        ry = sum(y for _, y in r["poly"]) / len(r["poly"])
        pal = r["palace_pie"]
        stars = ("中宮" if pal == "中" else
                 f"山{natal['palaces'][pal]['mountain']} 向{natal['palaces'][pal]['water']} "
                 f"年{annual[pal]}")
        fill = "rgba(176,58,46,.13)" if r["sleeping"] else "rgba(46,125,50,.10)"
        stroke = "#b03a2e" if r["sleeping"] else "#999"
        parts.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}"/>'
                     f'<text x="{rx:.0f}" y="{ry - 4:.0f}" text-anchor="middle" '
                     f'font-size="11" font-weight="600">{r["label"]}</text>'
                     f'<text x="{rx:.0f}" y="{ry + 10:.0f}" text-anchor="middle" '
                     f'font-size="10" fill="#8a8177">{pal} · {stars}</text>')
    return (f'<svg viewBox="0 0 {iw} {ih}" style="max-width:640px;width:100%">'
            + "".join(parts) + "</svg>")


def build_report(year: int, period: int, month: int | None = None,
                 policy: str = TRUE_SOLAR) -> str:
    month = month or dt.date.today().month
    members = load_family(ROOT / "data/family.json")
    house = json.loads((ROOT / "data/house.json").read_text("utf8"))
    rooms_data = load_rooms(ROOT / "data/rooms.json")
    rooms = rooms_data["rooms"]
    rooms_by_id = {r["id"]: r for r in rooms}
    current = rooms_data.get("default_assignment", {})

    charts = {m.name: build_chart(m.name, m.sex, m.birth_dt, policy) for m in members}
    ys_map = {n: yong_shen(c) for n, c in charts.items()}
    names = [m.name for m in members]
    natal = natal_chart_from_degrees(period, house["facing_deg"])
    fm = natal["facing"]
    annual = annual_chart(year)

    H = []
    today = dt.date.today().isoformat()
    H.append(f"<h1>羅盤 FengShui Family Compass — 家庭分析報告 {year}</h1>")
    H.append(f'<div class="sub">{house["name"]} — facing {house["facing_deg"]}° ({fm}向) · '
             f'Period {period} · annual centre star {annual_star(year)} · '
             f'generated {today} · time policy: {policy}</div>')
    if house.get("provisional"):
        H.append('<p class="warn">⚠ PROVISIONAL: facing degrees, period (8 vs 9) and room '
                 'tracing await the on-site compass check and renovation date.</p>')

    # 0. cards-first at-a-glance (M3 convergence: interpretation before working)
    from .aspects import ASPECTS, ASPECT_ZH, compose_family
    from .interpret import STRUCTURE_TEXT
    BAND_COL = {"strong": "#1a7f37", "good": "#2c8c7d", "fair": "#b58900",
                "weak": "#d2691e", "poor": "#b03a2e"}
    comp = compose_family(charts, ys_map, rooms, current, natal, annual, year,
                          "pie", STRUCTURE_TEXT.get(natal["structure"],
                                                    "a mixed structure"),
                          couple=current.get("master", []))
    H.append("<h2>0 · 速讀 At a glance</h2>")
    H.append('<div class="sub">Band words first: 旺 strong · 优 good · 平 fair · '
             '弱 weak · 忌 poor. The number beside each band exists only for '
             'comparison; everything is derived from the audited working in the '
             'sections below (weights: calibration, not classical truth).</div>')
    H.append("<table><tr><th></th>" + "".join(
        f"<th>{ASPECT_ZH[a]}<br>{a}</th>" for a in ASPECTS) + "</tr>")
    for n in names:
        cs = {c["aspect"]: c for c in comp["people"][n]}
        H.append(f"<tr><th>{_dn(n)}</th>" + "".join(
            f'<td style="text-align:center"><b style="color:'
            f'{BAND_COL[cs[a]["band"]]}">{cs[a]["band_zh"]}</b> '
            f'<span class="sub">{cs[a]["score"]}</span></td>'
            for a in ASPECTS) + "</tr>")
    hc = {c["aspect"]: c for c in comp["home"]}
    H.append("<tr><th>Our Home 全家</th>" + "".join(
        f'<td style="text-align:center"><b style="color:'
        f'{BAND_COL[hc[a]["band"]]}">{hc[a]["band_zh"]}</b> '
        f'<span class="sub">{hc[a]["score"]}</span></td>'
        for a in ASPECTS) + "</tr></table>")
    H.append(f'<div class="sub">Structure {hc["structure"]["band_zh"]} '
             f'{hc["structure"]["score"]} — {hc["structure"]["driver"]} · '
             f'Timing {hc["timing"]["band_zh"]} {hc["timing"]["score"]} — '
             f'{hc["timing"]["meaning"]}</div>')
    H.append("<h3>Top actions 首要行動</h3><ul>")
    for n in names:
        acts = [a for c in comp["people"][n] for a in c["actions"]]
        seen, top = set(), []
        for a in sorted(acts, key=lambda a: a["priority"]):
            if a["action"] not in seen:
                seen.add(a["action"])
                top.append(a)
            if len(top) == 2:
                break
        for a in top:
            H.append(f"<li><b>{_dn(n)}</b>: {a['action']} "
                     f'<span class="sub">↳ {a["trigger"]}</span></li>')
    H.append("</ul>")

    # 1. house verdict + full rule-based narrative
    H.append("<h2>1 · House verdict 宅運總評</h2>")
    hi = interpret_house(charts, ys_map, house, rooms, year, period,
                         current=current, master_couple=current.get("master", []))
    H.append(_sections_block(hi["sections"]))

    # 2. floorplan + 宅盤
    H.append("<h2>2 · Floorplan &amp; flying stars 宅盤</h2>")
    H.append('<div class="sub">Each room: 山 mountain star (people/health) · 向 water star '
             '(wealth) · 年 annual visiting star. Red rooms are sleeping rooms.</div>')
    H.append(_interp_block(interpret_housetab(natal, annual, year, period)["paragraphs"]))
    H.append(_floorplan_svg(rooms_data, natal, annual))
    grid = [("NW", "乾"), ("N", "坎"), ("NE", "艮"), ("W", "兌"), ("C", "中"),
            ("E", "震"), ("SW", "坤"), ("S", "離"), ("SE", "巽")]
    H.append(f"<h3>{natal['sitting']}山{natal['facing']}向 · Period {period} → "
             f"{natal['structure']}</h3><table>")
    for row in range(3):
        H.append("<tr>" + "".join(
            f'<td style="text-align:center"><span class="sub">{d} {p}</span><br>'
            f'<b style="color:#b03a2e">{natal["palaces"][p]["mountain"]}</b> '
            f'{natal["palaces"][p]["base"]} '
            f'<b style="color:#2471a3">{natal["palaces"][p]["water"]}</b><br>'
            f'<span class="sub">年 {annual[p]}</span></td>'
            for d, p in grid[row * 3:row * 3 + 3]) + "</tr>")
    H.append("</table>")

    # 3. family overview
    H.append("<h2>3 · Family overview 全家總覽</h2>")
    H.append(_interp_block(interpret_family(charts, ys_map)["paragraphs"]))
    H.append("<table><tr><th>Name</th><th></th><th>Birth</th><th>Four Pillars</th>"
             "<th>Day Master</th><th>用神</th><th>命卦</th></tr>")
    for m in members:
        c, ys = charts[m.name], ys_map[m.name]
        gua = ming_gua(c.lichun_year, c.sex)
        pil = " ".join(str(c.pillars[k]) for k in ("year", "month", "day", "hour"))
        H.append(f"<tr><td><b>{_dn(m.name)}</b></td><td>{m.sex}</td>"
                 f"<td>{m.birth_dt:%Y-%m-%d %H:%M}</td><td>{pil}</td>"
                 f"<td>{c.day_master} {c.strength['verdict']}</td>"
                 f"<td>{'·'.join(ys['favourable'])} ({'·'.join(ys['colours'])})</td>"
                 f"<td>{gua}命 {gua_group(gua)}</td></tr>")
    H.append("</table>")

    # 4. per-person readings
    H.append('<h2 class="pagebreak">4 · Individual readings 個人命書</h2>')
    for m in members:
        c, ys = charts[m.name], ys_map[m.name]
        gua = ming_gua(c.lichun_year, c.sex)
        H.append(f"<h3>{_dn(m.name)} ({m.sex}) — {m.birth_dt:%Y-%m-%d %H:%M}, "
                 f"effective {c.effective_dt:%H:%M}</h3>")
        H.append('<div class="gz">' + "　".join(str(c.pillars[k])
                 for k in ("year", "month", "day", "hour")) + "</div>")
        pe = pillar_extras(c)
        H.append('<div class="cite">納音/長生: ' + " · ".join(
            f"{pe[k]['nayin']} {pe[k]['stage']}" for k in ("year", "month", "day", "hour"))
            + f' — {c.strength["verdict"]}, support ratio {c.strength["support_ratio"]}%, '
              f'root mass {c.strength["root_ratio"]}%, {c.strength["formation"]["status"]}</div>')
        H.append(_interp_block(interpret_person(c, ys, year)["paragraphs"]))
        w = c.element_weights
        H.append("<table><tr>" + "".join(f"<th>{e} {ELEMENT_EN[e]}</th>" for e in w)
                 + "</tr><tr>" + "".join(f"<td>{v}</td>" for v in w.values())
                 + "</tr></table>")
        dd = dayun_detail(c, year)
        H.append("<table><tr>" + "".join(
            f"<th{' style=background:#fdf3ee' if d['current'] else ''}>{d['gz']}</th>" for d in dd)
            + "</tr><tr>" + "".join(f"<td>{d['ages']}</td>" for d in dd) + "</tr><tr>"
            + "".join(f"<td class='sub'>{d['stem_god']}/{d['branch_god']}</td>" for d in dd)
            + "</tr></table>")
        cur = next((d for d in dd if d["current"]), None)
        if cur:
            H.append(f'<div class="cite">current decade {cur["gz"]}: {cur["keywords"]}</div>')
        H.append('<div class="cite">personality axes: ' + "; ".join(
            f"{a['axis'].split(' ')[0]} {a['verdict']}" for a in personality_axes(c)
            if a["verdict"] != "no strong tendency") + "</div>")
        flags = [hh for hh in health_map(c) if hh["status"] != "balanced"]
        if flags:
            H.append('<div class="cite">health watch (TCM correspondence, not medical '
                     "advice): " + "; ".join(
                f"{hh['element']} {hh['status']} ({hh['share']}%) — {hh['organs']}"
                for hh in flags) + "</div>")
        H.append('<div class="cite">favourable industries: ' + "; ".join(
            f"{it['element']} — {it['industries']}"
            for it in industry_map(ys)["favourable"]) + "</div>")
        yx = youxing_stars(gua)
        H.append("<table><tr>" + "".join(f"<th>{p}</th>" for p in yx) + "</tr><tr>"
                 + "".join(f'<td class="{"good" if STAR_SCORE[s] > 0 else "bad"}">{s}</td>'
                           for s in yx.values()) + "</tr></table>")
        doms = life_domains(c, ys)
        H.append("<div>" + " ".join(
            f'<span class="tag">{d["en"]} {d["zh"]} <b>{d["score"]}</b> ({d["band"]})</span>'
            for d in doms) + "</div>")
        ss = shensha(c)
        if ss:
            H.append('<div class="cite">神煞: ' + "; ".join(
                f"{s['star']} ({'·'.join(s['pillars'])})" for s in ss) + "</div>")
        inter = natal_interactions(c)
        if inter:
            H.append('<div class="cite">natal interactions: ' + "; ".join(
                f"{i['pair']} {i['kind']}" for i in inter) + "</div>")
        pct = ten_god_pct(c)
        top = list(pct.items())[:3]
        H.append('<div class="cite">十神: ' + "; ".join(
            f"{g} {TEN_GOD_EN[g]} {p}% ({TEN_GOD_MEANING[g].split(' — ')[0]})"
            for g, p in top) + "</div>")
        # star-type reference: the vocabulary behind the life-domain evidence
        star_rows = [
            ("配偶星 Spouse star",
             "正財+偏財 — partner represented by the wealth gods" if m.sex == "M"
             else "正官+七殺 — partner represented by the authority gods",
             ("正財", "偏財") if m.sex == "M" else ("正官", "七殺")),
            ("財星 Wealth stars", "正財+偏財 — income, assets, practical results",
             ("正財", "偏財")),
            ("官殺 Authority stars", "正官+七殺 — career, status, discipline, pressure",
             ("正官", "七殺")),
            ("印 Resource stars", "正印+偏印 — learning, support, credentials",
             ("正印", "偏印")),
            ("食傷 Output stars", "食神+傷官 — expression, creativity, charm",
             ("食神", "傷官")),
            ("比劫 Peer stars", "比肩+劫財 — self-drive, siblings, competition",
             ("比肩", "劫財")),
        ]

        def _band(p):
            return ("prominent" if p >= 20 else "present" if p >= 8 else
                    "faint" if p > 0 else "absent")

        H.append("<table><tr><th>Star-type reference 星名對照</th>"
                 "<th>Which ten gods</th><th>This chart</th></tr>"
                 + "".join(
            (lambda p: f"<tr><td><b>{t}</b></td><td class='sub'>{d}</td>"
                       f"<td class='{'good' if p >= 8 else 'bad' if p == 0 else ''}'>"
                       f"{round(p, 1)}% — {_band(p)}</td></tr>")(
                sum(pct.get(g, 0) for g in gods))
            for t, d, gods in star_rows) + "</table>")
        H.append('<div class="cite">Bands: ≥20% prominent · ≥8% present · &lt;8% faint · '
                 "0% absent — the thresholds behind the life-domain evidence. 配偶宮 "
                 f"spouse palace = the day branch (here {c.pillars['day'].branch}); "
                 "財庫 wealth vault = the storage branch of the wealth element.</div>")

    # 5. room assignment with breakdowns
    H.append('<h2 class="pagebreak">5 · Room assignment 配房評分</h2>')
    res = score_assignment(current, charts, ys_map, rooms_by_id, natal, annual, "pie")
    H.append(f"<p>Current arrangement — household total <b>{res['household_total']:+.2f}</b> "
             "(see section 1 for the verdict and recommended moves).</p>")
    LAYER_ZH = {"bazhai": "八宅", "xuankong": "飛星", "yongshen": "用神", "bazi": "八字"}
    for s in res["scores"]:
        H.append(f"<h3>{_dn(s['person'])} in {s['room_label']}: {s['total']:+.2f}</h3>")
        for b in s["breakdown"]:
            H.append(f'<div class="cite">[{LAYER_ZH.get(b["layer"], b["layer"])}] '
                     f'{b["contribution"]:+.2f} — {b["explanation"]}</div>')

    # 6. annual forecasts
    H.append(f'<h2 class="pagebreak">6 · {year} forecasts 流年流月</h2>')
    room_of = {n: rooms_by_id[rid]["palace_pie"]
               for rid, ns in current.items() for n in ns}
    for m in members:
        fc = person_forecast(charts[m.name], ys_map[m.name], year,
                             room_of.get(m.name), period)
        H.append(f"<h3>{_dn(m.name)}</h3>")
        H.append(_interp_block(interpret_forecast(fc, ys_map[m.name], year)["paragraphs"]))
        H.append("<table><tr><th>月</th>"
                 + "".join(f"<td>{mo['month_branch']}</td>" for mo in fc["months"])
                 + "</tr><tr><th>room star</th>"
                 + "".join(f'<td class="{"bad" if mo.get("room_star") in (5, 2) else ""}">'
                           f'{mo.get("room_star", "—")}</td>' for mo in fc["months"])
                 + "</tr></table>")
        H.append("<table><tr><th>五年展望</th><th>verdict</th><th>interactions</th></tr>"
                 + "".join(
            f'<tr><td>{o["year"]} {o["gz"]}</td>'
            f'<td class="{"bad" if o["verdict"] == "high volatility" else "good" if o["verdict"] == "steady" else ""}">{o["verdict"]}</td>'
            f'<td class="sub">{"; ".join(o["events"] + o["support"]) or "—"}</td></tr>'
            for o in multi_year_outlook(charts[m.name], ys_map[m.name], year))
                 + "</table>")

    # 7. date selection for the report month
    H.append(f'<h2 class="pagebreak">7 · Date selection 擇日 — {year}-{month:02d}</h2>')
    mem = [{"name": m.name, "year_branch": charts[m.name].pillars["year"].branch,
            "day_branch": charts[m.name].pillars["day"].branch} for m in members]
    days = rate_month(year, month, mem)
    H.append(_interp_block(interpret_dates(days)["paragraphs"]))
    H.append("<table><tr><th>Date</th><th>日柱</th><th>建除</th><th>Score</th>"
             "<th>Person flags</th></tr>")
    for d in days:
        cls = "good" if d["score"] >= 1.5 else "bad" if d["score"] <= -1 else ""
        flags = " ".join(f'<span class="tag">{_dn(f["name"])} {f["kind"]}</span>'
                         for f in d["person_flags"])
        H.append(f"<tr><td>{d['date']}</td><td>{d['day_gz']}</td><td>{d['officer']}</td>"
                 f'<td class="{cls}">{d["score"]:+.1f}</td><td>{flags}</td></tr>')
    H.append("</table>")

    # 8. name analysis
    # Names section: the ONLY part of the report that keeps 繁體 (Kangxi strokes)
    HN = ['<h2 class="pagebreak">8 · Name analysis 姓名學</h2>']
    from .xingming import analyze_name, name_interpretation
    name_results = [analyze_name(m.name) for m in members]
    HN.append(_interp_block(interpret_names(name_results)["paragraphs"]))
    for p in name_results:
        if not p["valid"]:
            HN.append(f"<h3>{p['name']} — ⚠ invalid</h3>"
                      + "".join(f'<div class="cite">{x}</div>' for x in p["problems"]))
            continue
        strokes = " ".join(f"{c['char']}{c['kangxi_strokes']}" for c in p["chars"])
        HN.append(f"<h3>{p['name']} <span class='tag'>{strokes}</span> "
                  f"<span class='tag'>三才 {p['sancai']['elements']} "
                  f"{p['sancai']['verdict']}</span></h3>")
        HN.append("<table><tr>" + "".join(f"<th>{g}</th>" for g in p["grids"]) + "</tr><tr>"
                  + "".join(f'<td class="{"good" if v["luck"] == "吉" else "bad" if v["luck"] == "凶" else ""}">'
                            f'{v["number"]} {v["luck"]} ({v["element"]})</td>'
                            for v in p["grids"].values()) + "</tr></table>")
        HN.extend(f'<div class="cite">· {line}</div>' for line in name_interpretation(p))

    # 9. FengShui/BaZi 101 primer (mirrors the per-tab panels on the website)
    TAB_LABEL = {"family": "The family charts", "person": "Individual readings",
                 "house": "The house chart", "assign": "Room scores",
                 "forecast": "Annual forecasts", "dates": "Date selection",
                 "names": "Name analysis", "unit": "Screening a new home"}
    H9 = ['<h2 class="pagebreak">9 · FengShui/BaZi 101 — how to read this report</h2>']
    for tab, label in TAB_LABEL.items():
        pr = PRIMERS[tab]
        H9.append(f"<h3>{label} — {pr['title']}</h3><div class='primer-grid'>"
                  + "".join(f"<div class='pcard'><h5>{h}</h5><p>{t}</p></div>"
                            for h, t in pr["items"]) + "</div>")

    footer = ("\n".join(H9)
              + '<p class="sub">Rule-based · auto-generated · no AI — FengShui Family '
              'Compass. Every figure decomposes into cited classical rules; see the app '
              'for the full citation trail. Not a substitute for an on-site 通書/compass '
              'check on critical dates.</p>')

    body = (_tosimp("\n".join(H)) + _simp_protect("\n".join(HN), names)
            + _tosimp(footer))
    return ("<!doctype html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1, "
            "viewport-fit=cover'><meta name='format-detection' content='telephone=no'>"
            f"<title>FengShui report {year}</title><style>{CSS}</style></head>"
            f"<body>{body}</body></html>")


def main() -> None:
    ap = argparse.ArgumentParser(description="Emailable single-file HTML report")
    ap.add_argument("--year", type=int, default=2026)
    ap.add_argument("--period", type=int, default=8)
    ap.add_argument("--month", type=int, default=None)
    ap.add_argument("-o", "--out", default="data/out/report.html")
    a = ap.parse_args()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_report(a.year, a.period, a.month), "utf8")
    print(f"report → {out} ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
