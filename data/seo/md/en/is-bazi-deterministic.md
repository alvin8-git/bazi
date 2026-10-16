# Is BaZi Deterministic? Computed, Not Chatted

Canonical: https://bazifor.me/learn/is-bazi-deterministic
Language: en
Updated: 2026-10-16

BaZi Basics

By BaziMaster 2026-09-16 Updated 2026-10-16
BaZi is deterministic in its calculation and rule-guided in its interpretation. The pillars, strength score, favourable elements, ten gods and luck cycles all follow written rules. The same birth data therefore gives the same result every time.

## Which parts of a BaZi reading are deterministic?

Most of the structure is arithmetic on a calendar. Each step has one correct answer under a stated convention, and two honest implementations should agree to the digit. Table 1 follows the sample chart through each step. The sample is 王大明, a fictional man born 1988-03-15 at 09:30 in Singapore.

Key facts

- The same birth data or floor plan always gives the same result, which is claim one of the ten method claims at /method.
- Every output line names the classical rule it applies, with a rule id a practitioner can check.
- The sample's clock time 09:30 becomes true solar time 08:16, using longitude 103.8517°E and an equation of time of -9.4 minutes.
- The strength rule has four steps and returns weak Day Master (身弱) with a score of -0.97, from support 6.33 against drain 3.67.
- The sample's luck cycles run forward from the month pillar 乙卯 (Wood Rabbit) and start at age 6.8.
- No generative AI writes any reading, and the engine does not predict events.

Pipeline from birth data through true solar time, four pillars, strength, favourable elements and luck cycles to a reading in which each line cites its rule
Table 1: the sample chart, step by step

Step | Rule | Sample result | 

True solar time | clock converted by longitude and equation of time | 09:30 becomes 08:16 | 

Four pillars | solar terms, Start of Spring (立春) year boundary, sixty-day cycle | 戊辰 (Earth Dragon) 乙卯 己巳 (Earth Snake) 戊辰 | 

Strength | season, support, drain, root | Weak Day Master, score -0.97 | 

Favourable elements | Support-and-restrain method (扶抑法) then climate-adjustment method (調候法) | Fire (火) and Earth (土) | 

Ten gods | each stem's relation to the Day Master | Rob Wealth (劫財) 48.1 %, Seven Killings (七殺) 29.6 % | 

Luck cycles | Yang men and yin women count forward (陽男陰女順行), luck-cycle start (起運) = days to the solar-term boundary (距節日數) / 3 | forward from 乙卯, start age 6.8 | 

The useful god (用神) step uses the four classical methods (support-and-restrain method, climate-adjustment method, bridging element (通關), illness and remedy (病藥)) in a defined order. For the sample, the first two produced Fire and Earth as favourable and Wood (木), Water (水) and Metal (金) as unfavourable. A different order would be a different system, which is why the order is written down.

See these rules applied to your own chart: free BaZi reading →

## How does the strength rule show the idea?

The strength rule is a good test case, because it looks like judgement and is actually four fixed steps. For the sample Day Master 己 (Earth), the engine does the following.

- Season. The month branch 卯 (Rabbit, Wood) is Wood, and Wood controls Earth, so the season state is dead (死), scoring -2.0.

- Support. Peers (Earth 5.33) plus resource (Fire 1.0) give 6.33.

- Drain. Output, wealth and authority combined give 3.67.

- Root. The branches 辰 (Dragon, Earth), 巳 (Snake, Fire) and 辰 hold Earth in their hidden stems, so the Day Master is rooted.

The result is weak Day Master, with a score of -0.97 in an ordinary structure. Anyone can check the arithmetic by hand, which is the point. The engine prints each step with its rule id: the sample's citations list time-policy, strength-4step and dayun-direction, each tied to a named convention.

## Which parts are interpretation?

What a weak Earth Day Master with heavy authority stars means for a career is interpretation. It is still not freeform. The engine holds fixed sentence patterns for each palace and god, and fills them from the computed chart. The month palace template, for example, reads the career headquarters through the month stem's god. For the sample, that god is Seven Killings, which the engine words as raw pressure and discipline imposed from outside.

So the interpretive layer is written by people, in advance, and applied by rule. A sentence in a reading can be traced to a pattern, and the pattern can be argued with. That is a different thing from text produced fresh each time.

Some parts are weaker still, and the engine says so. The life-domain scores, such as learning at 65 and constitution at 67, are labelled a modern synthesis of star shares, symbolic stars and palace checks. They are rule-derived, but they are not classical doctrine (method note).

