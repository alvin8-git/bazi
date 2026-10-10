"""ONE glossary for every English surface of bazifor.me (presentation only).

Rule (English pages): English is the primary text. The first time a term appears in a
rendering context (a page, a card, one API response) it carries the Chinese once in
parentheses — "Day Master (日主)" — and after that it is English only.  Terms with no
accepted English rendering (heavenly stems, earthly branches, trigrams, symbolic-star
names) keep the Chinese and add pinyin plus a short gloss once — "甲 Jia (yang Wood)",
"坎 Kan (north)", "文昌 Wenchang (study star)" — then pinyin only.

Nothing here touches a computation: engine modules keep their Chinese keys and codes;
only the strings that are printed go through `Gloss` / `en()` / `Gloss.text()`.

web/glossary.js is GENERATED from this file (scripts/glossary_js.py) so the browser pages
use the same table and the same first-use rule; tests/test_english_surfaces.py checks that
the two stay in sync.
"""
from __future__ import annotations

import re

# term -> (English, pinyin, gloss, category).  English "" = no accepted English rendering:
# the term is shown as Chinese + pinyin + gloss on first use, pinyin after.
TERMS: dict[str, tuple[str, str, str, str]] = {}


def _add(cat: str, rows: list[tuple[str, str, str, str]]) -> None:
    for term, en_, py, gl in rows:
        TERMS[term] = (en_, py, gl, cat)


# ---------------------------------------------------------------- core BaZi vocabulary
_add("core", [
    ("八字", "BaZi", "bā zì", "eight characters"),
    ("四柱", "Four Pillars", "sì zhù", ""),
    ("四柱八字", "BaZi chart", "sì zhù bā zì", ""),
    ("命盘", "birth chart", "mìng pán", ""),
    ("命盤", "birth chart", "mìng pán", ""),
    ("排盘", "chart calculation", "pái pán", ""),
    ("排盤", "chart calculation", "pái pán", ""),
    ("八字排盘", "BaZi chart calculator", "bā zì pái pán", ""),
    ("命书", "the reading", "mìng shū", ""),
    ("命書", "the reading", "mìng shū", ""),
    ("命卡", "chart snapshot", "mìng kǎ", ""),
    ("本命", "natal chart", "běn mìng", ""),
    ("日主", "Day Master", "rì zhǔ", ""),
    ("日元", "Day Master", "rì yuán", ""),
    ("天干", "Heavenly Stem", "tiān gàn", ""),
    ("地支", "Earthly Branch", "dì zhī", ""),
    ("干支", "stem-branch pair", "gàn zhī", ""),
    ("藏干", "hidden stems", "cáng gàn", ""),
    ("支藏干", "hidden stems", "zhī cáng gàn", ""),
    ("年柱", "Year Pillar", "nián zhù", ""),
    ("月柱", "Month Pillar", "yuè zhù", ""),
    ("日柱", "Day Pillar", "rì zhù", ""),
    ("時柱", "Hour Pillar", "shí zhù", ""),
    ("年", "Year", "nián", ""),
    ("月", "Month", "yuè", ""),
    ("日", "Day", "rì", ""),
    ("時", "Hour", "shí", ""),
    ("五行", "Five Elements", "wǔ xíng", ""),
    ("五行占比", "element balance", "wǔ xíng zhàn bǐ", ""),
    ("十神", "Ten Gods", "shí shén", ""),
    ("六親", "family roles", "liù qīn", ""),
    ("用神", "useful god", "yòng shén", ""),
    ("喜神", "favourable element", "xǐ shén", ""),
    ("忌神", "unfavourable element", "jì shén", ""),
    ("喜用", "favourable elements", "xǐ yòng", ""),
    ("喜", "favourable", "xǐ", ""),
    ("忌", "unfavourable", "jì", ""),
    ("避", "avoid", "bì", ""),
    ("強弱", "strength", "qiáng ruò", ""),
    ("身強", "strong Day Master", "shēn qiáng", ""),
    ("身弱", "weak Day Master", "shēn ruò", ""),
    ("中和", "balanced Day Master", "zhōng hé", ""),
    ("從格", "follow structure", "cóng gé", ""),
    ("格局", "chart structure", "gé jú", ""),
    ("得令", "in season", "dé lìng", ""),
    ("失令", "out of season", "shī lìng", ""),
    ("有根", "rooted", "yǒu gēn", ""),
    ("通根", "rooting", "tōng gēn", ""),
    ("扶抑", "support and restrain", "fú yì", ""),
    ("扶抑法", "support-and-restrain method", "fú yì fǎ", ""),
    ("調候", "climate adjustment", "tiáo hòu", ""),
    ("調候法", "climate-adjustment method", "tiáo hòu fǎ", ""),
    ("病藥", "illness and remedy", "bìng yào", ""),
    ("通關", "bridging element", "tōng guān", ""),
    ("大運", "luck cycles", "dà yùn", ""),
    ("流年", "annual year", "liú nián", ""),
    ("流月", "monthly pillar", "liú yuè", ""),
    ("小運", "minor luck", "xiǎo yùn", ""),
    ("起運", "luck-cycle start", "qǐ yùn", ""),
    ("順行", "forward luck cycles", "shùn xíng", ""),
    ("逆行", "reverse luck cycles", "nì xíng", ""),
    ("時運", "timing", "shí yùn", ""),
    ("时运", "timing", "shí yùn", ""),
    ("生肖", "zodiac animal", "shēng xiào", ""),
    ("命宮", "Life Palace", "mìng gōng", ""),
    ("胎元", "Conception Pillar", "tāi yuán", ""),
    ("真太陽時", "true solar time", "zhēn tài yáng shí", ""),
    ("納音", "Nayin sound element", "nà yīn", ""),
    ("十二長生", "twelve life stages", "shí èr cháng shēng", ""),
    ("神煞", "symbolic stars", "shén shà", ""),
    ("綜合論斷", "the synthesis", "zōng hé lùn duàn", ""),
    ("命卦", "Kua number", "mìng guà", ""),
    ("命星", "natal star", "mìng xīng", ""),
    ("東四命", "East group", "dōng sì mìng", ""),
    ("西四命", "West group", "xī sì mìng", ""),
    ("合婚", "pair compatibility", "hé hūn", ""),
    ("立春", "Start of Spring", "lì chūn", ""),
    ("節氣", "solar term", "jié qì", ""),
    ("節", "solar-term boundary", "jié", ""),
    ("農曆", "lunar calendar", "nóng lì", ""),
    ("陽曆", "solar calendar", "yáng lì", ""),
    ("陰", "yin", "yīn", ""),
    ("陽", "yang", "yáng", ""),
    ("陰陽", "yin and yang", "yīn yáng", ""),
    ("吉", "auspicious", "jí", ""),
    ("凶", "adverse", "xiōng", ""),
    ("平", "neutral", "píng", ""),
    ("大吉", "very auspicious", "dà jí", ""),
    ("小吉", "mildly auspicious", "xiǎo jí", ""),
    ("吉凶", "fortune", "jí xiōng", ""),
    ("宜", "favourable for", "yí", ""),
    ("不宜", "unfavourable for", "bù yí", ""),
    ("擇日", "date selection", "zé rì", ""),
    ("入宅", "move-in", "rù zhái", ""),
    ("入宅擇日", "move-in date selection", "rù zhái zé rì", ""),
    ("風水", "feng shui", "fēng shuǐ", ""),
    ("宅運", "home feng shui", "zhái yùn", ""),
    ("性格", "personality", "xìng gé", ""),
])

# ---------------------------------------------------------------- five elements + cycles
_add("element", [
    ("木", "Wood", "mù", ""), ("火", "Fire", "huǒ", ""), ("土", "Earth", "tǔ", ""),
    ("金", "Metal", "jīn", ""), ("水", "Water", "shuǐ", ""),
    ("生", "generates", "shēng", ""), ("剋", "controls", "kè", ""), ("克", "controls", "kè", ""),
    ("相生", "feeding cycle", "xiāng shēng", ""), ("相剋", "controlling cycle", "xiāng kè", ""),
    ("洩", "drains", "xiè", ""), ("比", "same element", "bǐ", ""),
    ("旺", "prosperous", "wàng", ""), ("相", "assisting", "xiàng", ""), ("休", "resting", "xiū", ""),
    ("囚", "confined", "qiú", ""), ("死", "dead", "sǐ", ""),
    ("旺相休囚死", "seasonal strength", "wàng xiàng xiū qiú sǐ", ""),
])

