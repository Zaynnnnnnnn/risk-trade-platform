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

Architecture (high level)

The system is structured as a small, self-contained service that mirrors how pre-trade controls are typically implemented in a trading environment.

A lightweight dashboard acts as the operator interface.
It allows a user to submit trades, inspect decisions, and trigger risk snapshots, but it contains no business logic — it only calls the API.

The FastAPI application is the core of the system.
It exposes endpoints for trade submission, portfolio summaries, and risk snapshot generation.
When a trade is received, it is passed through a risk evaluation layer that calculates DV01 impact and checks configured limits before any persistence occurs.

The risk and controls logic is intentionally separated from the API layer.
This makes the decision process deterministic and testable, similar to how real control services isolate risk calculations from transport concerns.

PostgreSQL is used as the system of record.
It stores:

accepted trades,

an immutable event log capturing every evaluation (including blocked trades),

and persisted risk runs that represent point-in-time portfolio states.

Risk snapshots are written as their own entities so reports can be reproduced later without recalculating against changed data, which reflects how end-of-day or intraday risk cycles are handled operationally.

The entire stack runs inside Docker containers to ensure the environment is reproducible and can be started with a single command, similar to how internal services are packaged for deployment.
