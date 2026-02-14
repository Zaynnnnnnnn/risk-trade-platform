# Risk & Trade Platform (Pre-Trade Controls + DV01 Risk)

A small “bank-style” trade capture + risk control service.

It accepts trades, runs **pre-trade risk checks** (DV01 + limits), and either:
- **PASS / WARN** → stores the trade
- **BLOCK** → rejects the trade with **reason codes** (and does **not** store it)

Every decision is written to an **immutable audit log**, and the system can generate **persisted risk snapshots** to support reproducible reporting.

---

## Why this exists

In real trading environments, the hard part is not “saving a trade”.
The hard part is:
- consistent **risk calculations**
- **controls** that prevent limit breaches
- **auditability** (what happened, when, and why)
- **reproducibility** (what did risk look like at a specific time)

This project is a simplified version of that workflow.

---

## Key features

### 1) Pre-trade risk + controls
- Compute trade impact (DV01 + notional)
- Evaluate against per-book limits
- Return a decision with reason codes:
  - `LIM_TRADE_NOTIONAL_EXCEEDED`
  - `LIM_BOOK_DV01_EXCEEDED`

### 2) Audit event log (immutable trail)
Every evaluation is recorded as an event:
- `TRADE_EVALUATED`
- `TRADE_CREATED`

Blocked trades are also logged (important for traceability).

### 3) Risk snapshots (reproducible runs)
Create a persisted point-in-time risk report:
- `POST /risk-runs?book=RATES`
- `GET /risk-runs?book=RATES` (list)
- `GET /risk-runs/{run_id}` (retrieve)

This mirrors intraday / end-of-day risk runs in institutional workflows.

### 4) Operator-friendly dashboard
A small internal-tool style UI:
- submit trade
- see decision + reasons
- view latest audit events (click row for full payload)
- run risk snapshots + browse last runs

---

## Architecture (high level)

```text
Dashboard UI
  |
  v
FastAPI API Layer
  - POST /trades       -> pre-trade risk + limits -> Postgres
  - GET  /api/summary  -> portfolio DV01 summary
  - POST /risk-runs    -> persist snapshot
  - GET  /risk-runs    -> list snapshots
  |
  v
Postgres
  - trades
  - events (audit log)
  - risk_runs (snapshots)

#### Replace “Running locally (Docker)” with this
```md
## Running locally (Docker)

### 1) Start
```bash
docker compose up --build
2) Open
Dashboard: http://127.0.0.1:8000/

API docs (Swagger): http://127.0.0.1:8000/docs

3) Stop
docker compose down
Reset database (optional)
docker compose down -v
docker compose up --build

#### Add this “Demo script” section (super valuable)
```md
## Demo script (2 minutes)

1) Submit a small trade → PASS  
2) Submit a large trade → BLOCK (reason codes)  
3) Click the BLOCK audit event row → view full JSON payload  
4) Run “Risk Snapshot” → appears in “Last runs”  
5) Open a stored run by ID → shows reproducible report  
