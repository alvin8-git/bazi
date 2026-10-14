# Move-In Date (入宅) Selection: Day Officers

Canonical: https://bazifor.me/learn/move-in-date-selection
Language: en
Updated: 2026-10-08

Dates

By BaziMaster 2026-09-16 Updated 2026-10-08
Move-in date selection (入宅擇日) is a filter over the calendar. It keeps days whose day officer (建除) is Completion (成), Settle (定) or Open (開), then removes days whose branch clashes with the occupants or the house. Because the filters are fixed rules, a computer can run them exactly and a careful almanac reader gets the same days.

## How does the day-officer rule work?

Every day carries one of twelve officers (twelve day officers, 建除十二神). The officer is the offset of the day's branch from the month's branch: the day whose branch equals the month branch is Establish (建), the next branch is Remove (除), and so on round the cycle of twelve. This is the twelve day officers (十二建除) rule of the 協紀辨方書 (Qing almanac manual) tradition.

For moving in, the engine keeps three officers: Completion, Settle and Open. Everything else is passed over. A day whose branch clashes the month branch is a Month Breaker (月破) day, the hard avoid.

Key facts

- The 12 day officers run from Establish to Close (閉), and the engine keeps 3 of them for move-in: Completion, Settle and Open.
- Officer = (day branch minus month branch) modulo 12, counted from Establish.
- A move-in day is also dropped if its branch clashes an occupant's year branch, clashes the sitting branch or equals the year's Grand Duke (太歲) branch.
- In 2027 the Grand Duke branch is 未 (SW1, 202.5-217.5 degrees) and the year starts at Start of Spring (立春), 2027-02-04.
- For the sample household, facing 14.0 degrees, the engine returns 9 auspicious days between 2027-03-01 and 2027-04-30.
- The first of those is 2027-03-04, a 壬午 (Water Horse) day with officer Settle.

Flow chart of move-in date selection: twelve day officers, keep Completion Settle Open, remove branch clashes, then choose an entry hour
Get move-in dates for your own household: free home tool →

## What are the twelve officers worth?

The engine's date selection (擇日) layer rates each officer with a score (method note: these are the engine's weights, not a classical table). The move-in filter itself is simpler: it keeps Completion, Settle and Open and orders them Completion first, then Settle, then Open.

Cycle position | Officer | Engine score | Move-in use | 

0 | Establish | +0.5 | passed over | 

1 | Remove | +0.5 | passed over | 

2 | Full (滿) | +0.5 | passed over | 

3 | Neutral (平) | -0.5 | passed over | 

4 | Settle | +1.0 | kept for move-in | 

5 | Hold (執) | +0.0 | passed over | 

6 | Destruction | -2.0 | passed over | 

7 | Danger (危) | -1.0 | passed over | 

8 | Completion | +2.0 | kept for move-in | 

9 | Receive (收) | +0.0 | passed over | 

10 | Open | +1.5 | kept for move-in | 

11 | Close | -1.0 | passed over | 

Cycle position 0 is the day whose branch equals the month branch. The scores are used when a day is rated for a household, where destruction at -2.0 is the worst and Completion at +2.0 the best.

## Which days are struck out by clashes?

Each branch clashes with the one opposite it: 子 (Rat, Water) and 午 (Horse, Fire), 丑 (Ox, Earth) and 未, 寅 (Tiger, Wood) and 申 (Monkey, Metal), 卯 (Rabbit, Wood) and 酉 (Rooster, Metal), 辰 (Dragon, Earth) and 戌 (Dog, Earth), 巳 (Snake, Fire) and 亥 (Pig, Water). After the officer filter the engine drops a day when its branch:

- Clashes any occupant's year branch (Six Clash, 六沖), so the move does not collide with anyone who will live there.

- Clashes the sitting branch (clashes the sitting, 沖坐山), the branch of the direction the house sits toward, derived from the facing bearing.

- Equals the year's Grand Duke branch (meets the Grand Duke, 值太歲). In 2027 that branch is 未.

The engine can also rate a day for each household member, using a clash with their year branch (clashes the zodiac animal, 沖生肖), a clash with their day-pillar branch, and a Six Harmony (六合) bonus. Those are softer, personal layers on top of the move-in filter.

Last, the engine can return entry hours for a chosen day, computed from the day branch, the occupants' branches and the facing.

Get move-in dates for your own household: free home tool →

## What does a worked example look like?

