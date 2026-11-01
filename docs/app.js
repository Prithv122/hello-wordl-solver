// Hello Wordl solver - browser version (same scoring as the Python solver,
// with a lighter endgame search). All words are shown in CAPITALS.
"use strict";

const MAX_GUESSES = 6;          // Hello Wordl: 6 tries at every length
const PAIR_BUDGET = 3000000;    // guess x candidate pairs evaluated per step
const FAIL_PENALTY = 20;

const $ = (s) => document.querySelector(s);
let D = null;                    // data for current length
let S = null;                    // solver state

// ---------------------------------------------------------------- patterns
function pattern(g, a, L) {      // g, a: Uint8Array codes; returns base-3 int
  const left = new Int8Array(26);
  let p = 0, pw = 1;
  const res = new Int8Array(L);
  for (let i = 0; i < L; i++) {
    if (g[i] === a[i]) res[i] = 2; else left[a[i]]++;
  }
  for (let i = 0; i < L; i++) {
    if (res[i] === 0 && left[g[i]] > 0) { res[i] = 1; left[g[i]]--; }
    p += res[i] * pw; pw *= 3;
  }
  return p;
}
const enc = (w) => Uint8Array.from(w, (c) => c.charCodeAt(0) - 97);
const patStr = (p, L) => { let s = ""; for (let i = 0; i < L; i++) { s += "byg"[p % 3]; p = Math.floor(p / 3); } return s; };
const patInt = (s) => { let p = 0, pw = 1; for (const c of s) { p += "byg".indexOf(c) * pw; pw *= 3; } return p; };
const finish = (h) => (h <= 1 ? 1 + 0.5 * h : 1.5 + 0.35 * (h - 1));

// ------------------------------------------------------------------- data
function loadLength(L) {
  return new Promise((resolve, reject) => {
    if (window.WORDL_DATA && WORDL_DATA[L]) return resolve(WORDL_DATA[L]);
    const s = document.createElement("script");
    s.src = `data/len_${String(L).padStart(2, "0")}.js`;
    s.onload = () => resolve(WORDL_DATA[L]);
    s.onerror = reject;
    document.head.appendChild(s);
  });
}

function prepare(raw) {
  const L = raw.L, words = [], w = [], guess = [], tax = [];
  for (const [c, str] of Object.entries(raw.groups)) {
    const info = raw.classes[c];
    for (let i = 0; i < str.length; i += L) {
      words.push(str.slice(i, i + L)); w.push(info.w); guess.push(info.g); tax.push(info.t);
    }
  }
  const codes = words.map(enc);
  const index = new Map(words.map((x, i) => [x, i]));
  return { L, words, codes, index, w: Float64Array.from(w), guess: Uint8Array.from(guess),
           tax: Float64Array.from(tax), openers: raw.openers, book: raw.book };
}

function newState() {
  return { cand: D.words.map((_, i) => i), history: [], rejected: new Set(), hard: $("#hard").checked };
}

// ---------------------------------------------------------------- scoring
function scoreGuess(gc, cand, wn, L, buf, touched) {
  // returns {H, E, pwin, groups, worst}
  const win = 3 ** L - 1;
  let nt = 0;
  for (let k = 0; k < cand.length; k++) {
    const p = pattern(gc, D.codes[cand[k]], L);
    if (buf.cnt[p] === 0) touched[nt++] = p;
    buf.cnt[p]++; buf.ws[p] += wn[k]; buf.wl[p] += wn[k] * Math.log2(wn[k]);
  }
  let H = 0, E = 1, pwin = 0, worst = 0, gmaxSum = 0;
  for (let t = 0; t < nt; t++) {
    const p = touched[t], ws = buf.ws[p];
    H -= ws * Math.log2(ws);
    if (p === win) pwin = ws;
    else {
      const h = Math.max(Math.log2(ws) - buf.wl[p] / ws, 0);
      E += ws * finish(h);
    }
    if (buf.cnt[p] > worst) worst = buf.cnt[p];
    buf.cnt[p] = 0; buf.ws[p] = 0; buf.wl[p] = 0;
  }
  return { H, E, pwin, groups: nt, worst };
}

function pwinNext(gc, cand, wn, L) {  // P(win now or on next turn)
  const win = 3 ** L - 1, best = new Map();
  let pw = 0;
  for (let k = 0; k < cand.length; k++) {
    const p = pattern(gc, D.codes[cand[k]], L);
    if (p === win) { pw += wn[k]; continue; }
    best.set(p, Math.max(best.get(p) || 0, wn[k]));
  }
  for (const v of best.values()) pw += v;
  return pw;
}

