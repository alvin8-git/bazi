"""Four pillars, 十神, five-element weights, Day-Master strength, 大運.

Chart is the engine-wide contract (eng review 1A): computed once per
(person, time_policy); everything downstream takes a Chart, never a raw
datetime plus flags.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from . import calendar as cal
from .wuxing import (BRANCH_ELEMENT, ELEMENT_COLOURS, ELEMENT_EN, ELEMENTS,
                     HIDDEN_STEMS, KE, SHENG, SHENG_REV, STEM_ELEMENT,
                     STEM_YANG, STEMS)

CLOCK, TRUE_SOLAR = "clock", "true_solar"

TEN_GOD_ORDER = ["比肩", "劫財", "食神", "傷官", "偏財", "正財", "七殺", "正官", "偏印", "正印"]
TEN_GOD_EN = {"比肩": "Friend", "劫財": "Rob Wealth", "食神": "Eating God",
              "傷官": "Hurting Officer", "偏財": "Indirect Wealth", "正財": "Direct Wealth",
              "七殺": "7 Killings", "正官": "Direct Officer", "偏印": "Indirect Resource",
              "正印": "Direct Resource"}


def ten_god(day_stem: str, other_stem: str) -> str:
    dm_el, o_el = STEM_ELEMENT[day_stem], STEM_ELEMENT[other_stem]
    same_pol = STEM_YANG[day_stem] == STEM_YANG[other_stem]
    if o_el == dm_el:
        return "比肩" if same_pol else "劫財"
    if SHENG[dm_el] == o_el:          # DM generates other → output
        return "食神" if same_pol else "傷官"
    if KE[dm_el] == o_el:             # DM controls other → wealth
        return "偏財" if same_pol else "正財"
    if KE[o_el] == dm_el:             # other controls DM → officer
        return "七殺" if same_pol else "正官"
    return "偏印" if same_pol else "正印"  # other generates DM → resource


@dataclass
class DaYun:
    gz: cal.GZ
    start_age: float          # decimal years (3 days = 1 year rule)
    end_age: float

    def covers(self, age: float) -> bool:
        return self.start_age <= age < self.end_age


@dataclass
class Chart:
    person: str
    sex: str                     # "M" / "F"
    birth_local: datetime        # civil clock time
    policy: str                  # CLOCK | TRUE_SOLAR
    effective_dt: datetime       # datetime the pillars were computed from
    pillars: dict                # year/month/day/hour → GZ
    citations: list = field(default_factory=list)

    # ---- derived, filled in analyze() ----
    day_master: str = ""
    ten_gods: dict = field(default_factory=dict)          # position → god (stems)
    hidden_gods: dict = field(default_factory=dict)       # branch pos → [(stem, god)]
    element_weights: dict = field(default_factory=dict)   # element → float
    strength: dict = field(default_factory=dict)          # verdict + 4-step walkthrough
    dayun: list = field(default_factory=list)

    @property
    def lichun_year(self) -> int:
        """BaZi year (立春-bounded), recovered from the year-pillar cycle."""
        y = self.effective_dt.year
        # 干支 cycle position of `y` assuming boundary already applied by sxtwl:
        # if the pillar matches year y it IS y, else it's y-1 (born before 立春).
        stem_idx = (y - 4) % 10
        return y if STEMS[stem_idx] == self.pillars["year"].stem else y - 1


def build_chart(person: str, sex: str, birth_local: datetime, policy: str) -> Chart:
    if policy == TRUE_SOLAR:
        eff = cal.true_solar_datetime(birth_local)
        note = (f"true solar time: clock {birth_local:%H:%M} → {eff:%H:%M} "
                f"(SG UTC+{cal.sg_utc_offset_hours(birth_local.date()):g}, lon {cal.SG_LON}°E, "
                f"equation of time {cal.equation_of_time_minutes(birth_local.date()):+.1f} min)")
    else:
        eff, note = birth_local, "civil clock time, no solar correction"
    chart = Chart(person=person, sex=sex, birth_local=birth_local, policy=policy,
                  effective_dt=eff, pillars=cal.pillars_for(eff))
    chart.citations.append({"rule_id": "time-policy", "layer": "bazi",
                            "source_ref": "子平 convention (design premise 2)",
                            "explanation": note})
    analyze(chart)
    return chart


def analyze(chart: Chart) -> None:
    p = chart.pillars
    chart.day_master = p["day"].stem
    dm = chart.day_master
    dm_el = STEM_ELEMENT[dm]

    for pos in ("year", "month", "hour"):
        chart.ten_gods[pos] = ten_god(dm, p[pos].stem)
    chart.ten_gods["day"] = "日主"
    for pos in ("year", "month", "day", "hour"):
        chart.hidden_gods[pos] = [(s, ten_god(dm, s)) for s in HIDDEN_STEMS[p[pos].branch]]

    # Element weights: stems 1.0, branch main qi 1.0, minor hidden stems 1/3.
    w = {e: 0.0 for e in ELEMENTS}
    for pos in ("year", "month", "day", "hour"):
        w[STEM_ELEMENT[p[pos].stem]] += 1.0
        hidden = HIDDEN_STEMS[p[pos].branch]
        w[STEM_ELEMENT[hidden[0]]] += 1.0
        for s in hidden[1:]:
            w[STEM_ELEMENT[s]] += 1 / 3
    chart.element_weights = {e: round(v, 2) for e, v in w.items()}

    # --- Day-Master strength: the explicit 4-step walkthrough (design: reading format) ---
    month_el = BRANCH_ELEMENT[p["month"].branch]
    if month_el == dm_el:
        season_state, season_pts = "旺 (當令)", 2.0
    elif SHENG[month_el] == dm_el:
        season_state, season_pts = "相 (得生)", 1.0
    elif SHENG[dm_el] == month_el:
        season_state, season_pts = "休 (洩於月令)", -1.0
    elif KE[dm_el] == month_el:
        season_state, season_pts = "囚 (剋月令)", -1.5
    else:
        season_state, season_pts = "死 (月令剋我)", -2.0

    support = w[dm_el] + w[SHENG_REV[dm_el]]              # 比劫 + 印
    officer_el = next(e for e in ELEMENTS if KE[e] == dm_el)
    drain = w[SHENG[dm_el]] + w[KE[dm_el]] + w[officer_el]   # 食傷 + 財 + 官殺
    total = sum(w.values())

    roots = [p[pos].branch for pos in ("year", "month", "day", "hour")
             if any(STEM_ELEMENT[s] == dm_el for s in HIDDEN_STEMS[p[pos].branch])]
    root_pts = 0.5 if roots else -0.5

    score = season_pts + 2.0 * (support - drain) / total + root_pts
    # ponytail: threshold tuned to the 身弱 golden fixture; revisit if a future
    # verified chart disagrees — upgrade path is a per-school strength model.
    verdict = "身弱 (Weak)" if score < 0.25 else "身強 (Strong)"

    # Tier 4 extras: auditable ratios + formation (從格) decision boundary
    root_w = sum((1.0 if k == 0 else 1 / 3)
                 for pos in ("year", "month", "day", "hour")
                 for k, s in enumerate(HIDDEN_STEMS[p[pos].branch])
                 if STEM_ELEMENT[s] == dm_el)
    support_ratio = support / total
    if not roots and support_ratio < 0.12:
        formation = {"status": "從弱 candidate (follower)",
                     "detail": "no roots and minimal support — a specialist school may "
                               "read this as a follower structure; we keep the ordinary "
                               "扶抑 reading and flag it"}
    elif support_ratio > 0.75:
        formation = {"status": "專旺 candidate (dominant)",
                     "detail": "support overwhelms all drains — may qualify as a "
                               "dominant structure; ordinary reading kept, flagged"}
    else:
        formation = {"status": "正格 ordinary structure",
                     "detail": "evidence does not support a follower/special formation "
                               "— standard strength rules apply"}

    chart.strength = {
        "verdict": verdict,
        "score": round(score, 2),
        "support_ratio": round(100 * support_ratio, 1),
        "root_ratio": round(100 * root_w / total, 1),
        "formation": formation,
        "steps": [
            {"step": 1, "name": "Season 得令", "value": season_state,
             "detail": f"month branch {p['month'].branch} is {ELEMENT_EN[month_el]}; "
                       f"Day Master {dm} is {ELEMENT_EN[dm_el]} → {season_state}"},
            {"step": 2, "name": "Support count", "value": round(support, 2),
             "detail": f"比劫 {ELEMENT_EN[dm_el]} {w[dm_el]} + 印 {ELEMENT_EN[SHENG_REV[dm_el]]} {w[SHENG_REV[dm_el]]}"},
            {"step": 3, "name": "Drain count", "value": round(drain, 2),
             "detail": "食傷 + 財 + 官殺 weights combined"},
            {"step": 4, "name": "Root check", "value": "有根 " + "、".join(roots) if roots else "無根",
             "detail": f"branches whose hidden stems carry {ELEMENT_EN[dm_el]}"},
        ],
    }
    chart.citations.append({"rule_id": "strength-4step", "layer": "bazi",
                            "source_ref": "扶抑 framework (旺相休囚死 + 通根)",
                            "explanation": f"{verdict}, score {score:+.2f}"})

    _compute_dayun(chart)


def _compute_dayun(chart: Chart, count: int = 8) -> None:
    """大運: yang-year male / yin-year female run forward; otherwise backward."""
    year_yang = STEM_YANG[chart.pillars["year"].stem]
    forward = (year_yang and chart.sex == "M") or (not year_yang and chart.sex == "F")
    start_age, jie = cal.dayun_start_age(chart.effective_dt.date(), forward)

    m = chart.pillars["month"]
    stem_i, branch_i = STEMS.index(m.stem), cal.BRANCHES.index(m.branch)
    step = 1 if forward else -1
    luck = []
    age = start_age
    for k in range(1, count + 1):
        gz = cal.GZ(STEMS[(stem_i + step * k) % 10], cal.BRANCHES[(branch_i + step * k) % 12])
        luck.append(DaYun(gz=gz, start_age=round(age, 1), end_age=round(age + 10, 1)))
        age += 10
    chart.dayun = luck
    chart.citations.append({
        "rule_id": "dayun-direction", "layer": "bazi",
        "source_ref": "陽男陰女順行, 陰男陽女逆行; 起運 = 距節日數/3",
        "explanation": f"{'forward 順行' if forward else 'backward 逆行'} from month pillar "
                       f"{m}; start age {start_age:.1f} (to 節 {jie})"})


def favourable_colours(fav_elements: list[str]) -> list[str]:
    out: list[str] = []
    for e in fav_elements:
        out.extend(ELEMENT_COLOURS[e])
    return out
