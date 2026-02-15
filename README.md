Risk & Trade Platform (Pre-Trade Controls + DV01 Risk)

This project is a small trade capture and pre-trade risk service inspired by how sell-side control systems work.

It accepts trades, evaluates their risk impact, and decides whether they can be booked.
If a trade breaches limits, it is rejected with clear reason codes.
Every decision is recorded, and the system can generate point-in-time risk snapshots for reporting or investigation.

The goal wasn’t to build a “toy trading app”, but to model the control layer that sits between execution and risk in real environments.

What it does

At a high level, the service lets you:

Submit a trade

Calculate its DV01 and notional impact

Check that impact against configured limits

Either accept the trade or block it

Record the decision in an audit trail

Generate risk snapshots that can be revisited later

Why build this?

In practice, storing a trade is the easy part.
The harder problems are around control and traceability:

Making sure risk calculations are applied consistently

Preventing trades from breaching limits before they hit the book

Being able to explain exactly why a trade was allowed or rejected

Reconstructing what the portfolio looked like at a given time

This project is a simplified version of that workflow.

Main pieces of functionality
Pre-trade risk checks

When a trade is submitted, the system calculates its DV01 and notional impact and evaluates it against per-book limits.

It returns a structured decision:

PASS – trade is accepted

WARN – trade is allowed but flagged

BLOCK – trade is rejected

Blocked trades include reason codes such as:

LIM_TRADE_NOTIONAL_EXCEEDED

LIM_BOOK_DV01_EXCEEDED

Blocked trades are intentionally not stored, but they are still logged for traceability.

Immutable audit trail

Every evaluation is written as an event.

Typical events include:

TRADE_EVALUATED

TRADE_CREATED

This creates a simple but reliable history of what the system decided and when it decided it.

Risk snapshots

The service can generate a persisted snapshot of portfolio risk at a specific moment.

These runs are stored so they can be retrieved later without recalculating against updated data.
That mirrors how intraday or end-of-day risk runs are handled operationally.

Endpoints:

POST /risk-runs?book=RATES → create a snapshot

GET /risk-runs?book=RATES → list runs

GET /risk-runs/{run_id} → retrieve a specific run

Lightweight internal dashboard

There’s also a small UI intended to feel like an internal tool rather than a product:

Submit trades

See decisions and reason codes

View recent audit events

Trigger and browse risk snapshots

The UI contains no business logic — it just calls the API.

Architecture overview

The system is structured as a single service with clear separation between transport, risk logic, and persistence.

The FastAPI layer handles request routing and validation but does not contain risk calculations.
Trades are passed into a dedicated evaluation layer where DV01 is computed and limits are enforced.

Keeping that logic separate makes the decision process deterministic and easier to test, which is how control services are typically structured.

PostgreSQL acts as the system of record. It stores:

Accepted trades

The immutable audit log of evaluations

Persisted risk snapshot results

Snapshots are stored as their own entities so reports can be reproduced later without recalculating against changed data.

Everything runs in Docker so the full stack can be started reproducibly with a single command.

Running locally
docker compose up --build

Then open:
http://127.0.0.1:8000

## Business Context

This project simulates a pre-trade risk gateway similar to those used in
institutional execution systems.

Before an order reaches the market, it must pass:
• Exposure checks
• Instrument-level limits
• Portfolio risk constraints
• Audit logging for regulatory traceability

Client Order
    ↓
Risk Engine
    ↓
Validation Layer ──→ Reject (limit breach)
    ↓
Approval
    ↓
Audit Logger → Immutable record

