from sqlalchemy.orm import Session

from core.risk.dv01 import calculate_bond_dv01
from infra.db.models import Trade


def current_book_dv01(db: Session, book: str) -> float:
    trades = db.query(Trade).filter(Trade.book == book).all()

    total = 0.0
    for t in trades:
        risk = calculate_bond_dv01(symbol=t.symbol, quantity=t.quantity, price=t.price)
        total += risk.dv01
    return total
