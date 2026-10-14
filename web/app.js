/* FengShui Family Compass — M2 UI (vanilla JS, no deps) */
/* Reading strings (Phase 2, Simplified Chinese). READING_EN holds the English of every reading sentence by id; on /zh pages
   window.I18N.reading ({id: 中文}, injected by scripts/build_zh.py) takes over. RS(id, slots) fills {name} slots. English pages never read I18N. */
const READING_EN = {
  "appjs.CHAPTERS.makeup.title": "Make-up",
  "appjs.CHAPTERS.makeup.q": "What are you made of?",
  "appjs.CHAPTERS.makeup.tech": "Four pillars",
  "appjs.CHAPTERS.makeup.what": "the four pillars",
  "appjs.CHAPTERS.balance.title": "Balance",
  "appjs.CHAPTERS.balance.q": "What do you have too much or too little of?",
  "appjs.CHAPTERS.balance.tech": "Elements",
  "appjs.CHAPTERS.balance.what": "the five elements",
  "appjs.CHAPTERS.drives.title": "Drives",
  "appjs.CHAPTERS.drives.q": "What drives you?",
  "appjs.CHAPTERS.drives.tech": "Ten gods",
  "appjs.CHAPTERS.drives.what": "the ten gods",
  "appjs.CHAPTERS.timing.title": "Timing",
  "appjs.CHAPTERS.timing.q": "What is coming, and when?",
  "appjs.CHAPTERS.timing.tech": "Luck cycles",
  "appjs.CHAPTERS.timing.what": "luck cycles",
  "appjs.CHAPTERS.space.title": "Space",
  "appjs.CHAPTERS.space.q": "Where should you sit, sleep and work?",
  "appjs.CHAPTERS.space.tech": "Compass",
  "appjs.CHAPTERS.space.what": "eight-house directions",
  "appjs.CHART_CAP.makeup": "Your eight characters.",
  "appjs.CHART_CAP.balance": "Your five elements, and how they feed and check each other.",
  "appjs.CHART_CAP.drives": "The ten classical roles, grouped.",
  "appjs.CHART_CAP.timing": "Your luck pillars, decade by decade.",
  "appjs.CHART_CAP.space": "The eight directions for your Kua number.",
  "appjs.PILLAR_KEYS.year.label": "year",
  "appjs.PILLAR_KEYS.month.label": "month",
  "appjs.PILLAR_KEYS.day.label": "you",
  "appjs.PILLAR_KEYS.hour.label": "hour",
  "appjs.TG_EN_FALLBACK.\u6bd4\u80a9": "Friend",
  "appjs.TG_EN_FALLBACK.\u52ab\u8ca1": "Rob Wealth",
  "appjs.TG_EN_FALLBACK.\u98df\u795e": "Eating God",
  "appjs.TG_EN_FALLBACK.\u50b7\u5b98": "Hurting Officer",
  "appjs.TG_EN_FALLBACK.\u6b63\u8ca1": "Direct Wealth",
  "appjs.TG_EN_FALLBACK.\u504f\u8ca1": "Indirect Wealth",
  "appjs.TG_EN_FALLBACK.\u6b63\u5b98": "Direct Officer",
  "appjs.TG_EN_FALLBACK.\u4e03\u6bba": "Seven Killings",
  "appjs.TG_EN_FALLBACK.\u6b63\u5370": "Direct Resource",
  "appjs.TG_EN_FALLBACK.\u504f\u5370": "Indirect Resource",
  "appjs.PHASE_LINE.growth": "Conditions favour building.",
  "appjs.PHASE_LINE.consolidation": "Build reserves rather than leap.",
  "appjs.PHASE_LINE.transition": "Expect change at home or work.",
  "appjs.PHASE_LINE.corrective": "Protect health, money and close ties.",
  "appjs.ZODIAC.\u9f20.animal": "Rat",
  "appjs.ZODIAC.\u725b.animal": "Ox",
  "appjs.ZODIAC.\u864e.animal": "Tiger",
  "appjs.ZODIAC.\u5154.animal": "Rabbit",
  "appjs.ZODIAC.\u9f99.animal": "Dragon",
  "appjs.ZODIAC.\u86c7.animal": "Snake",
  "appjs.ZODIAC.\u9a6c.animal": "Horse",
  "appjs.ZODIAC.\u7f8a.animal": "Goat",
  "appjs.ZODIAC.\u7334.animal": "Monkey",
  "appjs.ZODIAC.\u9e21.animal": "Rooster",
  "appjs.ZODIAC.\u72d7.animal": "Dog",
  "appjs.ZODIAC.\u732a.animal": "Pig",
  "appjs.EL_EN.\u6728": "Wood",
  "appjs.EL_EN.\u706b": "Fire",
  "appjs.EL_EN.\u571f": "Earth",
  "appjs.EL_EN.\u91d1": "Metal",
  "appjs.EL_EN.\u6c34": "Water",
  "appjs.BAZHAI_EN.\u751f\u6c23.0": "Vitality",
  "appjs.BAZHAI_EN.\u751f\u6c23.1": "the best — growth, energy, opportunity; ideal for bed, desk, main door",
  "appjs.BAZHAI_EN.\u5929\u91ab.0": "Heavenly Doctor",
  "appjs.BAZHAI_EN.\u5929\u91ab.1": "health and recovery; good bedroom direction when unwell",
  "appjs.BAZHAI_EN.\u5ef6\u5e74.0": "Longevity",
  "appjs.BAZHAI_EN.\u5ef6\u5e74.1": "harmony and relationships; supports couples and family bonds",
  "appjs.BAZHAI_EN.\u4f0f\u4f4d.0": "Stability",
  "appjs.BAZHAI_EN.\u4f0f\u4f4d.1": "calm, steady progress; suits quiet work and rest",
  "appjs.BAZHAI_EN.\u798d\u5bb3.0": "Mishap",
  "appjs.BAZHAI_EN.\u798d\u5bb3.1": "minor troubles and friction; fine for storage or bathrooms",
  "appjs.BAZHAI_EN.\u516d\u715e.0": "Six Killings",
  "appjs.BAZHAI_EN.\u516d\u715e.1": "conflict and setbacks; avoid placing the bed here",
  "appjs.BAZHAI_EN.\u4e94\u9b3c.0": "Five Ghosts",
  "appjs.BAZHAI_EN.\u4e94\u9b3c.1": "instability, quarrels, losses; keep activity here light",
  "appjs.BAZHAI_EN.\u7d55\u547d.0": "Severed Fate",
  "appjs.BAZHAI_EN.\u7d55\u547d.1": "the most adverse; avoid prolonged sleeping or sitting",
  "appjs.DIR_WORD_EN.N": "north",
  "appjs.DIR_WORD_EN.S": "south",
  "appjs.DIR_WORD_EN.E": "east",
  "appjs.DIR_WORD_EN.W": "west",
  "appjs.DIR_WORD_EN.NE": "north-east",
  "appjs.DIR_WORD_EN.NW": "north-west",
  "appjs.DIR_WORD_EN.SE": "south-east",
  "appjs.DIR_WORD_EN.SW": "south-west",
  "appjs.LEGENDS.chart.01.term": "Four Pillars",
  "appjs.LEGENDS.chart.01.gloss": "the Four Pillars: birth year·month·day·hour, each written as two characters — eight in all",
  "appjs.LEGENDS.chart.02.term": "Stem / branch",
  "appjs.LEGENDS.chart.02.gloss": "the top character of a pillar is its heavenly stem, the bottom its earthly branch (with the zodiac animal)",
  "appjs.LEGENDS.chart.03.term": "日主 Day Master",
  "appjs.LEGENDS.chart.03.gloss": "the day stem — the character that IS you; every other character is read by its relationship to it",
  "appjs.LEGENDS.chart.04.term": "Ten Gods",
  "appjs.LEGENDS.chart.04.gloss": "that relationship, named — translated god-by-god in §4",
  "appjs.LEGENDS.chart.05.term": "Hidden stems",
  "appjs.LEGENDS.chart.05.gloss": "hidden stems: extra elements stored inside each branch, listed under the pillar",
  "appjs.LEGENDS.chart.06.term": "Zodiac animal",
  "appjs.LEGENDS.chart.06.gloss": "the zodiac animal of the birth-year branch",
  "appjs.LEGENDS.chart.07.term": "Kua number",
  "appjs.LEGENDS.chart.07.gloss": "your personal trigram — decides your lucky compass directions (§7)",
  "appjs.LEGENDS.chart.08.term": "Natal star",
  "appjs.LEGENDS.chart.08.gloss": "the life star (Nine Star, 九星) of the birth year — the number feng shui overlays use for you",
  "appjs.LEGENDS.chart.09.term": "Life Palace",
  "appjs.LEGENDS.chart.09.gloss": "an auxiliary destiny point derived from the birth month + hour — classical readers weigh it for temperament and life theme",
  "appjs.LEGENDS.chart.10.term": "Conception Palace",
  "appjs.LEGENDS.chart.10.gloss": "the pillar of the estimated conception month — a supplementary root the chart can draw on",
  "appjs.LEGENDS.chart.11.term": "Useful god",
  "appjs.LEGENDS.chart.11.gloss": "the elements that act as this chart's medicine (§5)",
  "appjs.LEGENDS.chart.12.term": "Symbolic stars",
  "appjs.LEGENDS.chart.12.gloss": "symbolic stars carried by the pillars — detailed with meanings in §9",
  "appjs.LEGENDS.chart.13.term": "Sound element (Nayin)",
  "appjs.LEGENDS.chart.13.gloss": "the pillar's melodic element — its poetic name in the 60-cycle (e.g. Sea Metal, 海中金)",
  "appjs.LEGENDS.chart.14.term": "Life stage",
  "appjs.LEGENDS.chart.14.gloss": "the Day Master's life-stage in that branch (birth→peak→decline cycle) — vitality flavour, not a verdict",
  "appjs.LEGENDS.chart.15.gloss": "the 10-year luck cycles that colour each decade (§6)",
  "appjs.LEGENDS.1.01.term": "Wood / Fire / Earth / Metal / Water",
  "appjs.LEGENDS.1.01.gloss": "wood / fire / earth / metal / water",
  "appjs.LEGENDS.1.02.term": "weight",
  "appjs.LEGENDS.1.02.gloss": "weighted count of visible + hidden characters carrying that element",
  "appjs.LEGENDS.1.03.term": "reading it",
  "appjs.LEGENDS.1.03.gloss": "balance beats abundance — the tallest bar is the heaviest, not the best",
  "appjs.LEGENDS.1.04.term": "wheel: node size",
  "appjs.LEGENDS.1.04.gloss": "that element's share of THIS chart; gold ring = your Day Master",
  "appjs.LEGENDS.1.05.term": "green arrows (generating)",
  "appjs.LEGENDS.1.05.gloss": "the generating cycle (wood→fire→earth→metal→water) — thicker = stronger feeder",
  "appjs.LEGENDS.1.06.term": "red lines (controlling)",
  "appjs.LEGENDS.1.06.gloss": "the controlling cycle — solid red = an actual affliction in this chart (a heavy element crushing a weak one)",
  "appjs.LEGENDS.1.07.term": "The five roles",
  "appjs.LEGENDS.1.07.gloss": "the five roles every element plays relative to the Day Master — resource, output, wealth, pressure, peers; the ten gods refine these",
  "appjs.LEGENDS.2.01.term": "Strong",
  "appjs.LEGENDS.2.01.gloss": "the chart can afford to spend — output, wealth and pressure suit it",
  "appjs.LEGENDS.2.02.term": "Weak",
  "appjs.LEGENDS.2.02.gloss": "the chart needs feeding — support, rest and resource suit it",
  "appjs.LEGENDS.2.03.term": "support ratio",
  "appjs.LEGENDS.2.03.gloss": "share of the chart on the Day Master's side",
  "appjs.LEGENDS.2.04.term": "root mass",
  "appjs.LEGENDS.2.04.gloss": "the Day Master's own element hidden inside the branches — its anchoring",
  "appjs.LEGENDS.3.01.term": "Stem row",
  "appjs.LEGENDS.3.01.gloss": "the ten god of each pillar's visible character",
  "appjs.LEGENDS.3.02.term": "Hidden-stem row",
  "appjs.LEGENDS.3.02.gloss": "the gods of the hidden stems inside each branch",
  "appjs.LEGENDS.3.03.term": "Direct / Indirect / Seven Killings …",
  "appjs.LEGENDS.3.03.gloss": "each god's name and meaning is translated in §4's list",
  "appjs.LEGENDS.4.01.term": "Direct vs indirect",
  "appjs.LEGENDS.4.01.gloss": "Direct = the proper/conventional form of a domain, Indirect = its unconventional twin (opposite-polarity / same-polarity pairing)",
  "appjs.LEGENDS.4.02.gloss": "share of the chart's characters classified as that god — where life's attention defaults",
  "appjs.LEGENDS.4.03.term": "wheel: Day Master centre",
  "appjs.LEGENDS.4.03.gloss": "your Day Master; the five groups around it are the five roles from §1's element wheel, refined into gods",
  "appjs.LEGENDS.4.04.term": "node colour & size",
  "appjs.LEGENDS.4.04.gloss": "colour = that group's actual element for YOUR Day Master (§1 palette); size = its share of the chart",
  "appjs.LEGENDS.4.05.term": "green / red arrows",
  "appjs.LEGENDS.4.05.gloss": "generating (feeding) and controlling cycles between the god groups — same cycles as §1, one level up",
  "appjs.LEGENDS.4.06.term": "satellites",
  "appjs.LEGENDS.4.06.gloss": "each group's Direct/Indirect pair with its own share — faded = barely present",
  "appjs.LEGENDS.4.07.term": "rooted / floating",
  "appjs.LEGENDS.4.07.gloss": "a visible god whose element also sits in the branches is rooted (durable); visible-only is floating (shows up socially, needs backing)",
  "appjs.LEGENDS.4.08.term": "pair patterns",
  "appjs.LEGENDS.4.08.gloss": "classical combinations (Eating God controls Seven Killings, Hurting Officer meets Direct Officer, …) — the gods' joint behaviour, not just their sizes",
  "appjs.LEGENDS.5.01.term": "Useful god (favourable)",
  "appjs.LEGENDS.5.01.gloss": "favourable — the chart's medicine; carry these elements in colours, directions, fields",
  "appjs.LEGENDS.5.02.term": "Avoid",
  "appjs.LEGENDS.5.02.gloss": "elements that aggravate the imbalance",
  "appjs.LEGENDS.5.03.term": "Support-and-restrain method",
  "appjs.LEGENDS.5.03.gloss": "support-the-weak / restrain-the-strong: the method that picked them",
  "appjs.LEGENDS.5.04.term": "Seasonal adjustment",
  "appjs.LEGENDS.5.04.gloss": "seasonal climate cross-check (a winter chart may need fire regardless)",
  "appjs.LEGENDS.6.01.gloss": "one pillar per decade of life, starting from the month pillar",
  "appjs.LEGENDS.6.02.term": "ages",
  "appjs.LEGENDS.6.02.gloss": "your age span under that pillar",
  "appjs.LEGENDS.6.03.term": "god labels",
  "appjs.LEGENDS.6.03.gloss": "the decade's dominant themes, in §4's vocabulary",
  "appjs.LEGENDS.6.04.term": "highlighted",
  "appjs.LEGENDS.6.04.gloss": "the decade you are in now",
  "appjs.LEGENDS.7.01.term": "Eight House",
  "appjs.LEGENDS.7.01.gloss": "eight-house school: your trigram splits the compass into 4 green (use) and 4 red (avoid) directions",
  "appjs.LEGENDS.7.02.term": "how to use",
  "appjs.LEGENDS.7.02.gloss": "green = bed headboard, desk facing, main door; red = fine for storage/bathroom",
  "appjs.LEGENDS.7.03.term": "personal",
  "appjs.LEGENDS.7.03.gloss": "this map differs per person — a couple can have opposite maps",
  "appjs.LEGENDS.8.01.term": "score",
  "appjs.LEGENDS.8.01.gloss": "starts at a neutral 50; every chip is a rule that moved it",
  "appjs.LEGENDS.8.02.gloss": "a natural strength",
  "appjs.LEGENDS.8.03.gloss": "an area to consciously support",
  "appjs.LEGENDS.8.04.term": "chips",
  "appjs.LEGENDS.8.04.gloss": "the audit trail — hover none, they are the working",
  "appjs.LEGENDS.8.05.term": "Seated",
  "appjs.LEGENDS.8.05.gloss": "the domain's signal god actually resides in its primary palace — a seated signal lands harder than share alone suggests",
  "appjs.LEGENDS.8.06.term": "Wealth vault",
  "appjs.LEGENDS.8.06.gloss": "the wealth-element storage branch (Chen, Xu, Chou, Wei): open = accumulation compounds; sealed = opens in its clash years (§13); absent = wealth flows, systems must do the storing",
  "appjs.LEGENDS.9.01.gloss": "symbolic stars: classical stem-branch patterns, flavour on top of structure",
  "appjs.LEGENDS.9.02.term": "Year / month / day / hour tag",
  "appjs.LEGENDS.9.02.gloss": "which pillar carries it — ancestry · career/parents · self/spouse · children/later life",
  "appjs.LEGENDS.10.01.term": "axes",
  "appjs.LEGENDS.10.01.gloss": "read straight off §4's distribution — the basis column shows the exact threshold",
  "appjs.LEGENDS.10.02.term": "no strong tendency",
  "appjs.LEGENDS.10.02.gloss": "a legitimate result, not a failure",
  "appjs.LEGENDS.11.01.term": "element ↔ organs",
  "appjs.LEGENDS.11.01.gloss": "traditional five-element medicine correspondence — reference, not medical advice",
  "appjs.LEGENDS.11.02.term": "status",
  "appjs.LEGENDS.11.02.gloss": "flags an element too weak or too heavy to lean on",
  "appjs.LEGENDS.12.01.term": "fit",
  "appjs.LEGENDS.12.01.gloss": "how efficiently effort converts to reward in that field",
  "appjs.LEGENDS.12.02.term": "priced against",
  "appjs.LEGENDS.12.02.gloss": "low-ranked fields cost more energy here — never forbidden",
  "appjs.LEGENDS.13.01.term": "◉ window",
  "appjs.LEGENDS.13.01.gloss": "a supportive year for that life dimension",
  "appjs.LEGENDS.13.02.term": "⚠ caution",
  "appjs.LEGENDS.13.02.gloss": "navigate deliberately — a note, never a verdict",
  "appjs.LEGENDS.13.03.term": "· quiet",
  "appjs.LEGENDS.13.03.gloss": "nothing notable triggered",
  "appjs.LEGENDS.13.04.term": "climate / weather",
  "appjs.LEGENDS.13.04.gloss": "the decade sets the climate, the year the weather",
  "appjs.LEGENDS.13.05.term": "Peach blossom",
  "appjs.LEGENDS.13.05.gloss": "peach-blossom: the romance/charm activation branch",
  "appjs.PHASE_EN.growth": "expanding",
  "appjs.PHASE_EN.consolidation": "gathering",
  "appjs.PHASE_EN.transition": "changing",
  "appjs.PHASE_EN.corrective": "repairing",
  "appjs.GRP_THEME.\u6bd4\u52ab": "peers and self-drive",
  "appjs.GRP_THEME.\u5370": "learning and support",
  "appjs.GRP_THEME.\u98df\u50b7": "expression and output",
  "appjs.GRP_THEME.\u8ca1": "wealth and practical results",
  "appjs.GRP_THEME.\u5b98\u6bba": "structure and pressure",
  "appjs.ACT_EN.moving": "moving",
  "appjs.ACT_EN.signing": "signing",
  "appjs.ACT_EN.marriage": "marriage",
  "appjs.ACT_EN.travel": "travel",
  "appjs.ACT_EN.medical": "medical",
  "appjs.ACT_EN.launch": "launch",
  "appjs.OFFICER_EN.\u5efa": "Establish",
  "appjs.OFFICER_EN.\u9664": "Remove",
  "appjs.OFFICER_EN.\u6ee1": "Full",
  "appjs.OFFICER_EN.\u5e73": "Neutral",
  "appjs.OFFICER_EN.\u5b9a": "Settle",
  "appjs.OFFICER_EN.\u6267": "Hold",
  "appjs.OFFICER_EN.\u7834": "Destruction",
  "appjs.OFFICER_EN.\u5371": "Danger",
  "appjs.OFFICER_EN.\u6210": "Completion",
  "appjs.OFFICER_EN.\u6536": "Receive",
  "appjs.OFFICER_EN.\u5f00": "Open",
  "appjs.OFFICER_EN.\u95ed": "Close",
  "appjs.TAG_EN.\u5408\u65e5\u652f": "combines with your day branch",
  "appjs.TAG_EN.\u51b2\u65e5\u652f": "clashes your day branch",
  "appjs.TAG_EN.\u5bb3\u65e5\u652f": "harms your day branch",
  "appjs.TAG_EN.\u51b2\u751f\u8096": "clashes your zodiac animal",
  "appjs.TAG_EN.\u5211\u65e5\u652f": "punishes your day branch",
  "appjs.GRP_EN.\u5b98\u6bba": "authority",
  "appjs.GRP_EN.\u5370\u661f": "resource",
  "appjs.GRP_EN.\u6bd4\u52ab": "peers",
  "appjs.GRP_EN.\u98df\u50b7": "output",
  "appjs.GRP_EN.\u8ca1\u661f": "wealth",
  "appjs.TG_GIST.\u6bd4\u80a9": "peers and self-reliance",
  "appjs.TG_GIST.\u52ab\u8ca1": "rivals and boldness",
  "appjs.TG_GIST.\u98df\u795e": "gentle output, enjoyment and ease",
  "appjs.TG_GIST.\u50b7\u5b98": "sharp output and a will to challenge",
  "appjs.TG_GIST.\u504f\u8ca1": "windfall wealth and opportunity",
  "appjs.TG_GIST.\u6b63\u8ca1": "steady wealth, salary and savings",
  "appjs.TG_GIST.\u4e03\u6bba": "raw pressure and ambition",
  "appjs.TG_GIST.\u6b63\u5b98": "proper authority, rules and status",
  "appjs.TG_GIST.\u504f\u5370": "unconventional learning and solitary study",
  "appjs.TG_GIST.\u6b63\u5370": "nurturing support, study and protection",
  "appjs.GLOSS_IX.\u516d\u5bb3": "harms",
  "appjs.GLOSS_IX.\u51b2": "clashes with",
  "appjs.GLOSS_IX.\u5211": "punishes",
  "appjs.GLOSS_IX.\u7834": "breaks",
  "appjs.GLOSS_IX.\u516d\u5408": "combines with",
  "appjs.GLOSS_IX.\u534a\u5408": "half-combines with",
  "appjs.renderPerson.001": "raw data",
  "appjs.renderPerson.002": "useful god",
  "appjs.renderPerson.004": "life domains",
  "appjs.renderPerson.005": "symbolic stars",
  "appjs.renderPerson.006": "timing windows",
  "appjs.renderPerson.007": "Interpretation: {SEC_ZH_n} — the numbers read out",
  "appjs.renderPerson.008": "Strategy: {SEC_ZH_n} — what this asks of you",
  "appjs.renderPerson.015": "{who} <small class=\"rp-sub1\">Your reading (<span class=\"zh\" lang=\"zh-Hans\" tabindex=\"0\" title=\"mìng shū · the reading\">命书</span>)</small>",
  "appjs.renderPerson.016": "{who}: your BaZi reading",
  "appjs.bootReading.001": "load failed: {e_message}",
  "appjs.stratBlock.001": "What this asks of you",
  "appjs.stratBlock.002": "<b>Monthly rhythm</b>\n        (recurring every year): green months feed this chart, red months drain it —\n        schedule pushes into green months, recovery into red ones.",
  "appjs.stratBlock.003": "<b>{s_kid}:</b>\n        primary risk point — {dnAll_s}",
  "appjs.stratBlock.004": "<b>Peach blossom:</b> {s_taohua} · <b>Zodiac allies:</b> {s_allies}\n        · <b>Zodiac friction:</b> {s_clash}",
  "appjs.stratBlock.005": "<b>Element fit:</b> {dnAll_s}",
  "appjs.stratBlock.006": "Partnership & friendship patterns",
  "appjs.stratBlock.007": "Relationship patterns",
  "appjs.stratBlock.008": "How to parent them",
  "appjs.stratBlock.009": "How to work with them",
  "appjs.stratBlock.010": "<b>Trigger years:</b>\n        {s_trigger_years} ·\n        <b>recovery years:</b> {s_recovery_years}",
  "appjs.stratBlock.011": "none flagged in the next decade",
  "appjs.stratBlock.012": "<span>venture</span><b>{s_pct_corp}% structured</b>\n          <span>corporate</span>",
  "appjs.stratBlock.013": "structure evidence: {s_corp_ev} ·\n        volatility evidence: {s_vent_ev}",
  "appjs.stratBlock.014": "<b>Wealth pattern:</b>\n        {dnAll_s} {dnAll_s_2}",
  "appjs.stratBlock.015": "<b>Act-year windows:</b>\n          {s_act_windows}",
  "appjs.stratBlock.016": "no wealth-activation years in the next decade — build, don't chase",
  "appjs.stratBlock.017": "⚠ hold-back years: {s_cautions}",
  "appjs.stratBlock.018": "<b>Next-decade handoff:</b> {dnAll_s}",
  "appjs.stratBlock.019": "<b>Exam-year overlay:</b>",
  "appjs.pIdentity.001": "This is your day pillar: you, at every age. Each stage of life has its own side, shown below; you are now in {year_your}.",
  "appjs.pIdentity.002": "your roots",
  "appjs.pIdentity.003": "your working years",
  "appjs.pIdentity.004": "your home years",
  "appjs.pIdentity.005": "your later years",
  "appjs.pIdentity.006": "This is your day pillar: you, at every age. Each stage of life has its own side, shown below.",
  "appjs.pSides.001": "Your four sides",
  "appjs.pSides.002": "<span class=\"rp-here\">You are here</span>",
  "appjs.pSides.003": ", <span class=\"rp-nw\">ages {s_ages}</span>",
  "appjs.pSides.004": "<b>Children palace:</b> {kids}",
  "appjs.pAnswers.001": "Your balance",
  "appjs.pAnswers.003": "What helps you",
  "appjs.pAnswers.004": "Two things to do",
  "appjs.pAnswers.005": "your balance",
  "appjs.pAnswers.006": "what helps you",
  "appjs.pAnswers.007": "This year",
  "appjs.pAnswers.008": "this year",
  "appjs.pAnswers.009": "two things to do",
  "appjs.synthNote.001": "Findings",
  "appjs.synthNote.002": "Assessment",
  "appjs.synthNote.003": "Plan",
  "appjs.synthNote.004": "<b>How this was worked out.</b> {sy_confidence}",
  "appjs.synthNote.005": "The full report, in classical terms",
  "appjs.pChapBar.001": "Chapters",
  "appjs.readingChapters.001": "Sources and the full interpretation",
  "appjs.tidyEvidence.001": "What this shows",
  "appjs.tidyEvidence.002": "How to read this chart",
  "appjs.buildPillars.001": "fighting the season",
  "appjs.buildPillars.002": "carried by the season",
  "appjs.buildPillars.003": "level with the season",
  "appjs.buildPillars.004": "Four-Pillar Grid",
  "appjs.buildPillars.005": "A {weak_weak} {elc_dm} {elw_dmEl} day master, {season} — {fav_map} {fav_length} your medicine.",
  "appjs.buildPillars.006": "score {c_strength_score}",
  "appjs.buildPillars.007": "Branch interactions",
  "appjs.buildPillars.008": "Arcs join the pillars whose branches interact. Dashed amber = 害·刑·冲 (friction, punishment, clash);\n      solid green = 合 (combination). Read with the palaces: a tension between Year and Month touches ancestry\n      and career; Day is the self and spouse.{its_length}",
  "appjs.buildPillars.009": "<b>Columns:</b> <span class=\"keepzh\">神煞</span> symbolic star · <span class=\"keepzh\">柱</span> pillar (<span class=\"keepzh\">年</span> year, <span class=\"keepzh\">月</span> month, <span class=\"keepzh\">日</span> day, <span class=\"keepzh\">时</span> hour) · <span class=\"keepzh\">吉忌</span> helps (<span class=\"keepzh\">吉</span>) or asks for care (<span class=\"keepzh\">忌</span>)",
  "appjs.buildPillars.010": "<b>{en}</b> (<span class=\"keepzh\">{s_star}</span>), in your {s_pillars} pillar{s_pillars_2}: {gist}. {neg_Asks}",
  "appjs.buildPillars.011": "Asks for care.",
  "appjs.buildPillars.012": "Helps you.",
  "appjs.buildPillars.013": "{part_pos} brings {part_pos_2}",
  "appjs.buildPillars.014": "No helpful star is carried",
  "appjs.buildPillars.015": "; {part_neg} in your {PEN_neg} pillar asks for care: {part_neg_2}.",
  "appjs.buildPillars.016": ", and no star asks for care.",
  "appjs.buildPillars.018": "Symbolic stars (神煞) are classical patterns read from the stems and branches; they add flavour on top of the chart's structure and never override the balance reading.",
  "appjs.buildPillars.019": "Interpretation — the numbers read out",
  "appjs.buildPillars.020": "Every rule this reading cites",
  "appjs.buildElements.001": "单位 = 字重，不是个数：天干各 1.0、地支本气 1.0、余气 1/3，全盘合计 {wtot_toFixed}。\n      Units are weighted character counts: each stem 1.0, each branch's main hidden stem 1.0, each minor hidden stem 1/3.",
  "appjs.buildElements.002": "Element pentagon",
  "appjs.buildElements.003": "{elb_pr} {elw_pr} fights you hardest ({pr_share}%); {elb_rs} {elw_rs} feeds you {pr_share_2}{rs_share}% — {pr_share_3}.",
  "appjs.buildElements.004": "pressure outweighs support",
  "appjs.buildElements.005": "support outweighs pressure",
  "appjs.buildElements.006": "Authority",
  "appjs.buildElements.007": "Resource",
  "appjs.buildElements.008": "<b>五行关系 — the five relations, listed</b>{eflowsList_c}",
  "appjs.buildElements.009": "Strength gauge and its arithmetic",
  "appjs.buildElements.010": "<span class=\"tag\">support ratio {st_support_ratio}%</span> <span class=\"tag\">root mass {st_root_ratio}%</span> <span class=\"tag\">{st_formation_status}</span>",
  "appjs.buildElements.011": "{weak_Weak} ({st_score}) — {sp_the}{stage_stage}, not which element has the biggest bar.",
  "appjs.buildElements.014": "the season controls you",
  "appjs.buildElements.015": "the season carries you",
  "appjs.buildElements.016": "the season is neutral",
  "appjs.buildElements.017": "{elb_topSup} {topSup_zh} {elw_topSup} supports hardest ({topSup_w}) — support {pt_support} {pt_support_2} drain {pt_drain}, {weak_pt}.",
  "appjs.buildElements.018": "yet the season still tips it weak",
  "appjs.buildElements.019": "yet the season still carries it strong",
  "appjs.buildElements.020": "and the verdict follows",
  "appjs.buildElements.021": "Support",
  "appjs.buildElements.022": "Drain",
  "appjs.buildElements.024": "Formation check: {st_formation_detail}. Support ratio = share of the chart feeding the Day Master; root mass = share of hidden stems carrying its element.",
  "appjs.buildElements.025": "organ systems",
  "appjs.buildElements.026": "too much",
  "appjs.buildElements.027": "too little",
  "appjs.buildElements.028": "<b>{h_en}</b> (<span class=\"keepzh\">{h_element}</span>): {h_organs}; watch {h_aspects}.",
  "appjs.buildElements.029": "{elb_excess} {elw_excess} excess ({excess_share}%) — watch {excess_organs}; {excess_aspects} is the pattern to notice.",
  "appjs.buildElements.030": "{elb_weakEl} {elw_weakEl} weak ({weakEl_share}%) — support {weakEl_organs}; watch {weakEl_aspects}.",
  "appjs.buildElements.031": "All five elements sit in range — no organ system is flagged.",
  "appjs.buildElements.032": "Health element map",
  "appjs.buildElements.033": "Excess",
  "appjs.buildElements.034": "Deficient",
  "appjs.buildGods.001": "The god wheel",
  "appjs.buildGods.002": "{gs} {GRP_EN_gs} lead your wheel at {gs_2}%, {gs_3} {GRP_EN_gs_2} {gs_gs} at {gs_4}%.",
  "appjs.buildGods.003": "close behind",
  "appjs.buildGods.004": "The five circles are the ten roles in five groups; a bigger circle is a bigger share of your chart. The centre is you, the Day Master (日元).",
  "appjs.buildGods.005": "Solid green arrows: each group feeds the next. Dashed red arrows: each group checks the one it points at.",
  "appjs.buildGods.006": "<b class=\"keepzh\">{zh}</b> <b>{name}</b>: {en_a} ({a}) and {en_b} ({b})",
  "appjs.buildGods.007": "0% (absent)",
  "appjs.buildGods.008": "Spouse star",
  "appjs.buildGods.009": "Wealth stars",
  "appjs.buildGods.010": "Authority stars",
  "appjs.buildGods.011": "Resource stars",
  "appjs.buildGods.012": "Output stars",
  "appjs.buildGods.013": "Peer stars",
  "appjs.buildGods.014": "Ten-god bars",
  "appjs.buildGods.015": "Your chart runs on {godc_dm} {en_g1} ({Math_round}%) — {c_tengods_legend}.",
  "appjs.buildGods.016": "{absent_length} of 10 gods",
  "appjs.buildGods.017": "Each bar is how much of your chart one role takes up. A role is what a character is to you, the Day Master.",
  "appjs.buildGods.018": "<b>Bands:</b> 20% or more is prominent, 8% or more is present, under 8% is faint, 0% is absent.",
  "appjs.buildGods.019": "<span>{a_poles_left_zh} <small>{a_poles_left_en}</small></span><span class=\"mid\">neutral</span>\n        <span>{a_poles_right_zh} <small>{a_poles_right_en}</small></span>",
  "appjs.buildGods.020": "Personality axes",
  "appjs.buildGods.021": "{sharp_verdict} — {sharp_metrics} make up {sharp_metrics_2}% of your chart, your sharpest trait.",
  "appjs.buildGods.022": "No strong tendency on any axis — a balanced profile, not a failure.",
  "appjs.buildGods.023": "<b>Visible stems:</b> {ti_rooted}",
  "appjs.buildGods.024": "pair patterns · {ti_patterns_length}",
  "appjs.buildGods.025": "No classical pair pattern triggers — the gods operate independently in this chart.",
  "appjs.buildGods.026": "Structure check",
  "appjs.buildGods.027": "{godc_dm} ({bad_pct}%) carries an unfavourable element ({elc_bad}) — use it deliberately, budget recovery.",
  "appjs.buildGods.028": "{godc_dm} ({good_pct}%) carries {elc_good}, one of your 用神 — a clean engine; using it strengthens the chart.",
  "appjs.buildGods.029": "The heavy gods sit outside both lists — structure is neutral here.",
  "appjs.buildGods.030": "{ti_favor} of {ti_favor_length} heavy gods",
  "appjs.buildGods.031": "{ti_rooted} stems",
  "appjs.buildGods.032": "Three checks a percentage chart cannot make: is the heavy god aligned with your 用神, is it rooted in the branches, and what do the gods form together. Personality is not static: the current decade (时运 tab) overlays its own gods.",
  "appjs.buildGods.033": "Month pillar",
  "appjs.buildGods.034": "Month · Day",
  "appjs.buildGods.035": "Year · Month",
  "appjs.buildGods.036": "正財·偏財 (spouse star)",
  "appjs.buildGods.037": "正官·七殺 (spouse star)",
  "appjs.buildGods.038": "Day branch",
  "appjs.buildGods.039": "才华 Talent &amp; enterprise",
  "appjs.buildGods.040": "Hour pillar",
  "appjs.buildGods.041": "人脉 Network &amp; competition",
  "appjs.buildGods.043": "<b>Columns:</b> <span class=\"keepzh\">领域</span> life area · <span class=\"keepzh\">分</span> score out of 100 (50 is neutral) · <span class=\"keepzh\">十神</span> the roles that govern it, with their share of your chart · <span class=\"keepzh\">得位</span> ✓ when those roles sit in the area's own pillar",
  "appjs.buildGods.044": "<b>{n_split}</b> (<span class=\"keepzh\">{n_split_2}</span>): a signal only, with no score of its own.",
  "appjs.buildGods.045": "Life domains: score, signal, seat",
  "appjs.buildGods.046": "{top_en} stands highest among charts, with a score of {top_score}; your heaviest signal is {heavyName_toLowerCase} — {heavy}%, {inPal_heavy} {heavy_2}.",
  "appjs.buildGods.047": "seated in",
  "appjs.buildGods.048": "Each score starts at a neutral 50; every rule listed under the table moved it by the amount shown.",
  "appjs.buildGods.049": "<b>Marriage:</b> {c_spouse_reading_star_li} {c_spouse_reading_palace_}",
  "appjs.buildGods.050": "The best fields",
  "appjs.buildGods.051": "<b>Industries that recharge you:</b>",
  "appjs.buildGods.052": "Roles that fit now",
  "appjs.buildGods.053": "Harder going, not off limits",
  "appjs.buildGods.054": "Industries: {A_map}",
  "appjs.buildGods.055": "Work that fits",
  "appjs.buildGods.056": "{T_en} fits you best{Rl_the}.",
  "appjs.buildGods.057": "; the closest role today is {Rl_role}",
  "appjs.buildGods.058": "No field stands out for this chart.",
  "appjs.buildGods.059": "Fields and roles are ranked by how well their element matches the elements that help you, and by how they suit your leading roles. A low-ranked field costs more energy here; it is never forbidden.",
  "appjs.buildGods.060": "<b>Standing</b> under a score is where that score sits among a fixed reference sample of 10,000 fictional charts ({v}), from 0 to 100. It is a relative standing among charts, not strength. The score itself is unchanged.",
  "appjs.buildGods.061": "standing {p}",
  "appjs.buildTiming.001": "▲ now",
  "appjs.buildTiming.002": "<b>Each card:</b> the ages, the decade's pillar (stem over branch), its phase, the two roles it brings, and what those roles mean.",
  "appjs.buildTiming.003": "<b>Phases:</b> {phases_map}",
  "appjs.buildTiming.004": "<b>Pillars:</b> {W_decades}",
  "appjs.buildTiming.005": "<b>Roles:</b> {gods_map}",
  "appjs.buildTiming.006": "<span class=\"keepzh\">{gzc_d}</span> {STEM_YANG_d} {EL_EN_STEM_EL} over {ZODIAC_BR_ANIMAL} ({EL_EN_BR_EL})",
  "appjs.buildTiming.007": "Decade strip",
  "appjs.buildTiming.008": "In the {cur_gz} decade ({cur_ages}, {cur_phase}) — {nxt_shifts}",
  "appjs.buildTiming.009": "shifts to {nxt_gz} ({nxt_phase}) at age {String_nxt}.",
  "appjs.buildTiming.010": "the last charted decade.",
  "appjs.buildTiming.011": "Before the first decade — {W_decades}",
  "appjs.buildTiming.012": "{W_decades} begins at age {String_W}.",
  "appjs.buildTiming.013": "Luck cycle",
  "appjs.buildTiming.014": "Starts at age",
  "appjs.buildTiming.015": "<b>Life arc:</b> {W_arc}",
  "appjs.buildTiming.016": "<b>Peach blossom:</b> {W_taohua_branch} — {W_taohua_type}{W_taohua}",
  "appjs.buildTiming.017": "(in the {W_taohua} pillar)",
  "appjs.buildTiming.018": "{GRP_THEME_pair} with {GRP_THEME_pair_2}",
  "appjs.buildTiming.019": "This year, on this decade",
  "appjs.buildTiming.020": "YEAR {state_year}",
  "appjs.buildTiming.021": "annual transit",
  "appjs.buildTiming.022": "on the {L_gz} decade · ages {L_ages} · {L_stem_god}/{L_branch_god}",
  "appjs.buildTiming.023": "{L_gz} {theme_gYr} on top.",
  "appjs.buildTiming.024": "This decade {gDec_gDec} {theme_gDec}; this year adds",
  "appjs.buildTiming.025": "doubles down on",
  "appjs.buildTiming.026": "This year brings",
  "appjs.buildTiming.027": "LUCK",
  "appjs.buildTiming.028": "ages {L_ages}",
  "appjs.buildTiming.029": "YEAR",
  "appjs.buildTiming.030": "The two cards are the energies currently overlaid on the birth chart — the active 10-year luck pillar and this year's pillar — labelled with their ten gods relative to this Day Master.",
  "appjs.buildTiming.031": "<em class=\"rnow\">▲ now</em>",
  "appjs.buildTiming.032": "Monthly rhythm",
  "appjs.buildTiming.033": "Good months: {ranges_good} ({gel}). Pace {ranges_bad}.",
  "appjs.buildTiming.034": "No month carries your medicine — pace the whole year evenly.",
  "appjs.buildTiming.035": "Each solar month carries a branch and its element. Months whose element is your medicine are marked good; months carrying a 忌神 element are marked to pace. The rhythm is the same every year — the 流年 table says which years lift or lower it.",
  "appjs.buildCompass.001": "Eight House 3×3 grid",
  "appjs.buildCompass.002": "Face <b>{dirOf}</b> (Vitality) for bed and desk; keep long sitting out of <b>{dirOf_2}</b> (Severed Fate).",
  "appjs.buildCompass.004": "<b>Two layers:</b> 八宅 grades ORIENTATION — where to face and head long-stay activities; 用神 grades ELEMENT CONTENT — what colours, materials and fields feed the chart. A green direction whose element is unfavourable is still a good direction to FACE — furnish it in the 用神 palette. 命卦 comes from the birth year alone; the 用神 layer is the personal one.",
  "appjs.buildCompass.005": "Favourable {elbs_fav} · avoid {elbs_unf} · colours <b>{cols_join}</b>",
  "appjs.buildCompass.006": "<b>Medicine, ranked:</b> {c_medicine_rank}",
  "appjs.buildCompass.007": "西南·东北 SW/NE",
  "appjs.buildCompass.008": "坤·艮",
  "appjs.buildCompass.009": "east wall, plants and timber, green accents",
  "appjs.buildCompass.010": "south wall, warm light, red/orange accent",
  "appjs.buildCompass.011": "centre or SW/NE, ceramics and stone, yellow/brown tones",
  "appjs.buildCompass.012": "west wall, metal frames and white/gold",
  "appjs.buildCompass.013": "north wall, glass or a water feature, blue/black",
  "appjs.buildCompass.014": "useful element",
  "appjs.buildCompass.015": "trigram palace",
  "appjs.buildCompass.016": "Where the medicine sits",
  "appjs.buildCompass.017": "Add {elw_fav} ({elc_fav}){colEn_in} through lighting or an accent wall; keep {unf_map} ({unf_map_2}) out of your main room.",
  "appjs.buildCompass.018": ", in {colEn},",
  "appjs.buildCompass.022": "<b>Technique:</b> 扶抑 supports a weak chart or restrains a strong one; 调候 corrects its season — for this chart, add {fav_map}, keep {unf_map} light.",
  "appjs.buildCompass.023": "<b>In god vocabulary:</b> your 用神 {fav_map} — those life-areas ARE the medicine.",
  "appjs.buildCompass.024": "{elb_el} arrives as <b>{f_f}</b>",
  "appjs.buildCompass.025": "Placements",
  "appjs.buildCompass.026": "what is placed",
  "appjs.buildCompass.028": "the star or branch that decides it",
  "appjs.buildCompass.029": "Bed head to the <b>{bed_dir}</b> ({bed_star}), desk facing <b>{desk_dir}</b> ({desk_star}).",
  "appjs.buildCompass.030": "Bed head",
  "appjs.buildCompass.031": "Desk",
  "appjs.buildCompass.033": "Long-stay items follow the 八宅 stars of your 命卦: 天醫 for the bed, 生氣 for desk and door, 延年 for the couples' bed, 伏位 for a quiet room. The three corners are personal 神煞 — 文昌 by day stem, 桃花 and 驛馬 by the year-branch trine — mapped to their palace.",
  "appjs.buildCompass.034": "A direction is where the head or face points; when the room cannot allow the first choice, take the next favourable star, never an unfavourable one.",
  "appjs.buildCompass.035": "{AF_year} afflictions",
  "appjs.buildCompass.036": "Grand Duke",
  "appjs.buildCompass.037": "Year Breaker",
  "appjs.buildCompass.038": "Three Killings",
  "appjs.buildCompass.039": "None of this year's afflictions sits on your four favourable sectors.",
  "appjs.buildCompass.043": "<b>Grand Duke</b> — {AF_taisui_rule}",
  "appjs.buildCompass.044": "<b>Year Breaker</b> — {AF_suipo_rule}",
  "appjs.buildCompass.045": "<b>Three Killings</b> — {AF_sansha_rule}",
  "appjs.buildCompass.046": "{h_affliction} on your {h_star} ({h_dir}): {h_note}.",
  "appjs.buildCompass.047": "<b>Year Punishment</b>: {AF_suixing_rule}",
  "appjs.buildCompass.048": "Year Punishment",
  "appjs.pRelations.001": "<b>{x_a}</b> and <b>{x_b}</b>: {x_note} ({x_kind})",
  "appjs.pRelations.002": "No strong pulls between your pillars.",
  "appjs.pBudget.001": "<span class=\"rp-tag\">helps you most</span>",
  "appjs.pBudget.002": "Heavier than {st_n} in 100 charts",
  "appjs.pBudget.003": "Lighter than {st_n} in 100 charts",
  "appjs.pBudget.004": "most useful",
  "appjs.pBalance.001": "{EL_EN_top} leads your chart at {top_share}%, heavier than {st_n} in 100 charts.",
  "appjs.pBalance.002": "{EL_EN_top} leads your chart at {top_share}%, lighter than {st_n} in 100 charts.",
  "appjs.pBalance.003": "{EL_EN_top} leads your chart at {top_share}%.",
  "appjs.pBalance.004": "{EL_EN_H} is what helps you most, and {Y_y} reads as a {Y_word}.",
  "appjs.pBalance.005": "{EL_EN_H} is what helps you most.",
  "appjs.pVault.001": "{ZODIAC_BR_ANIMAL}, the {EL_EN_el} store",
  "appjs.pVault.002": "not in your chart",
  "appjs.pVault.003": "{ZODIAC_BR_ANIMAL} years open it",
  "appjs.pWeather.001": "Your luck decades",
  "appjs.pWeather.002": "<em class=\"rp-dnow\">now</em>",
  "appjs.pWeather.003": "<b>Next turn:</b> {nx_word}, from age {String_nx}.",
  "appjs.pRoom.001": "Room plan with north at the top: {Object_entries}",
  "appjs.pRoom.003": "{l_join} in the {d}",
  "appjs.pSlimGrid.001": "Top: the role each stem plays for you. Bottom: the stems hidden in each branch.",
  "appjs.pSlimGrid.002": "day (you)",
  "appjs.pSlimGrid.003": "Day Master",
  "appjs.pChapter.001": "The classical name for this: {tech}.",
  "appjs.pChapter.002": "<a href=\"/learn/{img}\">Learn more about {what}</a>",
  "appjs.pStory.001": "<span class=\"vh\">Evidence </span>{num_e}",
  "appjs.pStory.002": "Close evidence",
  "appjs.pStory.003": "Back to the text",
  "appjs.pStory.004": "<b>The classical chart.</b> {CHART_CAP_id}",
  "appjs.zhKey.001": "<b>Key:</b> {pairs_map}",
  "appjs.rdFig.001": "how to read this",
  "appjs.bazhaiCompass.001": "Eight directions, north at the top: {rows_map}",
  "appjs.dailyFig.002": "Best day this month for {B_for}: {B_date} {B_gz} ({B_officer} day).",
  "appjs.dailyFig.003": "No clear best day this month.",
  "appjs.dailyFig.004": "Avoid {W_avoid} on {W_date} {W_gz} — {W_why}.",
  "appjs.dailyFig.005": "Daily fortune, next 30 days",
  "appjs.dailyFig.006": "good days",
  "appjs.dailyFig.007": "days with a caution",
  "appjs.dailyFig.008": "<b>Columns:</b> <span class=\"keepzh\">日期</span> date · <span class=\"keepzh\">日柱</span> day pillar (with its day officer) · <span class=\"keepzh\">十神</span> the roles the day brings you · <span class=\"keepzh\">五行</span> the day's element (<span class=\"keepzh\">用</span> useful to you, <span class=\"keepzh\">忌</span> to avoid) · {actZh_map}",
  "appjs.dailyFig.009": "<b>Day officers:</b> {officers_map}",
  "appjs.dailyFig.010": "<b>◉ good · ⚠ avoid · · neutral</b> — per activity, hover a cell for the deciding rule.",
  "appjs.dailyFig.011": "<b>Twelve day officers</b> Completion, Open and Settle are good for most acts; Remove suits treatment; Close and Danger hold back travel and moving; Break (and any day that clashes the month) is avoided for everything.",
  "appjs.dailyFig.012": "<b>Your branches</b> a day branch that clashes your day branch ({elc_c}) or year branch ({elc_c_2}) is avoided for marriage, moving and launches; a Six Combination with your day branch favours marriage and signing; a Harm holds back medical.",
  "appjs.dailyFig.013": "<b>Element of the day</b> a day stem carrying your primary useful god favours launches and signing; one carrying your chief avoided element is avoided for banking and launches.",
  "appjs.dailyFig.014": "<b>Tags:</b> {tags_map}",
  "appjs.tenGodsWheel.003": "Peers",
  "appjs.tenGodsWheel.004": "Output",
  "appjs.tenGodsWheel.005": "Wealth",
  "appjs.gejuPlain.001": "<b>Chart structure (格局)</b> {g_replace}",
  "appjs.gejuPlain.002": "<b>Chart structure (格局).</b> Your month branch (月令) is {br}, and its main stem (本气) is {st}, {god}.",
  "appjs.gejuPlain.003": "{tou} also shows among your visible stems (透干), so the chart works as a {god} structure ({tou_2}).",
  "appjs.gejuPlain.004": "None of the month's hidden stems shows among your visible stems (透干), so the chart works from that ruling stem (司令), with the visible stems as the actors.",
  "appjs.elementWheel.001": ", your day master",
  "appjs.eflowsList.001": "How every other element relates to\n      YOUR Day Master {elb_er} — the same five roles the ten gods (十神 tab) are built from:",
  "appjs.eflowsList.002": "<span class=\"sub\">(this share is the Day Master's own element — as ten-god 比肩/劫財 peers the chart counts 0%)</span>",
  "appjs.strengthGauge.001": "strength {st_verdict} score {st_score}",
  "appjs.strengthGauge.002": "身弱 weak",
  "appjs.strengthGauge.003": "身強 strong",
  "appjs.strengthGauge.004": "{st_verdict} · score {st_score}",
  "appjs.supportDrain.001": "Supporting (same kind) vs draining (other kinds) — the score's own numbers",
  "appjs.supportDrain.002": "<span>← drain</span><span>support →</span>",
  "appjs.supportDrain.003": "<span class=\"sbl\">net balance</span>",
  "appjs.supportDrain.004": "score = in season {pt_season_pts}{pt_season_pts_2}\n      (season) + 2 × (support {pt_support} − drain {pt_drain}) / total {pt_total}\n      + rooting {pt_root_pts}{pt_root_pts_2} (roots) = <b>{c_strength_score}</b> → {c_strength_verdict}",
  "appjs.tiaohouStrip.001": "✓ aligned with the medicine",
  "appjs.tiaohouStrip.002": "not visible",
  "appjs.tiaohouStrip.003": "<b>Seasonal adjustment</b> the {elc_c} month asks for {chips}\n    — <b>{t_verdict}</b> with the support-and-restrain verdict above",
  "appjs.pillarGrid.001": "Read each column top to bottom: the role the stem plays for you, the stem, the branch, the stems hidden in the branch, its life stage and its sound element. Year is on the right, as in a classical chart; your own column, 日, is outlined. Tap any character for its meaning.",
  "appjs.pillarGrid.002": "(clock {clock})",
  "appjs.interactionsSvg.001": "<span><b style=\"color:{it_kind}\">{it_kind_2}</b> {it_pair} · {it_pillars} pillars</span>",
  "appjs.interactionsSvg.002": "branch interactions",
  "appjs.interactionsLine.001": "No 合冲刑害 among your four branches — the pillars sit quietly with each other.",
  "appjs.interactionsLine.002": "{elc_pair} doubles on itself",
  "appjs.interactionsLine.003": "One",
  "appjs.interactionsLine.004": "Two",
  "appjs.interactionsLine.005": "Three",
  "appjs.interactionsLine.006": "Four",
  "appjs.interactionsLine.007": "Five",
  "appjs.interactionsLine.008": "Six",
  "appjs.interactionsLine.009": "{words_n} branch {n_tension}, {clash_one}: {list} — {clash_watch}.",
  "appjs.interactionsLine.010": "one of them a clash",
  "appjs.interactionsLine.011": "none a clash",
  "appjs.interactionsLine.012": "watch the clash",
  "appjs.interactionsLine.013": "quiet friction, not rupture",
  "appjs.ansQ.001": "Why: {name}",
  "appjs.pWhy.001": "Why the chart says this",
  "appjs.pSeal.001": "Your four pillars, year to hour: {PILLAR_KEYS_map}",
  "appjs.sadv.001": "Strategy",
  "appjs.zhNote.001": "The Chinese version of this section is coming soon.",
  "appjs.renderPerson.sec1": "elements",
  "appjs.renderPerson.sec2": "strength",
  "appjs.renderPerson.sec4": "distribution",
  "appjs.renderPerson.sec7": "directions",
  "appjs.renderPerson.sec10": "personality",
  "appjs.renderPerson.sec11": "health",
  "appjs.renderPerson.sec12": "careers",
  "appjs.buildGods.rooted": "rooted",
  "appjs.buildGods.floating": "floating",
  "appjs.buildGods.favourable": "favourable",
  "appjs.buildGods.unfavourable": "unfavourable",
  "appjs.buildCompass.tag": "{h_affliction} on {h_star} {h_dir}"
};
const IS_ZH = !!(window.I18N && window.I18N.reading);
const zhNoteIf = (t) => (IS_ZH && /\b[a-z]{3,}\b/.test(String(t || "").replace(/<[^>]+>/g, "")) ? zhNote() : "");   // the notice stays only where English is left
const zhNote = () => (IS_ZH ? `<p class="zhnote" role="note">${RS("appjs.zhNote.001")}</p>` : "");
const RS = (id, slots) => {
  const z = window.I18N && window.I18N.reading ? window.I18N.reading[id] : undefined;
  const t = z !== undefined ? z : READING_EN[id];
  return slots ? t.replace(/\{([A-Za-z0-9_]+)(?::g)?\}/g, (m, k) => (k in slots ? slots[k] : m)) : t;
};
const $ = (s) => document.querySelector(s);
/* Snapshot mode: /snapshot bakes every API response into window.__BAKED__ so the
   identical page works offline as an email attachment (no server, no fetch). */