# ---------------------------------------------------------------- ten gods + groups
_add("tengod", [
    ("比肩", "Friend", "bǐ jiān", ""), ("劫財", "Rob Wealth", "jié cái", ""),
    ("食神", "Eating God", "shí shén", ""), ("傷官", "Hurting Officer", "shāng guān", ""),
    ("偏財", "Indirect Wealth", "piān cái", ""), ("正財", "Direct Wealth", "zhèng cái", ""),
    ("七殺", "Seven Killings", "qī shā", ""), ("正官", "Direct Officer", "zhèng guān", ""),
    ("偏印", "Indirect Resource", "piān yìn", ""), ("正印", "Direct Resource", "zhèng yìn", ""),
    ("梟神", "Indirect Resource", "xiāo shén", ""),
    ("比劫", "peers", "bǐ jié", ""), ("印", "resource", "yìn", ""), ("印星", "resource", "yìn xīng", ""),
    ("食傷", "output", "shí shāng", ""), ("財", "wealth", "cái", ""), ("財星", "wealth", "cái xīng", ""),
    ("官殺", "authority", "guān shā", ""), ("官星", "authority star", "guān xīng", ""),
    ("財庫", "wealth vault", "cái kù", ""),
])

# ---------------------------------------------------------------- twelve life stages
_add("stage", [
    ("長生", "Birth", "cháng shēng", ""), ("沐浴", "Bath", "mù yù", ""),
    ("冠帶", "Coming of Age", "guān dài", ""), ("臨官", "Officer", "lín guān", ""),
    ("帝旺", "Peak", "dì wàng", ""), ("衰", "Decline", "shuāi", ""), ("病", "Illness", "bìng", ""),
    ("墓", "Tomb", "mù", ""), ("絕", "Extinction", "jué", ""), ("胎", "Conception", "tāi", ""),
    ("養", "Nurture", "yǎng", ""),
])

# ---------------------------------------------------------------- nayin (sound elements)
_add("nayin", [
    ("海中金", "Sea Metal", "hǎi zhōng jīn", ""), ("爐中火", "Furnace Fire", "lú zhōng huǒ", ""),
    ("大林木", "Great Forest Wood", "dà lín mù", ""), ("路旁土", "Roadside Earth", "lù páng tǔ", ""),
    ("劍鋒金", "Sword-edge Metal", "jiàn fēng jīn", ""), ("山頭火", "Hilltop Fire", "shān tóu huǒ", ""),
    ("澗下水", "Ravine Water", "jiàn xià shuǐ", ""), ("城頭土", "City-wall Earth", "chéng tóu tǔ", ""),
    ("白蠟金", "White Wax Metal", "bái là jīn", ""), ("楊柳木", "Willow Wood", "yáng liǔ mù", ""),
    ("泉中水", "Spring Water", "quán zhōng shuǐ", ""), ("屋上土", "Rooftop Earth", "wū shàng tǔ", ""),
    ("霹靂火", "Thunderbolt Fire", "pī lì huǒ", ""), ("松柏木", "Pine Wood", "sōng bǎi mù", ""),
    ("長流水", "Long River Water", "cháng liú shuǐ", ""), ("砂中金", "Sand Metal", "shā zhōng jīn", ""),
    ("沙中金", "Sand Metal", "shā zhōng jīn", ""),
    ("山下火", "Foothill Fire", "shān xià huǒ", ""), ("平地木", "Flatland Wood", "píng dì mù", ""),
    ("壁上土", "Wall Earth", "bì shàng tǔ", ""), ("金箔金", "Gold-leaf Metal", "jīn bó jīn", ""),
    ("覆燈火", "Lamp Fire", "fù dēng huǒ", ""), ("天河水", "Sky River Water", "tiān hé shuǐ", ""),
    ("大驛土", "Highway Earth", "dà yì tǔ", ""), ("釵釧金", "Jewellery Metal", "chāi chuàn jīn", ""),
    ("桑柘木", "Mulberry Wood", "sāng zhè mù", ""), ("大溪水", "Great Stream Water", "dà xī shuǐ", ""),
    ("沙中土", "Sand Earth", "shā zhōng tǔ", ""), ("天上火", "Sky Fire", "tiān shàng huǒ", ""),
    ("石榴木", "Pomegranate Wood", "shí liú mù", ""), ("大海水", "Ocean Water", "dà hǎi shuǐ", ""),
])

# ---------------------------------------------------------------- zodiac animals
_add("animal", [
    ("鼠", "Rat", "shǔ", ""), ("牛", "Ox", "niú", ""), ("虎", "Tiger", "hǔ", ""),
    ("兔", "Rabbit", "tù", ""), ("龍", "Dragon", "lóng", ""), ("蛇", "Snake", "shé", ""),
    ("馬", "Horse", "mǎ", ""), ("羊", "Goat", "yáng", ""), ("猴", "Monkey", "hóu", ""),
    ("雞", "Rooster", "jī", ""), ("狗", "Dog", "gǒu", ""), ("豬", "Pig", "zhū", ""),
])

# ---------------------------------------------------------------- stems / branches (no English)
_STEM_ROWS = [("甲", "jiǎ", "yang Wood"), ("乙", "yǐ", "yin Wood"), ("丙", "bǐng", "yang Fire"),
              ("丁", "dīng", "yin Fire"), ("戊", "wù", "yang Earth"), ("己", "jǐ", "yin Earth"),
              ("庚", "gēng", "yang Metal"), ("辛", "xīn", "yin Metal"), ("壬", "rén", "yang Water"),
              ("癸", "guǐ", "yin Water")]
_BRANCH_ROWS = [("子", "zǐ", "Rat, Water"), ("丑", "chǒu", "Ox, Earth"), ("寅", "yín", "Tiger, Wood"),
                ("卯", "mǎo", "Rabbit, Wood"), ("辰", "chén", "Dragon, Earth"), ("巳", "sì", "Snake, Fire"),
                ("午", "wǔ", "Horse, Fire"), ("未", "wèi", "Goat, Earth"), ("申", "shēn", "Monkey, Metal"),
                ("酉", "yǒu", "Rooster, Metal"), ("戌", "xū", "Dog, Earth"), ("亥", "hài", "Pig, Water")]
_add("stem", [(t, "", py, gl) for t, py, gl in _STEM_ROWS])
_add("branch", [(t, "", py, gl) for t, py, gl in _BRANCH_ROWS])

# ---------------------------------------------------------------- trigrams / palaces (no English)
_add("trigram", [
    ("坎", "", "kǎn", "north"), ("坤", "", "kūn", "southwest"), ("震", "", "zhèn", "east"),
    ("巽", "", "xùn", "southeast"), ("乾", "", "qián", "northwest"), ("兌", "", "duì", "west"),
    ("艮", "", "gèn", "northeast"), ("離", "", "lí", "south"), ("中宮", "", "zhōng gōng", "centre palace"),
])

# ---------------------------------------------------------------- directions
_add("direction", [
    ("北", "north", "běi", ""), ("南", "south", "nán", ""), ("東", "east", "dōng", ""),
    ("西", "west", "xī", ""), ("東北", "northeast", "dōng běi", ""), ("東南", "southeast", "dōng nán", ""),
    ("西北", "northwest", "xī běi", ""), ("西南", "southwest", "xī nán", ""), ("中", "centre", "zhōng", ""),
    ("方位", "compass directions", "fāng wèi", ""),
])

