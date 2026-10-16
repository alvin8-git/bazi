# BaZi (八字) Explained: Pillars and Day Master

Canonical: https://bazifor.me/learn/what-is-bazi
Language: en
Updated: 2026-10-14

BaZi Basics

By BaziMaster 2026-09-16 Updated 2026-10-14
BaZi ("eight characters") is a Chinese calendar system that converts a birth moment into four pillars, each a Heavenly Stem over an Earthly Branch, using solar terms and true solar time. The day stem is the Day Master, the character that stands for you. The pillars are computed exactly; only the reading that follows needs interpretation rules.

## What are the four pillars?

BaZi is often called Chinese astrology, but its first step is a calendar computation. Your birth moment becomes four pairs of characters, the Four Pillars (四柱). Two people born at the same place and minute get the same eight characters, from every competent practitioner, every time.

Each pillar is one Heavenly Stem (天干) sitting on one Earthly Branch (地支):

- Year pillar (年柱) changes at Start of Spring (立春), the "start of spring" solar term, not at Chinese New Year and not on 1 January.

- Month pillar (月柱) is set by solar terms, so each "month" begins at an astronomical moment rather than a calendar date.

- Day pillar (日柱) comes from the 60-day 甲子 (Wood Rat) cycle. Its stem is the Day Master (日主).

- Hour pillar (時柱) is one of twelve two-hour blocks (two-hour period, 時辰), counted on true solar time.

Ten stems and twelve branches combine into a 60-unit cycle (sixty-pair cycle, 六十甲子), so the same day pillar returns every 60 days and the same year pillar every 60 years.

Key facts

- The year pillar changes at Start of Spring, which falls on 2027-02-04 in 2027 (and on 2026-02-04 and 2028-02-04 in the neighbouring years).
- A chart has 4 pillars and 8 characters: 4 stems and 4 branches.
- Singapore clocks ran on UTC+7:30 before 1982-01-01 and on UTC+8 after it.
- Peninsular Malaysia has used UTC+8 since 1982-01-01, so the same correction applies to births there.
- The engine converts clock time to true solar time from longitude and the equation of time, following the 子平 (classical BaZi school) convention.
- Day Master strength is judged with the seasonal strength (旺相休囚死) and rooting (通根) framework.

Sample chart 戊辰 (Earth Dragon) 乙卯 (Wood Rabbit) 己巳 (Earth Snake) 戊辰 laid out as four pillars, with the day stem 己 (yin Earth) marked as the Day Master
See these rules applied to your own chart: free BaZi reading →

## How is a BaZi chart calculated?

The computation has three steps, and none of them involves judgement.

- Fix the moment on the sun's clock. A wall-clock time is a political convention. BaZi uses true solar time, which depends on how far your birthplace sits from the time-zone meridian and on the equation of time (the seasonal drift between sundial and clock). This is the 子平 time convention.

- Find the solar terms. The year turns at Start of Spring and each month turns at a "joint" solar term (節). A person born on 2027-01-20 has the year pillar 丙午 (Fire Horse) and the month pillar 辛丑 (Metal Ox). A person born on 2027-02-10, after Start of Spring, has the year pillar 丁未 (Fire Goat) and the month pillar 壬寅 (Water Tiger). Same Gregorian year, different pillars.

- Read the pillars off the 60-cycle. Each pillar is a stem-branch pair from the 甲子 cycle. For example, the day of 2027-01-20 is 己亥 (Earth Pig), and the day of 2027-02-10 is 庚申 (Metal Monkey).

Branches also contain hidden stems (藏干), which is why two charts with similar surfaces can behave differently. From these mappings, classical technique derives the strength of the Day Master, the favourable elements (useful god, 用神), the Ten Gods (十神) and the ten-year luck cycles (大運).

## What does a worked example look like?

Take the fictional person 王大明, a man born on 1988-03-15 at 09:30 Singapore clock time.

Step 1, true solar time. Singapore sits at longitude 103.8517°E, well west of the UTC+8 meridian, and on 15 March the equation of time is -9.4 minutes. The engine converts 09:30 on the clock to 08:16 true solar time. That matters: 09:30 falls in the 巳 (Snake, Fire) block, but 08:16 falls in the 辰 (Dragon, Earth) block. Skip the correction and the hour pillar is wrong.

Step 2, the pillars. The engine returns 戊辰 (year), 乙卯 (month), 己巳 (day) and 戊辰 (hour). The Day Master is 己, yin Earth.

