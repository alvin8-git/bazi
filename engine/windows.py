"""Windows 时机 — the timing cross-layer (7-insights completion).

Multiplies the layers the engine already computes — 大運 luck pillars, 流年
annual pillars, the natal pillars, 用神 lists, health imbalances, 桃花 and
the spouse palace — into labelled, per-dimension windows:

  decades — each 大運 phase-labelled (growth 成長 / consolidation 蓄勢 /
            transition 轉換 / corrective 修整) from element favourability
            plus branch interactions with the natal day/month pillars
  years   — ten years of per-dimension flags (career / wealth /
            relationship / health) plus a climate×weather overall verdict
            (decade = climate, year = weather)

Deterministic, no LLM; every flag carries its rule in the note.
"""
from __future__ import annotations

from .bazi import ten_god
from .domains import VAULT, health_map
from .liunian import year_element_read, year_ganzhi
from .wuxing import (BRANCH_ELEMENT, CHONG_MAP, HE_MAP, HIDDEN_STEMS, KE,
                     SANHE, STEM_ELEMENT)

_TRINE = {b: set(grp) for grp, _ in SANHE for b in grp}
_TAOHUA = {"申": "酉", "子": "酉", "辰": "酉", "寅": "卯", "午": "卯", "戌": "卯",
           "巳": "午", "酉": "午", "丑": "午", "亥": "子", "卯": "子", "未": "子"}
WEALTH_GODS = {"正財", "偏財"}
OFFICER_GODS = {"正官", "七殺"}
SUPPORT_GODS = {"比肩", "劫財", "正印", "偏印"}


def _decade_phase(chart, ys, d) -> dict:
    """Phase-label one 大運 pillar dict (needs gz/ages/current)."""
    st, br = d["gz"][0], d["gz"][1]
    fav, unfav = set(ys["favourable"]), set(ys["unfavourable"])
    score, notes = 0, []
    for el, what in ((STEM_ELEMENT[st], f"stem {st}"), (BRANCH_ELEMENT[br], f"branch {br}")):
        if el in fav:
            score += 1
            notes.append(f"{what} {el} favourable")
        elif el in unfav:
            score -= 1
            notes.append(f"{what} {el} unfavourable")
    day_br = chart.pillars["day"].branch
    month_br = chart.pillars["month"].branch
    transition = False
    if CHONG_MAP.get(br) == day_br:
        score -= 1
        transition = True
        notes.append(f"decade branch 沖 day branch {day_br} — personal upheaval")
    if CHONG_MAP.get(br) == month_br:
        score -= 1
        transition = True
        notes.append(f"decade branch 沖 month branch {month_br} — career-pillar shakeup")
    if HE_MAP.get(br) in (day_br, month_br):
        score += 1
        notes.append("decade branch 六合 with a core pillar — steadying")
    phase, zh = (("growth", "成長") if score >= 2 else
                 ("corrective", "修整") if score <= -2 else
                 ("transition", "轉換") if transition else
                 ("consolidation", "蓄勢"))
    return {**{k: d[k] for k in ("gz", "ages")}, "current": d.get("current", False),
            "phase": phase, "phase_zh": zh, "score": score, "notes": notes}


