from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home() -> str:
    return r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Risk & Trade Platform</title>

  <style>
    :root{
      --bg0:#070b14;
      --bg1:#0b1220;
      --text:#e7eefc;
      --muted:#a8b3cf;
      --border:rgba(255,255,255,.10);
      --accent:#6ea8fe;
      --good:#46d39a;
      --warn:#ffcc66;
      --bad:#ff6b6b;
      --shadow: 0 12px 40px rgba(0,0,0,.35);
      --radius: 18px;
    }
    *{ box-sizing:border-box; }
    body{
      margin:0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
      background:
        radial-gradient(1200px 700px at 22% 10%, rgba(110,168,254,.20), transparent),
        radial-gradient(900px 600px at 85% 20%, rgba(70,211,154,.10), transparent),
        radial-gradient(800px 600px at 55% 85%, rgba(255,204,102,.10), transparent),
        linear-gradient(180deg, var(--bg0), var(--bg1));
      color:var(--text);
    }

    .shell{ max-width:1200px; margin:0 auto; padding: 22px 16px 60px; }
    .topbar{ display:flex; align-items:center; justify-content:space-between; gap:16px; padding: 10px 0 18px; }
    .brand{ display:flex; align-items:center; gap:12px; }
    .logo{
      width:42px; height:42px; border-radius:14px;
      background: rgba(110,168,254,.15);
      border:1px solid rgba(110,168,254,.30);
      display:flex; align-items:center; justify-content:center;
      box-shadow: var(--shadow);
    }
    .brand h1{ margin:0; font-size:18px; letter-spacing:.2px; }
    .brand .sub{ color:var(--muted); font-size:12px; margin-top:3px; }

    .actions{ display:flex; gap:10px; flex-wrap:wrap; align-items:center; }
    .btn{
      appearance:none; border:1px solid var(--border);
      background: rgba(255,255,255,.06);
      color:var(--text); text-decoration:none;
      padding:10px 12px; border-radius: 14px;
      font-size:13px;
      display:inline-flex; gap:8px; align-items:center;
      cursor:pointer;
    }
    .btn:hover{ border-color: rgba(110,168,254,.55); }
    .btn.primary{
      border-color: rgba(110,168,254,.55);
      background: rgba(110,168,254,.12);
    }

    .grid{ display:grid; grid-template-columns: 360px 1fr; gap:14px; align-items:start; }
    @media (max-width: 980px){ .grid{ grid-template-columns: 1fr; } }

    .card{
      background: rgba(17,26,46,.78);
      border:1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow: visible; /* allow tooltips to show */
    }
    }
    .card .hd{
      padding: 14px 16px;
      border-bottom: 1px solid rgba(255,255,255,.08);
      display:flex; align-items:center; justify-content:space-between; gap:12px;
      background: rgba(14,23,41,.65);
    }
    .card .hd h2{ margin:0; font-size:13px; color:var(--muted); font-weight:700; letter-spacing:.3px; text-transform:uppercase; }
    .card .bd{ padding: 14px 16px; }

    .kpis{ display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; }
    @media (max-width: 980px){ .kpis{ grid-template-columns: 1fr; } }
    .kpi{
      padding:14px; border-radius:16px;
      background: rgba(255,255,255,.05);
      border:1px solid rgba(255,255,255,.08);
    }
    .kpi .label{ color:var(--muted); font-size:12px; }
    .kpi .value{ font-size:22px; margin-top:6px; }

    label{ display:block; color:var(--muted); font-size:12px; margin: 10px 0 6px; }
    input, select{
      width:100%;
      background: rgba(0,0,0,.25);
      border:1px solid rgba(255,255,255,.10);
      color: var(--text);
      padding: 10px 10px;
      border-radius: 12px;
      outline:none;
      font-size: 13px;
    }
    input:focus, select:focus{ border-color: rgba(110,168,254,.55); }
    .row{ display:grid; grid-template-columns: 1fr 1fr; gap:10px; }
    @media (max-width: 980px){ .row{ grid-template-columns: 1fr; } }

    .hint{
      margin-top:10px;
      padding: 10px 12px;
      background: rgba(110,168,254,.10);
      border:1px solid rgba(110,168,254,.20);
      border-radius: 14px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }

    table{ width:100%; border-collapse: collapse; font-size: 13px; }
    th, td{
      padding: 10px 8px;
      border-bottom: 1px solid rgba(255,255,255,.08);
      vertical-align: top;
    }
    th{ text-align:left; color:var(--muted); font-weight:700; font-size:12px; }

    pre{
      margin:0;
      padding: 10px;
      background: rgba(0,0,0,.30);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 14px;
      overflow:auto;
      font-size: 12px;
      line-height: 1.35;
      max-height: 260px;
    }

    .pill{
      padding: 2px 8px;
      border-radius: 999px;
      border:1px solid rgba(255,255,255,.12);
      background: rgba(255,255,255,.06);
      font-size: 12px;
      display:inline-block;
    }
    .pill.good{ border-color: rgba(70,211,154,.35); background: rgba(70,211,154,.12); }
    .pill.bad{ border-color: rgba(255,107,107,.35); background: rgba(255,107,107,.12); }
    .pill.warn{ border-color: rgba(255,204,102,.35); background: rgba(255,204,102,.12); }

    .help{
      width:26px; height:26px;
      border-radius: 10px;
      display:inline-flex; align-items:center; justify-content:center;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.06);
      cursor:pointer;
      position: relative;
      flex: 0 0 auto;
    }
    .help:hover{ border-color: rgba(110,168,254,.55); }
    .help[data-tip]:hover::after{
      content: attr(data-tip);
      position:absolute;
      right:0;
      top:34px;
      width: min(360px, 70vw);
      padding: 10px 12px;
      background: rgba(0,0,0,.85);
      border: 1px solid rgba(255,255,255,.12);
      border-radius: 14px;
      color: var(--text);
      font-size: 12px;
      line-height: 1.35;
      z-index: 50;
      box-shadow: var(--shadow);
    }

    .toasts{
      position: fixed; right: 16px; bottom: 16px;
      display:flex; flex-direction:column; gap:10px;
      z-index: 200;
    }
    .toast{
      min-width: 280px;
      max-width: 520px;
      padding: 12px 12px;
      border-radius: 16px;
      border:1px solid rgba(255,255,255,.12);
      background: rgba(17,26,46,.95);
      box-shadow: var(--shadow);
      display:flex; gap:10px; align-items:flex-start;
    }
    .dot{ width:10px; height:10px; border-radius:999px; margin-top:5px; background: var(--accent); }
    .dot.good{ background: var(--good); }
    .dot.bad{ background: var(--bad); }
    .dot.warn{ background: var(--warn); }
    .toast .t{ font-size: 13px; }
    .toast .m{ color: var(--muted); font-size:12px; margin-top:4px; white-space: pre-wrap; }
    .toast .x{ margin-left:auto; background:transparent; border:none; color:var(--muted); cursor:pointer; font-size:16px; }

    .modal-backdrop{
      position: fixed; inset: 0;
      background: rgba(0,0,0,.55);
      display:none;
      align-items:center; justify-content:center;
      z-index: 300;
      padding: 16px;
    }
    .modal{
      width: min(860px, 96vw);
      border-radius: 20px;
      border:1px solid rgba(255,255,255,.12);
      background: rgba(17,26,46,.98);
      box-shadow: var(--shadow);
      overflow:hidden;
    }
    .modal .mh{
      padding: 14px 16px;
      border-bottom: 1px solid rgba(255,255,255,.08);
      display:flex; align-items:center; justify-content:space-between;
      background: rgba(14,23,41,.85);
    }
    .modal .mh h3{ margin:0; font-size: 14px; color: var(--text); }
    .modal .mb{ padding: 14px 16px; color: var(--muted); font-size: 13px; line-height: 1.45; }
  </style>
