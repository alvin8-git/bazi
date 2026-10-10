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
PALACE_ZH = {"year": ("年柱", "祖辈根基", "elders and family roots"),
             "month": ("月柱", "事业父母", "career and parents"),
             "day": ("日柱", "自身配偶", "self (and partner, for couples)"),
             "hour": ("时柱", "子女晚年", "children and later years")}
# child / teen wording: no partner or spouse framing
PALACE_EN_KID = {"day": "self"}
from .hehun import KIND_EN, relation_additions  # noqa: E402  (batch 2 rows live beside the score)


def _pal_en(p: str, kid: bool = False) -> str:
    return PALACE_EN_KID.get(p, PALACE_ZH[p][2]) if kid else PALACE_ZH[p][2]


def _age_on(birth, today=None) -> int:
    """Whole years on today's date (a birthday not yet reached this year counts one less)."""
    import datetime as _dt
    today = today or _dt.date.today()
    b = birth.date() if hasattr(birth, "date") else birth
    return today.year - b.year - ((today.month, today.day) < (b.month, b.day))


def _voice(ages) -> str:
    y = min(ages)
    return "child" if y < 13 else "teen" if y < 18 else "adult"


REL_GLOSS = {"六合": ("牵引相吸", "draws together"),
             "半三合": ("气场相近", "shared current"),
             "六沖": ("骤然冲击", "sudden friction"),
             "刑": ("暗中角力", "a hidden tug of wills"),
             "六害": ("悄然耗损", "a quiet drain")}

# §2c — how A experiences B's Day Master (all ten gods; EN = natural gloss)
TG_SEES = {
    "比肩": ("对等的自己人——彼此尊重，但也可能争夺同一份资源",
           "Feels like an equal and an ally. There is real mutual respect, and some "
           "chance of competing for the same things."),
    "劫財": ("大胆的对手——带来冲劲，也可能牵动共同财物",
           "Feels like a bold sparring partner. They bring drive and courage; keep "
           "shared money clearly separate."),
    "食神": ("温和的出口——享受与滋养，相处轻松愉快",
           "Feels like good company: easy to relax, eat well and laugh with. Time "
           "together is naturally restful."),
    "傷官": ("锋芒的挑战者——激发创意，也会挑战既有规矩",
           "Feels like a sharp, witty challenger. They spark fresh ideas and will also "
           "poke at rules and routines the other person values."),
    "偏財": ("意外的机遇——带来慷慨与生意眼光，较不稳定",
           "Feels like a lucky break: generous, fun and quick to spot opportunities, "
           "but not the one to rely on for steadiness."),
    "正財": ("稳当的供给——踏实可靠的照顾与理财",
           "Feels like a safe pair of hands: practical, reliable, and good at keeping "
           "money sensible."),
    "七殺": ("外来的压力——逼人表现，也可能感到被掌控",
           "Feels like pressure to perform. They raise the other person's game, but it "
           "can start to feel controlling if nobody says so."),
    "正官": ("端正的秩序——令人负责任，带来地位感",
           "Feels like a standard to live up to. They bring structure, responsibility "
           "and a sense of standing."),
    "偏印": ("另类的导师——直觉、私密，传授小众本领",
           "Feels like an unconventional mentor: intuitive, private, and a door to "
           "unusual skills and ideas."),
    "正印": ("定心的靠山——滋养、保护，稳定人心",
           "Feels like a steady anchor: protective and caring. Being around them makes "
           "things feel more settled."),
}

# §2c′ (2026-09-27) — the same ten relations read in a modern setting:
# (home zh, home en, work zh, work en). MODERN SYNTHESIS — glosses, not scoring.
TG_MODERN = {
    "比肩": ("像室友般平等——分工要说清，否则两人都以为对方会做", "At home: equals, like flatmates. Split chores out loud, or each will assume the other has it.",
           "同级搭档，各有一摊——最怕抢同一个功劳", "At work: peers with their own lanes. The one risk is competing for the same credit."),
    "劫財": ("热闹又冲动的伴——钱和承诺分开管", "At home: lively and impulsive. Keep money and promises separate.",
           "敢闯的同事，适合开局——别让他们碰共同预算", "At work: a bold starter, like a co-founder. Keep them away from the shared budget."),
    "食神": ("轻松的伴侣，饭桌上最好——容易舒服到不做规划", "At home: easygoing and restful, best over a meal. It can be so comfortable that planning slips.",
           "创意与产品感强的同事——需要有人收尾", "At work: strong on taste and product sense. Pair them with someone who finishes things."),
    "傷官": ("会挑战你习惯的伴侣——新鲜但费神", "At home: someone who questions your habits. Refreshing, and tiring.",
           "敢说真话的同事——最好的评审，最差的执行者", "At work: an honest critic. Your best reviewer, and the least likely to follow rules."),
    "偏財": ("慷慨、爱玩的伴侣——不靠他们守家", "At home: generous and fun, but not the one who keeps the house running.",
           "会找机会的同事，适合业务开拓——签合同前再核一遍", "At work: spots opportunities and is good for deals. Re-read the contract before signing."),
    "正財": ("踏实的照顾者——账目清楚、生活稳", "At home: steady and caring. Bills get paid and routines get kept.",
           "可靠的执行者——交付准时，但不爱冒险", "At work: dependable. Delivers on time and avoids risk."),
    "七殺": ("推着你成长的伴侣——压力若不说破会变成控制", "At home: someone who pushes you to act. The pressure can turn into control if nobody says so.",
           "高要求的上级或对手——让你清醒，也让你累", "At work: a demanding boss or rival. Clarifying and exhausting in equal measure."),
    "正官": ("讲规矩的伴侣——家有秩序，惊喜少", "At home: the rule-keeper. Order at home, fewer surprises.",
           "守流程的同事——合规与稳定的保证", "At work: the process person. Your guarantee of compliance and stability."),
    "偏印": ("私密而直觉的伴侣——需要独处，也需要被理解", "At home: private and intuitive. Needs time alone, and needs to be understood.",
           "另辟蹊径的专家——专项问题找他们，日常汇报别指望", "At work: a niche specialist. Go to them for the hard problem, not the weekly update."),
    "正印": ("让人安心的伴侣——照顾周到，偶尔过度保护", "At home: steadying and attentive, sometimes over-protective.",
           "耐心的导师型同事——培养人，但决策慢", "At work: a patient mentor who grows people but decides slowly."),
}