# ---------------------------------------------------------------- eight-house (八宅) stars
_add("bazhai", [
    ("八宅", "Eight House", "bā zhái", ""),
    ("遊年", "eight-house stars", "yóu nián", ""),
    ("生氣", "Vitality", "shēng qì", ""), ("天醫", "Heavenly Doctor", "tiān yī", ""),
    ("延年", "Longevity", "yán nián", ""), ("伏位", "Stability", "fú wèi", ""),
    ("禍害", "Mishap", "huò hài", ""), ("六煞", "Six Killings", "liù shà", ""),
    ("五鬼", "Five Ghosts", "wǔ guǐ", ""), ("絕命", "Severed Fate", "jué mìng", ""),
    ("東四宅", "East-group house", "dōng sì zhái", ""), ("西四宅", "West-group house", "xī sì zhái", ""),
    ("宅卦", "house trigram", "zhái guà", ""), ("坐", "sitting", "zuò", ""), ("向", "facing", "xiàng", ""),
    ("坐向", "sitting and facing", "zuò xiàng", ""),
    ("太極點", "centre point", "tài jí diǎn", ""), ("財位", "wealth spot", "cái wèi", ""),
    ("文昌位", "study spot", "wén chāng wèi", ""), ("明財位", "visible wealth spot", "míng cái wèi", ""),
])

# ---------------------------------------------------------------- flying stars (玄空飛星)
_add("flyingstar", [
    ("玄空飛星", "Flying Stars", "xuán kōng fēi xīng", ""), ("飛星", "flying stars", "fēi xīng", ""),
    ("玄空", "Flying Stars school", "xuán kōng", ""),
    ("一白", "1 White", "yī bái", ""), ("二黑", "2 Black", "èr hēi", ""), ("三碧", "3 Jade", "sān bì", ""),
    ("四綠", "4 Green", "sì lǜ", ""), ("五黃", "5 Yellow", "wǔ huáng", ""), ("六白", "6 White", "liù bái", ""),
    ("七赤", "7 Red", "qī chì", ""), ("八白", "8 White", "bā bái", ""), ("九紫", "9 Purple", "jiǔ zǐ", ""),
    ("貪狼", "Greedy Wolf", "tān láng", ""), ("巨門", "Giant Door", "jù mén", ""),
    ("祿存", "Prosperity Keeper", "lù cún", ""), ("文曲", "Literary Curve", "wén qū", ""),
    ("廉貞", "Chaste Star", "lián zhēn", ""), ("武曲", "Military Curve", "wǔ qū", ""),
    ("破軍", "Army Breaker", "pò jūn", ""), ("左輔", "Left Assistant", "zuǒ fǔ", ""),
    ("右弼", "Right Assistant", "yòu bì", ""),
    ("病符", "illness star", "bìng fú", ""), ("是非", "quarrel star", "shì fēi", ""),
    ("元運", "period", "yuán yùn", ""), ("運", "period", "yùn", ""), ("運星", "period star", "yùn xīng", ""),
    ("山星", "mountain star", "shān xīng", ""), ("向星", "facing star", "xiàng xīng", ""),
    ("年星", "annual star", "nián xīng", ""), ("流年飛星", "annual flying stars", "liú nián fēi xīng", ""),
    ("旺山旺向", "prosperous sitting and facing", "wàng shān wàng xiàng", ""),
    ("上山下水", "reversed stars", "shàng shān xià shuǐ", ""),
    ("雙星到坐", "double stars at the sitting", "shuāng xīng dào zuò", ""),
    ("雙星到向", "double stars at the facing", "shuāng xīng dào xiàng", ""),
    ("二五交加", "2-5 combination", "èr wǔ jiāo jiā", ""),
    ("太歲", "Grand Duke", "tài suì", ""), ("歲破", "Year Breaker", "suì pò", ""),
    ("三煞", "Three Killings", "sān shà", ""), ("年神", "year spirits", "nián shén", ""),
    ("城門", "water gate", "chéng mén", ""), ("正城門", "main water gate", "zhèng chéng mén", ""),
    ("副城門", "side water gate", "fù chéng mén", ""),
    ("正向", "true facing", "zhèng xiàng", ""), ("兼向", "mixed facing", "jiān xiàng", ""),
    ("替卦", "replacement chart", "tì guà", ""),
])

# ---------------------------------------------------------------- symbolic stars (no English)
_add("shensha", [
    ("天乙貴人", "", "tiān yǐ guì rén", "nobleman star"), ("貴人", "", "guì rén", "helpful people"),
    ("太極貴人", "", "tài jí guì rén", "mystic nobleman"), ("文昌", "", "wén chāng", "study star"),
    ("文昌貴人", "", "wén chāng guì rén", "study star"), ("學堂", "", "xué táng", "study hall"),
    ("桃花", "", "táo huā", "romance star"), ("咸池", "", "xián chí", "romance star"),
    ("驛馬", "", "yì mǎ", "travel horse"), ("華蓋", "", "huá gài", "canopy, solitude"),
    ("將星", "", "jiàng xīng", "general star"), ("羊刃", "", "yáng rèn", "goat blade"),
    ("祿神", "", "lù shén", "salary star"), ("劫煞", "", "jié shà", "robbery star"),
    ("亡神", "", "wáng shén", "loss star"), ("孤辰", "", "gū chén", "lonely star"),
    ("寡宿", "", "guǎ sù", "widow star"), ("紅鸞", "", "hóng luán", "marriage star"),
    ("天喜", "", "tiān xǐ", "celebration star"), ("天德", "", "tiān dé", "heavenly virtue"),
    ("月德", "", "yuè dé", "monthly virtue"), ("天醫星", "", "tiān yī xīng", "healing star"),
    ("魁罡", "", "kuí gāng", "strong-will day"), ("金輿", "", "jīn yú", "golden carriage"),
    ("空亡", "", "kōng wáng", "void"), ("災煞", "", "zāi shà", "disaster star"),
    ("十惡大敗", "", "shí è dà bài", "ten-evil day"), ("陰差陽錯", "", "yīn chā yáng cuò", "mismatch day"),
    ("天赦", "", "tiān shè", "pardon day"), ("福星貴人", "", "fú xīng guì rén", "blessing star"),
    ("國印", "", "guó yìn", "official seal"), ("天廚", "", "tiān chú", "heavenly kitchen"),
    ("血刃", "", "xuè rèn", "blood blade"), ("勾絞", "", "gōu jiǎo", "entanglement star"),
    ("喪門", "", "sāng mén", "mourning star"), ("弔客", "", "diào kè", "mourner star"),
    ("披麻", "", "pī má", "mourning cloth"), ("元辰", "", "yuán chén", "disharmony star"),
    ("詞館", "", "cí guǎn", "literary hall"), ("德秀", "", "dé xiù", "virtue star"),
    ("天羅地網", "", "tiān luó dì wǎng", "heaven-earth net"),
])

# ---------------------------------------------------------------- branch / stem relations
_add("relation", [
    ("六合", "Six Harmony", "liù hé", ""), ("三合", "Three Harmony", "sān hé", ""),
    ("半合", "half harmony", "bàn hé", ""), ("三會", "seasonal union", "sān huì", ""),
    ("六沖", "Six Clash", "liù chōng", ""), ("沖", "clash", "chōng", ""), ("冲", "clash", "chōng", ""),
    ("六害", "Six Harm", "liù hài", ""), ("害", "harm", "hài", ""),
    ("相刑", "punishment", "xiāng xíng", ""), ("刑", "punishment", "xíng", ""),
    ("相破", "destruction", "xiāng pò", ""), ("破", "destruction", "pò", ""),
    ("合", "combination", "hé", ""), ("天干五合", "stem combination", "tiān gàn wǔ hé", ""),
    ("伏吟", "repeated pillar", "fú yín", ""), ("反吟", "clashing pillar", "fǎn yín", ""),
    ("自刑", "self-punishment", "zì xíng", ""),
])

