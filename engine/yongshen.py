"""用神 determination — the classical techniques as ordered, cited passes.

扶抑 (support/suppress) and 調候 (climatic) choose the favourable and unfavourable elements. 病藥 (sickness/remedy) is a detected finding that
rides beside them: it names the one built-in strain the chart carries and the element that cures it, and says whether 扶抑 agrees. 扶抑 leads,
as 調候 does: where the medicine is an element 扶抑 avoids, the finding says so and changes nothing else (tests pin this). 通關 (bridging) is
not applied to a single chart; it is used only between two charts, in the pair report (hehun_detail), and is left for a later round.
"""
from __future__ import annotations

from .bazi import Chart, favourable_colours
from .wuxing import (BRANCH_ELEMENT, ELEMENT_EN, ELEMENTS, KE, SHENG,
                     SHENG_REV, STEM_ELEMENT)
from .i18n import ELEM, L, T, and_l, cap, dot, jn, zs  # noqa: F401

WINTER, SUMMER = {"亥", "子", "丑"}, {"巳", "午", "未"}

# 病藥. The rule behind it: 《滴天髓》〈中和〉 "有病方為貴，無傷不是奇，格中如去病，財祿兩相隨" (a chart's sickness is named, then cured).
# Detection reuses interpret.ten_god_insights' pattern cuts (傷官 8% and 正官 5%; 比劫 20% and 財 8%; 財 25% and a weak Day Master), so no new
# number is introduced. The fixed order below is the tie-break: the first pattern that fires is the one reported.
#   pattern     medicine group  where the classics say it
#   傷官見官    印              《淵海子平》〈論傷官〉 傷官見官，為禍百端 (病); 〈傷官說〉 傷官見官，印運不妨 (藥)
#   比劫奪財    官殺            《淵海子平》〈論劫財〉 (病); 〈論陽刃〉 喜偏官七殺 (藥: the check on 比劫 at its strongest)
#   財多身弱    印              《三命通會》卷六〈論正財〉 財多身弱，柱無印助，皆不為福 (病); 身衰逢印資助 (藥)
# Not built, and why: 貪財壞印 and 梟神奪食 (techniques.md lists them) have no source we could read for their medicine; 財多身弱 names 印 in
# the text we could read, where techniques.md lists 比劫 first, so 比劫 is left out until a source says it. 通關 stays for a later round.
BINGYAO = (("傷官見官", "印", "《淵海子平》〈論傷官〉, 〈傷官說〉"),
           ("比劫奪財", "官殺", "《淵海子平》〈論劫財〉, 〈論陽刃〉"),
           ("財多身弱", "印", "《三命通會》卷六〈論正財〉"))


def yong_shen(chart: Chart, lang: str = "en") -> dict:
    dm_el = STEM_ELEMENT[chart.day_master]
    weak = chart.strength["verdict"].startswith("身弱")
    officer_el = next(e for e in ELEMENTS if KE[e] == dm_el)

    if weak:
        fav = [SHENG_REV[dm_el], dm_el]           # 印 first, then 比劫
        unfav = [officer_el, KE[dm_el], SHENG[dm_el]]
        fuyi = (T("yongshen.yong_shen.01", f"Weak Day Master: favour 印 ({ELEM(lang)[SHENG_REV[dm_el]]}) to nourish and "
                f"比劫 ({ELEM(lang)[dm_el]}) to support; avoid 官殺/財/食傷", lang, dm_el_sheng_rev_element_en=ELEM(lang)[SHENG_REV[dm_el]], dm_el_element_en=ELEM(lang)[dm_el]))
    else:
        fav = [SHENG[dm_el], KE[dm_el], officer_el]   # drain, wealth, control
        unfav = [SHENG_REV[dm_el], dm_el]
        fuyi = (T("yongshen.yong_shen.02", f"Strong Day Master: favour 食傷 ({ELEM(lang)[SHENG[dm_el]]}) to drain, "
                f"財 ({ELEM(lang)[KE[dm_el]]}) and 官殺 ({ELEM(lang)[officer_el]}); "
                f"avoid 印/比劫", lang, dm_el_sheng_element_en=ELEM(lang)[SHENG[dm_el]], dm_el_ke_element_en=ELEM(lang)[KE[dm_el]], officer_el_element_en=ELEM(lang)[officer_el]))

    citations = [{"rule_id": "yongshen-fuyi", "layer": "yongshen",
                  "source_ref": T("yongshen.yong_shen.03", "扶抑法 (technique 1 of 4)", lang), "explanation": fuyi}]

    month_branch = chart.pillars["month"].branch
    tiaohou = None
    if month_branch in WINTER and "火" not in fav:
        fav = ["火"] + fav
        tiaohou = T("yongshen.yong_shen.04", "born in winter — chart is cold, 火 (Fire) promoted by 調候", lang)
    elif month_branch in SUMMER and "水" not in fav:
        fav = ["水"] + fav
        tiaohou = T("yongshen.yong_shen.05", "born in summer — chart is hot, 水 (Water) promoted by 調候", lang)
    elif month_branch in WINTER or month_branch in SUMMER:
        tiaohou = T("yongshen.yong_shen.06", "climatic need already satisfied by 扶抑 selection", lang)
    citations.append({"rule_id": "yongshen-tiaohou", "layer": "yongshen",
                      "source_ref": T("yongshen.yong_shen.07", "調候法 (technique 2 of 4)", lang),
                      "explanation": tiaohou or T("yongshen.yong_shen.08", f"month {month_branch}: mild season, no climatic override", lang, month_branch=month_branch)})
    # dedupe, keep order
    fav = list(dict.fromkeys(fav))
    unfav = [e for e in dict.fromkeys(unfav) if e not in fav]

    by = bing_yao(chart, fav, unfav)
    expl = _bingyao_text(by, lang)
    citations.append({"rule_id": "yongshen-bingyao", "layer": "yongshen",
                      "source_ref": T("yongshen.yong_shen.13", "病藥法 (《滴天髓》〈中和〉: 格中如去病，財祿兩相隨)", lang),
                      "explanation": expl})
    citations.append({"rule_id": "yongshen-tongguan", "layer": "yongshen",
                      "source_ref": T("yongshen.yong_shen.11", "通關法 (technique 4 of 4)", lang),
                      "explanation": T("yongshen.yong_shen.21", "not used on a single chart: 通關 is applied only between two charts, in the pair report", lang)})
    return {"favourable": fav, "unfavourable": unfav,
            "colours": favourable_colours(fav[:2]),
            "citations": citations,
            "bingyao": by}


