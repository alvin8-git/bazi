/* FengShui Family Compass — M2 UI (vanilla JS, no deps) */
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
  "釋释義义儀仪";
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
  "生氣": ["Vitality", "the best — growth, energy, opportunity; ideal for bed, desk, main door"],
  "天醫": ["Heavenly Doctor", "health and recovery; good bedroom direction when unwell"],
  "延年": ["Longevity", "harmony and relationships; supports couples and family bonds"],
  "伏位": ["Stability", "calm, steady progress; suits quiet work and rest"],
  "禍害": ["Mishap", "minor troubles and friction; fine for storage or bathrooms"],
  "六煞": ["Six Killings", "conflict and setbacks; avoid placing the bed here"],
  "五鬼": ["Five Ghosts", "instability, quarrels, losses; keep activity here light"],
  "絕命": ["Severed Fate", "the most adverse; avoid prolonged sleeping or sitting"],
};
const layerZh = (l) => LAYER_ZH[l] || l;

function explain(t, tab) {
  const p = state.primer && state.primer[tab];
  const primer = p ? `<h5 class="primer-head">FengShui/BaZi 101 — ${p.title}</h5>
    <div class="primer-grid">${p.items.map(([h, x]) =>
      `<div class="pcard"><h5>${h}</h5><p>${x}</p></div>`).join("")}</div>` : "";
  return `<details class="explain"><summary>ℹ️ How to read this page — FengShui/BaZi 101</summary>
    <div class="lede">${t}</div>${primer}</details>`;
}
const narrBlock = (i) => !i ? "" : `<div class="section interp">
    <h3>Narrative 解读 <span class="tag">rule-based · auto-generated · no AI</span></h3>
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
  <b>Legend 释义</b>${pairs.map(([t, d]) => `<span><b>${t}</b> — ${d}</span>`).join("")}</div>`;
const elb = (e) => `<span class="elb el-${e}">${e}</span>`;
const elbs = (a) => (a || []).map(elb).join("");
const sadv = (items, title = "Strategy 策略") => !items || !items.length ? "" :
  `<div class="sadv"><b>${title}</b>${items.map((x) => `<div>· ${dnAll(x)}</div>`).join("")}</div>`;