const BAKED = window.__BAKED__ || null;
const state = { year: BAKED ? BAKED.year : 2026, period: 8, method: "pie",
                policy: "true_solar",
                person: null, house: null, family: null, assignment: null };

const POS = ["year", "month", "day", "hour"];
const POS_LAB = { year: "YEAR 年", month: "MONTH 月", day: "DAY 日", hour: "HOUR 时" };

/* ---------- Traditional → Simplified for descriptions (names stay 繁體) ---------- */
const T2S_PAIRS =
  "氣气醫医禍祸絕绝遊游東东調调飛飞運运節节沖冲歲岁學学體体筆笔畫画數数宮宫兌兑離离盤盘" +
  "書书擇择評评時时陰阴陽阳貪贪貞贞祿禄輔辅軍军門门龍龙剋克強强對对與与為为後后應应屬属" +
  "顯显凱凯優优趙赵黃黄簡简單单總总滿满執执開开閉闭關关藥药殺杀傷伤財财梟枭納纳當当進进" +
  "錯错雙双靜静動动護护顏颜綠绿紅红藍蓝廚厨廁厕臥卧廳厅羅罗兩两個个這这裡里從从洩泄勢势" +
  "幫帮論论據据見见訣诀經经續续變变讓让選选適适頭头帶带極极過过還还沒没內内發发間间問问" +
  "題题響响環环風风師师傳传統统現现綜综標标準准側侧測测記记計计認认證证誤误說说詳详註注" +
  "釋释義义儀仪" +
  "斷断壞坏謹谨聽听觀观際际團团隊队條条確确實实稱称雜杂濕湿燥燥窮穷寶宝鑑鉴長长" +
  "戀恋貴贵將将華华業业馬马驛驿號号蓋盖脈脉穩稳雞鸡豬猪";
const T2S = {};
for (let i = 0; i < T2S_PAIRS.length; i += 2) T2S[T2S_PAIRS[i]] = T2S_PAIRS[i + 1];
const toSimp = (s) => [...String(s)].map((c) => T2S[c] || c).join("");
/* Everything (names included) renders 简体; only the Names 姓名 tab keeps 繁體,
   because Kangxi stroke analysis is only meaningful on traditional forms. */
const jt = toSimp;
const dn = (n) => n;       // names now pass through; jt() simplifies them
const dnAll = (s) => s;
const LAYER_ZH = { bazhai: "八宅", xuankong: "飞星", yongshen: "用神", bazi: "八字" };
const PALACE_DIR = { 坎: "N", 艮: "NE", 震: "E", 巽: "SE", 離: "S", 坤: "SW", 兌: "W", 乾: "NW" };
const BAZHAI_ORDER = ["生氣", "天醫", "延年", "伏位", "禍害", "六煞", "五鬼", "絕命"];
const BAZHAI_EN = {
  "生氣": [RS("appjs.BAZHAI_EN.生氣.0"), RS("appjs.BAZHAI_EN.生氣.1")],
  "天醫": [RS("appjs.BAZHAI_EN.天醫.0"), RS("appjs.BAZHAI_EN.天醫.1")],
  "延年": [RS("appjs.BAZHAI_EN.延年.0"), RS("appjs.BAZHAI_EN.延年.1")],
  "伏位": [RS("appjs.BAZHAI_EN.伏位.0"), RS("appjs.BAZHAI_EN.伏位.1")],
  "禍害": [RS("appjs.BAZHAI_EN.禍害.0"), RS("appjs.BAZHAI_EN.禍害.1")],
  "六煞": [RS("appjs.BAZHAI_EN.六煞.0"), RS("appjs.BAZHAI_EN.六煞.1")],
  "五鬼": [RS("appjs.BAZHAI_EN.五鬼.0"), RS("appjs.BAZHAI_EN.五鬼.1")],
  "絕命": [RS("appjs.BAZHAI_EN.絕命.0"), RS("appjs.BAZHAI_EN.絕命.1")],
};
const layerZh = (l) => LAYER_ZH[l] || l;

const narrBlock = (i) => !i ? "" : `<div class="section interp">
    <h3>Interpretation <span class="tag">rule-based · auto-generated · no AI</span></h3>
    ${i.paragraphs.map((t) => `<p>${dnAll(t)}</p>`).join("")}</div>`;

/* Reading-tab helpers: narrative paragraphs carry [§N] tags — distribute each
   under its own section instead of one block at the top; every section also
   gets a term-translation legend (the interpretation IS the product). */
function splitNarr(i) {
  const by = {}, rest = [];
  for (const t of (i && i.paragraphs) || []) {
    const m = t.match(/^\[§(\d+)[^\]]*\]\s*/);
    if (m) (by[+m[1]] = by[+m[1]] || []).push(t.slice(m[0].length));
    else rest.push(t);
  }
  return { by, rest };
}
const legendBlock = (pairs) => !pairs ? "" : `<div class="legend">
  <b>Legend</b>${pairs.map(([t, d]) => `<span><b>${t}</b> — ${d}</span>`).join("")}</div>`;
/* the one element icon, site wide: the painted swatch with its character on it (the same disc as the wheel and the character
   cards). Decorative, so the name reaches a screen reader as hidden text; silent when the element's name is printed beside it.
   keepzh + data-notip keep the glossary from expanding the character. Width and height come from --s, so nothing shifts; the 128 px file is the one the wheel and answer cards already
   load, so the icons add no request. */
const eli = (e, { s = 24, silent = false } = {}) => `<span class="eli el-${e} keepzh" data-notip title="${EL_EN[e] || e}" style="--s:${s}px;background-image:url(/static/img/reading/sw/${EL_SLUG[e]}-128.webp)"><b aria-hidden="true">${e}</b>${silent ? "" : `<span class="vh">${EL_EN[e] || e}</span>`}</span>`;
const elis = (a) => (a || []).map((e) => eli(e)).join("");
const sadv = (items, title = RS("appjs.sadv.001")) => !items || !items.length ? "" :
  `<div class="sadv"><b>${title}</b>${items.map((x) => `<div>· ${dnAll(x)}</div>`).join("")}</div>`;

/* strategy report content distributed into its Reading sections */
function stratBlock(n, st) {
  const s = st && st["s" + n];
  if (!s) return "";
  switch (n) {
    case 2: return sadv([s.advice], RS("appjs.stratBlock.001"));
    case 5: return `<div class="cite" style="margin-top:8px">${RS("appjs.stratBlock.002")}</div>
      <div class="mos">${s.rhythm.map((m) => `<span class="mo ${m.cls}">${m.mon} ${m.br}${m.el}</span>`).join("")}</div>`;
    case 8: return `<div class="cite" style="margin-top:8px">${RS("appjs.stratBlock.003", {s_kid: s.kid
        ? RS("appjs.stratBlock.006") : RS("appjs.stratBlock.007"), dnAll_s: dnAll(s.risk)})}</div>
      ${s.evidence.map((e) => `<div class="cite">· ${dnAll(e)}</div>`).join("")}
      <div class="cite">${RS("appjs.stratBlock.004", {s_taohua: s.taohua, s_allies: s.allies.join(", "), s_clash: s.clash})}</div>
      <div class="cite">${RS("appjs.stratBlock.005", {dnAll_s: dnAll(s.el_line)})}</div>
      ${sadv(s.advice)}`;
    case 10: return !s.handle.length ? "" : `<div class="cite" style="margin-top:8px">
        <b>${s.kid ? RS("appjs.stratBlock.008") : RS("appjs.stratBlock.009")}:</b>
        ${s.handle.map(dnAll).join(". ")}.</div>`;
    case 11: return `<div class="cite" style="margin-top:8px">${RS("appjs.stratBlock.010", {s_trigger_years: s.trigger_years.join(", ") || RS("appjs.stratBlock.011"), s_recovery_years: s.recovery_years.join(", ") || "—"})}</div>
      ${sadv(s.advice)}`;
    case 12: return `<div class="sdial"><div class="sdialbar"><div style="width:${s.pct_corp}%"></div></div>
        <div class="sdialcap">${RS("appjs.stratBlock.012", {s_pct_corp: s.pct_corp})}</div></div>
      <div class="cite"><b>${dnAll(s.verdict)}</b></div>
      <div class="cite">${RS("appjs.stratBlock.013", {s_corp_ev: s.corp_ev.join(", ") || "—", s_vent_ev: s.vent_ev.join(", ") || "—"})}</div>
      ${sadv(s.advice)}`;
    case 13: return `<div class="cite" style="margin-top:8px">${RS("appjs.stratBlock.014", {dnAll_s: dnAll(s.wealth_pattern), dnAll_s_2: dnAll(s.wealth_carry)})}</div>
      ${s.act_windows.length ? `<div class="cite">${RS("appjs.stratBlock.015", {s_act_windows: s.act_windows.map((x) => "◉ " + dnAll(x)).join("<br>")})}</div>`
        : `<div class="cite">${RS("appjs.stratBlock.016")}</div>`}
      ${s.cautions.length ? `<div class="cite">${RS("appjs.stratBlock.017", {s_cautions: s.cautions.join(", ")})}</div>` : ""}
      ${s.handoff ? `<div class="cite">${RS("appjs.stratBlock.018", {dnAll_s: dnAll(s.handoff)})}</div>` : ""}
      ${s.exams.length ? `<div class="cite">${RS("appjs.stratBlock.019")}<br>
          ${s.exams.map((r) => `<b>${r.exam} — ${r.year}:</b> ${dnAll(r.note)}`).join("<br>")}</div>` : ""}
      ${sadv(s.wealth_advice.concat(s.advice))}`;
  }
  return "";
}

function controls() {
  for (const id of ["year", "period", "method", "policy"]) {
    $("#" + id).addEventListener("change", (e) => {
      state[id] = id === "year" || id === "period" ? +e.target.value : e.target.value;
      refresh();
    });
  }
  document.querySelectorAll(".tab[data-tab]").forEach((b) =>
    b.addEventListener("click", () => showTab(b.dataset.tab)));
  $("#working-toggle").addEventListener("click", () => {
    const nav = $("#working-nav");
    nav.hidden = !nav.hidden;
    $("#working-toggle").textContent =
      "The Working " + (nav.hidden ? "▾" : "▴");
  });
  if (BAKED) {
    $("#year").value = BAKED.year;
    $("#year").disabled = true;
    $("#year").title = "fixed in this snapshot";
    $("#report-link").hidden = true;
    const sl = $("#snapshot-link");
    if (sl) sl.hidden = true;
    const tl = $("#trace-link");
    if (tl) tl.hidden = true;   // tracing needs the server
  }
}

function showTab(name) {
  document.querySelectorAll(".tab").forEach((b) =>
    b.classList.toggle("active", b.dataset.tab === name));
  document.querySelectorAll(".tabpane").forEach((p) =>
    p.classList.toggle("active", p.id === "tab-" + name));
  const workingTab = document.querySelector(`#working-nav [data-tab="${name}"]`);
  if (workingTab) $("#working-nav").hidden = false;   // opening a classic tab reveals its nav
}

async function api(path, opts) {
  if (BAKED) return bakedApi(path, opts);
  const r = await fetch(path, opts);
  if (!r.ok) throw new Error(path + " → " + r.status);
  return r.json();
}