def bing_yao(chart: Chart, fav: list[str], unfav: list[str]) -> dict:
    """The 病藥 finding (language-free codes; _bingyao_text words it). Never changes fav/unfav: 扶抑 leads, and a medicine element that 扶抑
    avoids is reported as `parts`, not acted on."""
    from .interpret import pattern_hits
    from .shensha import ten_god_pct
    dm_el = STEM_ELEMENT[chart.day_master]
    fired = pattern_hits(ten_god_pct(chart), chart.strength["verdict"].startswith("身弱"))
    hit = next((b for b in BINGYAO if fired[b[0]]), None)
    if hit is None:
        return {"rule_id": "bingyao-none", "pattern": None, "medicine_group": None, "medicine_el": None, "present": None,
                "status": "none", "leads": "扶抑", "source_ref": "《滴天髓》〈中和〉", "tongguan": "pair report only"}
    name, group, src = hit
    med_el = SHENG_REV[dm_el] if group == "印" else next(e for e in ELEMENTS if KE[e] == dm_el)
    w = chart.element_weights
    present = w[med_el] / (sum(w.values()) or 1) > .07          # the engine's own "weak" cut (domains.health_map)
    status = "agrees" if med_el in fav else "parts" if med_el in unfav else "neutral"
    return {"rule_id": f"bingyao-{name}", "pattern": name, "medicine_group": group, "medicine_el": med_el, "present": present,
            "status": status, "leads": "扶抑", "source_ref": src, "tongguan": "pair report only"}


_BINGYAO_ID = {"傷官見官": "yongshen.yong_shen.15", "比劫奪財": "yongshen.yong_shen.16", "財多身弱": "yongshen.yong_shen.17"}
_BINGYAO_EN = {
    "傷官見官": "傷官見官: sharp expression meets rules and authority, which 《淵海子平》〈論傷官〉 calls 為禍百端. The medicine is 印 ({el}): 〈傷官說〉 says 傷官見官，印運不妨.",
    "比劫奪財": "比劫奪財: peers and rivals take the wealth the chart earns (《淵海子平》〈論劫財〉). The medicine is 官殺 ({el}), the check on 比劫 (〈論陽刃〉 喜偏官七殺).",
    "財多身弱": "財多身弱: more wealth than the Day Master can carry, so it does not stay (《三命通會》卷六〈論正財〉: 財多身弱，柱無印助，皆不為福). The medicine is 印 ({el}): 身衰逢印資助."}


def _bingyao_text(by: dict, lang: str) -> str:
    if by["pattern"] is None:
        return T("yongshen.yong_shen.14", "no built-in strain found: 傷官見官, 比劫奪財 and 財多身弱 are each below the usual cut, so 病藥 adds nothing and 扶抑 stands alone", lang)
    el = ELEM(lang)[by["medicine_el"]]
    head = T(_BINGYAO_ID[by["pattern"]], _BINGYAO_EN[by["pattern"]].format(el=el), lang, el=el)
    tail = {"agrees": T("yongshen.yong_shen.18", f"Your 扶抑 reading also favours {el}, so the two readings agree.", lang, el=el),
            "parts": T("yongshen.yong_shen.19", f"Your 扶抑 reading avoids {el}, so 扶抑 leads and this medicine is a short-term aid, not a lasting choice.", lang, el=el),
            "neutral": T("yongshen.yong_shen.20", f"Your 扶抑 reading neither favours nor avoids {el}, so treat this medicine as secondary: 扶抑 leads.", lang, el=el)}[by["status"]]
    return jn([head, tail], lang, en=" ", zh="")