# §2a — positive-chip expansions (display only): zh, en, cite, action{zh,en}
STRENGTH_EXPL = {
    "day六合": ("日支相合如锁扣相接，夫妻宫自然相吸——生活习惯、亲密与默契天生契合",
              "Their day branches, the most personal part of each chart, fit together "
              "like matched clasps. Daily habits, affection and unspoken understanding "
              "tend to line up on their own.",
              "淵海子平《论支合》",
              ("多安排两人独处的日常仪式，让默契自然生长",
               "Keep a few small daily rituals for just the two of them. The natural "
               "rapport does the rest.")),
    "day半三合": ("两人日支同属一个三合局，气场相近，夫妻宫互相扶持",
               "Their day branches sit in the same three-way group, called Three Harmony "
               "(三合). It is not a full lock, but it is a shared current that steadies both.",
               "淵海子平《三合局》",
               ("共同的目标最能放大这股同频之气",
                "Give this shared current something to work on. Common goals and "
                "projects make it stronger.")),
    "五合": ("日干相合，两人本命日主彼此吸引、志趣相投——合婚中仅次于日支的经典指标",
           "Their Day Masters, the core self of each chart, form a classic pairing "
           "called Five Combination (五合). Each is drawn to how the other thinks and works.",
           "三命通會《论十干配合》",
           ("重大决定两人同商，互补的视角最见效",
            "Make big decisions together. This bond pays off where their two styles meet.")),
    "year合": ("年柱主祖辈根基，年支相合代表两家背景、成长节奏合拍，长辈易相处",
             "Their year branches, the zodiac layer tied to family roots, combine well. "
             "Upbringings mesh easily, and the elders on both sides tend to approve.",
             "民间合婚歌诀",
             ("多创造两家人同场的机会",
              "Bring the two families together often. This bond works best in person.")),
}
# per-element palette words for the dynamic supply/avoid sentences
EL_PALETTE = {"木": "greens and natural wood", "火": "warm reds and soft lighting",
              "土": "earth tones and ceramics", "金": "whites and metal accents",
              "水": "deep blues and flowing forms"}

# §3a — 六沖 bridged by 通關 (三命通會〈论刑冲会合〉)
CHONG_BRIDGE = {
    frozenset("子午"): ("木", "水生木，木生火——以木通關化解对冲",
                     "Wood sits between water and fire and turns a head-on clash into a "
                     "flow. The classical name is Bridging (通關).",
                     "green or teal, timber furniture, shared plants", "east or southeast"),
    frozenset("丑未"): ("金", "土生金——以金洩土，化解僵持",
                     "Metal drains the stuck earth energy outward.",
                     "white or metal accents, round metal objects", "northwest or west"),
    frozenset("寅申"): ("水", "金生水，水生木——以水通關",
                     "Water carries metal's force into wood.",
                     "black or blue, a water feature", "north"),
    frozenset("卯酉"): ("水", "金生水，水生木——以水通關",
                     "Water carries metal's force into wood.",
                     "black or blue, a water feature", "north"),
    frozenset("辰戌"): ("金", "土生金——以金洩土", "Metal drains the stuck earth energy.",
                     "white or metal accents", "northwest or west"),
    frozenset("巳亥"): ("木", "水生木，木生火——以木通關",
                     "Wood bridges water and fire.", "green, timber, plants", "east or southeast"),
}

# §3b — 刑 (三命通會〈论三刑〉; element remedy MODERN SYNTHESIS)
# last item: (English note, Chinese note)
XING_GROUPS = [
    (frozenset("寅巳申"), "恃势之刑", "水", "水制巳火、生寅木，打断循环相克",
     "Water interrupts the cycle of leaning on power.",
     ("Take turns leading the decisions that involve ambition.", "轮流主导重大决定")),
    (frozenset("丑戌未"), "无恩之刑", "金", "金洩僵持之土",
     "Metal drains the stuck earth energy.",
     ("Put shared agreements in writing.", "共同约定写成白纸黑字")),
    (frozenset("子卯"), "无礼之刑", "火", "火微洩过旺之木气，缓和唐突",
     "Fire gently drains the excess wood, which softens abruptness.",
     ("Sort out the tone before the content.", "先调语气，再谈内容")),
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
    "木": "Use metal accents or warm lighting instead of green.",
    "火": "Use blue or black accents, or earthy neutrals, instead of red.",
    "土": "Use green accents, or white or metal, instead of yellow or brown.",
    "金": "Use red or purple accents, or black or blue, instead of white.",
    "水": "Use yellow or brown accents, or green, instead of black or blue.",
}

# §3e — behavioural strategy by (relation, pillar)
BEHAVIOUR = {
    ("六沖", "day"): ("情感 Emotional display · 行动 Action",
        "把大反应放慢半拍——冲突别变成当场的决定",
        "Slow big reactions down. Don't let a clash turn into a snap decision."),
    ("六沖", "year"): ("权威 Authority stance",
        "家规传统各有默认值——明说家里的规则，别靠假设",
        "Agree house rules out loud rather than assuming you share the same family habits."),
    ("刑", "day"): ("表达 Expression · 情感 Emotional display",
        "暗劲在沉默里累积——定期直接沟通，别让摩擦攒着",
        "Tension builds quietly when nobody speaks. Schedule regular, direct check-ins."),
    ("刑", "year"): ("权威 Authority stance",
        "长辈事务先说清谁定什么，免得反复",
        "Agree clearly who decides what in extended-family matters."),
    ("六害", "day"): ("思维 Thinking style",
        "耗损常来自思路错位——把计划翻译成对方的语言",
        "Explain plans in the other person's style: one may think things through, "
        "the other may want practical steps. Don't assume you reason alike."),
    ("六害", "year"): ("表达 Expression",
        "与亲族沟通时，把背景讲透，宁多勿省",
        "Explain more than feels necessary to extended family. Hidden assumptions "
        "are what wear things down."),
}

# §4 — framings keyed off the band
FRAMING = {
    "上等": {"family": ("相处自然合拍，家庭氛围融洽", "Life under one roof comes easily. The household finds its rhythm without effort."),
           "couple": ("夫妻宫呼应，感情基础稳固", "The two day pillars answer each other: a naturally solid foundation to build on."),
           "colleagues": ("默契佳，适合长期合作项目", "Rapport comes built in. This pair can be trusted with long-running projects.")},
    "中上": {"family": ("大方向一致，小习惯可磨合", "Aligned where it counts. The small daily habits just need a little adjusting."),
           "couple": ("感情有基础，仍需用心经营", "There is real substance here, and it rewards steady care."),
           "colleagues": ("合作顺畅，分工清楚即可", "Working together flows well once each person's role is clear.")},
    "中": {"family": ("需要主动沟通维系关系", "Closeness will not happen by default. It takes regular, deliberate communication."),
          "couple": ("需磨合，建议明确沟通节奏", "Workable with effort. Agree on how and when you talk things through."),
          "colleagues": ("可共事，建议书面约定分工", "Fine to work together. Just put who does what in writing.")},
    "需磨合": {"family": ("差异明显，建议长辈或顾问协助沟通", "The differences are real. A trusted elder or advisor can help bridge the gap."),
            "couple": ("需要认真经营，必要时寻求咨询", "This pairing asks for serious commitment. Professional guidance is worth it if marriage is the goal."),
            "colleagues": ("合作前先明确边界与退出机制", "Agree on boundaries, and an exit plan, before committing to anything big.")},
}
_BAND_KEY = lambda s: ("上等" if s >= 70 else "中上" if s >= 55 else
                       "中" if s >= 45 else "需磨合")
_BAND_EN = {"上等": "Very compatible", "中上": "Compatible",
            "中": "Workable", "需磨合": "Needs effort"}

_REL_PTS = {"day": {"六合": 15, "半三合": 10, "六沖": -15, "刑": -8, "六害": -8},
            "year": {"六合": 8, "半三合": 8, "六沖": -8, "刑": -4, "六害": -4}}


def _bi(zh, en):
    return {"zh": zh, "en": en}


