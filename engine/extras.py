"""Report extras — per-person BaZi profiles, the house placement audit and the
family harmony matrix, as JSON for the web report (battlecard parity).

Three independent pieces:
  person_profile  — temperament axes, industry map, organ watch, 神煞 roster,
                    流年 year chips, 貴人/文昌 rooms (per person)
  house_audit     — 缺角 missing corners, entry, stove, wet rooms, 財位
                    (per active house)
  harmony_matrix  — all-pairs 合婚 scores + friction chips (house-independent)
"""
from __future__ import annotations

from .bazhai import ming_gua, youxing_stars
from .domains import health_map, industry_map, personality_axes
from .hehun import pair_compatibility
from .liunian import (BRANCH_PALACE, taisui_interactions, year_element_read,
                      year_ganzhi)
from .shensha import TIANYI, WENCHANG, shensha

PALACES8 = ["坎", "艮", "震", "巽", "離", "坤", "兌", "乾"]
ROLE_PALACE = {"乾": "father 父", "坤": "mother 母", "震": "eldest son 長男",
               "巽": "eldest daughter 長女", "坎": "middle son 中男",
               "離": "middle daughter 中女", "艮": "youngest son 少男",
               "兌": "youngest daughter 少女"}
WET_IDS = {"bath", "bath2", "bath3", "mbath", "jrbath", "wc", "yard"}
BAD_BAZHAI = {"五鬼", "絕命", "六煞", "禍害"}
BAD_TAISUI = {"值太歲", "沖太歲", "刑太歲", "害太歲"}


def _year_chip(chart, fav, y: int) -> dict:
    rels = [i["rule_id"].split("-", 1)[1] for i in taisui_interactions(chart, y)]
    rels = [r for r in rels if r != "none"]
    elem = year_element_read(chart, fav, y)["explanation"]
    good, bad = elem.count("favourable"), elem.count("unfavourable")
    bad_rel = any(r in BAD_TAISUI for r in rels)
    good_rel = any(("三合" in r or "六合" in r) for r in rels)
    cls = ("bad" if bad_rel else "good" if good_rel or good > bad
           else "watch" if bad > good else "steady")
    return {"y": y, "gz": "".join(year_ganzhi(y)), "rels": rels,
            "good": good, "bad": bad, "cls": cls}


def person_profile(chart, ys: dict, rooms: list[dict], year: int,
                   method: str = "pie") -> dict:
    """One person's battlecard profile block, house-aware only in the
    貴人/文昌 room lookups."""
    key = "palace_pie" if method == "pie" else "palace_grid"
    axes = [f'{a["axis"].split()[0]}: {a["verdict"]}'
            for a in personality_axes(chart) if "no strong" not in a["verdict"]]
    ind = industry_map(ys)
    hm = [f'{h["element"]} {h["status"]} — {h["organs"]}'
          for h in health_map(chart) if h["status"] != "balanced"]

    def rooms_in(pal):
        return [r["label"] for r in rooms if r.get(key) == pal]
    wc_pal = BRANCH_PALACE[WENCHANG[chart.day_master]]
    gr = [{"palace": p, "rooms": rooms_in(p)}
          for p in dict.fromkeys(BRANCH_PALACE[b]
                                 for b in TIANYI.get(chart.day_master, ""))]
    return {
        "gua": ming_gua(chart.lichun_year, chart.sex),
        "day_master": chart.day_master,
        "axes": axes,
        "industries": {
            "fav": [{"en": i["en"], "element": i["element"],
                     "list": i["industries"]} for i in ind["favourable"]],
            "avoid": [i["en"] for i in ind["avoid"]]},
        "health": hm,
        "shensha": list(dict.fromkeys(s["star"] for s in shensha(chart))),
        "years": [_year_chip(chart, ys["favourable"], y)
                  for y in range(year, year + 5)],
        "wenchang": {"palace": wc_pal, "rooms": rooms_in(wc_pal)},
        "guiren": gr,
    }


