from fastapi import APIRouter
from infra.db.session import SessionLocal
from infra.db.models import Trade
from core.risk.aggregate import portfolio_dv01

router = APIRouter()


@router.get("/summary")
def risk_summary() -> dict:
    db = SessionLocal()

    trades = db.query(Trade).all()

    trade_dicts = [
        {
            "symbol": t.symbol,
            "quantity": t.quantity,
            "price": t.price,
        }
        for t in trades
    ]

    if not trade_dicts:
        return {"message": "No trades available"}

    return portfolio_dv01(trade_dicts)