def _friction(kind, pillar, ba, bb, na, nb, kid=False):
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
                "This friction sits mostly inside one person and shows up in the "
                "relationship. Put the calming element in that person's own space."),
                "colour_material": "", "direction": ""}
        else:
            grp = next((g for g in XING_GROUPS if {ba, bb} <= g[0]), None)
            name, el, zh_w, en_w, note = (grp[1], grp[2], grp[3], grp[4], grp[5]) \
                if grp else ("刑", "", "", "", ("", ""))
            mech, cite = "洩/克", "三命通會〈论三刑〉; element remedy MODERN SYNTHESIS"
            elem = {"zh": el, "en": ELEMENT_EN.get(el, ""),
                    "why": _bi(f"{name}：{zh_w}", en_w),
                    "colour_material": note[0], "note_zh": note[1], "direction": ""}
    else:  # 六害
        el, zh_w = HAI_FIX[frozenset((ba, bb))]
        mech, cite = "合化解", "淵海子平〈论六害〉; element pick MODERN SYNTHESIS"
        elem = {"zh": el, "en": "/".join(ELEMENT_EN.get(e, e) for e in el.split("/")),
                "why": _bi(zh_w + "——择两人共同用神所喜的一边",
                           "Restore the Six Harmony pairing that the harm disturbed. "
                           "Choose the side that the pair's shared useful element favours."),
                "colour_material": "", "direction": ""}
    ax, bzh, ben = BEHAVIOUR[(kind, pillar)]
    things = "big purchases or joint decisions" if kid else "weddings, big purchases or joint signings"
    return {"mechanism": mech, "source_ref": cite,
            "element": elem,
            "behaviour": {"axis": ax, "zh": bzh, "en": ben},
            "timing": _bi(f"逢{ba}年或{bb}年，避免签订重大共同决定（伏吟/反吟再触此{kind}）",
                          f"Treat {ba} and {bb} years as poor timing for {things}. "
                          f"Those years bring this {KIND_EN[kind]} back to life.")}


def _and(items) -> str:
    items = list(items)
    if len(items) == 1:
        return items[0]
    if len(items) > 2 and any("," in x for x in items):
        return "; ".join(items[:-1]) + "; and " + items[-1]
    return ", ".join(items[:-1]) + " and " + items[-1]


def _semi(items, cap=3) -> str:
    """Tied items joined with semicolons, at most `cap` named (batch 1, B8)."""
    items = list(items)
    more = len(items) - cap
    items = items[:cap]
    body = items[0] if len(items) == 1 else "; ".join(items[:-1]) + "; and " + items[-1]
    return body + (f"; and {more} more, listed below" if more > 0 else "")


def _need(weights: dict, e: str) -> str:
    """B1: how much the receiver's chart has of an element, in words. One function feeds the row
    label, its explanation and the summary so they can never disagree."""
    tot = sum(weights.values()) or 1
    s = {x: weights.get(x, 0) / tot * 100 for x in "木火土金水"}
    v = s[e]
    return "is short of" if v < 12 else "could use more of" if v < 16 and v == min(s.values()) else "benefits from"


def _summary_parts(arith) -> dict:
    """Top positive rows and most negative rows, EVERY tie included."""
    pos = [r for r in arith if r["delta"] > 0]
    neg = [r for r in arith if r["delta"] < 0]
    pmax = max((r["delta"] for r in pos), default=0)
    wmin = min((r["delta"] for r in neg), default=0)
    plus = [r for r in pos if r["delta"] == pmax]
    watch = [r for r in neg if r["delta"] == wmin]
    return {"plus": [r["label"]["en"] for r in plus],
            "watch": [r["label"]["en"] for r in watch],
            "plus_delta": pmax, "watch_delta": wmin,
            "plus_plain": [r["plain_cn"] for r in plus],
            "watch_plain": [r["plain_cn"] for r in watch],
            "plus_rows": [arith.index(r) for r in plus],
            "watch_rows": [arith.index(r) for r in watch]}


