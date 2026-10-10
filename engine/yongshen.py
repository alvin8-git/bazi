"""用神 determination — the four classical techniques as ordered, cited passes.

Imperial Harvest parity: 扶抑 (support/suppress), 調候 (climatic), 病藥
(sickness/remedy), 通關 (bridging). M1 implements 扶抑 fully and 調候 as a
seasonal adjustment; 病藥/通關 are emitted as advisory notes.
ponytail: 病藥/通關 need pillar-interaction analysis — upgrade in M4 if a
verified chart disagrees with the 扶抑+調候 verdict.
"""
from __future__ import annotations

from .bazi import Chart, favourable_colours
from .wuxing import (BRANCH_ELEMENT, ELEMENT_EN, ELEMENTS, KE, SHENG,
                     SHENG_REV, STEM_ELEMENT)
from .i18n import ELEM, L, T, and_l, cap, dot, jn, zs  # noqa: F401

WINTER, SUMMER = {"亥", "子", "丑"}, {"巳", "午", "未"}


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
    citations.append({"rule_id": "yongshen-bingyao", "layer": "yongshen",
                      "source_ref": T("yongshen.yong_shen.09", "病藥法 (technique 3 of 4)", lang),
                      "explanation": T("yongshen.yong_shen.10", "advisory in M1 — full pillar-interaction pass planned (M4)", lang)})
    citations.append({"rule_id": "yongshen-tongguan", "layer": "yongshen",
                      "source_ref": T("yongshen.yong_shen.11", "通關法 (technique 4 of 4)", lang),
                      "explanation": T("yongshen.yong_shen.12", "advisory in M1 — applied when two camps deadlock (M4)", lang)})

    # dedupe, keep order
    fav = list(dict.fromkeys(fav))
    unfav = [e for e in dict.fromkeys(unfav) if e not in fav]
    return {"favourable": fav, "unfavourable": unfav,
            "colours": favourable_colours(fav[:2]),
            "citations": citations}
