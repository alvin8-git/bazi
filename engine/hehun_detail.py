"""合婚 drill-down — display + remedy layer over pair_compatibility().

Spec: scratchpad hehun_spec.md v1 (2026-09-20). The 0–100 arithmetic is FROZEN
in hehun.py: everything here relabels the existing chips or adds descriptive,
unscored enrichment (four-pillar sweep, ten-god gloss, remedies, framings).
Citations per rule; MODERN SYNTHESIS marked where a mapping is ours.
"""
from __future__ import annotations

from .bazi import ten_god
from .hehun import WUHE, _branch_rel, pair_compatibility
from .wuxing import BRANCH_ELEMENT, ELEMENT_EN

PALACES = ("year", "month", "day", "hour")
PALACE_ZH = {"year": ("年柱", "祖辈根基", "elders & family roots"),
             "month": ("月柱", "事业父母", "career & parents"),
             "day": ("日柱", "自身配偶", "self & spouse palace"),
             "hour": ("时柱", "子女晚年", "children & later years")}
REL_GLOSS = {"六合": ("牵引相吸", "draws together"),
             "半三合": ("气场相近", "kindred current"),
             "六沖": ("骤然冲击", "abrupt friction"),
             "刑": ("暗中角力", "hidden power struggle"),
             "六害": ("悄然耗损", "quiet drain")}

# §2c — how A experiences B's Day Master (all ten gods)
TG_SEES = {
    "比肩": ("对等的自己人——彼此尊重，但也可能争夺同一份资源",
           "A peer and equal — mutual respect, with some rivalry over shared resources"),
    "劫財": ("大胆的对手——带来冲劲，也可能牵动共同财物",
           "A bold rival — energising, but can pull at shared resources"),
    "食神": ("温和的出口——享受与滋养，相处轻松愉快",
           "A gentle outlet — nurture and easy-going enjoyment"),
    "傷官": ("锋芒的挑战者——激发创意，也会挑战既有规矩",
           "A brilliant challenger — sparks creativity but needles the rules"),
    "偏財": ("意外的机遇——带来慷慨与生意眼光，较不稳定",
           "A windfall — opportunity and generosity, less predictable"),
    "正財": ("稳当的供给——踏实可靠的照顾与理财",
           "Steady provision — dependable, grounding practical care"),
    "七殺": ("外来的压力——逼人表现，也可能感到被掌控",
           "Raw pressure — pushes performance, can feel controlling"),
    "正官": ("端正的秩序——令人负责任，带来地位感",
           "Proper structure — keeps one accountable, brings status"),
    "偏印": ("另类的导师——直觉、私密，传授小众本领",
           "An unconventional mentor — intuitive, private, teaches niche skill"),
    "正印": ("定心的靠山——滋养、保护，稳定人心",
           "Steadying mentor energy — nurturing and protective"),
}

# §2a — positive-chip expansions (display only)
STRENGTH_EXPL = {
    "day六合": ("日支相合如锁扣相接，夫妻宫自然相吸——生活习惯、亲密与默契天生契合",
              "The day branches (spouse palaces) lock together — naturally aligned "
              "habits, intimacy and rapport", "淵海子平《论支合》"),
    "day半三合": ("两人日支同属一个三合局，气场相近，夫妻宫互相扶持",
               "Day branches share a trine group — a kindred current reinforcing "
               "both spouse palaces", "淵海子平《三合局》"),
    "五合": ("日干相合，两人本命日主彼此吸引、志趣相投——合婚中仅次于日支的经典指标",
           "Day stems combine (五合) — each core self is drawn to the other; the "
           "classic second-tier 合婚 signal", "三命通會《论十干配合》"),
    "year合": ("年柱主祖辈根基，年支相合代表两家背景、成长节奏合拍，长辈易相处",
             "Year branches combine — family roots and upbringing rhythms align; "
             "elders tend to get along", "民间合婚歌诀"),
    "supply": ("一方五行充沛，恰是对方八字所需的用神——同住同色即有扶持之效",
             "One person is rich in an element the other's chart needs — everyday "
             "proximity in that element is naturally supportive",
             "用神 classical 子平法; cross-chart supply MODERN SYNTHESIS"),
}