def pair_breakdown(ca, cb, ys_a, ys_b) -> dict:
    """The drawer payload: pass-through score + bilingual ledger + enrichment.
    The ledger re-derives the SAME rules as pair_compatibility() so the sum is
    guaranteed to reconcile (pinned by test)."""
    base = pair_compatibility(ca, cb, ys_a, ys_b)
    na, nb = ca.person, cb.person
    da, db = ca.pillars["day"], cb.pillars["day"]
    ages = [_age_on(ca.birth_local), _age_on(cb.birth_local)]
    voice = _voice(ages)
    kid = voice != "adult"
    ledger, strengths, frictions = [], [], []

    def add(zh, en, delta, pillars, skind=None, fr=None, sdyn=None, element=None,
            kind="other", plain=None, plain_cn=None, **extra):
        row = {"label": _bi(zh, en), "delta": delta, "pillars": pillars, "kind": kind,
               "plain": plain or en, "plain_cn": plain_cn or plain or en}
        if element:
            row["element"] = element
        row.update(extra)
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

    def rel_plain(kind, subject):
        verb = "form a" if kind in ("六合", "半三合") else "meet in a"
        return (f"{subject} {verb} {KIND_EN[kind]}",
                f"{subject} {verb} {KIND_EN[kind]} ({kind})")

    rel = _branch_rel(da.branch, db.branch)
    if rel is None:
        add("日支中性", "Day branches: no link", 0, "day-day", kind="day",
            plain="their day branches show no link", relation="", relation_en="no link")
    else:
        kind, _ = rel
        pts = _REL_PTS["day"][kind]
        pl, plc = rel_plain(kind, f"their day branches {da.branch} and {db.branch}")
        add(f"日支{kind} {da.branch}{db.branch}（夫妻宫）",
            f"Day branches {da.branch} and {db.branch}: {KIND_EN[kind]}",
            pts, "day-day",
            skind=("day" + kind) if pts > 0 else None,
            fr=_friction(kind, "day", da.branch, db.branch, na, nb, kid) if pts < 0 else None,
            kind="day", plain=pl, plain_cn=plc, relation=kind, relation_en=KIND_EN[kind])
    if WUHE.get(da.stem) == db.stem:
        s_pl = f"their Day Master stems {da.stem} and {db.stem} form a Five Combination"
        add(f"日干五合 {da.stem}{db.stem}",
            f"Day stems {da.stem} and {db.stem}: Five Combination",
            10, "day-day", skind="五合", kind="stem", plain=s_pl,
            plain_cn=s_pl + " (五合)", relation="五合", relation_en="Five Combination")
    ya, yb = ca.pillars["year"].branch, cb.pillars["year"].branch
    yrel = _branch_rel(ya, yb)
    if yrel:
        kind, _ = yrel
        pts = _REL_PTS["year"][kind]
        pl, plc = rel_plain(kind, "their zodiac years")
        add(f"年支(生肖){kind} {ya}{yb}", f"Zodiac years: {KIND_EN[kind]}",
            pts, "year-year",
            skind="year合" if pts > 0 else None,
            fr=_friction(kind, "year", ya, yb, na, nb, kid) if pts < 0 else None,
            kind="year", plain=pl, plain_cn=plc, relation=kind, relation_en=KIND_EN[kind])
    adds = relation_additions(ca, cb)                    # batch 2 rows, listed after the supply rows (same order as the score)
    scored_cells = {(r["pillar_a"], r["pillar_b"]): r["delta"] for r in adds if r["kind"] == "cell"}
    wa, wb = ca.element_weights, cb.element_weights
    ta, tb = sum(wa.values()) or 1, sum(wb.values()) or 1
    for giver, gw, gt, taker, tys, gys in ((ca, wa, ta, cb, ys_b, ys_a), (cb, wb, tb, ca, ys_a, ys_b)):
        n = 0
        for e in tys["favourable"]:
            if gw.get(e, 0) / gt >= 0.2 and n < 2:
                w = _need(taker.element_weights, e)
                tires = e in gys["unfavourable"]          # the giver's own chart avoids it (B2)
                add(f"{giver.person}五行{e}旺，补{taker.person}所需",
                    f"{giver.person} has plenty of {ELEMENT_EN[e]}, which "
                    f"{taker.person}'s chart {w}", 6, "chart-wide",
                    element=e, kind="supply", giver=giver.person, receiver=taker.person, tires=tires,
                    sdyn={
                        "explanation": _bi(
                            "一方五行充沛，恰是对方八字所需的用神——同住同色即有扶持之效",
                            f"{ELEMENT_EN[e]} helps {taker.person} but tires {giver.person}. "
                            f"Keep it in {taker.person}'s own space rather than shared rooms." if tires else
                            f"{giver.person} brings the {ELEMENT_EN[e]} that {taker.person}'s chart {w}."),
                        "action": _bi(
                            f"共处空间多用{e}系配色，多安排共同活动即可",
                            f"Give {taker.person} relaxed, unhurried time with {giver.person}."),
                        "source_ref": "Classical useful-element method (用神, 子平法). "
                                      "Using one chart's supply for the other is our own "
                                      "modern addition."})
                n += 1
        dom = max(gw, key=gw.get)
        if dom in tys["unfavourable"]:
            add(f"{giver.person}主气{dom}为{taker.person}所忌",
                f"{ELEMENT_EN[dom]} is {giver.person}'s strongest element, and "
                f"{taker.person}'s chart does better with less of it", -6, "chart-wide",
                element=dom, kind="clash", giver=giver.person, receiver=taker.person,
                fr={"mechanism": "克/洩",
                    "source_ref": "用神扶抑 (三命通會); lever MODERN SYNTHESIS",
                    "element": {"zh": dom, "en": ELEMENT_EN[dom],
                                "why": _bi("以其克/洩元素调和共处环境",
                                           f"Soften the extra {ELEMENT_EN[dom]} in shared "
                                           "rooms with the element that balances it."),
                                "colour_material": AVOID_LEVER[dom], "direction": ""},
                    "behaviour": {"axis": "环境 environment",
                                  "zh": f"共处空间少用{dom}色系，多用{taker.person}的用神色",
                                  "en": ""},          # B4: colour advice lives in the one rooms line
                    "timing": _bi("——", "")})
    for r in adds:                                       # the same rows pair_compatibility() summed (capped cells show 0)
        extra = {k: r[k] for k in ("relation", "pillar_a", "pillar_b", "raw", "capped", "giver", "receiver") if k in r}
        if r["kind"] == "cell":
            extra["relation_en"] = KIND_EN[r["relation"]]
        add(r["zh"], r["en"], r["delta"], r["pillars"], kind=r["kind"], plain=r["plain"], plain_cn=r["plain"], **extra)

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
                "already_scored": (pa == pb == "day") or (pa == pb == "year") or bool(scored_cells.get((pa, pb))),
                "meaning": _bi(
                    f"{na}的{PALACE_ZH[pa][1]}遇{nb}的{PALACE_ZH[pb][1]}——{gz}",
                    f"{na}'s {_pal_en(pa, kid)} meets {nb}'s {_pal_en(pb, kid)}: {ge}.")})

    def _god_el(dm, g):
        from .wuxing import STEM_ELEMENT, STEMS
        return next((STEM_ELEMENT[s] for s in STEMS if ten_god(dm, s) == g), "")

    g_ab, g_ba = base["relation"]["a_sees_b"], base["relation"]["b_sees_a"]
    band_zh = _BAND_KEY(base["score"])
    fr = FRAMING[band_zh]
    def _rel(dm_stem, g):
        mh_zh, mh_en, mw_zh, mw_en = TG_MODERN.get(g, ("", "", "", ""))
        return {"god": g, "element": _god_el(dm_stem, g), **_bi(*TG_SEES[g]),
                "modern_home": _bi(mh_zh, mh_en), "modern_work": _bi(mw_zh, mw_en)}
    return {"a": na, "b": nb, "score": base["score"],
            "ages": ages, "voice": voice,
            "band": _bi(band_zh, _BAND_EN[band_zh]),
            "day_pillars": base["day_pillars"],
            "arithmetic": ledger,
            "summary_parts": _summary_parts(ledger),
            "pillar_sweep": sweep,
            "sweep_matrix": sweep_matrix(ca, cb, scored_cells),
            "sweep_reading": sweep_reading(ca, cb, sweep, voice),
            "relation": {"a_sees_b": _rel(da.stem, g_ab), "b_sees_a": _rel(db.stem, g_ba)},
            "strengths": strengths, "frictions": frictions,
            "framing": {k: _bi(*fr[k]) for k in ("family", "couple", "colleagues")},
            "source_ref": base["source_ref"]}


# ---------------------------------------------------------------------------
# 2026-09-27 — modern layers and the pair clinical report
# (docs/designs/pair-compatibility-deep-dive.md §B, §C). The frozen score is
# untouched: the layers report their own delta and a second, labelled total.
# ---------------------------------------------------------------------------
from .shensha import ten_god_pct as _tg_pct
from .wuxing import KE as _KE, SHENG as _SHENG, STEM_ELEMENT as _SE

_GROUPS = {"官殺": ("正官", "七殺"), "食傷": ("食神", "傷官"), "印": ("正印", "偏印"),
           "比劫": ("比肩", "劫財"), "財": ("正財", "偏財")}
_GRP_EN = {"官殺": "authority", "食傷": "output", "印": "resource", "比劫": "peers", "財": "wealth"}


def _g(pct: dict, grp: str) -> float:
    return round(sum(pct.get(x, 0) for x in _GROUPS[grp]), 1)


def _clamp(x: float) -> int:
    return int(max(5, min(95, round(x))))