Step 3, strength. The month branch 卯 (Rabbit, Wood) is wood, and wood restrains earth, so the Day Master is in the dead (死) phase of seasonal strength (method note: the engine scores the phases numerically). Support totals 6.33 against a drain of 3.67, and the roots (rooting) are 辰, 巳 and 辰. The net score is -0.97, so the chart is weak Day Master (身弱).

Step 4, what follows. A weak Day Master calls for support, so the useful gods are Fire and Earth, and the colour families that carry them are red (紅) purple (紫) yellow (黃) brown (棕). His kua is 震 (east), in the East group (東四命). The luck cycles run forward (forward luck cycles, 順行) from 乙卯 and start at age 6.8, counted to the Clear and Bright (清明) term. Each of these lines is one rule applied once, which is why the reading can cite it.

The five elements in this chart relate through two cycles, and the table below is the lookup the engine uses for both.

Element | Generates (生) | Restrains (controls, 剋) | Colour families | 

Wood (木) | Fire (火) | Earth (土) | Green (綠) teal (青) | 

Fire | Earth | Metal (金) | Red purple | 

Earth | Metal | Water (水) | Yellow brown | 

Metal | Water | Wood | White (白) Metal | 

Water | Wood | Fire | Black (黑) blue (藍) | 

See these rules applied to your own chart: free BaZi reading →

## Why does "deterministic" matter?

The computation is exact, and the interpretation follows written rules. When a reading says your Day Master is weak and fire and earth support you, that conclusion comes from a rule you can look up, not from a mood, a template or a chatbot. At bazifor.me every line of a reading cites the rule that produced it, because a claim you cannot check is marketing, not knowledge.

Deterministic does not mean fatalistic. A chart is a starting point. The same pillars read differently once luck cycles and annual years (annual year, 流年) are layered on, and a person's choices are not in the chart at all.

## Which mistakes change the pillars in Singapore and Malaysia?

- Using Chinese New Year as the year boundary. The boundary is Start of Spring, so someone born in late January or early February may belong to the previous year.

- Using the clock instead of the sun. In 王大明's case the correction is 74 minutes and moves the hour from 巳 to 辰.

- Ignoring the pre-1982 clock. A Singapore birth before 1982-01-01 was recorded on UTC+7:30. The engine applies that offset before it computes true solar time.

- Taking a birth time from memory. A time of "around 9" can sit in two different two-hour periods. If the hour is unknown, a reading should say which findings depend on it.

Flats and condominiums do not enter a BaZi chart; they enter the home layer of feng shui, where your Day Master's favourable elements and your kua become colours and directions for each room. See the favourable-elements guide and the bed direction guide for those steps.

## FAQ

### What is BaZi?

BaZi ("eight characters") is a Chinese calendar system that converts a birth moment into four pillars. Each pillar is a Heavenly Stem over an Earthly Branch. The day stem is the Day Master, the character that stands for you.

### Is BaZi just fortune telling?

BaZi is often called Chinese astrology, but its first step is a calendar computation. Two people born at the same place and minute get the same eight characters. Deterministic does not mean fatalistic, and a chart is a starting point.

### What birth details do I need for BaZi in Singapore or Malaysia?

You need the date, a reliable birth time and the place. Singapore clocks ran on UTC+7:30 before 1982-01-01 and UTC+8 after it. Malaysia has used UTC+8 since 1982-01-01. The engine converts the clock to true solar time.

### Is the BaZi year the same as Chinese New Year?

No. The year pillar changes at Start of Spring, not at Chinese New Year and not on 1 January. In 2027 it falls on 2027-02-04. Someone born in late January or early February may belong to the previous year.

### What if I do not know my exact birth time?

A time of "around 9" can sit in two different two-hour periods. If the hour is unknown, a reading should say which findings depend on it. Taking a birth time from memory is one of the common mistakes that change the pillars.

## Sources and method

- Solar-term months and the Start of Spring year boundary: the 子平 calendar convention, with annual and monthly turns at the solar terms.

- Hour pillar: the 子平 true-solar-time convention, with the Singapore (UTC+7:30 before 1982, UTC+8 after) and Malaysian (UTC+8 from 1982) clock offsets applied before conversion (method note).

- Day Master strength: the seasonal strength and rooting framework, with a numeric score (method note).

- Favourable elements: the useful god methods support and restrain (扶抑) then climate adjustment (調候), numbered 1 and 2 in the engine's citations, with illness and remedy (病藥) reported beside them. Bridging element (通關) is not applied to a single chart.

- Ten stems, branches and their combinations: 三命通會 (Ming-era BaZi classic), in the chapters the engine cites on stem pairing, clashes and combinations.

To see your own four pillars with these conversions applied, run the free reading at /start.
