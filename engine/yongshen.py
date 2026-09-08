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

WINTER, SUMMER = {"亥", "子", "丑"}, {"巳", "午", "未"}


def yong_shen(chart: Chart) -> dict:
    dm_el = STEM_ELEMENT[chart.day_master]
    weak = chart.strength["verdict"].startswith("身弱")
    officer_el = next(e for e in ELEMENTS if KE[e] == dm_el)

    if weak:
        fav = [SHENG_REV[dm_el], dm_el]           # 印 first, then 比劫
        unfav = [officer_el, KE[dm_el], SHENG[dm_el]]
        fuyi = (f"Weak Day Master: favour 印 ({ELEMENT_EN[SHENG_REV[dm_el]]}) to nourish and "
                f"比劫 ({ELEMENT_EN[dm_el]}) to support; avoid 官殺/財/食傷")
    else:
        fav = [SHENG[dm_el], KE[dm_el], officer_el]   # drain, wealth, control
        unfav = [SHENG_REV[dm_el], dm_el]
        fuyi = (f"Strong Day Master: favour 食傷 ({ELEMENT_EN[SHENG[dm_el]]}) to drain, "
                f"財 ({ELEMENT_EN[KE[dm_el]]}) and 官殺 ({ELEMENT_EN[officer_el]}); "
                f"avoid 印/比劫")

    citations = [{"rule_id": "yongshen-fuyi", "layer": "yongshen",
                  "source_ref": "扶抑法 (technique 1 of 4)", "explanation": fuyi}]

    month_branch = chart.pillars["month"].branch
    tiaohou = None
    if month_branch in WINTER and "火" not in fav:
        fav = ["火"] + fav
        tiaohou = "born in winter — chart is cold, 火 (Fire) promoted by 調候"
    elif month_branch in SUMMER and "水" not in fav:
        fav = ["水"] + fav
        tiaohou = "born in summer — chart is hot, 水 (Water) promoted by 調候"
    elif month_branch in WINTER or month_branch in SUMMER:
        tiaohou = "climatic need already satisfied by 扶抑 selection"
    citations.append({"rule_id": "yongshen-tiaohou", "layer": "yongshen",
                      "source_ref": "調候法 (technique 2 of 4)",
                      "explanation": tiaohou or f"month {month_branch}: mild season, no climatic override"})
    citations.append({"rule_id": "yongshen-bingyao", "layer": "yongshen",
                      "source_ref": "病藥法 (technique 3 of 4)",
                      "explanation": "advisory in M1 — full pillar-interaction pass planned (M4)"})
    citations.append({"rule_id": "yongshen-tongguan", "layer": "yongshen",
                      "source_ref": "通關法 (technique 4 of 4)",
                      "explanation": "advisory in M1 — applied when two camps deadlock (M4)"})

    # dedupe, keep order
    fav = list(dict.fromkeys(fav))
    unfav = [e for e in dict.fromkeys(unfav) if e not in fav]
    return {"favourable": fav, "unfavourable": unfav,
            "colours": favourable_colours(fav[:2]),
            "citations": citations}