def modern_layers(ca, cb, ys_a, ys_b) -> dict:
    """Deep-dive §B rows: DEFENSIBLE items scored on their own ledger (basis:
    classical principle on new data); descriptive rows carry delta 0."""
    na, nb = ca.person, cb.person
    pa, pb = _tg_pct(ca), _tg_pct(cb)
    rows = []

    def row(zh, en, delta, basis, note="", kind="other", **extra):
        rows.append({"label": _bi(zh, en), "delta": delta, "basis": basis, "note": note,
                     "kind": kind, **extra})
    # B1 complementarity — one prominent (≥20%) where the other is absent (0%)
    comp = []
    for grp in ("官殺", "食傷", "印"):
        a, b = _g(pa, grp), _g(pb, grp)
        if a >= 20 and b == 0:
            comp.append((a, na, nb, grp))
        elif b >= 20 and a == 0:
            comp.append((b, nb, na, grp))
    for share, giver, taker, grp in sorted(comp, reverse=True)[:2]:
        row(f"十神互补：{giver}{grp}旺而{taker}缺",
            f"{giver} has a lot of {_GRP_EN[grp]} energy ({share}% of the chart) that {taker}'s chart has none of",
            5, "classical", "One chart is strong in something the other lacks, so they fill each other's gaps.",
            kind="complement", giver=giver, receiver=taker)
    # B2 collision — both heavy in 比劫 or 食傷; 財↔比劫 risk
    if _g(pa, "比劫") >= 20 and _g(pb, "比劫") >= 20:
        row("双方比劫皆旺——争财", "Both charts are heavy in \"peers\" energy: the two may compete for the same money or resources.", -6, "classical", kind="peers")
    if pa.get("傷官", 0) >= 20 and pb.get("傷官", 0) >= 20:
        row("双方伤官皆旺——两不相让", "Both charts are heavy in Hurting Officer (傷官) energy: two sharp critics, and neither gives way.", -6, "classical", kind="critics")
    for x, y, nx, ny in ((pa, pb, na, nb), (pb, pa, nb, na)):
        if _g(x, "財") >= 20 and _g(y, "比劫") >= 20:
            row(f"{nx}财旺遇{ny}比劫旺——劫财之虞", f"{nx}'s chart is strong in wealth and {ny}'s is heavy in peers, so money can become a point of rivalry. Keep money matters explicit.", -4, "classical", kind="wealth_peers", giver=nx, receiver=ny)
    # B4 strength pairing
    wa, wb = ca.strength["verdict"].startswith("身弱"), cb.strength["verdict"].startswith("身弱")
    if wa != wb:
        weak, strong = (na, nb) if wa else (nb, na)
        row("一弱一强——强者稳弱者", f"One stronger chart and one weaker chart: {strong}'s chart has spare strength to steady {weak}'s.", 6, "classical",
            "Partly the same idea as the element-supply rows above.", kind="strength_pair", giver=strong, receiver=weak)
    else:
        row("强弱同类", "Both charts are weak: neither can steady the other, so the pair leans on outside routines and structure." if wa else
            "Both charts are strong: two engines, so agree who leads in each area.", 0, "modern", kind="strength_same")
    # B5 element flow between the two day masters (descriptive)
    ea, eb = _SE[ca.day_master], _SE[cb.day_master]
    flow = ("same element, kindred, on equal footing." if ea == eb else
            f"{na}'s {ELEMENT_EN[ea]} feeds {nb}'s {ELEMENT_EN[eb]}. {na} gives, {nb} receives." if _SHENG[ea] == eb else
            f"{nb}'s {ELEMENT_EN[eb]} feeds {na}'s {ELEMENT_EN[ea]}. {nb} gives, {na} receives." if _SHENG[eb] == ea else
            f"{na}'s {ELEMENT_EN[ea]} controls {nb}'s {ELEMENT_EN[eb]}: {na} sets the frame." if _KE[ea] == eb else
            f"{nb}'s {ELEMENT_EN[eb]} controls {na}'s {ELEMENT_EN[ea]}: {nb} sets the frame.")
    row("日主五行相互关系", f"How their core elements relate: {flow}", 0, "classical", kind="flow")
    # B6 用神 conflict — one side's useful element is the other's 忌
    for x, y, nx, ny, cx in ((ys_a, ys_b, na, nb, ca), (ys_b, ys_a, nb, na, cb)):
        hit = [e for e in x["favourable"] if e in y["unfavourable"]]
        if hit:
            dom = max(cx.element_weights, key=cx.element_weights.get)
            same = len(hit) == 1 and hit[0] == dom
            row(f"{nx}用神{''.join(hit)}为{ny}所忌", f"What helps {nx} ({'/'.join(ELEMENT_EN[e] for e in hit)}) is something {ny} should keep to a minimum.", -4, "classical",
                "This is the same issue as the strongest-element row in the score working." if same
                else "Fixing one person's chart with it can cost the other in shared rooms.",
                kind="conflict", giver=nx, receiver=ny, repeats_strongest_element=same)
    delta = sum(r["delta"] for r in rows)
    return {"rows": rows, "delta": delta,
            "source_ref": "These checks apply classical ideas to the two charts. They are shown "
                          "separately and do not change the main score."}


def pair_clinical_report(pair: dict, pa: dict, pb: dict, modern: dict | None = None) -> dict:
    """summary · findings (Bond, Exchange, Drivers, Fit, Friction, Timing) ·
    assessment · plan · confidence — every sentence over payload fields."""
    na, nb = pair["a"], pair["b"]
    score, band = pair["score"], pair["band"]["en"]
    kid = pair.get("voice", "adult") != "adult"
    arith = pair.get("arithmetic") or []
    sp = pair.get("summary_parts") or _summary_parts(arith)
    m = modern or {"rows": [], "delta": 0}
    score2 = _clamp(score + m["delta"])
    tg = lambda p: max((p.get("tengods_pct") or {}).items(), key=lambda kv: kv[1], default=("none", 0))
    ga, gb = tg(pa), tg(pb)
    supply = [r for r in arith if r["delta"] > 0 and r.get("element")]
    conflict = [r for r in arith if r["delta"] < 0 and r.get("element")]
    # summary
    pl, wt = sp["plus_plain"], sp["watch_plain"]
    parts = [f"{score} out of 100: {band}."]
    if pl:                                                   # B8: ties with semicolons, at most three named
        parts.append(f"Biggest plus: {pl[0]} ({sp['plus_delta']:+d})." if len(pl) == 1 else
                     f"Biggest pluses: {_semi(pl)} ({sp['plus_delta']:+d} each).")
    if wt:
        parts.append(f"To watch: {wt[0]} ({sp['watch_delta']:+d})." if len(wt) == 1 else
                     f"To watch: {_semi(wt)} ({sp['watch_delta']:+d} each).")
    if not pl and not wt:
        parts.append("No single factor stands out; the day branches show no link.")
    summary = " ".join(parts)                                # B9: one number in the headline
    F = []
    dp = pair.get("day_pillars") or ["", ""]
    dayrow = arith[0] if arith else {}
    stem = next((r for r in arith if r.get("kind") == "stem"), None)
    F.append(("Bond", f"Day pillars {dp[0]} and {dp[1]}: {dayrow.get('relation_en', 'no link')}"
              + (f" ({dayrow['delta']:+d})" if dayrow.get("delta") else "") + ". "
              + (f"Their Day Masters form a Five Combination (+{stem['delta']}). " if stem else "Their Day Masters do not form a Five Combination. ")
              + ("The day pillar is the core of each chart, and the classical method weighs it most."
                 if kid else
                 "The day pillar is the most personal part of each chart, and the classical method weighs it most.")))
    F.append(("Exchange", f"Element supply: {len(supply)} plus, {len(conflict)} minus; details in the score working."
              if supply or conflict else "Neither chart is rich in what the other needs."))
    F.append(("Drivers", f"{na} runs mostly on {ga[0]} ({ga[1]}%); {nb} on {gb[0]} ({gb[1]}%)."))
    F.append(("Fit", ""))
    frs = pair.get("frictions") or []
    coll = [r for r in m["rows"] if r["delta"] < 0 and r.get("kind") != "conflict"]
    if frs or coll:
        k = len(frs) + len(coll)
        F.append(("Friction", f"Friction shows up in {k} place{'s' if k != 1 else ''}; see the score working for each one."))
    else:
        F.append(("Friction", "No day or year clash applies here, so any friction is likely to be about the situation, not the charts."))
    def yrs(p, flag):
        return {y["y"] for y in ((p.get("windows") or {}).get("years") or []) if (y.get("relationship") or {}).get("flag") == flag}
    both_c, both_w = sorted(yrs(pa, "caution") & yrs(pb, "caution")), sorted(yrs(pa, "window") & yrs(pb, "window"))
    c_things = "big purchases and joint decisions" if kid else "weddings and joint signings"
    one = lambda ys: len(ys) == 1
    F.append(("Timing", (f"Both charts mark {', '.join(map(str, both_c))} as {'a year' if one(both_c) else 'years'} for extra care. Treat {'it as a poor year' if one(both_c) else 'them as poor years'} for {c_things}. " if both_c else "No year is marked for extra care in both charts at once. ")
              + (f"Both charts mark {', '.join(map(str, both_w))} as {'a favourable year' if one(both_w) else 'favourable years'} for the relationship." if both_w else "")))
    # assessment
    A = []
    big = max((abs(r["delta"]) for r in arith), default=0)
    tops = [r for r in arith if big and abs(r["delta"]) == big]
    tp, tn = [r["plain_cn"] for r in tops if r["delta"] > 0], [r["plain_cn"] for r in tops if r["delta"] < 0]
    if tp and tn:
        A.append(f"The biggest factors pull both ways. Supportive: {_and(tp)}. A tension: {_and(tn)}.")
    elif tp:
        A.append(f"The biggest single factor is a supportive one: {tp[0]}." if len(tp) == 1
                 else f"The biggest single factors are supportive ones: {_and(tp)}.")
    elif tn:
        A.append(f"The biggest single factor is a tension: {tn[0]}." if len(tn) == 1
                 else f"The biggest single factors are tensions: {_and(tn)}.")
    else:
        A.append("Nothing in the charts pulls the pair strongly together or apart. What matters is what the two of them bring.")
    if m["delta"]:
        A.append(f"The extra checks {'add' if m['delta'] > 0 else 'subtract'} {abs(m['delta'])} points, taking the figure from {score} to {score2}. The main score does not change.")
    # plan
    plan = []
    for s in (pair.get("strengths") or [])[:2]:
        if s.get("action", {}).get("en"): plan.append(s["action"]["en"])
    for f in frs[:2]:
        if f.get("behaviour", {}).get("en"): plan.append(f["behaviour"]["en"])
    if any("比劫" in r["label"]["zh"] for r in coll):
        plan.append("Write down who owns what: money, decisions and time. Two charts heavy in peers energy tend to compete unless roles are clear.")
    if any(r.get("kind") == "conflict" for r in m["rows"]):
        plan.append("Split shared rooms by colour: each person's helpful colours in their own corner, neutral tones in common space.")
    if both_c:
        c_plan = "big purchases and joint decisions" if kid else "weddings, purchases and joint signings"
        plan.append(f"Keep {c_plan} out of {', '.join(map(str, both_c))}.")
    if not plan:
        plan.append("With no strong link either way, invest in shared time rather than shared assets until a favourable year comes.")
    timing_line, actions = _timing_and_actions(pair, pa, pb, m)
    return {"summary": summary, "findings": [{"label": l, "text": t.strip()} for l, t in F],
            "assessment": " ".join(A), "plan": plan[:5], "confidence": "",
            "score_with_modern": score2, "timing_line": timing_line, "actions": actions}