/* ---------- snapshot (offline) mode ---------- */
function bakedApi(path, opts) {
  if (opts && opts.method === "POST") {
    const body = JSON.parse(opts.body);
    if (path === "/api/score") return jsScore(body);
    if (path === "/api/optimize") return jsOptimize(body);
    if (path === "/api/interpret")
      return BAKED.interpret[`${body.period}|${body.method || "pie"}|${body.policy}`];
    if (path === "/api/evaluate_unit")
      return BAKED.unit[`${jsMountain(body.facing_deg)}|${body.period}`];
  }
  const r = BAKED.get[path];
  if (!r) throw new Error(path + " not baked into this snapshot");
  return r;
}

function jsMountain(deg) {
  return BAKED.MO[Math.floor(((deg + 7.5) % 360) / 15)];
}

/* mirrors engine/optimizer.py score_assignment (lam fixed at 1.0) */
function jsScore(body) {
  const key = body.method === "grid" ? "palace_grid" : "palace_pie";
  const base = BAKED.base[body.policy][body.period];
  const pairs = BAKED.pairs[body.policy];
  const roomsById = {};
  BAKED.rooms.forEach((r) => (roomsById[r.id] = r));
  const scores = [], violations = [];
  let household = 0;
  for (const [rid, names] of Object.entries(body.assignment)) {
    const room = roomsById[rid];
    if (!room) { violations.push(`unknown room ${rid}`); continue; }
    if (!room.sleeping && names.length) violations.push(`${room.label} is not a sleeping room`);
    if (room.capacity && names.length > room.capacity)
      violations.push(`${room.label} over capacity (${names.length}/${room.capacity})`);
    for (const name of names) {
      const s = JSON.parse(JSON.stringify(base[name][room[key]]));
      for (const other of names) {
        if (other === name) continue;
        const pr = pairs[name] && pairs[name][other];
        if (pr) s.breakdown.push(pr);
      }
      s.total = Math.round(s.breakdown.reduce((a, b) => a + b.contribution, 0) * 1000) / 1000;
      s.room = rid; s.room_label = room.label;
      scores.push(s); household += s.total;
    }
  }
  const assigned = Object.values(body.assignment).flat();
  for (const n of BAKED.people)
    if (!assigned.includes(n)) violations.push(`${n} has no room`);
  for (const n of new Set(assigned.filter((x) => assigned.indexOf(x) !== assigned.lastIndexOf(x))))
    violations.push(`${n} assigned to multiple rooms`);
  return { scores, household_total: Math.round(household * 1000) / 1000, violations };
}

/* mirrors engine/optimizer.py optimize */
function jsOptimize(body) {
  const rooms = BAKED.rooms.filter((r) => r.sleeping);
  const ids = rooms.map((r) => r.id);
  const roomsById = {};
  rooms.forEach((r) => (roomsById[r.id] = r));
  const couple = BAKED.master_couple, split = body.allow_master_split;
  const free = BAKED.people.filter((n) => split || !couple.includes(n));
  const cands = [];
  const rec = (i, asg) => {
    if (i === free.length) {
      const assignment = {};
      ids.forEach((r) => (assignment[r] = []));
      if (!split) couple.forEach((n) => assignment["master"].push(n));
      free.forEach((n, j) => assignment[asg[j]].push(n));
      for (const rid of ids)
        if (assignment[rid].length > roomsById[rid].capacity) return;
      const res = jsScore({ ...body, assignment });
      if (res.violations.length) return;
      const clean = {};
      for (const [k, v] of Object.entries(assignment)) if (v.length) clean[k] = v;
      cands.push({ assignment: clean, ...res });
      return;
    }
    for (const rid of ids) { asg.push(rid); rec(i + 1, asg); asg.pop(); }
  };
  rec(0, []);
  cands.sort((a, b) => b.household_total - a.household_total);
  return { evaluated: cands.length, best: cands.slice(0, 3), constraints: {} };
}

async function refresh() {
  const q = `year=${state.year}&period=${state.period}&policy=${state.policy}`;
  [state.family, state.house] = await Promise.all([
    api(`/api/family?${q}`),
    api(`/api/house?year=${state.year}&method=${state.method}`),
  ]);
  // single-period houses (e.g. periods:[9]) — snap the default P8 to what exists
  const pers = Object.keys(state.house.natal || {});
  if (pers.length && !pers.includes(String(state.period))) {
    state.period = +pers[0];
    if ($("#period")) $("#period").value = String(state.period);
  }
  if ($("#period")) [...$("#period").options].forEach(
    (o) => { o.disabled = pers.length > 0 && !pers.includes(o.value); });
  if (!state.assignment) {
    state.assignment = {};
    const h = state.house;
    const def = h.default_assignment || {};
    h.rooms.filter((r) => r.sleeping)
      .forEach((r) => (state.assignment[r.id] = def[r.id] || []));
  }
  if (!BAKED) {
    $("#report-link").href =
      `/report?year=${state.year}&period=${state.period}&policy=${state.policy}`;
    const sl = $("#snapshot-link");
    if (sl) sl.href = `/snapshot?year=${state.year}`;
  }
  $("#house-line").textContent = toSimp(
    `${state.house.house.name} — facing ${state.house.house.facing_deg}° (${state.house.house.facing_mountain}向) · ` +
    `annual center star ${state.house.annual_center} (${state.year})`
    + (BAKED ? ` · offline snapshot ${BAKED.generated}` : ""));
  $("#warnings").textContent = state.house.house.provisional
    ? "⚠ PROVISIONAL: facing degrees, period (8 vs 9) and room tracing await the compass / renovation-date check — see design doc assignment."
    : "";
  await renderForMe();
  await renderOurHome();
  await renderCompare();
  await renderPlanner();
  renderFamily();
  renderHouse();
  await renderAssign();
  renderForecastTab();
  renderDatesTab();
  renderPairTab();
  renderNamesTab();
  renderUnitTab();
  if (state.person) renderPerson(state.person);
}

/* ---------- For Me tab (aspect cards — design doc §3, T5-A band-first) ---- */
const BAND_COL = { strong: "#1a7f37", good: "#2c8c7d", fair: "#b58900",
                   weak: "#d2691e", poor: "#b03a2e" };
const BAND_EN = { strong: RS("appjs.LEGENDS.2.01.term"), good: "Good", fair: "Fair", weak: RS("appjs.LEGENDS.2.02.term"), poor: "Poor" };

function aspectCard(c) {
  const col = BAND_COL[c.band] || "var(--muted)";
  const acts = (c.actions || []).map((a) =>
    `<div class="act"><span class="actchip p${a.priority}">${jt(a.category)} P${a.priority}</span>${jt(a.action)}
      <div class="cite">↳ ${jt(a.trigger)} · ${jt(a.source_ref)}</div></div>`).join("");
  const audit = (c.audit || []).map((a) =>
    `<tr><td>${a.rule_id}</td><td>${a.sub_score ?? "—"}</td><td>${a.weight || ""}</td>
       <td>${jt(a.explanation)}<div class="cite">${jt(a.source_ref)}</div></td></tr>`).join("");
  const sup = (c.superseded || []).map((a) =>
    `<li>${jt(a.action)} — <i>${jt(a.superseded_by ? "superseded by: " + a.superseded_by
                                                   : a.deferred || "")}</i></li>`).join("");
  return `<div class="acard" style="border-top:3px solid ${col}">
    <div class="acard-head"><span class="aband" style="color:${col}">${c.band_zh} ${BAND_EN[c.band]}</span>
      <span class="ascore">${c.score}/100</span></div>
    <h4>${c.subject && ["room", "date", "year"].includes(c.subject.type)
         ? jt(c.subject.label) : jt(c.aspect_zh) + " · " + c.aspect}</h4>
    <p class="ameaning">${jt(c.meaning)}</p>
    <p class="adriver">◉ ${jt(c.driver)}</p>${acts}
    <details class="awork"><summary>▾ Show the classical working</summary>
      <table class="atable"><tr><th>rule</th><th>sub</th><th>wt</th><th>why</th></tr>${audit}</table>
      ${sup ? `<div class="cite">Superseded / deferred actions:</div><ul class="cite">${sup}</ul>` : ""}
      <div class="cite">${jt(c.source_ref)}</div></details></div>`;
}

/* ---------- extras (battlecard parity: profiles + audit + harmony) -------- */
async function fetchExtras() {
  const key = `${state.year}|${state.method}|${state.policy}`;
  if (state.extrasKey === key) return state.extras;
  try {
    state.extras = await api(`/api/extras?year=${state.year}` +
                             `&method=${state.method}&policy=${state.policy}`);
  } catch (e) { state.extras = null; }
  state.extrasKey = key;
  return state.extras;
}

function profileHtml(p) {
  if (!p) return "";
  const yc = { good: "yg", bad: "yb", watch: "yr", steady: "yn" };
  const years = p.years.map((y) => `<span class="yc ${yc[y.cls] || "yn"}">${y.y}
    ${y.gz}${y.rels.length ? " " + y.rels.join("·") : ""} · 喜${y.good}忌${y.bad}</span>`).join("");
  const rows = [
    ["Temperament", p.axes.join(" · ") || "balanced, no strong tilt"],
    ["Industries", p.industries.fav.map((i) => `${i.en}: ${i.list}`).join("; ")
      + ` <span class="neg">(avoid: ${p.industries.avoid.join(", ")})</span>`],
    ["Organ watch", p.health.join(" · ") || "five elements in workable balance"],
    [RS("appjs.LEGENDS.chart.12.term"), p.shensha.join(" · ") || "—"],
    ["5-year outlook", years],
    ["Study palace", `${p.wenchang.palace}宮 → ${p.wenchang.rooms.join(", ") || "no room"}`],
    ["Helpful people", p.guiren.map((g) =>
      `${g.palace}宮 → ${g.rooms.join(", ") || "no room"}`).join(" · ") || "—"],
  ];
  return `<details class="profile-block"><summary>BaZi profile ·
      kua ${p.gua} · Day Master ${p.day_master}</summary>
    <table class="ptable">${rows.map(([k, v]) =>
      `<tr><th>${k}</th><td>${v}</td></tr>`).join("")}</table></details>`;
}

function harmonyHtml(h) {
  if (!h) return "";
  const names = h.names;
  const cell = {};
  h.pairs.forEach((p) => { cell[p.a + "|" + p.b] = p; cell[p.b + "|" + p.a] = p; });
  const head = `<tr><th></th>${names.slice(1).map((n) => `<th>${n}</th>`).join("")}</tr>`;
  const rows = names.slice(0, -1).map((a, i) =>
    `<tr><th>${a}</th>${names.slice(1).map((b, j) => {
      if (j < i) return "<td></td>";
      const p = cell[a + "|" + b];
      const col = p.score >= 60 ? "#1a7f37" : p.score >= 45 ? "#8a8a8a" : "#b03a2e";
      return `<td><b style="color:${col}">${p.score}</b>
        <span class="drv">${p.band}</span></td>`;
    }).join("")}</tr>`).join("");
  const rough = h.pairs.filter((p) => p.score < 50)
    .sort((x, y) => x.score - y.score)
    .map((p) => `<p class="cite">⚠ <b>${p.a} × ${p.b} (${p.score})</b>:
      ${p.chips.slice(0, 3).join("; ")}</p>`).join("");
  return `<div class="section"><h3>Family harmony
      <span class="tag">day-pillar based · same in every home</span></h3>
    <table class="ptable">${head}${rows}</table>${rough}</div>`;
}

const auditHtml = (audit) => !audit ? "" : `<div class="section">
  <h3>Placement audit
    <span class="tag">missing corners · entry · stove · wet rooms · wealth spots</span></h3>
  <table class="ptable">${audit.map((r) =>
    `<tr><th>${r.zh}</th><td>${r.text}</td></tr>`).join("")}</table></div>`;

function cmpCols(d) {
  return d.columns.map((col) => `<div class="cmp-col">
      <h3>${jt(col.label)}</h3><div class="cmp-head">${jt(col.headline)}</div>
      ${col.boundary && col.boundary.zone !== "正向"
        ? `<div class="baked-note">⚠ ${jt(col.boundary.explanation)}</div>` : ""}
      ${col.cards.map(aspectCard).join("")}</div>`).join("");
}

async function renderForMe() {
  const el = $("#tab-forme");
  let d;
  try {
    if (!BAKED && state.assignment) {       // 2A: live cards follow the Rooms tab
      d = await api("/api/aspects", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ assignment: state.assignment, year: state.year,
                               period: state.period, method: state.method,
                               policy: state.policy }),
      });
    } else {
      d = await api(`/api/aspects?year=${state.year}&period=${state.period}` +
                    `&method=${state.method}&policy=${state.policy}`);
    }
  } catch (e) { el.innerHTML = `<p class="hint">${e.message}</p>`; return; }
  state.aspects = d;
  const extras = await fetchExtras();
  const note = BAKED ? `<div class="baked-note">🧭 Offline snapshot: these cards are baked
    for the recommended room arrangement and do not react to Rooms-tab changes —
    the live site does.</div>` : "";
  const people = Object.entries(d.people).map(([name, cards]) => {
    const room = cards[0].room ? ` <span class="tag">${jt(cards[0].room)}</span>` :
                 ` <span class="tag warn">no room assigned</span>`;
    const prof = extras && extras.profiles ? profileHtml(extras.profiles[name]) : "";
    return `<div class="person-block"><h3>${name}${room}</h3>${prof}
      <div class="agrid">${cards.map(aspectCard).join("")}</div></div>`;
  }).join("");
  const harmony = extras ? harmonyHtml(extras.harmony) : "";
  el.innerHTML = note + people + harmony;
}

/* ---------- Our Home tab (M2 — home cards + room suitability) ------------- */
async function renderOurHome() {
  const el = $("#tab-ourhome");
  const d = state.aspects;
  if (!d) { el.innerHTML = `<p class="hint">aspect cards unavailable</p>`; return; }
  const extras = await fetchExtras();
  let homesCols = "";
  try {
    const cmp = await api(`/api/compare?kind=homes&year=${state.year}` +
                          `&period=${state.period}&method=${state.method}` +
                          `&policy=${state.policy}`);
    homesCols = `<div class="section"><h3>${jt("Homes side-by-side 三宅对比")}
        <span class="tag">${jt("each home on its optimal arrangement")}</span></h3>
      <div class="cmp-cols">${cmpCols(cmp)}</div></div>`;
  } catch (e) { /* compare not available in this snapshot */ }
  const roomCards = Object.entries(d.rooms || {}).map(([name, c]) => aspectCard(c)).join("");
  el.innerHTML = `<div class="section"><h3>${jt("Our Home 我们的家")}
        <span class="tag">${state.period === 9 ? "P9" : "P8"} · ${state.year}</span></h3>
       <div class="agrid">${d.home.map(aspectCard).join("")}</div></div>`
    + (extras ? jt(auditHtml(extras.audit)) : "")
    + `<div class="section"><h3>${jt("Room suitability 各房适配")}
        <span class="tag">${jt(BAKED ? "recommended arrangement" : "current arrangement")}</span></h3>
       <div class="agrid">${roomCards}</div></div>`
    + homesCols;
}

/* ---------- Compare tab (M2 — N subjects, same cards side by side) -------- */
async function renderCompare() {
  const el = $("#tab-compare");
  const kind = state.cmpKind || "homes";
  const person = state.cmpPerson || (state.family ? state.family.people[0].name : "");
  const q = `year=${state.year}&period=${state.period}&method=${state.method}&policy=${state.policy}`;
  let d;
  try {
    d = await api(`/api/compare?kind=${kind}` +
                  (kind === "rooms" ? `&person=${encodeURIComponent(person)}` : "") +
                  `&${q}`);
  } catch (e) { el.innerHTML = `<p class="hint">${e.message}</p>`; return; }
  const people = state.family ? state.family.people.map((p) => p.name) : [];
  const kinds = [["homes", "三宅 Homes"], ["rooms", "一人各房 Rooms"],
                 ["arrangements", "配房方案 Arrangements"]];
  const controls = `<div class="cmp-bar">
    ${kinds.map(([k, l]) => `<button class="cmp-kind ${k === kind ? "on" : ""}"
       data-kind="${k}">${l}</button>`).join("")}
    <select id="cmp-person" ${kind === "rooms" ? "" : "hidden"}>
      ${people.map((n) => `<option ${n === person ? "selected" : ""}>${n}</option>`).join("")}
    </select></div>`;
  const cols = cmpCols(d);
  el.innerHTML = controls + `<div class="cmp-cols">${cols}</div>`;
  el.querySelectorAll(".cmp-kind").forEach((b) =>
    b.addEventListener("click", () => { state.cmpKind = b.dataset.kind; renderCompare(); }));
  const sel = el.querySelector("#cmp-person");
  if (sel) sel.addEventListener("change", (e) => {
    state.cmpPerson = e.target.value; renderCompare();
  });
}

/* ---------- Planner tab (M3 — dates/hours/reno windows as cards) ---------- */
async function renderPlanner() {
  const el = $("#tab-planner");
  const month = state.plannerMonth || new Date().getMonth() + 1;
  let d;
  try {
    d = await api(`/api/planner?year=${state.year}&month=${month}` +
                  `&period=8&method=${state.method}`);
  } catch (e) { el.innerHTML = `<p class="hint">${e.message}</p>`; return; }
  const avoid = d.avoid.length
    ? `<div class="section"><h3>${jt("Avoid 忌用")} <span class="tag warn">${d.avoid.length} day(s)</span></h3>
       ${d.avoid.map((a) => `<p class="cite">✗ <b>${a.date}</b> ${a.day_gz}日 — ${jt(a.why)}</p>`).join("")}</div>`
    : "";
  el.innerHTML = `<div class="cmp-bar"><label>Month 月份
        <select id="pl-month">${Array.from({length: 12}, (_, i) =>
          `<option value="${i + 1}" ${i + 1 === month ? "selected" : ""}>${i + 1}月</option>`).join("")}
       </select></label></div>`
    + `<div class="section"><h3>${jt("修造 Renovation windows")} <span class="tag">${state.year}</span></h3>
       <div class="agrid">${aspectCard(d.reno)}</div></div>`
    + `<div class="section"><h3>${jt(`Best days 吉日 — ${state.year}-${String(month).padStart(2, "0")}`)}</h3>
       <div class="agrid">${d.best.map((c) => `<div>${aspectCard(c)}
         ${c.person_flags.length ? `<div class="cite">${c.person_flags.map((f) =>
             `⚑ ${f.name}: ${jt(f.why)}`).join("<br>")}</div>` : ""}</div>`).join("")}</div></div>`
    + avoid;
  $("#pl-month").addEventListener("change", (e) => {
    state.plannerMonth = +e.target.value; renderPlanner();
  });
}

/* ---------- Family tab ---------- */
function renderFamily() {
  const el = $("#tab-family");
  el.innerHTML = jt(narrBlock(state.family.interpretation) +
    `<div class="cards">` + state.family.people.map((p) => `
    <div class="card" data-name="${p.name}">
      <h3>${dn(p.name)} <span class="sub">${p.sex} · ${p.birth}</span></h3>
      <div class="pillar-chips">${POS.map((k) => `<span>${p.pillars[k]}</span>`).join("")}</div>
      <div>日主 ${p.day_master} · ${p.strength}
        ${p.hour_pillar_differs ? '<span class="tag warn">hour differs clock↔solar</span>' : ""}</div>
      <div style="margin:4px 0">${p.yongshen.favourable.map((e) => `<span class="tag">用神 ${e}</span>`).join("")}
        <span class="tag">colours ${p.yongshen.colours.join("·")}</span></div>
      <div><span class="tag">${p.gua}命 ${p.group}</span></div>
      <div class="sub">best sectors: ${p.top_sectors.map((s) => `${s.direction} (${s.total.toFixed(2)})`).join(", ")}</div>
    </div>`).join("") + `</div>`);
  el.querySelectorAll(".card").forEach((c) =>
    c.addEventListener("click", () => { state.person = c.dataset.name; renderPerson(c.dataset.name); showTab("person"); }));
}

/* ---------- Person tab (baziValidation.docx layout) ---------- */
/* ---------- Chart Card 命卡 (JY-style dense one-glance summary) ----------- */
const EL_COL = { 木: "#1e8e3e", 火: "#c5221f", 土: "#8a6d1f", 金: "#5f6b7a", 水: "#1a56b0" };
/* chart FILLS use EL_COL; coloured TEXT uses EL_TXT, the darkened tokens that pass 4.5:1 */
const EL_TXT = { 木: "#187a35", 火: "#c5221f", 土: "#7a601b", 金: "#8a6500", 水: "#1a56b0" };
/* fit a label inside a node: widest the word may be is 2r - 6 units */
const fitFont = (word, r, max) => Math.max(6.4, Math.min(max, (2 * r - 6) / (String(word).length * 0.58)));
/* a node label, wrapped onto a second line when it is two words, centred and scaled to fit */
function nodeLines(label, x, y, r, maxFs) {
  const w = String(label).split(" ");
  const lines = w.length > 1 ? [w[0], w.slice(1).join(" ")] : w;
  const longest = lines.reduce((a, b) => (a.length >= b.length ? a : b));
  const fs = fitFont(longest, r, maxFs), top = y - (lines.length - 1) * fs * 0.55 + fs * 0.35;
  return lines.map((ln, k) => `<text x="${x}" y="${(top + k * fs * 1.1).toFixed(1)}" text-anchor="middle"
    font-size="${fs.toFixed(1)}" font-weight="700" fill="#fff">${ln}</text>`).join("");
}
const STEM_EL = { 甲: "木", 乙: "木", 丙: "火", 丁: "火", 戊: "土", 己: "土",
                  庚: "金", 辛: "金", 壬: "水", 癸: "水" };
const BR_EL = { 子: "水", 丑: "土", 寅: "木", 卯: "木", 辰: "土", 巳: "火",
                午: "火", 未: "土", 申: "金", 酉: "金", 戌: "土", 亥: "水" };
const GUA_EL = { 坎: "水", 離: "火", 离: "火", 震: "木", 巽: "木", 乾: "金", 兌: "金", 兑: "金", 坤: "土", 艮: "土" };
const BR_ANIMAL = { 子: "鼠", 丑: "牛", 寅: "虎", 卯: "兔", 辰: "龙", 巳: "蛇",
                    午: "马", 未: "羊", 申: "猴", 酉: "鸡", 戌: "狗", 亥: "猪" };

/* personalised 生剋 wheel: node size = element share, gold ring = Day Master,
   green arrows = generating cycle, red = controlling (solid when afflicted) */
/* watercolour discs (owner 2026-10-10): each element circle is its painted swatch, a touch larger than the circle
   so the blot's soft edge shows; the character is white with a dark halo, or ink on the pale Metal wash */
const swatchDisc = (x, y, r, el) => `<image href="/static/img/reading/sw/${EL_SLUG[el]}-128.webp" x="${(x - r * 1.14).toFixed(1)}" y="${(y - r * 1.14).toFixed(1)}" width="${(r * 2.28).toFixed(1)}" height="${(r * 2.28).toFixed(1)}" preserveAspectRatio="none"/>`;
const swatchInk = (el) => el === "金" ? 'fill="#22242a" paint-order="stroke" stroke="rgba(250,247,242,.7)" stroke-width="2.4"'
  : 'fill="#fff" paint-order="stroke" stroke="rgba(28,20,12,.55)" stroke-width="2.6" stroke-linejoin="round"';
/* painted brush arrows (owner pick A, 2026-10-10): a brush shaft, a painted head that keeps its own shape however long
   the arrow is, and ink dabs for the controlling cycle. The masks are luminance images; each arrow is filled in its colour. */
let INK_N = 0;
const inkDefs = () => { const u = "ink" + (++INK_N);
  return [u, ["shaft", "head", "dab"].map((k) => `<mask id="${u}-${k}" maskContentUnits="objectBoundingBox"><image href="/static/img/reading/ink/${k}-mask.png" width="1" height="1" preserveAspectRatio="none"/></mask>`).join("")]; };
function inkArrow(u, x1, y1, x2, y2, col, sw, dotted, op = 1) {
  const L = Math.hypot(x2 - x1, y2 - y1), ang = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI, t = Math.max(3, sw * 2.6);
  const hw = t * 3, hh = hw * 0.77, r = (x, y, w, h, k) => `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" fill="${col}" mask="url(#${u}-${k})"/>`;
  let g = "";
  if (dotted) for (let d = t; d < L - hw * 0.6; d += t * 1.9) g += r(d - t * 0.6, -t * 0.48, t * 1.2, t * 0.96, "dab");
  else g += r(0, -t / 2, Math.max(t, L - hw * 0.55), t, "shaft");
  return `<g transform="translate(${x1.toFixed(1)} ${y1.toFixed(1)}) rotate(${ang.toFixed(1)})" opacity="${op}">${g}${r(L - hw, -hh / 2, hw, hh, "head")}</g>`;
}
function elementWheel(er) {
  const ORDER = ["火", "土", "金", "水", "木"];
  const cx = 170, cy = 170, R = 115;
  const pos = {};
  ORDER.forEach((el, i) => {
    const a = (-90 + i * 72) * Math.PI / 180;
    pos[el] = [cx + R * Math.cos(a), cy + R * Math.sin(a)];
  });
  const rOf = el => 17 + Math.min(er.share[el] || 0, 40) * 0.42;
  const seg = (a, b) => {
    const [x1, y1] = pos[a], [x2, y2] = pos[b];
    const d = Math.hypot(x2 - x1, y2 - y1), ux = (x2 - x1) / d, uy = (y2 - y1) / d;
    return [x1 + ux * (rOf(a) + 3), y1 + uy * (rOf(a) + 3),
            x2 - ux * (rOf(b) + 8), y2 - uy * (rOf(b) + 8)];
  };
  const SHENG_P = [["木", "火"], ["火", "土"], ["土", "金"], ["金", "水"], ["水", "木"]];
  const KE_P = [["木", "土"], ["土", "水"], ["水", "火"], ["火", "金"], ["金", "木"]];
  const aff = new Set((er.afflictions || []).map(p => p.join()));
  const [u, defs] = inkDefs();
  let s = `<svg viewBox="0 0 340 350" class="ewheel"><defs>${defs}</defs>`;
  KE_P.forEach(([a, b]) => {
    const [x1, y1, x2, y2] = seg(a, b), bad = aff.has(a + "," + b);
    s += inkArrow(u, x1, y1, x2, y2, bad ? "#b03a2e" : "#d5b3b0", bad ? 3 : 1.3, !bad);
  });
  SHENG_P.forEach(([a, b]) => {
    const [x1, y1, x2, y2] = seg(a, b);
    s += inkArrow(u, x1, y1, x2, y2, "#7aa87f", Math.max(1.2, Math.min(4, (er.share[a] || 0) / 9)), false, (er.share[a] || 0) < 6 ? 0.35 : 0.9);
  });
  ORDER.forEach(el => {
    const [x, y] = pos[el], r = rOf(el);
    s += swatchDisc(x, y, r, el);
    if (el === er.dm) s += `<circle cx="${x}" cy="${y}" r="${r + 3.5}" fill="none"
      stroke="var(--gold)" stroke-width="2.5"/>`;
    const fs = Math.max(11, Math.min(22, r * 0.62));
    s += `<title>${EL_EN[el]} ${er.share[el]}%${el === er.dm ? RS("appjs.elementWheel.001") : ""}</title>
      <text x="${x}" y="${y + fs * 0.35}" text-anchor="middle" font-size="${fs.toFixed(1)}"
      font-weight="700" ${swatchInk(el)}>${el}</text>
      <text x="${x}" y="${y + r + 13}" text-anchor="middle" font-size="10.5"
      paint-order="stroke" stroke="#faf7f2" stroke-width="3" stroke-linejoin="round" fill="#6b6357">${er.share[el]}%${el === er.dm ? " 日主" : ""}</text>`;
  });
  return s + "</svg>";
}

/* 十神对照 wheel: 日元 centre, five god-groups in the 生剋 pentagon (each
   coloured by ITS element for this chart), yin/yang god pairs as satellites */
const WX_S = {木:"火",火:"土",土:"金",金:"水",水:"木"};
const WX_K = {木:"土",土:"水",水:"火",火:"金",金:"木"};
const WX_IS = {火:"木",土:"火",金:"土",水:"金",木:"水"};
const WX_IK = {土:"木",水:"土",火:"水",金:"火",木:"金"};
/* the element (→ colour) each ten god carries for THIS Day Master */
function godEl(dm, god) {
  const e = STEM_EL[dm];
  if (god === "比肩" || god === "劫財" || god === "劫财") return e;
  if (god === "食神" || god === "傷官" || god === "伤官") return WX_S[e];
  if (god === "正財" || god === "偏財" || god === "正财" || god === "偏财") return WX_K[e];
  if (god === "正官" || god === "七殺" || god === "七杀") return WX_IK[e];
  return WX_IS[e];                                   // 正印 / 偏印
}

/* two sides of each god (汇林文化 十神双面性, condensed + translated) */
const TG_SIDES = {
  "正印": ["broad learning, kindness, quiet support 学识渊博·仁慈包容·精神支持",
           "over-reliance, idealism, indecision 过度依赖·理想主义·缺决断"],
  "偏印": ["deep insight in niche fields, original self-taught skill 小众洞察·深度创新",
           "solitary, suspicious, keeps people at arm's length 孤僻多疑·疏离人际"],
  "正官": ["responsibility, order, stable social standing 责任感强·守序重诺·地位稳",
           "conservatism, rule-bound pressure and anxiety 循规保守·压力焦虑"],
  "七殺": ["leadership in adversity, execution, pioneering 逆境显领袖·执行力强",
           "impulsiveness; health and legal risks 冲动暴力·易招风险"],
  "比肩": ["confident, loyal, natural team player 自信独立·重义善团队",
           "stubborn over spoils, self-centred splits 固执争利·自我中心"],
  "劫財": ["strong social drive, dares to take risks 社交力强·敢于冒险",
           "impulsive losses, easily talked into traps 冲动失财·轻信陷骗局"],
  "食神": ["overflowing talent, easy-going, deep bond with children 才华横溢·豁达乐天",
           "comfort-seeking, weak follow-through, indulgence 贪图安逸·行动力弱"],
  "傷官": ["innovation, eloquence, artistic force 创新突破·口才卓越",
           "rebellious, attracts resentment, marriage friction 叛逆招怨·个性冲突"],
  "正財": ["diligence, steady income, loyalty 勤俭持家·收入稳定·婚姻忠诚",
           "stingy, conservative, material over spirit 吝啬保守·重物轻神"],
  "偏財": ["keen money sense, generosity, seizes windfalls 财运敏锐·慷慨善机遇",
           "extravagance, tangled romantic affairs 挥霍无度·情感纠纷"],
};
const TG_CANON = {"七杀": "七殺", "劫财": "劫財", "伤官": "傷官",
                  "正财": "正財", "偏财": "偏財"};
const tgCanon = g => TG_CANON[g] || g;
const STEM_YANG = {甲: 1, 乙: 0, 丙: 1, 丁: 0, 戊: 1, 己: 0, 庚: 1, 辛: 0, 壬: 1, 癸: 0};
function godOfStem(dm, st) {
  const e1 = STEM_EL[dm], e2 = STEM_EL[st];
  const same = STEM_YANG[dm] === STEM_YANG[st];
  if (e2 === e1) return same ? "比肩" : "劫財";
  if (e2 === WX_S[e1]) return same ? "食神" : "傷官";
  if (e2 === WX_K[e1]) return same ? "偏財" : "正財";
  if (e2 === WX_IK[e1]) return same ? "七殺" : "正官";
  return same ? "偏印" : "正印";
}