function rank(top = 8) {
  const L = D.L, cand = S.cand, K = cand.length;
  if (K === 0) return [];
  if (S.history.length === 0 && !S.rejected.size && D.openers.length)
    return D.openers.slice(0, top).map(([word, E, H, pwin]) => ({ word, E, H, pwin, src: "precomputed" }));
  if (S.history.length === 1 && !S.hard && !S.rejected.size && D.book && S.history[0][0] === D.book.opener) {
    const hit = D.book.p[patStr(S.history[0][1], L)];
    if (hit) return hit.slice(0, top).map(([word, E, H, pwin]) => ({ word, E, H, pwin, src: "opening book" }));
  }
  let tot = 0; for (const i of cand) tot += D.w[i];
  const wn = Float64Array.from(cand, (i) => D.w[i] / tot);
  if (K <= 2) {
    return cand.map((i, k) => ({ word: D.words[i], E: 2 - wn[k], H: K - 1, pwin: wn[k] }))
      .sort((a, b) => b.pwin - a.pwin);
  }
  // guess pool
  let pool;
  if (S.hard) pool = cand.slice();
  else { const set = new Set(cand); D.guess.forEach((g, i) => { if (g) set.add(i); }); pool = [...set]; }
  pool = pool.filter((i) => !S.rejected.has(i));
  if (pool.length * K > PAIR_BUDGET) pool = prefilter(pool, cand, wn, Math.max(250, Math.floor(PAIR_BUDGET / K)));
  const buf = { cnt: new Int32Array(3 ** L), ws: new Float64Array(3 ** L), wl: new Float64Array(3 ** L) };
  const touched = new Int32Array(Math.min(K, 3 ** L) + 1);
  const turnsLeft = MAX_GUESSES - S.history.length;
  const rows = pool.map((i) => {
    const r = scoreGuess(D.codes[i], cand, wn, L, buf, touched);
    r.word = D.words[i]; r.cost = r.E + D.tax[i]; r.i = i;
    return r;
  });
  rows.sort((a, b) => a.cost - b.cost || b.pwin - a.pwin);
  if (turnsLeft <= 2 && K <= 400) {         // exact last-two-turns maths
    for (const r of rows.slice(0, 40)) {
      const p2 = turnsLeft === 1 ? r.pwin : pwinNext(D.codes[r.i], cand, wn, L);
      r.cost = r.E + D.tax[r.i] + FAIL_PENALTY * (1 - p2);
    }
    const head = rows.slice(0, 40).sort((a, b) => a.cost - b.cost);
    return head.slice(0, top);
  }
  return rows.slice(0, top);
}

function prefilter(pool, cand, wn, keep) {
  const L = D.L, f = new Float64Array(26), pos = Array.from({ length: L }, () => new Float64Array(26));
  cand.forEach((i, k) => {
    const c = D.codes[i], seen = new Uint8Array(26);
    for (let j = 0; j < L; j++) { pos[j][c[j]] += wn[k]; if (!seen[c[j]]) { seen[c[j]] = 1; f[c[j]] += wn[k]; } }
  });
  const sc = pool.map((i) => {
    const c = D.codes[i], seen = new Uint8Array(26); let s = 0;
    for (let j = 0; j < L; j++) {
      if (!seen[c[j]]) { seen[c[j]] = 1; s += f[c[j]] * (1 - f[c[j]]); }
      const pj = pos[j][c[j]]; s += 0.5 * pj * (1 - pj);
    }
    return [s, i];
  }).sort((a, b) => b[0] - a[0]);
  const out = new Set(sc.slice(0, keep).map((x) => x[1]));
  cand.slice().sort((a, b) => D.w[b] - D.w[a]).slice(0, 100).forEach((i) => out.add(i));
  return [...out];
}

function update(word, p) {
  const gc = enc(word), L = D.L;
  S.cand = S.cand.filter((i) => pattern(gc, D.codes[i], L) === p);
  S.history.push([word, p]);
}

// --------------------------------------------------------------------- UI
let cur = { word: "", colors: [] };

function setCurrent(word) {
  cur = { word: word.toLowerCase(), colors: Array(D.L).fill(0) };
  $("#played").value = word.toUpperCase();
  drawCurrent();
}

