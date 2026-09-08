# Aspects & Remedies Overhaul — "what it means for me, and what to do about it"

**Status:** DRAFT for /plan-eng-review · 2026-09-06
**Depends on:** the shipped engine (docs/designs/fengshui-family-compass.md, all four
milestones + tiers 1–4). This overhaul adds layers; it recomputes nothing.

## 1 · Problem

The app is method-first: 八宅 says X, 飞星 says Y, 神煞 says Z, each in its own
vocabulary. A family member's actual question is aspect-first — *"is this room good for
my study?"*, *"what should I change?"*. Today the interpretation and the actions are
scattered across narratives, and the user must synthesise them — exactly the job a
geomancer is paid for. A wholesale calculator without prescriptions has no value-add.

## 2 · Vision — the three-layer pipeline

```
CALCULATE (exists, untouched)  →  INTERPRET (0–100 aspect scores)  →  PRESCRIBE (actions)
 bazi/xuankong/bazhai/shensha…     engine/aspects.py                   engine/remedies.py
 every figure rule-cited           declared weights, one scale         every action rule-cited
```

The classical apparatus becomes the *audit trail* inside every card — collapsed by
default, one tap away for the interested few. Interpretability becomes part of the
auditability, never a replacement for it.

## 3 · The universal Card contract

One schema for **everything** evaluated (person, person×room, home, pair, date, year,
name — "generic cards for whatever is being evaluated"):

```python
AspectCard = {
  "subject":  {"type": "person|room|home|pair|date|year|name", "id": ..., "label": ...},
  "aspect":   "health|career|study|wealth|relationship|luck"   # + subject extras
              # home extra: "structure"; year/date extra: "timing"; name extra: "name",
  "score":    0-100,          # 50 = neutral; 5 quantised bands (T5-A):
                              # ≥80 旺 strong · 65-79 优 good · 45-64 平 fair
                              # · 30-44 弱 weak · <30 忌 poor
  "band":     "strong|good|fair|weak|poor",
  "meaning":  "one plain sentence — what this means for this subject",
  "driver":   "the single biggest contributor, in plain English",
  "actions":  [RemedyAction, ...],      # 0-3, ranked; THE value-add
  "audit":    [ScoreBreakdown, ...],    # the full cited classical working (collapsed UI)
  "source_ref": "aspect composition vX (weights table §5) — MODERN SYNTHESIS",
}
```

Rendering: one generic card component — **band word + colour lead; the number sits
small beside it** (T5-A: near-ties inside a band look identical; Compare still sorts
numerically; full precision in the audit). Meaning line, action chips, `▾ Show the
classical working` details. Used identically on every page, in the static report, the
offline snapshot and the battlecard.

Schema vs renderers (T4-A): the dict contract keeps all subject types (each is already
computed by the shipped engine), but **renderers implement only the subjects their
milestone ships** — M1: person/room/home; pair/date/name/year card UI lands with the
M2/M3 pages that show them.

## 4 · The Remedy engine (`engine/remedies.py`) — NEW

Deterministic rule tables mapping *cited findings* → *concrete actions*. Contract:

```python
RemedyAction = {
  "trigger":  "the finding, cited (e.g. '木 excess 33% — element_weights')",
  "action":   "imperative, concrete (e.g. 'add reds/warm lighting — Fire drains excess Wood')",
  "category": "colour|material|direction|placement|timing|habit",
  "priority": 1-3,            # 1 = do this first
  "source_ref": "classical rule name",
}
```

### Remedy rule families (all pure lookup, no LLM)

**R1 · Element imbalance (person)** — the user's own example.
- *Excess* element E → prefer 洩 drain (the element E generates): excess 木 → 火
  colours/lighting/warmth; controlling element (剋) offered as secondary, labelled
  "harsher". *Deficient* element E → supplement directly (E colours/materials) + its
  mother (生): weak 水 → 黑藍 + metal decor (金生水). Materials map: 木 plants/wood
  furniture · 火 lights/red textiles · 土 ceramics/stone/earth tones · 金 metal
  decor/white · 水 water feature/glass/black-blue.
- Emitted on: person Health card (organ framing), person overview.