# ---------------------------------------------------------------- 24 solar terms
_add("jieqi", [
    ("立春", "Start of Spring", "lì chūn", ""), ("雨水", "Rain Water", "yǔ shuǐ", ""),
    ("驚蟄", "Awakening of Insects", "jīng zhé", ""), ("春分", "Spring Equinox", "chūn fēn", ""),
    ("清明", "Clear and Bright", "qīng míng", ""), ("穀雨", "Grain Rain", "gǔ yǔ", ""),
    ("立夏", "Start of Summer", "lì xià", ""), ("小滿", "Grain Buds", "xiǎo mǎn", ""),
    ("芒種", "Grain in Ear", "máng zhòng", ""), ("夏至", "Summer Solstice", "xià zhì", ""),
    ("小暑", "Minor Heat", "xiǎo shǔ", ""), ("大暑", "Major Heat", "dà shǔ", ""),
    ("立秋", "Start of Autumn", "lì qiū", ""), ("處暑", "End of Heat", "chǔ shǔ", ""),
    ("白露", "White Dew", "bái lù", ""), ("秋分", "Autumn Equinox", "qiū fēn", ""),
    ("寒露", "Cold Dew", "hán lù", ""), ("霜降", "Frost's Descent", "shuāng jiàng", ""),
    ("立冬", "Start of Winter", "lì dōng", ""), ("小雪", "Minor Snow", "xiǎo xuě", ""),
    ("大雪", "Major Snow", "dà xuě", ""), ("冬至", "Winter Solstice", "dōng zhì", ""),
    ("小寒", "Minor Cold", "xiǎo hán", ""), ("大寒", "Major Cold", "dà hán", ""),
])

# ---------------------------------------------------------------- 建除 day officers
_add("officer", [
    ("建", "Establish", "jiàn", ""), ("除", "Remove", "chú", ""), ("滿", "Full", "mǎn", ""),
    ("定", "Settle", "dìng", ""), ("執", "Hold", "zhí", ""), ("危", "Danger", "wēi", ""),
    ("成", "Completion", "chéng", ""), ("收", "Receive", "shōu", ""), ("開", "Open", "kāi", ""),
    ("閉", "Close", "bì", ""), ("建除", "day officers", "jiàn chú", ""),
    ("建除十二神", "twelve day officers", "jiàn chú shí èr shén", ""),
])

# ---------------------------------------------------------------- naming (五格 / 三才)
_add("naming", [
    ("五格", "Five Grids", "wǔ gé", ""), ("三才", "Three Talents", "sān cái", ""),
    ("天格", "Heaven grid", "tiān gé", ""), ("人格", "Person grid", "rén gé", ""),
    ("地格", "Earth grid", "dì gé", ""), ("外格", "Outer grid", "wài gé", ""),
    ("總格", "Total grid", "zǒng gé", ""), ("康熙字典", "Kangxi Dictionary", "kāng xī zì diǎn", ""),
    ("康熙", "Kangxi", "kāng xī", ""), ("筆畫", "stroke count", "bǐ huà", ""), ("畫", "strokes", "huà", ""),
    ("字義", "character meaning", "zì yì", ""), ("音韻", "sound", "yīn yùn", ""),
    ("可信度", "confidence", "kě xìn dù", ""), ("性別", "gender fit", "xìng bié", ""),
    ("八十一數理", "81 numerology", "bā shí yī shù lǐ", ""), ("數理", "numerology", "shù lǐ", ""),
    ("單名", "one-character given name", "dān míng", ""), ("雙名", "two-character given name", "shuāng míng", ""),
    ("姓氏", "surname", "xìng shì", ""), ("名字", "given name", "míng zì", ""),
    ("起名", "baby naming", "qǐ míng", ""), ("寶寶起名", "baby name builder", "bǎo bǎo qǐ míng", ""),
    ("諧音", "sound-alike", "xié yīn", ""), ("繁體", "traditional form", "fán tǐ", ""),
    ("簡體", "simplified form", "jiǎn tǐ", ""), ("字形", "character form", "zì xíng", ""),
    ("證書", "certificate", "zhèng shū", ""), ("候選", "shortlist", "hòu xuǎn", ""),
])

# ---------------------------------------------------------------- compatibility / grades
_add("grade", [
    ("上等", "very compatible", "shàng děng", ""), ("中上", "compatible", "zhōng shàng", ""),
    ("中等", "average", "zhōng děng", ""), ("中下", "below average", "zhōng xià", ""),
    ("下等", "difficult", "xià děng", ""), ("需磨合", "needs work", "xū mó hé", ""),
    ("上佳", "excellent", "shàng jiā", ""), ("優", "excellent", "yōu", ""), ("良", "good", "liáng", ""),
    ("佳", "good", "jiā", ""), ("可", "fair", "kě", ""), ("差", "poor", "chà", ""),
])

# ---------------------------------------------------------------- feng shui and guide phrases
_add("core", [
    ("靠", "backing", "kào", ""), ("靠山", "backing mountain", "kào shān", ""),
    ("門沖床", "door facing the bed", "mén chōng chuáng", ""), ("過旺", "excess", "guò wàng", ""),
    ("不足", "deficient", "bù zú", ""), ("宮位", "palaces", "gōng wèi", ""), ("正格", "ordinary structure", "zhèng gé", ""),
    ("被剋", "restrained", "bèi kè", ""), ("人剋", "the person element restrains", "rén kè", ""),
    ("沖坐山", "clashes the sitting", "chōng zuò shān", ""), ("值太歲", "meets the Grand Duke", "zhí tài suì", ""),
    ("沖生肖", "clashes the zodiac animal", "chōng shēng xiào", ""), ("六十甲子", "sixty-pair cycle", "liù shí jiǎ zǐ", ""),
    ("用神四法", "four useful-god methods", "yòng shén sì fǎ", ""),
    ("合化木", "combines into Wood", "hé huà mù", ""), ("合化火", "combines into Fire", "hé huà huǒ", ""),
    ("合化土", "combines into Earth", "hé huà tǔ", ""), ("合化金", "combines into Metal", "hé huà jīn", ""),
    ("合化水", "combines into Water", "hé huà shuǐ", ""),
    ("半三合", "half Three Harmony", "bàn sān hé", ""), ("五合", "stem combination", "wǔ hé", ""),
    ("子平法", "Ziping method", "zǐ píng fǎ", ""), ("十神互補", "Ten God complementarity", "shí shén hù bǔ", ""),
    ("喜用神", "favourable and useful elements", "xǐ yòng shén", ""), ("門對門", "door facing door", "mén duì mén", ""), ("月令剋我", "the month controls the Day Master", "yuè lìng kè wǒ", ""),
])

# ---------------------------------------------------------------- guide vocabulary, colours, classics
_add("core", [
    ("東四", "East group", "dōng sì", ""), ("西四", "West group", "xī sì", ""),
    ("陽男陰女順行", "yang men and yin women count forward", "yáng nán yīn nǚ shùn xíng", ""),
    ("陰男陽女逆行", "yin men and yang women count backward", "yīn nán yáng nǚ nì xíng", ""),
    ("距節日數", "days to the solar-term boundary", "jù jié rì shù", ""),
    ("五行生剋", "element cycles", "wǔ xíng shēng kè", ""), ("生剋", "feed-and-control cycles", "shēng kè", ""),
    ("生克", "feed-and-control cycles", "shēng kè", ""), ("時辰", "two-hour period", "shí chén", ""),
    ("動土", "groundbreaking", "dòng tǔ", ""), ("月破", "Month Breaker", "yuè pò", ""),
    ("十二建除", "twelve day officers", "shí èr jiàn chú", ""),
    ("平星", "neutral star", "píng xīng", ""), ("吉白星", "auspicious white star", "jí bái xīng", ""),
    ("當運旺星", "current-period star", "dāng yùn wàng xīng", ""), ("生氣星", "rising star", "shēng qì xīng", ""),
    ("成長", "growth", "chéng zhǎng", ""), ("蓄勢", "build-up", "xù shì", ""), ("修整", "consolidation", "xiū zhěng", ""),
    ("表達", "expression", "biǎo dá", ""), ("行動", "action", "xíng dòng", ""), ("權威", "authority", "quán wēi", ""),
    ("思維", "thinking", "sī wéi", ""), ("情感", "feelings", "qíng gǎn", ""),
    ("待斟酌", "needs a second look", "dài zhēn zhuó", ""), ("未定", "undetermined", "wèi dìng", ""),
    ("閑", "neutral", "xián", ""), ("八宅大遊年", "Great Wandering Year", "bā zhái dà yóu nián", ""),
    ("離宮", "", "lí gōng", "south palace"), ("退氣星", "retreating star", "tuì qì xīng", ""), ("年神", "year spirits", "nián shén", ""),
    ("天乙", "Tianyi", "tiān yǐ", ""), ("太極", "Taiji", "tài jí", ""),
])
_add("trigram", [(t + "命", "", py + " mìng", f"kua {n}, {grp} group") for t, py, n, grp in [
    ("坎", "kǎn", 1, "East"), ("坤", "kūn", 2, "West"), ("震", "zhèn", 3, "East"), ("巽", "xùn", 4, "East"),
    ("乾", "qián", 6, "West"), ("兌", "duì", 7, "West"), ("艮", "gèn", 8, "West"), ("離", "lí", 9, "East")]])