# ---------------------------------------------------------------------------
# 2026-10-10 batch 1: the dated timing line and up to three actions. Wording only: every
# sentence reads a field already in the payload; the score is untouched.
# ---------------------------------------------------------------------------
_CHONG = {frozenset(x) for x in ("子午", "丑未", "寅申", "卯酉", "辰戌", "巳亥")}
_AREA = {"day": "daily routines and personal time", "year": "family gatherings and traditions",
         "month": "work or school schedules", "hour": "evenings and plans for later years"}
_HABIT = {"六沖": "agree a fixed routine for {a}, so a clash never turns into a snap decision",
          "刑": "set a short weekly check-in about {a}, so friction does not build in silence",
          "六害": "explain the background before changing anything about {a}"}
_HABIT_KID = {"六沖": "keep a steady routine for {a}",
              "刑": "keep a calm end-of-day chat, so small frictions are said out loud",
              "六害": "explain changes before they happen"}
_THINGS = {"child": "moving home or school", "teen": "moves, school changes or big family purchases",
           "adult": "big shared decisions such as moves, purchases or signings"}


def _rooms_line(arith) -> str | None:
    """B4: one rooms line per pair. An element is never both leaned toward and limited."""
    shared, own, limit = [], [], []
    for r in arith:
        if r.get("kind") == "supply":
            (own if r.get("tires") else shared).append((r["element"], r["receiver"]))
        elif r.get("kind") == "clash":
            limit.append(r["element"])
    shared = [e for e in dict.fromkeys(e for e, _ in shared) if e not in limit]
    bits = []
    if shared:
        bits.append("lean shared rooms toward " + " and ".join(EL_PALETTE[e] for e in shared))
    for e, t in dict.fromkeys(own):
        bits.append(f"keep {EL_PALETTE[e]} in {t}'s own space")
    if limit:
        bits.append("go easy on " + " and ".join(f"{ELEMENT_EN[e]} tones" for e in dict.fromkeys(limit)) + " in common rooms")
    return ("Rooms: " + "; ".join(bits) + ".") if bits else None


_THINGS_REL = {"couple": "weddings, moves, purchases or signings",
               "colleagues": "big commitments such as contracts or hires"}
_AREA_WORK = {"year": "team traditions and the shared calendar", "hour": "late hours and long-term plans"}


