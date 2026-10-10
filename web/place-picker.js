/* Birth place picker (2026-10-10): country, then a searchable city (native datalist). The city's longitude and
   time zone set true solar time. Every label lives in PLACE_TEXT so other languages can swap the table. */
window.PLACE_TEXT = window.PLACE_TEXT || {
  country: "Country of birth", city: "City of birth",
  cityHelp: "Pick the nearest city: its longitude and time zone set true solar time.",
};
(function () {
  const SINGAPORE = 1880252;
  let dataP = null;
  const load = () => dataP || (dataP = fetch("/static/geo/cities.json").then((r) => r.json()));
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
  /* Renders into `host`; resolves to a getter that returns the chosen city id (the capital if the typed name is unknown). */
  window.placePicker = async function (host, initialId, idp) {
    const d = await load(), T = window.PLACE_TEXT;
    const byId = new Map(d.cities.map((c) => [c[0], c]));
    const init = byId.get(+initialId) || byId.get(SINGAPORE);
    const ccs = Object.entries(d.countries).sort((a, b) => a[1].localeCompare(b[1]));
    host.innerHTML = `<div><label for="${idp}-cc">${T.country}</label><select id="${idp}-cc">${ccs.map(([cc, n]) =>
      `<option value="${cc}"${cc === init[2] ? " selected" : ""}>${esc(n)}</option>`).join("")}</select></div>
      <div><label for="${idp}-city">${T.city}</label><input id="${idp}-city" list="${idp}-list" autocomplete="off" value="${esc(init[1])}">
        <datalist id="${idp}-list"></datalist><span class="help">${T.cityHelp}</span></div>`;
    const sel = host.querySelector("select"), inp = host.querySelector("input"), dl = host.querySelector("datalist");
    const cities = (cc) => d.cities.filter((c) => c[2] === cc);
    const fill = (cc, reset) => { const cs = cities(cc);
      dl.innerHTML = cs.map((c) => `<option value="${esc(c[1])}">`).join("");
      if (reset) { const cap = cs.find((c) => c[6]) || cs[0]; inp.value = cap ? cap[1] : ""; } };
    fill(init[2], false);
    sel.addEventListener("change", () => fill(sel.value, true));
    return () => { const cs = cities(sel.value), v = inp.value.trim().toLowerCase();
      const c = cs.find((x) => x[1].toLowerCase() === v) || cs.find((x) => x[6]) || cs[0];
      return c ? c[0] : null; };
  };
})();