</head>

<body>
  <div class="shell">
    <div class="topbar">
      <div class="brand">
        <div class="logo" title="Risk & Trade Platform">
          <span style="font-weight:800;color:var(--accent);">RT</span>
        </div>
        <div>
          <h1>Risk & Trade Platform</h1>
          <div class="sub">Trade capture • pre-trade limits • DV01 risk • audit events • risk snapshots</div>
        </div>
      </div>

      <div class="actions">
        <span class="pill" id="statusPill">Status: …</span>
        <button class="btn primary" id="refreshBtn">Refresh</button>
        <a class="btn" href="/docs" target="_blank">API Docs</a>
        <a class="btn" href="/api/report">Download Report</a>
        <button class="btn" id="helpBtn">Help</button>
      </div>
    </div>

    <div class="grid">
      <!-- Left column -->
      <div>
        <!-- Submit trade -->
        <div class="card">
          <div class="hd">
            <h2>Submit trade</h2>
            <div class="help" data-tip="Creates a trade. The system runs pre-trade risk checks (DV01 + limits). If breached, trade is BLOCKED and NOT stored.">?</div>
          </div>
          <div class="bd">
            <div class="row">
              <div>
                <label>Book <span class="pill">required</span></label>
                <select id="book">
                  <option value="RATES">RATES</option>
                </select>
              </div>
              <div>
                <label>Symbol <span class="pill">required</span></label>
                <select id="symbol">
                  <option value="UKT10Y">UKT10Y</option>
                  <option value="UKT5Y">UKT5Y</option>
                  <option value="UKT30Y">UKT30Y</option>
                </select>
              </div>
            </div>

            <div class="row">
              <div>
                <label>Quantity</label>
                <input id="quantity" type="number" value="1000000" />
              </div>
              <div>
                <label>Price</label>
                <input id="price" type="number" step="0.01" value="99.25" />
              </div>
            </div>

            <label>
              Idempotency Key
              <span class="help" style="margin-left:8px;" data-tip="Optional. If you submit the same key twice, the server returns the same result and does not duplicate trades.">?</span>
            </label>
            <input id="idem" placeholder="e.g., abc123" />

            <div style="display:flex; gap:10px; margin-top:14px; flex-wrap:wrap;">
              <button class="btn primary" id="submitTradeBtn">Submit</button>
              <button class="btn" id="submitBlockBtn">Try BLOCK example</button>
            </div>

            <div class="hint">
              Tip: Click <b>Try BLOCK example</b> to see a bank-style rejection with reason codes.
            </div>
          </div>
        </div>

        <!-- Risk limits -->
        <div class="card" style="margin-top:14px;">
          <div class="hd">
            <h2>Risk limits</h2>
            <div class="help" data-tip="These limits are used by the controls engine. Trades breaching limits are BLOCKED with reason codes.">?</div>
          </div>
          <div class="bd">
            <div class="muted" style="font-size:12px; margin-bottom:10px;">
              Limits are per book (e.g., RATES). These are intentionally simple and configurable.
            </div>
            <pre id="limitsBox">Loading…</pre>
          </div>
        </div>

        <!-- Risk snapshots -->
        <div class="card" style="margin-top:14px;">
          <div class="hd">
            <h2>Risk snapshots</h2>
            <div class="help" data-tip="Creates a persisted risk calculation (snapshot). Used for audit, reporting, and reproducibility.">?</div>
          </div>
          <div class="bd">
            <button class="btn primary" id="runRiskBtn">Run Risk Snapshot</button>

            <div class="muted" style="margin-top:10px;font-size:12px;">
              Last runs (most recent first):
            </div>

            <div id="runsList" class="muted" style="margin-top:8px;font-size:12px;">Loading…</div>
          </div>
        </div>
      </div>

      <!-- Right column -->
      <div style="display:flex; flex-direction:column; gap:14px;">
        <div class="card">
          <div class="hd">
            <h2>Portfolio snapshot</h2>
            <div class="help" data-tip="Metrics come from /api/summary which reads trades from Postgres and computes DV01 using the risk engine.">?</div>
          </div>
          <div class="bd">
            <div class="kpis">
              <div class="kpi">
                <div class="label">Trades stored</div>
                <div id="tradeCount" class="value">—</div>
              </div>
              <div class="kpi">
                <div class="label">Portfolio Notional</div>
                <div id="notional" class="value">—</div>
              </div>
              <div class="kpi">
                <div class="label">Portfolio DV01</div>
                <div id="dv01" class="value">—</div>
              </div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="hd">
            <h2>Latest audit events <span class="pill">immutable</span></h2>
            <div class="help" data-tip="Click a row to drill into the full audit payload. Even BLOCKED trades are logged.">?</div>
          </div>
          <div class="bd">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Type</th>
                  <th>Decision</th>
                </tr>
              </thead>
              <tbody id="eventsBody">
                <tr><td class="muted">Loading…</td><td></td><td></td></tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  </div>

  <div class="toasts" id="toasts"></div>

  <!-- Help Modal -->
  <div class="modal-backdrop" id="modalBackdrop">
    <div class="modal">
      <div class="mh">
        <h3>How to use this platform</h3>
        <button class="btn" id="closeModalBtn">Close</button>
      </div>
      <div class="mb">
        <ul>
          <li><b>Submit trade</b> → server calculates DV01 impact and checks limits.</li>
          <li>If limits are breached, the trade is <b>BLOCKED</b> with reason codes and <b>not stored</b>.</li>
          <li>All actions are written into an <b>audit event log</b> for traceability.</li>
          <li><b>Risk snapshots</b> store point-in-time reports for reproducible reporting.</li>
          <li><b>Tip:</b> Click an event row to open full JSON audit payload.</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- Event Details Modal -->
  <div class="modal-backdrop" id="eventModalBackdrop">
    <div class="modal">
      <div class="mh">
        <h3>Event details</h3>
        <button class="btn" id="closeEventModalBtn">Close</button>
      </div>
      <div class="mb">
        <div class="muted" style="margin-bottom:10px;">
          Clicked event payload (audit record)
        </div>
        <pre id="eventDetailsPre">Loading…</pre>
      </div>
    </div>
  </div>