_add("colour", [
    ("紅", "red", "hóng", ""), ("紫", "purple", "zǐ", ""), ("黃", "yellow", "huáng", ""), ("棕", "brown", "zōng", ""),
    ("綠", "green", "lǜ", ""), ("青", "teal", "qīng", ""), ("白", "white", "bái", ""), ("黑", "black", "hēi", ""),
    ("藍", "blue", "lán", ""), ("灰", "grey", "huī", ""),
])
_add("book", [
    ("子平", "", "zǐ píng", "classical BaZi school"), ("三命通會", "", "sān mìng tōng huì", "Ming-era BaZi classic"),
    ("協紀辨方書", "", "xié jì biàn fāng shū", "Qing almanac manual"), ("八宅明鏡", "", "bā zhái míng jìng", "Eight House classic"),
    ("沈氏玄空學", "", "shěn shì xuán kōng xué", "Flying Stars classic"), ("淵海子平", "", "yuān hǎi zǐ píng", "Song-era BaZi classic"),
    ("滴天髓", "", "dī tiān suǐ", "BaZi classic"), ("窮通寶鑑", "", "qióng tōng bǎo jiàn", "climate-method classic"),
])

# Traditional → simplified for the glossary's own keys (superset of engine/htmlreport.py's map;
# 乾 is deliberately absent so the trigram never becomes 干).
_T2S_EXTRA = ("運运殺杀傷伤財财劫劫氣气醫医禍祸絕绝遊游東东調调飛飞節节沖冲歲岁學学宮宫兌兑離离盤盘書书"
              "擇择時时陰阴陽阳貪贪貞贞祿禄輔辅軍军門门龍龙剋克強强顯显黃黄簡简單单總总滿满執执開开閉闭"
              "關关藥药梟枭納纳雙双綠绿紅红長长貴贵將将華华馬马驛驿蓋盖雞鸡豬猪綜综論论斷断親亲帶带"
              "臨临養养爐炉劍剑鋒锋頭头澗涧蠟蜡楊杨靂雳燈灯釵钗釧钏柘柘曆历農农驚惊蟄蛰穀谷種种處处"
              "滿满義义韻韵數数畫画筆笔體体諧谐證证選选優优會会錯错弔吊喪丧輿舆廚厨國国鸞鸾詞词館馆"
              "補补對对沖冲羅罗網网惡恶敗败煞煞極极點点卦卦宅宅風风紅红藍蓝綠绿別别動动權权達达維维閑闲協协辨辨鏡镜淵渊滴滴窮穷寶宝鑑鉴蓄蓄勢势")
_T2S = {_T2S_EXTRA[i]: _T2S_EXTRA[i + 1] for i in range(0, len(_T2S_EXTRA), 2)}


def to_simp(s: str) -> str:
    return "".join(_T2S.get(c, c) for c in s)


# alias (simplified or variant spelling) -> canonical key
ALIASES: dict[str, str] = {}
for _k in list(TERMS):
    _s = to_simp(_k)
    if _s != _k and _s not in TERMS:
        ALIASES[_s] = _k
ALIASES.update({"劫财": "劫財", "梟": "梟神", "枭神": "梟神", "龙": "龍", "马": "馬", "鸡": "雞",
                "猪": "豬", "强弱": "強弱", "时": "時"})

NO_EN = {t for t, v in TERMS.items() if not v[0]}
CATEGORIES = sorted({v[3] for v in TERMS.values()})


def lookup(term: str):
    """(canonical key, (en, pinyin, gloss, category)) or None."""
    k = term if term in TERMS else ALIASES.get(term)
    return (k, TERMS[k]) if k else None


# ---------------------------------------------------------------- pinyin
# Every TERMS entry carries tone-marked Hanyu Pinyin taken from data/naming/chardata.json (the
# repo's per-character reading table).  Readings that differ inside these terms (polyphones)
# were corrected by hand: _CHAR_FIX applies glossary-wide, PINYIN_HAND lists the affected terms.
_CHAR_FIX = {"地": "dì", "剋": "kè", "艮": "gèn", "喪": "sāng", "將": "jiàng", "處": "chǔ", "種": "zhòng",
             "調": "tiáo", "長": "cháng", "煞": "shà"}
PINYIN_HAND = {"成長", "相", "旺相休囚死", "陰差陽錯", "差", "地支", "平地木", "天羅地網", "地格", "剋",
               "相剋", "五行生剋", "生剋", "艮", "艮命", "喪門", "將星", "處暑", "芒種", "調候", "調候法",
               "十二長生", "長生", "長流水", "六煞", "三煞", "劫煞", "神煞", "災煞"}
_CHARPY: dict[str, str] | None = None


def _charpy() -> dict[str, str]:
    global _CHARPY
    if _CHARPY is None:
        import json
        from pathlib import Path
        f = Path(__file__).resolve().parent.parent / "data/naming/chardata.json"
        try:
            d = json.loads(f.read_text("utf8"))
            _CHARPY = {c: v["py"].split(",")[0].strip() for c, v in d.items() if v.get("py")}
        except (OSError, ValueError):
            _CHARPY = {}
        _CHARPY.update(_CHAR_FIX)
    return _CHARPY


def pinyin(s: str) -> str:
    """Tone-marked pinyin for a Chinese string: glossary readings first, else per character."""
    hit = lookup(s)
    if hit:
        return hit[1][1]
    seg = segment(s)
    if seg:
        return " ".join(lookup(p)[1][1] for p in seg)
    cp = _charpy()
    return " ".join(cp[c] for c in s if c in cp)


def english(term: str) -> str:
    """The form used after first mention: English, or the characters alone for terms with no
    English (their pinyin lives in the tooltip, see tip())."""
    hit = lookup(term)
    if not hit:
        return term
    return hit[1][0] or term


def _first(term: str, entry) -> str:
    en_, py, gl, cat = entry
    if en_:
        return f"{en_} ({term})"
    return f"{term} ({gl})" if gl else term


def en(term: str, first: bool = True) -> str:
    """Stateless helper: 'English (漢字)' when first, 'English' after; for terms with no
    English equivalent '漢字 (gloss)' then '漢字'.  Pinyin is never inline: see tip()."""
    hit = lookup(term)
    if not hit:
        return term
    return _first(term, hit[1]) if first else english(term)


_STEMS = "甲乙丙丁戊己庚辛壬癸"
_BRANCHES = "子丑寅卯辰巳午未申酉戌亥"


def _is_pillar(r: str) -> bool:
    return len(r) == 2 and r[0] in _STEMS and r[1] in _BRANCHES


def _is_year(r: str) -> bool:
    return len(r) == 3 and _is_pillar(r[:2]) and r[2] == "年"


def _pgl(gz: str) -> str:
    """'戊辰' -> 'Earth Dragon' (the stem's element and the branch's animal)."""
    return f"{TERMS[gz[0]][2].split()[1]} {TERMS[gz[1]][2].split(',')[0]}"