# §3a — 六沖 bridged by 通關 (三命通會〈论刑冲会合〉)
CHONG_BRIDGE = {
    frozenset("子午"): ("木", "水生木，木生火——以木通關化解对冲",
                     "wood carries water's energy into fire instead of a head-on clash",
                     "green/teal, timber furniture, shared plants", "E/SE 震巽"),
    frozenset("丑未"): ("金", "土生金——以金洩土，化解僵持",
                     "metal drains the earth stalemate outward",
                     "white/metal accents, round metal objects", "NW/W 乾兌"),
    frozenset("寅申"): ("水", "金生水，水生木——以水通關",
                     "water carries metal's force into wood",
                     "black/blue, a water feature", "N 坎"),
    frozenset("卯酉"): ("水", "金生水，水生木——以水通關",
                     "water carries metal's force into wood",
                     "black/blue, a water feature", "N 坎"),
    frozenset("辰戌"): ("金", "土生金——以金洩土", "metal drains the earth stalemate",
                     "white/metal accents", "NW/W 乾兌"),
    frozenset("巳亥"): ("木", "水生木，木生火——以木通關",
                     "wood bridges water and fire", "green, timber, plants", "E/SE 震巽"),
}

# §3b — 刑 (三命通會〈论三刑〉; element remedy MODERN SYNTHESIS)
XING_GROUPS = [
    (frozenset("寅巳申"), "恃势之刑", "水", "水制巳火、生寅木，打断循环相克",
     "water interrupts the power-reliance loop",
     "轮流主导重大决定 take turns leading ambition-driven decisions"),
    (frozenset("丑戌未"), "无恩之刑", "金", "金洩僵持之土",
     "metal drains the stalemated triple earth",
     "共同约定写成白纸黑字 put shared agreements in writing"),
    (frozenset("子卯"), "无礼之刑", "火", "火微洩过旺之木气，缓和唐突",
     "fire gently drains the excess wood, softening abruptness",
     "先调语气，再谈内容 coach on tone before content"),
]
SELF_XING_KE = {"辰": "木", "午": "水", "酉": "火", "亥": "土"}

# §3c — 六害 fixed by 合化解 (淵海子平〈论六害〉; element pick MODERN SYNTHESIS)
HAI_FIX = {
    frozenset("子未"): ("土/火", "补回被扰的丑或午之合"),
    frozenset("丑午"): ("水/土", "补回被扰的子或未之合"),
    frozenset("寅巳"): ("水/金", "补回被扰的亥或申之合"),
    frozenset("卯辰"): ("土/金", "补回被扰的戌或酉之合"),
    frozenset("申亥"): ("火/木", "补回被扰的巳或寅之合"),
    frozenset("酉戌"): ("土/木", "补回被扰的辰或卯之合"),
}

# §3d — dominant-avoided lever (克/洩; colour mapping MODERN SYNTHESIS)
AVOID_LEVER = {
    "木": "metal accents or warm-toned lighting instead of green",
    "火": "blue/black accents or earthy neutrals instead of red",
    "土": "green accents or white/metal instead of yellow/brown",
    "金": "red/purple accents or black/blue instead of white",
    "水": "yellow/brown accents or green instead of black/blue",
}

# §3e — behavioural strategy by (relation, pillar)
BEHAVIOUR = {
    ("六沖", "day"): ("情感 Emotional display · 行动 Action",
        "把大反应放慢半拍——冲突别变成当场的决定",
        "Pace big reactions; don't let a clash become a snap decision."),
    ("六沖", "year"): ("权威 Authority stance",
        "家规传统各有默认值——明说家里的规则，别靠假设",
        "Agree explicit house rules rather than assuming shared family defaults."),
    ("刑", "day"): ("表达 Expression · 情感 Emotional display",
        "暗劲在沉默里累积——定期直接沟通，别让摩擦攒着",
        "Hidden entanglement builds under silence — schedule regular direct check-ins."),
    ("刑", "year"): ("权威 Authority stance",
        "长辈事务先说清谁定什么，免得反复",
        "Settle explicitly who decides what in extended-family matters."),
    ("六害", "day"): ("思维 Thinking style",
        "耗损常来自思路错位——把计划翻译成对方的语言",
        "Translate plans between reflective and pragmatic styles; don't assume shared logic."),
    ("六害", "year"): ("表达 Expression",
        "与亲族沟通时，把背景讲透，宁多勿省",
        "Over-communicate context with extended family; assumptions are the drain."),
}

# §4 — framings keyed off the band
FRAMING = {
    "上等": {"family": ("相处自然合拍，家庭氛围融洽", "Naturally in sync — an easy household rhythm"),
           "couple": ("夫妻宫呼应，感情基础稳固", "Spouse palaces resonate — a solid emotional foundation"),
           "colleagues": ("默契佳，适合长期合作项目", "Strong rapport — suited to long-run projects")},
    "中上": {"family": ("大方向一致，小习惯可磨合", "Aligned on the big things; small habits need adjusting"),
           "couple": ("感情有基础，仍需用心经营", "A real foundation — still worth active tending"),
           "colleagues": ("合作顺畅，分工清楚即可", "Smooth collaboration once roles are clear")},
    "中": {"family": ("需要主动沟通维系关系", "Needs deliberate communication to stay close"),
          "couple": ("需磨合，建议明确沟通节奏", "Needs active work — agree a communication rhythm"),
          "colleagues": ("可共事，建议书面约定分工", "Workable — put role division in writing")},
    "需磨合": {"family": ("差异明显，建议长辈或顾问协助沟通", "Clear differences — a third party can help bridge"),
            "couple": ("需要认真经营，必要时寻求咨询", "Needs serious effort — consider counselling if pursuing marriage"),
            "colleagues": ("合作前先明确边界与退出机制", "Set boundaries and an exit plan before committing")},
}
_BAND_KEY = lambda s: ("上等" if s >= 70 else "中上" if s >= 55 else
                       "中" if s >= 45 else "需磨合")
