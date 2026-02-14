from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter
from sqlalchemy.orm import Session

from core.risk.aggregate import portfolio_dv01
from infra.db.models import RiskRun, Trade
from infra.db.session import SessionLocal

router = APIRouter()


def get_db() -> Session:
    return SessionLocal()


@router.post("/risk-runs/run")
def run_risk(book: str = "RATES") -> dict:
    db = get_db()

    trades = db.query(Trade).filter(Trade.book == book).all()
    trade_dicts = [{"symbol": t.symbol, "quantity": t.quantity, "price": t.price} for t in trades]

    risk = {"message": "No trades available"} if not trade_dicts else portfolio_dv01(trade_dicts)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "book": book,
        "trade_count": len(trades),
        "risk": risk,
    }

    run = RiskRun(book=book, report=json.dumps(payload))
    db.add(run)
    db.commit()

    return {"run_id": run.id, "book": book, "generated_at": payload["generated_at"]}


@router.get("/risk-runs")
def list_runs(book: str = "RATES", limit: int = 5) -> list[dict]:
    db = get_db()

    runs = (
        db.query(RiskRun)
        .filter(RiskRun.book == book)
        .order_by(RiskRun.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {"run_id": r.id, "book": r.book, "created_at": r.created_at.isoformat()}
        for r in runs
    ]


@router.get("/risk-runs/{run_id}")
def get_run(run_id: str) -> dict:
    db = get_db()

    run = db.query(RiskRun).filter(RiskRun.id == run_id).first()
    if not run:
        return {"error": "run not found"}

    return json.loads(run.report)
