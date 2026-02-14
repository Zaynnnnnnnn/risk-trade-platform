from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter
from sqlalchemy.orm import Session

from core.risk.aggregate import portfolio_dv01
from infra.db.models import Event, Trade
from infra.db.session import SessionLocal

router = APIRouter()


def get_db() -> Session:
    return SessionLocal()


@router.get("/summary")
def dashboard_summary() -> dict[str, Any]:
    db = get_db()

    trades = db.query(Trade).all()
    trade_dicts = [{"symbol": t.symbol, "quantity": t.quantity, "price": t.price} for t in trades]

    risk = {"message": "No trades available"}
    if trade_dicts:
        risk = portfolio_dv01(trade_dicts)

    events = (
        db.query(Event)
        .order_by(Event.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "trade_count": len(trades),
        "risk": risk,
        "latest_events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "payload": json.loads(e.payload),
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ],
    }