def _timing_and_actions(pair: dict, pa: dict, pb: dict, m: dict) -> tuple[str, list[str]]:
    na, nb, voice = pair["a"], pair["b"], pair.get("voice", "adult")
    rel, senior = pair.get("rel") or "", pair.get("senior") or ""
    work = rel == "colleagues"
    ages = pair.get("ages") or [40, 40]
    dp = pair.get("day_pillars") or ["", ""]
    pillars = {na: pa.get("pillars") or {}, nb: pb.get("pillars") or {}}
    yrs = lambda p: {y["y"]: y for y in ((p.get("windows") or {}).get("years") or []) if 2026 <= y["y"] <= 2031}
    YA, YB = yrs(pa), yrs(pb)
    clashed, fuyin, anyclash = {}, {}, set()
    for y, row in YA.items():
        gz = row.get("gz") or ""
        for who, day in ((na, dp[0]), (nb, dp[1])):
            if gz and day and frozenset(gz[1] + day[1]) in _CHONG:
                clashed.setdefault(y, []).append((who, gz))
            if gz and gz == day:                                        # 伏吟: the year repeats a day pillar
                fuyin.setdefault(y, []).append((who, gz))
            if gz and any(frozenset(gz[1] + p[1]) in _CHONG for p in pillars[who].values() if p):
                anyclash.add(y)
    flag = lambda Y, f: {y for y in Y if (Y[y].get("relationship") or {}).get("flag") == f}
    care = sorted(flag(YA, "caution") & flag(YB, "caution"))
    good = sorted((flag(YA, "window") & flag(YB, "window")) - anyclash)   # never a good year that clashes a pillar
    gentle = sorted(set(care) | set(clashed) | set(fuyin))

    def why(y):
        bits = ([f"{w}'s day pillar is clashed by {g}" for w, g in clashed.get(y, [])]
                + [f"the year repeats {w}'s day pillar {g} (伏吟)" for w, g in fuyin.get(y, [])])
        return " and ".join(bits) if bits else "both charts mark it for care"
    tl = []
    if gentle:
        things = _THINGS.get(voice, _THINGS["adult"]) if voice != "adult" else _THINGS_REL.get(rel, _THINGS["adult"])
        tl.append("Years to go gently: " + _semi([f"{y}, when {why(y)}" for y in gentle], cap=4)
                  + f". Keep {things} out of {'it' if len(gentle) == 1 else 'them'}.")
    if good:
        tl.append(f"Good {'year' if len(good) == 1 else 'years'} for the two of them: {', '.join(map(str, good))}.")
    timing = ("Timing, 2026 to 2031. " + " ".join(tl)) if tl else "Timing, 2026 to 2031: no year stands out for the two of them."

    acts = []
    if clashed:                                                         # A1
        y = min(clashed); w, _ = clashed[y][0]
        age = (ages[0] if w == na else ages[1]) + (y - 2026)            # age in that year
        if age < 13:
            acts.append((9, f"In {y}, keep {w}'s routine steady and avoid big changes for them."))
        elif age < 18:
            acts.append((9, f"In {y}, keep {w}'s school year steady and avoid big changes for them."))
        elif work:
            acts.append((9, f"In {y}, check {w}'s workload before agreeing deadlines."))
        else:
            acts.append((9, f"In {y}, let {w} set the pace" + (" and book a health check-up." if age >= 65 else " and plan lighter commitments.")))
    cells = [x for row in (pair.get("sweep_matrix") or []) for x in row if x["relation"] and not x["bond"]]
    cells.sort(key=lambda x: (not x["scored"], x["pillar_a"] != "day"))
    if cells and cells[0]["relation"] in _HABIT:                        # A2
        x = cells[0]
        ak = "day" if "day" in (x["pillar_a"], x["pillar_b"]) else x["pillar_a"]
        area = (_AREA_WORK.get(ak) if work else None) or _AREA[ak]
        habit = (_HABIT_KID if voice == "child" else _HABIT)[x["relation"]].format(a=area)
        acts.append((8 if x["scored"] else 5,
                     f"Because of the {KIND_EN[x['relation']]} between {na}'s {x['pillar_a']} pillar and {nb}'s {x['pillar_b']} pillar, {habit}."))
    tg = lambda p: p.get("tengods_pct") or {}
    if any(tg(p).get("傷官", 0) >= 20 for p in (pa, pb)) or any(x["relation"] == "刑" and x["scored"] for x in cells):   # A5
        acts.append((6, "Agree a pause rule in advance: when voices rise, stop and come back to it after an hour."))
    ya, yb = ages
    if voice == "child":                                                # A3, only on a chart fact
        kidn, kidp = (na, pa) if ya < yb else (nb, pb)
        press = tg(kidp).get("七殺", 0) + tg(kidp).get("傷官", 0)
        if press >= 15:
            acts.append((7, f"With {kidn}, keep rules few, steady and explained: pressure lands hard on this chart (七殺 and 傷官 together {press:.0f}%)."))
    elif voice == "adult":                                              # A4: care planning
        if rel in ("parent-child", "grandparent-grandchild"):           # the named elder, 65 or over
            elder_age = ya if senior == na else yb if senior == nb else 0
            fire = elder_age >= 65
        elif rel:                                                       # any other set relationship: never
            fire = False
        else:                                                           # unset: age alone, as batch 1
            fire = min(ya, yb) >= 18 and max(ya, yb) >= 65 and abs(ya - yb) >= 18
        if fire:
            acts.append((7, "Talk through support, health and household plans together"
                         + (f" before {gentle[0]}." if gentle else " while things are calm.")))
    rows = m.get("rows") or []
    if voice == "adult" and any(r.get("kind") == "peers" for r in rows):   # A6
        acts.append((5, "Write down who owns what: " + ("budget, credit and decisions." if work else "money, decisions and time.")))
    wp = next((r for r in rows if r.get("kind") == "wealth_peers"), None)
    if voice == "adult" and work and gentle:                            # A7, colleagues
        acts.append((4, f"Decide roles in writing before {gentle[0]}."))
    elif voice == "adult" and wp and not work:                          # A7
        acts.append((4, f"Keep money matters explicit: agree in writing who pays for what, since {wp['giver']}'s chart is strong in wealth and {wp['receiver']}'s is heavy in peers."))
    rooms = _rooms_line(pair.get("arithmetic") or [])
    if rooms:                                                           # A8
        acts.append((2, rooms))
    return timing, [a for _, a in sorted(acts, key=lambda t: -t[0])[:3]]


REL_VALUES = ("couple", "parent-child", "grandparent-grandchild", "siblings", "colleagues", "friends", "other")
REL_FAMILY = ("parent-child", "grandparent-grandchild", "siblings")


def pair_full(ca, cb, ys_a, ys_b, pa: dict, pb: dict, rel: str | None = None, senior: str | None = None) -> dict:
    """breakdown + modern layers + the clinical report, for the public pair route.
    `rel` (batch 2) is the owner-set relationship, wording only: the score is the same for every value.
    `senior` names the parent or grandparent for the two family types."""
    out = pair_breakdown(ca, cb, ys_a, ys_b)
    out["rel"] = rel if rel in REL_VALUES else ""
    out["senior"] = senior if out["rel"] in ("parent-child", "grandparent-grandchild") and senior in (out["a"], out["b"]) else ""
    out["modern"] = modern_layers(ca, cb, ys_a, ys_b)
    out["modern"]["score_with_modern"] = _clamp(out["score"] + out["modern"]["delta"])
    out["report"] = pair_clinical_report(out, pa, pb, out["modern"])
    out["framings_table"] = framings_table(out, out["modern"])
    return out


# ---------------------------------------------------------------------------
# 2026-09-27 — pillar sweep as a 4×4 matrix with a layman reading; framings table
# ---------------------------------------------------------------------------
_BONDS = ("六合", "半三合")
_KIND_DAY = {"六合": ("日常习惯自然对上", "Daily habits line up on their own"),
             "半三合": ("同频，容易并肩做事", "A shared current: easy to move in step"),
             "六沖": ("反应来得快、来得热——大事慢半拍再定", "Reactions run hot and fast, so take your time with big decisions"),
             "刑": ("摩擦在沉默里积累——早说", "Friction builds quietly when nobody speaks, so talk early"),
             "六害": ("小的耗损来自各自的假设——多交代背景", "Small drains come from mismatched assumptions, so explain the background")}


def sweep_matrix(ca, cb, scored_cells: dict | None = None) -> list[list[dict]]:
    """rows = A's pillars (year/month/day/hour), cols = B's. `scored` marks the cells that count in
    the score: day-day and year-year (frozen rules) and, since batch 2, the other cells whose
    points survived the dedupe, 拱合 filter and cap; `points` carries what they added."""
    if scored_cells is None:
        scored_cells = {(r["pillar_a"], r["pillar_b"]): r["delta"] for r in relation_additions(ca, cb) if r["kind"] == "cell"}
    out = []
    for pa in PALACES:
        row = []
        for pb in PALACES:
            ba, bb = ca.pillars[pa].branch, cb.pillars[pb].branch
            r = _branch_rel(ba, bb)
            frozen = (pa == pb == "day") or (pa == pb == "year")
            pts = scored_cells.get((pa, pb), 0)
            row.append({"pillar_a": pa, "pillar_b": pb, "branch_a": ba, "branch_b": bb,
                        "element_a": BRANCH_ELEMENT.get(ba, ""), "element_b": BRANCH_ELEMENT.get(bb, ""),
                        "relation": r[0] if r else None, "bond": bool(r and r[1] > 0),
                        "scored": frozen or bool(pts), "points": pts if not frozen else None})
        out.append(row)
    return out