function drawCurrent() {
  const row = $("#current");
  row.innerHTML = "";
  for (let i = 0; i < D.L; i++) {
    const t = document.createElement("button");
    t.className = "tile c" + cur.colors[i];
    t.textContent = (cur.word[i] || "").toUpperCase();
    t.title = "tap to change colour";
    t.onclick = () => { cur.colors[i] = (cur.colors[i] + 1) % 3; drawCurrent(); };
    row.appendChild(t);
  }
}

function drawHistory() {
  const h = $("#history");
  h.innerHTML = "";
  for (const [w, p] of S.history) {
    const row = document.createElement("div");
    row.className = "row";
    const s = patStr(p, D.L);
    for (let i = 0; i < D.L; i++) {
      const t = document.createElement("span");
      t.className = "tile small c" + "byg".indexOf(s[i]);
      t.textContent = w[i].toUpperCase();
      row.appendChild(t);
    }
    h.appendChild(row);
  }
}

function refresh() {
  drawHistory();
  const K = S.cand.length;
  const status = $("#status");
  if (K === 0) {
    status.textContent = "No word fits these colours - check for a typo (Undo).";
    $("#suggest").innerHTML = ""; $("#cands").textContent = ""; return;
  }
  const t0 = performance.now();
  const rows = rank(8);
  const ms = Math.round(performance.now() - t0);
  const turn = S.history.length + 1;
  status.textContent = `Turn ${turn} of ${MAX_GUESSES} · ${K.toLocaleString()} possible answer${K > 1 ? "s" : ""} · ${ms} ms`;
  const tb = $("#suggest");
  tb.innerHTML = "<tr><th>guess</th><th title='expected number of guesses including this one'>exp. guesses</th>" +
    "<th title='expected information'>info (bits)</th><th>P(win now)</th></tr>";
  rows.forEach((r, k) => {
    const tr = document.createElement("tr");
    if (k === 0) tr.className = "best";
    tr.innerHTML = `<td><b>${r.word.toUpperCase()}</b></td><td>${r.E.toFixed(2)}</td><td>${r.H.toFixed(2)}</td><td>${(r.pwin * 100).toFixed(1)}%</td>`;
    tr.onclick = () => setCurrent(r.word);
    tb.appendChild(tr);
  });
  if (rows.length) setCurrent(rows[0].word);
  // candidates
  let tot = 0; for (const i of S.cand) tot += D.w[i];
  const top = S.cand.slice().sort((a, b) => D.w[b] - D.w[a]).slice(0, 40);
  $("#cands").innerHTML = top.map((i) => {
    const p = D.w[i] / tot;
    return `<span class="cand" style="opacity:${0.45 + Math.min(0.55, p * 4)}">${D.words[i].toUpperCase()}` +
      `${p >= 0.01 ? ` <small>${(p * 100).toFixed(0)}%</small>` : ""}</span>`;
  }).join(" ") + (K > 40 ? ` <small>… +${(K - 40).toLocaleString()} more</small>` : "");
}

function submit() {
  const word = $("#played").value.trim().toLowerCase();
  if (word.length !== D.L || !/^[a-z]+$/.test(word)) { alert(`Enter a ${D.L}-letter word`); return; }
  cur.word = word;
  const p = cur.colors.reduce((acc, c, i) => acc + c * 3 ** i, 0);
  if (p === 3 ** D.L - 1) {
    $("#status").textContent = `Solved in ${S.history.length + 1}! 🎉  Press "New game".`;
    S.history.push([word, p]); drawHistory(); return;
  }
  update(word, p);
  refresh();
}

async function start() {
  const L = +$("#len").value;
  $("#status").textContent = "loading words…";
  D = prepare(await loadLength(L));
  S = newState();
  refresh();
}

window.addEventListener("DOMContentLoaded", () => {
  $("#len").onchange = start;
  $("#hard").onchange = start;
  $("#new").onclick = start;
  $("#submit").onclick = submit;
  $("#played").oninput = (e) => { cur.word = e.target.value.toLowerCase(); drawCurrent(); };
  $("#played").onkeydown = (e) => { if (e.key === "Enter") submit(); };
  $("#reject").onclick = () => {
    const i = D.index.get(cur.word);
    if (i !== undefined) { S.rejected.add(i); S.cand = S.cand.filter((x) => x !== i); }
    refresh();
  };
  $("#undo").onclick = () => {
    const h = S.history.slice(0, -1), rej = S.rejected;
    S = newState(); S.rejected = rej;
    for (const [w, p] of h) update(w, p);
    refresh();
  };
  start();
});