**R2 · Room fit (person×room)** — bad 八宅 star or bad annual star in one's bedroom.
- Bad personal star (五鬼/絕命/六煞/禍害): headboard/desk toward that person's best
  available direction (from 遊年); occupant's 用神 colours in their zone of the room.
- Annual star remedies (紫白 classical table): 五黃/二黑 (earth) → metal (brass,
  six-coin, metal pendulum clock), avoid red/fire, no disturbance; 三碧 (wood,
  conflict) → red/fire drains; 七赤 → water colours drain; auspicious 8/9/1/4 →
  activate with light/movement/use.
- Emitted on: room-suitability cards, forecast/room-watch cards.

**R3 · Star placement gaps (home)** — 向星8/9 without water/activity → "keep this zone
bright, lively; moving object/water feature here"; 山星8/9 without solid backing →
"heavy furniture / solid wall use here; keep it still". (TowerC's blocked-明堂 and
TowerB's dry facing become explicit action cards.)

**R4 · Timing (year/date)** — afflicted sector → "no drilling/renovation in <rooms>
until 立春 <date>"; planned works → "best window: <month/year>, best days on Planner";
month watches → "keep <room> quiet in <months>".

**R5 · Study alignment (person)** — desk facing personal 文昌; relocate desk to 文昌
room when one exists; homework at the house 文昌星 table.

**R6 · Relationship (pair/couple)** — clash pairs → separate work corners, calmer
decor, avoid dates clashing either; bedroom penalties → R2; 桃花位 room → "use it
together regularly" when it exists.

Ranking: priority asc, then |trigger contribution| desc; cards show top ≤3, the full
list lives in the audit dropdown. Every action carries its trigger — no orphan advice.

### Resource arbitration (T1-A)

Remedy families compete for the same physical resources (one headboard, one desk, one
room colour scheme). remedies.py resolves via an **arbitration table**: each
RemedyAction declares its `resource` (headboard|desk|room_colour|zone_object|schedule)
and each resource emits **at most one winning action** per card, chosen by declared
priority (annual-safety 1 > 八宅 personal 2 > 用神 colour 3 > activation 4). Losing
actions are not dropped — they move to the audit tagged `superseded by <winner>`.
Pinned by a pytest: no card ever shows two actions on the same resource.

## 5 · Aspect composition (`engine/aspects.py`) — declared weights

All existing outputs, blended per (subject, aspect), normalised to 0–100
(rooms' zero-centred fit maps affinely: `score = clamp(50 + 25·fit, 5, 95)`; raw value
kept in audit). **T2-A:** weights live in ONE table-driven constant (`WEIGHTS` in
aspects.py); golden tests derive expected values from that table (change the table,
goldens follow), and the primer labels the table "calibration, not classical truth".
**T3-A:** the affine map saturates only beyond |fit| 1.8; real family fits span
−1.20…+1.34 today — a saturation-guard test asserts every produced card sits inside
the linear region and fails loudly if a future config pushes one out. Initial table
(reviewable):

| Subject × aspect | Composition (weights) |
|---|---|
| person · health | TCM element flags 40 · bed on/near 山星 25 · 天醫-room access 20 · year room-watch 15 |
| person · career | life_domains.career 50 · 生氣 room/desk access 25 · 向星8 zone usability 25 |
| person · study | life_domains.learning 40 · personal 文昌 alignment 35 · house 文昌星/文昌水 25 |
| person · wealth | life_domains.wealth 50 · home 向8 activation 30 · P9 durability 20 |
| person · relationship | life_domains attraction/stability 50 · bedroom fit 30 · 桃花位 access 20 |
| person · luck | room fit (assigned) 50 · year outlook verdict 30 · 大運 favourability 20 |
| home · <aspect> | aggregate of member cards (mean, min flagged) + structure modifiers |
| pair/date/name | existing scores re-banded to 0–100 + actions |

## 6 · Information architecture — five pages, person-first

1. **家人 Me & Family** — per member: 6 aspect cards + top actions. Landing page.
2. **Our Home 我们的家** — home cards (structure, per-member room suitability, this-year
   timing card with action chips).
3. **Compare 对比** — generic N-subject comparison: pick homes/rooms/arrangements/dates
   → same cards side-by-side. (fengshuiBattlecard becomes a preset of this.)
4. **Planner 择时** — dates/hours/reno windows as action cards.
5. **The Working 审计** — the entire current 10-tab apparatus, unchanged, as the deep
   secondary report; every card's audit deep-links here. Trace/Pair/Unit tools live on.

Outputs converge: static report = cards first, working appended; offline snapshot bakes
cards like everything else; battlecard generated from Compare presets.

## 7 · Invariants

- **No LLM at runtime.** Cards, meanings, actions: all templates + rule tables.
- **Every number cited; every action carries its trigger.** MODERN SYNTHESIS labelled.
- 简体 UI / 繁體 names-analysis convention, phone/Safari support, offline snapshot
  parity (JS mirror consumes baked cards), 87-test suite grows with parity tests
  (card audit sums == existing engine numbers; golden cards for dad pinned).

## 8 · Milestones (strangler-fig — eng review D1: incremental over big-bang)

- **M1 — Engines + one new page (existing tabs untouched):** aspects.py, remedies.py
  (R1–R5), card component, a single new **为我 For Me** landing tab (per-member aspect
  cards + home/timing cards + actions), primer weights table, parity + golden tests.
  ~5 files; every current surface keeps working.
- **M2 — Our Home + Compare pages** ✅ shipped 2026-09-06: pages 2–3, R6 (pair
  remedies), room_fit_card; the Compare Homes preset shares the battlecard's
  optimal-arrangement basis (the emailable battlecard generator stays until a
  real need to retire it). Old tabs untouched.
- **M3 — Convergence** ✅ shipped 2026-09-06: report leads with a cards-first
  "0 · 速讀 At a glance" section (band matrix + top actions) before the working;
  snapshot bakes all card endpoints; Planner 择时 page (reno-window card +
  day/hour cards over the existing zeri engine); old tabs regrouped under a
  collapsible The Working 审计 nav. Each milestone shipped reversible.

## 8b · What already exists (reused, not rebuilt)

- `life_domains()` — five person-aspects with 0–100 scores + evidence chips: consumed
  as-is by aspects.py (career/wealth/learning/attraction/stability components).
- `score_direction`/`score_assignment` — room fits + cited breakdowns → affine-mapped.
- 文昌/學堂/祿/桃花 tables (shensha), health/industry maps (domains), afflictions +
  outlook (liunian), pair (hehun), structure texts (interpret) — all direct inputs.
- Remedy *content* already drafted as prose in interpret.py — extracted into
  remedies.py tables (7A), not rewritten.
- Card UI: existing `.section/.tag/.cite` styles + details-dropdown pattern; narrBlock
  precedent. Battlecard generator becomes a Compare preset in M2 — not a rebuild.

## 8c · NOT in scope (considered, deferred, rationale)

- Reactive offline card recompute (2A) — needs a JS composition mirror; drift risk
  outweighs benefit until someone actually asks for it.
- Compare/Planner pages + report/snapshot/battlecard convergence — M2/M3 by D1.
- Per-member auth/profiles — single-household local tool, no need.
- Weighted family aggregation (kids ×2, 6C) — invents non-classical weighting.
- New visual design system — cards reuse the existing parchment theme.
- 兼向替卦, exterior 巒頭 — pre-existing engine gaps, unchanged by this overhaul.

## 8d · Failure modes (new codepaths)

| Codepath | Realistic failure | Test? | Handled? | User sees |
|---|---|---|---|---|
| compose() member w/o room | KeyError on room lookup | §11 ✓ | degrade + meaning line | honest partial card |
| remedies conflict resolver | both rules emitted (silent contradiction) | §11 ✓ | 3A precedence | one action + deferred note |
| affine map | fit outside −1.8..+1.8 clamps silently | §11 ✓ | clamp + raw in audit | banded score, raw on tap |
| baked cards (snapshot) | stale vs live after config edit | regen flow ✓ | regen scripts | timestamped snapshot note |
| interpret.py refactor | wording drift breaks narrative meaning | §11 parity ✓ | template reuse | unchanged prose |

No critical gaps: every new path has a planned test and a visible (never silent) degradation.

## 8e · Parallelization

| Step | Modules touched | Depends on |
|---|---|---|
| remedies.py + tests | engine/ | — |
| aspects.py + tests | engine/ | remedies.py (actions on cards) |
| interpret.py refactor | engine/ | remedies.py |
| /api/aspects + baking | server.py | aspects.py |
| For Me page + card CSS | web/ | API shape (can stub from schema) |

Lane A: remedies → aspects → interpret refactor → API (sequential, shared engine/).
Lane B: card component + page against the schema stub (web/ only).
Launch A and B in parallel; merge; then browse QA. Conflict risk: low (disjoint dirs);
server.py touched only in A.

## 9 · Non-goals

Ziwei/Western systems; AI chat; exterior 峦头 without site data; medical claims
(health cards keep the TCM-correspondence disclaimer).

## 10 · Decisions (resolved in eng review, 2026-09-06)

1. **(4A)** 0–100 is the only user-facing scale, everywhere; zero-centred raw values
   retained inside audits. Rooms map: `clamp(50 + 25·fit, 5, 95)`.
2. **(5A)** Six aspects fixed; Relationship is ONE card = mean(attraction, stability),
   meaning line names the weaker half, both sub-scores + chips in the audit.
3. **(6A)** Home aggregation = family mean; the driver line ALWAYS names the weakest
   member and their top fix — comparable across homes, nothing buried.
4. **(3A)** Remedy conflicts: annual-star safety precedence beats person-用神 within
   the affected room for the current year; the deferred personal remedy stays in the
   audit tagged "resumes 立春 <date>". Conflicts are surfaced, never silent.
5. **(1A)** Input registry: each rule_id feeds exactly ONE component per card; §5
   weights operate on disjoint inputs (桃花位 removed from relationship — already in
   attraction; year-outlook overlap removed from luck). Enforced by a pytest that
   asserts no duplicate rule_id inside any card's audit.
6. **(2A)** Offline snapshots bake cards computed for the recommended arrangement
   (static), with a visible note; live site is fully reactive. No JS composition
   mirror.
7. **(7A)** interpret.py narrative advice strings are refactored in M1 to render from
   RemedyAction objects — remedies.py is the single source of remedy text; a
   wording-parity regression test guards the refactor.
8. Card schema carries `"v": 1` for the baked snapshot (cheap future-proofing).

### Cross-model tensions (outside voice — Claude subagent; all resolved)

- **T1-A** Resource arbitration table in remedies.py: one action per physical
  resource, declared priorities, losers kept in audit as `superseded` (§4).
- **T2-A** Table-driven `WEIGHTS`; goldens derived from the table; primer labels
  weights "calibration, not classical truth" (§5).
- **T3-A** Keep the affine map + a saturation-guard test; verified real fit range
  −1.20…+1.34, nothing saturates today (§5, §8d).
- **T4-A** Keep the 7-subject schema (all subjects already computed by the engine);
  renderers implement only the subjects their milestone ships (§3).
- **T5-A** Band word + colour is the primary visual, 5 quantised bands; the number is
  secondary; Compare still sorts numerically; full precision in audit (§3). Does not
  reopen 4A.

## 11 · M1 test requirements (from eng review coverage audit)

`tests/test_aspects_remedies.py` — all REQUIRED before M1 ships: golden dad cards
(six scores pinned); affine-map endpoints; input-registry no-dup-rule_id; parity
(audit Σ == existing engine numbers); home mean + weakest-driver; relationship
merge naming the weak half; R1 excess-drain/deficient-mother pairs; R2 star→remedy
classes incl. 五黃/二黑→metal, 三碧→fire, auspicious→activate; R3 明堂/dry-facing
cards; R4 affliction end-dates; R5 own-room vs desk fallback; conflict resolution
(annual wins, deferred remedy with resume date); interpret.py wording-parity
regression; unassigned-member degradation; no-文昌-room fallback; resource-arbitration
uniqueness (T1 — one action per resource per card); goldens derived from WEIGHTS
table (T2); saturation guard — every produced card inside the affine linear region
(T3); band quantisation boundaries 80/65/45/30 (T5). Plus browse QA:
For Me page render, phone 390px, offline snapshot static-cards note, existing tabs
regression (+1.86/+1.62 optimums intact).

## Implementation Tasks
Synthesized from this review's findings. Each task derives from a specific
finding above. Run with Claude Code or Codex; checkbox as you ship.

- [x] **T1 (P1, human: ~2d / CC: ~30min)** — engine — build `engine/remedies.py`: rule
  families R1–R5, resource-arbitration table (one action per physical resource, T1-A),
  annual-safety conflict precedence with deferred remedies tagged (3A)
  - Surfaced by: §4 remedy engine + outside-voice T1
  - Files: engine/remedies.py, tests/test_aspects_remedies.py
  - Verify: pytest -k remedies (arbitration uniqueness, 五黃/二黑→metal, conflict resume-date)
- [x] **T2 (P1, human: ~2d / CC: ~30min)** — engine — build `engine/aspects.py`:
  table-driven `WEIGHTS` (T2-A), disjoint input registry (1A), affine map + saturation
  guard (T3-A), 5-band quantisation 80/65/45/30 (T5-A), schema v:1
  - Surfaced by: §5 composition + outside-voice T2/T3/T5
  - Files: engine/aspects.py, tests/test_aspects_remedies.py
  - Verify: pytest -k aspects (goldens derived from WEIGHTS, no-dup rule_id, saturation, band edges)
- [x] **T3 (P1, human: ~1d / CC: ~20min)** — engine — refactor interpret.py advice
  strings to render from RemedyAction objects (7A) with wording-parity regression
  - Surfaced by: §10 decision 7A
  - Files: engine/interpret.py, engine/remedies.py, tests/test_aspects_remedies.py
  - Verify: wording-parity test — narrative output unchanged byte-for-byte
- [x] **T4 (P1, human: ~1d / CC: ~20min)** — server — `/api/aspects` endpoint + snapshot
  baking of static cards with visible note (2A)
  - Surfaced by: §6 IA + §10 decision 2A
  - Files: server.py, snapshot baking path
  - Verify: GET /api/aspects returns cards for all 5 members; snapshot carries static-cards note
- [x] **T5 (P1, human: ~2d / CC: ~40min)** — web — 为我 For Me landing tab + generic card
  component: band word + colour primary, number secondary (T5-A); render only
  person/room/home subjects in M1 (T4-A)
  - Surfaced by: §3 card contract + §6 IA + outside-voice T4/T5
  - Files: web/ (index.html/app.js/css)
  - Verify: browse QA — For Me renders 6 cards/member, audit dropdown opens, 390px phone
- [x] **T6 (P2, human: ~2h / CC: ~5min)** — web — primer gains the weights table
  labelled "calibration, not classical truth" (T2-A)
  - Surfaced by: §5 + outside-voice T2
  - Files: engine/primer.py
  - Verify: primer section renders the WEIGHTS table verbatim
- [x] **T7 (P2, human: ~2h / CC: ~10min)** — qa — browse regression: existing tabs
  unchanged, optimums +1.86/+1.62 intact, offline snapshot parity
  - Surfaced by: §11 test requirements
  - Files: tests/, browse QA
  - Verify: full pytest suite green + browse pass

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 0 | — | — |
| Codex Review | `/codex review` | Independent 2nd opinion | 0 | — | — |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 1 | CLEAR (PLAN) | 12 issues, 0 critical gaps |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | — | — |
| DX Review | `/plan-devex-review` | Developer experience gaps | 0 | — | — |

- **CROSS-MODEL:** outside voice via fresh-context Claude subagent (Codex not installed
  — same-family, not cross-model). 6 findings: 1 already resolved (stale doc), 5
  presented as tensions T1–T5; user resolved all 5 (T1-A arbitration, T2-A table-driven
  weights, T3-A saturation guard, T4-A schema kept/renderers deferred, T5-A band-first
  rendering). All folded into §3/§4/§5/§10.
- **VERDICT:** ENG CLEARED — ready to implement M1.

NO UNRESOLVED DECISIONS