function tenGodsWheel(c, opts = {}) {
  const pct = c.tengods_pct || {};
  const p = keys => { for (const k of keys) if (pct[k] != null) return pct[k]; return 0; };
  const dmEl = STEM_EL[c.day_master];
  const S = WX_S, K = WX_K, invS = WX_IS, invK = WX_IK;
  const GROUPS = [
    {zh:"官殺", en:RS("appjs.buildElements.006"), el:invK[dmEl], gods:[["正官"],["七殺","七杀"]], lab:["正官","七殺"]},
    {zh:"印星", en:RS("appjs.buildElements.007"), el:invS[dmEl], gods:[["正印"],["偏印"]], lab:["正印","偏印"]},
    {zh:"比劫", en:RS("appjs.tenGodsWheel.003"), el:dmEl, gods:[["比肩"],["劫財","劫财"]], lab:["比肩","劫財"]},
    {zh:"食傷", en:RS("appjs.tenGodsWheel.004"), el:S[dmEl], gods:[["食神"],["傷官","伤官"]], lab:["食神","傷官"]},
    {zh:"財星", en:RS("appjs.tenGodsWheel.005"), el:K[dmEl], gods:[["正財","正财"],["偏財","偏财"]], lab:["正財","偏財"]},
  ];
  const cx = 170, cy = 170, R1 = 86, R2 = 132;
  GROUPS.forEach((g, i) => {
    g.a = (-90 + i * 72) * Math.PI / 180;
    g.x = cx + R1 * Math.cos(g.a); g.y = cy + R1 * Math.sin(g.a);
    g.sum = Math.round((p(g.gods[0]) + p(g.gods[1])) * 10) / 10;
    g.r = 22 + Math.min(g.sum, 45) * 0.26;
    g.sat = g.gods.map((keys, j) => {
      const a2 = g.a + (j ? 1 : -1) * 0.42;
      const v = p(keys);
      return {x: cx + R2 * Math.cos(a2), y: cy + R2 * Math.sin(a2),
              v, r: 19 + Math.min(v, 35) * 0.18, lab: g.lab[j], en: godEn(c, g.lab[j])};
    });
  });
  const seg = (x1, y1, r1, x2, y2, r2) => {
    const d = Math.hypot(x2 - x1, y2 - y1) || 1, ux = (x2 - x1) / d, uy = (y2 - y1) / d;
    return [x1 + ux * (r1 + 3), y1 + uy * (r1 + 3), x2 - ux * (r2 + 7), y2 - uy * (r2 + 7)];
  };
  const G = i => GROUPS[i];
  const SHENGI = [[2, 3], [3, 4], [4, 0], [0, 1], [1, 2]];   // 比劫→食傷→財→官殺→印→比劫
  const inkD = inkDefs(), u = inkD[0];
  const KEI = [[2, 4], [3, 0], [4, 1], [0, 2], [1, 3]];      // 剋 star
  let s = `<svg viewBox="${opts.groupsOnly ? "45 45 250 265" : "0 0 340 345"}" class="ewheel tgwheel${opts.groupsOnly ? " tgwheel-groups" : ""}${opts.zh ? " keepzh" : ""}"${opts.zh ? ' data-notip role="img" aria-label="' + GROUPS.map((g) => `${g.en} (${g.zh}) ${g.sum}%`).join(", ") + '"' : ""}><defs>${inkD[1]}</defs>`;
  if (!opts.groupsOnly) GROUPS.forEach(g => g.sat.forEach(t => {   // connectors first
    s += `<line x1="${g.x}" y1="${g.y}" x2="${t.x}" y2="${t.y}"
      stroke="#cbc2b4" stroke-width="1" stroke-dasharray="2 3"/>`;
  }));
  KEI.forEach(([a, b]) => {
    const [x1, y1, x2, y2] = seg(G(a).x, G(a).y, G(a).r, G(b).x, G(b).y, G(b).r);
    s += inkArrow(u, x1, y1, x2, y2, "#d5b3b0", 1.3, true);
  });
  SHENGI.forEach(([a, b]) => {
    const [x1, y1, x2, y2] = seg(G(a).x, G(a).y, G(a).r, G(b).x, G(b).y, G(b).r);
    s += inkArrow(u, x1, y1, x2, y2, "#7aa87f", Math.max(1.2, Math.min(4, G(a).sum / 10)), false, G(a).sum < 5 ? 0.35 : 0.85);
  });
  s += `<circle cx="${cx}" cy="${cy}" r="20" fill="${EL_COL[dmEl]}"/>
    <circle cx="${cx}" cy="${cy}" r="23.5" fill="none" stroke="var(--gold)" stroke-width="2.5"/>
    <text x="${cx}" y="${cy + 1}" text-anchor="middle" font-size="13" font-weight="700"
      fill="#fff">${c.day_master}</text>
    <text x="${cx}" y="${cy + 13}" text-anchor="middle" font-size="8.5" fill="#fff">日元</text>`;
  GROUPS.forEach(g => {
    s += `<g><title>${g.en} ${g.sum}% (${g.zh})</title>
      ${opts.zh ? swatchDisc(g.x, g.y, g.r, g.el) : `<circle cx="${g.x}" cy="${g.y}" r="${g.r}" fill="${EL_COL[g.el]}" opacity=".92"/>`}
      ${opts.zh ? `<text x="${g.x}" y="${g.y + 5.5}" text-anchor="middle" font-size="${Math.min(16, g.r * 0.62).toFixed(1)}" font-weight="700" ${swatchInk(g.el)} font-family="Noto Serif SC, serif">${g.zh}</text>` : nodeLines(g.en, g.x, g.y, g.r, 10.5)}</g>
      <text x="${g.x}" y="${g.y + g.r + 11}" text-anchor="middle" font-size="9.5"
        paint-order="stroke" stroke="#faf7f2" stroke-width="3" stroke-linejoin="round" fill="#6b6357">${g.sum}%</text>`;
    if (!opts.groupsOnly) g.sat.forEach(t => {
      s += `<g><title>${t.en} ${t.v}% (${t.lab})</title>
      <circle cx="${t.x}" cy="${t.y}" r="${t.r}" fill="${EL_COL[g.el]}"
        opacity="${t.v < 5 ? 0.35 : 0.68}"/>
      ${nodeLines(t.en, t.x, t.y, t.r, 8.5)}</g>
      <text x="${t.x}" y="${t.y + t.r + 10}" text-anchor="middle" font-size="8.5"
        paint-order="stroke" stroke="#faf7f2" stroke-width="3" stroke-linejoin="round" fill="#6b6357">${t.v}%</text>`;
    });
  });
  return s + "</svg>";
}

const LEGENDS = {
  chart: [
    [RS("appjs.LEGENDS.chart.01.term"), RS("appjs.LEGENDS.chart.01.gloss")],
    [RS("appjs.LEGENDS.chart.02.term"), RS("appjs.LEGENDS.chart.02.gloss")],
    [RS("appjs.LEGENDS.chart.03.term"), RS("appjs.LEGENDS.chart.03.gloss")],
    [RS("appjs.LEGENDS.chart.04.term"), RS("appjs.LEGENDS.chart.04.gloss")],
    [RS("appjs.LEGENDS.chart.05.term"), RS("appjs.LEGENDS.chart.05.gloss")],
    [RS("appjs.LEGENDS.chart.06.term"), RS("appjs.LEGENDS.chart.06.gloss")],
    [RS("appjs.LEGENDS.chart.07.term"), RS("appjs.LEGENDS.chart.07.gloss")],
    [RS("appjs.LEGENDS.chart.08.term"), RS("appjs.LEGENDS.chart.08.gloss")],
    [RS("appjs.LEGENDS.chart.09.term"), RS("appjs.LEGENDS.chart.09.gloss")],
    [RS("appjs.LEGENDS.chart.10.term"), RS("appjs.LEGENDS.chart.10.gloss")],
    [RS("appjs.LEGENDS.chart.11.term"), RS("appjs.LEGENDS.chart.11.gloss")],
    [RS("appjs.LEGENDS.chart.12.term"), RS("appjs.LEGENDS.chart.12.gloss")],
    [RS("appjs.LEGENDS.chart.13.term"), RS("appjs.LEGENDS.chart.13.gloss")],
    [RS("appjs.LEGENDS.chart.14.term"), RS("appjs.LEGENDS.chart.14.gloss")],
    [RS("appjs.CHAPTERS.timing.tech"), RS("appjs.LEGENDS.chart.15.gloss")],
  ],
  1: [[RS("appjs.LEGENDS.1.01.term"), RS("appjs.LEGENDS.1.01.gloss")],
    [RS("appjs.LEGENDS.1.02.term"), RS("appjs.LEGENDS.1.02.gloss")],
    [RS("appjs.LEGENDS.1.03.term"), RS("appjs.LEGENDS.1.03.gloss")],
    [RS("appjs.LEGENDS.1.04.term"), RS("appjs.LEGENDS.1.04.gloss")],
    [RS("appjs.LEGENDS.1.05.term"), RS("appjs.LEGENDS.1.05.gloss")],
    [RS("appjs.LEGENDS.1.06.term"), RS("appjs.LEGENDS.1.06.gloss")],
    [RS("appjs.LEGENDS.1.07.term"), RS("appjs.LEGENDS.1.07.gloss")]],
  2: [[RS("appjs.LEGENDS.2.01.term"), RS("appjs.LEGENDS.2.01.gloss")],
    [RS("appjs.LEGENDS.2.02.term"), RS("appjs.LEGENDS.2.02.gloss")],
    [RS("appjs.LEGENDS.2.03.term"), RS("appjs.LEGENDS.2.03.gloss")],
    [RS("appjs.LEGENDS.2.04.term"), RS("appjs.LEGENDS.2.04.gloss")]],
  3: [[RS("appjs.LEGENDS.3.01.term"), RS("appjs.LEGENDS.3.01.gloss")],
    [RS("appjs.LEGENDS.3.02.term"), RS("appjs.LEGENDS.3.02.gloss")],
    [RS("appjs.LEGENDS.3.03.term"), RS("appjs.LEGENDS.3.03.gloss")]],
  4: [[RS("appjs.LEGENDS.4.01.term"), RS("appjs.LEGENDS.4.01.gloss")],
    ["%", RS("appjs.LEGENDS.4.02.gloss")],
    [RS("appjs.LEGENDS.4.03.term"), RS("appjs.LEGENDS.4.03.gloss")],
    [RS("appjs.LEGENDS.4.04.term"), RS("appjs.LEGENDS.4.04.gloss")],
    [RS("appjs.LEGENDS.4.05.term"), RS("appjs.LEGENDS.4.05.gloss")],
    [RS("appjs.LEGENDS.4.06.term"), RS("appjs.LEGENDS.4.06.gloss")],
    [RS("appjs.LEGENDS.4.07.term"), RS("appjs.LEGENDS.4.07.gloss")],
    [RS("appjs.LEGENDS.4.08.term"), RS("appjs.LEGENDS.4.08.gloss")]],
  5: [[RS("appjs.LEGENDS.5.01.term"), RS("appjs.LEGENDS.5.01.gloss")],
    [RS("appjs.LEGENDS.5.02.term"), RS("appjs.LEGENDS.5.02.gloss")],
    [RS("appjs.LEGENDS.5.03.term"), RS("appjs.LEGENDS.5.03.gloss")],
    [RS("appjs.LEGENDS.5.04.term"), RS("appjs.LEGENDS.5.04.gloss")]],
  6: [[RS("appjs.CHAPTERS.timing.tech"), RS("appjs.LEGENDS.6.01.gloss")],
    [RS("appjs.LEGENDS.6.02.term"), RS("appjs.LEGENDS.6.02.gloss")],
    [RS("appjs.LEGENDS.6.03.term"), RS("appjs.LEGENDS.6.03.gloss")],
    [RS("appjs.LEGENDS.6.04.term"), RS("appjs.LEGENDS.6.04.gloss")]],
  7: [[RS("appjs.LEGENDS.7.01.term"), RS("appjs.LEGENDS.7.01.gloss")],
    [RS("appjs.LEGENDS.7.02.term"), RS("appjs.LEGENDS.7.02.gloss")],
    [RS("appjs.LEGENDS.7.03.term"), RS("appjs.LEGENDS.7.03.gloss")]],
  8: [[RS("appjs.LEGENDS.8.01.term"), RS("appjs.LEGENDS.8.01.gloss")],
    ["≥70", RS("appjs.LEGENDS.8.02.gloss")], ["<45", RS("appjs.LEGENDS.8.03.gloss")],
    [RS("appjs.LEGENDS.8.04.term"), RS("appjs.LEGENDS.8.04.gloss")],
    [RS("appjs.LEGENDS.8.05.term"), RS("appjs.LEGENDS.8.05.gloss")],
    [RS("appjs.LEGENDS.8.06.term"), RS("appjs.LEGENDS.8.06.gloss")]],
  9: [[RS("appjs.LEGENDS.chart.12.term"), RS("appjs.LEGENDS.9.01.gloss")],
    [RS("appjs.LEGENDS.9.02.term"), RS("appjs.LEGENDS.9.02.gloss")]],
  10: [[RS("appjs.LEGENDS.10.01.term"), RS("appjs.LEGENDS.10.01.gloss")],
    [RS("appjs.LEGENDS.10.02.term"), RS("appjs.LEGENDS.10.02.gloss")]],
  11: [[RS("appjs.LEGENDS.11.01.term"), RS("appjs.LEGENDS.11.01.gloss")],
    [RS("appjs.LEGENDS.11.02.term"), RS("appjs.LEGENDS.11.02.gloss")]],
  12: [[RS("appjs.LEGENDS.12.01.term"), RS("appjs.LEGENDS.12.01.gloss")],
    [RS("appjs.LEGENDS.12.02.term"), RS("appjs.LEGENDS.12.02.gloss")]],
  13: [[RS("appjs.LEGENDS.13.01.term"), RS("appjs.LEGENDS.13.01.gloss")],
    [RS("appjs.LEGENDS.13.02.term"), RS("appjs.LEGENDS.13.02.gloss")],
    [RS("appjs.LEGENDS.13.03.term"), RS("appjs.LEGENDS.13.03.gloss")],
    [RS("appjs.LEGENDS.13.04.term"), RS("appjs.LEGENDS.13.04.gloss")],
    [RS("appjs.LEGENDS.13.05.term"), RS("appjs.LEGENDS.13.05.gloss")]],
};


/* ===== Reading rework 2026-09-19 (mockup data/out/readingMockup.html, decisions: A-tabs,
   inline SVG, card stats = medicine/dominant/missing/best/watch/decade) ===== */
const ALLGODS = ["比肩", "劫財", "食神", "傷官", "正財", "偏財", "正官", "七殺", "正印", "偏印"];
/* the chart carries its own legend; fall back to the table below when it does not */
const godEn = (c, g) => ((c.tengods_legend || {})[g] || {}).en || TG_EN_FALLBACK[g] || g;
const STAR_GROUP_ZH = { "Spouse star": "配偶星", "Wealth stars": "财星", "Authority stars": "官杀", "Resource stars": "印星", "Output stars": "食伤", "Peer stars": "比劫" };
const WHEEL_KEY = [["比劫", RS("appjs.GRP_EN.比劫"), "比肩", "劫財"], ["食傷", RS("appjs.GRP_EN.食傷"), "食神", "傷官"], ["財星", RS("appjs.GRP_EN.財星"), "正財", "偏財"],
  ["官殺", RS("appjs.GRP_EN.官殺"), "正官", "七殺"], ["印星", RS("appjs.GRP_EN.印星"), "正印", "偏印"]];
const TG_GIST = Object.fromEntries(Object.entries({   // one line per role, from the engine's TEN_GOD_MEANING
  比肩: RS("appjs.TG_GIST.比肩"), 劫財: RS("appjs.TG_GIST.劫財"), 食神: RS("appjs.TG_GIST.食神"), 傷官: RS("appjs.TG_GIST.傷官"),
  偏財: RS("appjs.TG_GIST.偏財"), 正財: RS("appjs.TG_GIST.正財"), 七殺: RS("appjs.TG_GIST.七殺"), 正官: RS("appjs.TG_GIST.正官"),
  偏印: RS("appjs.TG_GIST.偏印"), 正印: RS("appjs.TG_GIST.正印") }).flatMap(([k, v]) =>
  [[k, v], [k.replace("財", "财").replace("殺", "杀").replace("傷", "伤"), v]]));
const TG_EN_FALLBACK = { 比肩: RS("appjs.TG_EN_FALLBACK.比肩"), 劫財: RS("appjs.TG_EN_FALLBACK.劫財"), 食神: RS("appjs.TG_EN_FALLBACK.食神"),
  傷官: RS("appjs.TG_EN_FALLBACK.傷官"), 正財: RS("appjs.TG_EN_FALLBACK.正財"), 偏財: RS("appjs.TG_EN_FALLBACK.偏財"),
  正官: RS("appjs.TG_EN_FALLBACK.正官"), 七殺: RS("appjs.TG_EN_FALLBACK.七殺"), 正印: RS("appjs.TG_EN_FALLBACK.正印"), 偏印: RS("appjs.TG_EN_FALLBACK.偏印") };
const deepWrap = (label, inner) => inner
  ? `<details class="deep"><summary>${label}</summary><div class="deepbody">${inner}</div></details>` : "";

const ZODIAC = { 鼠: ["🐭", RS("appjs.ZODIAC.鼠.animal")], 牛: ["🐮", RS("appjs.ZODIAC.牛.animal")], 虎: ["🐯", RS("appjs.ZODIAC.虎.animal")], 兔: ["🐰", RS("appjs.ZODIAC.兔.animal")],
  龙: ["🐲", RS("appjs.ZODIAC.龙.animal")], 蛇: ["🐍", RS("appjs.ZODIAC.蛇.animal")], 马: ["🐴", RS("appjs.ZODIAC.马.animal")], 羊: ["🐑", RS("appjs.ZODIAC.羊.animal")],
  猴: ["🐵", RS("appjs.ZODIAC.猴.animal")], 鸡: ["🐔", RS("appjs.ZODIAC.鸡.animal")], 狗: ["🐶", RS("appjs.ZODIAC.狗.animal")], 猪: ["🐷", RS("appjs.ZODIAC.猪.animal")],
  龍: ["🐲", RS("appjs.ZODIAC.龙.animal")], 馬: ["🐴", RS("appjs.ZODIAC.马.animal")], 雞: ["🐔", RS("appjs.ZODIAC.鸡.animal")], 豬: ["🐷", RS("appjs.ZODIAC.猪.animal")] };
const EL_EN = { 木: RS("appjs.EL_EN.木"), 火: RS("appjs.EL_EN.火"), 土: RS("appjs.EL_EN.土"), 金: RS("appjs.EL_EN.金"), 水: RS("appjs.EL_EN.水") };

function strengthGauge(st) {
  const x = Math.max(-1, Math.min(1, st.score));       // score −1..+1
  const px = 150 + x * 130;
  return `<svg viewBox="0 0 300 64" class="sgauge" role="img"
      aria-label="${RS("appjs.strengthGauge.001", {st_verdict: st.verdict, st_score: st.score})}">
    <rect x="20" y="26" width="260" height="10" rx="5" fill="rgba(0,0,0,.07)"/>
    <rect x="20" y="26" width="104" height="10" rx="5" fill="#e8c8be"/>
    <rect x="176" y="26" width="104" height="10" rx="5" fill="#c9dcc0"/>
    <line x1="150" y1="20" x2="150" y2="42" stroke="#b9b4a6" stroke-width="1.5"/>
    <circle cx="${px}" cy="31" r="8" fill="#a63d2f"/>
    <text x="24" y="16" font-size="10" fill="#8b8f9a">${RS("appjs.strengthGauge.002")}</text>
    <text x="276" y="16" font-size="10" fill="#8b8f9a" text-anchor="end">${RS("appjs.strengthGauge.003")}</text>
    <text x="150" y="58" font-size="11" font-weight="700" fill="#22242a"
      text-anchor="middle">${RS("appjs.strengthGauge.004", {st_verdict: st.verdict, st_score: st.score})}</text>
  </svg>`;
}

/* the eight directions as a painted compass ring (owner pick A, 2026-10-10): north at the top, green washes where the
   house stars help, red-ochre where they harm, the person's season painting at the centre; characters in the ring, English in the key */
function bazhaiCompass(c) {
  const ANG = { N: -90, NE: -45, E: 0, SE: 45, S: 90, SW: 135, W: 180, NW: -135 }, R0 = 64, R1 = 158, C = 170;
  const pt = (r, a) => [C + r * Math.cos(a * Math.PI / 180), C + r * Math.sin(a * Math.PI / 180)];
  const season = { 寅: "spring", 卯: "spring", 辰: "spring", 巳: "summer", 午: "summer", 未: "summer", 申: "autumn", 酉: "autumn", 戌: "autumn", 亥: "winter", 子: "winter", 丑: "winter" }[c.pillars.month[1]];
  const GOOD = ["生氣", "天醫", "延年", "伏位"], rows = Object.entries(PALACE_DIR).map(([pal, dir]) => ({ pal, dir, s: c.youxing[pal], good: GOOD.includes(c.youxing[pal]) }));
  let svg = `<svg viewBox="0 0 340 340" class="cring keepzh" data-notip role="img" aria-label="${RS("appjs.bazhaiCompass.001", {rows_map: rows.map((r) => `${r.dir} ${BAZHAI_EN[r.s] ? BAZHAI_EN[r.s][0] : r.s}, ${r.good ? "use" : "avoid"}`).join("; ")})}">
    <circle cx="${C}" cy="${C}" r="${R1 + 8}" fill="#fdfbf6" stroke="#d9d0c1"/>`;
  rows.forEach((r, i) => {
    const a = ANG[r.dir], [x1, y1] = pt(R1, a - 22.5), [x2, y2] = pt(R1, a + 22.5), [x3, y3] = pt(R0, a + 22.5), [x4, y4] = pt(R0, a - 22.5);
    const d = `M${x1.toFixed(1)} ${y1.toFixed(1)}A${R1} ${R1} 0 0 1 ${x2.toFixed(1)} ${y2.toFixed(1)}L${x3.toFixed(1)} ${y3.toFixed(1)}A${R0} ${R0} 0 0 0 ${x4.toFixed(1)} ${y4.toFixed(1)}Z`;
    const [mx, my] = pt((R0 + R1) / 2 + 4, a), id = `cr${++INK_N}`;
    svg += `<clipPath id="${id}"><path d="${d}"/></clipPath><path d="${d}" fill="${r.good ? "#e6f0e4" : "#f7e6e1"}"/>
      <image href="/static/img/reading/sw/${r.good ? "wood" : "fire"}-128.webp" x="${(mx - 70).toFixed(1)}" y="${(my - 70).toFixed(1)}" width="140" height="140" opacity="${r.good ? 0.5 : 0.38}" clip-path="url(#${id})"/>
      <path d="${d}" fill="none" stroke="#faf7f2" stroke-width="3"/>
      <text x="${mx.toFixed(1)}" y="${(my - 4).toFixed(1)}" text-anchor="middle" font-size="15" font-weight="700" fill="#2b2620" font-family="Georgia,'Noto Serif SC',serif">${r.dir} ${toSimp(r.pal)} ${r.good ? "✓" : "✗"}</text>
      <text x="${mx.toFixed(1)}" y="${(my + 15).toFixed(1)}" text-anchor="middle" font-size="14" fill="#2b2620" font-family="'Noto Serif SC',serif">${toSimp(r.s)}</text>`;
  });
  const cid = `cc${++INK_N}`;
  svg += `<clipPath id="${cid}"><circle cx="${C}" cy="${C}" r="${R0 - 4}"/></clipPath>
    <image href="/static/img/reading/bg/${STEM_SLUG[c.day_master]}-${season}-600.jpg" x="${C - R0}" y="${C - R0}" width="${2 * R0}" height="${2 * R0}" preserveAspectRatio="xMidYMid slice" clip-path="url(#${cid})"/>
    <circle cx="${C}" cy="${C}" r="${R0 - 4}" fill="none" stroke="#8a7f72" stroke-width="1.5"/>
    <text x="${C}" y="9" text-anchor="middle" font-size="11" fill="#5f574e">${RS("appjs.DIR_WORD_EN.N")}</text></svg>`;
  const key = zhKey(rows.map((r) => [toSimp(r.s), BAZHAI_EN[r.s] ? BAZHAI_EN[r.s][0] : ""]).concat(rows.map((r) => [toSimp(r.pal), DIR_WORD_EN[r.dir] || r.dir])).concat([["✓", "use"], ["✗", "avoid"]]));
  return `${svg}${key}`;
}

/* ---- Reading layout A (owner pick 2026-10-10) -------------------------------------------
   A one-screen answer, then five chapters titled as questions on one scroll (no hidden tabs).
   Each lead conclusion is a card: plain headline, what it means, what to do, signal strength,
   and the proof behind "Why the chart says this". The plain view sits beside the classical
   chart. All plain copy comes from c.plain (engine/plain.py, owner-approved templates). */
const CHAPTERS = [
  ["makeup", RS("appjs.CHAPTERS.makeup.title"), RS("appjs.CHAPTERS.makeup.q"), RS("appjs.CHAPTERS.makeup.tech"), "what-is-bazi", RS("appjs.CHAPTERS.makeup.what")],
  ["balance", RS("appjs.CHAPTERS.balance.title"), RS("appjs.CHAPTERS.balance.q"), RS("appjs.CHAPTERS.balance.tech"), "five-elements-cycles", RS("appjs.CHAPTERS.balance.what")],
  ["drives", RS("appjs.CHAPTERS.drives.title"), RS("appjs.CHAPTERS.drives.q"), RS("appjs.CHAPTERS.drives.tech"), "ten-gods-guide", RS("appjs.CHAPTERS.drives.what")],
  ["timing", RS("appjs.CHAPTERS.timing.title"), RS("appjs.CHAPTERS.timing.q"), RS("appjs.CHAPTERS.timing.tech"), "luck-cycles-and-windows", RS("appjs.CHAPTERS.timing.what")],
  ["space", RS("appjs.CHAPTERS.space.title"), RS("appjs.CHAPTERS.space.q"), RS("appjs.CHAPTERS.space.tech"), "eight-house-directions", RS("appjs.CHAPTERS.space.what")]];
const EL_SLUG = { 木: "wood", 火: "fire", 土: "earth", 金: "metal", 水: "water" };
const STEM_SLUG = { 甲: "jia", 乙: "yi", 丙: "bing", 丁: "ding", 戊: "wu", 己: "ji", 庚: "geng", 辛: "xin", 壬: "ren", 癸: "gui" };
const SWATCH = { 火: ["#c5221f", "#7b2d8e", "#e07b1f"], 水: ["#1b1f2a", "#1a56b0"], 木: ["#187a35", "#6aa84f"],
  土: ["#c9a227", "#d8c8a4", "#7a601b"], 金: ["#ffffff", "#c9a227", "#b8bec6"] };
const pWhy = (txt, html, label = RS("appjs.pWhy.001")) => txt || html
  ? `<details class="rp-why"><summary>${label}</summary><div class="rp-whyb">${txt ? `<p>${txt}</p>` : ""}${html || ""}</div></details>` : "";
const PILLAR_KEYS = [["year", RS("appjs.PILLAR_KEYS.year.label")], ["month", RS("appjs.PILLAR_KEYS.month.label")], ["day", RS("appjs.PILLAR_KEYS.day.label")], ["hour", RS("appjs.PILLAR_KEYS.hour.label")]];
function pSeal(c) {
  const P = c.pillars;
  return `<div class="rp-seal keepzh" data-notip role="img" aria-label="${RS("appjs.pSeal.001", {PILLAR_KEYS_map: PILLAR_KEYS.map(([k]) => P[k]).join(" ")})}">${PILLAR_KEYS.map(([k, lab]) =>
    `<div${k === "day" ? ' class="me"' : ""}><span style="color:${EL_TXT[STEM_EL[P[k][0]]]}">${P[k][0]}</span><span style="color:${EL_TXT[BR_EL[P[k][1]]]}">${P[k][1]}</span><small>${lab}</small></div>`).join("")}</div>`;
}
const SEASON_OF = { 寅: "spring", 卯: "spring", 辰: "spring", 巳: "summer", 午: "summer", 未: "summer",
  申: "autumn", 酉: "autumn", 戌: "autumn", 亥: "winter", 子: "winter", 丑: "winter" };
function preloadOpeningArt(c) {
  if (!c || !c.pillars || !document.head) return;
  const art = `/static/img/reading/bg/${STEM_SLUG[c.day_master]}-${SEASON_OF[c.pillars.month[1]]}`, phone = matchMedia("(max-width:640px)").matches;
  const l = document.createElement("link"); l.rel = "preload"; l.as = "image"; l.fetchPriority = "high";
  l.imageSrcset = phone ? `${art}-p-600.webp 600w, ${art}-p-900.webp 900w` : `${art}-600.jpg 600w, ${art}-1200.jpg 1200w`;
  l.imageSizes = phone ? "100vw" : "(max-width:1180px) 100vw, 1180px";
  document.head.appendChild(l);
}
/* the side of life the reader is in now: the four sides' age ranges against the reader's age */
function sideNow(c) {
  const age = (c.story || {}).age; if (age == null) return null;
  return (c.plain.sides || []).find((s) => { const [a, b] = String(s.ages).replace("+", "–999").split("–").map(Number);
    return age >= a && age <= (b || 999); }) || null;
}
/* the opening line speaks to the person by name (owner 2026-10-10): "王大明, you are garden soil in spring." */
const nameLine = (who, head) => who ? `<span class="rp-hname keepzh" data-notip>${who}${IS_ZH ? "，" : ","}</span>${IS_ZH ? "" : " "}${head.replace(/^You\b/, "you")}` : head;
function pIdentity(c, name) {
  const I = c.plain.identity, now = sideNow(c);
  const where = now ? `${RS("appjs.pIdentity.001", {year_your: { year: RS("appjs.pIdentity.002"), month: RS("appjs.pIdentity.003"), day: RS("appjs.pIdentity.004"), hour: RS("appjs.pIdentity.005") }[now.key]})}`
    : RS("appjs.pIdentity.006");
  const season = { 寅: "spring", 卯: "spring", 辰: "spring", 巳: "summer", 午: "summer", 未: "summer",
    申: "autumn", 酉: "autumn", 戌: "autumn", 亥: "winter", 子: "winter", 丑: "winter" }[c.pillars.month[1]];
  const art = `/static/img/reading/bg/${STEM_SLUG[c.day_master]}-${season}`;   // the identity line, drawn: stem × season
  return `<section class="rp-ident rp-bgart" data-art="${STEM_SLUG[c.day_master]}-${season}">
    <picture class="rp-bgimg"><source media="(max-width:640px)" type="image/webp" srcset="${art}-p-600.webp 600w, ${art}-p-900.webp 900w" sizes="100vw">
      <source media="(max-width:640px)" srcset="${art}-p-600.jpg 600w, ${art}-p-900.jpg 900w" sizes="100vw">
      <img src="${art}-1200.jpg" srcset="${art}-600.jpg 600w, ${art}-1200.jpg 1200w" sizes="(max-width:1180px) 100vw, 1180px" alt="" fetchpriority="high" decoding="async"></picture><div class="rp-idtext"><p class="rp-name">${dn(name || c.name)}</p>${pSeal(c)}
      <h2 class="rp-h">${nameLine(dn(name || c.name), I.head)}</h2><p class="rp-sub">${I.sub}</p><p class="rp-sub rp-where">${where}</p>${pWhy(I.why)}</div>
  </section>`;   // the Day Master image now lives on the "you at home" card in the four sides
}
/* the four pillars as four life characters (owner pick 2026-10-10); replaces the Four Palaces chart */
function pSides(c) {
  const S = c.plain.sides || []; if (!S.length) return "";
  const kids = ((c.palaces || {}).children || {}).line, now = sideNow(c);
  return `<section class="rp-sides" aria-labelledby="h-sides"><h3 id="h-sides">${RS("appjs.pSides.001")}</h3><div class="rp-sidegrid">${S.map((s) =>
    `<article class="rp-side${s.key === "day" ? " me" : ""}${now === s ? " here" : ""}"${now === s ? ' aria-current="true"' : ""}>${now === s ? RS("appjs.pSides.002") : ""}<img src="/static/img/reading/dm-${STEM_SLUG[s.stem]}-600.jpg" alt="" width="600" height="400" loading="lazy" decoding="async">
      <p class="rp-k">${s.area.charAt(0).toUpperCase() + s.area.slice(1)}${s.ages ? `${RS("appjs.pSides.003", {s_ages: s.ages})}` : ""}</p><h4>${s.head}</h4><p>${s.role}</p></article>`).join("")}</div>
    ${pWhy("", S.map((s) => `<p>${s.why}</p>`).join("") + (kids ? `<p>${RS("appjs.pSides.004", {kids: kids})}</p>` : ""))}</section>`;
}
const DRIVE_IMG = { 比劫: "peers", 食傷: "expression", 財: "money", 官殺: "duty", 印: "support" };
function pCareers(c) {
  const C = c.careers || {}, row = (a) => `<li><b>${a.en}</b> (${a.score} pts): ${a.reasons.join("; ")}</li>`;
  return (C.top || []).length ? `<p><b>Career archetypes, ranked.</b></p><ul class="rp-list">${C.top.map(row).join("")}${(C.avoid || []).map((a) =>
    `<li>Harder going: <b>${a.en}</b> (${a.score} pts): ${a.reasons.join("; ")}</li>`).join("")}</ul>` : "";
}
/* The helping element's ink dots, drawn only in the "What helps you" region (owner 2026-10-14, round 38: they left the element rows).
   A dot whose colour sits within 15% of the page's cream in luminance (metal's white) gets a thin ring in the muted ink so every dot has an edge. */
const PANEL_BG = "#faf7f2", RING_MAX_DL = 0.15;
const relLum = (hex) => { const v = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255).map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
const needsRing = (hex) => Math.abs(relLum(hex) - relLum(PANEL_BG)) <= RING_MAX_DL;
const swDots = (el) => (SWATCH[el] || []).map((x) => `<span class="swd${needsRing(x) ? " ring" : ""}"><i style="background-color:${x}"></i></span>`).join("");
const swBlot = (el) => `--blot:url('/static/img/reading/sw/${EL_SLUG[el]}-128.webp')`;
/* One row per element: painted disc, name, track, the printed share, the band word. The band word takes the flag colour only when it is
   not "about right". The helping element's name carries a quiet second line, "most useful" (round 38: the ink dots left the row). In Chinese
   the disc already carries the character, so the row has no name cell: the disc names the element to a screen reader through its hidden
   label, and the tag becomes a quiet line under the row. The quiet line under a row appears only where the standing among charts contradicts that
   band word; the rule lives in engine/element_reference.py (standing.contradicts) and arrives on the row. */