def tip(term: str) -> str:
    """Tooltip text for a Chinese run: 'pīnyīn · English' (or '· gloss' for terms with no
    English); stem-branch pairs read 'wù chén · Earth Dragon'; other words get their
    per-character pinyin only; '' when no reading is known."""
    hit = lookup(term)
    if hit:
        en_, py, gl, _ = hit[1]
        return f"{py} · {en_ or gl}" if (en_ or gl) else py
    if _is_pillar(term):
        return f"{TERMS[term[0]][1]} {TERMS[term[1]][1]} · {_pgl(term)}"
    if _is_year(term):
        return f"{TERMS[term[0]][1]} {TERMS[term[1]][1]} nián · {_pgl(term[:2])} year"
    seg = segment(term)
    if seg:
        return " ".join(lookup(p)[1][1] for p in seg) + " · " + ", ".join(
            lookup(p)[1][0] or lookup(p)[1][2] or p for p in seg)
    cp = _tipchars()
    if term and all(c in cp or c in _PUNCT for c in term):
        return " ".join(cp[c] for c in term if c in cp)
    return ""


_TIPCHARS: dict[str, str] | None = None


def _tipchars() -> dict[str, str]:
    """Per-character readings the tooltip may use: exactly the set web/glossary.js embeds (the
    common characters plus every glossary character), so server and browser agree."""
    global _TIPCHARS
    if _TIPCHARS is None:
        keep = _js_keep()                      # hoisted: _js_keep re-parses a 1.7 MB file
        _TIPCHARS = {c: p for c, p in _charpy().items() if c in keep}
    return _TIPCHARS


def _js_keep() -> set[str]:
    import json
    from pathlib import Path
    d = json.loads((Path(__file__).resolve().parent.parent / "data/naming/chardata.json").read_text("utf8"))
    return {c for c, v in d.items() if v.get("common")} | set("".join(TERMS)) | set("".join(ALIASES))


# ---------------------------------------------------------------- free-text rewriting
_CJK = re.compile(r"[㐀-鿿豈-﫿]+")
_MAXLEN = max(len(k) for k in list(TERMS) + list(ALIASES))
_LIST_CATS = {"element", "stem", "branch", "trigram", "direction", "animal", "colour"}
_NB = r"(?![A-Za-zÀ-ɏ])"          # end of a latin word (ASCII \b misses tone marks in JS)


def segment(run: str):
    """Split a CJK run into glossary terms (longest match first); None if any part is unknown.
    A run of several pieces is accepted only when every single-character piece is an element,
    stem, branch, trigram, direction, animal or colour — so ordinary words built from
    one-character terms (生日, 年月) are never mistranslated."""
    out, i = [], 0
    while i < len(run):
        for n in range(min(_MAXLEN, len(run) - i), 0, -1):
            piece = run[i:i + n]
            if lookup(piece):
                out.append(piece); i += n
                break
        else:
            return None
    if len(out) > 1 and any(len(p) == 1 and lookup(p)[1][3] not in _LIST_CATS for p in out):
        return None
    return out


_START = re.compile(r"(^|[.!?|]|^\s*(?:[-*>#]+|\d+\.)(?:\s+[-*>#]+)*)$")


def _cap(prev: str, r: str) -> str:
    """Capitalise a rendering that starts a sentence, list item or table cell."""
    if r and r[0].islower() and _START.search(re.sub(r"[\s*_]+$", "", prev)):
        return r[0].upper() + r[1:]
    return r


def _compact(r: str) -> str:
    """A rendering placed inside someone else's parentheses: no nested brackets.
    'Rob Wealth (劫財)' -> 'Rob Wealth, 劫財'; '戊 (yang Earth)' -> '戊, yang Earth'."""
    m = re.match(r"^(.*?) \((.*)\)$", r)
    return f"{m.group(1)}, {m.group(2)}" if m else r


def _opened(out: str) -> bool:
    return out.endswith(("(", "（"))