The sample inputs are the occupant branches 辰 and 巳 (the sample person's year and day branches, passed to the engine as a two-branch household). The facing is 14.0 degrees, and the window is 2027-03-01 to 2027-04-30. A 辰 occupant removes 戌 days and a 巳 occupant removes 亥 days, and 未 days are removed as Grand Duke.

The engine returns 9 days. The first four listed are:

Date | Weekday | Day pillar | Officer | 

2027-03-04 | Thu | 壬午 | Settle | 

2027-04-11 | Sun | 庚申 (Metal Monkey) | Settle | 

2027-04-23 | Fri | 壬申 (Water Monkey) | Settle | 

2027-03-11 | Thu | 己丑 (Earth Ox) | Open | 

You can check the officers by hand with the offset rule. On 2027-03-11 the month branch is 卯 and the day branch is 丑, which sits 10 places on from 卯 in the cycle of twelve, and position 10 is Open. On 2027-04-11 the month branch is 辰 and the day branch is 申, 4 places on, which is Settle. Other days in the engine's output show why most are passed over: 2027-03-06 (甲申, Wood Monkey) is Hold, 2027-03-15 (癸巳, Water Snake) is Full and 2027-04-08 (丁巳, Fire Snake) is Remove.

Nine days out of a 61-day window is a short list, which is why the window should be generous. The filter knows nothing about your leave days, lift bookings or key-collection date, so choose the window first, take the engine's list, then fit practical constraints to it. If none of the nine works, widen the window rather than relaxing a clash rule.

## What changes for Singapore and Malaysia homes?

- Facing. For an HDB flat or condominium unit, take the facing from the unit's main door, outward, as a bearing in degrees. The sitting branch follows from it, so a different bearing can change which days survive.

- Year boundary. The 2027 year begins at Start of Spring on 2027-02-04. The positions below apply to the 丁未 (Fire Goat) year that opens on that date.

- 2027 year positions. Grand Duke is at 未, SW1. Year Breaker (歲破) is at 丑, NE1, 22.5-37.5 degrees. Three Killings (三煞) covers the west, 232.5-307.5 degrees. A door facing 14.0 degrees lies outside all three bands. These are rule-derived positions from the year spirits (年神) rules of the 協紀辨方書.

- Time. Dates here follow the calendar as set by the solar terms, which the engine takes from an astronomical library. Singapore and Malaysia both use UTC+8 today.

## FAQ

### How is a move-in date chosen in feng shui?

Move-in date selection is a filter over the calendar. It keeps days whose day officers officer is Completion, Settle or Open. It then removes days whose branch clashes with the occupants or the house. Fixed rules mean a careful almanac reader gets the same days.

### What are the twelve day officers?

Every day carries one of twelve officers (twelve day officers), set by the day branch's offset from the month branch. The day whose branch equals the month branch is Establish, and the next is Remove. For moving in, only Completion, Settle and Open are kept.

### Which days are struck out for a house move?

After the officer filter, a day is dropped if its branch clashes an occupant's year branch or the sitting branch. A day is also dropped if it equals the year's Grand Duke branch. In 2027 the Grand Duke branch is 未. A day that clashes the month branch is destruction, the hard avoid.

### What do I need to give for a move-in date in Singapore or Malaysia?

You need the occupants' year branches, the facing bearing in degrees and a date window. For an HDB flat or condo, take the facing from the unit's main door, outward. A different bearing can change which days survive.

### What if none of the suggested days works for my schedule?

The filter knows nothing about your leave days, lift bookings or key collection date. Choose the window first, take the list, then fit practical constraints to it. If none works, widen the window rather than relaxing a clash rule.

## Sources and method

- Day officers: the twelve day officers rule, with the officer set by the day branch's offset from the month branch.

- Kept officers: Completion, Settle and Open for move-in, the engine's convention (method note).

- Month breaker: Month Breaker, the day whose branch clashes the month branch, treated as a hard avoid.

- Clash filters: the Six Clash pairs applied to occupants' year branches, the sitting branch and the Grand Duke branch.

- 2027 positions: the year spirits position rules of 協紀辨方書, applied to the 丁未 year.

- Scope: the engine does not run the full almanac layers (twenty-eight mansions, individual stars), so its verdict may differ from a printed almanac (method note).

Run the same filter for your own household with the free home tool at /fengshui, which reads every occupant's year branch and your facing.