/* strategy report content distributed into its Reading sections */
function stratBlock(n, st) {
  const s = st && st["s" + n];
  if (!s) return "";
  switch (n) {
    case 2: return sadv([s.advice], "What this asks of you 策略");
    case 5: return `<div class="cite" style="margin-top:8px"><b>Monthly rhythm 节律</b>
        (recurring every year): green months feed this chart, red months drain it —
        schedule pushes into green months, recovery into red ones.</div>
      <div class="mos">${s.rhythm.map((m) => `<span class="mo ${m.cls}">${m.mon} ${m.br}${m.el}</span>`).join("")}</div>`;
    case 8: return `<div class="cite" style="margin-top:8px"><b>${s.kid
        ? "Partnership & friendship patterns 关系" : "Relationship patterns 感情"}:</b>
        primary risk point — ${dnAll(s.risk)}</div>
      ${s.evidence.map((e) => `<div class="cite">· ${dnAll(e)}</div>`).join("")}
      <div class="cite"><b>桃花:</b> ${s.taohua} · <b>生肖 allies:</b> ${s.allies.join(", ")}
        · <b>friction 生肖:</b> ${s.clash}</div>
      <div class="cite"><b>Element fit:</b> ${dnAll(s.el_line)}</div>
      ${sadv(s.advice)}`;
    case 10: return !s.handle.length ? "" : `<div class="cite" style="margin-top:8px">
        <b>${s.kid ? "How to parent them" : "How to work with them"}:</b>
        ${s.handle.map(dnAll).join(". ")}.</div>`;
    case 11: return `<div class="cite" style="margin-top:8px"><b>Trigger years:</b>
        ${s.trigger_years.join(", ") || "none flagged in the next decade"} ·
        <b>recovery years:</b> ${s.recovery_years.join(", ") || "—"}</div>
      ${sadv(s.advice)}`;
    case 12: return `<div class="sdial"><div class="sdialbar"><div style="width:${s.pct_corp}%"></div></div>
        <div class="sdialcap"><span>venture 创业型</span><b>${s.pct_corp}% structured</b>
          <span>corporate 体制型</span></div></div>
      <div class="cite"><b>${dnAll(s.verdict)}</b></div>
      <div class="cite">structure evidence: ${s.corp_ev.join(", ") || "—"} ·
        volatility evidence: ${s.vent_ev.join(", ") || "—"}</div>
      ${sadv(s.advice)}`;
    case 13: return `<div class="cite" style="margin-top:8px"><b>Wealth pattern 财富:</b>
        ${dnAll(s.wealth_pattern)} ${dnAll(s.wealth_carry)}</div>
      ${s.act_windows.length ? `<div class="cite"><b>Act-year windows:</b>
          ${s.act_windows.map((x) => "◉ " + dnAll(x)).join("<br>")}</div>`
        : `<div class="cite">no wealth-activation years in the next decade — build, don't chase</div>`}
      ${s.cautions.length ? `<div class="cite">⚠ hold-back years: ${s.cautions.join(", ")}</div>` : ""}
      ${s.handoff ? `<div class="cite"><b>Next-decade handoff:</b> ${dnAll(s.handoff)}</div>` : ""}
      ${s.exams.length ? `<div class="cite"><b>Exam-year overlay 考试年:</b><br>
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
      "The Working 审计 " + (nav.hidden ? "▾" : "▴");
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
  if (!state.primer) state.primer = await api("/api/primer");
  const q = `year=${state.year}&period=${state.period}&policy=${state.policy}`;
  [state.family, state.house] = await Promise.all([
    api(`/api/family?${q}`),
    api(`/api/house?year=${state.year}&method=${state.method}`),
  ]);
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
const BAND_EN = { strong: "Strong", good: "Good", fair: "Fair", weak: "Weak", poor: "Poor" };

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
    <details class="awork"><summary>▾ Show the classical working 审计</summary>
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
    ["性格 Temperament", p.axes.join(" · ") || "balanced, no strong tilt"],
    ["行业 Industries", p.industries.fav.map((i) => `${i.en}: ${i.list}`).join("; ")
      + ` <span class="neg">(avoid: ${p.industries.avoid.join(", ")})</span>`],
    ["健康 Organ watch", p.health.join(" · ") || "five elements in workable balance"],
    ["神煞 Stars", p.shensha.join(" · ") || "—"],
    ["流年 5-year", years],
    ["文昌 study palace", `${p.wenchang.palace}宮 → ${p.wenchang.rooms.join(", ") || "no room"}`],
    ["贵人 helpful-people", p.guiren.map((g) =>
      `${g.palace}宮 → ${g.rooms.join(", ") || "no room"}`).join(" · ") || "—"],
  ];
  return `<details class="profile-block"><summary>八字 profile 命理档案 ·
      命卦 ${p.gua} · day master ${p.day_master}</summary>
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
  return `<div class="section"><h3>Family harmony 合婚互动
      <span class="tag">day-pillar based · same in every home</span></h3>
    <table class="ptable">${head}${rows}</table>${rough}</div>`;
}

const auditHtml = (audit) => !audit ? "" : `<div class="section">
  <h3>Placement audit 宅内布局
    <span class="tag">缺角 · entry · stove · wet rooms · 財位</span></h3>
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
  el.innerHTML = jt(explain(
    `Everything personal on one page. Each card answers one question — <b>is this
     aspect of life supported, for this person, in this home, this year?</b> The
     <b>band word</b> (旺 strong · 优 good · 平 fair · 弱 weak · 忌 poor) is the
     reading; the number beside it only exists so cards can be compared and sorted —
     a 3-point gap is noise, a band gap is signal. Under it: what it means, the
     single biggest driver, and up to three concrete actions, each citing the rule
     that triggered it. Each person's <b>八字 profile 命理档案</b> dropdown adds
     their chart-level readings — temperament, favourable industries, organ watch,
     神煞 stars, a five-year 流年 outlook and where their 文昌/贵人 palaces fall in
     this house. At the bottom: the <b>family harmony matrix</b> — pair
     compatibility from the day pillars, identical in every home. Whole-house
     cards live on the Home tab; room assignment on the Rooms tab.`, "forme"))
    + note + people + harmony;
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
  el.innerHTML = jt(explain(
    `Property suitability on one page. Top: the eight home cards — six family-mean
     aspects (the driver line always names the weakest member and their top fix),
     plus the structure and this-year timing cards. Then the <b>placement audit
     宅内布局</b> — 缺角 missing corners, entry, stove, wet-room pressure and the
     財位 wealth spots, each judged against the classical rules. Below: <b>one
     suitability card per person for their assigned room</b> — the same
     three-layer fit (八宅 40% · 飞星 40% · 用神 20%) as the Rooms tab. At the
     bottom, the candidate homes side by side, each on its own optimal
     arrangement — the live battlecard.`, "ourhome"))
    + `<div class="section"><h3>${jt("Our Home 我们的家")}
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
  el.innerHTML = jt(explain(
    `Pick a comparison and read the SAME cards side by side — bands compare
     directly across columns. <b>三宅 Homes</b> puts the three homes' family-mean
     cards next to each other, each on its own optimal arrangement (the live
     version of the battlecard). <b>一人各房 Rooms</b> shows one person's
     suitability in every bedroom of this house. <b>配房方案 Arrangements</b>
     shows everyone's room card under the current vs the optimizer's best
     assignment.`, "compare"))
    + controls + `<div class="cmp-cols">${cols}</div>`;
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
  el.innerHTML = jt(explain(
    `Planning something — a move, a signing, a renovation? Top: the <b>修造
     renovation-window card</b> for the year — which traced rooms sit on this
     year's afflicted zones (fine to occupy, bad to drill) and until when. Then
     the month's <b>best days as cards</b>, rated by the classical 十二建除 day
     officers, minus 破日 and any day that clashes a family member's chart —
     each with its 吉時 best hours as actions. Small print names who, if anyone,
     should not lead an event that day.`, "planner"))
    + `<div class="cmp-bar"><label>Month 月份
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
  el.innerHTML = jt(explain(
    "<b>What this page shows:</b> one card per family member, computed from their birth " +
    "date &amp; time. The four chips are the BaZi <b>Four Pillars</b> (year·month·day·hour). " +
    "日主 is the Day Master — the element that represents the person — with a verdict on " +
    "whether it is strong or weak. 用神 lists the elements (and colours) that help balance " +
    "the chart. The trigram tag (e.g. 乾命) is the personal <b>Life Gua</b> used for lucky " +
    "directions, and “best sectors” are the compass directions of the house that score " +
    "highest for this person. <b>Click a card</b> for the full reading.", "family") +
    narrBlock(state.family.interpretation) +
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
const STEM_EL = { 甲: "木", 乙: "木", 丙: "火", 丁: "火", 戊: "土", 己: "土",
                  庚: "金", 辛: "金", 壬: "水", 癸: "水" };
const BR_EL = { 子: "水", 丑: "土", 寅: "木", 卯: "木", 辰: "土", 巳: "火",
                午: "火", 未: "土", 申: "金", 酉: "金", 戌: "土", 亥: "水" };
const BR_ANIMAL = { 子: "鼠", 丑: "牛", 寅: "虎", 卯: "兔", 辰: "龙", 巳: "蛇",
                    午: "马", 未: "羊", 申: "猴", 酉: "鸡", 戌: "狗", 亥: "猪" };

function chartCard(c) {
  const lp = c.life_palaces;
  const order = ["hour", "day", "month", "year"];
  const labels = { hour: "時 Hour", day: "日 Day", month: "月 Month", year: "年 Year" };
  const pcols = order.map((p) => {
    const gz = c.pillars[p], st = gz[0], br = gz[1];
    return `<div class="ccol${p === "day" ? " dm" : ""}">
      <div class="cclab">${labels[p]}</div>
      <div class="ccgod">${c.ten_gods[p] === "日主" ? "日主 DM" : c.ten_gods[p]}</div>
      <div class="ccstem" style="color:${EL_COL[STEM_EL[st]]}">${st}<span>${STEM_EL[st]}</span></div>
      <div class="ccbranch" style="color:${EL_COL[BR_EL[br]]}">${br}<span>${BR_ANIMAL[br]} ${BR_EL[br]}</span></div>
      <div class="ccstage">${c.pillar_extras[p].stage} · ${c.pillar_extras[p].nayin}</div>
      <div class="cchid">${c.hidden_gods[p].join("<br>")}</div>
    </div>`;
  }).join("");
  const favOrder = ["生氣", "天醫", "延年", "伏位"];
  const badOrder = ["禍害", "六煞", "五鬼", "絕命"];
  const dirOf = {};
  Object.entries(c.youxing).forEach(([pal, s]) => (dirOf[s] = PALACE_DIR[pal]));
  const dirPanel = (stars, cls) => `<div class="ccdirs ${cls}">${stars.map((s) =>
    `<div><b>${dirOf[s]}</b> ${s} <span>${BAZHAI_EN[s][0]}</span></div>`).join("")}</div>`;
  const dayun = `<div class="ccdayun">${c.dayun_detail.map((d) => `
    <div class="ccdy${d.current ? " now" : ""}"><div class="ccdyage">${d.ages}</div>
      <div class="ccdygz">${d.gz}</div>
      <div class="ccdygod">${d.stem_god}/${d.branch_god}</div>
      ${d.current ? `<div class="ccdyhere">▲ ${state.year} 在此</div>` : ""}</div>`).join("")}</div>`;
  const tg = Object.entries(c.tengods_pct).sort((a, b) => b[1] - a[1]);
  const tgmax = Math.max(...tg.map(([, v]) => v)) || 1;
  const bars = tg.map(([g, v]) => `<div class="cctgrow"><span class="cctgl">${g}
      ${c.tengods_legend[g].en}</span>
    <div class="cctgbar"><div style="width:${Math.round(v / tgmax * 100)}%"></div></div>
    <span class="cctgv">${v.toFixed(0)}%</span></div>`).join("");
  const stars = c.shensha.map((s) => s.star).join(" · ");
  return `<div class="ccard">
    <div class="cchead">
      <div class="ccbig"><div class="ccgua">${c.gua}</div>
        <div>命卦 ${c.gua} (${c.group}) · 命星 ${lp.life_star_zh} ${lp.life_star_element}</div></div>
      <div class="ccfacts">
        <div><span>生肖</span>${lp.animal}</div>
        <div><span>日主</span>${c.day_master} ${STEM_EL[c.day_master]} · ${c.strength.verdict}</div>
        <div><span>命宮</span>${lp.ming_gong}</div>
        <div><span>用神</span>${elbs(c.yongshen.favourable)} <em>avoid</em> ${elbs(c.yongshen.unfavourable)}</div>
        <div><span>神煞</span>${stars}</div>
        <div><span>胎元</span>${lp.tai_yuan}</div>
      </div>
    </div>
    <div class="ccpillars">${pcols}</div>
    <div class="ccdirwrap">${dirPanel(favOrder, "fav")}${dirPanel(badOrder, "bad")}</div>
    ${dayun}
    <div class="cctg">${bars}</div>
  </div>`;
}

/* personalised 生剋 wheel: node size = element share, gold ring = Day Master,
   green arrows = generating cycle, red = controlling (solid when afflicted) */
function elementWheel(er) {
  const ORDER = ["火", "土", "金", "水", "木"];
  const cx = 130, cy = 130, R = 88;
  const pos = {};
  ORDER.forEach((el, i) => {
    const a = (-90 + i * 72) * Math.PI / 180;
    pos[el] = [cx + R * Math.cos(a), cy + R * Math.sin(a)];
  });
  const rOf = el => 13 + Math.min(er.share[el] || 0, 40) * 0.32;
  const seg = (a, b) => {
    const [x1, y1] = pos[a], [x2, y2] = pos[b];
    const d = Math.hypot(x2 - x1, y2 - y1), ux = (x2 - x1) / d, uy = (y2 - y1) / d;
    return [x1 + ux * (rOf(a) + 3), y1 + uy * (rOf(a) + 3),
            x2 - ux * (rOf(b) + 8), y2 - uy * (rOf(b) + 8)];
  };
  const SHENG_P = [["木", "火"], ["火", "土"], ["土", "金"], ["金", "水"], ["水", "木"]];
  const KE_P = [["木", "土"], ["土", "水"], ["水", "火"], ["火", "金"], ["金", "木"]];
  const aff = new Set((er.afflictions || []).map(p => p.join()));
  let s = `<svg viewBox="0 0 260 270" class="ewheel"><defs>
    <marker id="mS" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5" markerHeight="5.5"
      orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#7aa87f"/></marker>
    <marker id="mK" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5" markerHeight="5.5"
      orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#d5b3b0"/></marker>
    <marker id="mKa" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6"
      orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#b03a2e"/></marker></defs>`;
  KE_P.forEach(([a, b]) => {
    const [x1, y1, x2, y2] = seg(a, b), bad = aff.has(a + "," + b);
    s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"
      stroke="${bad ? "#b03a2e" : "#d5b3b0"}" stroke-width="${bad ? 3 : 1.3}"
      ${bad ? "" : 'stroke-dasharray="4 3"'} marker-end="url(#${bad ? "mKa" : "mK"})"/>`;
  });
  SHENG_P.forEach(([a, b]) => {
    const [x1, y1, x2, y2] = seg(a, b);
    s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#7aa87f"
      stroke-width="${Math.max(1.2, Math.min(4, (er.share[a] || 0) / 9))}"
      opacity="${(er.share[a] || 0) < 6 ? 0.35 : 0.9}" marker-end="url(#mS)"/>`;
  });
  ORDER.forEach(el => {
    const [x, y] = pos[el], r = rOf(el);
    s += `<circle cx="${x}" cy="${y}" r="${r}" fill="${EL_COL[el]}" opacity=".92"/>`;
    if (el === er.dm) s += `<circle cx="${x}" cy="${y}" r="${r + 3.5}" fill="none"
      stroke="var(--gold)" stroke-width="2.5"/>`;
    s += `<text x="${x}" y="${y + 5.5}" text-anchor="middle" font-size="15"
      font-weight="700" fill="#fff">${el}</text>
      <text x="${x}" y="${y + r + 13}" text-anchor="middle" font-size="9.5"
      fill="#6b6357">${er.share[el]}%${el === er.dm ? " 日主" : ""}</text>`;
  });
  return s + "</svg>";
}

/* 十神对照 wheel: 日元 centre, five god-groups in the 生剋 pentagon (each
   coloured by ITS element for this chart), yin/yang god pairs as satellites */
function tenGodsWheel(c) {
  const pct = c.tengods_pct || {};
  const p = keys => { for (const k of keys) if (pct[k] != null) return pct[k]; return 0; };
  const dmEl = STEM_EL[c.day_master];
  const S = {木:"火",火:"土",土:"金",金:"水",水:"木"};
  const K = {木:"土",土:"水",水:"火",火:"金",金:"木"};
  const invS = {火:"木",土:"火",金:"土",水:"金",木:"水"};
  const invK = {土:"木",水:"土",火:"水",金:"火",木:"金"};
  const GROUPS = [
    {zh:"官殺", el:invK[dmEl], gods:[["正官"],["七殺","七杀"]], lab:["正官","七殺"]},
    {zh:"印星", el:invS[dmEl], gods:[["正印"],["偏印"]], lab:["正印","偏印"]},
    {zh:"比劫", el:dmEl, gods:[["比肩"],["劫財","劫财"]], lab:["比肩","劫財"]},
    {zh:"食傷", el:S[dmEl], gods:[["食神"],["傷官","伤官"]], lab:["食神","傷官"]},
    {zh:"財星", el:K[dmEl], gods:[["正財","正财"],["偏財","偏财"]], lab:["正財","偏財"]},
  ];
  const cx = 170, cy = 170, R1 = 86, R2 = 141;
  GROUPS.forEach((g, i) => {
    g.a = (-90 + i * 72) * Math.PI / 180;
    g.x = cx + R1 * Math.cos(g.a); g.y = cy + R1 * Math.sin(g.a);
    g.sum = Math.round((p(g.gods[0]) + p(g.gods[1])) * 10) / 10;
    g.r = 15 + Math.min(g.sum, 45) * 0.3;
    g.sat = g.gods.map((keys, j) => {
      const a2 = g.a + (j ? 1 : -1) * 0.42;
      const v = p(keys);
      return {x: cx + R2 * Math.cos(a2), y: cy + R2 * Math.sin(a2),
              v, r: 9.5 + Math.min(v, 35) * 0.27, lab: g.lab[j]};
    });
  });
  const seg = (x1, y1, r1, x2, y2, r2) => {
    const d = Math.hypot(x2 - x1, y2 - y1) || 1, ux = (x2 - x1) / d, uy = (y2 - y1) / d;
    return [x1 + ux * (r1 + 3), y1 + uy * (r1 + 3), x2 - ux * (r2 + 7), y2 - uy * (r2 + 7)];
  };
  const G = i => GROUPS[i];
  const SHENGI = [[2, 3], [3, 4], [4, 0], [0, 1], [1, 2]];   // 比劫→食傷→財→官殺→印→比劫
  const KEI = [[2, 4], [3, 0], [4, 1], [0, 2], [1, 3]];      // 剋 star
  let s = `<svg viewBox="0 0 340 345" class="ewheel tgwheel"><defs>
    <marker id="tS" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5" markerHeight="5.5"
      orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#7aa87f"/></marker>
    <marker id="tK" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5" markerHeight="5.5"
      orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#c98a86"/></marker></defs>`;
  GROUPS.forEach(g => g.sat.forEach(t => {                    // connectors first
    s += `<line x1="${g.x}" y1="${g.y}" x2="${t.x}" y2="${t.y}"
      stroke="#cbc2b4" stroke-width="1" stroke-dasharray="2 3"/>`;
  }));
  KEI.forEach(([a, b]) => {
    const [x1, y1, x2, y2] = seg(G(a).x, G(a).y, G(a).r, G(b).x, G(b).y, G(b).r);
    s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#d5b3b0"
      stroke-width="1.3" stroke-dasharray="4 3" marker-end="url(#tK)"/>`;
  });
  SHENGI.forEach(([a, b]) => {
    const [x1, y1, x2, y2] = seg(G(a).x, G(a).y, G(a).r, G(b).x, G(b).y, G(b).r);
    s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#7aa87f"
      stroke-width="${Math.max(1.2, Math.min(4, G(a).sum / 10))}"
      opacity="${G(a).sum < 5 ? 0.35 : 0.85}" marker-end="url(#tS)"/>`;
  });
  s += `<circle cx="${cx}" cy="${cy}" r="20" fill="${EL_COL[dmEl]}"/>
    <circle cx="${cx}" cy="${cy}" r="23.5" fill="none" stroke="var(--gold)" stroke-width="2.5"/>
    <text x="${cx}" y="${cy + 1}" text-anchor="middle" font-size="13" font-weight="700"
      fill="#fff">${c.day_master}</text>
    <text x="${cx}" y="${cy + 13}" text-anchor="middle" font-size="8.5" fill="#fff">日元</text>`;
  GROUPS.forEach(g => {
    s += `<circle cx="${g.x}" cy="${g.y}" r="${g.r}" fill="${EL_COL[g.el]}" opacity=".92"/>
      <text x="${g.x}" y="${g.y + 4.5}" text-anchor="middle" font-size="12.5"
        font-weight="700" fill="#fff">${g.zh}</text>
      <text x="${g.x}" y="${g.y + g.r + 11}" text-anchor="middle" font-size="9"
        fill="#6b6357">${g.sum}%</text>`;
    g.sat.forEach(t => {
      s += `<circle cx="${t.x}" cy="${t.y}" r="${t.r}" fill="${EL_COL[g.el]}"
        opacity="${t.v < 5 ? 0.35 : 0.68}"/>
      <text x="${t.x}" y="${t.y + 3.5}" text-anchor="middle" font-size="9.5"
        font-weight="700" fill="#fff">${t.lab}</text>
      <text x="${t.x}" y="${t.y + t.r + 10}" text-anchor="middle" font-size="8.5"
        fill="#6b6357">${t.v}%</text>`;
    });
  });
  return s + "</svg>";
}

const LEGENDS = {
  chart: [
    ["四柱 八字", "the Four Pillars: birth year·month·day·hour, each written as two characters — eight in all"],
    ["天干 / 地支", "the top character of a pillar is its heavenly stem, the bottom its earthly branch (with the zodiac animal)"],
    ["日主 Day Master", "the day stem — the character that IS you; every other character is read by its relationship to it"],
    ["十神 Ten Gods", "that relationship, named — translated god-by-god in §4"],
    ["藏干", "hidden stems: extra elements stored inside each branch, listed under the pillar"],
    ["生肖", "the zodiac animal of the birth-year branch"],
    ["命卦", "your personal trigram — decides your lucky compass directions (§7)"],
    ["命星", "the life star (九星) of the birth year — the number 風水 overlays use for you"],
    ["命宮 Life Palace", "an auxiliary destiny point derived from the birth month + hour — classical readers weigh it for temperament and life theme"],
    ["胎元 Conception Palace", "the pillar of the estimated conception month — a supplementary root the chart can draw on"],
    ["用神", "the elements that act as this chart's medicine (§5)"],
    ["神煞", "symbolic stars carried by the pillars — detailed with meanings in §9"],
    ["納音", "the pillar's melodic element — its poetic name in the 60-cycle (e.g. 海中金)"],
    ["長生 stage", "the Day Master's life-stage in that branch (birth→peak→decline cycle) — vitality flavour, not a verdict"],
    ["大運", "the 10-year luck cycles that colour each decade (§6)"],
  ],
  1: [["木/火/土/金/水", "wood / fire / earth / metal / water"],
    ["weight", "weighted count of visible + hidden characters carrying that element"],
    ["reading it", "balance beats abundance — the tallest bar is the heaviest, not the best"],
    ["wheel: node size", "that element's share of THIS chart; gold ring = your Day Master"],
    ["green arrows 生", "the generating cycle (wood→fire→earth→metal→water) — thicker = stronger feeder"],
    ["red lines 剋", "the controlling cycle — solid red = an actual affliction in this chart (a heavy element crushing a weak one)"],
    ["生我/我生/我剋/剋我/同我", "the five roles every element plays relative to the Day Master — resource, output, wealth, pressure, peers; the ten gods refine these"]],
  2: [["身強 strong", "the chart can afford to spend — output, wealth and pressure suit it"],
    ["身弱 weak", "the chart needs feeding — support, rest and resource suit it"],
    ["support ratio", "share of the chart on the Day Master's side"],
    ["root mass", "the Day Master's own element hidden inside the branches — its anchoring"]],
  3: [["Stem row", "the ten god of each pillar's visible character"],
    ["藏干 row", "the gods of the hidden stems inside each branch"],
    ["正 / 偏 / 七殺 …", "each god's name and meaning is translated in §4's list"]],
  4: [["正◯ vs 偏◯", "正 = the proper/conventional form of a domain, 偏 = its unconventional twin (the image's 异性/同性 pairing)"],
    ["%", "share of the chart's characters classified as that god — where life's attention defaults"],
    ["wheel: 日元 centre", "your Day Master; the five groups around it are the five roles from §1's element wheel, refined into gods"],
    ["node colour & size", "colour = that group's actual element for YOUR Day Master (§1 palette); size = its share of the chart"],
    ["green / red arrows", "生 feeding and 剋 controlling cycles between the god groups — same cycles as §1, one level up"],
    ["satellites", "each group's 正/偏 pair with its own share — faded = barely present"]],
  5: [["用神 / 喜", "favourable — the chart's medicine; carry these elements in colours, directions, fields"],
    ["忌 avoid", "elements that aggravate the imbalance"],
    ["扶抑法", "support-the-weak / restrain-the-strong: the method that picked them"],
    ["調候", "seasonal climate cross-check (a winter chart may need fire regardless)"]],
  6: [["大運", "one pillar per decade of life, starting from the month pillar"],
    ["ages", "your age span under that pillar"],
    ["god labels", "the decade's dominant themes, in §4's vocabulary"],
    ["highlighted", "the decade you are in now"]],
  7: [["八宅", "eight-house school: your trigram splits the compass into 4 green (use) and 4 red (avoid) directions"],
    ["how to use", "green = bed headboard, desk facing, main door; red = fine for storage/bathroom"],
    ["personal", "this map differs per person — a couple can have opposite maps"]],
  8: [["score", "starts at a neutral 50; every chip is a rule that moved it"],
    ["≥70", "a natural strength"], ["<45", "an area to consciously support"],
    ["chips", "the audit trail — hover none, they are the working"]],
  9: [["神煞", "symbolic stars: classical stem-branch patterns, flavour on top of structure"],
    ["年/月/日/時 tag", "which pillar carries it — ancestry · career/parents · self/spouse · children/later life"]],
  10: [["axes", "read straight off §4's distribution — the basis column shows the exact threshold"],
    ["no strong tendency", "a legitimate result, not a failure"]],
  11: [["element ↔ organs", "traditional five-element medicine correspondence — reference, not medical advice"],
    ["status", "flags an element too weak or too heavy to lean on"]],
  12: [["fit", "how efficiently effort converts to reward in that field"],
    ["priced against", "low-ranked fields cost more energy here — never forbidden"]],
  13: [["◉ window", "a supportive year for that life dimension"],
    ["⚠ caution", "navigate deliberately — a note, never a verdict"],
    ["· quiet", "nothing notable triggered"],
    ["climate / weather", "the decade sets the climate, the year the weather"],
    ["桃花", "peach-blossom: the romance/charm activation branch"]],
};

async function renderPerson(name) {
  const url = window.__CHART_URL__ ||
    `/api/chart/${encodeURIComponent(name)}?policy=${state.policy}&year=${state.year}`;
  const c = await api(url);
  const nb = splitNarr(c.interpretation);
  const narr = (n) => (nb.by[n] || []).map((t) =>
    `<div class="ninline"><b>解读 Narrative:</b> ${dnAll(t)}</div>`).join("");
  const lg = (k) => legendBlock(LEGENDS[k]);
  const stb = (n) => stratBlock(n, c.strategy);
  const wmax = Math.max(...Object.values(c.element_weights));
  const EL_ZH = { Wood: "木", Fire: "火", Earth: "土", Metal: "金", Water: "水" };
  $("#tab-person").innerHTML = jt(explain(
    "<b>What this page shows:</b> the full BaZi reading, laid out like a geomancer's report. " +
    "The birth moment is converted to <b>true solar time</b> (Singapore ran on UTC+7:30 before " +
    "1982), then mapped to four stem-branch pillars. The element bars show the balance of the " +
    "Five Elements in the chart; the strength steps explain <i>why</i> the Day Master is judged " +
    "strong or weak; 十神 (Ten Gods) name each pillar's relationship to the Day Master; 大运 " +
    "are the 10-year luck cycles; and the 八宅 row grades each compass direction for this " +
    "person (green = favourable, red = avoid). Every number cites the rule that produced it.",
    "person") + `
    <h2>${dn(name || c.name)} — Four Pillars (${state.policy === "true_solar" ? "TRUE SOLAR" : "CLOCK"})</h2>
    <div class="sub">effective time ${c.effective_time}</div>
    ${chartCard(c)}
    ${nb.rest.length ? narrBlock({ paragraphs: nb.rest }) : ""}
    <div class="pillar-cards">${POS.map((k) => `
      <div class="pillar-card"><div class="gz">${c.pillars[k]}</div>
        <div class="pos">${POS_LAB[k]}</div>
        <div class="god">${c.ten_gods[k] || ""}</div>
        <div class="sub">${c.pillar_extras[k].nayin} · ${c.pillar_extras[k].stage}</div></div>`).join("")}
      ${c.transit.luck ? `<div class="pillar-card transit"><div class="gz">${c.transit.luck.gz}</div>
        <div class="pos">LUCK 大運</div>
        <div class="god">${c.transit.luck.stem_god}/${c.transit.luck.branch_god}</div>
        <div class="sub">ages ${c.transit.luck.ages}</div></div>` : ""}
      <div class="pillar-card transit"><div class="gz">${c.transit.year_gz}</div>
        <div class="pos">YEAR 流年 ${state.year}</div>
        <div class="god">${c.transit.year_stem_god}/${c.transit.year_branch_god}</div>
        <div class="sub">annual transit</div></div>
    </div>
    <div class="cite" style="margin:-6px 0 10px">The four solid cards are the birth chart
      (fixed for life); the two dashed cards are the energies currently overlaid on it —
      the active 10-year luck pillar and this year's pillar — labelled with their ten
      gods relative to this Day Master.</div>
    ${lg("chart")}
    <div class="section"><h3>1. Five Elements Balance 五行</h3>
      <div class="bars">${Object.entries(c.element_weights).map(([en, v]) => `
        <div class="bar-row el-${EL_ZH[en]}"><span>${elb(EL_ZH[en])} ${en}</span>
          <div class="bar"><i style="width:${(100 * v / wmax).toFixed(0)}%"></i></div>
          <b>${v.toFixed(1)}</b></div>`).join("")}
      </div>
      ${c.element_relations ? `<h4>Interaction between the five elements 生剋</h4>
      <div class="ewrap">${elementWheel(c.element_relations)}
        <div class="eflows">
          <div class="cite" style="margin:0 0 6px">How every other element relates to
            YOUR Day Master ${elb(c.element_relations.dm)} — the same five roles the
            ten gods (§3–4) are built from:</div>
          ${["resource", "output", "wealth", "pressure", "peer"].map((k) => {
            const f = c.element_relations.flows[k];
            return `<div class="eflow"><span class="efr">${f.role}</span>
              ${elb(f.el)} <b>${f.share}%</b>
              <span class="efb ef-${f.band}">${f.band}</span>
              <span class="sub">${f.meaning}</span></div>`;
          }).join("")}
        </div>
      </div>` : ""}
      ${narr(1)}${lg(1)}</div>
    <div class="section"><h3>2. Core Identity &amp; Day Master</h3>
      <p>Day Master <b>${c.day_master}</b> — <b>${c.strength.verdict}</b> (score ${c.strength.score})
        <span class="tag">support ratio ${c.strength.support_ratio}%</span>
        <span class="tag">root mass ${c.strength.root_ratio}%</span>
        <span class="tag">${c.strength.formation.status}</span></p>
      <div class="cite">Formation check: ${c.strength.formation.detail}. Support ratio =
        share of the chart feeding the Day Master; root mass = share of hidden stems
        carrying its element.</div>
      ${c.strength.steps.map((s) => `<div class="cite"><b>${s.step}. ${s.name}:</b> ${s.value} — ${s.detail}</div>`).join("")}
      ${stb(2)}${narr(2)}${lg(2)}
    </div>
    <div class="section"><h3>3. Ten Gods 十神 (hidden stems)</h3>
      <div class="cite" style="margin:0 0 6px">The raw data behind sections 4–10: the
        Stem row classifies each visible character's relationship to the Day Master;
        the 藏干 row lists the stems hidden inside each branch with their own
        classifications. Section 4 summarises this table as percentages.</div>
      <table><tr><th></th>${POS.map((k) => `<th>${POS_LAB[k]}</th>`).join("")}</tr>
        <tr><th>Stem</th>${POS.map((k) => `<td>${c.ten_gods[k]}</td>`).join("")}</tr>
        <tr><th>藏干</th>${POS.map((k) => `<td>${(c.hidden_gods[k] || []).join("<br>")}</td>`).join("")}</tr>
      </table>${narr(3)}${lg(3)}</div>
    <div class="section"><h3>4. Ten-god distribution 十神分布</h3>
      <div class="cite" style="margin:0 0 8px">Section 3 summarised as percentages —
        how the chart's energy is divided among the ten archetypes (weighted count of
        visible + hidden stems). Where the chart is heavy shows where life's attention
        naturally goes; a faint or missing god marks a domain that needs deliberate
        effort.</div>
      <div class="ewrap"><div class="tgwrap">${tenGodsWheel(c)}
        <div class="cite" style="text-align:center;margin-top:2px">十神对照 — each group
          coloured by ITS element for this Day Master (same palette as §1)</div></div>
      <div class="bars" style="flex:1;min-width:280px;max-width:680px">${Object.entries(c.tengods_pct).map(([g, p]) => `
        <div class="bar-row tg-row"><span><b>${g}</b> <span class="sub">${c.tengods_legend[g].en}</span></span>
          <div class="bar"><i style="width:${p}%;background:var(--gold)"></i></div>
          <b>${p}%</b><span class="sub tg-meaning">${c.tengods_legend[g].meaning}</span></div>`).join("")}
      </div></div>
      ${(() => {
        const e = Object.entries(c.tengods_pct);
        const [g1, p1] = e[0], [g2, p2] = e[1];
        const faint = e.filter(([, p]) => p < 5).map(([g]) => g);
        return `<div class="cite" style="margin-top:8px"><b>Reading:</b> this chart is
          heaviest in ${g1} ${c.tengods_legend[g1].en} (${p1}% — ${c.tengods_legend[g1].meaning})
          and ${g2} ${c.tengods_legend[g2].en} (${p2}%).${faint.length ? ` Faint: ${faint.map((g) =>
            `${g} ${c.tengods_legend[g].en}`).join(", ")} — ${faint.length > 1 ? "these domains" : "this domain"}
            won't come automatically and rewards conscious effort.` : ""}</div>`;
      })()}
      ${(() => {
        const sex = ((state.family ? state.family.people : [])
          .find((p) => p.name === name) || {}).sex || c.sex;
        const grp = (gods) => Math.round(gods.reduce((a, g) => a + (c.tengods_pct[g] || 0), 0) * 10) / 10;
        const band = (p) => p >= 20 ? "prominent" : p >= 8 ? "present" : p > 0 ? "faint" : "absent";
        const rows = [
          ["配偶星 Spouse star", sex === "M"
            ? "正財+偏財 — in a man's chart the partner is represented by the wealth gods"
            : "正官+七殺 — in a woman's chart the partner is represented by the authority gods",
            sex === "M" ? ["正財", "偏財"] : ["正官", "七殺"]],
          ["財星 Wealth stars", "正財+偏財 — income, assets, practical results", ["正財", "偏財"]],
          ["官殺 Authority stars", "正官+七殺 — career, status, discipline, pressure", ["正官", "七殺"]],
          ["印 Resource stars", "正印+偏印 — learning, support, protection, credentials", ["正印", "偏印"]],
          ["食傷 Output stars", "食神+傷官 — expression, creativity, charm", ["食神", "傷官"]],
          ["比劫 Peer stars", "比肩+劫財 — self-drive, siblings, competition", ["比肩", "劫財"]],
        ];
        return `<h4 style="margin-top:12px">Star-type reference 星名對照
            <span class="tag">the vocabulary used by the §8 evidence chips</span></h4>
          <table><tr><th>Term</th><th>Which ten gods &amp; what they mean</th><th>This chart</th></tr>
            ${rows.map(([t, d, gods]) => { const p = grp(gods);
              return `<tr><td><b>${t}</b></td><td class="sub">${d}</td>
                <td class="${p >= 8 ? "good" : p === 0 ? "bad" : ""}">${p}% — ${band(p)}</td></tr>`; }).join("")}
          </table>
          <div class="cite">Bands: ≥20% prominent · ≥8% present · &lt;8% faint · 0% absent —
            the same thresholds behind chips like "spouse star faint". 配偶宮 Spouse palace =
            the DAY branch (here ${c.pillars.day[1]}); clashes or combinations to it are read
            in §8 Relationship stability. 財庫 wealth vault = the storage branch of the
            wealth element (one of 辰戌丑未).</div>`;
      })()}
      ${narr(4)}${lg(4)}
    </div>
    <div class="section"><h3>5. 用神 Favourable Elements</h3>
      <p>Favourable: ${elbs(c.yongshen.favourable)} · avoid ${elbs(c.yongshen.unfavourable)}
         · colours <b>${c.yongshen.colours.join("、")}</b></p>
      ${c.yongshen.citations.map((x) => `<div class="cite"><b>${x.source_ref}:</b> ${x.explanation}</div>`).join("")}
      ${stb(5)}${narr(5)}${lg(5)}
    </div>
    <div class="section"><h3>6. Luck Cycles 大運</h3>
      <div class="cite" style="margin:0 0 6px">Each 10-year decade is labelled by the ten
        gods its two characters bring — a hint of the decade's dominant themes. The
        highlighted column is the current decade.</div>
      <div style="overflow-x:auto"><table><tr>${c.dayun_detail.map((d) =>
          `<th class="${d.current ? "cur-dayun" : ""}">${d.gz}</th>`).join("")}</tr>
        <tr>${c.dayun_detail.map((d) => `<td class="${d.current ? "cur-dayun" : ""}">${d.ages}</td>`).join("")}</tr>
        <tr>${c.dayun_detail.map((d) => `<td class="${d.current ? "cur-dayun" : ""}">
          <b>${d.stem_god}/${d.branch_god}</b><div class="sub" style="max-width:120px">${d.keywords}</div></td>`).join("")}</tr>
      </table></div>${narr(6)}${lg(6)}</div>
    <div class="section"><h3>7. 八宅 Directions (${c.gua}命 · ${c.group})</h3>
      <div class="cite" style="margin:0 0 6px">Your personal trigram splits the compass
        into four lucky (green) and four unlucky (red) directions — a different map for
        each person. Use green directions for the things you do for hours (bed
        headboard, desk facing, main door); red directions are fine for storage and
        bathrooms.</div>
      <table><tr><th>Palace</th>${Object.keys(c.youxing).map((p) => `<th>${p}</th>`).join("")}</tr>
        <tr><td>Direction</td>${Object.keys(c.youxing).map((p) => `<td>${PALACE_DIR[p]}</td>`).join("")}</tr>
        <tr><td>遊年星</td>${Object.values(c.youxing).map((s) =>
          `<td class="${["生氣", "天醫", "延年", "伏位"].includes(s) ? "good" : "bad"}">${s}</td>`).join("")}</tr>
      </table>
      ${BAZHAI_ORDER.map((s) => `<div class="cite"><b>${s} ${BAZHAI_EN[s][0]}</b> — ${BAZHAI_EN[s][1]}</div>`).join("")}
      ${(() => {
        const good = Object.entries(c.youxing)
          .filter(([, s]) => ["生氣", "天醫", "延年", "伏位"].includes(s))
          .sort((a, b) => BAZHAI_ORDER.indexOf(a[1]) - BAZHAI_ORDER.indexOf(b[1]))
          .map(([p, s]) => `${PALACE_DIR[p]} (${s})`).join(", ");
        const bad = Object.entries(c.youxing)
          .filter(([, s]) => ["絕命", "五鬼"].includes(s))
          .map(([p, s]) => `${PALACE_DIR[p]} (${s})`).join(", ");
        return `<div class="cite" style="margin-top:7px"><b>Reading:</b> point the
          headboard/desk toward ${good}. The heaviest cautions are ${bad} — avoid
          sleeping or long sitting oriented to these. The Rooms tab applies exactly
          this map when scoring bedroom sectors.</div>`;
      })()}
      ${narr(7)}${lg(7)}
    </div>
    <div class="section"><h3>8. Life-domain signals 人生領域
        <span class="tag warn">structural tendencies · not guarantees</span></h3>
      <div class="cite" style="margin:0 0 8px">Each score starts at a neutral 50; every
        chip below shows a rule that moved it up or down. Above 70 = a natural strength,
        below 45 = an area to consciously support.</div>
      <div class="domain-grid">${c.domains.map((d) => `
        <div class="dcard"><div class="dscore ${d.score >= 70 ? "good" : d.score < 45 ? "bad" : ""}">${d.score}</div>
          <b>${d.en}</b> <div class="sub">${d.zh} · ${d.band}</div>
          <div style="margin-top:5px">${d.evidence.map((e) =>
            `<span class="tag ${e.delta < 0 ? "warn" : ""}">${e.label} ${e.delta > 0 ? "+" : ""}${e.delta}</span>`).join(" ")}</div>
        </div>`).join("")}
      </div>${stb(8)}${narr(8)}${lg(8)}</div>
    ${c.shensha.length ? `<div class="section"><h3>9. 神煞 Symbolic stars</h3>
      <div class="cite" style="margin:0 0 8px">Special stem-branch patterns from classical
        lookup tables — flavour on top of the structural reading. The small tag shows
        which pillar (year=ancestry/childhood, month=career/parents, day=self/spouse,
        hour=later life/children) carries each star.</div>
      ${c.shensha.map((s) => `<div class="cite"><b>${s.star}</b>
        <span class="tag">${s.pillars.join("·")}</span> ${s.meaning}</div>`).join("")}
      ${c.interactions.length ? `<div class="cite" style="margin-top:7px"><b>Natal branch interactions:</b>
        ${c.interactions.map((i) => `${i.pair} ${i.kind} (${i.pillars.join("+")}) — ${i.note}`).join("; ")}</div>` : ""}
      ${narr(9)}${lg(9)}
    </div>` : ""}
    <div class="section"><h3>10. Personality axes 性格軸 <span class="tag warn">modern synthesis · tendencies only</span></h3>
      <div class="cite" style="margin:0 0 6px">Five axes read straight off the ten-god
        distribution above — the basis column shows the exact share and threshold behind
        each verdict. "No strong tendency" is a legitimate result, not a failure.</div>
      <table><tr><th>Axis</th><th>Verdict</th><th>Basis</th></tr>
        ${c.personality.map((a) => `<tr><td>${a.axis}</td>
          <td class="${a.verdict === "no strong tendency" ? "" : "good"}">${a.verdict}</td>
          <td class="sub">${a.basis}</td></tr>`).join("")}
      </table>${stb(10)}${narr(10)}${lg(10)}</div>
    <div class="section"><h3>11. Health element map 健康
        <span class="tag warn">TCM correspondence · reference, not medical advice</span></h3>
      <div class="cite" style="margin:0 0 6px">Traditional five-element medicine maps
        each element to organ systems; a very weak or excessive element in the chart
        marks the systems worth caring for.</div>
      <table><tr><th>Element</th><th>Share</th><th>Organ systems</th><th>Watch aspects</th><th>Status</th></tr>
        ${c.health.map((hh) => `<tr><td>${elb(hh.element)} ${hh.en}</td><td>${hh.share}%</td>
          <td class="sub">${hh.organs}</td><td class="sub">${hh.aspects}</td>
          <td class="${hh.status.startsWith("balanced") ? "" : "bad"}">${hh.status}</td></tr>`).join("")}
      </table>
      ${stb(11)}${narr(11)}${lg(11)}
    </div>
    ${c.careers ? `<div class="section"><h3>12. Career paths 事業方向
        <span class="tag warn">rule-based ranking · fit, not fate</span></h3>
      <div class="cite" style="margin:0 0 8px">Fifteen career archetypes, each scored on
        three cited terms: the field's element(s) against the 用神 lists, the ten-god
        working style (shares ≥8% count), and 神煞 talents that serve the path. "Fit"
        means effort converts to reward efficiently there — low-ranked fields are priced
        against the chart, never forbidden. For the children read these as directions to
        expose and nurture, revisited as 大運 decades turn.</div>
      <h4>Favourable industries by element 行業五行</h4>
      ${c.industries.favourable.map((it) => `<div class="cite"><b>Favourable ${elb(it.element)} ${it.en}
        industries</b> — ${it.industries}</div>`).join("")}
      <div class="cite" style="margin-bottom:8px">Understated: ${c.industries.avoid.map((it) =>
        `${elb(it.element)} (${it.industries.split(",")[0]}…)`).join("; ")}
        — not forbidden, just not where this chart recharges.</div>
      <h4>Career archetypes ranked 事業方向</h4>
      ${c.careers.top.map((a, i) => `<div class="cite"><b>#${i + 1} ${a.en} ${a.zh}</b>
        <span class="tag ${a.score >= 12 ? "" : "warn"}">${a.score >= 12 ? "strong fit" :
          a.score >= 4 ? "good fit" : "workable"}</span>
        <div class="sub" style="margin-top:2px">${a.reasons.join(" · ")}</div></div>`).join("")}
      <div class="cite" style="margin-top:7px"><b>Priced against this chart:</b>
        ${c.careers.avoid.map((a) => `${a.en} ${a.zh} — ${a.reasons.join("; ")}`).join(" · ")}</div>
      ${stb(12)}${narr(12)}${lg(12)}
    </div>` : ""}
    ${c.windows ? `<div class="section"><h3>13. Windows 時機
        <span class="tag warn">timing cross-layer · climate × weather · not prediction</span></h3>
      <div class="cite" style="margin:0 0 8px">The decade is the climate, the year is the
        weather. Each 大運 is phase-labelled from its elements against the 用神 plus its
        interactions with the day/month pillars; each of the next ten years is checked
        per dimension — <b>career</b> (month-pillar activation or clash, 官殺 arrival),
        <b>wealth</b> (財星 arrival with a can-the-chart-hold-it check, 財庫 vault years),
        <b>relationship</b> (桃花 and spouse-palace 日支 activation) and <b>health</b>
        (years that feed an excess or replenish a weak element). Green = window, red =
        caution, grey = quiet. A caution is a navigation note, never a verdict.</div>
      <div class="ccdayun">${c.windows.decades.map((d) => `
        <div class="ccdy${d.current ? " now" : ""}" title="${d.notes.join("; ")}">
          <div class="ccdyage">${d.ages}</div><div class="ccdygz">${d.gz}</div>
          <div class="wphase w-${d.phase}">${d.phase_zh}<span class="wp-en"> ${d.phase}</span></div>
          ${d.current ? `<div class="ccdyhere">▲ now</div>` : ""}</div>`).join("")}
      </div>
      <div class="cite" style="margin:4px 0 8px"><b>桃花:</b> ${c.windows.taohua.branch}
        — ${c.windows.taohua.type}${c.windows.taohua.pillars.length
          ? ` (in the ${c.windows.taohua.pillars.join("/")} pillar)` : ""}</div>
      <table class="wtable"><tr><th>Year</th><th>Overall</th><th>事業 Career</th>
        <th>財富 Wealth</th><th>感情 Relationship</th><th>健康 Health</th></tr>
        ${c.windows.years.map((yr) => {
          const cell = (d) => `<td class="wf-${d.flag}"><b>${
            d.flag === "window" ? "◉" : d.flag === "caution" ? "⚠" : "·"}</b>
            <span>${d.note}</span></td>`;
          return `<tr><th>${yr.y} ${yr.gz}</th>
            <td class="wf-${yr.overall === "peak" ? "window" : yr.overall === "careful" ? "caution" : "quiet"}">
              <b>${yr.overall_zh}</b></td>
            ${cell(yr.career)}${cell(yr.wealth)}${cell(yr.relationship)}${cell(yr.health)}</tr>`;
        }).join("")}
      </table>${stb(13)}${narr(13)}${lg(13)}</div>` : ""}
    <div class="section"><h3>Rule citations</h3>
      ${c.citations.map((x) => `<div class="cite"><b>[${layerZh(x.layer)}] ${x.source_ref}:</b> ${x.explanation}</div>`).join("")}
    </div>`);
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
  $("#tab-house").innerHTML = jt(explain(
    "<b>What this page shows:</b> the home's energy map. The floorplan is cut into 8 compass " +
    "sectors from the house centre (dashed lines), and each room is labelled with its " +
    "<b>Flying Star</b> numbers for the chosen construction period: 山 mountain star governs " +
    "people &amp; health, 向 water star governs wealth, and 年 is this year's visiting star " +
    "(5 and 2 are the ones to watch). The 3×3 grid on the right is the same chart drawn the " +
    "traditional way — red = mountain star, blue = water star, middle = period base star.",
    "house") +
    narrBlock(h.interpretation && h.interpretation[String(state.period)]) + `
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
  $("#tab-assign").innerHTML = jt(explain(
    "<b>What this page shows:</b> who sleeps where, and how well it suits them. Each " +
    "person-in-room score adds three layers: <b>八宅</b> (is this sector one of their four " +
    "lucky or four unlucky directions), <b>Flying Stars</b> (quality of the sector's " +
    "mountain/water/annual stars), and <b>用神 match</b> (does the sector's element feed " +
    "their favourable elements). Tick the boxes to try any arrangement — scores recompute " +
    "instantly and every line shows its rule. <b>✨ Optimize</b> searches all allowed " +
    "arrangements (parents stay together unless you allow a split) and proposes the top 3.",
    "assign") + `
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
  $("#tab-forecast").innerHTML = jt(explain(
    "<b>What this page shows:</b> how the chosen year treats this person and their bedroom. " +
    "The top section checks the year's stem-branch against their chart — clashing (冲) or " +
    "combining (合) with 太岁, the 'Grand Duke' of the year. <b>Room watch</b> warns for the " +
    "months when the troublesome 5-yellow or 2-black monthly star flies into their bedroom " +
    "sector (a month to avoid renovation/drilling there). The table lists each month's " +
    "centre star and the star landing in their room — green months are supportive, red " +
    "months deserve extra care.", "forecast") + `
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
  $("#tab-dates").innerHTML = jt(explain(
    "<b>What this page shows:</b> a rating for every day of the month, for picking dates " +
    "(moving house, starting renovation, signing contracts). Each day gets its 12-officer " +
    "(建除) day quality — 成 'Success' and 開 'Open' days score high, 破 'Destruction' days " +
    "score low — plus a penalty on 月破 (month-clash) days. The flags column warns when a " +
    "day clashes (冲) with a family member's zodiac year or day pillar — that person should " +
    "avoid big moves that day — or combines (合) favourably. Green rows = the month's best " +
    "five days; red rows = avoid.", "dates") + `
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
  $("#tab-pair").innerHTML = jt(explain(
    "<b>What this page shows:</b> classical pair compatibility (合婚) between any two " +
    "family members. It weighs the two DAY pillars (each person's 'spouse palace') " +
    "heaviest, then the year branches (生肖 relation), the 五合 stem bond, and whether " +
    "each chart is rich in elements the other needs. Works for couples, parent–child " +
    "and siblings — the score reads as natural ease, not destiny.", "pair") + `
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
  $("#tab-names").innerHTML = jtNames(explain(
    "<b>What this page shows:</b> classical name analysis (姓名学). Each character is first " +
    "checked against its <b>Kangxi-dictionary traditional stroke count</b> — the count BaZi " +
    "name analysis requires (simplified forms are rejected loudly). The strokes then build " +
    "the <b>Five Grids</b> (天 heaven, 人 person, 地 earth, 外 outer, 总 total); each grid " +
    "number is looked up in the 81-number table as lucky 吉, neutral 半吉 or unlucky 凶, " +
    "with its element. <b>三才</b> (Three Talents) checks whether the heaven→person→earth " +
    "elements feed each other (generating = good) or fight (controlling = bad).", "names") +
    narrBlock(out.interpretation) +
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
  $("#tab-unit").innerHTML = jt(explain(
    "<b>What this page shows:</b> a quick screening tool for a home you might buy or rent. " +
    "Enter the unit's facing direction in degrees (from a phone compass at the main " +
    "door/balcony) and its construction/renovation period, and it builds the Flying-Star " +
    "chart and scores every compass sector for each family member. Use it to shortlist " +
    "units — it knows nothing about the actual floorplan, so it is a first filter, not a " +
    "verdict.", "unit") + `
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
    try { state.primer = await api("/api/primer"); } catch (e) { /* optional */ }
    window.__CHART_URL__ = window.__PUBLIC_READING__.chartUrl;
    try { await renderPerson(window.__PUBLIC_READING__.name); }
    catch (e) { $("#tab-person").innerHTML = `<p class="hint">load failed: ${e.message}</p>`; }
  })();
} else {
  controls();
  refresh().catch((e) => ($("#warnings").textContent = "load failed: " + e.message));
}