<script>
  const $ = (id) => document.getElementById(id);

  function toast(kind, title, msg){
    const wrap = $("toasts");
    const t = document.createElement("div");
    t.className = "toast";
    const dot = document.createElement("div");
    dot.className = "dot " + (kind || "");
    const body = document.createElement("div");
    body.innerHTML = `<div class="t"><b>${title}</b></div><div class="m">${msg || ""}</div>`;
    const x = document.createElement("button");
    x.className = "x";
    x.textContent = "×";
    x.onclick = () => t.remove();
    t.appendChild(dot); t.appendChild(body); t.appendChild(x);
    wrap.appendChild(t);
    setTimeout(() => { if (t.parentNode) t.remove(); }, 6500);
  }

  function fmtMoney(x){
    if (x === null || x === undefined) return "—";
    return "£" + new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(x);
  }

  function openModal(){ $("modalBackdrop").style.display = "flex"; }
  function closeModal(){ $("modalBackdrop").style.display = "none"; }

  function openEventModal(payload){
    $("eventDetailsPre").textContent = JSON.stringify(payload, null, 2);
    $("eventModalBackdrop").style.display = "flex";
  }
  function closeEventModal(){
    $("eventModalBackdrop").style.display = "none";
  }

  $("helpBtn").onclick = openModal;
  $("closeModalBtn").onclick = closeModal;
  $("modalBackdrop").onclick = (e) => { if (e.target.id === "modalBackdrop") closeModal(); };

  $("closeEventModalBtn").onclick = closeEventModal;
  $("eventModalBackdrop").onclick = (e) => { if (e.target.id === "eventModalBackdrop") closeEventModal(); };

  async function loadStatus(){
    try{
      const res = await fetch("/api/status");
      const data = await res.json();
      const pill = $("statusPill");
      pill.textContent = `Status: API ${data.api} • DB ${data.db}`;
      pill.className = "pill good";
    }catch(e){
      const pill = $("statusPill");
      pill.textContent = "Status: degraded";
      pill.className = "pill bad";
    }
  }

  async function loadLimits(){
    try{
      const res = await fetch("/api/limits");
      const data = await res.json();
      $("limitsBox").textContent = JSON.stringify(data, null, 2);
    }catch(e){
      $("limitsBox").textContent = "Could not load limits.";
    }
  }

  async function loadRuns(){
    try{
      const res = await fetch("/risk-runs?book=RATES");
      const runs = await res.json();

      if (!Array.isArray(runs) || runs.length === 0){
        $("runsList").textContent = "No runs yet. Click “Run Risk Snapshot”.";
        return;
      }

      const html = runs.map(r => {
        const ts = (r.created_at || "").replace("T"," ").replace("Z","");
        return `<div style="margin:6px 0;">
          <a href="/risk-runs/${r.run_id}" target="_blank" style="color: var(--accent); text-decoration:none;">
            ${r.run_id}
          </a>
          <span class="muted"> (${ts})</span>
        </div>`;
      }).join("");

      $("runsList").innerHTML = html;
    }catch(e){
      $("runsList").textContent = "Could not load runs.";
    }
  }

  async function runRisk(){
    const res = await fetch("/risk-runs?book=RATES", { method: "POST" });
    const data = await res.json();

    if (res.status >= 200 && res.status < 300){
      toast("good", "Risk run created", `Run ID: ${data.run_id}`);
      await loadRuns();
      return;
    }

    toast("bad", "Risk run failed", JSON.stringify(data, null, 2));
  }

  async function refresh(){
    await loadStatus();
    await loadLimits();
    await loadRuns();

    const res = await fetch("/api/summary");
    const data = await res.json();

    $("tradeCount").textContent = data.trade_count ?? "0";

    const risk = data.risk || {};
    $("notional").textContent = risk.portfolio_notional ? fmtMoney(risk.portfolio_notional) : "—";
    $("dv01").textContent = risk.portfolio_dv01 ? (fmtMoney(risk.portfolio_dv01) + "/bp") : "—";

    const tbody = $("eventsBody");
    tbody.innerHTML = "";
    const events = data.latest_events || [];
    if (events.length === 0){
      tbody.innerHTML = `<tr><td class="muted">No events yet</td><td></td><td></td></tr>`;
      return;
    }

    events.forEach(ev => {
      const ts = (ev.created_at || "").replace("T"," ").replace("Z","");
      let decisionTxt = "—";
      let pillClass = "";
      try{
        const d = ev.payload?.decision?.status;
        const reasons = ev.payload?.decision?.reasons || [];
        if (d){
          decisionTxt = d + (reasons.length ? (" • " + reasons.join(", ")) : "");
          pillClass = (d === "BLOCK") ? "bad" : (d === "WARN") ? "warn" : "good";
        }
      }catch(_){}

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="muted">${ts}</td>
        <td><span class="pill">${ev.event_type}</span></td>
        <td><span class="pill ${pillClass}">${decisionTxt}</span></td>
      `;
      tr.style.cursor = "pointer";
      tr.onclick = () => openEventModal(ev);
      tbody.appendChild(tr);
    });
  }

  async function submitTrade(payload, idemKey){
    const headers = { "Content-Type": "application/json" };
    if (idemKey) headers["Idempotency-Key"] = idemKey;

    const res = await fetch("/trades/", {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });

    if (res.status === 200){
      const j = await res.json();
      toast("good", "Trade accepted",
        `Status: ${j.status}\nDV01 before: ${j.book_dv01_before}\nDV01 after: ${j.book_dv01_after}\nTrade ID: ${j.trade_id}`
      );
      await refresh();
      return;
    }

    if (res.status === 409){
      const j = await res.json();
      const d = j.detail || j;
      toast("bad", "Trade blocked",
        `Reasons: ${(d.reasons || []).join(", ")}\nDV01 before: ${d.book_dv01_before}\nDV01 after: ${d.book_dv01_after}`
      );
      await refresh();
      return;
    }

    const txt = await res.text();
    toast("warn", "Unexpected response", `HTTP ${res.status}\n${txt}`);
  }

  $("submitTradeBtn").onclick = async () => {
    const payload = {
      symbol: $("symbol").value,
      quantity: Number($("quantity").value),
      price: Number($("price").value),
      book: $("book").value,
    };
    const idemKey = $("idem").value.trim();
    await submitTrade(payload, idemKey);
  };

  $("submitBlockBtn").onclick = async () => {
    $("quantity").value = "50000000";
    const payload = {
      symbol: $("symbol").value,
      quantity: Number($("quantity").value),
      price: Number($("price").value),
      book: $("book").value,
    };
    await submitTrade(payload, "block-demo");
  };

  $("refreshBtn").onclick = refresh;
  $("runRiskBtn").onclick = runRisk;

  refresh();
</script>
</body>
</html>
"""
