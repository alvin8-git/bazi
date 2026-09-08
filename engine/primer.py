"""FengShui/BaZi 101 — layman primer text, one entry per UI tab.

Single source for the website (/api/primer), the offline snapshot and the
emailable report. Items are [heading, text] pairs; text is plain English with
the Chinese terms introduced, written for someone with zero background.
"""

PRIMERS = {
    "family": {"title": "what a BaZi chart is", "items": [
        ["Eight characters", "BaZi (八字, 'eight characters') maps a birth moment onto "
         "four pillars — year, month, day and hour. Each pillar is two characters (a "
         "heavenly stem + an earthly branch); the eight together are a snapshot of the "
         "five-element 'weather' you were born into. Everything on this site is computed "
         "from those eight characters plus the home's compass data."],
        ["The five elements", "Wood 木, Fire 火, Earth 土, Metal 金 and Water 水 interact "
         "in two cycles: generating (Wood feeds Fire → Fire makes Earth → Earth bears "
         "Metal → Metal carries Water → Water grows Wood) and controlling (Wood breaks "
         "Earth, Earth dams Water, Water quenches Fire, Fire melts Metal, Metal cuts "
         "Wood). A chart is 'healthy' when its elements support each other; most charts "
         "tilt one way, and correcting the tilt is the whole game."],
        ["Day Master & strength", "The stem of your DAY pillar is the Day Master — the "
         "character that stands for you. 'Strong' or 'weak' is neither compliment nor "
         "insult: it measures whether the birth season and the other seven characters "
         "feed your element or drain it, and it only decides WHICH elements help you."],
        ["用神 favourable elements", "The elements that would rebalance the chart are its "
         "用神 ('useful gods'). They become practical handles: colours to wear and "
         "decorate with, and compass sectors whose element feeds yours."],
        ["命卦 Life Gua & East/West groups", "A separate, simpler system — 八宅 Eight "
         "Mansions — reduces birth year + sex to one of eight trigrams. East-group "
         "people (坎離震巽) and West-group people (乾坤艮兌) have OPPOSITE sets of four "
         "lucky and four unlucky directions, which is why a mixed family can never share "
         "one perfect room and this app optimises the trade-off instead."]]},

    "person": {"title": "how a full reading is built", "items": [
        ["True solar time", "Birth certificates record clock time, but the hour pillar "
         "follows the sun. Singapore's clock ran at UTC+7:30 before 1982 and UTC+8 "
         "after, while the sun crosses Singapore around 13 minutes off either — so a "
         "a recorded 07:09 can be a true-solar 06:43, occasionally shifting the hour "
         "pillar entirely. The toggle at the top lets you compare both."],
        ["Hidden stems 藏干", "Each earthly branch secretly 'stores' one to three stems "
         "(e.g. 寅 stores 甲丙戊). They count toward the element balance at reduced "
         "weight, which is why the tables show more than eight characters."],
        ["Ten Gods 十神", "Every other character is classified by its relationship to "
         "your Day Master into ten archetypes, grouped in five life domains: peers "
         "(independence, siblings), output (creativity, children), wealth, authority "
         "(career, pressure) and resource (learning, support). They describe domains of "
         "life, not literal people."],
        ["How the strength verdict is derived", "Four auditable steps: ① does the birth "
         "MONTH's element feed or drain you (the season rules the chart); ② weight of "
         "supporters (your element + the one that generates it); ③ weight of drains "
         "(the elements you generate, control, and are controlled by); ④ roots — do any "
         "branches hide your element. The steps are printed below so you can check the "
         "arithmetic."],
        ["大運 luck cycles", "Life is divided into 10-year chapters. The starting age "
         "comes from the days between birth and the next solar term divided by 3; each "
         "chapter overlays two more elements on the chart, tilting its balance — that is "
         "why the same person has easier and harder decades."],
        ["神煞 symbolic stars", "Classical BaZi also tags special stem-branch patterns "
         "as 'stars': helpful-people stars (天乙/天德), romance (桃花), travel (驛馬), "
         "study (文昌/學堂), depth (華蓋), voids (空亡). Each is a fixed lookup table — "
         "colour and texture on top of the structural read, never a verdict by itself."],
        ["納音 & growth stages", "Two classical extras on the pillar cards: 納音 gives "
         "each pillar a poetic 'sound element' (e.g. 沙中土 'sand-in-earth') from the "
         "60-cycle table, and the 十二長生 growth stage (長生 birth → 帝旺 peak → 墓 "
         "storage…) shows how vigorous the Day Master's element is at each pillar. "
         "Flavour and nuance, not verdicts."],
        ["Health & industry maps", "Traditional five-element medicine links each "
         "element to organ systems (Water→kidneys, Wood→liver, Fire→heart, "
         "Earth→digestion, Metal→lungs); a very weak or excessive element marks "
         "systems worth caring for — a correspondence tradition, not medical advice. "
         "Likewise every industry has an element nature, so the 用神 doubles as a "
         "career-direction hint."],
        ["Formation & personality axes", "The formation check tests whether the chart "
         "is an ordinary structure (正格) or a rare follower/dominant special case "
         "(從格/專旺) that would flip the reading — decided by roots and support ratio. "
         "The personality axes translate the ten-god distribution into five everyday "
         "tendencies, each with its threshold shown; 'no strong tendency' is a normal "
         "result."],
        ["Life-domain signals", "The career / relationship / wealth / learning scores "
         "are assembled from auditable parts: how much of the chart is made of the "
         "relevant star type (spouse star, authority stars…), whether that element is "
         "among the 用神, palace checks (the DAY branch is the spouse palace), and the "
         "symbolic stars above. 0–100, zero-centred at 50 — structural tendencies to "
         "act on, never guarantees."]]},

    "house": {"title": "how a house gets a chart", "items": [
        ["Houses have birth charts too", "玄空飛星 (Flying Stars) gives the home its own "
         "chart from two facts: WHEN it was built or last majorly renovated (20-year "
         "periods — Period 8 = 2004–Feb 2024, Period 9 = Feb 2024–2044) and WHICH "
         "direction it faces. Nine 'stars' (numbered energies) are then distributed over "
         "the nine sectors."],
        ["Mountain star vs water star", "Each sector holds two numbers: the mountain "
         "star 山星 governs people, health and relationships (best where people rest), "
         "and the water star 向星 governs wealth and activity (best where life happens — "
         "door, living areas). Red = mountain, blue = water in the grid."],
        ["Structures", "When the current period's own star lands in its proper places "
         "the house is 旺山旺向 ('prosperous mountain, prosperous facing') — the best "
         "case. Inverted placement is 上山下水, the weakest. This is a property of the "
         "whole house, independent of who lives in it."],
        ["Visiting stars", "Stars also move yearly and monthly. The 五黃 (5-yellow, "
         "misfortune) and 二黑 (2-black, illness) are the two to respect: tradition says "
         "do not renovate, drill or 'ground-break' in the sector they currently occupy — "
         "keep it quiet and tidy instead."],
        ["Door & stove rules (八宅)", "The house's own trigram (from its sitting "
         "direction) gives the HOUSE a lucky/unlucky direction map, separate from any "
         "person's. The main door — the mouth of 氣 — wants a lucky sector; the stove "
         "classically PRESSES an unlucky one (壓凶), burning away its negativity. Mark "
         "both on the Trace page to activate this reading."],
        ["Annual afflictions 太歲/歲破/三煞", "Beyond the visiting stars, each year "
         "afflicts whole directions: the 太歲 sector (the year branch's home — don't "
         "face it for long, never dig there), the 歲破 sector opposite it, and the "
         "三煞 band of three sectors (don't sit toward it). These are marked on the "
         "grid and rotate every year."],
        ["米字 pie vs 九宮 grid", "Two traditional ways of cutting a floorplan into nine "
         "sectors: 8 pie slices from the centre, or a 3×3 grid over the bounding box. "
         "Rooms flagged ⚠ land in different sectors under the two methods — treat their "
         "readings with more caution."]]},

    "assign": {"title": "how the room scores are computed", "items": [
        ["Three layers, fixed weights", "Each person-in-room score = 40% 八宅 (is this "
         "sector one of their four lucky or four unlucky directions), + 40% Flying Stars "
         "(quality of the sector's mountain/water/annual stars for this period), + 20% "
         "用神 match (does the sector's element feed their favourable elements). Every "
         "line in the breakdown cites the rule that produced it."],
        ["Zero-centred scores", "0 means neutral fit. A negative number marks a mismatch "
         "between one person and one sector — NOT a bad house and NOT a prediction of "
         "harm. In a mixed East/West family some negatives are mathematically "
         "unavoidable; the goal is the arrangement that minimises them."],
        ["Roommate compatibility", "Sharing a room adds small terms: day-branch 六沖 "
         "(clash) pairs subtract, 六合 (harmony) pairs add. This is why the optimizer "
         "sometimes separates two people even when their individual room fits look "
         "similar."],
        ["The optimizer", "✨ Optimize brute-forces every allowed arrangement (parents "
         "stay together in the master unless you allow a split; capacity limits "
         "respected) and ranks them by household total — nothing is estimated, every "
         "candidate is fully scored."],
        ["Compensation", "A person stuck in a weak sector isn't stuck: point the "
         "headboard/desk toward one of their personal lucky directions and bring in "
         "their 用神 colours. In classical practice, in-room alignment mitigates a large "
         "part of a sector penalty."]]},

    "forecast": {"title": "reading a year and its months", "items": [
        ["太歲 the Grand Duke", "Each year carries a stem-branch pair (2026 = 丙午); its "
         "branch is personified as 太歲, the year's governor. Your relationship to it is "
         "read by comparing your birth branches to the year branch: same branch = 值 "
         "(your zodiac year — turbulence), opposite = 沖 (clash — movement, disruption), "
         "certain pairs = 合/三合 (harmony — support), others = 害 (friction)."],
        ["Year element vs your chart", "Separately, the year's two elements are checked "
         "against your 用神: a year made of elements you need generally flows with you; "
         "a year made of elements you avoid demands more pacing."],
        ["Monthly stars in your bedroom", "The visiting stars move every month. When "
         "5-yellow or 2-black lands in YOUR bedroom's sector, tradition says avoid "
         "renovating or drilling in that room that month — that's the red months in the "
         "table. Green months carry supportive stars and suit fresh starts."],
        ["5-year outlook", "Each coming year's branch is compared against your four "
         "natal branches. Clashes (沖) and punishments (刑) mark years of movement and "
         "friction; combinations (合/半合) mark support. 'High volatility' is not a bad "
         "year — it is a year to decide slowly, write things down, and avoid "
         "irreversible commitments made in haste."]]},

    "dates": {"title": "how days are rated", "items": [
        ["建除 twelve officers", "Days rotate through twelve 'officers' determined by "
         "how far the day's branch sits from the month's branch. 成 (Success) and 開 "
         "(Open) days favour beginnings; 破 (Destruction) days are the classical worst "
         "for anything important. That cycle is the base score."],
        ["月破 month-breaker", "A day whose branch directly opposes the month's branch "
         "is 月破 — an extra penalty on top of its officer."],
        ["Personal flags", "A day can be fine in general but bad for one person: if the "
         "day's branch clashes (沖) your zodiac year or your day pillar, that member "
         "should sit out big personal moves that day. 合 days are mildly supportive for "
         "that person. These flags are per-member, which is why they're listed by name."],
        ["吉時 hour selection", "Within a chosen day, hours are rated too: 貴人 hours "
         "(where the day stem's nobleman branches fall) and 合日 hours (combining the "
         "day branch) are favourable; the 時破 hour clashes the day itself and is "
         "avoided for signings and openings. Each 時辰 spans two clock hours."],
        ["Cross-check", "This is a simplified 擇日 (date-selection) model. For a "
         "once-in-years event (wedding, major renovation start), tradition cross-checks "
         "a published almanac (通書) which layers many more cycles."]]},

    "pair": {"title": "how 合婚 compatibility is read", "items": [
        ["Spouse palaces first", "The DAY branch of each chart is that person's spouse "
         "palace. Classical 合婚 starts by comparing the two day pillars: 六合/三合 "
         "between them reads as a natural bond, 沖/刑/害 as friction to manage. The "
         "day STEMS can also form one of the five 五合 pairs — the classic stem bond."],
        ["生肖 year branches", "The zodiac-level check: year branches in 六合 or the "
         "same 三合 frame support each other; opposite branches (相沖, six years "
         "apart) mark a generational clash — softer than a day-pillar clash."],
        ["Element supply", "The practical layer: if one chart is rich in an element "
         "the other's 用神 needs, being together tends to feel supportive — and vice "
         "versa when one person's dominant element is what the other avoids."],
        ["How to read the score", "50 is neutral; every factor is a visible chip. It "
         "measures natural ease between two charts, not the quality or destiny of a "
         "relationship — low scores are managed with rooms, colours and date choices, "
         "exactly like a room mismatch."]]},

    "names": {"title": "Chinese name numerology", "items": [
        ["Kangxi strokes", "姓名學 counts each character's strokes as written in the "
         "Kangxi dictionary's traditional form — 簡體 simplified forms have different "
         "counts and would corrupt every number below. That is why this is the one page "
         "that keeps names in 繁體."],
        ["The Five Grids 五格", "Stroke sums build five numbers, each read against a "
         "traditional 1–81 table of lucky 吉 / mixed 半吉 / unlucky 凶 meanings: 天格 "
         "heaven (inherited — least personal), 人格 person (core character — the most "
         "important), 地格 earth (early life & foundations), 外格 outer (social face), "
         "總格 total (the whole life arc)."],
        ["三才 Three Talents", "The elements of heaven, person and earth grids should "
         "GENERATE each other (e.g. Fire→Earth→Metal). A generating flow is 吉; a "
         "controlling one signals internal friction. A less-than-perfect 三才 or one 凶 "
         "grid is traditionally softened with a usage name — not a legal rename."]]},

    "forme": {"title": "how aspect cards are scored", "items": [
        ["Three layers", "Every card is the top of a pipeline: CALCULATE (the classical "
         "BaZi/飞星/八宅 engines, unchanged and fully cited) → INTERPRET (this 0–100 "
         "score, blended with the declared weights below) → PRESCRIBE (the action "
         "chips, each citing the classical rule that triggered it)."],
        ["Bands, not decimals", "The band word is the reading: 旺 strong (≥80), 优 good "
         "(65–79), 平 fair (45–64), 弱 weak (30–44), 忌 poor (<30). Scores inside one "
         "band are equivalent — the number exists only so cards can be sorted and "
         "compared across people, rooms and homes."],
        ["The weights are calibration, not classical truth", "Classical texts rank and "
         "describe; they do not assign percentages. The blend weights below are this "
         "app's own declared calibration — visible, criticisable and adjustable — "
         "never a claim that '40%' appears in any classic."],
        ["One action per resource", "You have one headboard, one desk, one room colour "
         "scheme. When rules compete for the same physical resource, the higher-"
         "priority rule wins (annual-star safety > 八宅 personal > 用神 colour > "
         "activation) and the loser is kept visible in the audit as 'superseded' — "
         "advice never silently contradicts itself."]]},

    "ourhome": {"title": "reading the household page", "items": [
        ["Family-mean cards", "Each home aspect card is the arithmetic mean of the "
         "five members' scores — deliberately simple and criticisable. The driver "
         "line always names the WEAKEST member and their top fix, so a good average "
         "can never bury one person's problem."],
        ["Room suitability", "A room card is a compatibility rating between one "
         "person and one room — 八宅 personal directions (40%), the sector's flying "
         "stars (40%) and 用神 element match (20%) — not a prediction. Negative raw "
         "fits appear as sub-50 scores with compensations attached."],
        ["Structure & timing", "The structure card grades the house's own flying-star "
         "chart; the timing card counts which traced rooms sit on this year's "
         "afflicted sectors (fine to occupy, bad to disturb)."]]},

    "compare": {"title": "comparing like with like", "items": [
        ["One card language", "Every column renders the same card component, so a "
         "band word in one column means exactly the same thing in another — that is "
         "the point of the universal card contract."],
        ["Homes are compared at their best", "The Homes view scores each home under "
         "its own OPTIMAL room arrangement, not whoever happens to sleep where today "
         "— a fair ceiling-vs-ceiling comparison (the emailable battlecard uses the "
         "same basis)."],
        ["Small gaps are noise", "Compare bands first. A 3-point score gap within "
         "the same band is below the method's resolution; a band gap is signal."]]},

    "planner": {"title": "picking times, not fearing them", "items": [
        ["Day officers 十二建除", "Classical almanacs assign each day one of twelve "
         "'officers' by how its branch relates to the month's. 成 (completion) and "
         "開 (open) days favour starts and signings; 破 (breaker) days — where the "
         "day clashes the month — are the one hard avoid. This is a simplified 宜忌 "
         "map, not a full 通書."],
        ["Personalised clashes", "A generically good day can still clash one family "
         "member's year or day branch — the flag under a card names who should not "
         "LEAD the event that day (attending is fine by convention)."],
        ["吉時 hours", "Within a chosen day, hours whose branch is the day stem's "
         "貴人 or combines the day branch are preferred; the hour clashing the day "
         "(時破) is skipped. Hours are a refinement — get the day right first."],
        ["Renovation windows", "The no-disturbance zones (太歲/歲破/三煞/五黃/二黑) "
         "reset every 立春. Blocked means no drilling or hacking in that zone — "
         "living there normally is fine."]]},

    "unit": {"title": "screening a candidate home", "items": [
        ["Coarse mode", "With only a facing direction and a period, the engine can "
         "already build the unit's flying-star chart and score its eight sectors for "
         "each family member — no floorplan needed. That's enough to RANK candidate "
         "units against each other before viewing."],
        ["What to look for", "Prefer units whose structure is 旺山旺向, whose best "
         "sectors spread across family members, and whose household best-sum beats the "
         "alternatives. Treat the numbers as a shortlist filter: room shapes, door "
         "positions and the real compass reading come later."],
        ["Before deciding", "Take an on-site compass reading at the main door/balcony "
         "(phone compass, 2–3 spots) — developer brochures are often tens of degrees "
         "off, and a reading near a 15° mountain boundary can flip the whole chart."]]},
}


def _weights_table_text() -> str:
    """The §5 weights table, rendered from aspects.WEIGHTS itself (T2-A: one
    source — the primer can never drift from the code)."""
    from .aspects import ASPECT_ZH, WEIGHTS
    rows = []
    for aspect, comps in WEIGHTS.items():
        parts = " · ".join(f"{rid} {w}" for rid, w in comps)
        rows.append(f"{ASPECT_ZH[aspect]} {aspect}: {parts}")
    return ("Component weights per aspect (each component is scored 0–100 from the "
            "cited classical outputs, then blended): " + "; ".join(rows) +
            ". CALIBRATION, NOT CLASSICAL TRUTH — these percentages are this app's "
            "own declared blend.")


PRIMERS["forme"]["items"].append(["The declared weights table", _weights_table_text()])
