from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.controls.limits import evaluate_limits
from core.risk.book import current_book_dv01
from core.risk.dv01 import calculate_bond_dv01
from infra.db.models import Event, IdempotencyRecord, Trade
from infra.db.session import SessionLocal

router = APIRouter()


class TradeRequest(BaseModel):
    symbol: str
    quantity: float
    price: float
    book: str


def get_db() -> Session:
    return SessionLocal()


@router.post("/")
def create_trade(
    trade: TradeRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, Any]:
    db = get_db()
    try:
        # 0) Idempotency check
        if idempotency_key:
            existing = db.query(IdempotencyRecord).filter_by(key=idempotency_key).first()
            if existing:
                return json.loads(existing.response)

        # 1) Compute risk for THIS trade
        try:
            risk = calculate_bond_dv01(trade.symbol, trade.quantity, trade.price)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # 2) Current book DV01
        book_dv01_now = current_book_dv01(db, trade.book)

        # 3) Limits decision
        decision = evaluate_limits(
            book=trade.book,
            trade_notional=risk.notional,
            trade_dv01=risk.dv01,
            current_book_dv01=book_dv01_now,
        )

        # 4) Audit evaluation (always)
        decision_payload = {
            "trade": trade.model_dump(),
            "trade_notional": risk.notional,
            "trade_dv01": risk.dv01,
            "book_dv01_before": book_dv01_now,
            "decision": {"status": decision.status, "reasons": decision.reasons},
        }
        db.add(Event(event_type="TRADE_EVALUATED", payload=json.dumps(decision_payload)))
        db.commit()

        # 5) If blocked, store idempotency record and return 409
        if decision.status == "BLOCK":
            blocked_payload = {
                "status": "BLOCK",
                "reasons": decision.reasons,
                "book_dv01_before": book_dv01_now,
                "book_dv01_after": book_dv01_now + risk.dv01,
            }

            if idempotency_key:
                db.add(IdempotencyRecord(key=idempotency_key, response=json.dumps(blocked_payload)))
                db.commit()

            raise HTTPException(status_code=409, detail=blocked_payload)

        # 6) Persist trade
        db_trade = Trade(
            symbol=trade.symbol,
            quantity=trade.quantity,
            price=trade.price,
            book=trade.book,
        )
        db.add(db_trade)
        db.add(Event(event_type="TRADE_CREATED", payload=json.dumps(trade.model_dump())))
        db.commit()

        # 7) Response payload (always returned)
        response_payload: dict[str, Any] = {
            "status": decision.status,  # PASS or WARN
            "reasons": decision.reasons,
            "trade_id": db_trade.id,
            "book_dv01_before": book_dv01_now,
            "book_dv01_after": book_dv01_now + risk.dv01,
        }

        # store idempotency record for success
        if idempotency_key:
            db.add(IdempotencyRecord(key=idempotency_key, response=json.dumps(response_payload)))
            db.commit()

        return response_payload

    finally:
        db.close()


@router.get("/")
def list_trades() -> list[dict[str, Any]]:
    db = get_db()
    try:
        trades = db.query(Trade).all()
        return [
            {
                "id": t.id,
                "symbol": t.symbol,
                "quantity": t.quantity,
                "price": t.price,
                "book": t.book,
            }
            for t in trades
        ]
    finally:
        db.close()
