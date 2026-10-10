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
const elb = (e) => `<span class="elb el-${e} keepzh" title="${EL_EN[e] || e}">${e}</span>`;
const elbs = (a) => (a || []).map(elb).join("");
const sadv = (items, title = "Strategy") => !items || !items.length ? "" :
  `<div class="sadv"><b>${title}</b>${items.map((x) => `<div>· ${dnAll(x)}</div>`).join("")}</div>`;

/* strategy report content distributed into its Reading sections */
function stratBlock(n, st) {
  const s = st && st["s" + n];
  if (!s) return "";
  switch (n) {
    case 2: return sadv([s.advice], "What this asks of you");
    case 5: return `<div class="cite" style="margin-top:8px"><b>Monthly rhythm</b>
        (recurring every year): green months feed this chart, red months drain it —
        schedule pushes into green months, recovery into red ones.</div>
      <div class="mos">${s.rhythm.map((m) => `<span class="mo ${m.cls}">${m.mon} ${m.br}${m.el}</span>`).join("")}</div>`;
    case 8: return `<div class="cite" style="margin-top:8px"><b>${s.kid
        ? "Partnership & friendship patterns" : "Relationship patterns"}:</b>
        primary risk point — ${dnAll(s.risk)}</div>
      ${s.evidence.map((e) => `<div class="cite">· ${dnAll(e)}</div>`).join("")}
      <div class="cite"><b>Peach blossom:</b> ${s.taohua} · <b>Zodiac allies:</b> ${s.allies.join(", ")}
        · <b>Zodiac friction:</b> ${s.clash}</div>
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
        <div class="sdialcap"><span>venture</span><b>${s.pct_corp}% structured</b>
          <span>corporate</span></div></div>
      <div class="cite"><b>${dnAll(s.verdict)}</b></div>
      <div class="cite">structure evidence: ${s.corp_ev.join(", ") || "—"} ·
        volatility evidence: ${s.vent_ev.join(", ") || "—"}</div>
      ${sadv(s.advice)}`;
    case 13: return `<div class="cite" style="margin-top:8px"><b>Wealth pattern:</b>
        ${dnAll(s.wealth_pattern)} ${dnAll(s.wealth_carry)}</div>
      ${s.act_windows.length ? `<div class="cite"><b>Act-year windows:</b>
          ${s.act_windows.map((x) => "◉ " + dnAll(x)).join("<br>")}</div>`
        : `<div class="cite">no wealth-activation years in the next decade — build, don't chase</div>`}
      ${s.cautions.length ? `<div class="cite">⚠ hold-back years: ${s.cautions.join(", ")}</div>` : ""}
      ${s.handoff ? `<div class="cite"><b>Next-decade handoff:</b> ${dnAll(s.handoff)}</div>` : ""}
      ${s.exams.length ? `<div class="cite"><b>Exam-year overlay:</b><br>
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
  if (!state.primer) state.primer = await api("/api/primer");
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
    ["Symbolic stars", p.shensha.join(" · ") || "—"],
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
  let s = `<svg viewBox="0 0 340 350" class="ewheel"><defs>
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
    s += swatchDisc(x, y, r, el);
    if (el === er.dm) s += `<circle cx="${x}" cy="${y}" r="${r + 3.5}" fill="none"
      stroke="var(--gold)" stroke-width="2.5"/>`;
    const fs = Math.max(11, Math.min(22, r * 0.62));
    s += `<title>${EL_EN[el]} ${er.share[el]}%${el === er.dm ? ", your day master" : ""}</title>
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
    {zh:"官殺", en:"Authority", el:invK[dmEl], gods:[["正官"],["七殺","七杀"]], lab:["正官","七殺"]},
    {zh:"印星", en:"Resource", el:invS[dmEl], gods:[["正印"],["偏印"]], lab:["正印","偏印"]},
    {zh:"比劫", en:"Peers", el:dmEl, gods:[["比肩"],["劫財","劫财"]], lab:["比肩","劫財"]},
    {zh:"食傷", en:"Output", el:S[dmEl], gods:[["食神"],["傷官","伤官"]], lab:["食神","傷官"]},
    {zh:"財星", en:"Wealth", el:K[dmEl], gods:[["正財","正财"],["偏財","偏财"]], lab:["正財","偏財"]},
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
  const KEI = [[2, 4], [3, 0], [4, 1], [0, 2], [1, 3]];      // 剋 star
  let s = `<svg viewBox="${opts.groupsOnly ? "45 45 250 265" : "0 0 340 345"}" class="ewheel tgwheel${opts.groupsOnly ? " tgwheel-groups" : ""}${opts.zh ? " keepzh" : ""}"${opts.zh ? ' data-notip role="img" aria-label="' + GROUPS.map((g) => `${g.en} (${g.zh}) ${g.sum}%`).join(", ") + '"' : ""}><defs>
    <marker id="tS" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5" markerHeight="5.5"
      orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#7aa87f"/></marker>
    <marker id="tK" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5" markerHeight="5.5"
      orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#c98a86"/></marker></defs>`;
  if (!opts.groupsOnly) GROUPS.forEach(g => g.sat.forEach(t => {   // connectors first
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
    ["Four Pillars", "the Four Pillars: birth year·month·day·hour, each written as two characters — eight in all"],
    ["Stem / branch", "the top character of a pillar is its heavenly stem, the bottom its earthly branch (with the zodiac animal)"],
    ["日主 Day Master", "the day stem — the character that IS you; every other character is read by its relationship to it"],
    ["Ten Gods", "that relationship, named — translated god-by-god in §4"],
    ["Hidden stems", "hidden stems: extra elements stored inside each branch, listed under the pillar"],
    ["Zodiac animal", "the zodiac animal of the birth-year branch"],
    ["Kua number", "your personal trigram — decides your lucky compass directions (§7)"],
    ["Natal star", "the life star (Nine Star, 九星) of the birth year — the number feng shui overlays use for you"],
    ["Life Palace", "an auxiliary destiny point derived from the birth month + hour — classical readers weigh it for temperament and life theme"],
    ["Conception Palace", "the pillar of the estimated conception month — a supplementary root the chart can draw on"],
    ["Useful god", "the elements that act as this chart's medicine (§5)"],
    ["Symbolic stars", "symbolic stars carried by the pillars — detailed with meanings in §9"],
    ["Sound element (Nayin)", "the pillar's melodic element — its poetic name in the 60-cycle (e.g. Sea Metal, 海中金)"],
    ["Life stage", "the Day Master's life-stage in that branch (birth→peak→decline cycle) — vitality flavour, not a verdict"],
    ["Luck cycles", "the 10-year luck cycles that colour each decade (§6)"],
  ],
  1: [["Wood / Fire / Earth / Metal / Water", "wood / fire / earth / metal / water"],
    ["weight", "weighted count of visible + hidden characters carrying that element"],
    ["reading it", "balance beats abundance — the tallest bar is the heaviest, not the best"],
    ["wheel: node size", "that element's share of THIS chart; gold ring = your Day Master"],
    ["green arrows (generating)", "the generating cycle (wood→fire→earth→metal→water) — thicker = stronger feeder"],
    ["red lines (controlling)", "the controlling cycle — solid red = an actual affliction in this chart (a heavy element crushing a weak one)"],
    ["The five roles", "the five roles every element plays relative to the Day Master — resource, output, wealth, pressure, peers; the ten gods refine these"]],
  2: [["Strong", "the chart can afford to spend — output, wealth and pressure suit it"],
    ["Weak", "the chart needs feeding — support, rest and resource suit it"],
    ["support ratio", "share of the chart on the Day Master's side"],
    ["root mass", "the Day Master's own element hidden inside the branches — its anchoring"]],
  3: [["Stem row", "the ten god of each pillar's visible character"],
    ["Hidden-stem row", "the gods of the hidden stems inside each branch"],
    ["Direct / Indirect / Seven Killings …", "each god's name and meaning is translated in §4's list"]],
  4: [["Direct vs indirect", "Direct = the proper/conventional form of a domain, Indirect = its unconventional twin (opposite-polarity / same-polarity pairing)"],
    ["%", "share of the chart's characters classified as that god — where life's attention defaults"],
    ["wheel: Day Master centre", "your Day Master; the five groups around it are the five roles from §1's element wheel, refined into gods"],
    ["node colour & size", "colour = that group's actual element for YOUR Day Master (§1 palette); size = its share of the chart"],
    ["green / red arrows", "generating (feeding) and controlling cycles between the god groups — same cycles as §1, one level up"],
    ["satellites", "each group's Direct/Indirect pair with its own share — faded = barely present"],
    ["rooted / floating", "a visible god whose element also sits in the branches is rooted (durable); visible-only is floating (shows up socially, needs backing)"],
    ["pair patterns", "classical combinations (Eating God controls Seven Killings, Hurting Officer meets Direct Officer, …) — the gods' joint behaviour, not just their sizes"]],
  5: [["Useful god (favourable)", "favourable — the chart's medicine; carry these elements in colours, directions, fields"],
    ["Avoid", "elements that aggravate the imbalance"],
    ["Support-and-restrain method", "support-the-weak / restrain-the-strong: the method that picked them"],
    ["Seasonal adjustment", "seasonal climate cross-check (a winter chart may need fire regardless)"]],
  6: [["Luck cycles", "one pillar per decade of life, starting from the month pillar"],
    ["ages", "your age span under that pillar"],
    ["god labels", "the decade's dominant themes, in §4's vocabulary"],
    ["highlighted", "the decade you are in now"]],
  7: [["Eight House", "eight-house school: your trigram splits the compass into 4 green (use) and 4 red (avoid) directions"],
    ["how to use", "green = bed headboard, desk facing, main door; red = fine for storage/bathroom"],
    ["personal", "this map differs per person — a couple can have opposite maps"]],
  8: [["score", "starts at a neutral 50; every chip is a rule that moved it"],
    ["≥70", "a natural strength"], ["<45", "an area to consciously support"],
    ["chips", "the audit trail — hover none, they are the working"],
    ["Seated", "the domain's signal god actually resides in its primary palace — a seated signal lands harder than share alone suggests"],
    ["Wealth vault", "the wealth-element storage branch (Chen, Xu, Chou, Wei): open = accumulation compounds; sealed = opens in its clash years (§13); absent = wealth flows, systems must do the storing"]],
  9: [["Symbolic stars", "symbolic stars: classical stem-branch patterns, flavour on top of structure"],
    ["Year / month / day / hour tag", "which pillar carries it — ancestry · career/parents · self/spouse · children/later life"]],
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
    ["Peach blossom", "peach-blossom: the romance/charm activation branch"]],
};


/* ===== Reading rework 2026-09-19 (mockup data/out/readingMockup.html, decisions: A-tabs,
   inline SVG, card stats = medicine/dominant/missing/best/watch/decade) ===== */
const ALLGODS = ["比肩", "劫財", "食神", "傷官", "正財", "偏財", "正官", "七殺", "正印", "偏印"];
/* the chart carries its own legend; fall back to the table below when it does not */
const godEn = (c, g) => ((c.tengods_legend || {})[g] || {}).en || TG_EN_FALLBACK[g] || g;
const WHEEL_KEY = [["比劫", "peers", "比肩", "劫財"], ["食傷", "output", "食神", "傷官"], ["財星", "wealth", "正財", "偏財"],
  ["官殺", "authority", "正官", "七殺"], ["印星", "resource", "正印", "偏印"]];
const TG_GIST = Object.fromEntries(Object.entries({   // one line per role, from the engine's TEN_GOD_MEANING
  比肩: "peers and self-reliance", 劫財: "rivals and boldness", 食神: "gentle output, enjoyment and ease", 傷官: "sharp output and a will to challenge",
  偏財: "windfall wealth and opportunity", 正財: "steady wealth, salary and savings", 七殺: "raw pressure and ambition", 正官: "proper authority, rules and status",
  偏印: "unconventional learning and solitary study", 正印: "nurturing support, study and protection" }).flatMap(([k, v]) =>
  [[k, v], [k.replace("財", "财").replace("殺", "杀").replace("傷", "伤"), v]]));
const TG_EN_FALLBACK = { 比肩: "Friend", 劫財: "Rob Wealth", 食神: "Eating God",
  傷官: "Hurting Officer", 正財: "Direct Wealth", 偏財: "Indirect Wealth",
  正官: "Direct Officer", 七殺: "Seven Killings", 正印: "Direct Resource", 偏印: "Indirect Resource" };
const deepWrap = (label, inner) => inner
  ? `<details class="deep"><summary>${label}</summary><div class="deepbody">${inner}</div></details>` : "";

const ZODIAC = { 鼠: ["🐭", "Rat"], 牛: ["🐮", "Ox"], 虎: ["🐯", "Tiger"], 兔: ["🐰", "Rabbit"],
  龙: ["🐲", "Dragon"], 蛇: ["🐍", "Snake"], 马: ["🐴", "Horse"], 羊: ["🐑", "Goat"],
  猴: ["🐵", "Monkey"], 鸡: ["🐔", "Rooster"], 狗: ["🐶", "Dog"], 猪: ["🐷", "Pig"],
  龍: ["🐲", "Dragon"], 馬: ["🐴", "Horse"], 雞: ["🐔", "Rooster"], 豬: ["🐷", "Pig"] };
const EL_EN = { 木: "Wood", 火: "Fire", 土: "Earth", 金: "Metal", 水: "Water" };

function strengthGauge(st) {
  const x = Math.max(-1, Math.min(1, st.score));       // score −1..+1
  const px = 150 + x * 130;
  return `<svg viewBox="0 0 300 64" class="sgauge" role="img"
      aria-label="strength ${st.verdict} score ${st.score}">
    <rect x="20" y="26" width="260" height="10" rx="5" fill="rgba(0,0,0,.07)"/>
    <rect x="20" y="26" width="104" height="10" rx="5" fill="#e8c8be"/>
    <rect x="176" y="26" width="104" height="10" rx="5" fill="#c9dcc0"/>
    <line x1="150" y1="20" x2="150" y2="42" stroke="#b9b4a6" stroke-width="1.5"/>
    <circle cx="${px}" cy="31" r="8" fill="#a63d2f"/>
    <text x="24" y="16" font-size="10" fill="#8b8f9a">身弱 weak</text>
    <text x="276" y="16" font-size="10" fill="#8b8f9a" text-anchor="end">身強 strong</text>
    <text x="150" y="58" font-size="11" font-weight="700" fill="#22242a"
      text-anchor="middle">${st.verdict} · score ${st.score}</text>
  </svg>`;
}

function bazhaiCompass(c) {
  const cell = (pal, dir) => { const s = c.youxing[pal];
    const good = ["生氣", "天醫", "延年", "伏位"].includes(s);
    return `<div class="${good ? "g" : "b"}"><b>${dir} ${pal}</b>${s}</div>`; };
  return `<div class="cmpx">
    ${cell("乾", "NW")}${cell("坎", "N")}${cell("艮", "NE")}
    ${cell("兌", "W")}<div class="c"><b class="dmark" style="color:${EL_TXT[STEM_EL[c.day_master]]}">${c.day_master}</b>${dn(c.name)}</div>${cell("震", "E")}
    ${cell("坤", "SW")}${cell("離", "S")}${cell("巽", "SE")}</div>`;
}

/* ---- Reading layout A (owner pick 2026-10-10) -------------------------------------------
   A one-screen answer, then five chapters titled as questions on one scroll (no hidden tabs).
   Each lead conclusion is a card: plain headline, what it means, what to do, signal strength,
   and the proof behind "Why the chart says this". The plain view sits beside the classical
   chart. All plain copy comes from c.plain (engine/plain.py, owner-approved templates). */
const CHAPTERS = [
  ["makeup", "Make-up", "What are you made of?", "Four pillars", "what-is-bazi", "the four pillars"],
  ["balance", "Balance", "What do you have too much or too little of?", "Elements", "five-elements-cycles", "the five elements"],
  ["drives", "Drives", "What drives you?", "Ten gods", "ten-gods-guide", "the ten gods"],
  ["timing", "Timing", "What is coming, and when?", "Luck cycles", "luck-cycles-and-windows", "luck cycles"],
  ["space", "Space", "Where should you sit, sleep and work?", "Compass", "eight-house-directions", "eight-house directions"]];
const EL_SLUG = { 木: "wood", 火: "fire", 土: "earth", 金: "metal", 水: "water" };
const STEM_SLUG = { 甲: "jia", 乙: "yi", 丙: "bing", 丁: "ding", 戊: "wu", 己: "ji", 庚: "geng", 辛: "xin", 壬: "ren", 癸: "gui" };
const SWATCH = { 火: ["#c5221f", "#7b2d8e", "#e07b1f"], 水: ["#1b1f2a", "#1a56b0"], 木: ["#187a35", "#6aa84f"],
  土: ["#c9a227", "#d8c8a4", "#7a601b"], 金: ["#ffffff", "#c9a227", "#b8bec6"] };
const pWhy = (txt, html, label = "Why the chart says this") => txt || html
  ? `<details class="rp-why"><summary>${label}</summary><div class="rp-whyb">${txt ? `<p>${txt}</p>` : ""}${html || ""}</div></details>` : "";
const PILLAR_KEYS = [["year", "year"], ["month", "month"], ["day", "you"], ["hour", "hour"]];
function pSeal(c) {
  const P = c.pillars;
  return `<div class="rp-seal keepzh" data-notip role="img" aria-label="Your four pillars, year to hour: ${PILLAR_KEYS.map(([k]) => P[k]).join(" ")}">${PILLAR_KEYS.map(([k, lab]) =>
    `<div${k === "day" ? ' class="me"' : ""}><span style="color:${EL_TXT[STEM_EL[P[k][0]]]}">${P[k][0]}</span><span style="color:${EL_TXT[BR_EL[P[k][1]]]}">${P[k][1]}</span><small>${lab}</small></div>`).join("")}</div>`;
}
/* the side of life the reader is in now: the four sides' age ranges against the reader's age */
function sideNow(c) {
  const age = (c.story || {}).age; if (age == null) return null;
  return (c.plain.sides || []).find((s) => { const [a, b] = String(s.ages).replace("+", "–999").split("–").map(Number);
    return age >= a && age <= (b || 999); }) || null;
}
function pIdentity(c, name) {
  const I = c.plain.identity, now = sideNow(c);
  const where = now ? `This is your day pillar: you, at every age. Each stage of life has its own side, shown below; you are now in ${{ year: "your roots", month: "your working years", day: "your home years", hour: "your later years" }[now.key]}.`
    : "This is your day pillar: you, at every age. Each stage of life has its own side, shown below.";
  const season = { 寅: "spring", 卯: "spring", 辰: "spring", 巳: "summer", 午: "summer", 未: "summer",
    申: "autumn", 酉: "autumn", 戌: "autumn", 亥: "winter", 子: "winter", 丑: "winter" }[c.pillars.month[1]];
  const art = `/static/img/reading/bg/${STEM_SLUG[c.day_master]}-${season}`;   // the identity line, drawn: stem × season
  return `<section class="rp-ident rp-bgart" data-art="${STEM_SLUG[c.day_master]}-${season}" style="--bg6:url('${art}-600.jpg');--bg12:url('${art}-1200.jpg');--bgp6:url('${art}-p-600.jpg');--bgp9:url('${art}-p-900.jpg')"><div class="rp-idtext"><p class="rp-name">${dn(name || c.name)}</p>${pSeal(c)}
      <h2 class="rp-h">${I.head}</h2><p class="rp-sub">${I.sub}</p><p class="rp-sub rp-where">${where}</p>${pWhy(I.why)}</div>
  </section>`;   // the Day Master image now lives on the "you at home" card in the four sides
}
/* the four pillars as four life characters (owner pick 2026-10-10); replaces the Four Palaces chart */
function pSides(c) {
  const S = c.plain.sides || []; if (!S.length) return "";
  const kids = ((c.palaces || {}).children || {}).line, now = sideNow(c);
  return `<section class="rp-sides" aria-labelledby="h-sides"><h3 id="h-sides">Your four sides</h3><div class="rp-sidegrid">${S.map((s) =>
    `<article class="rp-side${s.key === "day" ? " me" : ""}${now === s ? " here" : ""}"${now === s ? ' aria-current="true"' : ""}>${now === s ? '<span class="rp-here">You are here</span>' : ""}<img src="/static/img/reading/dm-${STEM_SLUG[s.stem]}-600.jpg" alt="" width="600" height="400" loading="lazy" decoding="async">
      <p class="rp-k">${s.area.charAt(0).toUpperCase() + s.area.slice(1)}${s.ages ? `, <span class="rp-nw">ages ${s.ages}</span>` : ""}</p><h4>${s.head}</h4><p>${s.role}</p></article>`).join("")}</div>
    ${pWhy("", S.map((s) => `<p>${s.why}</p>`).join("") + (kids ? `<p><b>Children palace:</b> ${kids}</p>` : ""))}</section>`;
}
const DRIVE_IMG = { 比劫: "peers", 食傷: "expression", 財: "money", 官殺: "duty", 印: "support" };
function pCareers(c) {
  const C = c.careers || {}, row = (a) => `<li><b>${a.en}</b> (${a.score} pts): ${a.reasons.join("; ")}</li>`;
  return (C.top || []).length ? `<p><b>Career archetypes, ranked.</b></p><ul class="rp-list">${C.top.map(row).join("")}${(C.avoid || []).map((a) =>
    `<li>Harder going: <b>${a.en}</b> (${a.score} pts): ${a.reasons.join("; ")}</li>`).join("")}</ul>` : "";
}
function pBudget(c, compact) {
  return `<div class="rp-bud">${c.plain.balance.map((r) => `${elb(r.el)}<span>${r.en}</span>
    <span class="rp-tr"><i style="width:${Math.min(100, Math.max(2, r.share / 60 * 100)).toFixed(0)}%;background:${EL_COL[r.el]}"></i></span>
    <span class="rp-bd${r.band === "about right" ? "" : " rp-strong"}">${r.band}</span>${r.medicine || (!compact && r.note)
      ? `<span class="rp-note">${r.medicine ? '<span class="rp-tag">helps you most</span> ' : ""}${compact ? "" : r.note}</span>` : ""}`).join("")}</div>`;
}
function pAnswers(c) {
  const P = c.plain, H = P.helps, Y = P.year;
  const heavy = Object.entries(c.element_weights).sort((a, b) => b[1] - a[1])[0][0];
  return `<div class="rp-answers">
    <div class="rp-ans rp-bal"><p class="rp-k">Your balance</p><h3>${heavy} is heaviest; ${EL_EN[H.el]} is what you need.</h3>${pBudget(c, true)}</div>
    <div class="rp-ans"><p class="rp-k">What helps you</p><h3>${H.head}</h3><div class="rp-sw" aria-hidden="true" style="--blot:url('/static/img/reading/sw/${EL_SLUG[H.el]}-128.webp')">${(SWATCH[H.el] || []).map((x) =>
      `<i style="background-color:${x}"></i>`).join("")}</div><p>${H.means}</p></div>
    ${Y ? `<div class="rp-ans"><p class="rp-k">This year</p><p class="rp-year"><span class="rp-ybig">${Y.y}</span> <span class="rp-gz keepzh" data-notip>${Y.gz}</span></p>
      <h3>${Y.word}</h3><p>${Y.means}</p></div>` : ""}
    <div class="rp-ans rp-wide"><p class="rp-k">Two things to do</p><ul class="rp-acts">${P.actions.map((a) => `<li>${a}</li>`).join("")}</ul></div></div>`;
}
/* luck decades as rows: a painted phase mark, the ages, the phase, one plain line; the next turn named (owner 2026-10-10) */
const PHASE_LINE = { growth: "Conditions favour building.", consolidation: "Build reserves rather than leap.",
  transition: "Expect change at home or work.", corrective: "Protect health, money and close ties." };
function pWeather(c) {
  const D = c.plain.decades || [], i = D.findIndex((d) => d.current), nx = i >= 0 ? D[i + 1] : D[0];
  return `<ol class="rp-dec" aria-label="Your luck decades">${D.map((d, k) => `<li class="${d.current ? "now" : i >= 0 && k < i ? "past" : ""}"${d.current ? ' aria-current="true"' : ""}>
      <img src="/static/img/reading/mk/${d.phase}-96.png" alt="" width="40" height="40" decoding="async">
      <span class="rp-dage">${d.ages}</span><b>${d.word}</b><span class="rp-dline">${PHASE_LINE[d.phase] || ""}</span>${d.current ? '<em class="rp-dnow">now</em>' : ""}</li>`).join("")}</ol>
    ${nx ? `<p class="rp-dnext"><b>Next turn:</b> ${nx.word.toLowerCase()}, from age ${String(nx.ages).split(/[–-]/)[0]}.</p>` : ""}`;
}
const pYears = (c) => `<div class="rp-yrs">${c.plain.years.map((y) => `<div class="${y.overall}"><b>${y.y}</b>${y.word.split(" ")[0]}</div>`).join("")}</div>`;
const pDrives = (c) => `<div class="rp-drv">${c.plain.drives.groups.map((g) => `<b>${g.name}</b><span class="rp-tr"><i style="width:${Math.max(1, g.pct).toFixed(0)}%"></i></span>
  <span>${Math.round(g.pct)}%</span><small>${g.gloss} (${g.zh})</small>`).join("")}</div>`;
function pRoom(c) {
  const S = c.plain.space; if (!S) return "";
  const pos = { NW: [0, 0], N: [1, 0], NE: [2, 0], W: [0, 1], E: [2, 1], SW: [0, 2], S: [1, 2], SE: [2, 2] }, q = 93.3;
  let s = `<svg class="rp-room" viewBox="0 0 300 312" role="img" aria-label="Room plan with north at the top: ${Object.entries(S.marks).map(([d, l]) => `${l.join(" and ")} in the ${d}`).join("; ")}">
    <text x="150" y="11" text-anchor="middle" font-size="11" fill="#6b6359">north</text>
    <rect x="10" y="22" width="280" height="280" fill="#fff" stroke="#2b2620" stroke-width="2"/>`;
  [1, 2].forEach((k) => { s += `<line x1="${10 + k * q}" y1="22" x2="${10 + k * q}" y2="302" stroke="#e5ded2"/><line x1="10" y1="${22 + k * q}" x2="290" y2="${22 + k * q}" stroke="#e5ded2"/>`; });
  Object.entries(pos).forEach(([dr, [cx, cy]]) => { const x = 10 + cx * q + q / 2, y = 22 + cy * q + q / 2;
    s += `<text x="${x}" y="${y - 22}" text-anchor="middle" font-size="12" fill="#6b6359">${dr}</text>`;
    (S.marks[dr] || []).forEach((lab, j) => { s += `<rect x="${x - 38}" y="${y - 10 + j * 24}" width="76" height="20" rx="10" fill="#c7301d"/>
      <text x="${x}" y="${y + 4 + j * 24}" text-anchor="middle" font-size="12" fill="#fff" font-weight="600">${lab}</text>`; }); });
  return s + "</svg>";
}
const pRelations = (c) => { const ps = c.plain.makeup.pairs;
  return ps.length ? `<ul class="rp-list">${ps.map((x) => `<li><b>${x.a.charAt(0).toUpperCase() + x.a.slice(1)}</b> and <b>${x.b}</b>: ${x.note} (${x.kind})</li>`).join("")}</ul>`
    : "<p>No strong pulls between your pillars.</p>"; };
function pSlimGrid(c) {
  const P = c.pillars, tg = c.ten_gods || {}, hid = c.hidden_gods || {};
  return `<div class="rp-sg keepzh" data-notip>${PILLAR_KEYS.map(([k, lab]) => { const g = k === "day" ? "日主" : tg[k] || "";
    return `<div${k === "day" ? ' class="me"' : ""}><small>${k === "day" ? "day (you)" : lab}</small><span class="rp-tg" title="${k === "day" ? "Day Master" : godEn(c, g)}">${g}</span>
      <span class="rp-big" style="color:${EL_TXT[STEM_EL[P[k][0]]]}">${P[k][0]}</span><span class="rp-big" style="color:${EL_TXT[BR_EL[P[k][1]]]}">${P[k][1]}</span>
      <span class="rp-hid">${(hid[k] || []).map((x) => `<span title="${godEn(c, x.slice(2, -1))}">${x[0]}</span>`).join(" ")}</span></div>`; }).join("")}</div>
    <p class="rp-cap">Top: the role each stem plays for you. Bottom: the stems hidden in each branch.</p>`;
}
function pChapter([id, , q, tech, img, what], body, src) {
  return `<section class="rp-chap" id="ch-${id}" aria-labelledby="h-${id}"><div class="rp-chead"><div><h2 id="h-${id}">${q}</h2>
      <p class="rp-tech">The classical name for this: ${tech}.</p></div>
      <img src="${src || `/static/learn/img/hero/${img}-600.jpg`}" alt="" width="600" height="400" loading="lazy" decoding="async"></div>
    ${body}
    <p class="rp-learn"><a href="/learn/${img}">Learn more about ${what}</a></p></section>`;
}
/* Story layout (round 3, 2026-10-10). Each chapter reads as paragraphs from c.story (engine/story.py).
   Every sentence carries evidence ids; each id becomes a numbered marker that opens its proof in place,
   right under the paragraph that first cites it. A proof's figures render once, in the chapter that owns it. */
const CHART_CAP = { makeup: "Your eight characters.", balance: "Your five elements, and how they feed and check each other.",
  drives: "The ten classical roles, grouped.", timing: "Your luck pillars, decade by decade.", space: "The eight directions for your Kua number." };
const EV_OWNER = { pillars: "makeup", stars: "makeup", interactions: "makeup", personality: "makeup", elements: "balance", strength: "balance",
  flows: "balance", medicine: "balance", health: "balance", gods: "drives", domains: "drives", work: "drives", money: "drives",
  decades: "timing", years: "timing", months: "timing", days: "timing", placements: "space", afflict: "space" };
function pStory(id, S, ev, proofs, chart) {
  const num = {}; let n = 0;
  const mk = (e) => `<button type="button" class="mk" aria-expanded="false" aria-controls="ev-${id}-${num[e]}"><span class="vh">Evidence </span>${num[e]}</button>`;
  const panel = (e) => `<div class="ev" id="ev-${id}-${num[e]}" hidden><p class="evh">${num[e]}. ${ev[e].label}</p>${ev[e].why ? ev[e].why.split("\n").map((x) => `<p>${x}</p>`).join("") : ""}${(proofs[e] || []).join("")}</div>`;
  // a run of sentences resting on the same evidence shows its markers once, at the end of the run
  const para = (ss, cls) => { const fresh = [];
    const html = ss.map((s, k) => s.t.replace(/^If you do one thing:/, "<b>$&</b>") + (ss[k + 1] && ss[k + 1].ev.join() === s.ev.join() ? "" : s.ev.map((e) => {
      if (!num[e]) { num[e] = ++n; fresh.push(e); } return mk(e); }).join(""))).join(" ");
    return `<p${cls ? ` class="${cls}"` : ""}>${html}</p>${fresh.map(panel).join("")}`; };
  let out = "";
  S.paras.forEach((p, k) => { out += para(p);
    if (k === S.chart_after && chart) out += `<figure class="rp-chart"><figcaption><b>The classical chart.</b> ${CHART_CAP[id]}</figcaption>${chart}</figure>`; });
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
    domains: [G.figs.domains, R.stb(8), R.narr(8)], work: [G.figs.industries, G.figs.roles, pCareers(c), R.stb(12), R.narr(12)],
    money: [], decades: [pWeather(c), R.narr(6)], years: [pYears(c), T.figs.thisyear, R.stb(13), R.narr(13)],
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
    + (rest.length ? `<details class="rp-more rp-sources"><summary>Sources and the full interpretation</summary><div class="rd-tail">${rest.join("")}</div></details>` : "");
}
const pChapBar = () => `<nav class="rp-bar" aria-label="Chapters"><div>${CHAPTERS.map(([id, lab]) =>
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
const TG_GRP_EN = { 比劫: "peers", 印: "resource", 食傷: "output", 食伤: "output",
  財: "wealth", 财: "wealth", 官殺: "authority", 官杀: "authority" };
function colorizeTerms(root, dm) {
  if (!root) return;
  const re = new RegExp(`(${GOD_LIST.join("|")})|(?<![\u4e00-\u9fff])(木|火(?!车|車)|土(?!豆)|金(?!额|額)|水(?!平|准|準))|\\b(Wood|Fire|Earth|Metal|Water)\\b`, "g");
  const EN2EL = { Wood: "木", Fire: "火", Earth: "土", Metal: "金", Water: "水" };
  const nodes = [];
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode: (n) => n.parentElement
      && !n.parentElement.closest("script,style,svg,input,textarea,.nocolor,h1,h2,h3,a,button,summary")
      ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT });
  let t; while ((t = w.nextNode())) { re.lastIndex = 0; if (re.test(t.nodeValue)) nodes.push(t); }
  for (const node of nodes) {
    const s = node.nodeValue, frag = document.createDocumentFragment();
    let last = 0, m; re.lastIndex = 0;
    while ((m = re.exec(s))) {
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
      && !n.parentElement.closest("script,style,svg,input,textarea,.nocolor,.tcol,.elb")
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
const GRP_THEME = { 比劫: "peers and self-drive", 印: "learning and support", 食傷: "expression and output",
  財: "wealth and practical results", 官殺: "structure and pressure" };
const GRP_EN = { 官殺: "authority", 印星: "resource", 比劫: "peers", 食傷: "output", 財星: "wealth" };
const COLOUR_ZH_EN = { 红: "red", 紅: "red", 紫: "purple", 黄: "yellow", 黃: "yellow", 棕: "brown",
  绿: "green", 綠: "green", 青: "green", 蓝: "blue", 藍: "blue", 黑: "black", 灰: "grey", 白: "white", 金: "gold" };
const legendList = (n) => (LEGENDS[n] || []).map(([k, v]) => `<div><b>${k}</b> — ${v}</div>`).join("");
const clip = (s, n) => { s = String(s || ""); return s.length > n ? s.slice(0, n - 1) + "…" : s; };

/* --- the figure ------------------------------------------------------------ */
function rdFig(o) {
  const legend = o.legend ? `<details class="rd-legend"><summary aria-label="how to read this">?</summary>
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
  const hid = (p) => c.hidden_gods[p].map((x) => `<span class="cghid">${col(x[0], STEM_EL[x[0]])}<small>${zhs(x.slice(2, -1))}</small></span>`).join("");
  const tp = (c.citations || []).find((x) => x.rule_id === "time-policy") || {};
  const clock = (tp.explanation || "").match(/clock (\S+)/);
  return `<div class="cgwrap keepzh"><table class="cgrid">
    <thead><tr><th></th>${order.map((p) => `<th scope="col"${p === "day" ? ' class="dm"' : ""}>${zhs(head[p])}</th>`).join("")}</tr></thead>
    <tbody>${row("十神", (p) => zhs(c.ten_gods[p]), "cggod")}
      ${row("天干", (p) => col(c.pillars[p][0], STEM_EL[c.pillars[p][0]]), "cgbig")}
      ${row("地支", (p) => col(c.pillars[p][1], BR_EL[c.pillars[p][1]]), "cgbig")}
      ${row("藏干", hid, "cghids")}
      ${row("长生", (p) => zhs(c.pillar_extras[p].stage))}
      ${row("纳音", (p) => zhs(c.pillar_extras[p].nayin))}</tbody></table>
    <p class="cgfacts">${zhs("命卦")} ${col(c.gua, GUA_EL[c.gua])} · ${zhs("生肖")} ${zhs(lp.animal)} · ${zhs("命宫")} ${zhs(lp.ming_gong)} · ${zhs("胎元")} ${zhs(lp.tai_yuan)} · ${zhs("年命星")} ${zhs(lp.life_star_zh)} · ${zhs("真太阳时")} ${(c.effective_time || "").slice(11)}${clock ? ` (clock ${clock[1]})` : ""}</p></div>
    <p class="cgcap">Read each column top to bottom: the role the stem plays for you, the stem, the branch, the stems hidden in the branch, its life stage and its sound element. Year is on the right, as in a classical chart; your own column, 日, is outlined. Tap any character for its meaning.</p>`;
}
const GLOSS_IX = { 六害: "harms", 害: "harms", 冲: "clashes with", 六冲: "clashes with", 刑: "punishes",
  破: "breaks", 六合: "combines with", 三合: "combines with", 半合: "half-combines with" };
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
  const legend = many ? `<div class="ixlegend">${its.map((it) => `<span><b style="color:${it.kind.includes("合") ? "#0e7a6a" : "#99460a"}">${it.kind}</b> ${it.pair} · ${it.pillars.join("+")} pillars</span>`).join("")}</div>` : "";
  return `<svg class="ixsvg" viewBox="0 ${minY.toFixed(0)} 640 ${(maxY - minY).toFixed(0)}" role="img" aria-label="branch interactions">${s}</svg>${legend}`;
}
function interactionsLine(c) {
  const its = c.interactions || [], n = its.length;
  if (!n) return "No 合冲刑害 among your four branches — the pillars sit quietly with each other.";
  const seen = new Map();
  its.forEach((it) => { const k = it.kind + "|" + it.pair.split("").sort().join(""); seen.set(k, (seen.get(k) || 0) + 1); });
  const tail = [...seen.entries()].map(([k, cnt]) => { const [kind, pair] = k.split("|");
    const t = kind === "自刑" ? `${elc(pair[0])} doubles on itself` : `${elc(pair[0])} ${GLOSS_IX[kind] || kind} ${elc(pair[1])}`;
    return t + (cnt === 2 ? " twice" : cnt > 2 ? ` ×${cnt}` : ""); });
  const clash = its.some((it) => it.kind.includes("冲"));
  const words = ["", "One", "Two", "Three", "Four", "Five", "Six"];
  const list = tail.length > 1 ? tail.slice(0, -1).join(", ") + " and " + tail[tail.length - 1] : tail[0];
  return `${words[n] || n} branch ${n === 1 ? "tension" : "tensions"}, ${clash ? "one of them a clash" : "none a clash"}: ${list} — ${clash ? "watch the clash" : "quiet friction, not rupture"}.`;
}
function eflowsList(c) {
  const er = c.element_relations; if (!er) return "";
  return `<div class="eflows"><div class="cite" style="margin:0 0 6px">How every other element relates to
      YOUR Day Master ${elb(er.dm)} — the same five roles the ten gods (十神 tab) are built from:</div>
    ${["resource", "output", "wealth", "pressure", "peer"].map((k) => { const f = er.flows[k];
      const peerNote = (k === "peer" && !((c.tengods_pct["比肩"] || 0) + (c.tengods_pct["劫財"] || 0)))
        ? ` <span class="sub">(this share is the Day Master's own element — as ten-god 比肩/劫財 peers the chart counts 0%)</span>` : "";
      return `<div class="eflow"><span class="efr">${f.role}</span> ${elb(f.el)} <b>${f.share}%</b>
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
    <div class="sbhead">Supporting (same kind) vs draining (other kinds) — the score's own numbers</div>
    <div class="sbaxhead"><span>← drain</span><span>support →</span></div>
    ${pt.groups.map(row).join("")}
    <div class="sbrow sbnet"><span class="sbl">net balance</span>
      <div class="sbax"><span class="zero"></span>
        <i style="${net >= 0 ? "left:50%" : "right:50%"};width:${netPct}%;background:${net >= 0 ? "#1e7d32" : "#b03a2e"}"></i></div>
      <b class="sbv ${net >= 0 ? "sup" : "drn"}">${net >= 0 ? "+" : "−"}${Math.abs(net).toFixed(2)}</b></div>
    <div class="cite" style="margin-top:5px">score = in season ${pt.season_pts > 0 ? "+" : ""}${pt.season_pts}
      (season) + 2 × (support ${pt.support} − drain ${pt.drain}) / total ${pt.total}
      + rooting ${pt.root_pts > 0 ? "+" : ""}${pt.root_pts} (roots) = <b>${c.strength.score}</b> → ${c.strength.verdict}</div></div>`;
}
function tiaohouStrip(c) {
  const t = c.tiaohou; if (!t || !t.gods) return "";
  const chips = t.gods.map((g) => `<span class="thchip">${elc(g.stem)} ${g.god}
    <small>${g.aligned ? "✓ aligned with the medicine" : g.visible ? "visible" : "not visible"}</small></span>`).join(" ");
  return `<div class="tiaohou"><b>Seasonal adjustment</b> the ${elc(c.pillars.month[1])} month asks for ${chips}
    — <b>${t.verdict}</b> with the support-and-restrain verdict above</div>`;
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
  if (!m) return `<b>Chart structure (格局)</b> ${g.replace(/^格局[:：]\s*/, "").split(/[.。] /)[0]}`;
  const [, br, st, god, rest] = m, tou = /^(\S+?格)\s*\(月支藏干\s*(\S)\s*透干\)/.exec(rest);
  const lead = `<b>Chart structure (格局).</b> Your month branch (月令) is ${br}, and its main stem (本气) is ${st}, ${god}. `;
  return lead + (tou ? `${tou[2]} also shows among your visible stems (透干), so the chart works as a ${god} structure (${tou[1]}).`
    : `None of the month's hidden stems shows among your visible stems (透干), so the chart works from that ruling stem (司令), with the visible stems as the actors.`);
}
function buildPillars(c, R) {
  const dm = c.day_master, dmEl = STEM_EL[dm], fav = c.yongshen.favourable, weak = isWeak(c);
  const sp = (c.strength.parts || {}).season_pts || 0;
  const season = sp < 0 ? "fighting the season" : sp > 0 ? "carried by the season" : "level with the season";
  const p1 = rdFig({ tier: "hero", span: 12, label: "Four-Pillar Grid", learn: "chart",
    chart: pillarGrid(c),
    line: `A ${weak ? "weak" : "strong"} ${elc(dm)} ${elw(dmEl)} day master, ${season} — ${fav.map(elw).join(" and ")} ${fav.length > 1 ? "are" : "is"} your medicine.`,
    facts: [[c.strength.verdict.split(" ")[0], `score ${c.strength.score}`]],   // 格局 is explained in plain words under the structure check
    legend: legendList("chart") });
  const its = c.interactions || [], kinds = {};
  its.forEach((it) => (kinds[it.kind] = (kinds[it.kind] || 0) + 1));
  const p6 = rdFig({ tier: "secondary", span: 5, label: "Branch interactions", learn: "chart",
    chart: interactionsSvg(c), line: interactionsLine(c),
    facts: [...Object.entries(kinds).map(([k, n]) => [k, `×${n}`]), ...(its.some((i) => i.kind.includes("冲")) ? [] : [["冲", "none"]])],
    legend: `Arcs join the pillars whose branches interact. Dashed amber = 害·刑·冲 (friction, punishment, clash);
      solid green = 合 (combination). Read with the palaces: a tension between Year and Month touches ancestry
      and career; Day is the self and spouse.${its.length ? "<hr>" + its.map((i) => `<div><b>${i.pair} ${i.kind}</b> (${i.pillars.join("+")}) — ${i.note}</div>`).join("") : ""}` });
  // Four Palaces retired 2026-10-10: the four sides in the opening carry each palace (owner cut)
  // Which Way to Face retired 2026-10-10: it repeated the Compass 3×3 grid (owner cut)
  let p5 = "";
  if ((c.shensha || []).length) {
    const NEG = ["劫煞", "空亡", "災煞", "亡神", "羊刃", "孤辰", "寡宿"];
    const rows = c.shensha.map((s) => { const neg = NEG.includes(s.star);
      return `<div class="cite"><b class="${neg ? "shen-neg" : "shen-pos"}">${neg ? "⚠" : "✦"} ${s.star}</b>
        <span class="tag">${s.pillars.join("·")}</span> ${s.meaning}</div>`; }).join("");
    const pos = c.shensha.find((s) => !NEG.includes(s.star)), neg = c.shensha.find((s) => NEG.includes(s.star));
    const short = (s) => clip((s.meaning.split(" — ")[1] || s.meaning).split(";")[0], 48);
    const line = (pos ? `${pos.star} brings ${short(pos)}` : "No auspicious star is carried")
      + (neg ? `; watch ${neg.star} in your ${neg.pillars[0]} pillar — ${short(neg)}.` : " — and no cautionary star either.");
    p5 = rdFig({ tier: "reference", span: 7, label: "Symbolic Stars", learn: 9, chart: rows, line,
      facts: [["stars", `${c.shensha.length} total`], ["flagged", `${c.shensha.filter((s) => NEG.includes(s.star)).length} ⚠`]],
      legend: legendList(9) });
  }
  return { figs: { grid: p1, interactions: p6, stars: p5 },
    tail: [R.nb.rest.length ? deepWrap("Interpretation — the numbers read out", R.nb.rest.map((t) => `<div class="ninline">${dnAll(t)}</div>`).join("")) : "",
      R.narr(9), deepWrap("Every rule this reading cites",
        c.citations.map((x) => `<div class="cite"><b>[${layerZh(x.layer)}] ${x.source_ref}:</b> ${x.explanation}</div>`).join(""))] };
}

/* --- 五行 Elements ------------------------------------------------------------ */
function buildElements(c, R) {
  const dm = c.day_master, dmEl = STEM_EL[dm], fav = c.yongshen.favourable, unf = c.yongshen.unfavourable;
  const wtot = Object.values(c.element_weights).reduce((x, y) => x + y, 0) || 1;
  // Element bars retired 2026-10-10 (owner cut: the energy budget and the pentagon carry the same numbers);
  // its counting note now sits under the budget as "How these numbers are counted".
  const units = `<div class="cite">单位 = 字重，不是个数：天干各 1.0、地支本气 1.0、余气 1/3，全盘合计 ${wtot.toFixed(1)}。
      Units are weighted character counts: each stem 1.0, each branch's main hidden stem 1.0, each minor hidden stem 1/3.</div>`;
  const er = c.element_relations; let e2 = "";
  if (er) {
    const pr = er.flows.pressure, rs = er.flows.resource;
    e2 = rdFig({ tier: "hero", span: 5, extra: "rd-pair2", label: "Element pentagon", learn: 1,
      chart: `<div class="ewrap"><div class="svg-plate">${elementWheel(er)}</div></div>`,
      line: `${elb(pr.el)} ${elw(pr.el)} fights you hardest (${pr.share}%); ${elb(rs.el)} ${elw(rs.el)} feeds you ${pr.share > rs.share ? "only " : ""}${rs.share}% — ${pr.share > rs.share ? "pressure outweighs support" : "support outweighs pressure"}.`,
      facts: [["Authority", `${elc(pr.el)} ${pr.share}%`], ["Resource", `${elc(rs.el)} ${rs.share}%`]],
      legend: `<b>五行关系 — the five relations, listed</b>${eflowsList(c)}` });
  }
  const st = c.strength, pt = st.parts || {}, sp = pt.season_pts || 0, weak = isWeak(c);
  const stage = (c.pillar_extras.month || {}).stage;
  const topSup = (pt.groups || []).filter((g) => g.side === "support").sort((a, b) => b.w - a.w)[0];
  const e45 = rdFig({ tier: "secondary", span: 5, label: "Strength gauge and its arithmetic", learn: 2,
    chart: `<div class="svg-plate">${strengthGauge(st)}</div>
      <p class="rd-tags"><span class="tag">support ratio ${st.support_ratio}%</span> <span class="tag">root mass ${st.root_ratio}%</span> <span class="tag">${st.formation.status}</span></p>
      ${supportDrain(c)}${tiaohouStrip(c)}`,
    line: `${weak ? "Weak" : "Strong"} (${st.score}) — ${sp < 0 ? "the season controls you" : sp > 0 ? "the season carries you" : "the season is neutral"}${stage ? ` (${stage})` : ""}, not which element has the biggest bar.`,
    line2: topSup ? `${elb(topSup.el)} ${topSup.zh} ${elw(topSup.el)} supports hardest (${topSup.w}) — support ${pt.support} ${pt.support > pt.drain ? "beats" : "trails"} drain ${pt.drain}, ${weak && pt.support > pt.drain ? "yet the season still tips it weak" : !weak && pt.support < pt.drain ? "yet the season still carries it strong" : "and the verdict follows"}.` : "",
    facts: [[st.verdict.split(" ")[0], `${st.score}`], ["Support", `${pt.support}`], ["Drain", `${pt.drain}`],
      c.tiaohou ? ["Seasonal adjustment", c.tiaohou.verdict] : null].filter(Boolean),
    legend: `<div class="cite">Formation check: ${st.formation.detail}. Support ratio = share of the chart feeding the Day Master; root mass = share of hidden stems carrying its element.</div>
      ${(st.steps || []).map((s) => `<div class="cite"><b>${s.step}. ${s.name}:</b> ${s.value} — ${s.detail}</div>`).join("")}${legendList(2)}
      ${c.tiaohou && c.tiaohou.line ? `<div class="cite">${c.tiaohou.line} <span class="tag">${c.tiaohou.source_ref}</span></div>` : ""}` });
  const H = c.health || [];
  const table = `<div class="scrollx"><table class="htable"><tr><th>Element</th><th>Organ systems</th><th>Watch aspects</th><th>Status</th></tr>
    ${H.map((h) => `<tr><td>${elb(h.element)}</td><td class="sub">${h.organs}</td><td class="sub">${h.aspects}</td>
      <td class="${h.status.startsWith("balanced") ? "" : "bad"}">${h.status}</td></tr>`).join("")}</table></div>`;
  const excess = H.find((h) => /excess|過旺|过旺/i.test(h.status)), weakEl = H.find((h) => /weak|不足/i.test(h.status));
  const hline = excess ? `${elb(excess.element)} ${elw(excess.element)} excess (${excess.share}%) — watch ${excess.organs}; ${(excess.aspects.split(";").pop() || "").trim()} is the pattern to notice.`
    : weakEl ? `${elb(weakEl.element)} ${elw(weakEl.element)} weak (${weakEl.share}%) — support ${weakEl.organs}; watch ${weakEl.aspects}.`
    : "All five elements sit in range — no organ system is flagged.";
  const h1 = rdFig({ tier: "secondary", span: 7, label: "Health element map", learn: 11, chart: table, line: hline,
    facts: [["Excess", H.filter((h) => /excess|過旺|过旺/i.test(h.status)).map((h) => elc(h.element)).join("·") || "—"],
      ["Deficient", H.filter((h) => /weak|不足/i.test(h.status)).map((h) => elc(h.element)).join("·") || "—"]],
    legend: legendList(11) });
  return { figs: { pentagon: e2, gauge: e45, health: h1 }, units,
    tail: [R.narr(1), R.narr(2), R.stb(2), R.narr(11), R.stb(11)] };
}

/* --- 十神 Gods -------------------------------------------------------------- */
function buildGods(c, R) {
  const dm = c.day_master, en = (g) => (c.tengods_legend[g] || {}).en || TG_EN_FALLBACK[g] || "";
  const gs = groupSums(c).sort((a, b) => b[1] - a[1]);
  const g2 = rdFig({ tier: "hero", span: 5, label: "The god wheel", learn: 4,
    chart: `<div class="tgwrap svg-plate">${tenGodsWheel(c, { groupsOnly: true, zh: true })}</div>`,
    line: `${gs[0][0]} ${GRP_EN[gs[0][0]]} lead your wheel at ${gs[0][1]}%, ${gs[1][0]} ${GRP_EN[gs[1][0]]} ${gs[0][1] - gs[1][1] < 12 ? "close behind" : "behind"} at ${gs[1][1]}%.`,
    facts: gs.slice(0, 2).map(([z, v]) => [z, `${v}%`]),
    legend: `<div>The five circles are the ten roles in five groups; a bigger circle is a bigger share of your chart. The centre is you, the Day Master (日元).</div>
      ${WHEEL_KEY.map(([zh, name, a, b]) => `<div><b class="keepzh">${zh}</b> <b>${name}</b>: ${en(a)} (${a}) and ${en(b)} (${b})</div>`).join("")}
      <div>Solid green arrows: each group feeds the next. Dashed red arrows: each group checks the one it points at.</div>${legendList(4)}` });
  const rows = ALLGODS.map((g) => [g, c.tengods_pct[g] || 0]), pmax = Math.max(...rows.map(([, v]) => v)) || 1;
  const [g1, p1] = topGod(c), absent = ALLGODS.filter((g) => !(c.tengods_pct[g] > 0));
  const bars = `<div class="bars tgbars">${rows.map(([g, p]) => `<div class="bar-row tg-row2${p ? "" : " tg-zero"}">
      <span><b style="color:${EL_TXT[godEl(dm, g)]}">${en(g)}</b> <span class="sub keepzh">(${g})</span></span>
      <div class="bar">${p ? `<i style="width:${(p / pmax * 100).toFixed(0)}%;background:${EL_COL[godEl(dm, g)]}"></i>` : ""}</div>
      <b>${p ? p + "%" : "0% (absent)"}</b></div>`).join("")}</div>`;
  const sex = c.sex, grp = (gods) => Math.round(gods.reduce((a, g) => a + (c.tengods_pct[g] || 0), 0) * 10) / 10;
  const band = (p) => p >= 20 ? "prominent" : p >= 8 ? "present" : p > 0 ? "faint" : "absent";
  const starRows = [["Spouse star", sex === "M" ? "正財+偏財" : "正官+七殺", sex === "M" ? ["正財", "偏財"] : ["正官", "七殺"]],
    ["Wealth stars", "正財+偏財", ["正財", "偏財"]], ["Authority stars", "正官+七殺", ["正官", "七殺"]],
    ["Resource stars", "正印+偏印", ["正印", "偏印"]], ["Output stars", "食神+傷官", ["食神", "傷官"]],
    ["Peer stars", "比肩+劫財", ["比肩", "劫財"]]];
  const g1f = rdFig({ tier: "hero", span: 7, extra: "rd-pair2", label: "Ten-god bars", learn: 4, chart: bars,
    line: `Your chart runs on ${godc(dm, g1)} ${en(g1)} (${Math.round(p1)}%) — ${(c.tengods_legend[g1] || {}).meaning || GRP_THEME[grpOfGod(g1)]}.`,
    facts: [[g1, `${p1}%`], ["absent", `${absent.length} of 10 gods`]],
    legend: `<div>Each bar is how much of your chart one role takes up. A role is what a character is to you, the Day Master.</div>
      <div><b>Bands:</b> 20% or more is prominent, 8% or more is present, under 8% is faint, 0% is absent.</div>
      <div class="tgkey2">${ALLGODS.map((g) => `<div><b style="color:${EL_TXT[godEl(dm, g)]}">${en(g)}</b> <span class="keepzh">(${g})</span>: ${TG_GIST[g] || ""}</div>`).join("")}</div>
      <table class="tgsides"><tr><th>Group</th><th>This chart</th></tr>${starRows.map(([t, , gods]) => { const p = grp(gods);
        return `<tr><td><b>${t}</b> <span class="sub">${gods.map(en).join(" and ")}</span></td><td>${p}%, ${band(p)}</td></tr>`; }).join("")}</table>` });
  const axes = c.personality || [];
  const pax = `<div class="paxchips">${axes.map((a) => { if (!a.zone) return `<div class="pax"><b>${a.axis}</b> ${a.verdict}<div class="sub">${a.basis}</div></div>`;
    const pos = a.zone === "left" ? 16 : a.zone === "right" ? 84 : 50;
    return `<div class="pax"><b>${a.axis}</b><div class="paxv ${a.zone}">${a.verdict}</div>
      <div class="paxstrip"><span class="pz l"></span><span class="pz m"></span><span class="pz r"></span><i style="left:${pos}%"></i></div>
      <div class="paxends"><span>${a.poles.left.zh} <small>${a.poles.left.en}</small></span><span class="mid">neutral</span>
        <span>${a.poles.right.zh} <small>${a.poles.right.en}</small></span></div>
      <div class="paxm">${a.metrics.map((m) => `<span>${m.label} <b>${m.pct}%</b></span>`).join("")}</div><div class="sub">${a.basis}</div></div>`; }).join("")}</div>`;
  const sharp = axes.filter((a) => a.zone && a.zone !== "mid" && a.metrics && a.metrics.length)
    .sort((a, b) => Math.max(...b.metrics.map((m) => m.pct)) - Math.max(...a.metrics.map((m) => m.pct)))[0];
  const g8 = rdFig({ tier: "secondary", span: 6, label: "Personality axes", learn: 10, chart: pax,
    line: sharp ? `${sharp.verdict.charAt(0).toUpperCase() + sharp.verdict.slice(1)} — ${sharp.metrics[0].label} make up ${sharp.metrics[0].pct}% of your chart, your sharpest trait.`
      : "No strong tendency on any axis — a balanced profile, not a failure.",
    facts: axes.filter((a) => a.zone && a.zone !== "mid").slice(0, 2).map((a) => [a.axis.split(" ")[0], a.verdict.split(" — ")[0]]),
    legend: legendList(10) });
  const ti = c.tengod_insights; let g5 = "";
  if (ti) {
    const geju = c.geju ? `<div class="geju">${gejuPlain(c.geju)}</div>` : "";
    const chart = geju + ti.favor.map((f) => `<div class="cite structrow"><b>${f.god} ${f.pct}%</b> ${elb(f.el)}
        <span class="dirchip ${f.status === "favourable" ? "good" : f.status === "unfavourable" ? "bad" : ""}">${f.status}</span> — ${f.note}</div>`).join("")
      + `<div class="cite" style="margin-top:6px"><b>Visible stems:</b> ${ti.rooted.map((r) => `<span class="dirchip ${r.state === "rooted" ? "good" : "bad"}">${r.god} ${r.state === "rooted" ? "rooted" : "floating"}</span>`).join(" ")}</div>`
      + (ti.patterns.length ? `<details class="deep pairpat"><summary>pair patterns · ${ti.patterns.length}</summary><div class="deepbody">${ti.patterns.map((p) => `<div class="ninline"><b>${p.name} — ${p.zh}</b> ${p.state ? `<span class="dirchip ${p.state.startsWith("formed") ? "good" : ""}">${p.state}</span>` : ""}<div>${p.note}${p.activation ? ` <b>${p.activation}.</b>` : ""}</div></div>`).join("")}</div></details>`
        : `<div class="cite">No classical pair pattern triggers — the gods operate independently in this chart.</div>`);
    const bad = ti.favor.find((f) => f.status === "unfavourable"), good = ti.favor.find((f) => f.status === "favourable");
    g5 = rdFig({ tier: "secondary", span: 6, label: "Structure check", learn: 4, chart,
      line: bad ? `${godc(dm, bad.god)} (${bad.pct}%) carries an unfavourable element (${elc(bad.el)}) — use it deliberately, budget recovery.`
        : good ? `${godc(dm, good.god)} (${good.pct}%) carries ${elc(good.el)}, one of your 用神 — a clean engine; using it strengthens the chart.`
        : "The heavy gods sit outside both lists — structure is neutral here.",
      facts: [["favourable", `${ti.favor.filter((f) => f.status === "favourable").length} of ${ti.favor.length} heavy gods`],
        ["rooted", `${ti.rooted.filter((r) => r.state === "rooted").length} stems`]],
      legend: `<div>Three checks a percentage chart cannot make: is the heavy god aligned with your 用神, is it rooted in the branches, and what do the gods form together. Personality is not static: the current decade (时运 tab) overlays its own gods.</div>` });
  }
  const P = c.palaces; let ld = "";
  if (P && c.domains) {
    const g = (...n) => Math.round(n.reduce((a, k) => a + (c.tengods_pct[k] || 0), 0) * 10) / 10;
    const inPal = (keys, groups) => keys.some((k) => { const p = P.pillars.find((x) => x.key === k);
      return p && [p.stem_god, ...(p.hidden || [])].some((gd) => groups.includes(tgCanon(gd))); });
    const sig = { 事业官星: ["正官·七殺", g("正官", "七殺", "七杀"), ["month"], ["正官", "七殺"], "Month pillar"],
      财富财库: ["正財·偏財", g("正財", "正财", "偏財", "偏财"), ["month", "day"], ["正財", "偏財"], "Month · Day"],
      学习文昌: ["正印·偏印", g("正印", "偏印"), ["year", "month"], ["正印", "偏印"], "Year · Month"],
      感情稳定: [sex === "M" ? "正財·偏財 (spouse star)" : "正官·七殺 (spouse star)", sex === "M" ? g("正財", "正财", "偏財", "偏财") : g("正官", "七殺", "七杀"), ["day"], sex === "M" ? ["正財", "偏財"] : ["正官", "七殺"], "Day branch"] };
    const extra = [["才华 Talent &amp; enterprise", "食神·傷官", g("食神", "傷官", "伤官"), ["hour"], ["食神", "傷官"], "Hour pillar"],
      ["人脉 Network &amp; competition", "比肩·劫財", g("比肩", "劫財", "劫财"), ["year", "month"], ["比肩", "劫財"], "Year · Month"]];
    const chip = (e) => `<span class="tag${e.delta < 0 ? " warn" : ""}">${e.label} ${e.delta > 0 ? "+" : ""}${e.delta}</span>`;
    const row = (zh, enTxt, score, band, s, ev) => { const cls = score == null ? "" : score >= 70 ? "good" : score < 45 ? "weak" : "";
      const sc = score == null ? '<span class="sub">— signal only</span>' : `<div class="dbar"><i class="${cls}" style="width:${score}%"></i></div><b class="dnum ${cls === "good" ? "b-good" : cls === "weak" ? "b-weak" : ""}">${score}</b>`;
      return `<tr><td><b>${enTxt}</b> <span class="zhs">(${zh})</span></td><td class="ldscore">${sc}</td>
        <td class="sub">${s ? `${s[0]} <b>${s[1]}%</b>` : "—"}</td><td class="seat">${s ? `<span class="seat-pal">${s[4]}</span><span class="dirchip ${inPal(s[2], s[3]) ? "good" : ""}">${inPal(s[2], s[3]) ? "✓ seated" : "elsewhere"}</span>` : "—"}</td>
        <td class="ldev">${ev.slice().sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta)).slice(0, 3).map(chip).join(" ")}</td></tr>`; };
    const doms = c.domains.slice().sort((a, b) => b.score - a.score);
    const table = `<div class="scrollx"><table class="bc-table ldtable"><tr><th>Life domain</th><th>Score</th><th>Signal gods · share</th><th>Seat</th><th>Evidence</th></tr>
      ${doms.map((d) => row(d.zh, d.en, d.score, d.band, sig[d.zh], d.evidence)).join("")}
      ${extra.map(([n, sg, sh, keys, groups, pal]) => row(n.split(" ")[0], n.split(" ").slice(1).join(" "), null, null, [sg, sh, keys, groups, pal], [])).join("")}</table></div>`;
    const top = doms[0], low = doms[doms.length - 1];
    const sigs = [...Object.entries(sig).map(([k, v]) => [k, v]), ...extra.map((e) => [e[0], [e[1], e[2], e[3], e[4], e[5]]])];
    const heavy = sigs.sort((a, b) => b[1][1] - a[1][1])[0];
    const heavyName = (c.domains.find((d) => d.zh === heavy[0]) || {}).en || heavy[0].replace(/^\S+\s/, "").replace("&amp;", "&");
    ld = rdFig({ tier: "secondary", span: 12, label: "Life domains: score, signal, seat", learn: 8, chart: table,
      line: `${top.en} leads at ${top.score}; your heaviest signal is ${heavyName.toLowerCase()} — ${heavy[1][1]}%, ${inPal(heavy[1][2], heavy[1][3]) ? "seated in" : "from"} ${heavy[1][4]}.`,
      facts: [["strongest", `${top.en} ${top.score}`], ["weakest", `${low.en} ${low.score}`], ["domains", `${doms.length + extra.length}`]],
      legend: `<div><b>Score</b> starts at a neutral 50; every chip is a rule that moved it. <b>Signal gods</b> govern the domain; <b>seat</b> is the pillar they sit in and whether that is the domain's own palace (得位).</div>
        ${doms.map((d) => `<div class="cite"><b>${d.en} (${d.zh})</b> · ${d.band.replace(/^(.*?)\s+([㐀-鿿]+)$/, "$1 ($2)")}: ${d.evidence.map(chip).join(" ")}</div>`).join("")}
        ${c.spouse_reading ? `<div class="cite"><b>Marriage:</b> ${c.spouse_reading.star_line} ${c.spouse_reading.palace_line}</div>` : ""}${legendList(8)}` });
  }
  // raw pillar data (G7) retired 2026-09-27: the Pillars grid carries every stem/hidden stem; its key lives in the bars' legend. Gods = 7 figures.
  let k1 = "", k3 = "";
  if (c.industries) {
    const F = c.industries.favourable || [], A = c.industries.avoid || [];
    const chart = `<div class="klist-ind">${F.map((it) => `<div class="cite"><b>Favourable ${elb(it.element)} ${elw(it.element)} industries</b> — ${it.industries}</div>`).join("")}
      <div class="cite">Understated: ${A.map((it) => `${elb(it.element)} (${it.industries.split(",")[0]}…)`).join("; ")} — not forbidden, just not where this chart recharges.</div></div>`;
    const f0 = F[0];
    k1 = rdFig({ tier: "reference", span: 12, label: "Favourable industries", learn: 12, chart,
      line: f0 ? `${elw(f0.element)} suits you best — ${f0.industries.split(",").slice(0, 3).map((s) => s.trim()).join(", ")} top the list.` : "No favourable field is listed for this chart.",
      facts: [['Favourable <span class="keepzh">(宜)</span>', elbs(F.map((it) => it.element))], ['Go carefully <span class="keepzh">(慎)</span>', elbs(A.map((it) => it.element))]], legend: legendList(12) });
  }
  if (c.careers) {
    const R = (c.career_roles || {}).top || [], rmx = Math.max(...R.map((x) => Math.abs(x.score)), 1);
    const rolesChart = R.length ? `<div class="klist">${R.map((x, i) =>
      `<div class="krow"><span class="klab">#${i + 1} ${x.role} <small>${x.parent}${x.basis === "arguable" ? " · mapping arguable" : ""}</small></span>
        <div class="kbar"><i style="width:${(Math.abs(x.score) / rmx * 100).toFixed(0)}%"></i></div><b>${x.score}</b></div>`).join("")}</div>` : "";
    if (R.length) {
      const r0 = R[0];
      k3 = rdFig({ tier: "reference", span: 6, label: "Roles today", learn: 12, chart: rolesChart,
        line: `#1 today: ${r0.role} (${r0.score} pts) — ${clip(r0.reasons[0].split(" — ")[0], 44)}.`,
        facts: [["#1", `${r0.score} pts`], ["arguable mappings", `${R.filter((x) => x.basis === "arguable").length} of ${R.length}`]],
        legend: `<div>Present-day roles scored on the archetype rules — the field's element against the 用神 lists and the ten-god working style. Each role carries its parent archetype; "mapping arguable" marks roles whose element assignment is a modern convention, not a classical one.</div>
          ${R.map((x) => `<div><b>${x.role}</b> (${x.score} pts) — ${x.reasons.join("; ")}</div>`).join("")}` });
    }
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
      ${x.keywords ? `<div class="dykw">${x.keywords}</div>` : ""}${d.current ? `<div class="ccdyhere">▲ now</div>` : ""}</div>`; }).join("")}</div>`;
  const gods = [...new Set(dd.flatMap((x) => [x.stem_god, x.branch_god]).filter(Boolean))];
  const phases = [...new Map(W.decades.map((d) => [d.phase, d.phase_zh])).entries()];
  const stripKey = `<div class="tkey"><p><b>Each card:</b> the ages, the decade's pillar (stem over branch), its phase, the two roles it brings, and what those roles mean.</p>
    <p><b>Phases:</b> ${phases.map(([en, zh]) => `<span class="keepzh">${zh}</span> ${PHASE_EN[en] || en}`).join(" · ")}</p>
    <p><b>Pillars:</b> ${W.decades.map((d) => `<span class="keepzh">${gzc(d.gz)}</span> ${STEM_YANG[d.gz[0]] ? "yang" : "yin"} ${EL_EN[STEM_EL[d.gz[0]]]} over ${(ZODIAC[BR_ANIMAL[d.gz[1]]] || ["", d.gz[1]])[1]} (${EL_EN[BR_EL[d.gz[1]]]})`).join("; ")}</p>
    <p><b>Roles:</b> ${gods.map((g) => `<span class="keepzh">${godz(g)}</span> ${TG_EN_FALLBACK[tgCanon(g)] || TG_EN_FALLBACK[g] || ""}`).join(" · ")}</p></div>`;
  const ci = W.decades.findIndex((d) => d.current), cur = W.decades[ci], nxt = W.decades[ci + 1];
  const arc = ((W.arc || "").match(/Element arc: (.*?) —/) || [])[1];
  const t1 = rdFig({ tier: "hero", span: 12, label: "Decade strip", learn: 6, chart: strip,
    line: cur ? `In the ${cur.gz} decade (${cur.ages}, ${cur.phase}) — ${nxt ? `shifts to ${nxt.gz} (${nxt.phase}) at age ${String(nxt.ages).split(/[–-]/)[0]}.` : "the last charted decade."}`
      : `Before the first decade — ${W.decades[0] ? `${W.decades[0].gz} begins at age ${String(W.decades[0].ages).split(/[–-]/)[0]}.` : ""}`,
    facts: [cur ? ["Luck cycle", `${cur.gz} · ${cur.ages}`] : null, nxt ? ["next", `${nxt.gz} · ${nxt.ages}`] : null,
      c.dayun && c.dayun[0] ? ["Starts at age", `${String(c.dayun[0].ages).split(/[–-]/)[0]}`] : null, arc ? ["arc", arc] : null].filter(Boolean),
    legend: `${stripKey}${legendList(6)}${W.arc ? `<div class="cite"><b>Life arc:</b> ${W.arc}</div>` : ""}
      ${W.taohua ? `<div class="cite"><b>Peach blossom:</b> ${W.taohua.branch} — ${W.taohua.type}${W.taohua.pillars.length ? ` (in the ${W.taohua.pillars.join("/")} pillar)` : ""}</div>` : ""}` });
  const T = c.transit || {}, L = T.luck || {};
  const gDec = [grpOfGod(L.stem_god || ""), grpOfGod(L.branch_god || "")], gYr = [grpOfGod(T.year_stem_god || ""), grpOfGod(T.year_branch_god || "")];
  const theme = (pair) => pair[0] === pair[1] ? GRP_THEME[pair[0]] : `${GRP_THEME[pair[0]]} with ${GRP_THEME[pair[1]]}`;
  const p8 = rdFig({ tier: "secondary", span: 5, label: "This year, on this decade", learn: 13,
    chart: `<div class="pillar-cards"><div class="pillar-card transit"><div class="gz">${T.year_gz}</div><div class="pos">YEAR ${state.year}</div>
        <div class="god">${T.year_stem_god}/${T.year_branch_god}</div><div class="sub">annual transit</div></div>
      ${L.gz ? `<div class="pillar-chip">on the ${L.gz} decade · ages ${L.ages} · ${L.stem_god}/${L.branch_god}</div>` : ""}</div>`,
    line: `${L.gz ? `This decade ${gDec[0] === gDec[1] ? "doubles down on" : "mixes"} ${theme(gDec)}; this year adds` : "This year brings"} ${theme(gYr)} on top.`,
    facts: [L.gz ? ["LUCK", `ages ${L.ages}`] : null, ["YEAR", `${state.year}`]].filter(Boolean),
    legend: "The two cards are the energies currently overlaid on the birth chart — the active 10-year luck pillar and this year's pillar — labelled with their ten gods relative to this Day Master." });
  const RH = ((c.strategy || {}).s5 || {}).rhythm; let t6 = "";
  if (RH && RH.length) {
    const nowBr = (c.daily || {}).now_month_branch;
    const cells = RH.map((r) => `<div class="rcell ${r.cls}${r.br === nowBr ? " now" : ""}"><small>${r.mon}</small><b style="color:${EL_TXT[r.el]}">${r.br}</b><span class="rel" style="color:${EL_TXT[r.el]}">${r.el}</span><span class="rrate">${r.cls === "good" ? "good" : "pace"}</span>${r.br === nowBr ? `<em class="rnow">▲ now</em>` : ""}</div>`).join("");
    const order = RH.map((r) => r.mon), ranges = (ms) => { const idx = ms.map((m) => order.indexOf(m)).sort((a, b) => a - b), out = []; let i = 0;
      while (i < idx.length) { let j = i; while (j + 1 < idx.length && idx[j + 1] === idx[j] + 1) j++;
        out.push(i === j ? order[idx[i]] : `${order[idx[i]]}–${order[idx[j]]}`); i = j + 1; } return out.join(", "); };
    const good = RH.filter((r) => r.cls === "good"), bad = RH.filter((r) => r.cls !== "good");
    const gel = [...new Set(good.map((r) => r.el))].map(elw).join(" and ");
    t6 = rdFig({ tier: "secondary", span: 7, label: "Monthly rhythm", learn: 13, chart: `<div class="rhy keepzh">${cells}</div>`,
      line: good.length ? `Good months: ${ranges(good.map((r) => r.mon))} (${gel}). Pace ${ranges(bad.map((r) => r.mon))}.` : "No month carries your medicine — pace the whole year evenly.",
      facts: [["good", `${good.length}`], ["pace", `${bad.length}`]],
      legend: "Each solar month carries a branch and its element. Months whose element is your medicine are marked good; months carrying a 忌神 element are marked to pace. The rhythm is the same every year — the 流年 table says which years lift or lower it." });
  }
  const daily = dailyFig(c);
  return { figs: { strip: t1, thisyear: p8, rhythm: t6, daily }, tail: [R.stb(13), R.narr(13), R.narr(6)] };
}

/* 流日 daily fortune — the next 30 days, six activities, from the engine's daily layer */
const OFFICER_EN = { 建: "Establish", 除: "Remove", 满: "Full", 滿: "Full", 平: "Neutral", 定: "Settle", 执: "Hold", 執: "Hold", 破: "Destruction",
  危: "Danger", 成: "Completion", 收: "Receive", 开: "Open", 開: "Open", 闭: "Close", 閉: "Close" };
const TAG_EN = { 合日支: "combines with your day branch", 冲日支: "clashes your day branch", 沖日支: "clashes your day branch", 害日支: "harms your day branch",
  冲生肖: "clashes your zodiac animal", 沖生肖: "clashes your zodiac animal", 刑日支: "punishes your day branch" };
const PHASE_EN = { growth: "growth", consolidation: "gathering (building reserves)", transition: "changing", corrective: "repairing" };
const ACT_EN = { moving: "moving", signing: "signing", marriage: "marriage", travel: "travel", medical: "medical", launch: "launch" };
function dailyFig(c) {
  const D = c.daily; if (!D || !(D.rows || []).length) return "";
  const dm = c.day_master, acts = D.activities || [];
  const mark = (f) => f.verdict === "good" ? "◉" : f.verdict === "avoid" ? "⚠" : "·";
  const rows = D.rows.map((r) => `<tr class="${r.today ? "today" : ""}${r.officer === "破" || r.interactions.some((x) => x.startsWith("沖")) ? " dclash" : ""}">
      <th>${r.date.slice(5)} <small>${r.weekday}</small>${r.today ? '<em class="rnow">▲ now</em>' : ""}</th>
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
  const line = (B ? `Best day this month for ${B.for.slice(0, 2).map((k) => ACT_EN[k]).join(" or ")}: ${B.date.slice(5)} ${B.gz} (${B.officer} day).` : "No clear best day this month.")
    + (W && W.avoid.length ? ` Avoid ${W.avoid.slice(0, 2).map((k) => ACT_EN[k]).join(" and ")} on ${W.date.slice(5)} ${W.gz} — ${W.why}.` : "");
  const nGood = D.rows.filter((r) => Object.values(r.flags).some((f) => f.verdict === "good")).length;
  const nAvoid = D.rows.filter((r) => Object.values(r.flags).some((f) => f.verdict === "avoid")).length;
  return rdFig({ tier: "secondary", span: 12, label: "Daily fortune, next 30 days", learn: 13, chart: table, line,
    facts: [["from", D.start], ["good days", `${nGood}`], ["days with a caution", `${nAvoid}`]],
    legend: `<div class="tkey"><p><b>Columns:</b> <span class="keepzh">日期</span> date · <span class="keepzh">日柱</span> day pillar (with its day officer) · <span class="keepzh">十神</span> the roles the day brings you · <span class="keepzh">五行</span> the day's element (<span class="keepzh">用</span> useful to you, <span class="keepzh">忌</span> to avoid) · ${actZh.map(([, zh, en]) => `<span class="keepzh">${zh}</span> ${en}`).join(" · ")}</p>
      <p><b>Day officers:</b> ${officers.map((o) => `<span class="keepzh">${o}</span> ${OFFICER_EN[o] || ""}`).join(" · ")}</p>
      ${tags.length ? `<p><b>Tags:</b> ${tags.map((x) => `<span class="keepzh">${x}</span> ${TAG_EN[x] || ""}`).join(" · ")}</p>` : ""}</div>
      <div><b>◉ good · ⚠ avoid · · neutral</b> — per activity, hover a cell for the deciding rule.</div>
      <div><b>Twelve day officers</b> Completion, Open and Settle are good for most acts; Remove suits treatment; Close and Danger hold back travel and moving; Break (and any day that clashes the month) is avoided for everything.</div>
      <div><b>Your branches</b> a day branch that clashes your day branch (${elc(c.pillars.day[1])}) or year branch (${elc(c.pillars.year[1])}) is avoided for marriage, moving and launches; a Six Combination with your day branch favours marriage and signing; a Harm holds back medical.</div>
      <div><b>Element of the day</b> a day stem carrying your primary useful god favours launches and signing; one carrying your chief avoided element is avoided for banking and launches.</div>
      <div class="sub">${D.source_ref}</div>` });
}

/* --- 方位 Compass ------------------------------------------------------------- */
function buildCompass(c, R) {
  const dirOf = {}; Object.entries(c.youxing).forEach(([pal, s]) => (dirOf[s] = PALACE_DIR[pal]));
  const c1 = rdFig({ tier: "hero", span: 5, label: "Eight House 3×3 grid", learn: 7,
    chart: `<div class="cmpx-wrap">${bazhaiCompass(c)}</div>`,
    line: `Face <b>${dirOf["生氣"]}</b> (Vitality) for bed and desk; keep long sitting out of <b>${dirOf["絕命"]}</b> (Severed Fate).`,
    facts: [["Kua number", `${c.gua} · ${c.group.split(" ")[0]}`], ["生氣", dirOf["生氣"]], ["絕命", dirOf["絕命"]], ["五鬼", dirOf["五鬼"]]],
    legend: `${BAZHAI_ORDER.map((s) => `<div><b>${s} ${BAZHAI_EN[s][0]}</b> — ${BAZHAI_EN[s][1]}</div>`).join("")}
      <div class="cite"><b>Two layers:</b> 八宅 grades ORIENTATION — where to face and head long-stay activities; 用神 grades ELEMENT CONTENT — what colours, materials and fields feed the chart. A green direction whose element is unfavourable is still a good direction to FACE — furnish it in the 用神 palette. 命卦 comes from the birth year alone; the 用神 layer is the personal one.</div>${legendList(7)}` });
  const fav = c.yongshen.favourable, unf = c.yongshen.unfavourable, cols = c.yongshen.colours || [];
  const colEn = cols.map((z) => COLOUR_ZH_EN[z] || z).slice(0, 2).join("/");
  const chart = `${c.medicine_rank ? `<p class="cite" style="margin:0 0 6px"><b>Medicine, ranked:</b> ${c.medicine_rank.replace(/^Medicine, ranked:\s*/, "")}</p>` : ""}
    <p class="cite" style="margin:0 0 8px">Favourable ${elbs(fav)} · avoid ${elbs(unf)} · colours <b>${cols.join("、")}</b></p>
    ${c.xiji ? `<div class="scrollx"><table class="xiji htable">${c.xiji.map((r) => `<tr><th>${r.zh}</th>
      <td>${r.elements.map((e) => elb(e)).join(" ")}</td><td class="sub">${r.gods.join("·")}</td></tr>`).join("")}</table></div>` : ""}`;
  const EL_DIR = { 木: ["东 E", "震·巽"], 火: ["南 S", "離"], 土: ["西南·东北 SW/NE", "坤·艮 (centre)"], 金: ["西 W", "乾·兌"], 水: ["北 N", "坎"] };
  const EL_ROOM = { 木: "east wall, plants and timber, green accents", 火: "south wall, warm light, red/orange accent",
    土: "centre or SW/NE, ceramics and stone, yellow/brown tones", 金: "west wall, metal frames and white/gold", 水: "north wall, glass or a water feature, blue/black" };
  const dirTable = `<div class="scrollx"><table class="htable eldir"><tr><th>Useful god</th><th>Direction</th><th>Palace</th><th>in the room</th></tr>
    ${fav.map((e) => `<tr><td>${elb(e)}</td><td><b>${EL_DIR[e][0]}</b></td><td>${EL_DIR[e][1]}</td><td class="sub">${EL_ROOM[e]}</td></tr>`).join("")}</table></div>`;
  const chart2 = dirTable + chart;
  const c34 = rdFig({ tier: "hero", span: 7, extra: "rd-pair2", label: "Where the medicine sits", learn: 5, chart: chart2,
    line: `Add ${elw(fav[0])} (${elc(fav[0])})${colEn ? `, in ${colEn},` : ""} through lighting or an accent wall; keep ${unf.map((e) => EL_EN[e]).join("/")} (${unf.map(elc).join("")}) out of your main room.`,
    facts: [["Useful god", elbs(fav)], ["Avoid", elbs(unf)], c.tiaohou ? ["Seasonal adjustment", c.tiaohou.verdict] : null].filter(Boolean),
    legend: `<div><b>Technique:</b> 扶抑 supports a weak chart or restrains a strong one; 调候 corrects its season — for this chart, add ${fav.map((e) => EL_EN[e]).join(" and ")}, keep ${unf.map((e) => EL_EN[e]).join(", ")} light.</div>
      ${c.tiaohou && c.tiaohou.line ? `<div class="cite">${c.tiaohou.line}</div>` : ""}
      ${c.element_relations ? `<div class="cite"><b>In god vocabulary:</b> your 用神 ${fav.map((el) => { const f = Object.values(c.element_relations.flows).find((x) => x.el === el);
        return `${elb(el)} arrives as <b>${f ? f.role : "—"}</b>`; }).join(" · ")} — those life-areas ARE the medicine.</div>` : ""}
      ${(c.yongshen.citations || []).map((x) => `<div class="cite"><b>${x.source_ref}:</b> ${x.explanation}</div>`).join("")}${legendList(5)}` });
  const PL = c.placements || [], AF = c.afflictions;
  const bed = PL.find((r) => r.key === "bed"), desk = PL.find((r) => r.key === "desk");
  const c2 = PL.length ? rdFig({ tier: "secondary", span: 7, label: "Placements", learn: 7,
    chart: `<div class="scrollx"><table class="htable pltable"><tr><th>Placement</th><th>Direction</th><th>Rule</th></tr>
      ${PL.map((r) => `<tr><th>${r.zh}<small>${r.en}</small></th><td><b class="pdir">${r.dir}</b> ${r.palace}${r.star ? ` <span class="tag">${r.star}</span>` : r.branch ? ` <span class="tag">${r.branch}</span>` : ""}</td><td class="sub">${r.rule}</td></tr>`).join("")}</table></div>`,
    line: `Bed head to the <b>${bed.dir}</b> (${bed.star}), desk facing <b>${desk.dir}</b> (${desk.star}).`,
    facts: [["Bed head", bed.dir], ["Desk", desk.dir], ["文昌", (PL.find((r) => r.key === "wenchang") || {}).dir || "—"], ["Peach blossom", (PL.find((r) => r.key === "taohua") || {}).dir || "—"]],
    legend: `<div>Long-stay items follow the 八宅 stars of your 命卦: 天醫 for the bed, 生氣 for desk and door, 延年 for the couples' bed, 伏位 for a quiet room. The three corners are personal 神煞 — 文昌 by day stem, 桃花 and 驛馬 by the year-branch trine — mapped to their palace.</div>
      <div class="cite">A direction is where the head or face points; when the room cannot allow the first choice, take the next favourable star, never an unfavourable one.</div>` }) : "";
  const c5 = AF ? rdFig({ tier: "secondary", span: 5, label: `${AF.year} afflictions`, learn: 7,
    chart: `<table class="htable aftable">
      <tr><th>Grand Duke (太岁)</th><td><b class="pdir">${AF.taisui.dir}</b> ${AF.taisui.palace} · ${AF.taisui.branch}</td></tr>
      <tr><th>Year Breaker (岁破)</th><td><b class="pdir">${AF.suipo.dir}</b> ${AF.suipo.palace} · ${AF.suipo.branch}</td></tr>
      <tr><th>Three Killings (三煞)</th><td><b class="pdir">${AF.sansha.dirs.join(" · ")}</b> ${AF.sansha.palaces.join("·")} · ${AF.sansha.branches}</td></tr></table>
      ${AF.collisions.length ? `<div class="afhits">${AF.collisions.map((h) => `<div class="tag warn">${h.affliction} on ${h.star} ${h.dir}</div>`).join("")}</div>` : ""}`,
    line: AF.collisions.length ? `${AF.collisions[0].note.replace(/^your/, "Your")}.` : `None of this year's afflictions sits on your four favourable sectors.`,
    facts: [["Grand Duke", AF.taisui.dir], ["Year Breaker", AF.suipo.dir], ["Three Killings", AF.sansha.dirs.join("/")]],
    legend: `<div><b>Grand Duke</b> — ${AF.taisui.rule}</div><div><b>Year Breaker</b> — ${AF.suipo.rule}</div><div><b>Three Killings</b> — ${AF.sansha.rule}</div>
      ${AF.collisions.map((h) => `<div class="cite">${h.affliction} on your ${h.star} (${h.dir}): ${h.note.split(" — ")[1] || h.note}.</div>`).join("")}` }) : "";
  return { figs: { grid: c1, medicine: c34, placements: c2, afflictions: c5 }, tail: [R.stb(5), R.narr(5), R.narr(7)] };
}

/* Evidence panels (owner 2026-10-10): the charts' conclusions lead as "What this shows", and folds inside a
   panel open flat, so a panel never hides a second dropdown. Runs before the English pass. */
function tidyEvidence(root) {
  root.querySelectorAll(".ev").forEach((p) => {
    const lines = [...p.querySelectorAll(".rd-line")];
    if (lines.length) {
      const lead = document.createElement("div"); lead.className = "ev-lead";
      lead.innerHTML = `<p class="ev-k">What this shows</p>${lines.map((l) => `<p>${l.innerHTML}</p>`).join("")}`;
      (p.querySelector(".evh") || p.firstChild).after(lead);
      lines.forEach((l) => { const row = l.closest(".rd-line-row"); l.remove();
        if (row) { const lg = row.querySelector(".rd-legend"); if (lg) row.before(lg); row.remove(); } });
    }
    p.querySelectorAll("details").forEach((d) => {
      const sum = d.querySelector(":scope > summary"), sec = document.createElement("section");
      const title = sum ? (sum.getAttribute("aria-label") === "how to read this" ? "How to read this chart" : sum.textContent.trim()) : "";
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
    root.querySelectorAll(".rp-chap").forEach((s) => io.observe(s));
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
  root.addEventListener("toggle", markOverflow, true);
  // evidence markers: every marker with the same number opens and closes the one proof panel
  root.addEventListener("click", (ev) => {
    const b = ev.target.closest(".mk"); if (!b) return;
    const p = document.getElementById(b.getAttribute("aria-controls")); if (!p) return;
    const open = p.hidden; p.hidden = !open;
    root.querySelectorAll(`.mk[aria-controls="${p.id}"]`).forEach((x) => x.setAttribute("aria-expanded", String(open)));
    if (open) { markOverflow(); const r = p.getBoundingClientRect(); if (r.top < 0 || r.top > innerHeight - 80) p.scrollIntoView({ block: "nearest" }); }
  });
}

/* The geomancer's report (summary, findings, assessment, plan, method note) behind one fold under
   the opening: the plain answers above carry its summary, this keeps every line of it one tap away. */
function synthNote(sy) {
  if (!sy) return "";
  const body = Array.isArray(sy) ? (sy.length ? `<p class="rd-synth-p">${sy.join(" ")}</p>` : "")
    : `${sy.summary ? `<p class="rd-synth-lede">${sy.summary}</p>` : ""}
      ${(sy.findings || []).length ? `<h4>Findings</h4><dl class="rd-synth-dl">${sy.findings.map((f) => `<dt>${f.label}</dt><dd>${f.text}</dd>`).join("")}</dl>` : ""}
      ${sy.assessment ? `<h4>Assessment</h4><p class="rd-synth-p">${sy.assessment}</p>` : ""}
      ${(sy.plan || []).length ? `<h4>Plan</h4><ol class="rd-synth-plan">${sy.plan.map((x) => `<li>${x}</li>`).join("")}</ol>` : ""}
      ${sy.confidence ? `<p class="rd-synth-conf"><b>How this was worked out.</b> ${sy.confidence}</p>` : ""}`;
  return body ? `<details class="rp-more rp-report"><summary>The full report, in classical terms</summary><div class="rd-synth-body">${body}</div></details>` : "";
}

async function renderPerson(name) {
  const url = window.__CHART_URL__ ||
    `/api/chart/${encodeURIComponent(name)}?policy=${state.policy}&year=${state.year}`;
  const c = await api(url);
  const nb = splitNarr(c.interpretation);
  const SEC_ZH = { 1: "elements", 2: "strength", 3: "raw data",
    4: "distribution", 5: "useful god", 6: "luck cycles", 7: "directions",
    8: "life domains", 9: "symbolic stars", 10: "personality",
    11: "health", 12: "careers", 13: "timing windows" };
  const R = { nb,
    narr: (n) => deepWrap(`Interpretation: ${SEC_ZH[n] || ""} — the numbers read out`,
      (nb.by[n] || []).map((t) => `<div class="ninline">${dnAll(t)}</div>`).join("")),
    stb: (n) => deepWrap(`Strategy: ${SEC_ZH[n] || ""} — what this asks of you`, stratBlock(n, c.strategy)) };
  const howto = explain(
    "<b>What this page is.</b> A BaZi reading built from the birth moment. The top answers four questions in plain words: " +
    "who you are, what helps you, what this year holds and what to do.<br>" +
    "<b>Five chapters follow</b>, each a question: what you are made of, what you have too much or too little of, what drives you, " +
    "what is coming and when, and where to sit, sleep and work.<br>" +
    "<b>Every answer</b> leads with a plain sentence. Open \"Why the chart says this\" for the pillars, the rule and the citation behind it. " +
    "<b>The plain view and the classical chart</b> sit side by side; the <b>?</b> on a chart opens its legend.<br>" +
    "<b>Colour key.</b> Wood, Fire, Earth, Metal and Water each keep one colour across the page.<br>" +
    "<b>Timing is climate and weather, not prediction:</b> the decade sets the climate, the year the weather; ◉ marks a window, ⚠ a caution.",
    "person");
  $("#tab-person").innerHTML = jt(`
    <div class="rp-open">${pIdentity(c, name)}${pSides(c)}${pAnswers(c)}${synthNote(c.synthesis)}</div>
    ${pChapBar()}
    ${readingChapters(c, R)}
    <div class="rd-howto">${howto}</div>`);
  wireReading($("#tab-person"));
  const who = dn(name || c.name), h1 = document.querySelector(".pub-in h1");
  if (h1 && who) {
    h1.innerHTML = `${who} <small class="rp-sub1">Your reading (<span class="zh" lang="zh-Hans" tabindex="0" title="mìng shū · the reading">命书</span>)</small>`;
    document.title = `${who}: your BaZi reading`;
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
    catch (e) { $("#tab-person").innerHTML = `<p class="hint">load failed: ${e.message}</p>`; return; }
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
