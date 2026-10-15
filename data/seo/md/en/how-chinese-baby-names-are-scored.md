# How Chinese Baby Names Are Scored

Canonical: https://bazifor.me/learn/how-chinese-baby-names-are-scored
Language: en
Updated: 2026-10-08

Naming

By BaziMaster 2026-10-08 Updated 2026-10-08
A Chinese baby name score is a 100-point total built from seven checked parts: the child's favourable element (useful god), the five grids, the three talents, meaning, sound, gender fit and data confidence. Each part has a fixed weight, so the final grade can be traced back to the rule behind every point.

## How is a name scored out of 100?

A name is rarely good or bad on one test. A character can carry the right element, have an excellent stroke count and still sound like something embarrassing. The builder at bazifor.me therefore scores seven parts, weights them, and adds them up. Nothing is hidden: the weights below are the ones the engine uses.

Part | Weight | What it checks | 

Useful god | 30 | Does each character carry an element the child's chart needs? | 

Five Grids | 25 | Are the five stroke-count grids lucky or unlucky? | 

Three Talents | 15 | Do the elements of the heaven, person and earth grids support each other? | 

Character meaning (字义) | 10 | What do the characters mean, in 16 meaning categories? | 

Sound (音韵) | 5 | Do the tones and sounds read well, and do they collide with a bad word? | 

Gender fit (性别) | 5 | Does the name fit the child's gender, using character tags? | 

Confidence (可信度) | 10 | How far can the engine trust the data behind the other parts? | 

The seven weights add up to 100. The sum of the weights is the highest total a name can reach.

Key facts

- The seven weights are useful god 30, Five Grids 25, Three Talents 15, character meaning 10, sound 5, gender fit 5 and confidence 10.
- The grade bands are 90 and above excellent (上佳), 80 and above good (佳), 65 and above fair (可), and below 65 needs a second look (待斟酌).
- A strong sound hit (an English profanity, a homophone or a severe homophone) caps the grade at needs a second look whatever the total.
- The sound layer is backed by 303 sound-alike entries, of which 79 are severe, and 72 English reading checks.
- 478 characters carry meaning tags, in 16 meaning categories, and 171 characters carry gender tags.
- Strokes follow the Kangxi Dictionary (康熙字典) count, which uses the traditional form of each character.

Score a name for your own baby: free name builder →

## Why does useful god carry the most weight?

Because it is the part that comes from the child, not from the name. The useful god is the element the child's BaZi chart needs most, chosen by support and restrain (扶抑), climate adjustment (調候), bridging element (通關) and illness and remedy (病藥). See what a useful god is for how it is found. A character carries an element, and the engine gives each character a role score against the child's chart:

- Useful god: 1.0

- Favourable (喜): 0.7

- Undetermined (未定), for a character whose element is not set: 0.3

- Unfavourable (忌): 0.0