class Gloss:
    """One rendering context (a page, a card or one API response): tracks first use."""

    def __init__(self):
        self.seen: set[str] = set()

    def reset(self) -> None:
        self.seen.clear()

    def en(self, term: str) -> str:
        """'English (漢字)' the first time in this context, 'English' afterwards."""
        hit = lookup(term)
        if not hit:
            return term
        k = hit[0]
        if k in self.seen:
            return english(term)
        self.seen.add(k)
        return _first(term, hit[1])

    __call__ = en

    def zh_once(self, term: str) -> str:
        """'漢字' the first time (for a small secondary label), '' afterwards."""
        hit = lookup(term)
        k = hit[0] if hit else term
        if k in self.seen:
            return ""
        self.seen.add(k)
        return term

    def pair(self, zh: str, en_: str) -> str:
        """A page's own (Chinese, English) label pair: 'English (中文)' first, 'English' after.
        Tracked by the glossary key when the Chinese is a glossary term, else by the string."""
        hit = lookup(zh)
        k = hit[0] if hit else zh
        if not zh or k in self.seen:
            return en_
        self.seen.add(k)
        return f"{en_} ({zh})"

    def label(self, zh: str, en_: str | None = None) -> str:
        """HTML label: English big, the characters small once (pinyin in their tooltip);
        no-English terms keep the characters with the gloss on first use."""
        import html as _h
        hit = lookup(zh)
        k = hit[0] if hit else zh
        first = bool(zh) and k not in self.seen
        self.seen.add(k)
        zs = zh_span(zh)
        if hit and not hit[1][0] and not en_:
            gl = hit[1][2]
            small = f" <small>{_h.escape(gl)}</small>" if first and gl else ""
            return f'<span class="bl en">{zs}{small}</span>'
        e = en_ or (hit[1][0] if hit else zh)
        small = f" <small>{zs}</small>" if first and zh != e else ""
        return f'<span class="bl en">{_h.escape(e)}{small}</span>'

    def pillar(self, gz: str) -> str:
        """A stem-branch pair: '戊辰 (Earth Dragon)' on first use, '戊辰' after."""
        if not _is_pillar(gz):
            return self.text(gz)
        if gz in self.seen:
            return gz
        self.seen.add(gz)
        return f"{gz} ({_pgl(gz)})"

    def _render_run(self, run: str) -> str | None:
        if _is_pillar(run):
            return self.pillar(run)
        if _is_year(run):
            if run in self.seen:
                return run
            self.seen.add(run)
            return f"{run} ({_pgl(run[:2])} year)"
        seg = segment(run)
        if seg is None:
            return None
        parts = [self.en(p) for p in seg]
        if len(seg) > 1 and all(lookup(p)[1][3] in ("element", "colour") for p in seg):
            return ", ".join(parts)
        return " ".join(parts)

    @staticmethod
    def _own(after: str, py: str, gl: str) -> int:
        """Length of an annotation this module (either style) already put after the run:
        ' (pīnyīn, gloss)', ' pīnyīn (gloss)', ' (gloss)', ' (pīnyīn)' or ' pīnyīn'; 0 if none."""
        for c in ([f" ({py}, {gl})", f" {py} ({gl})", f" ({gl})"] if gl else []) + [f" ({py})"]:
            if after.startswith(c):
                return len(c)
        m = re.match(r"\s" + re.escape(py) + _NB, after)
        return m.end() if m else 0

    def text(self, s: str) -> str:
        """Rewrite a mixed string English-first.  Handles 'EN (中)', '中 (EN)', '中 EN', 'EN 中',
        'X(中)' and bare '中', drops any pinyin a previous rendering left inline, and is
        idempotent on its own output.  CJK runs that are not entirely glossary terms (names,
        phrases) are left as they are."""
        if not s or not isinstance(s, str) or not _CJK.search(s):
            return s
        out, pos = "", 0
        for m in _CJK.finditer(s):
            run, a, b = m.group(0), m.start(), m.end()
            if a < pos:
                continue
            out += s[pos:a]
            pos = b
            after = s[b:]
            hit = lookup(run)
            # terms shown as characters + gloss: no-English terms, stem-branch pairs, 'X年' years
            if hit and not hit[1][0]:
                key, py, gl = hit[0], hit[1][1], hit[1][2]
            elif not hit and _is_pillar(run):
                key, py, gl = run, f"{TERMS[run[0]][1]} {TERMS[run[1]][1]}", _pgl(run)
            elif not hit and _is_year(run):
                key, py, gl = run, f"{TERMS[run[0]][1]} {TERMS[run[1]][1]} nián", _pgl(run[:2]) + " year"
            else:
                key = None
            if key is not None:
                # "辛 Metal day master": the element already follows, so "辛 (yin Metal) Metal" would say it twice
                ew = re.match(r"\s+(Wood|Fire|Earth|Metal|Water)\b", after) if gl else None
                if ew and gl.endswith(ew.group(1)):
                    self.seen.add(key)
                    out += run
                    continue
                n = self._own(after, py, gl)
                if n:
                    first = key not in self.seen
                    self.seen.add(key)
                    rest = after[n:]
                    if gl and rest.startswith(f", {gl}"):          # old '(戊 wù, yang Earth)'
                        out += run
                    elif _opened(out) and rest[:1] in ")）":
                        out += _compact(f"{run} ({gl})") if first and gl else run
                    else:
                        out += f"{run} ({gl})" if first and gl else run
                    pos = b + n
                    continue
                if gl and _opened(out) and after.startswith(f", {gl}"):   # our own '(戊, yang Earth)'
                    self.seen.add(key)
                    out += run
                    continue
            if not hit and _opened(out) and after[:1] in ")）":
                r = self._render_run(run)
                out += _compact(r) if r else run
                continue
            if hit:
                k, entry = hit
                en_, py, gl, cat = entry
                first = k not in self.seen
                mp = re.match(r"\s" + re.escape(py) + _NB, after)
                if mp and en_:
                    # '漢字 pīnyīn' from an earlier rendering or by hand: the pinyin goes
                    after = after[mp.end():]; pos = b + mp.end()
                    self.seen.add(k)
                    me = re.search(re.escape(en_) + r"(\s?)$", out, re.I)
                    if first:
                        if re.search(re.escape(en_) + r"[*_]*\s?[(（]$|" + re.escape(en_) + r",\s$", out, re.I):
                            out += run                   # 'EN (中' or 'EN, 中': English already there
                        elif _opened(out):
                            out += _compact(_first(run, entry))
                        elif me:
                            out = out[:len(out) - len(me.group(1))] + f" ({run})"
                        else:
                            out += _cap(out, _first(run, entry))
                    elif _opened(out) and after[:1] in ")）":
                        out = re.sub(r"\s?[(（]$", "", out); pos += 1
                    elif _opened(out) and after[:2] in (", ", "; "):
                        pos += 2
                    elif re.search(re.escape(en_) + r",\s$", out, re.I):
                        out = out[:-2]
                    elif not me:
                        out += _cap(out, en_)
                    continue
                if _opened(out):
                    eb = re.search(r"([A-Za-z][A-Za-z0-9' \-]*?)[*_]*\s?[(（]$", out)
                    if eb and not re.search(r"[A-Za-z]{3,}", eb.group(1)):
                        eb = None                        # 'N(天醫)': a compass letter is not English
                    if en_ and ((eb and eb.group(1).lower().endswith(en_.lower()))
                                or re.search(re.escape(en_) + r"[*_]*\s?[(（]$", out, re.I)):
                        # 'EN (中 …' — already English-first
                        self.seen.add(k)
                        if first:
                            out += run
                        elif after[:1] in ")）":
                            out = re.sub(r"\s?[(（]$", "", out); pos += 1
                        elif after[:2] in (", ", "; "):
                            pos += 2
                        else:
                            pos += 1 if after[:1] == " " else 0
                        continue
                    if after[:1] in ")）":
                        # 'X(中)' — keep it compact inside the parentheses
                        r = self._render_run(run) or run
                        out += _compact(r)
                        continue
                    if eb and after[:1] in ",;，；":
                        # 'english words (中, …' — the term's English joins the bracket
                        self.seen.add(k)
                        out += (f"{en_}, {run}" if first else en_) if en_ else run
                        continue
                # '中 (x)' — something already sits in the parentheses
                ma = re.match(r"\s?[(（]\s*([A-Za-zÀ-ɏ][^()（）㐀-鿿]{0,60}?)\s*[)）]", after)
                if ma:
                    x = ma.group(1)
                    if not en_:
                        self.seen.add(k)
                        if x.lower().startswith(py.lower()):      # '(pīnyīn, note)': keep the note
                            rest = x[len(py):].lstrip(" ,;")
                            out += _cap(out, f"{run} ({rest})" if rest else run)
                        else:
                            out += _cap(out, f"{run} ({x})")
                    elif x.lower() in en_.lower() or en_.lower() in x.lower():
                        out += _cap(out, self.en(run))
                    else:
                        self.seen.add(k)
                        out += _cap(out, f"{x} ({run})" if first else x)
                    pos += ma.end()
                    continue
                # '中 EN'
                if en_:
                    ma = re.match(r"\s?" + re.escape(en_) + _NB, after, re.I)
                    if ma:
                        out += _cap(out, self.en(run)); pos += ma.end()
                        continue
                # 'EN 中'
                me = re.search(re.escape(en_) + r"(\s?)$", out, re.I) if en_ else None
                if me:                                   # also glued 'Wood木'
                    self.seen.add(k)
                    out = out[:len(out) - len(me.group(1))] + (f" ({run})" if first else "")
                    continue
                # 'EN, 中' — our own compact form inside parentheses
                if en_ and re.search(re.escape(en_) + r",\s$", out, re.I):
                    self.seen.add(k)
                    if first:
                        out += run
                    else:
                        out = out[:-2]
                    continue
            r = self._render_run(run)
            out += _cap(out, r) if r is not None else run
        return out + s[pos:]

    def walk(self, obj, keys=None):
        """Apply .text() to every string in a JSON-like object (only under `keys` when given)."""
        if isinstance(obj, str):
            return self.text(obj) if keys is None else obj
        if isinstance(obj, list):
            return [self.walk(x, keys) for x in obj]
        if isinstance(obj, dict):
            return {k: (self.walk(v, None) if keys is not None and k in keys else self.walk(v, keys))
                    for k, v in obj.items()}
        return obj


# ---------------------------------------------------------------- HTML: tooltips and element colours
# One shape for a glossed run on every English surface (pages, guides, report, browser):
#   <span class="zh" lang="zh-Hant" tabindex="0" title="rì zhǔ · Day Master" data-tip="…">日主</span>
# title gives the hover tooltip; web/glossary-tip.js shows the same text on tap, focus or
# Enter/Space.  Inside a link or button the span is not focusable (title only).
# The five elements take the site's element colour on the English word and the character:
#   <span class="el el-wood">Wood (<span class="zh" …>木</span>)</span>
# The shared CSS for the tooltip span, its popover and the element colours (each colour passes
# 4.5:1 on cream #faf7f2 and on white).  Server-rendered pages inline it; web/glossary-tip.js
# injects the same block, so every English page has it exactly once per source.
TIP_CSS = (":root{--wood:#187a35;--fire:#c5221f;--earth:#8a6d1f;--metal:#8a6500;--water:#1a56b0}"
           ".el-wood{color:var(--wood)}.el-fire{color:var(--fire)}.el-earth{color:var(--earth)}"
           ".el-metal{color:var(--metal)}.el-water{color:var(--water)}"
           ".zh[data-tip]{cursor:help;text-decoration:underline dotted;text-decoration-thickness:1px;"
           "text-underline-offset:3px;border-radius:2px}"
           ".zh[data-tip]:focus-visible{outline:2px solid #8a6d1f;outline-offset:2px}"
           ".gl-tip{position:fixed;z-index:9999;max-width:calc(100vw - 32px);width:max-content;"
           "background:#2b2620;color:#fff;font:500 14px/1.45 system-ui,sans-serif;padding:6px 10px;"
           "border-radius:8px;box-shadow:0 4px 14px rgba(43,38,32,.25);opacity:0;transition:opacity .15s;"
           "pointer-events:none;text-align:left;white-space:normal}"
           ".gl-tip.on{opacity:1}@media (prefers-reduced-motion:reduce){.gl-tip{transition:none}}")