function pBudget(c, compact) {
  return `<div class="rp-bud${IS_ZH ? " rp-bud-zh" : ""}">${c.plain.balance.map((r) => { const st = r.standing, flag = (r.band_key || r.band) !== "about right",
    most = compact && r.medicine ? `<span class="rp-most">${RS("appjs.pBudget.004")}</span>` : "";
    return `${eli(r.el, { silent: !IS_ZH })}${IS_ZH ? "" : `<span class="rp-nm">${r.en}${most}</span>`}
    <span class="rp-tr"><i style="width:${Math.min(100, Math.max(2, r.share / 60 * 100)).toFixed(0)}%;background:${EL_COL[r.el]}"></i></span>
    <span class="rp-pct">${Math.round(r.share)}%</span><span class="rp-bd${flag ? " rp-strong" : ""}">${r.band}</span>${IS_ZH ? most.replace('class="rp-most"', 'class="rp-most rp-most-ln"') : ""}${!compact && (r.medicine || r.note)
      ? `<span class="rp-note">${r.medicine ? (RS("appjs.pBudget.001") + ' ') : ""}${r.note}</span>` : ""}${st && st.contradicts
      ? `<span class="rp-pc">${RS(st.side === "heavier" ? "appjs.pBudget.002" : "appjs.pBudget.003", {st_n: st.n})}</span>` : ""}`; }).join("")}</div>`;
}
/* each answer card's "?" opens the evidence panel that proves it (owner 2026-10-10); keys in EV_OWNER */
const ANS_EV = { balance: ["elements", "strength"], helps: ["medicine"], year: ["years"], acts: ["medicine", "placements"] };
const ansQ = (k, name) => `<button type="button" class="rp-q" data-ev="${ANS_EV[k].join(" ")}" aria-label="${RS("appjs.ansQ.001", {name: name})}">?</button>`;
/* The panel's ground, keyed through one lookup. Today six pictures exist: one per helping element and one for a chart whose every element sits
   inside its band (13.5% of charts). A pair picture (heaviest element + helping element, 25 in all) is added by putting
   web/img/reading/bal/<heavy>-<help>-{600,1200}.webp on disk and its slug here; the lookup already tries the pair first after "balanced". */
/* No picture on a phone (owner 2026-10-14, round 38): the art sits in a <picture> whose only real source applies above the reading page's
   640 px breakpoint. Below it no source matches, the <img> keeps this inline 1 px transparent GIF (no request) and CSS removes the box. */
const BLANK_PX = "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==";
const BAL_ART = new Set(["wood", "fire", "earth", "metal", "water", "balanced"]);
function balanceArt(c, rows) {
  const heavy = EL_SLUG[rows[0].el], help = EL_SLUG[c.plain.helps.el];
  const inBand = rows.every((r) => !["too much", "too little"].includes(r.band_key || r.band));
  return [inBand ? "balanced" : null, `${heavy}-${help}`, help].find((k) => k && BAL_ART.has(k)) || null;
}
/* the one-line summary: heaviest element with where it stands among charts, the helping element, and the year */
function balanceStrip(c) {
  const top = c.plain.balance[0], st = top.standing, H = c.plain.helps, Y = c.plain.year;
  const lead = st ? RS(st.side === "heavier" ? "appjs.pBalance.001" : "appjs.pBalance.002", {EL_EN_top: EL_EN[top.el], top_share: Math.round(top.share), st_n: st.n})
    : RS("appjs.pBalance.003", {EL_EN_top: EL_EN[top.el], top_share: Math.round(top.share)});
  return `${lead}${IS_ZH ? "" : " "}${Y ? RS("appjs.pBalance.004", {EL_EN_H: EL_EN[H.el], Y_y: Y.y, Y_word: IS_ZH ? Y.word : Y.word.toLowerCase()})
    : RS("appjs.pBalance.005", {EL_EN_H: EL_EN[H.el]})}`;
}
const ansHead = (label, btn) => `<div class="rp-rh"><p class="rp-k">${label}</p>${btn}</div>`;
/* One seamless panel, single column, labelled regions: the element rows, what helps, this year, two things to do. No card edges (owner 2026-10-14). */
function pAnswers(c) {
  const P = c.plain, H = P.helps, Y = P.year, art = balanceArt(c, P.balance);
  return `<div class="rp-answers rp-pan${art ? " has-art" : ""}">
    <div class="rp-ans rp-bal">${art ? `<picture class="rp-artp"><source media="(min-width:641px)" srcset="/static/img/reading/bal/${art}-600.webp 600w, /static/img/reading/bal/${art}-1200.webp 1200w" sizes="(max-width:1079px) 100vw, 960px"><img class="rp-art" src="${BLANK_PX}" alt="" aria-hidden="true" width="1200" height="418" loading="lazy" decoding="async" data-art="${art}"></picture>` : ""}
      ${ansHead(RS("appjs.pAnswers.001"), ansQ("balance", RS("appjs.pAnswers.005")))}<h3 class="rp-sum">${balanceStrip(c)}</h3>${pBudget(c, true)}</div>
    <div class="rp-ans rp-help">${ansHead(RS("appjs.pAnswers.003"), ansQ("helps", RS("appjs.pAnswers.006")))}<h3>${H.head}</h3><div class="rp-sw" aria-hidden="true" style="${swBlot(H.el)}">${swDots(H.el)}</div><p>${H.means}</p></div>
    ${Y ? `<div class="rp-ans">${ansHead(RS("appjs.pAnswers.007"), ansQ("year", RS("appjs.pAnswers.008")))}<p class="rp-year"><span class="rp-ybig">${Y.y}</span> <span class="rp-gz keepzh" data-notip>${Y.gz}</span></p>
      <h3>${Y.word}</h3><p>${Y.means}</p></div>` : ""}
    <div class="rp-ans">${ansHead(RS("appjs.pAnswers.004"), ansQ("acts", RS("appjs.pAnswers.009")))}<ul class="rp-acts">${P.actions.map((a) => `<li>${a}</li>`).join("")}</ul></div></div>`;
}
/* luck decades as rows: a painted phase mark, the ages, the phase, one plain line; the next turn named (owner 2026-10-10) */
const PHASE_LINE = { growth: RS("appjs.PHASE_LINE.growth"), consolidation: RS("appjs.PHASE_LINE.consolidation"),
  transition: RS("appjs.PHASE_LINE.transition"), corrective: RS("appjs.PHASE_LINE.corrective") };
function pWeather(c) {
  const D = c.plain.decades || [], i = D.findIndex((d) => d.current), nx = i >= 0 ? D[i + 1] : D[0];
  return `<ol class="rp-dec" aria-label="${RS("appjs.pWeather.001")}">${D.map((d, k) => `<li class="${d.current ? "now" : i >= 0 && k < i ? "past" : ""}"${d.current ? ' aria-current="true"' : ""}>
      <img src="/static/img/reading/mk/${d.phase}-96.png" alt="" width="40" height="40" decoding="async">
      <span class="rp-dage">${d.ages}</span><b>${d.word}</b><span class="rp-dline">${PHASE_LINE[d.phase] || ""}</span>${d.current ? RS("appjs.pWeather.002") : ""}</li>`).join("")}</ol>
    ${nx ? `<p class="rp-dnext">${RS("appjs.pWeather.003", {nx_word: nx.word.toLowerCase(), String_nx: String(nx.ages).split(/[–-]/)[0]})}</p>` : ""}`;
}
/* the wealth store (財庫): the four storage branches, this chart's store outlined with its state (round D) */
const VAULTS = [["辰", "水"], ["戌", "火"], ["丑", "金"], ["未", "木"]];
function pVault(c) {
  const V = (c.palaces || {}).vault || {}, want = V.present ? V.branch : (VAULTS.find((v) => v[1] === V.element) || [])[0];
  const opens = ((V.state || "").match(/(?:opens in |到\s*)(\S)/) || [])[1];
  const st = V.present ? (V.open ? "开" : "闭") : "无";
  return `<div class="rp-vault keepzh" data-notip>${VAULTS.map(([br, el]) => `<div class="${br === want ? "me" : ""}">
      <b style="color:${EL_TXT[el]}">${br}</b><small>${el}库</small>${br === want ? `<em>${st}</em>` : ""}</div>`).join("")}</div>
    ${zhKey([...VAULTS.map(([br, el]) => [br, `${RS("appjs.pVault.001", {ZODIAC_BR_ANIMAL: (ZODIAC[BR_ANIMAL[br]] || ["", br])[1], EL_EN_el: EL_EN[el]})}`]),
      ["开", "open"], ["闭", "sealed"], ["无", RS("appjs.pVault.002")]].concat(opens ? [[opens, `${RS("appjs.pVault.003", {ZODIAC_BR_ANIMAL: (ZODIAC[BR_ANIMAL[opens]] || ["", opens])[1]})}`]] : []))}`;
}
const pYears = (c) => `<div class="rp-yrs">${c.plain.years.map((y) => `<div class="${y.overall}"><b>${y.y}</b>${y.word.split(" ")[0]}</div>`).join("")}</div>`;
const pDrives = (c) => `<div class="rp-drv">${c.plain.drives.groups.map((g) => `<b>${g.name}</b><span class="rp-tr"><i style="width:${Math.max(1, g.pct).toFixed(0)}%"></i></span>
  <span>${Math.round(g.pct)}%</span><small>${g.gloss} (${g.zh})</small>`).join("")}</div>`;
function pRoom(c) {
  const S = c.plain.space; if (!S) return "";
  const pos = { NW: [0, 0], N: [1, 0], NE: [2, 0], W: [0, 1], E: [2, 1], SW: [0, 2], S: [1, 2], SE: [2, 2] }, q = 93.3;
  let s = `<svg class="rp-room" viewBox="0 0 300 312" role="img" aria-label="${RS("appjs.pRoom.001", {Object_entries: Object.entries(S.marks).map(([d, l]) => `${RS("appjs.pRoom.003", {l_join: l.join(" and "), d: d})}`).join("; ")})}">
    <text x="150" y="11" text-anchor="middle" font-size="11" fill="#6b6359">${RS("appjs.DIR_WORD_EN.N")}</text>
    <rect x="10" y="22" width="280" height="280" fill="#fff" stroke="#2b2620" stroke-width="2"/>`;
  [1, 2].forEach((k) => { s += `<line x1="${10 + k * q}" y1="22" x2="${10 + k * q}" y2="302" stroke="#e5ded2"/><line x1="10" y1="${22 + k * q}" x2="290" y2="${22 + k * q}" stroke="#e5ded2"/>`; });
  Object.entries(pos).forEach(([dr, [cx, cy]]) => { const x = 10 + cx * q + q / 2, y = 22 + cy * q + q / 2;
    s += `<text x="${x}" y="${y - 22}" text-anchor="middle" font-size="12" fill="#6b6359">${dr}</text>`;
    (S.marks[dr] || []).forEach((lab, j) => { s += `<rect x="${x - 38}" y="${y - 10 + j * 24}" width="76" height="20" rx="10" fill="#c7301d"/>
      <text x="${x}" y="${y + 4 + j * 24}" text-anchor="middle" font-size="12" fill="#fff" font-weight="600">${lab}</text>`; }); });
  return s + "</svg>";
}
const pRelations = (c) => { const ps = c.plain.makeup.pairs;
  return ps.length ? `<ul class="rp-list">${ps.map((x) => `<li>${RS("appjs.pRelations.001", {x_a: x.a.charAt(0).toUpperCase() + x.a.slice(1), x_b: x.b, x_note: x.note, x_kind: x.kind})}</li>`).join("")}</ul>`
    : ("<p>" + RS("appjs.pRelations.002") + "</p>"); };
function pSlimGrid(c) {
  const P = c.pillars, tg = c.ten_gods || {}, hid = c.hidden_gods || {};
  return `<div class="rp-sg keepzh" data-notip>${PILLAR_KEYS.map(([k, lab]) => { const g = k === "day" ? "日主" : tg[k] || "";
    return `<div${k === "day" ? ' class="me"' : ""}><small>${k === "day" ? RS("appjs.pSlimGrid.002") : lab}</small><span class="rp-tg" title="${k === "day" ? RS("appjs.pSlimGrid.003") : godEn(c, g)}">${g}</span>
      <span class="rp-big" style="color:${EL_TXT[STEM_EL[P[k][0]]]}">${P[k][0]}</span><span class="rp-big" style="color:${EL_TXT[BR_EL[P[k][1]]]}">${P[k][1]}</span>
      <span class="rp-hid">${(hid[k] || []).map((x) => `<span title="${godEn(c, x.slice(2, -1))}">${x[0]}</span>`).join(" ")}</span></div>`; }).join("")}</div>
    <p class="rp-cap">${RS("appjs.pSlimGrid.001")}</p>`;
}
function pChapter([id, , q, tech, img, what], body, src) {
  return `<section class="rp-chap" id="ch-${id}" aria-labelledby="h-${id}"><div class="rp-chead"><div><h2 id="h-${id}">${q}</h2>
      <p class="rp-tech">${RS("appjs.pChapter.001", {tech: tech})}</p></div>
      <img src="${src || `/static/learn/img/hero/${img}-600.jpg`}" alt="" width="600" height="400" loading="lazy" decoding="async"></div>
    ${body}
    <p class="rp-learn">${RS("appjs.pChapter.002", {img: img, what: what})}</p></section>`;
}
/* Story layout (round 3, 2026-10-10). Each chapter reads as paragraphs from c.story (engine/story.py).
   Every sentence carries evidence ids; each id becomes a numbered marker that opens its proof in place,
   right under the paragraph that first cites it. A proof's figures render once, in the chapter that owns it. */
const CHART_CAP = { makeup: RS("appjs.CHART_CAP.makeup"), balance: RS("appjs.CHART_CAP.balance"),
  drives: RS("appjs.CHART_CAP.drives"), timing: RS("appjs.CHART_CAP.timing"), space: RS("appjs.CHART_CAP.space") };
const EV_OWNER = { pillars: "makeup", stars: "makeup", interactions: "makeup", personality: "makeup", elements: "balance", strength: "balance",
  flows: "balance", medicine: "balance", health: "balance", gods: "drives", domains: "drives", work: "drives", money: "drives",
  decades: "timing", years: "timing", months: "timing", days: "timing", placements: "space", afflict: "space" };
function pStory(id, S, ev, proofs, chart) {
  const num = {}; let n = 0;
  const mk = (e) => `<button type="button" class="mk" aria-expanded="false" aria-controls="ev-${id}-${num[e]}">${RS("appjs.pStory.001", {num_e: num[e]})}</button>`;
  const panel = (e) => `<div class="ev" id="ev-${id}-${num[e]}" data-ev="${e}" tabindex="-1" hidden><button type="button" class="ev-x" aria-label="${RS("appjs.pStory.002")}">×</button><p class="evh">${num[e]}. ${ev[e].label}</p>${zhNoteIf(ev[e].why)}${ev[e].why ? ev[e].why.split("\n").map((x) => `<p>${x}</p>`).join("") : ""}${(proofs[e] || []).join("")}<button type="button" class="ev-back">${RS("appjs.pStory.003")}</button></div>`;
  // a run of sentences resting on the same evidence shows its markers once, at the end of the run
  const para = (ss, cls) => { const fresh = [];
    const html = ss.map((s, k) => s.t.replace(/^(If you do one thing:|只做一件事的话：)/, "<b>$&</b>") + (ss[k + 1] && ss[k + 1].ev.join() === s.ev.join() ? "" : s.ev.map((e) => {
      if (!num[e]) { num[e] = ++n; fresh.push(e); } return mk(e); }).join(""))).join(IS_ZH ? "" : " ");
    return `<p${cls ? ` class="${cls}"` : ""}>${html}</p>${fresh.map(panel).join("")}`; };
  let out = "";
  S.paras.forEach((p, k) => { out += para(p);
    if (k === S.chart_after && chart) out += `<figure class="rp-chart"><figcaption>${RS("appjs.pStory.004", {CHART_CAP_id: CHART_CAP[id]})}</figcaption>${chart}</figure>`; });
  if (S.one) out += para([S.one], "rp-one");
  return `<div class="rp-story">${out}</div>`;
}
function readingChapters(c, R) {
  const P = c.plain, ST = c.story;
  const A = buildPillars(c, R), E = buildElements(c, R), G = buildGods(c, R), T = buildTiming(c, R), K = buildCompass(c, R);
  const cur = (P.decades || []).find((d) => d.current), top = (P.drives.groups || [])[0] || {};
  const figs = {   // every figure and citation the card layout carried, keyed by the evidence it proves
    pillars: [A.figs.grid], stars: [A.figs.stars, R.narr(9)], interactions: [pRelations(c), A.figs.interactions],
    personality: [G.figs.axes, R.stb(10), R.narr(10)], elements: [pBudget(c), E.units, R.narr(1)],
    strength: [E.figs.gauge, R.narr(2), R.stb(2)], flows: [], medicine: [K.figs.medicine, R.stb(5), R.narr(5)],
    health: [E.figs.health, R.narr(11), R.stb(11)], gods: [pDrives(c), G.figs.structure, G.figs.bars, R.narr(4), R.narr(3)],
    domains: [G.figs.domains, R.stb(8), R.narr(8)], work: [G.figs.industries, R.stb(12), R.narr(12)],   // one work figure (roles and archetypes merged in)
    money: [pVault(c)], decades: [pWeather(c), R.narr(6)], years: [pYears(c), T.figs.thisyear, R.stb(13), R.narr(13)],
    months: [T.figs.rhythm], days: [T.figs.daily], placements: [pRoom(c), K.figs.placements, R.narr(7)], afflict: [K.figs.afflictions] };
  const uses = (id) => new Set(ST.chapters[id].paras.flat().concat(ST.chapters[id].one || []).flatMap((s) => s.ev));
  const U = Object.fromEntries(CHAPTERS.map(([id]) => [id, uses(id)]));
  const owner = (e) => U[EV_OWNER[e]] && U[EV_OWNER[e]].has(e) ? EV_OWNER[e] : (CHAPTERS.find(([id]) => U[id].has(e)) || [])[0];
  const proofsFor = (id) => Object.fromEntries(Object.keys(figs).map((e) => [e, owner(e) === id ? figs[e].filter(Boolean) : []]));
  const charts = { makeup: pSlimGrid(c), balance: E.figs.pentagon, drives: G.figs.wheel, timing: T.figs.strip, space: K.figs.grid };
  const orphan = Object.keys(figs).filter((e) => !owner(e)).flatMap((e) => figs[e]).filter(Boolean);   // nothing cites them: keep them reachable
  const rest = A.tail.filter((x) => x && x !== R.narr(9)).concat(orphan);
  const img = { balance: `/static/img/reading/${EL_SLUG[P.helps.el]}-600.jpg`,
    drives: DRIVE_IMG[top.zh] ? `/static/img/reading/drive-${DRIVE_IMG[top.zh]}-600.jpg` : "",
    timing: cur ? `/static/img/reading/phase-${cur.phase}-600.jpg` : "" };
  return CHAPTERS.map((ch) => pChapter(ch, pStory(ch[0], ST.chapters[ch[0]], ST.evidence, proofsFor(ch[0]), charts[ch[0]]), img[ch[0]])).join("")
    + (rest.length ? `<section class="rp-chap rp-sources" id="ch-sources" aria-labelledby="h-sources"><div class="rp-chead"><div><h2 id="h-sources">${RS("appjs.readingChapters.001")}</h2></div></div><div class="rd-tail">${rest.join("")}</div></section>` : "");
}
const pChapBar = () => `<nav class="rp-bar" aria-label="${RS("appjs.pChapBar.001")}"><div>${CHAPTERS.map(([id, lab]) =>
  `<a href="#ch-${id}">${lab}</a>`).join("")}</div></nav>`;
/* Site-wide term coloring (2026-09-20): element + ten-god mentions in running
   text get bold + their element color. Text-node walker, conservative regex —
   excludes 水平/火车/金额/土豆-style non-element words; skips svg/script. */
const GOD_LIST = ["比肩", "劫財", "劫财", "食神", "傷官", "伤官", "正財", "正财",
  "偏財", "偏财", "正官", "七殺", "七杀", "正印", "偏印"];
/* 用神 colour advice words painted in their own colour. 白 is NEVER white —
   it would vanish on the light card tints — it gets ink + a thin chip instead. */
const COLOUR_WORDS = { 红: "#c5221f", 紅: "#c5221f", 紫: "#7b3fa0",
  黄: "#7d5800", 黃: "#7d5800", 棕: "#8a5a2b", 绿: "#17702f", 綠: "#17702f",
  青: "#17702f", 蓝: "#1a56b0", 藍: "#1a56b0", 黑: "#22242a", 灰: "#4b5563",
  金: "#7d5c00", 白: "#4b5563" };
const COLOUR_EN = { red: "#c5221f", purple: "#7b3fa0", yellow: "#7d5800",
  brown: "#8a5a2b", orange: "#a84a06", gold: "#7d5f08", silver: "#4b5563", beige: "#6f6046", green: "#17702f", blue: "#1a56b0", black: "#22242a",
  grey: "#4b5563", gray: "#4b5563", white: "#4b5563" };
// only standalone colour words / dot-separated colour lists — never 明白, 黄金,
// 青年, 红包, 黑马 … (a colour char followed or preceded by another CJK char)
const CJK = "\u4e00-\u9fff";
const COLOUR_RE = new RegExp(
  `(?<![${CJK}])([红紅紫黄黃棕绿綠青蓝藍黑灰白金])(?![${CJK}])`, "g");
const TG_GRP_EN = { 比劫: RS("appjs.GRP_EN.比劫"), 印: RS("appjs.GRP_EN.印星"), 食傷: RS("appjs.GRP_EN.食傷"), 食伤: RS("appjs.GRP_EN.食傷"),
  財: RS("appjs.GRP_EN.財星"), 财: RS("appjs.GRP_EN.財星"), 官殺: RS("appjs.GRP_EN.官殺"), 官杀: RS("appjs.GRP_EN.官殺") };
function colorizeTerms(root, dm) {
  if (!root) return;
  /* an element character inside Chinese prose, away from the compounds that merely contain it (水平, 金额, 火车, 土豆) */
  const mk = (el) => new RegExp(`(${GOD_LIST.join("|")})|${el}|\\b(Wood|Fire|Earth|Metal|Water)\\b`, "g");
  const re = mk("(?<![\u4e00-\u9fff])(木|火(?!车|車)|土(?!豆)|金(?!额|額)|水(?!平|准|準))");
  /* "your balance", "what helps you" and the balance chapter write the element in the middle of a sentence (对水日主, 是金) */
  const reSec = mk("(木(?!头|頭|材)|火(?!车|車|锅|鍋|灾|災)|土(?!豆|地|壤)|金(?!额|額|钱|錢|融)|水(?!平|准|準|分|果))");
  const SEC = ".rp-ans,#ch-balance", reOf = (n) => (n.parentElement.closest(SEC) ? reSec : re);
  const EN2EL = { Wood: "木", Fire: "火", Earth: "土", Metal: "金", Water: "水" };
  const nodes = [];
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode: (n) => n.parentElement
      && !n.parentElement.closest("script,style,svg,input,textarea,.nocolor,.eli,h1,h2,h3:not(.rp-ans h3),a,button,summary")
      ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT });
  let t; while ((t = w.nextNode())) { const r = reOf(t); r.lastIndex = 0; if (r.test(t.nodeValue)) nodes.push(t); }
  for (const node of nodes) {
    const s = node.nodeValue, frag = document.createDocumentFragment(), rx = reOf(node);
    let last = 0, m; rx.lastIndex = 0;
    while ((m = rx.exec(s))) {
      frag.appendChild(document.createTextNode(s.slice(last, m.index)));
      const el = m[1] ? godEl(dm, tgCanon(m[1])) : (EN2EL[m[0]] || m[0]);
      const b = document.createElement("b");
      b.className = "tcol";
      b.style.color = EL_TXT[el] || "";
      b.textContent = m[0];
      frag.appendChild(b);
      last = m.index + m[0].length;
    }
    frag.appendChild(document.createTextNode(s.slice(last)));
    node.parentNode.replaceChild(frag, node);
  }
}

function colorizeColours(root) {
  if (!root) return;
  const enRe = new RegExp(`\\b(${Object.keys(COLOUR_EN).join("|")})\\b`, "gi");
  const nodes = [];
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode: (n) => n.parentElement
      && !n.parentElement.closest("script,style,svg,input,textarea,.nocolor,.tcol,.eli")
      ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT });
  let t; while ((t = w.nextNode())) {
    COLOUR_RE.lastIndex = 0; enRe.lastIndex = 0;
    if (COLOUR_RE.test(t.nodeValue) || enRe.test(t.nodeValue)) nodes.push(t);
  }
  for (const node of nodes) {
    const s = node.nodeValue, frag = document.createDocumentFragment();
    const hits = [];
    COLOUR_RE.lastIndex = 0; enRe.lastIndex = 0;
    let m;
    while ((m = COLOUR_RE.exec(s))) hits.push([m.index, m[0], COLOUR_WORDS[m[0]]]);
    while ((m = enRe.exec(s))) hits.push([m.index, m[0], COLOUR_EN[m[0].toLowerCase()]]);
    hits.sort((a, b) => a[0] - b[0]);
    let last = 0;
    for (const [idx, txt, col] of hits) {
      if (idx < last) continue;                       // no overlapping repaint
      frag.appendChild(document.createTextNode(s.slice(last, idx)));
      const b = document.createElement("b");
      b.className = "cw" + (/^(白|white|silver)$/i.test(txt) ? " cw-white" : "");   // pale colours: ink on a thin chip
      b.style.color = col;
      b.textContent = txt;
      frag.appendChild(b);
      last = idx + txt.length;
    }
    frag.appendChild(document.createTextNode(s.slice(last)));
    node.parentNode.replaceChild(frag, node);
  }
}

const ELEMENT_ZH_OF_STEM = (st) => ({ 木: "木", 火: "火", 土: "土", 金: "金", 水: "水" }[STEM_EL[st]] || "");

/* ===== Reading v4 (2026-09-26): five chart-led dashboards, one per tab.
   Spec: docs/designs/mockups/reading-<section>-v4.html, reading-dashboard-composition.md,
   reading-dashboard-synthesis-v4.md. Every figure = chart · one interpretation line ·
   facts · `?` legend. The interpretation lines are templates over payload fields. ===== */
const EL_ZH_OF_EN = { Wood: "木", Fire: "火", Earth: "土", Metal: "金", Water: "水" };
const elc = (ch) => { const e = EL_COL[ch] || EL_COL[STEM_EL[ch]] || EL_COL[BR_EL[ch]];
  return e ? `<b class="tcol" style="color:${e}">${ch}</b>` : ch; };
const elw = (el) => `<b class="tcol" style="color:${EL_TXT[el]}">${EL_EN[el]}</b>`;
const godc = (dm, g) => `<b class="tcol" style="color:${EL_TXT[godEl(dm, g)] || "inherit"}">${g}</b>`;
const grpOfGod = (g) => { g = tgCanon(g);
  return ["比肩", "劫財"].includes(g) ? "比劫" : ["食神", "傷官"].includes(g) ? "食傷"
    : ["正財", "偏財"].includes(g) ? "財" : ["正官", "七殺"].includes(g) ? "官殺" : "印"; };
const GRP_THEME = { 比劫: RS("appjs.GRP_THEME.比劫"), 印: RS("appjs.GRP_THEME.印"), 食傷: RS("appjs.GRP_THEME.食傷"),
  財: RS("appjs.GRP_THEME.財"), 官殺: RS("appjs.GRP_THEME.官殺") };
const GRP_EN = { 官殺: RS("appjs.GRP_EN.官殺"), 印星: RS("appjs.GRP_EN.印星"), 比劫: RS("appjs.GRP_EN.比劫"), 食傷: RS("appjs.GRP_EN.食傷"), 財星: RS("appjs.GRP_EN.財星") };
const COLOUR_ZH_EN = { 红: "red", 紅: "red", 紫: "purple", 黄: "yellow", 黃: "yellow", 棕: "brown",
  绿: "green", 綠: "green", 青: "green", 蓝: "blue", 藍: "blue", 黑: "black", 灰: "grey", 白: "white", 金: "gold" };
const legendList = (n) => (LEGENDS[n] || []).map(([k, v]) => `<div><b>${k}</b> — ${v}</div>`).join("");
const clip = (s, n) => { s = String(s || ""); return s.length > n ? s.slice(0, n - 1) + "…" : s; };

/* --- the figure ------------------------------------------------------------ */
function rdFig(o) {
  const legend = o.legend ? `<details class="rd-legend"><summary aria-label="${RS("appjs.rdFig.001")}">?</summary>
      <div class="rd-legend-body">${o.legend}</div></details>` : "";
  const facts = o.facts && o.facts.length ? `<div class="facts rd-facts">${o.facts
      .map(([k, v]) => `<span><span class="fk">${k}</span> ${v}</span>`).join("")}</div>` : "";
  return `<figure class="rd-fig rd-${o.tier}${o.extra ? " " + o.extra : ""}" style="grid-column: span ${o.span}">
    <figcaption class="rd-label"><span>${o.label}</span></figcaption>
    <div class="rd-chart">${o.chart}</div>
    <div class="rd-line-row"><p class="rd-line">${o.line}</p>${legend}</div>
    ${o.line2 ? `<p class="rd-line rd-line2">${o.line2}</p>` : ""}${facts}</figure>`;
}

/* --- shared pieces ----------------------------------------------------------- */
/* chart-grid glyphs stay Chinese (the glyph IS the chart) with their pinyin in the tooltip
   span; the small line under each carries the short gloss on first sight, nothing after */
const zhs = (g) => (window.GL ? GL.zhSpan(g) : g);
function pillarGrid(c) {   // owner pick 2026-10-10: characters only, English in each tooltip
  const lp = c.life_palaces, order = ["hour", "day", "month", "year"], head = { hour: "时", day: "日", month: "月", year: "年" };
  const col = (z, el) => `<span style="color:${EL_TXT[el]}">${zhs(z)}</span>`;
  const row = (lab, f, cls = "") => `<tr class="${cls}"><th scope="row">${zhs(lab)}</th>${order.map((p) => `<td${p === "day" ? ' class="dm"' : ""}>${f(p)}</td>`).join("")}</tr>`;
  const hid = (p) => c.hidden_gods[p].map((x) => `<span class="cghid">${col(x[0], STEM_EL[x[0]])}<small>${zhs(x.slice(2, -1))}</small></span>`).join(" ");
  const tp = (c.citations || []).find((x) => x.rule_id === "time-policy") || {};
  const clock = (tp.explanation || "").match(/(?:clock |钟表时间\s*)(\d{1,2}:\d{2})/);
  return `<div class="cgwrap keepzh"><table class="cgrid">
    <thead><tr><th></th>${order.map((p) => `<th scope="col"${p === "day" ? ' class="dm"' : ""}>${zhs(head[p])}</th>`).join("")}</tr></thead>
    <tbody>${row("十神", (p) => zhs(c.ten_gods[p]), "cggod")}
      ${row("天干", (p) => col(c.pillars[p][0], STEM_EL[c.pillars[p][0]]), "cgbig")}
      ${row("地支", (p) => col(c.pillars[p][1], BR_EL[c.pillars[p][1]]), "cgbig")}
      ${row("藏干", hid, "cghids")}
      ${row("长生", (p) => zhs(c.pillar_extras[p].stage))}
      ${row("纳音", (p) => zhs(c.pillar_extras[p].nayin))}</tbody></table>
    <p class="cgfacts">${zhs("命卦")} ${col(c.gua, GUA_EL[c.gua])} · ${zhs("生肖")} ${zhs(lp.animal)} · ${zhs("命宫")} ${zhs(lp.ming_gong)} · ${zhs("胎元")} ${zhs(lp.tai_yuan)} · ${zhs("年命星")} ${zhs(lp.life_star_zh)} · ${zhs("真太阳时")} ${(c.effective_time || "").slice(11)}${clock ? ` ${RS("appjs.pillarGrid.002", {clock: clock[1]})}` : ""}</p></div>
    <p class="cgcap">${RS("appjs.pillarGrid.001")}</p>`;
}
const GLOSS_IX = { 六害: RS("appjs.GLOSS_IX.六害"), 害: RS("appjs.GLOSS_IX.六害"), 冲: RS("appjs.GLOSS_IX.冲"), 六冲: RS("appjs.GLOSS_IX.冲"), 刑: RS("appjs.GLOSS_IX.刑"),
  破: RS("appjs.GLOSS_IX.破"), 六合: RS("appjs.GLOSS_IX.六合"), 三合: RS("appjs.GLOSS_IX.六合"), 半合: RS("appjs.GLOSS_IX.半合") };
