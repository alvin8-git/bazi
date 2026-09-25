"""Multi-home battlecard — deterministic comparison page (no LLM).

Computes every figure fresh from the engine for whichever homes HOMES lists
and renders fengshuiBattlecard.html. Regenerate any time with:
    .venv/bin/python -m engine.battlecard
Output goes to data/out; set FENGSHUI_OUT_DIR to file it elsewhere.

Every home on the card is read from its own house/rooms config, so nothing here
depends on which home data/house.json currently holds. The card is entirely
computed — authored narrative for a home lives in that home's own report.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from .bazi import TRUE_SOLAR, build_chart
from .bazhai import STAR_SCORE, gua_group, ming_gua, youxing_stars
from .htmlreport import _tosimp
from .import_family import load_family
from .liunian import BRANCH_PALACE, annual_afflictions
from .optimizer import optimize
from .sectors import load_rooms
from .shensha import WENCHANG
from .wuxing import PALACES, mountain_of_degrees
from .xuankong import annual_chart, natal_chart_from_degrees
from .yongshen import yong_shen
from .join import score_direction

ROOT = Path(__file__).resolve().parent.parent


def _out_dir() -> Path:
    """Output directory. Defaults to data/out; override with FENGSHUI_OUT_DIR
    (relative to the repo root) to file a report next to its own source data."""
    d = ROOT / os.environ.get("FENGSHUI_OUT_DIR", "data/out")
    d.mkdir(parents=True, exist_ok=True)
    return d

DIR = lambda p: PALACES[p]["dir"] if p in PALACES else "C"
COUPLE = ["王大明", "李小华"]
KIDS = ["王一心", "王二强", "王三美"]

# Candidate set 2026-09-17: TowerA (old home) and TowerB (sold to another
# buyer) removed; the three live candidates compare against each other.
HOMES = [
    ("TowerA", "Tower A #01-01 · sample home", "data/house.json", "data/rooms.json"),
]
# facts the engine cannot know from configs (site observations)
WATER_NOTE = {
    "TowerA": "sample site note — describe real water placement here",
}


def analyse(tag: str, hf: str, rf: str, members, charts, ys_map, year=2026):
    house = json.loads((ROOT / hf).read_text("utf8"))
    rooms = load_rooms(ROOT / rf)
    natal8 = natal_chart_from_degrees(8, house["facing_deg"])
    natal9 = natal_chart_from_degrees(9, house["facing_deg"])
    annual = annual_chart(year)
    couple = rooms.get("default_assignment", {}).get("master") or ["王大明", "李小华"]
    opt = optimize(charts, ys_map, rooms["rooms"], natal8, annual, "pie", 1.0,
                   couple, False)
    best = opt["best"][0]
    per = {}
    rid_of = {n: rid for rid, ns in best["assignment"].items() for n in ns}
    room_by_id = {r["id"]: r for r in rooms["rooms"]}
    for s in best["scores"]:
        pal = room_by_id[s["room"]]["palace_pie"]
        star = youxing_stars(ming_gua(charts[s["person"]].lichun_year,
                                      charts[s["person"]].sex))[pal]
        per[s["person"]] = {"score": s["total"], "room": s["room_label"],
                            "palace": pal, "star": star}
    couple_sum = round(sum(per[n]["score"] for n in couple), 2)
    # coarse best-sum
    coarse = 0.0
    for n, c in charts.items():
        coarse += max(score_direction(c, ys_map[n], natal8, annual, p)["total"]
                      for p in natal8["palaces"])
    # affliction exposure: sleeping rooms hit in 2026/2027
    hits = {}
    for y in (2026, 2027):
        af = annual_afflictions(y)
        bad = {af["taisui"]["palace"], af["suipo"]["palace"]} | set(af["sansha"]["palaces"])
        ann = annual_chart(y)
        bad |= {p for p, s in ann.items() if s in (2, 5)}
        hits[y] = [r["label"] for r in rooms["rooms"]
                   if r["sleeping"] and r["palace_pie"] in bad]
    # study: which home-room holds each child's personal 文昌
    study = {}
    for n in KIDS:
        wc = WENCHANG[charts[n].day_master]
        pal = BRANCH_PALACE[wc]
        in_rooms = [r["label"] for r in rooms["rooms"] if r["palace_pie"] == pal]
        study[n] = {"palace": pal, "dir": DIR(pal),
                    "rooms": in_rooms, "own_room": per[n]["palace"] == pal}
    # couple 桃花位 (year-branch trine) — both parents' is 兌 W
    taohua_rooms = [r["label"] for r in rooms["rooms"] if r["palace_pie"] == "兌"]
    # aspect metrics
    m8_beds = [r["label"] for r in rooms["rooms"] if r["sleeping"]
               and natal8["palaces"][r["palace_pie"]]["mountain"] == 8]
    w8_rooms = [r["label"] for r in rooms["rooms"]
                if natal8["palaces"][r["palace_pie"]]["water"] == 8]
    shengqi = sum(1 for v in per.values() if v["star"] == "生氣")
    tianyi = sum(1 for v in per.values() if v["star"] == "天醫")
    positive = sum(1 for v in per.values() if v["score"] > 0)
    top_n = max(per, key=lambda n: per[n]["score"])
    wealth_p9 = ("wealth star kept" if natal9["structure"] in
                 ("旺山旺向", "旺向", "雙星到向") else "wealth star weakened")
    # house gua fit
    sit_pal = natal8["sitting_palace"]
    east_house = sit_pal in {"坎", "離", "震", "巽"}
    suits = sum(1 for n, c in charts.items()
                if (ming_gua(c.lichun_year, c.sex) in {"坎", "離", "震", "巽"}) == east_house)
    return {"tag": tag, "house": house, "structure8": natal8["structure"],
            "structure9": natal9["structure"], "best": best["household_total"],
            "per": per, "couple": couple_sum, "coarse": round(coarse, 2),
            "hits": hits, "study": study, "taohua": taohua_rooms,
            "m8_beds": m8_beds, "w8_rooms": w8_rooms, "shengqi": shengqi,
            "tianyi": tianyi, "positive": positive, "top": top_n,
            "wealth_p9": wealth_p9,
            "gua": f"{sit_pal}宅 {'East' if east_house else 'West'} — suits {suits}/5"}


CSS = """
body{margin:0 auto;max-width:1080px;padding:18px;background:#faf7f2;color:#2b2620;
 font:15.5px/1.55 "Noto Sans","PingFang SC","PingFang TC",sans-serif;-webkit-text-size-adjust:100%}