## Where do schools disagree?

The engine records its choices where traditions differ and marks the choice as disputed. The strength step shows one. The engine reads the month by the branch's own element. The seasonal strength (旺相休囚死) school reads it by the season's element, and the two can differ near a season change. The engine's step text names the alternative and gives an example, so the disagreement is visible in the output.

Strokes for naming follow the Kangxi Dictionary (康熙字典) count on the traditional form. The 81-number verdicts use a two-state scale until a finer cited table is adopted. Those are stated choices, not hidden ones.

See these rules applied to your own chart: free BaZi reading →

## Why does determinism matter when choosing a tool?

A tool that generates fluent text without rules fails in three ways that a rule engine does not. These are logical points about the method, not tests of any named product (method note).

- Calendar edge cases. The Start of Spring boundary, true solar time and the pre-1982 Singapore clock each change a pillar. A rule engine applies them in the same order every time.

- No traceable rule. A sentence produced by pattern completion has no rule id, because no rule produced it. You cannot check it.

- Repeatability. Text generated fresh can differ on each ask. A calculation cannot, so it can be tested.

Fluency is not method. The site's method claims put it plainly: no generative AI writes any reading, and the text is rule output plus hand-written guides.

## Is deterministic the same as fatalistic?

No. The word describes the computation, not your life. The engine states that it does not predict events. It computes classical structures and states their traditional reading. A chart is a starting condition and a map of tendencies, and the readings are framed that way.

The reason to want an exact chart is practical. The actionable layers, such as colours, directions, dates and room choices, then rest on a correct starting point. A wrong hour pillar propagates into every later layer. The ten gods guide shows what a later layer does with the pillars it is given.

## What changes for Singapore and Malaysia readers?

Local time rules are where determinism is tested hardest.

- Year boundary. The BaZi year turns at Start of Spring, which falls on 2027-02-04 in 2027. A late-January birth belongs to the earlier year. The engine gives year pillar 丙午 (Fire Horse) for 2027-01-20 and 丁未 (Fire Goat) for 2027-02-10.

- Time zone. Singapore ran on UTC+7:30 before 1982-01-01 and UTC+8 after it. Malaysia has used UTC+8 since 1982-01-01. The method page states that clock times before 1982 use the offset of that era.

- True solar time. The conversion uses longitude and the equation of time, so a Singapore birth at 09:30 is cast as 08:16.

- Homes. For an HDB flat or condominium unit, the direction and date layers take your door bearing as input. The same bearing gives the same output, which makes the result easy to check against a second tool.

## FAQ

### Is BaZi deterministic?

BaZi is deterministic in its calculation and rule-guided in its interpretation. The pillars, strength score, favourable elements, ten gods and luck cycles all follow written rules. The same birth data therefore gives the same result every time.

### Does deterministic mean my fate is fixed?

No. The word describes the computation, not your life. The engine states that it does not predict events. A chart is a starting condition and a map of tendencies, and the readings are framed that way.

### Which parts of a BaZi reading are interpretation?

The meaning of a chart, such as what a weak Day Master with heavy authority stars means for a career, is interpretation. It is not freeform. The engine holds fixed sentence patterns for each palace and god, written by people in advance.

### Does an AI write my BaZi reading?

No generative AI writes any reading. The text is rule output plus hand-written guides. Every output line names the classical rule it applies, with a rule id a practitioner can check.

### Why might my chart differ between tools in Singapore or Malaysia?

Local time rules are where determinism is tested hardest. The BaZi year turns at Start of Spring, Singapore ran on UTC+7:30 before 1982-01-01, and true solar time shifts the clock. A tool that skips these will cast different pillars.

## Sources and method

- Method claims: the ten claims at /method, including determinism, rule ids per line, true solar time and no generative AI (method note).

- Strength rule: seasonal strength with rooting (通根), in four steps.

- Favourable elements: the four useful god methods, support-and-restrain method, climate-adjustment method, bridging element and illness and remedy.

- Luck cycles: yang men and yin women count forward, yin men and yang women count backward (陰男陽女逆行), with luck-cycle start = days to the solar-term boundary / 3.

- Time convention: the 子平 (classical BaZi school) convention of true solar time.

- Stroke counts: Kangxi Dictionary.

- Interpretive text: fixed sentence patterns written in advance (method note).

Get a reading whose lines each cite a rule at /start, and see how the favourable elements are chosen in useful god colours.