_BAND_EN = {"上等": "Very compatible", "中上": "Compatible",
            "中": "Workable", "需磨合": "Needs effort"}

_REL_PTS = {"day": {"六合": 15, "半三合": 10, "六沖": -15, "刑": -8, "六害": -8},
            "year": {"六合": 8, "半三合": 8, "六沖": -8, "刑": -4, "六害": -4}}


def _bi(zh, en):
    return {"zh": zh, "en": en}


def _friction(kind, pillar, ba, bb, na, nb):
    """Remedy block for one scored negative chip (§3)."""
    pz = PALACE_ZH[pillar][0]
    if kind == "六沖":
        el, zh_w, en_w, mat, dr = CHONG_BRIDGE[frozenset((ba, bb))]
        mech, cite = "通關", "三命通會〈论刑冲会合〉通關法"
        elem = {"zh": el, "en": ELEMENT_EN[el], "why": _bi(zh_w, en_w),
                "colour_material": mat, "direction": dr}
    elif kind == "刑":
        if ba == bb:
            el = SELF_XING_KE.get(ba, "")
            mech, cite = "克洩", "三命通會〈论三刑〉自刑; remedy MODERN SYNTHESIS"
            elem = {"zh": el, "en": ELEMENT_EN.get(el, ""), "why": _bi(
                "自刑之郁在己不在人——以其克制元素安顿本人空间",
                "self-刑 friction is internal, projected onto the pair — the "
                "controlling element goes in that person's own space"),
                "colour_material": "", "direction": ""}
        else:
            grp = next((g for g in XING_GROUPS if {ba, bb} <= g[0]), None)
            name, el, zh_w, en_w, note = (grp[1], grp[2], grp[3], grp[4], grp[5]) \
                if grp else ("刑", "", "", "", "")
            mech, cite = "洩/克", "三命通會〈论三刑〉; element remedy MODERN SYNTHESIS"
            elem = {"zh": el, "en": ELEMENT_EN.get(el, ""),
                    "why": _bi(f"{name}：{zh_w}", en_w),
                    "colour_material": note, "direction": ""}
    else:  # 六害
        el, zh_w = HAI_FIX[frozenset((ba, bb))]
        mech, cite = "合化解", "淵海子平〈论六害〉; element pick MODERN SYNTHESIS"
        elem = {"zh": el, "en": "/".join(ELEMENT_EN.get(e, e) for e in el.split("/")),
                "why": _bi(zh_w + "——择两人共同用神所喜的一边",
                           "restore the disrupted 六合 partner — pick the side the "
                           "pair's shared 用神 favours"),
                "colour_material": "", "direction": ""}
    ax, bzh, ben = BEHAVIOUR[(kind, pillar)]
    return {"mechanism": mech, "source_ref": cite,
            "element": elem,
            "behaviour": {"axis": ax, "zh": bzh, "en": ben},
            "timing": _bi(f"逢{ba}年或{bb}年，避免签订重大共同决定（伏吟/反吟再触此{kind}）",
                          f"avoid initiating major joint decisions in {ba} or {bb} "
                          f"years — the 太岁 re-triggers this {kind}")}