function interactionsSvg(c) {
  const order = ["hour", "day", "month", "year"], zh = { hour: "时", day: "日", month: "月", year: "年" };
  const xs = {}; order.forEach((k, i) => (xs[k] = 80 + i * 160));
  const its = (c.interactions || []).slice()
    .sort((p, q) => Math.abs(xs[p.pillars[0]] - xs[p.pillars[1]]) - Math.abs(xs[q.pillars[0]] - xs[q.pillars[1]]));
  const many = its.length >= 4;                    // four or more: arc carries the kind only, a legend carries the rest
  const NY = 150, R = 26, boxes = [];
  let s = "", minY = NY - R - 10, maxY = NY + 48;
  its.forEach((it, i) => {
    const [a, b] = it.pillars; const [x1, x2] = [xs[a], xs[b]].sort((p, q) => p - q);
    const h = 40 + 28 * (x2 - x1) / 160, good = it.kind.includes("合"), col = good ? "#0e7a6a" : "#99460a";
    const below = its.length >= 3 && i % 2 === 1;   // alternate sides once three arcs share the strip
    const y0 = below ? NY + R : NY - R, ctl = below ? y0 + h * 1.6 : y0 - h * 1.6;
    const text = many ? it.kind : `${it.kind} ${it.pair}`;
    const lx = (x1 + x2) / 2, half = text.length * 11.5;
    let ly = below ? y0 + h * 0.8 + 22 : y0 - h * 0.8 - 8;
    while (boxes.some(([px, py, ph]) => Math.abs(px - lx) < half + ph && Math.abs(py - ly) < 26)) ly += below ? 26 : -26;
    boxes.push([lx, ly, half]); minY = Math.min(minY, ly - 24); maxY = Math.max(maxY, ly + 6);
    s += `<path d="M${x1} ${y0} Q${lx} ${ctl.toFixed(0)} ${x2} ${y0}" fill="none" stroke="${col}"
      stroke-width="2.5"${good ? "" : ' stroke-dasharray="5 4"'}/>
      <text x="${lx}" y="${ly.toFixed(0)}" text-anchor="middle" font-size="22" font-weight="700" fill="${col}">${text}</text>`;
  });
  order.forEach((k) => { const br = c.pillars[k][1], col = EL_COL[BR_EL[br]], x = xs[k];
    s += `<circle cx="${x}" cy="${NY}" r="${R}" fill="#fff" stroke="${col}" stroke-width="2.5"/>
      <text x="${x}" y="${NY + 9}" text-anchor="middle" font-size="26" font-weight="700" fill="${col}">${br}</text>
      <text x="${x}" y="${NY + 44}" text-anchor="middle" font-size="15" fill="#6b6359">${k}</text>`; });
  const legend = many ? `<div class="ixlegend">${its.map((it) => `${RS("appjs.interactionsSvg.001", {it_kind: it.kind.includes("合") ? "#0e7a6a" : "#99460a", it_kind_2: it.kind, it_pair: it.pair, it_pillars: it.pillars.join("+")})}`).join("")}</div>` : "";
  return `<svg class="ixsvg" viewBox="0 ${minY.toFixed(0)} 640 ${(maxY - minY).toFixed(0)}" role="img" aria-label="${RS("appjs.interactionsSvg.002")}">${s}</svg>${legend}`;
}
function interactionsLine(c) {
  const its = c.interactions || [], n = its.length;
  if (!n) return RS("appjs.interactionsLine.001");
  const seen = new Map();
  its.forEach((it) => { const k = it.kind + "|" + it.pair.split("").sort().join(""); seen.set(k, (seen.get(k) || 0) + 1); });
  const tail = [...seen.entries()].map(([k, cnt]) => { const [kind, pair] = k.split("|");
    const t = kind === "自刑" ? `${RS("appjs.interactionsLine.002", {elc_pair: elc(pair[0])})}` : `${elc(pair[0])} ${GLOSS_IX[kind] || kind} ${elc(pair[1])}`;
    return t + (cnt === 2 ? " twice" : cnt > 2 ? ` ×${cnt}` : ""); });
  const clash = its.some((it) => it.kind.includes("冲"));
  const words = ["", RS("appjs.interactionsLine.003"), RS("appjs.interactionsLine.004"), RS("appjs.interactionsLine.005"), RS("appjs.interactionsLine.006"), RS("appjs.interactionsLine.007"), RS("appjs.interactionsLine.008")];
  const list = tail.length > 1 ? tail.slice(0, -1).join(", ") + " and " + tail[tail.length - 1] : tail[0];
  return `${RS("appjs.interactionsLine.009", {words_n: words[n] || n, n_tension: n === 1 ? "tension" : "tensions", clash_one: clash ? RS("appjs.interactionsLine.010") : RS("appjs.interactionsLine.011"), list: list, clash_watch: clash ? RS("appjs.interactionsLine.012") : RS("appjs.interactionsLine.013")})}`;
}
function eflowsList(c) {
  const er = c.element_relations; if (!er) return "";
  return `<div class="eflows"><div class="cite" style="margin:0 0 6px">${RS("appjs.eflowsList.001", {elb_er: eli(er.dm)})}</div>
    ${["resource", "output", "wealth", "pressure", "peer"].map((k) => { const f = er.flows[k];
      const peerNote = (k === "peer" && !((c.tengods_pct["比肩"] || 0) + (c.tengods_pct["劫財"] || 0)))
        ? ` ${RS("appjs.eflowsList.002")}` : "";
      return `<div class="eflow"><span class="efr">${f.role}</span> ${eli(f.el)} <b>${f.share}%</b>
        <span class="efb ef-${f.band}">${f.band}</span> <span class="sub">${f.meaning}</span>${peerNote}</div>`; }).join("")}</div>`;
}
function supportDrain(c) {
  const pt = c.strength.parts; if (!pt) return "";
  const net = pt.support - pt.drain;
  const wmax = Math.max(...pt.groups.map((g) => g.w), Math.abs(net)) || 1;
  const row = (g) => { const pct = (g.w / wmax * 50).toFixed(1), sup = g.side === "support";
    return `<div class="sbrow"><span class="sbl">${g.zh} <small>${TG_GRP_EN[g.zh] || ""} · ${elc(g.el)}</small></span>
      <div class="sbax"><span class="zero"></span>
        <i style="${sup ? "left:50%" : "right:50%"};width:${pct}%;background:${EL_COL[g.el]}"></i></div>
      <b class="sbv ${sup ? "sup" : "drn"}">${sup ? "+" : "−"}${g.w}</b></div>`; };
  const netPct = (Math.abs(net) / wmax * 50).toFixed(1);
  return `<div class="sbwrap">
    <div class="sbhead">${RS("appjs.supportDrain.001")}</div>
    <div class="sbaxhead">${RS("appjs.supportDrain.002")}</div>
    ${pt.groups.map(row).join("")}
    <div class="sbrow sbnet">${RS("appjs.supportDrain.003")}
      <div class="sbax"><span class="zero"></span>
        <i style="${net >= 0 ? "left:50%" : "right:50%"};width:${netPct}%;background:${net >= 0 ? "#1e7d32" : "#b03a2e"}"></i></div>
      <b class="sbv ${net >= 0 ? "sup" : "drn"}">${net >= 0 ? "+" : "−"}${Math.abs(net).toFixed(2)}</b></div>
    <div class="cite" style="margin-top:5px">${RS("appjs.supportDrain.004", {pt_season_pts: pt.season_pts > 0 ? "+" : "", pt_season_pts_2: pt.season_pts, pt_support: pt.support, pt_drain: pt.drain, pt_total: pt.total, pt_root_pts: pt.root_pts > 0 ? "+" : "", pt_root_pts_2: pt.root_pts, c_strength_score: c.strength.score, c_strength_verdict: c.strength.verdict})}</div></div>`;
}
function tiaohouStrip(c) {
  const t = c.tiaohou; if (!t || !t.gods) return "";
  const chips = t.gods.map((g) => `<span class="thchip">${elc(g.stem)} ${g.god}
    <small>${g.aligned ? RS("appjs.tiaohouStrip.001") : g.visible ? "visible" : RS("appjs.tiaohouStrip.002")}</small></span>`).join(" ");
  return `<div class="tiaohou">${RS("appjs.tiaohouStrip.003", {elc_c: elc(c.pillars.month[1]), chips: chips, t_verdict: t.verdict})}</div>`;
}
function groupSums(c) {
  const p = (k) => c.tengods_pct[k] || c.tengods_pct[TG_CANON[k] || ""] || 0;
  const alt = (k) => p(k) || p(Object.keys(TG_CANON).find((s) => TG_CANON[s] === k) || "");
  return [["官殺", alt("正官") + alt("七殺")], ["印星", alt("正印") + alt("偏印")],
    ["比劫", alt("比肩") + alt("劫財")], ["食傷", alt("食神") + alt("傷官")],
    ["財星", alt("正財") + alt("偏財")]].map(([z, v]) => [z, Math.round(v * 10) / 10]);
}
const isWeak = (c) => /弱|weak/i.test(c.strength.verdict);
const topGod = (c) => Object.entries(c.tengods_pct).sort((a, b) => b[1] - a[1])[0] || ["—", 0];

/* --- 四柱 Pillars ------------------------------------------------------------- */
/* 格局 in plain English, the classical terms in brackets (owner 2026-10-10); falls back to the engine line */
function gejuPlain(g) {
  const m = /月令\s*(\S),\s*本[氣气]\s*(\S)\s*\((\S+?)\)\s*司令\s*·\s*(.*?)[.。](?:\s|$)/.exec(g);
  if (!m) return `${RS("appjs.gejuPlain.001", {g_replace: g.replace(/^格局[:：]\s*/, "").split(/[.。] /)[0]})}`;
  const [, br, st, god, rest] = m, tou = /^(\S+?格)\s*\(月支藏干\s*(\S)\s*透干\)/.exec(rest);
  const lead = `${RS("appjs.gejuPlain.002", {br: br, st: st, god: god})} `;
  return lead + (tou ? `${RS("appjs.gejuPlain.003", {tou: tou[2], god: god, tou_2: tou[1]})}`
    : `${RS("appjs.gejuPlain.004")}`);
}
function buildPillars(c, R) {
  const dm = c.day_master, dmEl = STEM_EL[dm], fav = c.yongshen.favourable, weak = isWeak(c);
  const sp = (c.strength.parts || {}).season_pts || 0;
  const season = sp < 0 ? RS("appjs.buildPillars.001") : sp > 0 ? RS("appjs.buildPillars.002") : RS("appjs.buildPillars.003");
  const p1 = rdFig({ tier: "hero", span: 12, label: RS("appjs.buildPillars.004"), learn: "chart",
    chart: pillarGrid(c),
    line: `${RS("appjs.buildPillars.005", {weak_weak: weak ? "weak" : "strong", elc_dm: elc(dm), elw_dmEl: elw(dmEl), season: season, fav_map: fav.map(elw).join(" and "), fav_length: fav.length > 1 ? "are" : "is"})}`,
    facts: [[c.strength.verdict.split(" ")[0], `${RS("appjs.buildPillars.006", {c_strength_score: c.strength.score})}`]],   // 格局 is explained in plain words under the structure check
    legend: legendList("chart") });
  const its = c.interactions || [], kinds = {};
  its.forEach((it) => (kinds[it.kind] = (kinds[it.kind] || 0) + 1));
  const p6 = rdFig({ tier: "secondary", span: 5, label: RS("appjs.buildPillars.007"), learn: "chart",
    chart: interactionsSvg(c), line: interactionsLine(c),
    facts: [...Object.entries(kinds).map(([k, n]) => [k, `×${n}`]), ...(its.some((i) => i.kind.includes("冲")) ? [] : [["冲", "none"]])],
    legend: `${RS("appjs.buildPillars.008", {its_length: its.length ? "<hr>" + its.map((i) => `<div><b>${i.pair} ${i.kind}</b> (${i.pillars.join("+")}) — ${i.note}</div>`).join("") : ""})}` });
  // Four Palaces retired 2026-10-10: the four sides in the opening carry each palace (owner cut)
  // Which Way to Face retired 2026-10-10: it repeated the Compass 3×3 grid (owner cut)
  let p5 = "";
  if ((c.shensha || []).length) {
    const NEG = ["劫煞", "空亡", "災煞", "亡神", "羊刃", "孤辰", "寡宿"];
    const PZH = { year: "年", month: "月", day: "日", hour: "时" }, PEN = { year: "year", month: "month", day: "day", hour: "hour" };
    const part = (s) => { const [en, ...g] = s.meaning.split(" — "); return [en, (g.join(" — ") || s.meaning).split(";")[0]]; };
    const named = (s) => IS_ZH ? part(s)[0] : `${part(s)[0]} (<span class="keepzh" lang="zh-Hans" data-notip>${s.star}</span>)`;   // English first, the characters beside it
    const chart = `<table class="htable shentable keepzh"><tr><th scope="col"></th><th scope="col">神煞</th><th scope="col">柱</th><th scope="col">吉忌</th></tr>
      ${c.shensha.map((s, i) => { const neg = NEG.includes(s.star); return `<tr><td>${i + 1}</td><td><b class="${neg ? "shen-neg" : "shen-pos"}">${s.star}</b></td>
        <td>${s.pillars.map((p) => PZH[p] || p).join("·")}</td><td>${neg ? "忌" : "吉"}</td></tr>`; }).join("")}</table>
      <ol class="tkey-list">${c.shensha.map((s) => { const [en, gist] = part(s); const neg = NEG.includes(s.star);
        return `<li class="cite">${RS("appjs.buildPillars.010", {en: en, s_star: s.star, s_pillars: s.pillars.map((p) => PEN[p] || p).join(" and "), s_pillars_2: s.pillars.length > 1 ? "s" : "", gist: gist, neg_Asks: neg ? RS("appjs.buildPillars.011") : RS("appjs.buildPillars.012")})}</li>`; }).join("")}</ol>
      <p class="tkey">${RS("appjs.buildPillars.009")}</p>`;
    const pos = c.shensha.find((s) => !NEG.includes(s.star)), neg = c.shensha.find((s) => NEG.includes(s.star));
    const line = (pos ? `${RS("appjs.buildPillars.013", {part_pos: named(pos), part_pos_2: part(pos)[1]})}` : RS("appjs.buildPillars.014"))
      + (neg ? `${RS("appjs.buildPillars.015", {part_neg: named(neg), PEN_neg: PEN[neg.pillars[0]], part_neg_2: part(neg)[1]})}` : RS("appjs.buildPillars.016"));
    p5 = rdFig({ tier: "reference", span: 7, label: RS("appjs.LEGENDS.chart.12.term"), learn: 9, chart, line,
      legend: ("<div>" + RS("appjs.buildPillars.018") + "</div>") });
  }
  return { figs: { grid: p1, interactions: p6, stars: p5 },
    tail: [R.nb.rest.length ? deepWrap(RS("appjs.buildPillars.019"), R.nb.rest.map((t) => `<div class="ninline">${dnAll(t)}</div>`).join("")) : "",
      R.narr(9), deepWrap(RS("appjs.buildPillars.020"),
        c.citations.map((x) => `<div class="cite"><b>[${layerZh(x.layer)}] ${x.source_ref}:</b> ${x.explanation}</div>`).join(""))] };
}

/* --- 五行 Elements ------------------------------------------------------------ */
function buildElements(c, R) {
  const dm = c.day_master, dmEl = STEM_EL[dm], fav = c.yongshen.favourable, unf = c.yongshen.unfavourable;
  const wtot = Object.values(c.element_weights).reduce((x, y) => x + y, 0) || 1;
  // Element bars retired 2026-10-10 (owner cut: the energy budget and the pentagon carry the same numbers);
  // its counting note now sits under the budget as "How these numbers are counted".
  const units = `<div class="cite">${RS("appjs.buildElements.001", {wtot_toFixed: wtot.toFixed(1)})}</div>`;
  const er = c.element_relations; let e2 = "";
  if (er) {
    const pr = er.flows.pressure, rs = er.flows.resource;
    e2 = rdFig({ tier: "hero", span: 5, extra: "rd-pair2", label: RS("appjs.buildElements.002"), learn: 1,
      chart: `<div class="ewrap"><div class="svg-plate">${elementWheel(er)}</div></div>`,
      line: `${RS("appjs.buildElements.003", {elb_pr: eli(pr.el, { silent: true }), elw_pr: elw(pr.el), pr_share: pr.share, elb_rs: eli(rs.el, { silent: true }), elw_rs: elw(rs.el), pr_share_2: pr.share > rs.share ? "only " : "", rs_share: rs.share, pr_share_3: pr.share > rs.share ? RS("appjs.buildElements.004") : RS("appjs.buildElements.005")})}`,
      facts: [[RS("appjs.buildElements.006"), `${elc(pr.el)} ${pr.share}%`], [RS("appjs.buildElements.007"), `${elc(rs.el)} ${rs.share}%`]],
      legend: `${RS("appjs.buildElements.008", {eflowsList_c: eflowsList(c)})}` });
  }
  const st = c.strength, pt = st.parts || {}, sp = pt.season_pts || 0, weak = isWeak(c);
  const stage = (c.pillar_extras.month || {}).stage;
  const topSup = (pt.groups || []).filter((g) => g.side === "support").sort((a, b) => b.w - a.w)[0];
  const e45 = rdFig({ tier: "secondary", span: 5, label: RS("appjs.buildElements.009"), learn: 2,
    chart: `<div class="svg-plate">${strengthGauge(st)}</div>
      <p class="rd-tags">${RS("appjs.buildElements.010", {st_support_ratio: st.support_ratio, st_root_ratio: st.root_ratio, st_formation_status: st.formation.status})}</p>
      ${supportDrain(c)}${tiaohouStrip(c)}`,
    line: `${RS("appjs.buildElements.011", {weak_Weak: weak ? "Weak" : "Strong", st_score: st.score, sp_the: sp < 0 ? RS("appjs.buildElements.014") : sp > 0 ? RS("appjs.buildElements.015") : RS("appjs.buildElements.016"), stage_stage: stage ? ` (${stage})` : ""})}`,
    line2: topSup ? `${RS("appjs.buildElements.017", {elb_topSup: eli(topSup.el, { silent: true }), topSup_zh: topSup.zh, elw_topSup: elw(topSup.el), topSup_w: topSup.w, pt_support: pt.support, pt_support_2: pt.support > pt.drain ? "beats" : "trails", pt_drain: pt.drain, weak_pt: weak && pt.support > pt.drain ? RS("appjs.buildElements.018") : !weak && pt.support < pt.drain ? RS("appjs.buildElements.019") : RS("appjs.buildElements.020")})}` : "",
    facts: [[st.verdict.split(" ")[0], `${st.score}`], [RS("appjs.buildElements.021"), `${pt.support}`], [RS("appjs.buildElements.022"), `${pt.drain}`],
      c.tiaohou ? [RS("appjs.LEGENDS.5.04.term"), c.tiaohou.verdict] : null].filter(Boolean),
    legend: `<div class="cite">${RS("appjs.buildElements.024", {st_formation_detail: st.formation.detail})}</div>
      ${(st.steps || []).map((s) => `<div class="cite"><b>${s.step}. ${s.name}:</b> ${s.value} — ${s.detail}</div>`).join("")}${legendList(2)}
      ${c.tiaohou && c.tiaohou.line ? `<div class="cite">${c.tiaohou.line} <span class="tag">${c.tiaohou.source_ref}</span></div>` : ""}` });
  const H = c.health || [];
  const stZh = (s) => (s.match(/[㐀-鿿]+/) || [s.startsWith("balanced") ? "平" : s])[0];
  const table = `<div class="scrollx keepzh"><table class="htable hltable"><tr><th scope="col">五行</th><th scope="col">脏腑</th><th scope="col">状态</th><th scope="col">%</th></tr>
    ${H.map((h) => `<tr><td>${eli(h.element)}</td><td>${ORGAN_ZH[h.element] || ""}</td>
      <td class="${h.status.startsWith("balanced") ? "" : "bad"}">${stZh(h.status)}</td><td>${h.share}</td></tr>`).join("")}</table></div>
    ${zhKey([["五行", "element"], ["脏腑", RS("appjs.buildElements.025")], ["状态", "status"], ["过旺", RS("appjs.buildElements.026")], ["不足", RS("appjs.buildElements.027")], ["平", "balanced"]])}
    <ul class="tkey-list">${H.map((h) => `<li>${RS("appjs.buildElements.028", {h_en: h.en, h_element: h.element, h_organs: h.organs, h_aspects: h.aspects})}</li>`).join("")}</ul>`;
  const excess = H.find((h) => /excess|過旺|过旺/i.test(h.status)), weakEl = H.find((h) => /weak|不足/i.test(h.status));
  const hline = excess ? `${RS("appjs.buildElements.029", {elb_excess: eli(excess.element, { silent: true }), elw_excess: elw(excess.element), excess_share: excess.share, excess_organs: excess.organs, excess_aspects: (excess.aspects.split(";").pop() || "").trim()})}`
    : weakEl ? `${RS("appjs.buildElements.030", {elb_weakEl: eli(weakEl.element, { silent: true }), elw_weakEl: elw(weakEl.element), weakEl_share: weakEl.share, weakEl_organs: weakEl.organs, weakEl_aspects: weakEl.aspects})}`
    : RS("appjs.buildElements.031");
  const h1 = rdFig({ tier: "secondary", span: 7, label: RS("appjs.buildElements.032"), learn: 11, chart: table, line: hline,
    facts: [[RS("appjs.buildElements.033"), H.filter((h) => /excess|過旺|过旺/i.test(h.status)).map((h) => elc(h.element)).join("·") || "—"],
      [RS("appjs.buildElements.034"), H.filter((h) => /weak|不足/i.test(h.status)).map((h) => elc(h.element)).join("·") || "—"]],
    legend: legendList(11) });
  return { figs: { pentagon: e2, gauge: e45, health: h1 }, units,
    tail: [R.narr(1), R.narr(2), R.stb(2), R.narr(11), R.stb(11)] };
}

/* --- 十神 Gods -------------------------------------------------------------- */
function buildGods(c, R) {
  const dm = c.day_master, en = (g) => (c.tengods_legend[g] || {}).en || TG_EN_FALLBACK[g] || "";
  const gs = groupSums(c).sort((a, b) => b[1] - a[1]);
  const g2 = rdFig({ tier: "hero", span: 5, label: RS("appjs.buildGods.001"), learn: 4,
    chart: `<div class="tgwrap svg-plate">${tenGodsWheel(c, { groupsOnly: true, zh: true })}</div>`,
    line: `${RS("appjs.buildGods.002", {gs: gs[0][0], GRP_EN_gs: GRP_EN[gs[0][0]], gs_2: gs[0][1], gs_3: gs[1][0], GRP_EN_gs_2: GRP_EN[gs[1][0]], gs_gs: gs[0][1] - gs[1][1] < 12 ? RS("appjs.buildGods.003") : "behind", gs_4: gs[1][1]})}`,
    facts: gs.slice(0, 2).map(([z, v]) => [z, `${v}%`]),
    legend: `<div>${RS("appjs.buildGods.004")}</div>
      ${WHEEL_KEY.map(([zh, name, a, b]) => `<div>${RS("appjs.buildGods.006", {zh: zh, name: name, en_a: en(a), a: a, en_b: en(b), b: b})}</div>`).join("")}
      <div>${RS("appjs.buildGods.005")}</div>${legendList(4)}` });
  const rows = ALLGODS.map((g) => [g, c.tengods_pct[g] || 0]), pmax = Math.max(...rows.map(([, v]) => v)) || 1;
  const [g1, p1] = topGod(c), absent = ALLGODS.filter((g) => !(c.tengods_pct[g] > 0));
  const bars = `<div class="bars tgbars">${rows.map(([g, p]) => `<div class="bar-row tg-row2${p ? "" : " tg-zero"}">
      <span><b style="color:${EL_TXT[godEl(dm, g)]}">${en(g)}</b> <span class="sub keepzh">(${g})</span></span>
      <div class="bar">${p ? `<i style="width:${(p / pmax * 100).toFixed(0)}%;background:${EL_COL[godEl(dm, g)]}"></i>` : ""}</div>
      <b>${p ? p + "%" : RS("appjs.buildGods.007")}</b></div>`).join("")}</div>`;
  const sex = c.sex, grp = (gods) => Math.round(gods.reduce((a, g) => a + (c.tengods_pct[g] || 0), 0) * 10) / 10;
  const band = (p) => p >= 20 ? "prominent" : p >= 8 ? "present" : p > 0 ? "faint" : "absent";
  const starRows = [[RS("appjs.buildGods.008"), sex === "M" ? "正財+偏財" : "正官+七殺", sex === "M" ? ["正財", "偏財"] : ["正官", "七殺"]],
    [RS("appjs.buildGods.009"), "正財+偏財", ["正財", "偏財"]], [RS("appjs.buildGods.010"), "正官+七殺", ["正官", "七殺"]],
    [RS("appjs.buildGods.011"), "正印+偏印", ["正印", "偏印"]], [RS("appjs.buildGods.012"), "食神+傷官", ["食神", "傷官"]],
    [RS("appjs.buildGods.013"), "比肩+劫財", ["比肩", "劫財"]]];
  const g1f = rdFig({ tier: "hero", span: 7, extra: "rd-pair2", label: RS("appjs.buildGods.014"), learn: 4, chart: bars,
    line: `${RS("appjs.buildGods.015", {godc_dm: godc(dm, g1), en_g1: en(g1), Math_round: Math.round(p1), c_tengods_legend: (c.tengods_legend[g1] || {}).meaning || GRP_THEME[grpOfGod(g1)]})}`,
    facts: [[g1, `${p1}%`], ["absent", `${RS("appjs.buildGods.016", {absent_length: absent.length})}`]],
    legend: `<div>${RS("appjs.buildGods.017")}</div>
      <div>${RS("appjs.buildGods.018")}</div>
      <div class="tgkey2">${ALLGODS.map((g) => `<div><b style="color:${EL_TXT[godEl(dm, g)]}">${en(g)}</b> <span class="keepzh">(${g})</span>: ${TG_GIST[g] || ""}</div>`).join("")}</div>
      <table class="tgsides keepzh"><tr><th scope="col">星</th><th scope="col">十神</th><th scope="col">%</th></tr>${starRows.map(([t, d, gods]) => { const p = grp(gods);
        return `<tr><td><b>${STAR_GROUP_ZH[t] || t}</b></td><td>${d}</td><td>${p}</td></tr>`; }).join("")}</table>
      ${zhKey(starRows.map(([t]) => [STAR_GROUP_ZH[t] || t, t.toLowerCase()]))}` });
  const axes = c.personality || [];
  const pax = `<div class="paxchips">${axes.map((a) => { if (!a.zone) return `<div class="pax"><b>${a.axis}</b> ${a.verdict}<div class="sub">${a.basis}</div></div>`;
    const pos = a.zone === "left" ? 16 : a.zone === "right" ? 84 : 50;
    return `<div class="pax"><b>${a.axis}</b><div class="paxv ${a.zone}">${a.verdict}</div>
      <div class="paxstrip"><span class="pz l"></span><span class="pz m"></span><span class="pz r"></span><i style="left:${pos}%"></i></div>
      <div class="paxends">${RS("appjs.buildGods.019", {a_poles_left_zh: a.poles.left.zh, a_poles_left_en: IS_ZH ? "" : a.poles.left.en, a_poles_right_zh: a.poles.right.zh, a_poles_right_en: IS_ZH ? "" : a.poles.right.en})}</div>
      <div class="paxm">${a.metrics.map((m) => `<span>${m.label} <b>${m.pct}%</b></span>`).join("")}</div><div class="sub">${a.basis}</div></div>`; }).join("")}</div>`;
  const sharp = axes.filter((a) => a.zone && a.zone !== "mid" && a.metrics && a.metrics.length)
    .sort((a, b) => Math.max(...b.metrics.map((m) => m.pct)) - Math.max(...a.metrics.map((m) => m.pct)))[0];
  const g8 = rdFig({ tier: "secondary", span: 6, label: RS("appjs.buildGods.020"), learn: 10, chart: pax,
    line: sharp ? `${RS("appjs.buildGods.021", {sharp_verdict: sharp.verdict.charAt(0).toUpperCase() + sharp.verdict.slice(1), sharp_metrics: sharp.metrics[0].label, sharp_metrics_2: sharp.metrics[0].pct})}`
      : RS("appjs.buildGods.022"),
    facts: axes.filter((a) => a.zone && a.zone !== "mid").slice(0, 2).map((a) => [a.axis.split(" ")[0], a.verdict.split(" — ")[0]]),
    legend: legendList(10) });
  const ti = c.tengod_insights; let g5 = "";
  if (ti) {
    const geju = c.geju ? `<div class="geju">${gejuPlain(c.geju)}</div>` : "";
    const chart = geju + ti.favor.map((f) => `<div class="cite structrow"><b>${f.god} ${f.pct}%</b> ${eli(f.el)}
        <span class="dirchip ${f.status === "favourable" ? "good" : f.status === "unfavourable" ? "bad" : ""}">${f.status === "favourable" ? RS("appjs.buildGods.favourable") : f.status === "unfavourable" ? RS("appjs.buildGods.unfavourable") : f.status}</span> — ${f.note}</div>`).join("")
      + `<div class="cite" style="margin-top:6px">${RS("appjs.buildGods.023", {ti_rooted: ti.rooted.map((r) => `<span class="dirchip ${r.state === "rooted" ? "good" : "bad"}">${r.god} ${r.state === "rooted" ? RS("appjs.buildGods.rooted") : RS("appjs.buildGods.floating")}</span>`).join(" ")})}</div>`
      + (ti.patterns.length ? `<details class="deep pairpat"><summary>${RS("appjs.buildGods.024", {ti_patterns_length: ti.patterns.length})}</summary><div class="deepbody">${ti.patterns.map((p) => `<div class="ninline"><b>${p.name} — ${p.zh}</b> ${p.state ? `<span class="dirchip ${/^(formed|已成)/.test(p.state) ? "good" : ""}">${p.state}</span>` : ""}<div>${p.note}${p.activation ? ` <b>${p.activation}${IS_ZH ? "。" : "."}</b>` : ""}</div></div>`).join("")}</div></details>`
        : `<div class="cite">${RS("appjs.buildGods.025")}</div>`);
    const bad = ti.favor.find((f) => f.status === "unfavourable"), good = ti.favor.find((f) => f.status === "favourable");
    g5 = rdFig({ tier: "secondary", span: 6, label: RS("appjs.buildGods.026"), learn: 4, chart,
      line: bad ? `${RS("appjs.buildGods.027", {godc_dm: godc(dm, bad.god), bad_pct: bad.pct, elc_bad: elc(bad.el)})}`
        : good ? `${RS("appjs.buildGods.028", {godc_dm: godc(dm, good.god), good_pct: good.pct, elc_good: elc(good.el)})}`
        : RS("appjs.buildGods.029"),
      facts: [["favourable", `${RS("appjs.buildGods.030", {ti_favor: ti.favor.filter((f) => f.status === "favourable").length, ti_favor_length: ti.favor.length})}`],
        ["rooted", `${RS("appjs.buildGods.031", {ti_rooted: ti.rooted.filter((r) => r.state === "rooted").length})}`]],
      legend: `<div>${RS("appjs.buildGods.032")}</div>` });
  }
  const P = c.palaces; let ld = "";
  if (P && c.domains) {
    const g = (...n) => Math.round(n.reduce((a, k) => a + (c.tengods_pct[k] || 0), 0) * 10) / 10;
    const inPal = (keys, groups) => keys.some((k) => { const p = P.pillars.find((x) => x.key === k);
      return p && [p.stem_god, ...(p.hidden || [])].some((gd) => groups.includes(tgCanon(gd))); });
    const sig = { 事业官星: ["正官·七殺", g("正官", "七殺", "七杀"), ["month"], ["正官", "七殺"], RS("appjs.buildGods.033")],
      财富财库: ["正財·偏財", g("正財", "正财", "偏財", "偏财"), ["month", "day"], ["正財", "偏財"], RS("appjs.buildGods.034")],
      学习文昌: ["正印·偏印", g("正印", "偏印"), ["year", "month"], ["正印", "偏印"], RS("appjs.buildGods.035")],
      感情稳定: [sex === "M" ? RS("appjs.buildGods.036") : RS("appjs.buildGods.037"), sex === "M" ? g("正財", "正财", "偏財", "偏财") : g("正官", "七殺", "七杀"), ["day"], sex === "M" ? ["正財", "偏財"] : ["正官", "七殺"], RS("appjs.buildGods.038")] };
    const extra = [[RS("appjs.buildGods.039"), "食神·傷官", g("食神", "傷官", "伤官"), ["hour"], ["食神", "傷官"], RS("appjs.buildGods.040")],
      [RS("appjs.buildGods.041"), "比肩·劫財", g("比肩", "劫財", "劫财"), ["year", "month"], ["比肩", "劫財"], RS("appjs.buildGods.035")]];
    const chip = (e) => `<span class="tag${e.delta < 0 ? " warn" : ""}">${e.label} ${e.delta > 0 ? "+" : ""}${e.delta}</span>`;
    const row = (zh, enTxt, score, band, s, ev, pct) => { const cls = score == null ? "" : score >= 70 ? "good" : score < 45 ? "weak" : "";
      const sc = score == null ? '<span class="sub">·</span>' : `<b class="dnum ${cls === "good" ? "b-good" : cls === "weak" ? "b-weak" : ""}">${score}</b><div class="dbar"><i class="${cls}" style="width:${score}%"></i></div>${pct == null ? "" : `<small class="ldst">${RS("appjs.buildGods.061", {p: pct})}</small>`}`;
      return `<tr><td><b>${zh}</b></td><td class="ldscore">${sc}</td>
        <td>${s ? `${s[0].replace(/\s*\(.*\)$/, "")}<small class="ldpct">${s[1]}%</small>` : "·"}</td><td class="seat">${s ? (inPal(s[2], s[3]) ? "✓" : "·") : "·"}</td></tr>`; };
    const doms = c.domains.slice().sort((a, b) => b.score - a.score);
    const table = `<div class="scrollx keepzh"><table class="bc-table ldtable"><tr><th scope="col">领域</th><th scope="col">分</th><th scope="col">十神</th><th scope="col">得位</th></tr>
      ${doms.map((d) => row(d.zh, d.en, d.score, d.band, sig[d.zh], d.evidence, d.percentile)).join("")}
      ${extra.map(([n, sg, sh, keys, groups, pal]) => row(n.split(" ")[0], n.split(" ").slice(1).join(" "), null, null, [sg, sh, keys, groups, pal], [])).join("")}</table></div>
      <ol class="tkey-list">${doms.map((d) => `<li class="cite"><b>${d.en}</b> (<span class="keepzh">${d.zh}</span>), ${d.score}, ${d.band.replace(/\s+[㐀-鿿]+$/, "")}: ${d.evidence.map((e) => `${e.label} ${e.delta > 0 ? "+" : ""}${e.delta}`).join("; ")}.</li>`).join("")}
        ${extra.map(([n]) => `<li>${RS("appjs.buildGods.044", {n_split: n.split(" ").slice(1).join(" "), n_split_2: n.split(" ")[0]})}</li>`).join("")}</ol>
      <p class="tkey">${RS("appjs.buildGods.043")}</p>`;
    const top = c.domains.slice().sort((a, b) => ((b.percentile ?? b.score) - (a.percentile ?? a.score)) || (b.score - a.score))[0];   // Layer 2: "highest" is by standing among charts
    const sigs = [...Object.entries(sig).map(([k, v]) => [k, v]), ...extra.map((e) => [e[0], [e[1], e[2], e[3], e[4], e[5]]])];
    const heavy = sigs.sort((a, b) => b[1][1] - a[1][1])[0];
    const heavyName = (c.domains.find((d) => d.zh === heavy[0]) || {}).en || heavy[0].replace(/^\S+\s/, "").replace("&amp;", "&");
    ld = rdFig({ tier: "secondary", span: 12, label: RS("appjs.buildGods.045"), learn: 8, chart: table,
      line: `${RS("appjs.buildGods.046", {top_en: top.en, top_score: top.score, heavyName_toLowerCase: heavyName.toLowerCase(), heavy: heavy[1][1], inPal_heavy: inPal(heavy[1][2], heavy[1][3]) ? RS("appjs.buildGods.047") : "from", heavy_2: heavy[1][4]})}`,

      legend: `<div>${RS("appjs.buildGods.048")}</div>
        ${c.domains[0] && c.domains[0].percentile != null ? `<div>${RS("appjs.buildGods.060", {v: c.domains[0].reference_version})}</div>` : ""}
        ${c.spouse_reading ? `<div class="cite">${RS("appjs.buildGods.049", {c_spouse_reading_star_li: c.spouse_reading.star_line, c_spouse_reading_palace_: c.spouse_reading.palace_line})}</div>` : ""}` });
  }
  // raw pillar data (G7) retired 2026-09-27: the Pillars grid carries every stem/hidden stem; its key lives in the bars' legend. Gods = 7 figures.
  let k1 = "", k3 = "";
  if (c.industries) {
    // one figure for work (owner 2026-10-10): best fields with their reasons, roles that fit now, harder going; each reason once
    const F = c.industries.favourable || [], A = c.industries.avoid || [], C = c.careers || {}, T = (C.top || []).slice(0, 3);
    const Rl = ((c.career_roles || {}).top || []).slice(0, 6), AV = C.avoid || [];
    const chart = `<div class="wkfig">
      <h5>${RS("appjs.buildGods.050")}</h5><ol class="wk-top">${T.map((x) => `<li><b>${x.en}</b> <span class="sub">${x.score} pts</span><span class="wk-why">${x.reasons.join("; ")}</span></li>`).join("")}</ol>
      ${F.length ? `<p class="wk-ind">${RS("appjs.buildGods.051")}</p>${F.map((it) => `<div class="cite wk-indrow">${eli(it.element)} ${it.industries}</div>`).join("")}` : ""}
      ${Rl.length ? `<h5>${RS("appjs.buildGods.052")}</h5><ul class="wk-roles">${Rl.map((x) => `<li>${x.role} <span class="sub">${x.score}</span></li>`).join("")}</ul>` : ""}
      ${AV.length || A.length ? `<h5>${RS("appjs.buildGods.053")}</h5><ul class="wk-av">${AV.map((x) => `<li><b>${x.en}</b>: ${x.reasons.join("; ")}</li>`).join("")}
        ${A.length ? `<li class="cite">${RS("appjs.buildGods.054", {A_map: A.map((it) => `${eli(it.element)} ${it.industries.split(",").slice(0, 3).join(",")}`).join("; ")})}</li>` : ""}</ul>` : ""}</div>`;
    k1 = rdFig({ tier: "reference", span: 12, label: RS("appjs.buildGods.055"), learn: 12, chart,
      line: T[0] ? `${RS("appjs.buildGods.056", {T_en: T[0].en, Rl_the: Rl[0] ? `${RS("appjs.buildGods.057", {Rl_role: Rl[0].role.toLowerCase()})}` : ""})}` : RS("appjs.buildGods.058"),
      legend: `<div>${RS("appjs.buildGods.059")}</div>` });
  }
  return { figs: { wheel: g2, bars: g1f, axes: g8, structure: g5, domains: ld, industries: k1, roles: k3 },
    tail: [R.narr(4), R.narr(3), R.stb(10), R.narr(10), R.stb(8), R.narr(8), R.stb(12), R.narr(12)] };
}