h1{color:#b03a2e;font-size:24px;margin:8px 0 2px} h2{color:#b03a2e;font-size:18px;margin-top:26px}
.sub{color:#8a8177;font-size:13px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin:14px 0}
.hcard{background:#fff;border:1px solid #e5ded2;border-radius:12px;padding:14px 16px}
.hcard .big{font-size:30px;font-weight:700;color:#b8860b}
.hcard.win{border:2px solid #2e7d32}.hcard.win .big{color:#2e7d32}
table{border-collapse:collapse;background:#fff;font-size:13.5px;margin:10px 0;width:100%}
th,td{border:1px solid #e5ded2;padding:6px 9px;text-align:left;vertical-align:top}
th{background:#f6f1e8}
td.good{color:#2e7d32;font-weight:600} td.bad{color:#b03a2e}
.edge{font-weight:700;color:#b8860b;white-space:nowrap}
.tag{display:inline-block;font-size:12px;border-radius:5px;padding:1px 7px;background:#f3efe7;border:1px solid #e5ded2}
.warn{background:#fff6df;border-color:#eedc9a;color:#8a6d00}
.note{background:#fbf6ea;border:1px solid #eadfc4;border-left:4px solid #b8860b;border-radius:8px;
 padding:10px 14px;margin:10px 0;font-size:14px;color:#4d463c}
@media(max-width:720px){table{display:block;overflow-x:auto;max-width:100%;-webkit-overflow-scrolling:touch}}
"""


def build() -> str:
    members = load_family(ROOT / "data/family.json")
    charts = {m.name: build_chart(m.name, m.sex, m.birth_dt, TRUE_SOLAR) for m in members}
    ys_map = {n: yong_shen(c) for n, c in charts.items()}
    homes = [analyse(t, hf, rf, members, charts, ys_map) for t, _, hf, rf in HOMES]
    H = {h["tag"]: h for h in homes}
    order = [tag for tag, _, _, _ in HOMES]
    winner = max(homes, key=lambda h: h["best"])["tag"]
    sub = {t: s for t, s, _, _ in HOMES}
    B = []
    n_cn = "一二三四五六七八九"[len(order) - 1]
    B.append(f"<h1>⚔️ {n_cn}宅對決 {len(order)}-Home Fengshui Battlecard</h1>")
    B.append('<div class="sub">黃家 five-member family · Period 8 charts · 2026 · '
             'rule-based, every figure engine-computed · regenerate with '
             '<code>python -m engine.battlecard</code></div>')

    B.append('<div class="cards">' + "".join(
        f'<div class="hcard{" win" if t == winner else ""}"><b>{t}</b>'
        f'<div class="sub">{sub[t]}</div>'
        f'<div class="sub">facing {H[t]["house"]["facing_deg"]}° · '
        f'P{"/".join(str(x) for x in H[t]["house"].get("periods", []))} per config</div>'
        f'<div class="big">{H[t]["best"]:+.2f}</div>'
        f'<div class="sub">optimal household fit · {H[t]["structure8"]} (P8)</div></div>'
        for t in order) + "</div>")

    def row(label, cells, edge=""):
        return (f"<tr><th>{label}</th>"
                + "".join(f"<td>{c}</td>" for c in cells)
                + f'<td class="edge">{edge}</td></tr>')

    B.append("<h2>1 · The card 對決表</h2>")
    B.append("<table><tr><th>Dimension</th>"
             + "".join(f"<th>{t}</th>" for t in order) + "<th>Edge</th></tr>")
    B.append(row("Structure P8 → P9",
                 [f"{H[t]['structure8']} → {H[t]['structure9']}" for t in order],
                 "—"))
    B.append(row("House type 宅卦", [H[t]["gua"] for t in order], "—"))
    def argmax(f):
        return max(order, key=lambda t: f(H[t]))

    kids = lambda h: sum(h["per"][n]["score"] for n in KIDS)
    B.append(row("Optimal household fit",
                 [f"<b>{H[t]['best']:+.2f}</b>" for t in order],
                 argmax(lambda h: h["best"])))
    B.append(row("Family-fit ceiling (coarse, floorplan-blind)",
                 [f"{H[t]['coarse']:+.2f}" for t in order],
                 argmax(lambda h: h["coarse"])))
    B.append(row("Couple's shared master (combined)",
                 [f"{H[t]['couple']:+.2f}" for t in order],
                 argmax(lambda h: h["couple"])))
    B.append(row("Kids combined", [f"{kids(H[t]):+.2f}" for t in order],
                 argmax(kids)))
    B.append(row("Luck 運氣 — members positive",
                 [f"{H[t]['positive']}/5 · top: {H[t]['top']} "
                  f"{H[t]['per'][H[t]['top']]['score']:+.2f}" for t in order],
                 argmax(lambda h: h["positive"])))
    B.append(row("Career 事業 — vitality & activity",
                 [f"{H[t]['shengqi']}× in 生氣 rooms · 向8 zone: "
                  + ("、".join(H[t]["w8_rooms"]) or "balcony/facing (no interior room)")
                  for t in order],
                 argmax(lambda h: h["shengqi"])))
    B.append(row("Wealth 財富 — 向8 & durability",
                 [f"向8: {('、'.join(H[t]['w8_rooms']) or 'balcony/facing')} · "
                  f"P9: {H[t]['wealth_p9']}" for t in order],
                 argmax(lambda h: len(h["w8_rooms"]))))
    B.append(row("Health 健康 — beds & 天醫",
                 [f"beds on 山8: {('、'.join(H[t]['m8_beds']) or 'none')} · "
                  f"{H[t]['tianyi']}× in 天醫 rooms" for t in order],
                 argmax(lambda h: len(h["m8_beds"]) + h["tianyi"])))
    B.append(row("Water & surroundings", [WATER_NOTE[t] for t in order], "—"))
    B.append(row("Couple 桃花位 (兌 W) — romance corner",
                 [("、".join(H[t]["taohua"]) or "not in enclosed area") for t in order],
                 argmax(lambda h: len(h["taohua"]))))
    B.append(row("2026 afflicted bedrooms (no-reno zones)",
                 ["、".join(H[t]["hits"][2026]) or "none" for t in order], "—"))
    B.append(row("2027 afflicted bedrooms",
                 ["、".join(H[t]["hits"][2027]) or "none" for t in order], "—"))
    B.append("</table>")

    B.append("<h2>2 · Per-person matrix 每人每宅</h2>")
    B.append('<div class="sub">Score in each home\'s optimal arrangement · room · '
             'that sector\'s 八宅 star for the person</div>')
    B.append("<table><tr><th>Member</th>"
             + "".join(f"<th>{t}</th>" for t in order) + "</tr>")
    for m in members:
        cells = []
        for t in order:
            p = H[t]["per"][m.name]
            cls = "good" if p["score"] >= 0.5 else "bad" if p["score"] < 0 else ""
            cells.append(f'<td class="{cls}">{p["score"]:+.2f} · {p["room"]} '
                         f'({DIR(p["palace"])} {p["star"]})</td>')
        B.append(f"<tr><th>{m.name}</th>" + "".join(cells) + "</tr>")
    B.append("</table>")

    B.append("<h2>3 · Relationship 感情</h2>")
    B.append('<div class="sub">The pair bond itself travels with you; what each '
             'home changes is the shared master bedroom.</div>')
    couple_rank = sorted(order, key=lambda t_: -H[t_]["couple"])
    B.append("<table><tr><th>Home</th><th>Couple combined</th>"
             + "".join(f"<th>{n}</th>" for n in COUPLE) + "</tr>")
    for t_ in couple_rank:
        cells = "".join(
            f'<td class="{"good" if H[t_]["per"][n]["score"] >= 0.5 else "bad" if H[t_]["per"][n]["score"] < 0 else ""}">'
            f'{H[t_]["per"][n]["score"]:+.2f} · {H[t_]["per"][n]["room"]} '
            f'({DIR(H[t_]["per"][n]["palace"])} {H[t_]["per"][n]["star"]})</td>'
            for n in COUPLE)
        B.append(f'<tr><th>{t_}</th><td><b>{H[t_]["couple"]:+.2f}</b></td>{cells}</tr>')
    B.append("</table>")

    B.append("<h2>4 · Study 學業 (three students)</h2>")
    B.append("<table><tr><th>Child</th>"
             + "".join(f"<th>{t}</th>" for t in order) + "</tr>")
    for n in ("王一心", "王二强", "王三美"):
        cells = []
        for t in order:
            s = H[t]["study"][n]
            where = "、".join(s["rooms"]) or f"no room — desk faces {s['dir']}"
            own = " ✓ own bedroom!" if s["own_room"] else ""
            cells.append(f"<td>文昌 {s['dir']} {s['palace']}宮: {where}{own}</td>")
        B.append(f"<tr><th>{n}</th>" + "".join(cells) + "</tr>")
    B.append("</table>")
    own_room = {t_: [n for n in KIDS if H[t_]["study"][n]["own_room"]] for t_ in order}
    B.append('<div class="note">Own-bedroom 文昌 (study star inside the child\'s '
             'own room, the strongest placement): '
             + " · ".join(f"<b>{t_}</b> {'、'.join(own_room[t_]) or 'none'}"
                          for t_ in order) + "</div>")

    B.append("<h2>5 · Verdict 總評</h2>")
    rank = sorted(order, key=lambda t_: -H[t_]["best"])
    B.append('<div class="note"><b>' + winner + f' tops the realized fit '
             f'({H[winner]["best"]:+.2f})</b> on optimal room allocation. Full order: '
             + " &gt; ".join(f"{t_} {H[t_]['best']:+.2f}" for t_ in rank)
             + '. Scores are person-room fits under each home\'s own optimal '
               'arrangement — not destiny, and every negative has a stated '
               'compensation in that home\'s own report.</div>')
    B.append('<div class="sub">Every figure on this card is engine-computed from '
             'each home\'s house/rooms config. The authored narrative — sources, '
             'measured-bearing caveats and remedies — lives in each home\'s own '
             'report under properties/&lt;home&gt;/analysis/, and the five-home '
             'board is scripts/residences_battlecard.py.</div>')

    body = _tosimp("\n".join(B))
    n_cn = "一二三四五六七八九"[len(HOMES) - 1]
    return ("<!doctype html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1, viewport-fit=cover'>"
            "<meta name='format-detection' content='telephone=no'>"
            f"<title>{_tosimp(n_cn)}宅对决 Battlecard</title>"
            f"<style>{CSS}</style></head>"
            f"<body>{body}</body></html>")


def main():
    out = _out_dir() / "fengshuiBattlecard.html"
    out.write_text(build(), "utf8")
    print(f"battlecard → {out} ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
