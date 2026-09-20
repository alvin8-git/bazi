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

# §2c — how A experiences B's Day Master (all ten gods; EN = natural gloss)
TG_SEES = {
    "比肩": ("对等的自己人——彼此尊重，但也可能争夺同一份资源",
           "Feels like an equal and an ally — genuine mutual respect, though they may "
           "find themselves competing for the same things"),
    "劫財": ("大胆的对手——带来冲劲，也可能牵动共同财物",
           "Feels like a daring sparring partner — brings out drive and boldness, but "
           "keep shared money matters clearly separated"),
    "食神": ("温和的出口——享受与滋养，相处轻松愉快",
           "Feels like good company — someone easy to relax, eat well and laugh with; "
           "time together is naturally restorative"),
    "傷官": ("锋芒的挑战者——激发创意，也会挑战既有规矩",
           "Feels like a sharp-witted provocateur — sparks fresh ideas, but will also "
           "poke at rules and routines the other holds dear"),
    "偏財": ("意外的机遇——带来慷慨与生意眼光，较不稳定",
           "Feels like a lucky break — generous, opportunity-minded and fun, though "
           "not the person to rely on for steadiness"),
    "正財": ("稳当的供给——踏实可靠的照顾与理财",
           "Feels like a safe pair of hands — practical care, reliability, and someone "
           "who keeps the household finances sensible"),
    "七殺": ("外来的压力——逼人表现，也可能感到被掌控",
           "Feels like pressure to perform — this presence raises the other's game, "
           "but can tip into feeling controlled if unspoken"),
    "正官": ("端正的秩序——令人负责任，带来地位感",
           "Feels like a standard to live up to — brings structure, accountability "
           "and a sense of standing in the world"),
    "偏印": ("另类的导师——直觉、私密，传授小众本领",
           "Feels like an unconventional mentor — intuitive and private, opening "
           "doors to skills and ideas off the beaten path"),
    "正印": ("定心的靠山——滋养、保护，稳定人心",
           "Feels like a steadying anchor — protective and nurturing; being around "
           "them simply makes things feel more settled"),
}

# §2a — positive-chip expansions (display only): zh, en, cite, action{zh,en}
STRENGTH_EXPL = {
    "day六合": ("日支相合如锁扣相接，夫妻宫自然相吸——生活习惯、亲密与默契天生契合",
              "Their day branches — the 'spouse palaces', the most intimate seat in "
              "each chart — lock together like matched clasps. Daily habits, affection "
              "and unspoken understanding tend to line up on their own.",
              "淵海子平《论支合》",
              ("多安排两人独处的日常仪式，让默契自然生长",
               "Protect small everyday rituals for just the two of them — the natural "
               "rapport does the rest.")),
    "day半三合": ("两人日支同属一个三合局，气场相近，夫妻宫互相扶持",
               "Their day branches belong to the same harmony trio (三合) — not a "
               "full lock, but a shared current that steadies both spouse palaces.",
               "淵海子平《三合局》",
               ("共同的目标最能放大这股同频之气",
                "Give this same-frequency current something to work on — shared goals "
                "and projects amplify it.")),
    "五合": ("日干相合，两人本命日主彼此吸引、志趣相投——合婚中仅次于日支的经典指标",
           "Their Day Masters — the core selves — form the classic stem bond (五合): "
           "each is instinctively drawn to how the other thinks and operates.",
           "三命通會《论十干配合》",
           ("重大决定两人同商，互补的视角最见效",
            "Make the big decisions together — the pull between their two styles is "
            "exactly where this bond pays off.")),
    "year合": ("年柱主祖辈根基，年支相合代表两家背景、成长节奏合拍，长辈易相处",
             "Their year branches — the zodiac layer that rules family roots — "
             "combine: upbringings mesh easily and the elders on both sides tend "
             "to approve.",
             "民间合婚歌诀",
             ("多创造两家人同场的机会",
              "Bring the two families into the same room often — this bond works "
              "best in person.")),
}
# per-element palette words for the dynamic supply/avoid sentences
EL_PALETTE = {"木": "greens and natural wood", "火": "warm reds and soft lighting",
              "土": "earth tones and ceramics", "金": "whites and metal accents",
              "水": "deep blues and flowing forms"}