_SIMP_ONLY = set(_T2S.values()) - set(_T2S)
EL_CLASS = {"木": "wood", "火": "fire", "土": "earth", "金": "metal", "水": "water",
            "Wood": "wood", "Fire": "fire", "Earth": "earth", "Metal": "metal", "Water": "water"}
_TONED = re.compile(r"[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]")
_SYL = r"[a-zü]*[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜa-zü][a-zü]*"
_RUNX = re.compile(r"[㐀-鿿豈-﫿]+(?:[，、；：][㐀-鿿豈-﫿]+)*")   # a run, CJK punctuation inside kept
_PUNCT = "，、；："


def zh_lang(run: str) -> str:
    return "zh-Hans" if any(c in _SIMP_ONLY for c in run) else "zh-Hant"


def zh_span(run: str, focus: bool = True, reading: str = "") -> str:
    """The shared tooltip span for a Chinese run ('' title -> the run stays as plain text).
    `reading` overrides the pinyin part (a hand-written reading taken from the source)."""
    import html as _h
    t = tip(run)
    if reading:
        t = reading + (" · " + t.split(" · ", 1)[1] if " · " in t else "")
    if not t:
        return _h.escape(run, quote=False)
    a = _h.escape(t, quote=True)
    f = f' tabindex="0" title="{a}" data-tip="{a}"' if focus else f' title="{a}"'
    return f'<span class="zh" lang="{zh_lang(run)}"{f}>{_h.escape(run, quote=False)}</span>'


def _inline_reading(run: str, after: str):
    """Pinyin written inline right after a run, in any of the forms the language pass used:
    ' pīnyīn', ' (pīnyīn)', ' (pīnyīn, gloss)'.  Returns (chars consumed, replacement, reading)
    or None.  One syllable per character, at least one tone mark."""
    n = len([c for c in run if c not in _PUNCT])
    syl = _SYL + (r"(?:,? " + _SYL + r"){%d}" % (n - 1) if n > 1 else "")
    m = re.match(r"( \()(" + syl + r")(\)|, )", after)
    if m and _TONED.search(m.group(2)):
        if m.group(3) == ")":
            return m.end(), "", m.group(2)
        return m.end(), " (", m.group(2)
    m = re.match(r" (" + syl + r")" + _NB, after)
    if m and _TONED.search(m.group(1)):
        return m.end(), "", m.group(1)
    return None


_TOKEN = re.compile(r"(?<![A-Za-z])((?:[Yy]in |[Yy]ang )?(Wood|Fire|Earth|Metal|Water))(?![A-Za-z])"
                    r"(?: \(([木火土金水])(?:\x01(\d+)\x02)?\))?|([㐀-鿿豈-﫿]+(?:[，、；：][㐀-鿿豈-﫿]+)*)(?:\x01(\d+)\x02)?")
_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source",
         "track", "wbr", "param"}
_RAW = {"script", "style", "textarea", "title"}
_SKIP = {"select", "option", "svg", "code", "pre", "template", "head", "noscript"}
_FOCUS_NO = {"a", "button", "label", "summary", "option"}
_COLOR_NO = {"h1", "h2", "h3", "h4", "h5", "h6", "a", "button", "nav", "footer", "label", "summary"}
_TAG = re.compile(r"<!--.*?-->|<(/?)([A-Za-z][A-Za-z0-9]*)\b((?:[^>\"']|\"[^\"]*\"|'[^']*')*)>", re.S)


def _tagflags(name: str, attrs: str) -> tuple[bool, bool, bool]:
    """(skip, no-focus, no-colour) contributed by one open tag."""
    cls = re.search(r"""class\s*=\s*["']([^"']*)["']""", attrs)
    cls = cls.group(1).split() if cls else []
    lang = re.search(r"""lang\s*=\s*["']?zh""", attrs)
    skip = (name in _SKIP or bool({"zh", "el", "zhver"} & set(cls))
            or (lang is not None and name != "span"))
    painted = any(re.match(r"(el|bg|f)-", c) for c in cls) or "chip" in cls or bool(
        re.search(r"""style\s*=\s*["'][^"']*(?<![-\w])color\s*:""", attrs))
    return skip, name in _FOCUS_NO, name in _COLOR_NO or painted


def _tipify_text(seg: str, focus: bool, colour: bool, strip_py: bool) -> str:
    readings: list[str] = []
    if strip_py and _CJK.search(seg):  # inline pinyin -> a marker holding the reading
        buf, p = [], 0
        for m in _RUNX.finditer(seg):
            if m.start() < p:
                continue
            buf.append(seg[p:m.end()])
            p = m.end()
            r = _inline_reading(m.group(0), seg[p:])
            if r:
                readings.append(r[2])
                buf.append(f"\x01{len(readings) - 1}\x02" + r[1])
                p += r[0]
        seg = "".join(buf) + seg[p:]
    out, pos = [], 0
    for m in _TOKEN.finditer(seg):
        out.append(seg[pos:m.start()])
        pos = m.end()
        if m.group(2):                                    # an English element word
            word, ch = m.group(1), m.group(3)
            rd = readings[int(m.group(4))] if m.group(4) else ""
            prev = seg[max(0, m.start() - 9):m.start()]
            inner = word + (f" ({zh_span(ch, focus, rd)})" if ch else "")
            if colour and (ch is None or EL_CLASS[ch] == EL_CLASS[m.group(2)]) \
                    and not re.search(r"Heaven,? (?:and )?$", prev):
                out.append(f'<span class="el el-{EL_CLASS[m.group(2)]}">{inner}</span>')
            else:
                out.append(inner)
            continue
        run = m.group(5)
        sp = zh_span(run, focus, readings[int(m.group(6))] if m.group(6) else "")
        if colour and run in EL_CLASS:
            sp = f'<span class="el el-{EL_CLASS[run]}">{sp}</span>'
        out.append(sp)
    out.append(seg[pos:])
    return "".join(out)


def tipify_html(html: str, strip_py: bool = True) -> str:
    """Wrap every Chinese run of an English page's <body> in the tooltip span, move any
    pinyin written inline into the span's tooltip (strip_py), and give the five elements
    their colour.  Scripts, styles, form controls, SVG, Chinese-version blocks and spans
    already processed are left alone; links, buttons and headings get no colour, and inside
    links and buttons the span is title-only (not focusable).  Idempotent."""
    i = html.find("<body")
    head, body = (html[:i], html[i:]) if i >= 0 else ("", html)
    out, stack, pos = [], [], 0
    while True:
        m = _TAG.search(body, pos)
        seg = body[pos:m.start() if m else len(body)]
        if seg:
            skip = any(f[0] for _, f in stack)
            if skip or not (_CJK.search(seg) or re.search(r"Wood|Fire|Earth|Metal|Water", seg)):
                out.append(seg)
            else:
                out.append(_tipify_text(seg, not any(f[1] for _, f in stack),
                                        not any(f[2] for _, f in stack), strip_py))
        if not m:
            break
        out.append(m.group(0))
        pos = m.end()
        if m.group(0).startswith("<!--"):
            continue
        close, name, attrs = m.group(1), m.group(2).lower(), m.group(3) or ""
        if close:
            for j in range(len(stack) - 1, -1, -1):
                if stack[j][0] == name:
                    del stack[j:]
                    break
        elif name in _RAW:
            e = re.compile(r"</" + name + r"\s*>", re.I).search(body, pos)
            end = e.start() if e else len(body)
            out.append(body[pos:end])
            pos = end
        elif name not in _VOID and not attrs.rstrip().endswith("/"):
            stack.append((name, _tagflags(name, attrs)))
    return head + "".join(out)


def table_for_js() -> dict:
    """The compact table web/glossary.js embeds: terms, aliases, and the per-character pinyin of
    the 3,500 common characters plus every glossary character (for page labels the table lacks)."""
    import json
    from pathlib import Path
    cp = _charpy()
    keep = _js_keep()
    return {"terms": {k: list(v) for k, v in TERMS.items()}, "aliases": ALIASES,
            "list_cats": sorted(_LIST_CATS), "simp_only": "".join(sorted(_SIMP_ONLY)),
            "charpy": "".join(c + cp[c] + " " for c in sorted(keep) if c in cp)}
