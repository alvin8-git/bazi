"""流日 daily fortune — the next N days for ONE person, activity by activity.

Layers, each cited in the row's reasons:
  ① 十二建除 day officer and 月破 — from zeri.rate_day (the house Dates tab's
    own rules; not duplicated here).
  ② Personal branch interactions — the day branch vs the natal DAY branch
    (spouse palace / the self) and YEAR branch (生肖): 沖 合 害.
  ③ Element of the day stem vs the chart's 用神 / 忌神.
Six activities: moving house, signing & banking, marriage & proposals, travel,
medical & surgery, launching & starting. Verdict per activity: good / neutral /
avoid, with the clause that decided it. ponytail: 刑 and 28宿 are out of scope —
add when a verdict disagrees with an almanac the owner trusts.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

SG = ZoneInfo("Asia/Singapore")

from .bazi import ten_god
from .wuxing import CHONG_MAP, HAI_MAP, HE_MAP, HIDDEN_STEMS, STEM_ELEMENT
from .zeri import day_info, rate_day
from .i18n import L, T, and_l, cap, dot, jn, zs  # noqa: F401

ACTIVITIES = [("moving", "搬家 moving house"), ("signing", "签约 signing & banking"),
              ("marriage", "婚嫁 marriage & proposals"), ("travel", "出行 travel"),
              ("medical", "医疗 medical & surgery"), ("launch", "开业 launching & starting")]
_GOOD_OFFICERS = {"成": "成日 success", "開": "開日 open", "定": "定日 settled"}
_RANK = {"avoid": 2, "good": 1, "neutral": 0}


def _set(flags: dict, key: str, verdict: str, why: str, short: str = "") -> None:
    cur = flags[key]
    if _RANK[verdict] > _RANK[cur["verdict"]]:
        flags[key] = {"verdict": verdict, "why": why, "short": short}
    elif verdict == cur["verdict"] and verdict != "neutral" and why not in cur["why"]:
        flags[key] = {"verdict": verdict, "why": (cur["why"] + "; " + why).strip("; "), "short": cur["short"] or short}


def daily_fortune(c, ys: dict, start: date | None = None, days: int = 30, lang: str = "en") -> dict:
    start = start or datetime.now(SG).date()      # the server runs on UTC; the reader lives in SG
    dm = c.day_master
    natal_db = c.pillars["day"].branch
    natal_yb = c.pillars["year"].branch
    fav = list(ys.get("favourable", [])); unfav = list(ys.get("unfavourable", []))
    member = [{"name": "you", "year_branch": natal_yb, "day_branch": natal_db}]
    rows = []
    for i in range(days):
        d = start + timedelta(days=i)
        r = rate_day(d, member, lang=lang)
        gz = r["day_gz"]; st, db = gz[0], gz[1]
        el = STEM_ELEMENT[st]
        stem_god = ten_god(dm, st); branch_god = ten_god(dm, HIDDEN_STEMS[db][0])
        med = "favourable" if el in fav else "against" if el in unfav else "neutral"
        ix = []
        if CHONG_MAP.get(db) == natal_db: ix.append("沖日支")
        if HE_MAP.get(db) == natal_db: ix.append("合日支")
        if HAI_MAP.get(db) == natal_db: ix.append("害日支")
        if CHONG_MAP.get(db) == natal_yb: ix.append("沖生肖")
        flags = {k: {"verdict": "neutral", "why": "", "short": ""} for k, _ in L("daily.ACTIVITIES", ACTIVITIES, lang)}
        off = r["officer"]
        # ① officer layer
        if off in L("daily._GOOD_OFFICERS", _GOOD_OFFICERS, lang):
            for k in ("moving", "signing", "marriage", "travel", "launch"):
                _set(flags, k, "good", L("daily._GOOD_OFFICERS", _GOOD_OFFICERS, lang)[off], f"{off}日")
            if off == "成": _set(flags, "medical", "good", T("daily.daily_fortune.01", "成日 success", lang), "成日")
        if off == "除": _set(flags, "medical", "good", T("daily.daily_fortune.02", "除日 removal — treatment and cleansing", lang), "除日")
        if off == "閉":
            _set(flags, "moving", "avoid", T("daily.daily_fortune.03", "閉日 closed", lang), "閉日"); _set(flags, "travel", "avoid", T("daily.daily_fortune.04", "閉日 closed", lang), "閉日")
        if off == "危":
            _set(flags, "medical", "avoid", T("daily.daily_fortune.05", "危日 danger", lang), "危日"); _set(flags, "travel", "avoid", T("daily.daily_fortune.06", "危日 danger", lang), "危日")
        podi = any(n["rule_id"] == "podi" for n in r["notes"]) or off == "破"
        if podi:
            for k, _ in L("daily.ACTIVITIES", ACTIVITIES, lang): _set(flags, k, "avoid", T("daily.daily_fortune.07", "破日 — day 沖 month", lang), "破日")
        # ② personal branch layer
        if "沖日支" in ix:
            for k in ("marriage", "moving", "launch"): _set(flags, k, "avoid", T("daily.daily_fortune.08", f"day {db} 沖 your day branch {natal_db}", lang, db=db, natal_db=natal_db), "沖日支")
        if "沖生肖" in ix:
            for k in ("marriage", "moving"): _set(flags, k, "avoid", T("daily.daily_fortune.09", f"day {db} 沖 your year branch {natal_yb}", lang, db=db, natal_yb=natal_yb), "沖生肖")
        if "合日支" in ix:
            for k in ("marriage", "signing"): _set(flags, k, "good", T("daily.daily_fortune.10", f"day {db} 六合 your day branch {natal_db}", lang, db=db, natal_db=natal_db), "合日支")
        if "害日支" in ix:
            _set(flags, "medical", "avoid", T("daily.daily_fortune.11", f"day {db} 害 your day branch {natal_db}", lang, db=db, natal_db=natal_db), "害日支")
        # ③ element layer
        if fav and el == fav[0]:
            for k in ("launch", "signing"): _set(flags, k, "good", T("daily.daily_fortune.12", f"{el} day carries your primary 用神", lang, el=el), "用神日")
        if unfav and el == unfav[0]:
            for k in ("signing", "launch"): _set(flags, k, "avoid", T("daily.daily_fortune.13", f"{el} day carries your chief 忌神", lang, el=el), "忌神日")
        rows.append({"date": d.isoformat(), "weekday": T(f"daily.WEEKDAY.{d.strftime('%a')}", d.strftime("%a"), lang), "gz": gz, "officer": off,
                     "stem_god": stem_god, "branch_god": branch_god, "element": el, "medicine": med,
                     "interactions": ix, "score": r["score"], "flags": flags, "today": i == 0})
    goods = [(sum(1 for f in r["flags"].values() if f["verdict"] == "good"), -sum(1 for f in r["flags"].values() if f["verdict"] == "avoid"), r) for r in rows]
    best = max(goods, key=lambda t: (t[1] == 0, t[0], t[1]))[2] if rows else None
    worst = max(rows, key=lambda r: sum(1 for f in r["flags"].values() if f["verdict"] == "avoid")) if rows else None
    return {"start": start.isoformat(), "days": days, "rows": rows,
            "now_month_branch": day_info(start)["month_branch"],   # the 月令 in force today (節-bounded)
            "best": {"date": best["date"], "gz": best["gz"], "officer": best["officer"],
                     "for": [k for k, f in best["flags"].items() if f["verdict"] == "good"]} if best else None,
            "worst": {"date": worst["date"], "gz": worst["gz"],
                      "avoid": [k for k, f in worst["flags"].items() if f["verdict"] == "avoid"],
                      "why": next((f["why"] for f in worst["flags"].values() if f["verdict"] == "avoid"), "")} if worst else None,
            "activities": L("daily.ACTIVITIES", ACTIVITIES, lang),
            "source_ref": T("daily.daily_fortune.14", "十二建除 + 月破 (zeri) · day branch 沖/合/害 vs natal day & year branch · day stem element vs 用神/忌神", lang)}