/* --- 时运 Timing ---------------------------------------------------------------- */
function buildTiming(c, R) {
  const W = c.windows; if (!W) return { figs: {}, tail: [R.narr(6), R.narr(13)] };
  const dd = c.dayun_detail || [], dm = c.day_master;
  // owner 2026-10-10: the classical strip in characters only, element-coloured; English lives in the "?" key
  const gzc = (gz) => `<span style="color:${EL_TXT[STEM_EL[gz[0]]]}">${gz[0]}</span><span style="color:${EL_TXT[BR_EL[gz[1]]]}">${gz[1]}</span>`;
  const godz = (g) => g ? `<span style="color:${EL_TXT[godEl(dm, tgCanon(g))]}">${g}</span>` : "";
  const strip = `<div class="ccdayun keepzh">${W.decades.map((d) => { const x = dd.find((y) => y.gz === d.gz) || {};
    return `<div class="ccdy${d.current ? " now" : ""}" title="${(d.notes || []).join("; ")}">
      <div class="ccdyage">${d.ages}</div><div class="ccdygz">${gzc(d.gz)}</div>
      <div class="wphase w-${d.phase}">${d.phase_zh}</div>
      <div class="dygods">${godz(x.stem_god)}${x.stem_god ? "·" : ""}${godz(x.branch_god)}</div>
      ${x.keywords ? `<div class="dykw">${x.keywords}</div>` : ""}${d.current ? `<div class="ccdyhere">${RS("appjs.buildTiming.001")}</div>` : ""}</div>`; }).join("")}</div>`;
  const gods = [...new Set(dd.flatMap((x) => [x.stem_god, x.branch_god]).filter(Boolean))];
  const phases = [...new Map(W.decades.map((d) => [d.phase, d.phase_zh])).entries()];
  const stripKey = `<div class="tkey"><p>${RS("appjs.buildTiming.002")}</p>
    <p>${RS("appjs.buildTiming.003", {phases_map: phases.map(([en, zh]) => `<span class="keepzh">${zh}</span> ${PHASE_EN[en] || en}`).join(" · ")})}</p>
    <p>${RS("appjs.buildTiming.004", {W_decades: W.decades.map((d) => `${RS("appjs.buildTiming.006", {gzc_d: gzc(d.gz), STEM_YANG_d: STEM_YANG[d.gz[0]] ? "yang" : "yin", EL_EN_STEM_EL: EL_EN[STEM_EL[d.gz[0]]], ZODIAC_BR_ANIMAL: (ZODIAC[BR_ANIMAL[d.gz[1]]] || ["", d.gz[1]])[1], EL_EN_BR_EL: EL_EN[BR_EL[d.gz[1]]]})}`).join("; ")})}</p>
    <p>${RS("appjs.buildTiming.005", {gods_map: gods.map((g) => `<span class="keepzh">${godz(g)}</span> ${TG_EN_FALLBACK[tgCanon(g)] || TG_EN_FALLBACK[g] || ""}`).join(" · ")})}</p></div>`;
  const ci = W.decades.findIndex((d) => d.current), cur = W.decades[ci], nxt = W.decades[ci + 1];
  const arc = ((W.arc || "").match(/(?:Element arc: |五行走势：)(.*?)(?: —|……)/) || [])[1];
  const t1 = rdFig({ tier: "hero", span: 12, label: RS("appjs.buildTiming.007"), learn: 6, chart: strip,
    line: cur ? `${RS("appjs.buildTiming.008", {cur_gz: cur.gz, cur_ages: cur.ages, cur_phase: cur.phase, nxt_shifts: nxt ? `${RS("appjs.buildTiming.009", {nxt_gz: nxt.gz, nxt_phase: nxt.phase, String_nxt: String(nxt.ages).split(/[–-]/)[0]})}` : RS("appjs.buildTiming.010")})}`
      : `${RS("appjs.buildTiming.011", {W_decades: W.decades[0] ? `${RS("appjs.buildTiming.012", {W_decades: W.decades[0].gz, String_W: String(W.decades[0].ages).split(/[–-]/)[0]})}` : ""})}`,
    facts: [cur ? [RS("appjs.buildTiming.013"), `${cur.gz} · ${cur.ages}`] : null, nxt ? ["next", `${nxt.gz} · ${nxt.ages}`] : null,
      c.dayun && c.dayun[0] ? [RS("appjs.buildTiming.014"), `${String(c.dayun[0].ages).split(/[–-]/)[0]}`] : null, arc ? ["arc", arc] : null].filter(Boolean),
    legend: `${stripKey}${legendList(6)}${W.arc ? `<div class="cite">${RS("appjs.buildTiming.015", {W_arc: W.arc})}</div>` : ""}
      ${W.taohua ? `<div class="cite">${RS("appjs.buildTiming.016", {W_taohua_branch: W.taohua.branch, W_taohua_type: W.taohua.type, W_taohua: W.taohua.pillars.length ? ` ${RS("appjs.buildTiming.017", {W_taohua: W.taohua.pillars.join("/")})}` : ""})}</div>` : ""}` });
  const T = c.transit || {}, L = T.luck || {};
  const gDec = [grpOfGod(L.stem_god || ""), grpOfGod(L.branch_god || "")], gYr = [grpOfGod(T.year_stem_god || ""), grpOfGod(T.year_branch_god || "")];
  const theme = (pair) => pair[0] === pair[1] ? GRP_THEME[pair[0]] : `${RS("appjs.buildTiming.018", {GRP_THEME_pair: GRP_THEME[pair[0]], GRP_THEME_pair_2: GRP_THEME[pair[1]]})}`;
  const p8 = rdFig({ tier: "secondary", span: 5, label: RS("appjs.buildTiming.019"), learn: 13,
    chart: `<div class="pillar-cards"><div class="pillar-card transit"><div class="gz">${T.year_gz}</div><div class="pos">${RS("appjs.buildTiming.020", {state_year: state.year})}</div>
        <div class="god">${T.year_stem_god}/${T.year_branch_god}</div><div class="sub">${RS("appjs.buildTiming.021")}</div></div>
      ${L.gz ? `<div class="pillar-chip">${RS("appjs.buildTiming.022", {L_gz: L.gz, L_ages: L.ages, L_stem_god: L.stem_god, L_branch_god: L.branch_god})}</div>` : ""}</div>`,
    line: `${RS("appjs.buildTiming.023", {L_gz: L.gz ? `${RS("appjs.buildTiming.024", {gDec_gDec: gDec[0] === gDec[1] ? RS("appjs.buildTiming.025") : "mixes", theme_gDec: theme(gDec)})}` : RS("appjs.buildTiming.026"), theme_gYr: theme(gYr)})}`,
    facts: [L.gz ? [RS("appjs.buildTiming.027"), `${RS("appjs.buildTiming.028", {L_ages: L.ages})}`] : null, [RS("appjs.buildTiming.029"), `${state.year}`]].filter(Boolean),
    legend: RS("appjs.buildTiming.030") });
  const RH = ((c.strategy || {}).s5 || {}).rhythm; let t6 = "";
  if (RH && RH.length) {
    const nowBr = (c.daily || {}).now_month_branch;
    const cells = RH.map((r) => `<div class="rcell ${r.cls}${r.br === nowBr ? " now" : ""}"><small>${r.mon}</small><b style="color:${EL_TXT[r.el]}">${r.br}</b><span class="rel" style="color:${EL_TXT[r.el]}">${r.el}</span><span class="rrate">${r.cls === "good" ? "good" : "pace"}</span>${r.br === nowBr ? `${RS("appjs.buildTiming.031")}` : ""}</div>`).join("");
    const order = RH.map((r) => r.mon), ranges = (ms) => { const idx = ms.map((m) => order.indexOf(m)).sort((a, b) => a - b), out = []; let i = 0;
      while (i < idx.length) { let j = i; while (j + 1 < idx.length && idx[j + 1] === idx[j] + 1) j++;
        out.push(i === j ? order[idx[i]] : `${order[idx[i]]}–${order[idx[j]]}`); i = j + 1; } return out.join(", "); };
    const good = RH.filter((r) => r.cls === "good"), bad = RH.filter((r) => r.cls !== "good");
    const gel = [...new Set(good.map((r) => r.el))].map(elw).join(" and ");
    t6 = rdFig({ tier: "secondary", span: 7, label: RS("appjs.buildTiming.032"), learn: 13, chart: `<div class="rhy keepzh">${cells}</div>`,
      line: good.length ? `${RS("appjs.buildTiming.033", {ranges_good: ranges(good.map((r) => r.mon)), gel: gel, ranges_bad: ranges(bad.map((r) => r.mon))})}` : RS("appjs.buildTiming.034"),
      facts: [["good", `${good.length}`], ["pace", `${bad.length}`]],
      legend: RS("appjs.buildTiming.035") });
  }
  const daily = dailyFig(c);
  return { figs: { strip: t1, thisyear: p8, rhythm: t6, daily }, tail: [R.stb(13), R.narr(13), R.narr(6)] };
}

/* 流日 daily fortune — the next 30 days, six activities, from the engine's daily layer */
/* tables in characters, translations in a key below (owner 2026-10-10: ready for other languages) */
const DIR_WORD_EN = { N: RS("appjs.DIR_WORD_EN.N"), S: RS("appjs.DIR_WORD_EN.S"), E: RS("appjs.DIR_WORD_EN.E"), W: RS("appjs.DIR_WORD_EN.W"), NE: RS("appjs.DIR_WORD_EN.NE"), NW: RS("appjs.DIR_WORD_EN.NW"), SE: RS("appjs.DIR_WORD_EN.SE"), SW: RS("appjs.DIR_WORD_EN.SW") };
const DIR_ZH = { N: "北", S: "南", E: "东", W: "西", NE: "东北", NW: "西北", SE: "东南", SW: "西南" };
const ORGAN_ZH = { 木: "肝胆", 火: "心·小肠", 土: "脾胃", 金: "肺·大肠", 水: "肾·膀胱" };
const zhKey = (pairs) => `<p class="tkey">${RS("appjs.zhKey.001", {pairs_map: pairs.map(([zh, en]) => (IS_ZH && (!en || en === zh || /^[\x20-\x7e]+$/.test(en)) ? `<span class="keepzh">${zh}</span>` : `<span class="keepzh">${zh}</span> ${en}`)).join(" · ")})}</p>`;
const OFFICER_EN = { 建: RS("appjs.OFFICER_EN.建"), 除: RS("appjs.OFFICER_EN.除"), 满: RS("appjs.OFFICER_EN.满"), 滿: RS("appjs.OFFICER_EN.满"), 平: RS("appjs.OFFICER_EN.平"), 定: RS("appjs.OFFICER_EN.定"), 执: RS("appjs.OFFICER_EN.执"), 執: RS("appjs.OFFICER_EN.执"), 破: RS("appjs.OFFICER_EN.破"),
  危: RS("appjs.OFFICER_EN.危"), 成: RS("appjs.OFFICER_EN.成"), 收: RS("appjs.OFFICER_EN.收"), 开: RS("appjs.OFFICER_EN.开"), 開: RS("appjs.OFFICER_EN.开"), 闭: RS("appjs.OFFICER_EN.闭"), 閉: RS("appjs.OFFICER_EN.闭") };
const TAG_EN = { 合日支: RS("appjs.TAG_EN.合日支"), 冲日支: RS("appjs.TAG_EN.冲日支"), 沖日支: RS("appjs.TAG_EN.冲日支"), 害日支: RS("appjs.TAG_EN.害日支"),
  冲生肖: RS("appjs.TAG_EN.冲生肖"), 沖生肖: RS("appjs.TAG_EN.冲生肖"), 刑日支: RS("appjs.TAG_EN.刑日支") };
const PHASE_EN = { growth: RS("appjs.PHASE_EN.growth"), consolidation: RS("appjs.PHASE_EN.consolidation"), transition: RS("appjs.PHASE_EN.transition"), corrective: RS("appjs.PHASE_EN.corrective") };
const ACT_EN = { moving: RS("appjs.ACT_EN.moving"), signing: RS("appjs.ACT_EN.signing"), marriage: RS("appjs.ACT_EN.marriage"), travel: RS("appjs.ACT_EN.travel"), medical: RS("appjs.ACT_EN.medical"), launch: RS("appjs.ACT_EN.launch") };
function dailyFig(c) {
  const D = c.daily; if (!D || !(D.rows || []).length) return "";
  const dm = c.day_master, acts = D.activities || [];
  const mark = (f) => f.verdict === "good" ? "◉" : f.verdict === "avoid" ? "⚠" : "·";
  const rows = D.rows.map((r) => `<tr class="${r.today ? "today" : ""}${r.officer === "破" || r.interactions.some((x) => x.startsWith("沖")) ? " dclash" : ""}">
      <th>${r.date.slice(5)} <small>${r.weekday}</small>${r.today ? RS("appjs.buildTiming.031") : ""}</th>
      <td><b class="dgz"><span style="color:${EL_TXT[STEM_EL[r.gz[0]]]}">${r.gz[0]}</span><span style="color:${EL_TXT[BR_EL[r.gz[1]]]}">${r.gz[1]}</span></b> <small class="sub">${r.officer}</small></td>
      <td class="sub"><span style="color:${EL_TXT[godEl(dm, tgCanon(r.stem_god))]}">${r.stem_god}</span>·<span style="color:${EL_TXT[godEl(dm, tgCanon(r.branch_god))]}">${r.branch_god}</span>${r.interactions.length ? ` <span class="tag${r.interactions.some((x) => x.startsWith("沖") || x.startsWith("害")) ? " warn" : ""}">${r.interactions.join(" ")}</span>` : ""}</td>
      <td><b style="color:${EL_TXT[r.element]}">${r.element}</b><small class="sub">${r.medicine === "favourable" ? "用" : r.medicine === "against" ? "忌" : ""}</small></td>
      ${acts.map(([k]) => { const f = r.flags[k]; return `<td class="wf-${f.verdict === "good" ? "window" : f.verdict === "avoid" ? "caution" : "quiet"}" title="${f.why}"><b>${mark(f)}</b>${f.verdict !== "neutral" && f.short ? `<span class="wshort">${f.short}</span>` : ""}</td>`; }).join("")}</tr>`).join("");
  const th2 = (zh) => `<th scope="col">${zh}</th>`;
  const actZh = acts.map(([k, lab]) => [k, lab.split(" ")[0], lab.split(" ").slice(1).join(" ") || ACT_EN[k] || k]);
  const table = `<div class="scrollx keepzh"><table class="wtable dtable-daily"><tr>${th2("日期")}${th2("日柱")}${th2("十神")}${th2("五行")}
    ${actZh.map(([, zh]) => th2(zh)).join("")}</tr>${rows}</table></div>`;
  const officers = [...new Set(D.rows.map((r) => r.officer))], tags = [...new Set(D.rows.flatMap((r) => r.interactions))];
  const B = D.best, W = D.worst;
  const line = (B ? `${RS("appjs.dailyFig.002", {B_for: B.for.slice(0, 2).map((k) => ACT_EN[k]).join(" or "), B_date: B.date.slice(5), B_gz: B.gz, B_officer: B.officer})}` : RS("appjs.dailyFig.003"))
    + (W && W.avoid.length ? ` ${RS("appjs.dailyFig.004", {W_avoid: W.avoid.slice(0, 2).map((k) => ACT_EN[k]).join(" and "), W_date: W.date.slice(5), W_gz: W.gz, W_why: W.why})}` : "");
  const nGood = D.rows.filter((r) => Object.values(r.flags).some((f) => f.verdict === "good")).length;
  const nAvoid = D.rows.filter((r) => Object.values(r.flags).some((f) => f.verdict === "avoid")).length;
  return rdFig({ tier: "secondary", span: 12, label: RS("appjs.dailyFig.005"), learn: 13, chart: table, line,
    facts: [["from", D.start], [RS("appjs.dailyFig.006"), `${nGood}`], [RS("appjs.dailyFig.007"), `${nAvoid}`]],
    legend: `<div class="tkey"><p>${RS("appjs.dailyFig.008", {actZh_map: actZh.map(([, zh, en]) => `<span class="keepzh">${zh}</span> ${en}`).join(" · ")})}</p>
      <p>${RS("appjs.dailyFig.009", {officers_map: officers.map((o) => `<span class="keepzh">${o}</span> ${OFFICER_EN[o] || ""}`).join(" · ")})}</p>
      ${tags.length ? `<p>${RS("appjs.dailyFig.014", {tags_map: tags.map((x) => `<span class="keepzh">${x}</span> ${TAG_EN[x] || ""}`).join(" · ")})}</p>` : ""}</div>
      <div>${RS("appjs.dailyFig.010")}</div>
      <div>${RS("appjs.dailyFig.011")}</div>
      <div>${RS("appjs.dailyFig.012", {elc_c: elc(c.pillars.day[1]), elc_c_2: elc(c.pillars.year[1])})}</div>
      <div>${RS("appjs.dailyFig.013")}</div>
      <div class="sub">${D.source_ref}</div>` });
}

/* --- 方位 Compass ------------------------------------------------------------- */
function buildCompass(c, R) {
  const dirOf = {}; Object.entries(c.youxing).forEach(([pal, s]) => (dirOf[s] = PALACE_DIR[pal]));
  const c1 = rdFig({ tier: "hero", span: 5, label: RS("appjs.buildCompass.001"), learn: 7,
    chart: `<div class="cmpx-wrap">${bazhaiCompass(c)}</div>`,
    line: `${RS("appjs.buildCompass.002", {dirOf: dirOf["生氣"], dirOf_2: dirOf["絕命"]})}`,
    facts: [[RS("appjs.LEGENDS.chart.07.term"), `${c.gua} · ${c.group.split(" ")[0]}`], ["生氣", dirOf["生氣"]], ["絕命", dirOf["絕命"]], ["五鬼", dirOf["五鬼"]]],
    legend: `${BAZHAI_ORDER.map((s) => `<div><b>${s} ${BAZHAI_EN[s][0]}</b> — ${BAZHAI_EN[s][1]}</div>`).join("")}
      <div class="cite">${RS("appjs.buildCompass.004")}</div>${legendList(7)}` });
  const fav = c.yongshen.favourable, unf = c.yongshen.unfavourable, cols = c.yongshen.colours || [];
  const colEn = cols.map((z) => COLOUR_ZH_EN[z] || z).slice(0, 2).join("/");
  const chart = `${c.medicine_rank ? `<p class="cite" style="margin:0 0 6px">${RS("appjs.buildCompass.006", {c_medicine_rank: c.medicine_rank.replace(/^(?:Medicine, ranked:|用神排序：)\s*/, "")})}</p>` : ""}
    <p class="cite" style="margin:0 0 8px">${RS("appjs.buildCompass.005", {elbs_fav: elis(fav), elbs_unf: elis(unf), cols_join: cols.join("、")})}</p>
    ${c.xiji ? `<div class="scrollx keepzh"><table class="xiji htable">${c.xiji.map((r) => `<tr><th scope="row">${r.zh.split(" ")[0]}</th>
      <td>${r.elements.map((e) => eli(e)).join(" ")}</td><td>${r.gods.join("·")}</td></tr>`).join("")}</table></div>
      ${zhKey(c.xiji.map((r) => [r.zh.split(" ")[0], r.zh.split(" ").slice(1).join(" ")]))}` : ""}`;
  const EL_DIR = { 木: ["东 E", "震·巽"], 火: ["南 S", "離"], 土: [RS("appjs.buildCompass.007") + (IS_ZH ? " SW/NE" : ""), RS("appjs.buildCompass.008")], 金: ["西 W", "乾·兌"], 水: ["北 N", "坎"] };
  const EL_ROOM = { 木: RS("appjs.buildCompass.009"), 火: RS("appjs.buildCompass.010"),
    土: RS("appjs.buildCompass.011"), 金: RS("appjs.buildCompass.012"), 水: RS("appjs.buildCompass.013") };
  const dirTable = `<div class="scrollx keepzh"><table class="htable eldir"><tr><th scope="col">用神</th><th scope="col">方位</th><th scope="col">宫</th></tr>
    ${fav.map((e) => `<tr><td>${eli(e)}</td><td><b>${EL_DIR[e][0].split(" ")[0]}</b></td><td>${EL_DIR[e][1]}</td></tr>`).join("")}</table></div>
    ${zhKey([["用神", RS("appjs.buildCompass.014")], ["方位", "direction"], ["宫", RS("appjs.buildCompass.015")]])}
    <ul class="tkey-list">${fav.map((e) => `<li><b>${EL_EN[e]}</b> (<span class="keepzh">${e}</span>): ${EL_DIR[e][0].split(" ").slice(1).join(" ")}; ${EL_ROOM[e]}.</li>`).join("")}</ul>`;
  const chart2 = dirTable + chart;
  const c34 = rdFig({ tier: "hero", span: 7, extra: "rd-pair2", label: RS("appjs.buildCompass.016"), learn: 5, chart: chart2,
    line: `${RS("appjs.buildCompass.017", {elw_fav: elw(fav[0]), elc_fav: elc(fav[0]), colEn_in: colEn ? `${RS("appjs.buildCompass.018", {colEn: colEn})}` : "", unf_map: unf.map((e) => EL_EN[e]).join("/"), unf_map_2: unf.map(elc).join("")})}`,
    facts: [[RS("appjs.LEGENDS.chart.11.term"), elis(fav)], [RS("appjs.LEGENDS.5.02.term"), elis(unf)], c.tiaohou ? [RS("appjs.LEGENDS.5.04.term"), c.tiaohou.verdict] : null].filter(Boolean),
    legend: `<div>${RS("appjs.buildCompass.022", {fav_map: fav.map((e) => EL_EN[e]).join(" and "), unf_map: unf.map((e) => EL_EN[e]).join(", ")})}</div>
      ${c.tiaohou && c.tiaohou.line ? `<div class="cite">${c.tiaohou.line}</div>` : ""}
      ${c.element_relations ? `<div class="cite">${RS("appjs.buildCompass.023", {fav_map: fav.map((el) => { const f = Object.values(c.element_relations.flows).find((x) => x.el === el);
        return `${RS("appjs.buildCompass.024", {elb_el: eli(el), f_f: f ? f.role : "—"})}`; }).join(" · ")})}</div>` : ""}
      ${(c.yongshen.citations || []).map((x) => `<div class="cite"><b>${x.source_ref}:</b> ${x.explanation}</div>`).join("")}${legendList(5)}` });
  const PL = c.placements || [], AF = c.afflictions;
  const bed = PL.find((r) => r.key === "bed"), desk = PL.find((r) => r.key === "desk");
  const c2 = PL.length ? rdFig({ tier: "secondary", span: 7, label: RS("appjs.buildCompass.025"), learn: 7,
    chart: `<div class="scrollx keepzh"><table class="htable pltable"><tr><th scope="col">位置</th><th scope="col">方位</th><th scope="col">宫</th><th scope="col">星</th></tr>
      ${PL.map((r) => `<tr><th scope="row">${r.zh}</th><td><b class="pdir">${DIR_ZH[r.dir] || r.dir}</b></td><td>${r.palace}</td><td>${r.star || r.branch || "·"}</td></tr>`).join("")}</table></div>
      ${zhKey([["位置", RS("appjs.buildCompass.026")], ["方位", "direction"], ["宫", RS("appjs.buildCompass.015")], ["星", RS("appjs.buildCompass.028")]])}
      <ul class="tkey-list">${PL.map((r) => `<li><b>${r.en.charAt(0).toUpperCase() + r.en.slice(1)}</b> (<span class="keepzh">${r.zh}</span>), ${DIR_WORD_EN[r.dir] || r.dir}: ${r.rule.replace(/^八宅:\s*/, "")}</li>`).join("")}</ul>`,
    line: `${RS("appjs.buildCompass.029", {bed_dir: bed.dir, bed_star: bed.star, desk_dir: desk.dir, desk_star: desk.star})}`,
    facts: [[RS("appjs.buildCompass.030"), bed.dir], [RS("appjs.buildCompass.031"), desk.dir], ["文昌", (PL.find((r) => r.key === "wenchang") || {}).dir || "—"], [RS("appjs.LEGENDS.13.05.term"), (PL.find((r) => r.key === "taohua") || {}).dir || "—"]],
    legend: `<div>${RS("appjs.buildCompass.033")}</div>
      <div class="cite">${RS("appjs.buildCompass.034")}</div>` }) : "";
  const c5 = AF ? rdFig({ tier: "secondary", span: 5, label: `${RS("appjs.buildCompass.035", {AF_year: AF.year})}`, learn: 7,
    chart: `<table class="htable aftable keepzh">
      <tr><th scope="row">太岁</th><td><b class="pdir">${DIR_ZH[AF.taisui.dir] || AF.taisui.dir}</b> ${AF.taisui.palace} · ${AF.taisui.branch}</td></tr>
      <tr><th scope="row">岁破</th><td><b class="pdir">${DIR_ZH[AF.suipo.dir] || AF.suipo.dir}</b> ${AF.suipo.palace} · ${AF.suipo.branch}</td></tr>
      <tr><th scope="row">三煞</th><td><b class="pdir">${AF.sansha.dirs.map((d) => DIR_ZH[d] || d).join("·")}</b> ${AF.sansha.palaces.join("·")} · ${AF.sansha.branches}</td></tr>
      ${AF.suixing ? `<tr><th scope="row">岁刑</th><td><b class="pdir">${DIR_ZH[AF.suixing.dir] || AF.suixing.dir}</b> ${AF.suixing.palace} · ${AF.suixing.branch}</td></tr>` : ""}</table>
      ${zhKey([["太岁", RS("appjs.buildCompass.036")], ["岁破", RS("appjs.buildCompass.037")], ["三煞", RS("appjs.buildCompass.038")]].concat(AF.suixing ? [["岁刑", RS("appjs.buildCompass.048")]] : []))}
      ${AF.collisions.length ? `<div class="afhits">${AF.collisions.map((h) => `<div class="tag warn">${RS("appjs.buildCompass.tag", {h_affliction: h.affliction, h_star: h.star, h_dir: IS_ZH ? DIR_ZH[h.dir] || h.dir : h.dir})}</div>`).join("")}</div>` : ""}`,
    line: AF.collisions.length ? `${AF.collisions[0].note.replace(/^your/, "Your")}${IS_ZH ? "。" : "."}` : `${RS("appjs.buildCompass.039")}`,
    facts: [[RS("appjs.buildCompass.036"), AF.taisui.dir], [RS("appjs.buildCompass.037"), AF.suipo.dir], [RS("appjs.buildCompass.038"), AF.sansha.dirs.join("/")]],
    legend: `<div>${RS("appjs.buildCompass.043", {AF_taisui_rule: AF.taisui.rule})}</div><div>${RS("appjs.buildCompass.044", {AF_suipo_rule: AF.suipo.rule})}</div><div>${RS("appjs.buildCompass.045", {AF_sansha_rule: AF.sansha.rule})}</div>${AF.suixing ? `<div>${RS("appjs.buildCompass.047", {AF_suixing_rule: AF.suixing.rule})}</div>` : ""}
      ${AF.collisions.map((h) => `<div class="cite">${RS("appjs.buildCompass.046", {h_affliction: h.affliction, h_star: h.star, h_dir: h.dir, h_note: h.note.split(" — ")[1] || h.note})}</div>`).join("")}` }) : "";
  return { figs: { grid: c1, medicine: c34, placements: c2, afflictions: c5 }, tail: [R.stb(5), R.narr(5), R.narr(7)] };
}

/* Evidence panels (owner 2026-10-10): the charts' conclusions lead as "What this shows", and folds inside a
   panel open flat, so a panel never hides a second dropdown. Runs before the English pass. */
function tidyEvidence(root) {
  root.querySelectorAll(".ev").forEach((p) => {
    const lines = [...p.querySelectorAll(".rd-line")];
    if (lines.length) {
      const lead = document.createElement("div"); lead.className = "ev-lead";
      lead.innerHTML = `<p class="ev-k">${RS("appjs.tidyEvidence.001")}</p>${lines.map((l) => `<p>${l.innerHTML}</p>`).join("")}`;
      (p.querySelector(".evh") || p.firstChild).after(lead);
      lines.forEach((l) => { const row = l.closest(".rd-line-row"); l.remove();
        if (row) { const lg = row.querySelector(".rd-legend"); if (lg) row.before(lg); row.remove(); } });
    }
    p.querySelectorAll("details").forEach((d) => {
      const sum = d.querySelector(":scope > summary"), sec = document.createElement("section");
      const title = sum ? (sum.getAttribute("aria-label") === "how to read this" ? RS("appjs.tidyEvidence.002") : sum.textContent.trim()) : "";
      sec.className = "ev-sub"; if (sum) sum.remove();
      sec.innerHTML = (title ? `<h5>${title.charAt(0).toUpperCase() + title.slice(1)}</h5>` : "") + d.innerHTML;
      sec.querySelectorAll(".rd-legend-body").forEach((x) => (x.className = "ev-legend"));   // a popover no longer: it reads in place
      d.replaceWith(sec);
    });
  });
}

