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
from .calendar import pillars_for
from .liunian import taisui_tiers
from .wuxing import CHONG_MAP, HAI_MAP, HE_MAP, HIDDEN_STEMS, STEM_ELEMENT
from .zeri import day_info, rate_day
from .i18n import L, T, and_l, cap, dot, jn, zs  # noqa: F401

ACTIVITIES = [("moving", "搬家 moving house"), ("signing", "签约 signing & banking"),
              ("marriage", "婚嫁 marriage & proposals"), ("travel", "出行 travel"),
              ("medical", "医疗 medical & surgery"), ("launch", "开业 launching & starting")]
_GOOD_OFFICERS = {"成": "成日 success", "開": "開日 open", "定": "定日 settled"}
_RANK = {"avoid": 2, "good": 1, "neutral": 0}
# Year against day (round A, integration.md rule 2): a person who meets the year's 太歲 as 值, 沖 or 刑 (犯太歲) is not sent to a day for these three
# activities. The veto never deletes a day: every row keeps its verdicts; only the recommendation (`best`) leaves the three activities out, and
# the date block carries one caution line. Source: 《淵海子平》〈論太歲吉凶〉 "太歲乃年中天子，故不可犯，犯之則凶". A veto beats a favour.
TAISUI_VETO_TIERS = ("值太歲", "沖太歲", "刑太歲")
TAISUI_VETO_ACTIVITIES = ("marriage", "moving", "launch")


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
            # 協紀辨方書 卷十〈宜忌〉建除十二神: 嫁娶 (結婚姻納采問名嫁娶) is listed under 成日 only (as 天喜); the 開日 and 定日 lists carry no
            # 嫁娶 line. Round A correction: 開 and 定 were wrongly good for marriage here. 開日 does list 般移 and 行幸遣使, so the rest stand.
            for k in ("moving", "signing", "travel", "launch") + (("marriage",) if off == "成" else ()):
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
        tb = pillars_for(datetime(d.year, d.month, d.day, 12))["year"].branch      # the 太歲 branch on that day (年柱 turns at 立春)
        vet = [t for t in taisui_tiers(natal_yb, tb) if t in TAISUI_VETO_TIERS]
        rows.append({"date": d.isoformat(), "weekday": T(f"daily.WEEKDAY.{d.strftime('%a')}", d.strftime("%a"), lang), "gz": gz, "officer": off,
                     "stem_god": stem_god, "branch_god": branch_god, "element": el, "medicine": med,
                     "interactions": ix, "score": r["score"], "flags": flags, "today": i == 0, "taisui": vet})

    def recommended(r):          # the activities a day may be recommended for: good, and not held back by the 太歲 check
        return [k for k, f in r["flags"].items() if f["verdict"] == "good" and not (r["taisui"] and k in TAISUI_VETO_ACTIVITIES)]
    goods = [(len(recommended(r)), -sum(1 for f in r["flags"].values() if f["verdict"] == "avoid"), r) for r in rows]
    best = max(goods, key=lambda t: (t[1] == 0, t[0], t[1]))[2] if rows else None
    if best is not None and not recommended(best):
        best = None                                  # nothing left to recommend: say nothing rather than recommend a vetoed day
    held = next((r["taisui"] for r in rows if r["taisui"]), None)
    worst = max(rows, key=lambda r: sum(1 for f in r["flags"].values() if f["verdict"] == "avoid")) if rows else None
    return {"start": start.isoformat(), "days": days, "rows": rows,
            "now_month_branch": day_info(start)["month_branch"],   # the 月令 in force today (節-bounded)
            "best": {"date": best["date"], "gz": best["gz"], "officer": best["officer"],
                     "for": recommended(best)} if best else None,
            "worst": {"date": worst["date"], "gz": worst["gz"],
                      "avoid": [k for k, f in worst["flags"].items() if f["verdict"] == "avoid"],
                      "why": next((f["why"] for f in worst["flags"].values() if f["verdict"] == "avoid"), "")} if worst else None,
            "taisui_caution": ({"tiers": held, "held_back": list(TAISUI_VETO_ACTIVITIES),
                                "text": T("daily.daily_fortune.15", f"A 犯太歲 year ({jn(held, lang)}) holds marriage, moving and launching back: the days below stay on the list, "
                                          "but none is recommended for those three", lang, join_held=jn(held, lang)),
                                "source_ref": T("daily.daily_fortune.16", "《淵海子平》〈論太歲吉凶〉 太歲乃年中天子，故不可犯，犯之則凶", lang)} if held else None),
            "activities": L("daily.ACTIVITIES", ACTIVITIES, lang),
            "source_ref": T("daily.daily_fortune.14", "十二建除 + 月破 (zeri) · day branch 沖/合/害 vs natal day & year branch · day stem element vs 用神/忌神", lang)}
