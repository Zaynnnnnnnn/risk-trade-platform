from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import Response
from sqlalchemy.orm import Session

from core.risk.aggregate import portfolio_dv01
from infra.db.models import Trade
from infra.db.session import SessionLocal

router = APIRouter()


def get_db() -> Session:
    return SessionLocal()


@router.get("/report")
def report() -> Response:
    db = get_db()
    trades = db.query(Trade).all()

    trade_dicts = [{"symbol": t.symbol, "quantity": t.quantity, "price": t.price} for t in trades]
    risk = {"message": "No trades available"} if not trade_dicts else portfolio_dv01(trade_dicts)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "trade_count": len(trades),
        "risk": risk,
    }

    body = json.dumps(payload, indent=2)
    filename = f"risk_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

    return Response(
        content=body,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