def sweep_reading(ca, cb, sweep: list[dict], voice: str = "adult") -> dict:
    """The sweep read for a layman: how many bonds vs frictions, which palaces
    they touch, the clearest pairing, and what it means day to day."""
    na, nb = ca.person, cb.person
    kid = voice != "adult"
    bonds = [x for x in sweep if x["relation"]["zh"] in _BONDS]
    fric = [x for x in sweep if x["relation"]["zh"] not in _BONDS]
    if not sweep:
        return _bi("两盘四柱之间没有合冲刑害——这对关系靠五行与十神运转，不靠地支的化学反应。",
                   "No part of one chart links with any part of the other. This pair runs on the elements and the Ten Gods, not on branch links.")
    # B5: every pairing named with its palaces and kind; ", scored" only on day-day and year-year
    pal = lambda x: (f"{na}'s {x['pillar_a']} pillar with {nb}'s {x['pillar_b']} pillar "
                     f"({KIND_EN[x['relation']['zh']]}{', scored' if x['already_scored'] else ''})")
    palz = lambda x: (f"{na}的{PALACE_ZH[x['pillar_a']][0]}对{nb}的{PALACE_ZH[x['pillar_b']][0]}"
                      f"（{x['relation']['zh']}{'，已计分' if x['already_scored'] else ''}）")
    en = (f"{len(bonds)} bond{'s' if len(bonds) != 1 else ''} and {len(fric)} friction{'s' if len(fric) != 1 else ''} across the sixteen pairings."
          + (f" Bonds: {'; '.join(pal(x) for x in bonds)}." if bonds else "")
          + (f" Frictions: {'; '.join(pal(x) for x in fric)}." if fric else ""))
    zh = (f"十六组地支中有{len(bonds)}处相合、{len(fric)}处相冲刑害。"
          + (f"相合：{'；'.join(palz(x) for x in bonds)}。" if bonds else "")
          + (f"冲刑害：{'；'.join(palz(x) for x in fric)}。" if fric else ""))
    # B6: a Day Master combining with a non-day stem of the partner, when the Day Masters themselves do not
    sa = {k: ca.pillars[k].stem for k in PALACES}
    sb = {k: cb.pillars[k].stem for k in PALACES}
    cross, crossz = [], []
    for k, s in sb.items():
        if k != "day" and WUHE.get(sa["day"]) == s:
            cross.append(f"{na}'s Day Master {sa['day']} combines with {nb}'s {k} stem {s}")
            crossz.append(f"{na}日主{sa['day']}合{nb}{PALACE_ZH[k][0]}天干{s}")
    for k, s in sa.items():
        if k != "day" and WUHE.get(sb["day"]) == s:
            cross.append(f"{nb}'s Day Master {sb['day']} combines with {na}'s {k} stem {s}")
            crossz.append(f"{nb}日主{sb['day']}合{na}{PALACE_ZH[k][0]}天干{s}")
    if cross and WUHE.get(sa["day"]) != sb["day"]:
        en += f" Stems: {_semi(cross)} (Five Combination, 五合); a pull between them, not counted in the score."
        zh += f"天干：{'；'.join(crossz)}（五合），有牵引之力，不计分。"
    return _bi(zh, en)


def framings_table(pair: dict, modern: dict) -> dict:
    """family / couple / colleagues × meaning / lean_on / watch, bilingual.
    Lean on and Watch are plain one-line factors (no points); a factor already
    shown in an earlier column is skipped while an unused one exists."""
    fr = pair.get("framing") or {}
    strengths = pair.get("strengths") or []
    frictions = pair.get("frictions") or []
    arith = pair.get("arithmetic") or []
    mrows = (modern or {}).get("rows") or []
    plain_of = {r["label"]["en"]: r.get("plain") for r in arith}

    def st(pred):
        return next((s for s in strengths if pred(s)), None)

    def fx(pred):
        return next((f for f in frictions if pred(f)), None)
    supply = sorted((s for s in strengths if "五行" in s["chip_label"]["zh"]), key=lambda s: -s["delta"])
    dayb = st(lambda s: s["chip_label"]["zh"].startswith("日"))
    yearb = st(lambda s: s["chip_label"]["zh"].startswith("年"))
    comp = next((r for r in mrows if r["delta"] > 0 and r.get("kind") == "complement"), None)
    ws = next((r for r in mrows if r.get("kind") == "strength_pair"), None)
    dayf = fx(lambda f: f["pillars"] == "day-day")
    yearf = fx(lambda f: f["pillars"] == "year-year")
    domf = [f for f in frictions if f["pillars"] == "chart-wide"]
    coll = next((r for r in mrows if r["delta"] < 0 and r.get("kind") != "conflict"), None)
    conf = next((r for r in mrows if r.get("kind") == "conflict"), None)
    none_lean = _bi("没有现成可倚的结构——需要刻意建立", "Nothing in the charts to lean on yet; it will have to be built on purpose.")
    none_watch = _bi("没有结构性的摩擦", "Nothing in the charts to watch.")

    def lab(x):
        if x is None:
            return None
        l = x["chip_label"] if "chip_label" in x else x["label"]
        p = plain_of.get(l["en"])
        en = (p[0].upper() + p[1:]) if p and p != l["en"] else l["en"]
        return _bi(l["zh"], en if en.endswith(".") else en + ".")

    def pick(cands, used, fallback):
        cands = [lab(c) for c in cands if c]
        for c in cands:
            if c["en"] not in used:
                used.add(c["en"])
                return c
        return cands[0] if cands else fallback
    # B10: one hint so a framing never contradicts the scored factors
    scored = [r for r in arith if r.get("kind") in ("day", "year", "stem") and r["delta"]]
    neg = min(scored, key=lambda r: r["delta"], default=None)
    pos = max(scored, key=lambda r: r["delta"], default=None)
    hi = pair.get("score", 0) >= 55
    hint = (f" One thing to manage: {neg['plain']}." if hi and neg and neg["delta"] < 0 else
            f" One real strength: {pos['plain']}." if not hi and pos and pos["delta"] > 0 else "")
    ul, uw = set(), set()
    out = {}
    for ctx, lean, watch in (
            ("family", [yearb, *supply], [yearf, *domf, conf]),
            ("couple", [dayb, *supply, ws], [dayf, conf, *domf]),
            ("colleagues", [comp, ws, *supply], [coll, *domf, conf])):
        mean = fr.get(ctx, _bi("", ""))
        out[ctx] = {"meaning": {"zh": mean["zh"], "en": (mean["en"] + hint) if mean["en"] else mean["en"]},
                    "lean_on": pick(lean, ul, none_lean),
                    "watch": pick(watch, uw, none_watch)}
    return out