def house_audit(charts: dict, rooms: list[dict], natal: dict,
                annual: dict[str, int], breadwinner: str,
                method: str = "pie") -> list[dict]:
    """缺角/entry/stove/wet/財位 audit rows for the active house.
    Returns [{key, zh, text}] — text strings ready to render."""
    key = "palace_pie" if method == "pie" else "palace_grid"
    dual = "alternate" in natal
    alt = natal.get("alternate") or natal
    rooms_by_id = {r["id"]: r for r in rooms}

    covered = {r.get(key) for r in rooms}
    missing = [p for p in PALACES8 if p not in covered]
    missing_txt = (" · ".join(f"{p}宮 缺角 → weakens {ROLE_PALACE[p]}"
                              for p in missing)
                   if missing else "none — all 8 palaces hold floor area ✓")

    def stx(pal):
        a = natal["palaces"][pal]
        if not dual:
            return f'山{a["mountain"]}向{a["water"]}'
        b = alt["palaces"][pal]
        return (f'山{a["mountain"]}向{a["water"]} (main) · '
                f'山{b["mountain"]}向{b["water"]} (alt)')
    rows = [{"key": "missing", "zh": "缺角 missing corners", "text": missing_txt}]
    entry = rooms_by_id.get("foyer") or rooms_by_id.get("living")
    if entry:
        epal = entry[key]
        ew = natal["palaces"][epal]["water"]
        rows.append({"key": "entry", "zh": "Entry 入口", "text":
                     f'{entry["label"]} in {epal}宮 · {stx(epal)} · '
                     + (f"door greets timely 向星{ew} ✓" if ew in (8, 9, 1)
                        else f"door 向星{ew} — dated qi, keep entry bright")})
    kitchen = rooms_by_id.get("kitchen")
    if kitchen and breadwinner in charts and kitchen[key] == "中":
        rows.append({"key": "stove", "zh": "Stove 灶位", "text":
                     "Kitchen in 中宮 — the heart of the home (火燒心堂): keep "
                     "the stove itself off-centre if the layout allows"})
    elif kitchen and breadwinner in charts:
        kpal = kitchen[key]
        c = charts[breadwinner]
        kstar = youxing_stars(ming_gua(c.lichun_year, c.sex))[kpal]
        rows.append({"key": "stove", "zh": "Stove 灶位", "text":
                     f"Kitchen in {kpal}宮 · "
                     + (f"stove presses breadwinner's {kstar} — correct 壓凶 ✓"
                        if kstar in BAD_BAZHAI
                        else f"stove burns an auspicious {kstar} — point the "
                             f"stove mouth toward a good direction to compensate")
                     + (f" · annual {annual[kpal]} star this year"
                        if annual[kpal] in (2, 5) else "")})
    wc_pals = {BRANCH_PALACE[WENCHANG[c.day_master]]: n
               for n, c in charts.items()}
    bits = []
    for r in rooms:
        if r["id"] not in WET_IDS:
            continue
        p = r[key]
        flags = []
        if natal["palaces"][p]["water"] in (8, 9):
            flags.append(f'presses wealth 向星{natal["palaces"][p]["water"]} ✗')
        if p in wc_pals:
            flags.append(f"presses {wc_pals[p]}'s 文昌 ✗")
        bits.append(f'{r["label"]}→{p}宮'
                    + (f' ({", ".join(flags)})' if flags else ""))
    rows.append({"key": "wet", "zh": "Wet rooms 廁浴",
                 "text": " · ".join(bits) or "—"})
    cw = []
    for tag, ch in ((("main", natal), ("alt", alt)) if dual
                    else (("", natal),)):
        lbl = f" ({tag})" if tag else ""
        for w in (8, 9):
            pals = [p for p in PALACES8 if ch["palaces"][p]["water"] == w]
            if not pals:
                cw.append(f"向星{w}{lbl}: 中宮 — locked in the centre, "
                          "not activatable")
                continue
            rms = [r["label"] for r in rooms if r.get(key) in pals]
            cw.append(f'向星{w}{lbl}: {"/".join(pals)}宮 → '
                      f'{", ".join(rms) or "no indoor room"}')
    rows.append({"key": "caiwei", "zh": "財位 wealth spots",
                 "text": " · ".join(cw)})
    return rows


def harmony_matrix(charts: dict, ys_map: dict) -> dict:
    """All-pairs 合婚: {names, pairs:[{a, b, score, band, chips}]}."""
    names = list(charts)
    pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            p = pair_compatibility(charts[a], charts[b], ys_map[a], ys_map[b])
            pairs.append({"a": a, "b": b, "score": p["score"],
                          "band": p["band"],
                          "chips": [c["label"] for c in p["chips"]]})
    return {"names": names, "pairs": pairs}