# §3a — 六沖 bridged by 通關 (三命通會〈论刑冲会合〉)
CHONG_BRIDGE = {
    frozenset("子午"): ("木", "水生木，木生火——以木通關化解对冲",
                     "wood stands between water and fire, turning a head-on collision "
                     "into a flow (通關, 'bridging')",
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
    "上等": {"family": ("相处自然合拍，家庭氛围融洽", "Life under one roof comes easily — the household finds its rhythm without effort"),
           "couple": ("夫妻宫呼应，感情基础稳固", "The spouse palaces answer each other — this is a naturally solid foundation to build on"),
           "colleagues": ("默契佳，适合长期合作项目", "Rapport comes built-in — a pairing worth trusting with long-running projects")},
    "中上": {"family": ("大方向一致，小习惯可磨合", "Aligned where it counts; the small daily habits just need a little adjusting"),
           "couple": ("感情有基础，仍需用心经营", "There is real substance here — it rewards deliberate, ongoing care"),
           "colleagues": ("合作顺畅，分工清楚即可", "Collaboration flows well once each person's lane is clearly marked")},
    "中": {"family": ("需要主动沟通维系关系", "Closeness won't happen by default — it takes deliberate, regular communication"),
          "couple": ("需磨合，建议明确沟通节奏", "Workable with effort — agree on how and when you talk things through"),
          "colleagues": ("可共事，建议书面约定分工", "Fine to work together — just put the division of duties in writing")},
    "需磨合": {"family": ("差异明显，建议长辈或顾问协助沟通", "The differences are real — a trusted elder or advisor helps bridge the gap"),
            "couple": ("需要认真经营，必要时寻求咨询", "This pairing asks for serious commitment — professional guidance is worth it if marriage is the goal"),
            "colleagues": ("合作前先明确边界与退出机制", "Agree on boundaries — and an exit plan — before committing to anything big")},
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
                          f"Treat {ba} and {bb} years as poor timing for weddings, big "
                          f"purchases or joint signings — the year's ruling branch "
                          f"re-ignites this {kind}.")}


def pair_breakdown(ca, cb, ys_a, ys_b) -> dict:
    """The drawer payload: pass-through score + bilingual ledger + enrichment.
    The ledger re-derives the SAME rules as pair_compatibility() so the sum is
    guaranteed to reconcile (pinned by test)."""
    base = pair_compatibility(ca, cb, ys_a, ys_b)
    na, nb = ca.person, cb.person
    da, db = ca.pillars["day"], cb.pillars["day"]
    ledger, strengths, frictions = [], [], []

    def add(zh, en, delta, pillars, skind=None, fr=None, sdyn=None, element=None):
        row = {"label": _bi(zh, en), "delta": delta, "pillars": pillars}
        if element:
            row["element"] = element
        ledger.append(row)
        if delta > 0 and skind:
            z, e, cite, (az, ae) = STRENGTH_EXPL[skind]
            strengths.append({"chip_label": row["label"], "delta": delta,
                              "explanation": _bi(z, e), "action": _bi(az, ae),
                              "source_ref": cite})
        if delta > 0 and sdyn:
            strengths.append({"chip_label": row["label"], "delta": delta, **sdyn})
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
                    f"{giver.person} carries plenty of the {ELEMENT_EN[e]} that "
                    f"{taker.person}'s chart runs short of", 6, "chart-wide",
                    element=e, sdyn={
                        "explanation": _bi(
                            "一方五行充沛，恰是对方八字所需的用神——同住同色即有扶持之效",
                            f"{giver.person} naturally supplies the {ELEMENT_EN[e]} "
                            f"that {taker.person}'s chart is short of — simply "
                            f"spending time together, in spaces that lean toward "
                            f"{EL_PALETTE[e]}, quietly works in {taker.person}'s favour."),
                        "action": _bi(
                            f"共处空间多用{e}系配色，多安排共同活动即可",
                            f"Lean shared rooms toward {EL_PALETTE[e]}, and let "
                            f"{taker.person} spend unhurried time in "
                            f"{giver.person}'s company."),
                        "source_ref": "用神 classical 子平法; cross-chart supply "
                                      "MODERN SYNTHESIS"})
                n += 1
        dom = max(gw, key=gw.get)
        if dom in tys["unfavourable"]:
            add(f"{giver.person}主气{dom}为{taker.person}所忌",
                f"{giver.person}'s strongest element, {ELEMENT_EN[dom]}, is one "
                f"{taker.person}'s chart works against", -6, "chart-wide",
                element=dom,
                fr={"mechanism": "克/洩",
                    "source_ref": "用神扶抑 (三命通會); lever MODERN SYNTHESIS",
                    "element": {"zh": dom, "en": ELEMENT_EN[dom],
                                "why": _bi("以其克/洩元素调和共处环境",
                                           f"soften the surplus {ELEMENT_EN[dom]} in "
                                           "shared spaces with its counter-element"),
                                "colour_material": AVOID_LEVER[dom], "direction": ""},
                    "behaviour": {"axis": "环境 environment",
                                  "zh": f"共处空间少用{dom}色系，多用{taker.person}的用神色",
                                  "en": f"Decorate shared spaces in {taker.person}'s "
                                        f"favourable palette rather than more "
                                        f"{ELEMENT_EN[dom]} tones."},
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