def pair_breakdown(ca, cb, ys_a, ys_b) -> dict:
    """The drawer payload: pass-through score + bilingual ledger + enrichment.
    The ledger re-derives the SAME rules as pair_compatibility() so the sum is
    guaranteed to reconcile (pinned by test)."""
    base = pair_compatibility(ca, cb, ys_a, ys_b)
    na, nb = ca.person, cb.person
    da, db = ca.pillars["day"], cb.pillars["day"]
    ledger, strengths, frictions = [], [], []

    def add(zh, en, delta, pillars, skind=None, fr=None):
        row = {"label": _bi(zh, en), "delta": delta, "pillars": pillars}
        ledger.append(row)
        if delta > 0 and skind:
            z, e, cite = STRENGTH_EXPL[skind]
            strengths.append({"chip_label": row["label"], "delta": delta,
                              "explanation": _bi(z, e), "source_ref": cite})
        if delta < 0 and fr:
            frictions.append({"chip_label": row["label"], "delta": delta,
                              "pillars": pillars, **fr})

    rel = _branch_rel(da.branch, db.branch)
    if rel is None:
        add("日支中性", "day branches neutral", 0, "day-day")
    else:
        kind, _ = rel
        pts = _REL_PTS["day"][kind]
        add(f"日支{kind} {da.branch}{db.branch}（夫妻宫）",
            f"day branches {da.branch}{db.branch} {kind} (spouse palaces)",
            pts, "day-day",
            skind=("day" + kind) if pts > 0 else None,
            fr=_friction(kind, "day", da.branch, db.branch, na, nb) if pts < 0 else None)
    if WUHE.get(da.stem) == db.stem:
        add(f"日干五合 {da.stem}{db.stem}", f"day stems {da.stem}{db.stem} bond (五合)",
            10, "day-day", skind="五合")
    ya, yb = ca.pillars["year"].branch, cb.pillars["year"].branch
    yrel = _branch_rel(ya, yb)
    if yrel:
        kind, _ = yrel
        pts = _REL_PTS["year"][kind]
        add(f"年支(生肖){kind} {ya}{yb}", f"year branches (zodiac) {kind}",
            pts, "year-year",
            skind="year合" if pts > 0 else None,
            fr=_friction(kind, "year", ya, yb, na, nb) if pts < 0 else None)
    wa, wb = ca.element_weights, cb.element_weights
    ta, tb = sum(wa.values()) or 1, sum(wb.values()) or 1
    for giver, gw, gt, taker, tys in ((ca, wa, ta, cb, ys_b), (cb, wb, tb, ca, ys_a)):
        n = 0
        for e in tys["favourable"]:
            if gw.get(e, 0) / gt >= 0.2 and n < 2:
                add(f"{giver.person}五行{e}旺，补{taker.person}所需",
                    f"{giver.person} is rich in {ELEMENT_EN[e]}{e} — an element "
                    f"{taker.person} needs", 6, "chart-wide", skind="supply")
                n += 1
        dom = max(gw, key=gw.get)
        if dom in tys["unfavourable"]:
            add(f"{giver.person}主气{dom}为{taker.person}所忌",
                f"{giver.person}'s dominant {ELEMENT_EN[dom]}{dom} is an element "
                f"{taker.person} avoids", -6, "chart-wide",
                fr={"mechanism": "克/洩",
                    "source_ref": "用神扶抑 (三命通會); lever MODERN SYNTHESIS",
                    "element": {"zh": dom, "en": ELEMENT_EN[dom],
                                "why": _bi("以其克/洩元素调和共处环境",
                                           "mute the surplus via its control/drain element"),
                                "colour_material": AVOID_LEVER[dom], "direction": ""},
                    "behaviour": {"axis": "环境 environment",
                                  "zh": f"共处空间少用{dom}色系，多用{taker.person}的用神色",
                                  "en": f"in shared spaces, lean toward {taker.person}'s "
                                        "favourable palette rather than the surplus element"},
                    "timing": _bi("——", "—")})

    # §2b descriptive sweep — never summed
    sweep = []
    for pa in PALACES:
        for pb in PALACES:
            r = _branch_rel(ca.pillars[pa].branch, cb.pillars[pb].branch)
            if not r:
                continue
            kind, _ = r
            gz, ge = REL_GLOSS[kind]
            sweep.append({
                "pillar_a": pa, "pillar_b": pb,
                "branch_a": ca.pillars[pa].branch, "branch_b": cb.pillars[pb].branch,
                "relation": _bi(kind, ge),
                "already_scored": (pa == pb == "day") or (pa == pb == "year"),
                "meaning": _bi(
                    f"{na}的{PALACE_ZH[pa][1]}遇{nb}的{PALACE_ZH[pb][1]}——{gz}",
                    f"{na}'s {PALACE_ZH[pa][2]} meets {nb}'s {PALACE_ZH[pb][2]} — {ge}")})

    g_ab, g_ba = base["relation"]["a_sees_b"], base["relation"]["b_sees_a"]
    band_zh = _BAND_KEY(base["score"])
    fr = FRAMING[band_zh]
    return {"a": na, "b": nb, "score": base["score"],
            "band": _bi(band_zh, _BAND_EN[band_zh]),
            "day_pillars": base["day_pillars"],
            "arithmetic": ledger,
            "pillar_sweep": sweep,
            "relation": {"a_sees_b": {"god": g_ab, **_bi(*TG_SEES[g_ab])},
                         "b_sees_a": {"god": g_ba, **_bi(*TG_SEES[g_ba])}},
            "strengths": strengths, "frictions": frictions,
            "framing": {k: _bi(*fr[k]) for k in ("family", "couple", "colleagues")},
            "source_ref": base["source_ref"]}