/* English-first pass: rewrite every text node through the shared glossary
   (window.GL, /static/glossary.js) in document order, so the first use of a term
   carries its Chinese once in parentheses and later uses are English only.
   Presentation only — no data, class or attribute is touched. */
function glossifyDom(root, fresh = true) {
  if (!root || !window.GL) return;
  if (fresh) GL.reset();
  // "<b>劫財</b> Rob Wealth" in chart legends: the term and its English sit in separate nodes, so the
  // pass below would write the English twice. Fold each pair into "Rob Wealth (劫財)" (owner rule).
  root.querySelectorAll(".ev b, .ev strong, .rd-synth-body b").forEach((el) => {   // where the legends put them
    const nx = el.nextSibling; if (!nx || nx.nodeType !== 3 || el.firstElementChild) return;
    const zh = el.textContent.trim(); if (!/^[㐀-鿿]{1,4}$/.test(zh)) return;
    const en = GL.english(zh); if (!en || en === zh) return;
    const m = new RegExp(`^\\s+${en.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "i").exec(nx.nodeValue); if (!m) return;
    nx.nodeValue = nx.nodeValue.slice(m[0].length); el.textContent = `${en} (${zh})`; el.classList.add("keepzh");
  });
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode: (n) => n.parentElement
      && /[\u3400-\u9fff]/.test(n.nodeValue)
      && !n.parentElement.closest("script,style,svg,input,textarea,.keepzh,.zh,[lang='zh-Hans']")
      ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT });
  const nodes = []; let t; while ((t = w.nextNode())) nodes.push(t);
  let box = null;   // each evidence panel and the full report start fresh: their first mention reads "English (漢字)"
  for (const n of nodes) {
    const b = n.parentElement.closest(".ev, .rd-synth-body"); if (b !== box) { box = b; if (b) GL.reset(); }
    const v = GL.text(n.nodeValue); if (v !== n.nodeValue) n.nodeValue = v; }
  // in panels and the report: a band word's bare characters go in brackets ("excess 過旺" → "excess (過旺)"),
  // and the engine's all-caps phrases read in sentence case
  const tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: (n) => n.parentElement
    && n.parentElement.closest(".ev, .rd-synth-body") && !n.parentElement.closest("svg,.keepzh,.zh") ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT });
  const tn = []; while ((t = tw.nextNode())) tn.push(t);
  for (const n of tn) {
    const v = n.nodeValue.replace(/\b(prominent|present|faint|absent|balanced|balanced centre|needs support|excess|weak|deficient|strong|favourable|unfavourable) ([㐀-鿿]{1,3})(?![㐀-鿿(（])/g, "$1 ($2)")
      .replace(/([A-Za-z]) ([㐀-鿿]{2,6})(?=$|[\s,;.:·—)])(?!\s?[(（](?!\d))/g, "$1 ($2)")   // "structure 学习文昌" → "structure (学习文昌)"
      .replace(/(^|[.:;—]\s*|\s)([A-Z]{4,}(?:[ -][A-Z]{2,})*)\b/g, (m, pre, caps) => pre + (/^$|[.:;—]\s*$/.test(pre) ? caps[0] + caps.slice(1).toLowerCase() : caps.toLowerCase()));
    if (v !== n.nodeValue) n.nodeValue = v;
  }
  GL.tipify(root);                     // Chinese runs -> tooltip spans (pinyin there only), element colours
}

function wireReading(root) {
  const links = Array.from(root.querySelectorAll(".rp-bar a")), byId = {};
  links.forEach((a) => (byId[a.getAttribute("href").slice(1)] = a));
  if (links.length && "IntersectionObserver" in window) {      // the chapter bar follows the reader
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (!e.isIntersecting) return;
      links.forEach((a) => { a.classList.remove("on"); a.removeAttribute("aria-current"); });
      const a = byId[e.target.id]; if (!a) return;
      a.classList.add("on"); a.setAttribute("aria-current", "true");
      a.parentElement.scrollTo({ left: a.offsetLeft - 16, behavior: "instant" }); }), { rootMargin: "-45% 0px -50% 0px" });
    root.querySelectorAll(".rp-chap:not(.rp-sources)").forEach((s) => io.observe(s));
  }
  // links from before the redesign (#tab-p1 … #tab-p5) still land on the matching chapter
  // chapters render after load, so the browser's own jump to #ch-… misses; links from before the
  // redesign (#tab-p1 … #tab-p5) land on the matching chapter too
  const hm = (location.hash || "").match(/^#(?:tab-p([1-5])|(ch-[a-z]+))$/);
  if (hm) { const s = root.querySelector(`#${hm[2] || "ch-" + CHAPTERS[+hm[1] - 1][0]}`); if (s) s.scrollIntoView({ block: "start" }); }
  // swipe hint only on tables that overflow; tables inside closed folds measure 0 until opened
  const markOverflow = () => root.querySelectorAll(".rd-fig .scrollx").forEach((w) =>
    w.classList.toggle("has-overflow", w.scrollWidth > w.clientWidth + 2));
  markOverflow(); window.addEventListener("resize", markOverflow);
  // the decade strip opens centred on the decade you are in now (or the first), without moving the page (round D)
  const centreNow = () => root.querySelectorAll(".ccdayun").forEach((s) => {
    const n = s.querySelector(".ccdy.now") || s.querySelector(".ccdy"); let sc = s;
    while (sc && sc !== root && sc.scrollWidth <= sc.clientWidth + 2) sc = sc.parentElement;
    if (!n || !sc || sc === root) return;
    const nr = n.getBoundingClientRect(), sr = sc.getBoundingClientRect();
    sc.scrollLeft += nr.left + nr.width / 2 - (sr.left + sr.width / 2); });
  centreNow(); window.addEventListener("resize", centreNow);
  root.addEventListener("toggle", markOverflow, true);
  // evidence panels open where you tapped (owner 2026-10-10): the one panel moves under the tapped marker's paragraph
  // (or under the answer cards for a "?"), shows its top without jumping, and × / Back / Escape close it and return focus
  const sync = (p, open) => root.querySelectorAll(`.mk[aria-controls="${p.id}"]`).forEach((m) => m.setAttribute("aria-expanded", String(open)));
  const reveal = (p) => { markOverflow(); const r = p.getBoundingClientRect();
    if (r.top > innerHeight - 120 || r.top < 0) scrollBy({ top: r.top - innerHeight * 0.3, behavior: "smooth" }); p.focus({ preventScroll: true }); };
  const close = (p) => { const o = p._opener;   // panels a "?" opened together close together
    (o && o.classList.contains("rp-q") ? [...root.querySelectorAll(".ev")].filter((x) => x._opener === o) : [p])
      .forEach((x) => { x.hidden = true; sync(x, false); x._opener = null; });
    if (o && o.isConnected) o.focus(); };
  root.addEventListener("click", (ev) => {
    const x = ev.target.closest(".ev-x,.ev-back");
    if (x) { close(x.closest(".ev")); return; }
    const q = ev.target.closest(".rp-q");
    if (q) {   // open every proof panel for this answer just below the answer cards, or fall back to its chapter
      const keys = q.dataset.ev.split(" ");   // the panel in the key's own chapter carries its figures and citations
      const ps = keys.map((k) => root.querySelector(`#ch-${EV_OWNER[k]} .ev[data-ev="${k}"]`) || root.querySelector(`.ev[data-ev="${k}"]`)).filter(Boolean);
      if (!ps.length) { const ch = document.getElementById("ch-" + EV_OWNER[keys[0]]); if (ch) ch.scrollIntoView({ block: "start", behavior: "smooth" }); return; }
      let at = q.closest(".rp-answers") || q.closest(".rp-ans");
      ps.forEach((p) => { at.after(p); at = p; p.hidden = false; p._opener = q; sync(p, true); });
      reveal(ps[0]); return;
    }
    const b = ev.target.closest(".mk"); if (!b) return;
    const p = document.getElementById(b.getAttribute("aria-controls")); if (!p) return;
    if (!p.hidden && p._opener === b) { close(p); return; }
    const para = b.closest("p, li") || b.parentElement;
    if (para.nextElementSibling !== p) para.after(p);
    p.hidden = false; p._opener = b; sync(p, true); reveal(p);
  });
  root.addEventListener("keydown", (ev) => { if (ev.key !== "Escape") return;
    const p = ev.target.closest && ev.target.closest(".ev"); if (p && !p.hidden) close(p); });
}

/* The geomancer's report (summary, findings, assessment, plan, method note) behind one fold under
   the opening: the plain answers above carry its summary, this keeps every line of it one tap away. */
function synthNote(sy) {
  if (!sy) return "";
  const body = Array.isArray(sy) ? (sy.length ? `<p class="rd-synth-p">${sy.join(" ")}</p>` : "")
    : `${sy.summary ? `<p class="rd-synth-lede">${sy.summary}</p>` : ""}
      ${(sy.findings || []).length ? `<h4>${RS("appjs.synthNote.001")}</h4><dl class="rd-synth-dl">${sy.findings.map((f) => `<dt>${f.label}</dt><dd>${f.text}</dd>`).join("")}</dl>` : ""}
      ${sy.assessment ? `<h4>${RS("appjs.synthNote.002")}</h4><p class="rd-synth-p">${sy.assessment}</p>` : ""}
      ${(sy.plan || []).length ? `<h4>${RS("appjs.synthNote.003")}</h4><ol class="rd-synth-plan">${sy.plan.map((x) => `<li>${x}</li>`).join("")}</ol>` : ""}
      ${sy.confidence ? `<p class="rd-synth-conf">${RS("appjs.synthNote.004", {sy_confidence: sy.confidence})}</p>` : ""}`;
  return body ? `<details class="rp-more rp-report"><summary>${RS("appjs.synthNote.005")}</summary><div class="rd-synth-body">${body}</div></details>` : "";
}

async function renderPerson(name) {
  const url = window.__CHART_URL__ ||
    `/api/chart/${encodeURIComponent(name)}?policy=${state.policy}&year=${state.year}`;
  const c = await api(url);
  // the server already sent the opening painting with the page (it is the largest element on a phone); keep that very
  // <img> so it never reloads or re-paints. Without it (other routes), start the download as soon as the data is here.
  const keepPic = document.querySelector("#tab-person .rp-ssr .rp-bgimg");
  if (!keepPic) preloadOpeningArt(c);
  const nb = splitNarr(c.interpretation);
  const SEC_ZH = { 1: RS("appjs.renderPerson.sec1"), 2: RS("appjs.renderPerson.sec2"), 3: RS("appjs.renderPerson.001"),
    4: RS("appjs.renderPerson.sec4"), 5: RS("appjs.renderPerson.002"), 6: RS("appjs.CHAPTERS.timing.what"), 7: RS("appjs.renderPerson.sec7"),
    8: RS("appjs.renderPerson.004"), 9: RS("appjs.renderPerson.005"), 10: RS("appjs.renderPerson.sec10"),
    11: RS("appjs.renderPerson.sec11"), 12: RS("appjs.renderPerson.sec12"), 13: RS("appjs.renderPerson.006") };
  const R = { nb,
    narr: (n) => deepWrap(`${RS("appjs.renderPerson.007", {SEC_ZH_n: SEC_ZH[n] || ""})}`,
      (nb.by[n] || []).map((t) => `<div class="ninline">${dnAll(t)}</div>`).join("")),
    stb: (n) => deepWrap(`${RS("appjs.renderPerson.008", {SEC_ZH_n: SEC_ZH[n] || ""})}`, stratBlock(n, c.strategy)) };
  $("#tab-person").innerHTML = jt(`
    <div class="rp-open">${pIdentity(c, name)}${pSides(c)}${pAnswers(c)}${synthNote(c.synthesis)}</div>
    ${pChapBar()}
    ${readingChapters(c, R)}`);
  if (keepPic) { const fresh = document.querySelector("#tab-person .rp-bgimg"); if (fresh) fresh.replaceWith(keepPic); }
  wireReading($("#tab-person"));
  const who = dn(name || c.name), h1 = document.querySelector(".pub-in h1");
  if (h1 && who) {
    h1.innerHTML = `${RS("appjs.renderPerson.015", {who: who})}`;
    document.title = `${RS("appjs.renderPerson.016", {who: who})}`;
    const own = $("#tab-person .rp-name"); if (own) own.remove();
  }
  tidyEvidence($("#tab-person"));
  // English first, then colour: colouring splits 劫財 into its own node, and the English pass must see
  // "劫財 Rob Wealth" whole or it writes the English twice
  glossifyDom($("#tab-person"));
  colorizeTerms($("#tab-person"), c.day_master);
  colorizeColours($("#tab-person"));
}

/* ---------- House tab ---------- */
function renderHouse() {
  const h = state.house;
  const [iw, ih] = h.image_size;
  const natal = h.natal[String(state.period)];
  const key = state.method === "pie" ? "palace_pie" : "palace_grid";
  const [cx, cy] = h.centroid;
  const sectorLines = [...Array(8)].map((_, i) => {
    const a = ((i * 45 + 22.5 - h.image_up_bearing) * Math.PI) / 180;
    const R = Math.max(iw, ih);
    return `<line class="sector-line" x1="${cx}" y1="${cy}"
      x2="${cx + R * Math.sin(a)}" y2="${cy - R * Math.cos(a)}"/>`;
  }).join("");
  const rooms = h.rooms.map((r) => {
    const pts = r.poly.map(([x, y]) => `${x},${y}`).join(" ");
    const [rx, ry] = r.poly.reduce(([ax, ay], [x, y]) => [ax + x / r.poly.length, ay + y / r.poly.length], [0, 0]);
    const pal = r[key];
    const st = pal === "中" ? null : natal.palaces[pal];
    const stars = st ? `山${st.mountain} 向${st.water} 年${h.annual[pal]}` : "中宮";
    const flag = r.method_disagrees ? " ⚠" : "";
    return `<polygon class="room-poly ${r.sleeping ? "sleeping" : ""}" points="${pts}"/>
      <text class="room-lab" x="${rx}" y="${ry - 4}" text-anchor="middle">${r.label}${flag}</text>
      <text class="room-star" x="${rx}" y="${ry + 10}" text-anchor="middle">${pal} · ${stars}</text>`;
  }).join("")
  + Object.entries(h.features || {}).map(([nm, [fx, fy]]) =>
      `<text x="${fx}" y="${fy}" text-anchor="middle" font-size="22">${nm === "stove" ? "🔥" : "🚪"}</text>`).join("");
  const cells = { NW: "乾", N: "坎", NE: "艮", W: "兌", C: "中", E: "震", SW: "坤", S: "離", SE: "巽" };
  const af = h.afflictions || {};
  const afTag = (p) => [
    af.taisui && af.taisui.palace === p ? '<span class="tag warn">太歲</span>' : "",
    af.suipo && af.suipo.palace === p ? '<span class="tag warn">歲破</span>' : "",
    af.sansha && af.sansha.palaces.includes(p) ? '<span class="tag warn">三煞</span>' : "",
  ].join("");
  const gridCells = ["NW", "N", "NE", "W", "C", "E", "SW", "S", "SE"].map((d) => {
    const p = cells[d];
    const base = natal.palaces[p].base;
    return `<div class="palace-cell"><div class="dirlab">${d} ${p} ${afTag(p)}</div>
      <div class="stars"><span class="m">${natal.palaces[p].mountain}</span> ${base} <span class="w">${natal.palaces[p].water}</span></div>
      <div class="ann">年 ${h.annual[p]}</div></div>`;
  }).join("");
  $("#tab-house").innerHTML = jt(narrBlock(h.interpretation && h.interpretation[String(state.period)]) + `
    <h2>${natal.sitting}山${natal.facing}向 · Period ${state.period} → <b>${natal.structure}</b></h2>
    <div class="house-flex">
      <div id="overlay-wrap">
        <img src="${BAKED ? BAKED.floorplan : "/floorplan.jpeg"}" alt="floorplan">
        <svg viewBox="0 0 ${iw} ${ih}" preserveAspectRatio="xMinYMin">${sectorLines}${rooms}</svg>
      </div>
      <div>
        <h3>宅盤 (山星 · 運盤 · 向星)</h3>
        <div class="palace-grid">${gridCells}</div>
        ${h.features_analysis && h.features_analysis.length ? `
          <h3 style="margin-top:12px">Door &amp; stove (八宅宅卦)</h3>
          ${h.features_analysis.map((fa) => `<div class="cite">
            <b>${fa.feature === "main_door" ? "🚪 Main door" : fa.feature === "stove" ? "🔥 Stove" : fa.feature}</b>
            <span class="tag ${fa.verdict === "caution" ? "warn" : ""}">${fa.verdict}</span>
            ${fa.explanation}</div>`).join("")}`
          : `<div class="cite" style="margin-top:10px">🚪🔥 Mark the main door and stove on
            the ✏️ Trace page to unlock the 八宅 door &amp; stove rules (door wants a
            lucky house sector; the stove classically presses an unlucky one).</div>`}
        <p class="cite">${h.notes.map((n) => `<div>· ${n}</div>`).join("")}</p>
      </div>
    </div>`);
}

/* ---------- Assignment tab ---------- */
async function renderAssign() {
  const people = state.family.people.map((p) => p.name);
  const rooms = state.house.rooms.filter((r) => r.sleeping);
  const body = JSON.stringify({ assignment: state.assignment, year: state.year,
                                period: state.period, method: state.method, policy: state.policy });
  const opts = { method: "POST", headers: { "Content-Type": "application/json" }, body };
  const [res, interp] = await Promise.all([api("/api/score", opts), api("/api/interpret", opts)]);
  const interpHtml = `<div class="section interp">
    <h3>Interpretation 解读 <span class="tag">rule-based · auto-generated · no AI</span></h3>
    ${interp.sections.map((sec) => `<h4>${sec.heading}</h4>` +
      sec.lines.map((l) => `<div class="cite">· ${dnAll(l)}</div>`).join("")).join("")}
  </div>`;
  const byRoom = {};
  res.scores.forEach((s) => (byRoom[s.room] = byRoom[s.room] || []).push(s));
  $("#tab-assign").innerHTML = jt(`
    <h2>Room assignment — household total <span id="hh-total">${res.household_total.toFixed(2)}</span>
      <button class="small" id="btn-optimize">✨ Optimize</button>
      <label style="font-size:13px"><input type="checkbox" id="opt-split"> allow parents to split</label>
    </h2>
    <div id="opt-result"></div>
    ${interpHtml}
    ${res.violations.map((v) => `<div class="violation">⚠ ${v}</div>`).join("")}
    <div class="assign-grid">${rooms.map((r) => `
      <div class="card" data-room="${r.id}">
        <h3>${r.label} <span class="sub">${r[state.method === "pie" ? "palace_pie" : "palace_grid"]}宮 · cap ${r.capacity}</span></h3>
        ${people.map((n) => `<label style="display:block">
          <input type="checkbox" data-room="${r.id}" data-name="${n}"
            ${(state.assignment[r.id] || []).includes(n) ? "checked" : ""}> ${dn(n)}</label>`).join("")}
        ${(byRoom[r.id] || []).map((s) => `<div class="cite"><b>${dn(s.person)}: ${s.total.toFixed(2)}</b>
          ${s.breakdown.map((b) => `<div>· [${layerZh(b.layer)}] ${b.contribution >= 0 ? "+" : ""}${b.contribution.toFixed(2)} — ${b.explanation}</div>`).join("")}</div>`).join("")}
      </div>`).join("")}
    </div>`);
  $("#tab-assign").querySelectorAll("input[type=checkbox][data-room]").forEach((cb) =>
    cb.addEventListener("change", () => {
      const { room, name } = cb.dataset;
      for (const rid of Object.keys(state.assignment))
        state.assignment[rid] = state.assignment[rid].filter((n) => n !== name);
      if (cb.checked) state.assignment[room].push(name);
      renderAssign();
      if (!BAKED) renderForMe().then(renderOurHome);   // 2A: live cards react
    }));
  $("#btn-optimize").addEventListener("click", async () => {
    $("#opt-result").innerHTML = `<p class="hint">optimizing…</p>`;
    const out = await api("/api/optimize", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ year: state.year, period: state.period, method: state.method,
                             policy: state.policy,
                             allow_master_split: $("#opt-split").checked }),
    });
    $("#opt-result").innerHTML = jt(`<div class="section">
      <h3>Best of ${out.evaluated} feasible assignments</h3>
      ${out.best.map((b, i) => `<div style="margin:6px 0">
        <b>#${i + 1} — total ${b.household_total.toFixed(2)}</b>
        ${Object.entries(b.assignment).map(([rid, ns]) => `<span class="tag">${rid}: ${ns.join("+")}</span>`).join(" ")}
        ${i === 0 ? `<button class="small" id="apply-opt">apply</button>` : ""}
      </div>`).join("")}
    </div>`);
    $("#apply-opt")?.addEventListener("click", () => {
      const best = out.best[0].assignment;
      for (const rid of Object.keys(state.assignment)) state.assignment[rid] = best[rid] || [];
      renderAssign();
      if (!BAKED) renderForMe().then(renderOurHome);   // 2A: live cards react
    });
  });
  try {
    const cmp = await api(`/api/compare?kind=arrangements&year=${state.year}` +
                          `&period=${state.period}&method=${state.method}` +
                          `&policy=${state.policy}`);
    $("#tab-assign").insertAdjacentHTML("beforeend", jt(`<div class="section">
      <h3>Current vs optimal 方案对比
        <span class="tag">everyone's room card under each arrangement</span></h3>
      <div class="cmp-cols">${cmpCols(cmp)}</div></div>`));
  } catch (e) { /* compare not available */ }
}

/* ---------- Forecast tab ---------- */
function renderForecastTab() {
  const people = state.family.people.map((p) => p.name);
  $("#tab-forecast").innerHTML = jt(`
    <h2>流年流月 Forecast ${state.year}</h2>
    <label>Person <select id="fc-person">${people.map((n) => `<option value="${n}">${dn(n)}</option>`).join("")}</select></label>
    <div id="fc-body"></div>`);
  const load = async () => {
    const name = $("#fc-person").value;
    const f = await api(`/api/forecast/${encodeURIComponent(name)}?year=${state.year}&period=${state.period}&policy=${state.policy}&method=${state.method}`);
    $("#fc-body").innerHTML = jt(narrBlock(f.interpretation) + `
      <div class="section"><h3>${f.year_ganzhi}年 · annual center star ${f.annual_center}</h3>
        ${f.taisui.map((t) => `<div class="cite"><b>${t.source_ref}:</b> ${t.explanation}</div>`).join("")}
        <div class="cite"><b>${f.year_element.source_ref}:</b> ${f.year_element.explanation}</div>
      </div>
      ${f.room_watch.length ? `<div class="section"><h3>⚠ Room watch (${f.room_palace}宮)</h3>
        ${f.room_watch.map((w) => `<div class="cite violation"><b>${w.source_ref}:</b> ${w.explanation}</div>`).join("")}</div>` : ""}
      <div class="section"><h3>流月 monthly stars${f.room_palace ? ` in your room (${f.room_palace}宮)` : ""}</h3>
        <table><tr><th>月</th>${f.months.map((m) => `<th>${m.month_branch}</th>`).join("")}</tr>
        <tr><td>中宮</td>${f.months.map((m) => `<td>${m.center}</td>`).join("")}</tr>
        ${f.room_palace ? `<tr><td>room</td>${f.months.map((m) =>
          `<td class="${m.room_star === 5 || m.room_star === 2 ? "bad" : m.room_quality >= 1.5 ? "good" : ""}">${m.room_star}</td>`).join("")}</tr>` : ""}
        </table></div>
      <div class="section"><h3>五年展望 5-year outlook</h3>
        <div class="cite" style="margin:0 0 6px">Each coming year's branch is checked
          against the four natal branches: 沖 clash / 刑 punishment score 2, 害 harm 1
          — total ≥3 reads high volatility, 1–2 moderate, 0 steady. 合/半合 contacts are
          listed as support. Volatile ≠ bad: it marks years to decide slowly and put
          agreements in writing.</div>
        <table><tr><th>Year</th><th>Verdict</th><th>Interactions</th><th>Elements</th><th>Advice</th></tr>
          ${f.outlook.map((o) => `<tr>
            <td><b>${o.year} ${o.gz}</b></td>
            <td class="${o.verdict === "high volatility" ? "bad" : o.verdict === "steady" ? "good" : ""}">${o.verdict}</td>
            <td>${o.events.map((e) => `<span class="tag warn">${e}</span>`).join(" ")}
                ${o.support.map((s) => `<span class="tag">${s}</span>`).join(" ")}</td>
            <td>${o.elements.join("<br>")}</td>
            <td class="sub">${o.advice}</td></tr>`).join("")}
        </table></div>`);
  };
  $("#fc-person").addEventListener("change", load);
  load();
}

/* ---------- Dates tab ---------- */
function renderDatesTab() {
  const now = new Date();
  $("#tab-dates").innerHTML = jt(`
    <h2>擇日 Date selection</h2>
    <label>Month <input id="zr-month" type="month" value="${state.year}-${String(now.getMonth() + 1).padStart(2, "0")}"
      ${BAKED ? `min="${state.year}-01" max="${state.year}-12"` : ""}></label>
    <p class="hint">Simplified 建除 + 月破 + per-person 沖/合 — for moving, renovation, signings. Cross-check a 通書 for final dates.</p>
    <div id="zr-body"></div>`);
  const load = async () => {
    const [y, m] = $("#zr-month").value.split("-").map(Number);
    const out = await api(`/api/dates?year=${y}&month=${m}`);
    const best = [...out.days].sort((a, b) => b.score - a.score).slice(0, 5).map((d) => d.date);
    $("#zr-body").innerHTML = jt(narrBlock(out.interpretation) + `
      <table><tr><th>Date</th><th>日柱</th><th>建除</th><th>Score</th><th>吉時 hours</th><th>Person flags</th></tr>
      ${out.days.map((d) => `<tr style="${best.includes(d.date) ? "background:#f0f7ee" : d.score <= -2 ? "background:#fbeeec" : ""}">
        <td>${d.date}</td><td>${d.day_gz}</td><td>${d.officer}</td>
        <td class="${d.score >= 1.5 ? "good" : d.score <= -1 ? "bad" : ""}">${d.score.toFixed(1)}</td>
        <td>${(d.hours ? d.hours.best.map((hh) =>
            `<span class="tag" title="${hh.tags.join("·")}">${hh.branch} ${hh.time} ${hh.tags.join("·")}</span>`).join(" ")
            + d.hours.avoid.map((hh) =>
            `<span class="tag warn">避 ${hh.branch} ${hh.time} ${hh.tags.join("·")}</span>`).join(" ") : "")}</td>
        <td>${d.person_flags.map((f) => `<span class="tag ${f.kind.startsWith("沖") ? "warn" : ""}" title="${f.why}">${dn(f.name)} ${f.kind}</span>`).join("")}</td>
      </tr>`).join("")}</table>`);
  };
  $("#zr-month").addEventListener("change", load);
  load();
}

/* ---------- Pair 合婚 tab ---------- */
function renderPairTab() {
  const people = state.family.people.map((p) => p.name);
  $("#tab-pair").innerHTML = jt(`
    <h2>合婚 Pair compatibility</h2>
    <label>A <select id="pa">${people.map((n, i) => `<option ${i === 0 ? "selected" : ""}>${n}</option>`).join("")}</select></label>
    <label>B <select id="pb">${people.map((n, i) => `<option ${i === 1 ? "selected" : ""}>${n}</option>`).join("")}</select></label>
    <div id="pair-body"></div>`);
  const load = async () => {
    const a = $("#pa").value, b = $("#pb").value;
    if (a === b) { $("#pair-body").innerHTML = `<p class="hint">pick two different people</p>`; return; }
    const r = await api(`/api/pair?a=${encodeURIComponent(a)}&b=${encodeURIComponent(b)}&policy=${state.policy}`);
    $("#pair-body").innerHTML = jt(narrBlock(r.interpretation) + `
      <div class="section">
        <h3>${r.a} × ${r.b} — <span class="${r.score >= 55 ? "good" : r.score < 45 ? "bad" : ""}">${r.score}/100</span> · ${r.band}</h3>
        <div class="sub">day pillars ${r.day_pillars.join(" · ")}</div>
        <div style="margin:8px 0">${r.chips.map((c2) =>
          `<span class="tag ${c2.delta < 0 ? "warn" : ""}">${c2.label} ${c2.delta > 0 ? "+" : ""}${c2.delta}</span>`).join(" ")}</div>
        <div class="cite">${r.source_ref}</div>
      </div>`);
  };
  $("#pa").addEventListener("change", load);
  $("#pb").addEventListener("change", load);
  load();
}

/* ---------- Names tab ---------- */
async function renderNamesTab() {
  const out = await api("/api/names");
  /* Names tab ONLY: keep 繁體 — protect full names and their individual
     characters (stroke tags) from the 简体 conversion. */
  const trad = out.people.map((p) => p.name);
  const keep = [...trad, ...new Set(trad.join(""))];
  const re = new RegExp(`(${keep.join("|")})`, "g");
  const jtNames = (html) =>
    html.split(re).map((seg, i) => (i % 2 ? seg : toSimp(seg))).join("");
  $("#tab-names").innerHTML = jtNames(narrBlock(out.interpretation) +
    `<h2>姓名學 (康熙繁體筆畫 · 三才五格)</h2>` + out.people.map((p) => {
    if (!p.valid)
      return `<div class="section"><h3>${dn(p.name)} — ⚠ invalid</h3>
        ${p.problems.map((x) => `<div class="violation">${x}</div>`).join("")}</div>`;
    return `<div class="section"><h3>${dn(p.name)}
        <span class="tag">${p.chars.map((c) => `${c.char}${c.kangxi_strokes}`).join(" ")}</span>
        <span class="tag ${p.sancai.verdict === "吉" ? "" : "warn"}">三才 ${p.sancai.elements} ${p.sancai.verdict}</span></h3>
      <table><tr>${Object.keys(p.grids).map((g) => `<th>${g}</th>`).join("")}</tr>
        <tr>${Object.values(p.grids).map((v) =>
          `<td class="${v.luck === "吉" ? "good" : v.luck === "凶" ? "bad" : ""}">${v.number} ${v.luck} (${v.element})</td>`).join("")}</tr>
      </table>
      ${(p.reading || []).map((l) => `<div class="cite">· ${l}</div>`).join("")}
      <div class="cite"><b>${p.citation.source_ref}</b></div></div>`;
  }).join(""));
}

/* ---------- Unit evaluator tab ---------- */
function renderUnitTab() {
  $("#tab-unit").innerHTML = jt(`
    <h2>評宅 Candidate-unit evaluator <span class="tag warn">coarse mode — approximate</span></h2>
    <label>Facing (degrees) <input id="ev-deg" type="number" value="135" min="0" max="359"></label>
    <label>Period <select id="ev-period"><option value="8">8</option><option value="9" selected>9</option></select></label>
    <button class="small" id="ev-go">Evaluate</button>
    <div id="ev-body"></div>`);
  $("#ev-go").addEventListener("click", async () => {
    const out = await api("/api/evaluate_unit", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ facing_deg: +$("#ev-deg").value, period: +$("#ev-period").value,
                             year: state.year, policy: state.policy }),
    });
    $("#ev-body").innerHTML = jt(narrBlock(out.interpretation) + `<div class="section">
      <h3>${out.facing_mountain}向 · P${out.period} → ${out.structure} · household best-sum ${out.household_best_sum.toFixed(2)}</h3>
      <div class="violation">${out.disclaimer}</div>
      <table><tr><th>Person</th>${out.people[0].sectors.map((s) => `<th>${s.direction}</th>`).join("")}</tr>
        ${out.people.map((p) => `<tr><td>${dn(p.name)}</td>${p.sectors.map((s) =>
          `<td class="${s.total >= 1 ? "good" : s.total <= -0.5 ? "bad" : ""}">${s.total.toFixed(1)}</td>`).join("")}</tr>`).join("")}
      </table></div>`);
  });
}

if (window.__PUBLIC_READING__) {
  // standalone Reading 命书 page (bazifor.me workspace person) — no family app boot
  (async () => {
    window.__CHART_URL__ = window.__PUBLIC_READING__.chartUrl;
    try { await renderPerson(window.__PUBLIC_READING__.name); }
    catch (e) { $("#tab-person").innerHTML = `<p class="hint">${RS("appjs.bootReading.001", {e_message: e.message})}</p>`; return; }
  })();
} else {
  controls();
  if (window.GL && window.MutationObserver) {      // demo app: English-first pass over each tab pane once it is rendered
    const seen = new WeakMap();
    new MutationObserver((muts) => {
      const panes = new Set(muts.map((m) => m.target.closest && m.target.closest(".tabpane")).filter(Boolean));
      panes.forEach((p) => { clearTimeout(seen.get(p)); seen.set(p, setTimeout(() => glossifyDom(p, true), 60)); });
    }).observe(document.querySelector("main"), { childList: true, subtree: true });
  }
  refresh().catch((e) => ($("#warnings").textContent = "load failed: " + e.message));
}