def _year_row(chart, ys, hm_excess, hm_weak, y, decade_score) -> dict:
    dm = chart.day_master
    st, br = year_ganzhi(y)
    g_st, g_br = ten_god(dm, st), ten_god(dm, HIDDEN_STEMS[br][0])
    els = {STEM_ELEMENT[st], BRANCH_ELEMENT[br]}
    gods = {g_st, g_br}
    fav, unfav = set(ys["favourable"]), set(ys["unfavourable"])
    weak = chart.strength["verdict"].startswith("身弱")
    day_br = chart.pillars["day"].branch
    month_br = chart.pillars["month"].branch
    wealth_el = KE[STEM_ELEMENT[dm]]

    def dim(flag, note):
        return {"flag": flag, "note": note}

    # career — month pillar activation vs clash, officer arrival
    if CHONG_MAP.get(br) == month_br:
        career = dim("caution", f"年支{br} 沖 month pillar {month_br} — don't force career moves")
    elif HE_MAP.get(br) == month_br or (br in _TRINE.get(month_br, set()) and br != month_br):
        career = dim("window", f"年支{br} 合 month pillar — career pillar activated, leverage window")
    elif gods & OFFICER_GODS:
        if gods & SUPPORT_GODS or not weak:
            career = dim("window", f"{'/'.join(gods & OFFICER_GODS)} arrives with support — authority spotlight")
        else:
            career = dim("caution", f"{'/'.join(gods & OFFICER_GODS)} arrives on a weak chart — pressure year, deliver quietly")
    else:
        career = dim("quiet", "no career-pillar activation")
    # wealth — wealth god arrival, vault, carry check
    if gods & WEALTH_GODS:
        if weak and wealth_el in unfav:
            wealth = dim("caution", f"{'/'.join(gods & WEALTH_GODS)} arrives but the chart can't hold it — "
                                    "wealth passes through; strengthen first, don't overreach")
        else:
            wealth = dim("window", f"{'/'.join(gods & WEALTH_GODS)} arrives — income moves possible")
    elif br == VAULT[wealth_el]:
        wealth = dim("window", f"年支{br} opens the 財庫 wealth vault")
    else:
        wealth = dim("quiet", "no wealth activation")
    # relationship — 桃花 and spouse palace
    th = _TAOHUA[chart.pillars["year"].branch]
    if CHONG_MAP.get(br) == day_br:
        rel = dim("caution", f"年支{br} 沖 spouse palace {day_br} — relationships need extra care")
    elif br == th:
        rel = dim("window", f"桃花 year ({br}) — social magnetism and relational openings")
    elif HE_MAP.get(br) == day_br or (br in _TRINE.get(day_br, set()) and br != day_br):
        rel = dim("window", f"年支{br} 合 spouse palace — partnership supported")
    else:
        rel = dim("quiet", "no relationship activation")
    # health — feeds an excess or replenishes a weakness
    hit_ex = sorted(els & hm_excess)
    hit_wk = sorted(els & hm_weak)
    if hit_ex:
        health = dim("caution", f"year feeds {'/'.join(hit_ex)} excess — watch those organ systems")
    elif hit_wk:
        health = dim("window", f"year replenishes weak {'/'.join(hit_wk)} — good recovery year")
    else:
        health = dim("quiet", "no imbalance triggered")
    # overall — climate (decade) × weather (year elements)
    elem = year_element_read(chart, ys["favourable"], y)["explanation"]
    yr_score = elem.count("favourable") - elem.count("unfavourable")
    overall, zh = (("peak", "峰值窗口") if decade_score > 0 and yr_score > 0 else
                   ("careful", "謹慎年") if decade_score < 0 and yr_score < 0 else
                   ("steady", "平穩"))
    return {"y": y, "gz": st + br, "overall": overall, "overall_zh": zh,
            "career": career, "wealth": wealth, "relationship": rel,
            "health": health}


def timing_windows(chart, ys: dict, dayun: list[dict], year_now: int) -> dict:
    """The full Windows payload for one person."""
    decades = [_decade_phase(chart, ys, d) for d in dayun]
    cur = next((d for d in decades if d["current"]), None)
    hm = health_map(chart)
    hm_excess = {h["element"] for h in hm if "excess" in h["status"]}
    hm_weak = {h["element"] for h in hm if "weak" in h["status"]}
    years = [_year_row(chart, ys, hm_excess, hm_weak, y,
                       cur["score"] if cur else 0)
             for y in range(year_now, year_now + 10)]
    th = _TAOHUA[chart.pillars["year"].branch]
    where = [p for p in ("year", "month", "day", "hour")
             if chart.pillars[p].branch == th]
    th_type = ("牆內 within walls — stable affection" if {"year", "month"} & set(where)
               else "牆外 outside walls — variable attraction" if where
               else "not in the natal chart — activated only in 桃花 years")
    return {"decades": decades, "years": years,
            "taohua": {"branch": th, "pillars": where, "type": th_type},
            "source_ref": "timing cross-layer — 大運/流年 × natal pillars × 用神 "
                          "(month pillar = career, 財星+財庫 = wealth, 日支+桃花 = "
                          "relationship, element imbalance = health; decade = "
                          "climate, year = weather)"}
