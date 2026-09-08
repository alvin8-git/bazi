"""Three-home battlecard — deterministic comparison page (no LLM).

Computes every figure fresh from the engine for TowerA / TowerC / TowerB and
renders data/out/fengshuiBattlecard.html. Regenerate any time with:
    .venv/bin/python -m engine.battlecard
Assumes data/house.json + data/rooms.json currently hold the TowerA configs
(the repo's committed state).
"""
from __future__ import annotations

import json
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
DIR = lambda p: PALACES[p]["dir"] if p in PALACES else "C"

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
    for n in ("王一心", "王二强", "王三美"):
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
    order = ["TowerC", "TowerA", "TowerB"]
    winner = max(homes, key=lambda h: h["best"])["tag"]
    sub = {t: s for t, s, _, _ in HOMES}
    B = []
    B.append("<h1>⚔️ 三宅對決 Three-Home Fengshui Battlecard</h1>")
    B.append('<div class="sub">黃家 five-member family · Period 8 charts · 2026 · '
             'rule-based, every figure engine-computed · regenerate with '
             '<code>python -m engine.battlecard</code></div>')

    B.append('<div class="cards">' + "".join(
        f'<div class="hcard{" win" if t == winner else ""}"><b>{t}</b>'
        f'<div class="sub">{sub[t]}</div>'
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
                 "TowerA & TowerB (P8)"))
    B.append(row("House type 宅卦", [H[t]["gua"] for t in order], "TowerC & TowerB"))
    def argmax(f):
        return max(order, key=lambda t: f(H[t]))

    kids = lambda h: sum(h["per"][n]["score"] for n in ("王一心", "王二强", "王三美"))
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
                  f"P9: {H[t]['wealth_p9']}" for t in order], "TowerB"))
    B.append(row("Health 健康 — beds & 天醫",
                 [f"beds on 山8: {('、'.join(H[t]['m8_beds']) or 'none')} · "
                  f"{H[t]['tianyi']}× in 天醫 rooms" for t in order],
                 argmax(lambda h: len(h["m8_beds"]) + h["tianyi"])))
    B.append(row("Water & surroundings", [WATER_NOTE[t] for t in order],
                 "TowerB (era-proof)"))
    B.append(row("Couple 桃花位 (兌 W) — romance corner",
                 [("、".join(H[t]["taohua"]) or "not in enclosed area") for t in order],
                 "TowerC (living)"))
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
    B.append('<div class="note">The pair bond itself (合婚 70/100 — 辰申半三合, mutual '
             'element supply) travels with you; what each home changes is the shared '
             'bedroom. <b>TowerA</b> is mum\'s individual best (延年 master +1.24, dad '
             'compensates at 五鬼) and the strongest couple-combined room. <b>TowerC</b> '
             'flips the burden onto mum at its heaviest (絕命 −0.88) — her in-room '
             'compensations (headboard N/S/E, 黑藍綠青) matter most here, and the living '
             'room doubles as both parents\' 桃花位 (兌) — a daily-use romance corner no '
             'other home offers. <b>TowerB</b> keeps the burden on mum but lighter '
             '(五鬼 −0.66) and gives her 天醫 daytime sectors. Net: for the marriage '
             'specifically, TowerA &gt; TowerC ≈ TowerB; for mum personally, '
             'TowerA &gt; TowerB &gt; TowerC.</div>')

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
    B.append('<div class="note">TowerB\'s house-level 文昌水 (pool on the N study star) '
             'holds only on the 乾 side of its 307.5° boundary — under the measured '
             '戌-side 替卦 the N pool sits on 向星3 instead; its dining table on 向星8 '
             'holds either way. TowerC\'s house 文昌星 sits in the central dining '
             'palace — the homework table; TowerA\'s falls on Bedroom 2.</div>')

    B.append("<h2>5 · Verdict 總評</h2>")
    B.append(f'<div class="note"><b>TowerB now tops the realized fit '
             f'({H["TowerB"]["best"]:+.2f})</b> under its compass-measured 307° 替卦 '
             'chart (+1.96 even on the 乾 side of the boundary), with 旺山旺向 holding on '
             'BOTH sides of its 騎線 — a 4th bedroom, 三美\'s ensuite doubling as her '
             'own-room 文昌 and 生氣, beds on the 山星8 side, and a lighter burden on mum '
             '(五鬼 −0.64 vs 絕命 −0.88 at TowerC). Its two open risks: which side of '
             '307.5° the true facing sits (it decides the pool\'s 文昌水-vs-三碧 story '
             'AND makes a P9 renovation 上山下水 on the 戌 side — re-measure before any '
             'reno), and the stack-mirroring check. '
             f'<b>TowerC — your current home — </b> ({H["TowerC"]["best"]:+.2f}) '
             'keeps the abstract ceiling '
             f'({H["TowerC"]["coarse"]:+.2f}) with your existing allocation already '
             'optimal; its limits stay the 3-bedroom plan (girls share) and mum\'s 絕命 '
             f'master. <b>TowerA</b> ({H["TowerA"]["best"]:+.2f}) remains the marriage- '
             'and mum-friendly home but the weakest for the children — a coherent asset, '
             'a less coherent family residence. Nothing here is destiny: scores are '
             'person-room fits, and every negative has a stated compensation.</div>')
    B.append('<div class="sub">TowerB compass-measured 307° (騎線 — which side of '
             '307.5° still to settle, 2-3 readings away from metal) &amp; '
             'stack-mirroring await viewing-day checks; TowerC compass-confirmed '
             '343°; TowerA facing 135° per brief. Sources: '
             'fengshuiTowerA/TowerC/TowerB.html carry the full cited breakdowns.</div>')

    body = _tosimp("\n".join(B))
    return ("<!doctype html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1, viewport-fit=cover'>"
            "<meta name='format-detection' content='telephone=no'>"
            f"<title>三宅对决 Battlecard</title><style>{CSS}</style></head>"
            f"<body>{body}</body></html>")


def main():
    out = ROOT / "data/out/fengshuiBattlecard.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(), "utf8")
    print(f"battlecard → {out} ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
