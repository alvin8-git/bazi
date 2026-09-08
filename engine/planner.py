"""Planner 择时 (M3) — dates, hours and renovation windows as action cards.

Wraps the existing zeri (十二建除 day rating + 吉時 hours) and R4 timing
remedies into the universal card contract. Subject types: "date" and "year".
Score map for days: zeri raw −4…+3 → clamp(50 + 15·raw, 5, 95).
"""
from __future__ import annotations

from .aspects import BAND_ZH, SCHEMA_V, band_of
from .remedies import timing_remedies

OFFICER_EN = {"建": "establish", "除": "remove/cleanse", "滿": "fullness",
              "平": "balance", "定": "settle", "執": "hold", "破": "破 breaker",
              "危": "danger", "成": "completion", "收": "harvest",
              "開": "open", "閉": "close"}


def _day_score(raw: float) -> int:
    return round(min(95.0, max(5.0, 50 + 15 * raw)))


def day_card(d: dict) -> dict:
    """One rated day (zeri.rate_day output) → a date card."""
    score = _day_score(d["score"])
    band = band_of(score)
    actions = []
    for h in d["hours"]["best"]:
        actions.append({
            "trigger": f"{'·'.join(h['tags'])} hour on {d['day_gz']}日",
            "action": f"favour the {h['branch']}時 window {h['time']} "
                      f"({'·'.join(h['tags'])})",
            "category": "timing", "priority": 2,
            "source_ref": "吉時 — 天乙貴人/合日 hour tables",
            "resource": f"hour:{h['branch']}"})
    for h in d["hours"]["avoid"]:
        actions.append({
            "trigger": f"時破 hour on {d['day_gz']}日",
            "action": f"avoid the {h['branch']}時 window {h['time']} (時破)",
            "category": "timing", "priority": 1,
            "source_ref": "時破 — hour clashes the day branch",
            "resource": f"hour:{h['branch']}"})
    officer = d["officer"]
    meaning = (f"{officer}日 ({OFFICER_EN.get(officer, officer)}) — "
               + ("a strong day for move-ins, signings and starts" if band in ("strong", "good")
                  else "an ordinary day — usable, not special" if band == "fair"
                  else "avoid launching anything important on this day"))
    return {"v": SCHEMA_V,
            "subject": {"type": "date", "id": d["date"], "label": d["date"]},
            "aspect": "timing", "aspect_zh": "择日",
            "score": score, "band": band, "band_zh": BAND_ZH[band],
            "meaning": meaning,
            "driver": f"{d['day_gz']}日 · officer {officer} "
                      f"({d['score']:+.1f} raw, incl. household clashes)",
            "actions": actions[:3],
            "audit": [{"rule_id": n["rule_id"], "sub_score": None, "weight": 0,
                       "explanation": n["explanation"],
                       "source_ref": n["source_ref"]} for n in d["notes"]] +
                     [{"rule_id": f"flag-{f['name']}", "sub_score": None,
                       "weight": 0, "explanation": f["why"],
                       "source_ref": f"per-person {f['kind']}"}
                      for f in d["person_flags"]],
            "superseded": [],
            "source_ref": "十二建除 + 月破 + household clash scan → affine 0-100",
            "person_flags": d["person_flags"]}


def reno_card(year: int, annual: dict[str, int],
              palace_rooms: dict[str, list[dict]]) -> dict:
    """Renovation-window card (subject type 'year'): R4 blocked zones."""
    acts = timing_remedies(year, annual, palace_rooms)
    n = len(acts)
    score = round(min(95.0, max(5.0, 85 - 15 * n)))
    band = band_of(score)
    return {"v": SCHEMA_V,
            "subject": {"type": "year", "id": str(year), "label": f"{year} 修造"},
            "aspect": "timing", "aspect_zh": "修造",
            "score": score, "band": band, "band_zh": BAND_ZH[band],
            "meaning": (f"{n} zone(s) must not be disturbed this year — plan works "
                        f"elsewhere, or wait for 立春 {year + 1} (≈4 Feb)" if n else
                        f"no traced room sits on a {year} afflicted zone — "
                        "renovation timing is only day-level this year"),
            "driver": (acts[0]["trigger"] if acts else f"clear year, {year}"),
            "actions": acts[:3],
            "audit": [{"rule_id": f"affliction-{i}", "sub_score": None,
                       "weight": 0, "explanation": a["trigger"],
                       "source_ref": a["source_ref"]}
                      for i, a in enumerate(acts)],
            "superseded": acts[3:],
            "source_ref": f"流年神煞 + 紫白 no-disturbance zones, {year}"}


def month_plan(days: list[dict], top: int = 5) -> dict:
    """Rated month (zeri.rate_month) → best-day cards + avoid list."""
    cards = sorted((day_card(d) for d in days), key=lambda c: -c["score"])[:top]
    avoid = [{"date": d["date"], "day_gz": d["day_gz"], "why":
              "破日 — day clashes the month" if any(n["rule_id"] == "podi"
                                                   for n in d["notes"])
              else f"officer {d['officer']} + clashes ({d['score']:+.1f})"}
             for d in days if d["score"] <= -1.5]
    return {"best": cards, "avoid": avoid}