The 30 points scale with these role scores (method note: the exact blending across characters is the engine's). That is why the child's birth moment matters for naming. The chart behind the useful god depends on true solar time. For a birth in Singapore or Malaysia the clock is UTC+8 (UTC+7:30 in Singapore before 1982), and a birth near a two-hour boundary can change the hour pillar and with it the useful god. The year changes at Start of Spring (立春), so a late January or early February birth may belong to the previous year.

## How do the five grids work?

The Five Grids are five numbers derived from the stroke counts of the surname and given name: the Heaven grid (天格), Person grid (人格), Earth grid (地格), Outer grid (外格) and Total grid (總格). Each number is looked up in the 81-number system (81numerology (數理)), which marks it auspicious (吉) or adverse (凶). This is a modern naming-school convention, not a classical rule, and the engine uses only the two-state auspicious/adverse reading (method note).

Stroke counts come from the Kangxi Dictionary. This matters because the dictionary uses the traditional form: 祿 (prosperity) has more strokes than the simplified 禄, so a name typed in simplified Chinese must be counted in its traditional form.

The 25 points are split across the grids by name length:

Name type | Person grid | Earth grid | Total grid | Outer grid | Total | 

Two-character given name (双名) | 8 | 7 | 7 | 3 | 25 | 

One-character given name (单名) | 15 | 10 | not scored | not scored | 25 | 

One-character given name with a two-character surname (复姓) | 8 | 10 | 7 | not scored | 25 | 

With a two-character surname such as 欧阳 or 司马, the Person grid and the Total grid are two different numbers, so each is scored on its own. The 15 points that one shared number carries with a one-character surname are split the way the two-character-given-name layout splits them: 8 for the Person grid and 7 for the Total grid. This split is the engine's choice, not a number from a text.

The Heaven grid is not scored in any layout: it comes from the surname alone, so no choice of given name changes it (method note).

## Which element relations count in the Three Talents?

The Three Talents are the elements of the Heaven grid, Person grid and Earth grid. The engine reads the relation between the elements and gives each relation a factor:

Relation | Factor | 

Generates (生) | 1.0 | 

Same element (比) | 0.8 | 

Drains (洩) | 0.4 | 

The person element restrains (人剋) | 0.2 | 

Restrained (被剋) | 0.0 | 

The 15 points scale with these factors. The relations follow the five-element generating and restraining cycles shown below.

The five-element generating and restraining cycles used to read the Three Talents relations: wood feeds fire, fire feeds earth, earth feeds metal, metal feeds water, water feeds wood

## How does the sound layer work?

The sound part is worth 5 points and starts from a full score. It subtracts penalties for patterns that make a name awkward to say, and for collisions with other words. The penalties are the engine's own (method note):

Pattern | Penalty | 

Same tone repeated | 0.4 | 

Two third tones together | 0.2 | 

Ending on a neutral tone | 0.2 | 

Same syllable repeated | 0.4 | 

Reduplication | 0.1 | 

Same initial | 0.2 | 

Same final | 0.2 | 

Cap on all repeat penalties together | 0.4 | 

Near-homophone of a bad word | 0.5 | 

Tone-different homophone | 0.7 | 

Homophone | 1.0 | 

Severe homophone | 1.0 | 

English tease | 0.5 | 

English profanity | 1.0 | 

Sound-alike checks run against 303 dictionary entries (79 of them severe) and 72 English reading checks. Three kinds of hit are strong: an English profanity, a homophone, and a severe homophone. A strong hit does more than lose points. It caps the grade at needs a second look whatever the total, because a name that sounds like a swear word is not rescued by lucky strokes. Weaker hits, such as a near-homophone or an English tease, only cost points.

Score a name for your own baby: free name builder →

## What does the meaning and gender layer add?

The character meaning part (10 points) looks up each character in a table of 478 tagged characters across 16 meaning categories. The result also produces a short interpretation of the name, written from those tags. The gender fit part (5 points) uses 171 gender tags, which check the name against the child's gender.

## What does a worked example look like?

Take the fictional girl's name 王禄婷 (traditional 王祿婷), for a child born on 2026-03-15 at 09:30.

- Strokes (Kangxi Dictionary): 王 4, 祿 13, 婷 12.

- Five grids: Heaven grid 5 (Earth, 土), Person grid 17 (Metal, 金), Earth grid 25 (Earth), Outer grid 13 (Fire, 火), Total grid 29 (Water, 水). All five read auspicious, so Five Grids earns the full 25.

- Three Talents: Earth Metal Earth. The engine's detail lines read 天土生人金 ×1.0 and 地土生人金 ×0.4, the verdict is centre (中), and the part earns 10.5 of 15.

- Sound: tones 2, 4, 2 (wang, lu, ting). There are no findings, so the part earns the full 5.0.

- The other parts: useful god 30.0, character meaning 10.0, gender fit 5.0 and confidence 10.0.

The total is 30 + 25 + 10.5 + 10 + 5 + 5 + 10 = 95.5, which lands in the excellent band. The only points lost are the 4.5 in the Three Talents part. The engine's reading of the name is: 既福禄双全，又亭亭玉立, or "a name suggesting blessing and prosperity; graceful and poised."

A name scoring 89.9 would read good, one scoring 79 would read fair, and anything under 65 reads needs a second look.

## How are the grades set?

Total | Grade | English | 

90 and above | Excellent | excellent | 

80 to under 90 | Good | good | 

65 to under 80 | Fair | fair | 

under 65 | Needs a second look | reconsider | 

"Reconsider" does not say the name is wrong for your family. It says the rules have found a reason to look again.

## FAQ

### How is a Chinese baby name scored out of 100?

The score has seven parts: useful god 30, Five Grids 25, Three Talents 15, character meaning 10, sound 5, gender fit 5 and confidence 10. The weights add up to 100. Nothing is hidden, so each point traces back to a rule.

### Why does the useful god carry the most weight in a baby name?

It comes from the child, not from the name. The useful god is the element the child's BaZi chart needs most. A character carries an element, and the engine gives it a role score against that chart, from 1.0 for useful god down to 0.0 for unfavourable.

### What are the grade bands for a name score?

A total of 90 and above is excellent, 80 and above is good, 65 and above is fair, and below 65 is needs a second look. A strong sound hit, such as a profanity or a severe homophone, caps the grade at needs a second look whatever the total.

### Does my baby's birth place or time matter for naming in Singapore or Malaysia?

Yes, because the useful god depends on the chart, and the chart depends on true solar time. The clock is UTC+8, and UTC+7:30 in Singapore before 1982. A birth near a two-hour boundary can change the hour pillar and the useful god.

### Should I count strokes in simplified or traditional characters?

Strokes follow the Kangxi Dictionary, which uses the traditional form of each character. For example, 祿 has more strokes than the simplified 禄. A name typed in simplified Chinese must therefore be counted in its traditional form.

## Sources and method

- Stroke counts: the Kangxi Dictionary, in traditional character forms.

- Five Grids and the 81 numbers: a modern naming-school convention (method note), with only the two-state auspicious/adverse reading used.

- Three Talents relations: the five-element generating and restraining cycles, with the factors above (method note).

- Useful god: the four methods support and restrain, climate adjustment, bridging element and illness and remedy, applied to the child's chart under the 子平 (classical BaZi school) true-solar-time convention.

- Sound, meaning, gender and confidence parts, and the grade cap: the engine's own rules and data tables (method note), not classical sources.

Score a name for your own child in the baby name builder at /baby, with the full breakdown and the rule behind every part.
